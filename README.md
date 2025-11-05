# QuantConnect Lean Trading Algorithms

A comprehensive algorithmic trading system built with QuantConnect Lean, featuring multiple trading strategies, an interactive dashboard, and Alpaca brokerage integration.

## 🚀 Features

### Trading Strategies
- **SMA Crossover** - Simple Moving Average crossover strategy for SPY
- **RSI Strategy** - Mean reversion using RSI with 14-period indicator
- **Buy & Hold** - Baseline strategy for performance comparison
- **Supertrend BTC** - Advanced cryptocurrency strategy using Supertrend indicator

### Tools & Components
- 📊 **Interactive Dashboard** - Web-based backtest analysis with Plotly
- 🔧 **Parameter Optimization** - Grid search, walk-forward, and Monte Carlo analysis
- 📈 **Real-time Analytics** - Minute-by-minute portfolio tracking
- 🔐 **Alpaca Integration** - Paper trading and market data via Alpaca API
- 🧪 **Comprehensive Testing** - Unit tests and validation frameworks

## 📁 Project Structure

```
lean/
├── lean.json                     # QuantConnect configuration
├── alpaca_credentials.txt       # API credentials
├── README.md                     # This file
├── sma-crossover/               # SMA strategy
├── rsi-minutely/                # RSI strategy
├── buy-and-hold-spy/            # Buy and hold baseline
├── supertrend-btc/              # Bitcoin Supertrend strategy
│   ├── optimize.py              # Parameter optimization
│   └── test_supertrend.py       # Unit tests
└── dashboard/                   # Web dashboard
    ├── app.py                   # Flask application
    ├── templates/               # HTML templates
    └── static/                  # CSS/JS assets
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- QuantConnect Lean CLI
- Alpaca API account (for live trading)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd lean
```

2. **Install dependencies**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure Alpaca credentials**
```bash
# Edit alpaca_credentials.txt or set environment variables
export ALPACA_API_KEY="your_key"
export ALPACA_API_SECRET="your_secret"
export ALPACA_ENVIRONMENT="paper"
```

4. **Download market data**
```bash
./download_spy_data.sh
# Or interactively: lean data download
```

### Running Backtests

```bash
# Activate environment
source venv/bin/activate

# Run backtests for each strategy
lean backtest sma-crossover
lean backtest rsi-minutely
lean backtest buy-and-hold-spy
lean backtest supertrend-btc

# Run parameter optimization
cd supertrend-btc
python optimize.py
```

### Starting the Dashboard

```bash
cd dashboard
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000/dashboard in your browser.

## 📊 Strategy Details

### 1. SMA Crossover
- **Symbol**: SPY
- **Indicators**: 5-minute and 40-minute Simple Moving Averages
- **Logic**: Buy when fast SMA crosses above slow SMA
- **Resolution**: Minute-level data

### 2. RSI Strategy
- **Symbol**: SPY
- **Indicators**: 14-period RSI
- **Thresholds**: Buy at RSI < 30, Sell at RSI > 70
- **Risk Management**: 2% stop-loss, 4% take-profit

### 3. Buy & Hold
- **Symbol**: SPY
- **Logic**: Simple baseline strategy
- **Purpose**: Performance comparison

### 4. Supertrend BTC
- **Symbol**: BTCUSD
- **Indicators**: Custom Supertrend with ATR
- **Features**: Dynamic stop-loss levels
- **Optimization**: Available via optimize.py

## 🔧 Configuration

### Backtest Settings
- **Date Range**: January 2023 (2023-01-01 to 2023-01-31)
- **Starting Capital**: $100,000
- **Resolution**: MINUTE for all strategies
- **Benchmark**: Respective traded security

### Alpaca Configuration
Paper trading is enabled by default in `lean.json`:
- **Environment**: paper
- **Brokerage**: Alpaca
- **Data Provider**: Alpaca API

## 📈 Performance Analysis

Each strategy exports minute-by-minute data:
```csv
timestamp,datetime_utc,open,high,low,close,volume,portfolio_value,equity
```

Use the dashboard to visualize:
- Equity curves
- Drawdowns
- Monthly returns
- Trade analysis
- Signal tracking

## 🔐 Security Best Practices

- ✅ API keys are never hardcoded
- ✅ Credentials via environment variables or config files
- ✅ Paper trading by default
- ✅ No sensitive data in repository
- ✅ `.gitignore` excludes credentials and data

## 📚 Documentation

- [QuantConnect Lean Docs](https://www.quantconnect.com/docs/v2/lean/cli/overview)
- [Alpaca API Docs](https://alpaca.markets/docs/)
- [Strategy-specific README files](./strategy-directories/)
- [CLAUDE.md](./CLAUDE.md) - Developer guide

## 🧪 Testing

```bash
# Run unit tests
cd supertrend-btc
python test_supertrend.py

# Check backtest logs
tail -f sma-crossover/backtest/main.py.log

# Validate CSV exports
head -10 sma-crossover/sma_minute_equity_data.csv
```

## 📊 Optimization

### Grid Search
```bash
cd supertrend-btc
python optimize.py
# Select option 1 for comprehensive grid search
```

### Walk-Forward Analysis
- Robustness testing across different time periods
- Out-of-sample validation

### Monte Carlo
- Statistical confidence intervals
- Risk assessment

## 🚀 Deployment

### Live Trading
```bash
# Switch to live environment
lean cloud live sma-crossover --open

# Or use paper trading
lean backtest rsi-minutely --debug
```

### Custom Deployment
Edit `lean.json` to configure:
- Live trading credentials
- Brokerage settings
- Data providers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-strategy`
3. Commit changes: `git commit -m "feat: add new strategy"`
4. Push to branch: `git push origin feature/new-strategy`
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.

## ⚠️ Disclaimer

This software is for educational purposes only. Past performance does not guarantee future results. Always:
- Test thoroughly before live trading
- Never risk more than you can afford to lose
- Understand the risks involved in algorithmic trading
- Consider consulting a financial advisor

## 📞 Support

- Create an issue for bugs or feature requests
- Review existing documentation
- Check QuantConnect community forums

---

**Built with ❤️ using QuantConnect Lean and Alpaca API**
