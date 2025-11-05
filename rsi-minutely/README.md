# Minutely RSI Trading Strategy

![QuantConnect](https://cdn.quantconnect.com/web/i/icon.png)

A comprehensive RSI-based trading strategy implemented using QuantConnect Lean CLI and Cloud platforms, designed for minute-level data analysis and algorithmic trading.

## 📋 Table of Contents

- [Overview](#overview)
- [Strategy Description](#strategy-description)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Backtesting](#backtesting)
- [Optimization](#optimization)
- [Live Trading](#live-trading)
- [Risk Management](#risk-management)
- [Performance Analysis](#performance-analysis)
- [Cloud Deployment](#cloud-deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements a sophisticated Relative Strength Index (RSI) trading strategy that operates on minute-level data to identify overbought and oversold market conditions. The strategy is designed to work seamlessly on both QuantConnect Lean CLI (local development) and QuantConnect Cloud (production deployment).

### Key Features

- ✅ **Dual Platform Support**: Works on both Lean CLI and Cloud
- ✅ **Advanced Risk Management**: Stop-loss, take-profit, and daily loss limits
- ✅ **Anti-Over-Trading**: Minimum signal intervals to prevent excessive trading
- ✅ **Configurable Parameters**: Fully customizable RSI periods and thresholds
- ✅ **Comprehensive Testing**: Built-in backtesting and optimization framework
- ✅ **Alpaca Integration**: Ready for paper and live trading
- ✅ **Real-time Monitoring**: Performance tracking and risk alerts

## 📊 Strategy Description

### Core Logic

The Minutely RSI Strategy implements the following trading logic:

1. **Signal Generation**:
   - **BUY Signal**: When RSI crosses below the oversold threshold (default: 30)
   - **SELL Signal**: When RSI crosses above the overbought threshold (default: 70)

2. **Position Management**:
   - **Entry**: Uses 95% of available capital for position sizing
   - **Exit**: Either via RSI signal reversal or risk management rules

3. **Risk Management**:
   - **Stop-Loss**: 2% maximum loss per trade
   - **Take-Profit**: 4% target profit per trade
   - **Daily Loss Limit**: 5% maximum daily portfolio loss
   - **Signal Filtering**: Minimum 5-minute intervals between signals

### Strategy Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `rsi_period` | 14 | 10-28 | RSI calculation period |
| `oversold_threshold` | 30 | 20-35 | RSI level for buy signals |
| `overbought_threshold` | 70 | 65-80 | RSI level for sell signals |
| `max_position_size` | 0.95 | 0.5-1.0 | Maximum position allocation |
| `stop_loss_pct` | 0.02 | 0.01-0.05 | Stop-loss percentage |
| `take_profit_pct` | 0.04 | 0.02-0.08 | Take-profit percentage |
| `max_daily_loss` | 0.05 | 0.03-0.10 | Daily loss limit |
| `min_signal_interval` | 5 | 1-60 | Minimum minutes between signals |

## 📁 Project Structure

```
rsi-minutely/
├── main.py                    # Main algorithm implementation
├── config.json               # Local configuration parameters
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
├── research/                 # Research and analysis
│   └── rsi_analysis.ipynb   # Jupyter notebook for strategy research
├── data/                     # Data directory (created by Lean)
├── output/                   # Backtest output directory
├── backtests/               # Backtest results (created by Lean)
├── cloud_config/            # QuantConnect Cloud configuration
│   └── cloud-deployment.json # Cloud deployment settings
└── tests/                   # Unit tests (future enhancement)
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- QuantConnect Lean CLI installed
- Alpaca API credentials (for trading)

### Local Setup

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd rsi-minutely

   # Or download and extract the ZIP file
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Alpaca API Keys** (Optional, for paper/live trading)
   ```bash
   export ALPACA_API_KEY="your_api_key"
   export ALPACA_SECRET_KEY="your_secret_key"
   export ALPACA_ENVIRONMENT="paper"  # or "live"
   ```

4. **Verify Installation**
   ```bash
   lean validate
   ```

## ⚙️ Configuration

### Local Configuration (config.json)

The `config.json` file contains strategy parameters that can be modified:

```json
{
  "algorithm-language": "Python",
  "parameters": {
    "rsi_period": 14,
    "oversold_threshold": 30,
    "overbought_threshold": 70,
    "max_position_size": 0.95,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.04,
    "max_daily_loss": 0.05,
    "min_signal_interval": 5
  }
}
```

### Alpaca Configuration

For live trading, configure Alpaca in the Lean configuration or environment variables:

```bash
# Environment variables
export ALPACA_API_KEY="your_api_key"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_ENVIRONMENT="paper"  # or "live"

# Or in Lean CLI commands
lean create-algorithm --brokerage Alpaca --start 2023-01-01 --end 2023-12-31
```

## 🎮 Usage

### Local Backtesting

1. **Run Basic Backtest**
   ```bash
   lean backtest
   ```

2. **Run with Custom Parameters**
   ```bash
   lean backtest --algorithm-file main.py --start 2023-01-01 --end 2023-12-31
   ```

3. **Run with Specific Parameters**
   ```bash
   lean backtest --algorithm-file main.py \
     --parameters '{"rsi_period": 21, "oversold_threshold": 25, "overbought_threshold": 75}'
   ```

### Research and Analysis

1. **Open Research Notebook**
   ```bash
   lean research
   ```

2. **Run Research Notebook**
   - The notebook opens in your browser
   - Execute cells to analyze the strategy
   - Modify parameters and re-run analysis

### Optimization

1. **Run Parameter Optimization**
   ```bash
   lean optimize --algorithm-file main.py \
     --parameters rsi_period=10..28:2,oversold_threshold=20..35:2,overbought_threshold=65..80:2
   ```

2. **Run Specific Optimization**
   ```bash
   lean optimize --target SharpeRatio --max-steps 100 \
     --parameters oversold_threshold=25..35:1,overbought_threshold=65..75:1
   ```

## 📈 Backtesting

### Running Backtests

```bash
# Basic backtest
lean backtest

# Custom date range
lean backtest --start 2023-06-01 --end 2023-12-31

# With specific parameters
lean backtest --parameters '{"rsi_period": 21, "oversold_threshold": 25}'
```

### Understanding Results

Backtest results are saved to the `backtests/` directory with timestamps. Key metrics include:

- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of executed trades

### Sample Output

```
=== FINAL ALGORITHM RESULTS ===
Total Signals Generated: 42
Initial Portfolio Value: $100,000.00
Final Portfolio Value: $107,234.56
Total Return: 7.23%
Total Fees Paid: $23.45
RSI Period Used: 14
Stop Loss/Take Profit: 2.0%/4.0%
```

## 🔍 Optimization

### Parameter Ranges

The strategy supports optimization of key parameters:

- **RSI Period**: 10-28 (step: 2)
- **Oversold Threshold**: 20-35 (step: 2)
- **Overbought Threshold**: 65-80 (step: 2)
- **Stop-Loss**: 1-5% (step: 0.5%)
- **Take-Profit**: 2-8% (step: 1%)

### Optimization Commands

```bash
# Full parameter optimization
lean optimize --algorithm-file main.py --target SharpeRatio --max-steps 200

# Specific parameters
lean optimize --parameters oversold_threshold=20..35:1,overbought_threshold=65..75:1

# Multi-objective optimization
lean optimize --target SharpeRatio --max-steps 100 --constraint "TotalReturn > 0.05"
```

### Best Practices

1. **Walk-Forward Analysis**: Use rolling windows for robust optimization
2. **Out-of-Sample Testing**: Reserve data for final validation
3. **Multiple Objectives**: Balance returns, Sharpe ratio, and drawdown
4. **Parameter Sensitivity**: Test parameter stability

## 🚀 Live Trading

### Prerequisites

1. **Alpaca Account**: Paper trading for testing, live account for production
2. **API Credentials**: Valid API key and secret
3. **Capital**: Minimum recommended capital of $10,000

### Paper Trading

1. **Deploy to Paper Trading**
   ```bash
   lean live --algorithm-file main.py --brokerage Alpaca --paper
   ```

2. **Monitor Results**
   - Check real-time performance in QuantConnect dashboard
   - Review trade logs and execution quality
   - Validate performance matches backtests

### Live Trading

⚠️ **Important**: Only proceed to live trading after thorough paper trading validation.

1. **Deploy to Live Trading**
   ```bash
   lean live --algorithm-file main.py --brokerage Alpaca
   ```

2. **Monitor and Manage**
   - Real-time performance monitoring
   - Risk limit enforcement
   - Regular strategy review and optimization

## 🛡️ Risk Management

### Built-in Risk Controls

1. **Position Limits**:
   - Maximum 95% of portfolio in single position
   - No leverage or margin usage

2. **Stop-Loss Orders**:
   - 2% automatic stop-loss per trade
   - Cannot be disabled or modified

3. **Take-Profit Rules**:
   - 4% target profit per trade
   - RSI reversal signals for manual exits

4. **Daily Loss Limits**:
   - 5% maximum daily portfolio loss
   - Automatic trading suspension if breached

5. **Signal Filtering**:
   - Minimum 5-minute intervals between signals
   - Prevents over-trading and excessive fees

### Risk Monitoring

- **Real-time P&L tracking**
- **Drawdown monitoring**
- **Trade execution quality**
- **Transaction cost analysis**

### Emergency Controls

- **Manual override capability**
- **Immediate position liquidation**
- **Automatic trading suspension**
- **Alert notifications**

## 📊 Performance Analysis

### Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Annual Return | >15% | Compounded daily returns |
| Sharpe Ratio | >1.0 | Risk-adjusted returns |
| Max Drawdown | <10% | Peak-to-trough analysis |
| Win Rate | >45% | Winning trades / Total trades |
| Profit Factor | >1.3 | Gross profit / Gross loss |
| Transaction Costs | <0.5% | Cost per dollar traded |

### Performance Tracking

The strategy automatically tracks:

- **Trade-level performance**
- **Signal accuracy and frequency**
- **Risk metrics and limits**
- **Execution quality and slippage**
- **Transaction cost impact**

## ☁️ Cloud Deployment

### Deployment Options

1. **QuantConnect Cloud Platform**:
   - Full cloud deployment with managed infrastructure
   - Real-time data feeds and execution
   - Professional monitoring and alerting

2. **Hybrid Approach**:
   - Local development and testing
   - Cloud deployment for live trading
   - Automated deployment pipeline

### Cloud Configuration

The `cloud_config/cloud-deployment.json` file contains deployment settings:

```json
{
  "projectName": "Minutely RSI Strategy",
  "brokerage": "Alpaca",
  "accountType": "Equity",
  "deploymentTargets": {
    "backtest": true,
    "paper_trading": true,
    "live_trading": true
  }
}
```

### Deployment Steps

1. **Upload to QuantConnect**:
   ```bash
   lean cloud upload
   ```

2. **Create Cloud Project**:
   - Login to QuantConnect Cloud
   - Create new algorithm project
   - Upload algorithm files

3. **Configure Deployment**:
   - Set brokerage to Alpaca
   - Configure data feeds
   - Set up notifications

4. **Deploy and Monitor**:
   - Launch backtests
   - Deploy to paper trading
   - Monitor performance

## 📚 Documentation

### Research Notebook

The `research/rsi_analysis.ipynb` notebook provides comprehensive analysis:

1. **Data Exploration**: Historical data analysis and statistics
2. **RSI Behavior**: RSI calculation and signal analysis
3. **Parameter Optimization**: Multi-parameter optimization
4. **Backtesting Framework**: Strategy validation and testing
5. **Performance Analysis**: Results interpretation and insights

### Additional Documentation

- **Strategy Specification**: Detailed algorithm documentation
- **API Reference**: QuantConnect API usage guide
- **Alpaca Integration**: Brokerage setup and configuration
- **Troubleshooting**: Common issues and solutions

## 🧪 Testing

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end strategy testing
3. **Performance Tests**: Speed and memory optimization
4. **Stress Tests**: Extreme market condition testing

### Test Commands

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_rsi_strategy.py

# Run with coverage
python -m pytest --cov=strategy tests/
```

## 🔧 Troubleshooting

### Common Issues

1. **Data Issues**:
   - Check data availability and quality
   - Verify date ranges and resolutions
   - Ensure proper data permissions

2. **Execution Problems**:
   - Validate Alpaca API credentials
   - Check account balance and permissions
   - Review order management logic

3. **Performance Issues**:
   - Optimize RSI calculation parameters
   - Review signal frequency and filtering
   - Analyze transaction cost impact

### Debug Commands

```bash
# Enable debug logging
lean backtest --debug

# Check algorithm logs
lean logs --algorithm "Minutely RSI Strategy"

# Validate configuration
lean validate --algorithm-file main.py
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 standards
2. **Documentation**: Include comprehensive docstrings
3. **Testing**: Maintain high test coverage
4. **Performance**: Optimize for execution speed

### Contribution Process

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request
5. Code review and merge

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 📞 Support

For questions and support:

- **QuantConnect Community**: [community.quantconnect.com](https://community.quantconnect.com)
- **Documentation**: [lean.quantconnect.com](https://lean.quantconnect.com)
- **GitHub Issues**: Report bugs and feature requests
- **Alpaca Support**: [alpaca.markets/support](https://alpaca.markets/support)

## 📈 Strategy Performance Disclaimer

**Important**: Past performance does not guarantee future results. All trading strategies carry substantial risk of loss. This strategy is for educational and research purposes only. Always:

- Test thoroughly with paper trading
- Start with small position sizes
- Monitor performance continuously
- Consult with financial professionals
- Understand the risks involved

## 🗓️ Version History

- **v1.0.0** (Current): Initial release with core RSI strategy implementation
- **Future releases**: Enhanced risk management, additional indicators, portfolio optimization

---

**Developed with ❤️ using QuantConnect Lean CLI and Cloud Platform**

*For the latest updates and documentation, visit the project repository.*
