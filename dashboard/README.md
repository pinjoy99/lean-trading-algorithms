# QuantConnect Backtest Results Dashboard

An interactive web-based dashboard for visualizing and analyzing QuantConnect backtest results across multiple projects. Built with Flask, Plotly.js, and Bootstrap for a professional and responsive user experience.

## 🚀 Features

### Interactive Visualizations
- **Equity Curves**: Interactive portfolio value charts with zoom and pan
- **Drawdown Analysis**: Visual representation of peak-to-trough declines
- **Monthly Returns**: Bar charts showing performance by month
- **Trade Analysis**: Scatter plots and tables for trade-level insights
- **Performance Metrics**: Real-time KPI cards with color-coded indicators

### Multi-Project Support
- **Project Management**: Support for multiple QuantConnect projects
- **Backtest Comparison**: Side-by-side analysis of different runs
- **Data Aggregation**: Automatic detection of backtest results
- **Parameter Tracking**: Visual display of strategy configurations

### Professional Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean Bootstrap 5 interface with custom styling
- **Real-time Updates**: Auto-refresh capabilities
- **Export Functionality**: Download results as JSON

## 📁 Project Structure

```
dashboard/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── README.md               # This documentation
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── overview.html      # Dashboard overview page
│   └── project_dashboard.html # Project-specific analysis
├── static/                 # Static assets
│   ├── css/
│   │   └── dashboard.css  # Custom styling
│   └── js/
│       └── dashboard.js   # Interactive functionality
├── data/                   # Data processing
│   └── backtest_parser.py # QuantConnect JSON parser
├── sample_data/            # Example datasets
└── utils/                 # Utility functions
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Flask and related dependencies
- Access to QuantConnect backtest results

### Quick Start

1. **Navigate to dashboard directory**:
   ```bash
   cd /home/pinjoy/projects/lean/dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the dashboard**:
   ```bash
   python app.py
   ```

4. **Access the dashboard**:
   ```
   http://localhost:5000/dashboard
   ```

## 📊 Usage Guide

### Dashboard Overview
The main dashboard provides:
- **Project Statistics**: Overview of all available projects
- **Quick Actions**: Load sample data, export results, clear cache
- **Recent Activity**: Timeline of dashboard usage
- **Navigation**: Easy access to project-specific analysis

### Project Analysis
For each project, the dashboard provides:
- **Performance Metrics Cards**: Key statistics with color-coded indicators
- **Interactive Charts**: Equity curves, drawdown analysis, monthly returns
- **Trade Analysis Table**: Detailed trade history with filtering
- **Strategy Parameters**: Visual display of configuration settings

### Supported Projects
Currently supports:
- **rsi-minutely**: RSI-based trading strategy
- **sma-crossover**: Simple Moving Average crossover strategy
- **custom**: Any project with QuantConnect backtest results

## 🎯 Key Metrics Displayed

### Performance Metrics
- **Total Return**: Overall strategy performance
- **Annual Return**: Yearly compounded performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside risk-adjusted returns
- **Win Rate**: Percentage of profitable trades

### Risk Metrics
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Value at Risk (VaR)**: Potential losses at confidence levels
- **Volatility**: Annualized standard deviation
- **Expectancy**: Average return per trade

### Trading Metrics
- **Total Trades**: Number of executed trades
- **Profit/Loss Ratio**: Gross profit divided by gross loss
- **Portfolio Turnover**: Trading activity measure
- **Transaction Costs**: Total fees paid

## 🔧 Technical Details

### Backend (Flask)
- **Web Framework**: Flask with Jinja2 templates
- **API Endpoints**: RESTful JSON API for data retrieval
- **Data Processing**: Automatic parsing of QuantConnect JSON files
- **Caching**: In-memory caching for improved performance

### Frontend
- **Charts**: Plotly.js for interactive visualizations
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Modern ES6+ with module patterns
- **Styling**: Custom CSS with CSS Grid and Flexbox

### Data Sources
- **QuantConnect Results**: Automatic parsing of backtest JSON files
- **Dynamic Detection**: Scans project directories for new results
- **Multiple Formats**: Supports various QuantConnect output formats

## 📈 Chart Types

### Equity Curve
- **Interactive line chart** showing portfolio value over time
- **Hover tooltips** with exact values and dates
- **Zoom and pan** capabilities
- **Performance annotations** at key points

### Drawdown Analysis
- **Area chart** displaying drawdown periods
- **Peak identification** and recovery tracking
- **Risk visualization** with color-coded severity

### Monthly Returns
- **Bar chart** with positive/negative coloring
- **Performance comparison** across time periods
- **Rolling analysis** capabilities

### Trade Analysis
- **Scatter plots** for trade P&L distribution
- **Interactive tables** with sorting and filtering
- **Trade details** on hover and click

## 🎨 Customization

### Styling
Edit `static/css/dashboard.css` to customize:
- Color scheme and branding
- Layout and spacing
- Typography and fonts
- Responsive breakpoints

### Charts
Modify `static/js/dashboard.js` to:
- Add new chart types
- Customize hover tooltips
- Change color schemes
- Add interactive features

### Data Processing
Extend `data/backtest_parser.py` to:
- Support additional data formats
- Calculate custom metrics
- Add data transformations

## 🔌 API Reference

### Endpoints
- `GET /api/projects` - List available projects
- `GET /api/project/<name>/data` - Get project backtest data
- `GET /api/project/<name>/metrics` - Get calculated metrics

### Response Format
```json
{
  "summary": {
    "totalPerformance": {
      "portfolioStatistics": {...},
      "tradeStatistics": {...}
    }
  },
  "trades": [...],
  "equity_curve": [...],
  "project": "project_name"
}
```

## 🚀 Deployment

### Local Development
```bash
# Development server with auto-reload
python app.py

# Or with Flask development server
FLASK_ENV=development python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t dashboard .
docker run -p 5000:5000 dashboard
```

## 🐛 Troubleshooting

### Common Issues

**No Projects Found**
- Ensure backtest results are in the correct directories
- Check that QuantConnect JSON files are properly formatted
- Verify file permissions

**Charts Not Loading**
- Check browser console for JavaScript errors
- Ensure Plotly.js is loading correctly
- Verify data format matches expected structure

**Performance Issues**
- Clear browser cache
- Check network connectivity
- Monitor server resource usage

### Debug Mode
Enable debug mode by setting environment variable:
```bash
export FLASK_DEBUG=1
python app.py
```

## 📚 Examples

### RSI Strategy Dashboard
```bash
# Navigate to dashboard
cd /home/pinjoy/projects/lean/dashboard

# Install dependencies
pip install -r requirements.txt

# Start dashboard
python app.py

# Visit http://localhost:5000/dashboard
# Select "rsi-minutely" project
```

### Custom Project Integration
1. Place QuantConnect backtest results in project directory
2. Ensure JSON files follow standard format
3. Dashboard will automatically detect new projects
4. Access via project selection menu

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Submit pull request

### Code Style
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Maintain consistent formatting
- Add appropriate comments

## 📄 License

This dashboard is part of the QuantConnect trading system and follows the same licensing terms.

## 🆘 Support

For questions and support:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Refer to QuantConnect docs
- **Community**: QuantConnect forums and Discord

---

**Built with ❤️ for the QuantConnect Community**
