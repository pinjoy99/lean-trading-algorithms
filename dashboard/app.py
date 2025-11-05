#!/usr/bin/env python3
"""
Interactive Backtest Results Dashboard
A web-based dashboard for analyzing QuantConnect backtest results across multiple projects.

Features:
- Interactive charts using Plotly.js
- Performance metrics visualization
- Trade analysis and filtering
- Multi-project backtest comparison
- Responsive web interface

Usage:
    python app.py
    # Then visit http://localhost:5000/dashboard
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'quantconnect-dashboard-2023'

# Configuration
DASHBOARD_CONFIG = {
    'title': 'QuantConnect Backtest Dashboard',
    'data_directory': 'sample_data',
    'supported_projects': ['rsi-minutely', 'sma-crossover', 'custom'],
    'default_project': 'rsi-minutely'
}

class BacktestDataManager:
    """Manage loading and processing of backtest data from multiple projects"""

    def __init__(self):
        self.data_cache = {}
        self.project_dirs = {
            'rsi-minutely': '../rsi-minutely/backtests',
            'sma-crossover': '../sma-crossover/backtests',
            'supertrend-btc': '../supertrend-btc/backtests',
            'buy-and-hold-spy': '../buy-and-hold-spy/backtests',
            'custom': '../custom/backtests'
        }

    def load_backtest_results(self, project_name, backtest_id=None):
        """Load backtest results for a specific project"""
        try:
            project_dir = self.project_dirs.get(project_name)
            if not project_dir or not os.path.exists(project_dir):
                return None

            # Get all backtest directories
            backtest_dirs = [d for d in os.listdir(project_dir)
                           if d.startswith('2025') and os.path.isdir(os.path.join(project_dir, d))]

            if not backtest_dirs:
                return None

            # Sort by timestamp (newest first)
            backtest_dirs.sort(reverse=True)

            # Use specified backtest_id or the latest
            target_dir = backtest_id if backtest_id else backtest_dirs[0]
            backtest_path = os.path.join(project_dir, target_dir)

            if not os.path.exists(backtest_path):
                return None

            # Load summary data
            summary_file = None
            for file in os.listdir(backtest_path):
                if file.endswith('-summary.json'):
                    summary_file = os.path.join(backtest_path, file)
                    break

            if not summary_file or not os.path.exists(summary_file):
                return None

            with open(summary_file, 'r') as f:
                summary_data = json.load(f)

            # Load additional files
            result_data = self._load_additional_files(backtest_path)

            return {
                'summary': summary_data,
                'project': project_name,
                'backtest_id': target_dir,
                'timestamp': target_dir,
                'trades': result_data.get('trades', []),
                'equity_curve': result_data.get('equity_curve', []),
                'buy_hold_curve': result_data.get('buy_hold_curve', []),
                'logs': result_data.get('logs', [])
            }

        except Exception as e:
            logger.error(f"Error loading backtest results: {e}")
            return None

    def _load_additional_files(self, backtest_path):
        """Load additional data files from backtest directory"""
        result = {
            'trades': [],
            'equity_curve': [],
            'logs': []
        }

        try:
            # Load order events (trade history)
            for file in os.listdir(backtest_path):
                if file.endswith('-order-events.json'):
                    order_file = os.path.join(backtest_path, file)
                    with open(order_file, 'r') as f:
                        result['trades'] = json.load(f)
                    break

            # Load chart data (equity curve) - look for full data file with charts
            for file in os.listdir(backtest_path):
                # Skip summary files, look for main data files
                if file.endswith('.json') and not file.endswith('-summary.json') and 'chart' not in file:
                    chart_file = os.path.join(backtest_path, file)
                    try:
                        with open(chart_file, 'r') as f:
                            data = json.load(f)
                            # Check if this file has the full chart data
                            if 'charts' in data and 'Strategy Equity' in data['charts']:
                                equity_series = data['charts']['Strategy Equity'].get('series', {})
                                if 'Equity' in equity_series and 'values' in equity_series['Equity']:
                                    equity_data = equity_series['Equity']['values']
                                    # Only use if we have substantial data (not just summary)
                                    if len(equity_data) > 10:
                                        result['equity_curve'] = equity_data
                                        # Calculate buy-and-hold equity curve
                                        result['buy_hold_curve'] = self._calculate_buy_hold_curve(equity_data)
                                        logger.info(f"Loaded equity curve with {len(equity_data)} data points from {file}")
                                        logger.info(f"Calculated buy-and-hold curve with {len(result['buy_hold_curve'])} points")
                                        break
                    except Exception as e:
                        logger.warning(f"Error loading {file}: {e}")
                        continue

            # If no equity curve found yet, try summary file as fallback
            if not result['equity_curve']:
                for file in os.listdir(backtest_path):
                    if file.endswith('-summary.json'):
                        summary_file = os.path.join(backtest_path, file)
                        try:
                            with open(summary_file, 'r') as f:
                                data = json.load(f)
                                if 'charts' in data and 'Strategy Equity' in data['charts']:
                                    equity_series = data['charts']['Strategy Equity'].get('series', {})
                                    if 'Equity' in equity_series and 'values' in equity_series['Equity']:
                                        result['equity_curve'] = equity_series['Equity']['values']
                                        logger.info(f"Loaded equity curve from summary: {len(result['equity_curve'])} points")
                        except Exception as e:
                            logger.warning(f"Error loading summary file: {e}")
                        break

        except Exception as e:
            logger.error(f"Error loading additional files: {e}")

        return result

    def _calculate_buy_hold_curve(self, equity_data):
        """Calculate baseline equity curve (cash/bond equivalent with minimal return)"""
        try:
            if not equity_data or len(equity_data) < 2:
                return []

            # Since we don't have access to the underlying asset price data,
            # we'll create a conservative baseline comparison
            # Using a 0% return (cash equivalent) as the most conservative buy-and-hold

            initial_capital = 100000  # Standard backtest starting capital
            annual_risk_free_rate = 0.05  # Assume 5% risk-free rate (conservative)

            buy_hold_curve = []

            for i, point in enumerate(equity_data):
                timestamp = point[0]

                # Calculate days since start
                if i == 0:
                    days_elapsed = 0
                else:
                    days_elapsed = (timestamp - equity_data[0][0]) / (24 * 3600)

                # Simple compounding: P * (1 + r)^t
                # Where r is daily rate and t is days
                daily_rate = annual_risk_free_rate / 365
                years = days_elapsed / 365
                buy_hold_equity = initial_capital * ((1 + annual_risk_free_rate) ** years)

                buy_hold_curve.append([timestamp, buy_hold_equity])

            final_return = ((buy_hold_curve[-1][1] / initial_capital) - 1) * 100
            logger.info(f"Calculated baseline (5% risk-free): Start=${initial_capital:,.2f}, End=${buy_hold_curve[-1][1]:,.2f}")
            logger.info(f"Baseline return: {final_return:.2f}%")
            logger.info("Note: Using risk-free rate as conservative buy-and-hold comparison")

            return buy_hold_curve

        except Exception as e:
            logger.error(f"Error calculating baseline curve: {e}")
            return []

    def list_available_projects(self):
        """List all projects with available backtest data"""
        projects = []
        for project_name, project_dir in self.project_dirs.items():
            if os.path.exists(project_dir):
                backtest_dirs = [d for d in os.listdir(project_dir)
                              if d.startswith('2025') and os.path.isdir(os.path.join(project_dir, d))]
                if backtest_dirs:
                    projects.append({
                        'name': project_name,
                        'backtests_count': len(backtest_dirs),
                        'latest_backtest': max(backtest_dirs) if backtest_dirs else None
                    })
        return projects

# Initialize data manager
data_manager = BacktestDataManager()

@app.route('/')
def index():
    """Main dashboard page"""
    projects = data_manager.list_available_projects()
    return render_template('overview.html',
                         projects=projects,
                         config=DASHBOARD_CONFIG)

@app.route('/dashboard')
def dashboard():
    """Dashboard overview page"""
    projects = data_manager.list_available_projects()
    return render_template('overview.html',
                         projects=projects,
                         config=DASHBOARD_CONFIG)

@app.route('/compare')
def compare_projects():
    """Project comparison page"""
    projects = data_manager.list_available_projects()
    return render_template('compare.html',
                         projects=projects,
                         config=DASHBOARD_CONFIG)

@app.route('/project/<project_name>')
def project_dashboard(project_name):
    """Project-specific dashboard"""
    backtest_data = data_manager.load_backtest_results(project_name)
    if not backtest_data:
        return f"No backtest data found for project: {project_name}", 404

    projects = data_manager.list_available_projects()
    return render_template('project_dashboard.html',
                         project=project_name,
                         data=backtest_data,
                         projects=projects,
                         config=DASHBOARD_CONFIG)

@app.route('/api/projects')
def api_projects():
    """API endpoint to get list of available projects"""
    projects = data_manager.list_available_projects()
    return jsonify(projects)

@app.route('/api/project/<project_name>/data')
def api_project_data(project_name):
    """API endpoint to get backtest data for a project"""
    backtest_data = data_manager.load_backtest_results(project_name)
    if not backtest_data:
        return jsonify({'error': 'No data found'}), 404

    return jsonify(backtest_data)

@app.route('/api/project/<project_name>/metrics')
def api_project_metrics(project_name):
    """API endpoint to get calculated metrics for a project"""
    backtest_data = data_manager.load_backtest_results(project_name)
    if not backtest_data:
        return jsonify({'error': 'No data found'}), 404

    # Calculate additional metrics
    metrics = calculate_additional_metrics(backtest_data)
    return jsonify(metrics)

@app.route('/api/projects/compare')
def api_compare_projects():
    """API endpoint to compare multiple projects"""
    projects_param = request.args.get('projects', '')
    if not projects_param:
        return jsonify({'error': 'No projects specified'}), 400

    project_names = [p.strip() for p in projects_param.split(',')]
    comparison_data = []

    for project_name in project_names:
        backtest_data = data_manager.load_backtest_results(project_name)
        if backtest_data:
            metrics = calculate_additional_metrics(backtest_data)
            comparison_data.append(metrics)

    return jsonify({
        'projects': comparison_data,
        'comparison_date': datetime.now().isoformat()
    })

@app.route('/api/project/<project_name>/trades')
def api_project_trades(project_name):
    """API endpoint to get trade analysis for a project"""
    backtest_data = data_manager.load_backtest_results(project_name)
    if not backtest_data:
        return jsonify({'error': 'No data found'}), 404

    trades = backtest_data.get('trades', [])
    if not trades:
        return jsonify({'trades': [], 'summary': {}})

    # Analyze trades
    trade_summary = analyze_trades(trades)
    return jsonify({
        'trades': trades,
        'summary': trade_summary
    })

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/test-chart')
def test_chart():
    """Test page for TradingView Lightweight Charts"""
    try:
        with open('test_chart.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Test file not found", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

def calculate_additional_metrics(backtest_data):
    """Calculate additional performance metrics from backtest data"""
    try:
        summary = backtest_data['summary']

        # Basic metrics from summary
        portfolio_stats = summary.get('totalPerformance', {}).get('portfolioStatistics', {})

        metrics = {
            'project_name': backtest_data['project'],
            'backtest_id': backtest_data['backtest_id'],

            # Performance metrics
            'total_return': portfolio_stats.get('totalNetProfit', 0),
            'annual_return': portfolio_stats.get('compoundingAnnualReturn', 0),
            'sharpe_ratio': portfolio_stats.get('sharpeRatio', 0),
            'sortino_ratio': portfolio_stats.get('sortinoRatio', 0),
            'max_drawdown': portfolio_stats.get('drawdown', 0),

            # Trade metrics
            'total_trades': len(backtest_data.get('trades', [])),
            'win_rate': portfolio_stats.get('winRate', 0),
            'profit_factor': summary.get('totalPerformance', {}).get('tradeStatistics', {}).get('profitFactor', 0),

            # Risk metrics
            'volatility': portfolio_stats.get('annualStandardDeviation', 0),
            'var_95': portfolio_stats.get('valueAtRisk95', 0),
            'var_99': portfolio_stats.get('valueAtRisk99', 0),

            # Trading metrics
            'portfolio_turnover': portfolio_stats.get('portfolioTurnover', 0),
            'total_fees': portfolio_stats.get('totalFees', 0),

            # Time period
            'start_date': summary.get('totalPerformance', {}).get('tradeStatistics', {}).get('startDateTime', ''),
            'end_date': summary.get('totalPerformance', {}).get('tradeStatistics', {}).get('endDateTime', ''),
        }

        return metrics

    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {}

def analyze_trades(trades):
    """Analyze trade data and return summary statistics"""
    try:
        # Process filled trades
        filled_trades = [t for t in trades if t.get('status') == 'filled']

        if not filled_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }

        # Group trades by orderId
        trade_pairs = {}
        for trade in filled_trades:
            order_id = trade.get('orderId')
            if order_id not in trade_pairs:
                trade_pairs[order_id] = []
            trade_pairs[order_id].append(trade)

        # Calculate P&L for completed trades
        completed_trades = []
        for order_id, trade_list in trade_pairs.items():
            if len(trade_list) == 2:  # Entry and exit
                entry_trade = trade_list[0] if trade_list[0]['direction'] == 'buy' else trade_list[1]
                exit_trade = trade_list[1] if trade_list[1]['direction'] == 'sell' else trade_list[0]

                quantity = entry_trade.get('fillQuantity', 0)
                entry_price = entry_trade.get('fillPrice', 0)
                exit_price = exit_trade.get('fillPrice', 0)

                pnl = (exit_price - entry_price) * quantity if entry_trade['direction'] == 'buy' else (entry_price - exit_price) * quantity

                completed_trades.append({
                    'entry_time': entry_trade.get('time'),
                    'exit_time': exit_trade.get('time'),
                    'symbol': entry_trade.get('symbolValue'),
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'direction': entry_trade['direction']
                })

        # Calculate statistics
        winning_trades = [t for t in completed_trades if t['pnl'] > 0]
        losing_trades = [t for t in completed_trades if t['pnl'] < 0]

        total_pnl = sum(t['pnl'] for t in completed_trades)
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))

        return {
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(completed_trades) if completed_trades else 0,
            'avg_win': total_wins / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_losses / len(losing_trades) if losing_trades else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else float('inf'),
            'total_pnl': total_pnl,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'largest_win': max(t['pnl'] for t in completed_trades) if completed_trades else 0,
            'largest_loss': min(t['pnl'] for t in completed_trades) if completed_trades else 0
        }

    except Exception as e:
        logger.error(f"Error analyzing trades: {e}")
        return {}

@app.template_filter('format_percentage')
def format_percentage(value):
    """Format number as percentage"""
    try:
        return f"{float(value) * 100:.2f}%"
    except:
        return f"{value:.2f}%"

@app.template_filter('format_currency')
def format_currency(value):
    """Format number as currency"""
    try:
        return f"${float(value):,.2f}"
    except:
        return f"${value:,.2f}"

@app.template_filter('format_number')
def format_number(value):
    """Format number with thousands separator"""
    try:
        return f"{float(value):,.2f}"
    except:
        return str(value)

if __name__ == '__main__':
    print("🚀 Starting QuantConnect Backtest Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000/dashboard")
    print("📁 Supported projects:")

    # Display available projects
    projects = data_manager.list_available_projects()
    for project in projects:
        print(f"   • {project['name']}: {project['backtests_count']} backtest(s)")

    print("\n💡 Usage:")
    print("   1. Visit http://localhost:5000/dashboard")
    print("   2. Select a project to view its backtest results")
    print("   3. Explore interactive charts and metrics")

    # Start Flask development server
    app.run(host='127.0.0.1', port=5000, debug=True)
