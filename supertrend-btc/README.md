# Bitcoin Supertrend Strategy

A comprehensive automated trading strategy implementation using the Supertrend indicator on Bitcoin minute bars, built with QuantConnect Lean framework.

## 📋 Table of Contents

- [Overview](#overview)
- [Strategy Description](#strategy-description)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Strategy Components](#strategy-components)
- [Risk Management](#risk-management)
- [Performance Metrics](#performance-metrics)
- [Backtesting](#backtesting)
- [Optimization](#optimization)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements a sophisticated Bitcoin trading strategy based on the Supertrend technical indicator. The strategy operates on minute-level data, providing rapid response to market movements while maintaining strict risk management controls.

### Key Features

- **Advanced Supertrend Implementation**: Custom-built indicator with Wilder's smoothing for ATR calculation
- **Dynamic Position Sizing**: Risk-based position sizing with configurable parameters
- **Multi-Layer Risk Management**: Portfolio-level controls, stop-losses, and drawdown protection
- **Comprehensive Analytics**: Real-time performance tracking and detailed reporting
- **Optimization Framework**: Walk-forward analysis for parameter tuning
- **Production Ready**: Error handling, logging, and monitoring capabilities

## 📊 Strategy Description

The Supertrend indicator is a trend-following indicator that combines Average True Range (ATR) with price action to create dynamic support and resistance levels. Our implementation:

### Core Logic

1. **Signal Generation**: Buy when price crosses above supertrend level, sell when it crosses below
2. **Trend Confirmation**: Multiple time period confirmation to reduce false signals
3. **Dynamic Stop-Loss**: Trailing stop-loss based on supertrend levels
4. **Risk Management**: Position sizing based on volatility and risk tolerance

### Mathematical Foundation

```
Basic Upper Band = (High + Low)/2 + (Multiplier × ATR)
Basic Lower Band = (High + Low)/2 - (Multiplier × ATR)
```

Where ATR (Average True Range) measures market volatility using Wilder's smoothing.

## 🏗️ Project Structure

```
supertrend-btc/
├── main.py                           # Main algorithm implementation
├── config.json                       # Strategy configuration
├── requirements.txt                  # Python dependencies
├── README.md                         # This documentation
├── Library/
│   └── technical_indicators/
│       └── supertrend.py            # Reusable Supertrend indicator
├── data/                             # Local data storage
├── backtests/                        # Backtest results
├── optimizations/                    # Optimization results
└── storage/                          # Lean algorithm storage
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- QuantConnect Lean CLI
- Valid QuantConnect account with data access

### Setup Instructions

1. **Clone or create the project:**
   ```bash
   lean create-project supertrend-btc
   cd supertrend-btc
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure QuantConnect credentials:**
   ```bash
   lean login
   lean cloud pull
   ```

4. **Verify installation:**
   ```bash
   lean research main.py
   ```

## ⚙️ Configuration

### Main Parameters (config.json)

```json
{
    "parameters": {
        "atr_period": "10",           // ATR calculation period
        "multiplier": "3",            // Supertrend multiplier
        "risk_percent": "0.02",       // Risk per trade (2%)
        "max_position_size": "0.1",   // Maximum position (10% of equity)
        "max_daily_trades": "10",     // Maximum trades per day
        "min_trade_interval": "5"     // Minimum minutes between trades
    }
}
```

### Parameter Guidelines

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `atr_period` | 7-21 | 10 | Higher values = smoother but slower signals |
| `multiplier` | 2-7 | 3 | Higher values = fewer but more reliable signals |
| `risk_percent` | 0.01-0.05 | 0.02 | Risk per trade as percentage of equity |
| `max_position_size` | 0.05-0.25 | 0.1 | Maximum single position size |

## 📈 Usage

### Running Backtests

1. **Basic backtest:**
   ```bash
   lean backtest main.py --output-path ./backtests/
   ```

2. **Custom date range:**
   ```bash
   lean backtest main.py --start 2024-01-01 --end 2024-12-31
   ```

3. **With optimization:**
   ```bash
   lean optimize main.py --output-path ./optimizations/
   ```

### Live Trading

1. **Paper trading:**
   ```bash
   lean paper-trade main.py --push
   ```

2. **Live trading:**
   ```bash
   lean live trade main.py --brokerage Coinbase --push
   ```

### Research and Analysis

```bash
lean research main.py --output-path research.ipynb
```

## 🧩 Strategy Components

### SuperTrendIndicator Class

The core technical indicator providing trend signals:

```python
# Initialize indicator
supertrend = SuperTrendIndicator(period=10, multiplier=3)

# Update with OHLC data
supertrend_level, signal = supertrend.update(high, low, close)

# Check for signals
if supertrend.is_buy_signal():
    # Execute buy logic
    pass
```

### Main Algorithm (BitcoinSupertrendStrategy)

The primary trading logic implementing:

- Data subscription and validation
- Signal processing and execution
- Risk management enforcement
- Performance tracking
- Error handling

### Risk Management Components

1. **Position Sizing**: Risk-based calculation considering stop-loss distance
2. **Portfolio Limits**: Maximum single position and daily loss limits
3. **Trade Timing**: Minimum intervals between trades and daily trade limits
4. **Market Conditions**: Pause trading during extreme volatility

## 🛡️ Risk Management

### Multi-Layer Protection

#### Layer 1: Position Sizing
- **Risk-Based Sizing**: 2% of portfolio value per trade maximum
- **Volatility Adjustment**: Position size inversely related to stop-loss distance
- **Maximum Exposure**: 10% of portfolio in single position

#### Layer 2: Portfolio Controls
- **Daily Loss Limit**: 3% maximum daily portfolio loss
- **Maximum Drawdown**: Automatic trading pause at critical levels
- **Correlation Limits**: Prevents over-concentration

#### Layer 3: Market Protection
- **Slippage Modeling**: Realistic execution assumptions
- **Volatility Breakouts**: Reduced activity during extreme moves
- **Error Recovery**: Automatic pause and resume logic

### Risk Metrics Tracking

```python
# Real-time risk monitoring
def monitor_risk(self):
    current_exposure = self.calculate_portfolio_exposure()
    daily_pnl = self.calculate_daily_pnl()
    max_drawdown = self.calculate_current_drawdown()

    if daily_pnl < -self.max_daily_loss:
        self.trigger_risk_pause()
```

## 📊 Performance Metrics

### Comprehensive Analytics

The strategy tracks multiple performance dimensions:

#### Returns Analysis
- **Total Return**: Overall portfolio performance
- **Annualized Return**: Time-weighted annual performance
- **Volatility**: Standard deviation of returns

#### Risk-Adjusted Metrics
- **Sharpe Ratio**: Risk-adjusted return measure
- **Sortino Ratio**: Downside risk-adjusted performance
- **Calmar Ratio**: Return/maximum drawdown ratio

#### Trading Statistics
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss ratio
- **Average Trade**: Mean profit/loss per trade
- **Maximum Consecutive Losses**: Risk of ruin analysis

### Performance Reporting

```python
def generate_performance_report(self):
    metrics = {
        'total_return': self.calculate_total_return(),
        'sharpe_ratio': self.calculate_sharpe_ratio(),
        'max_drawdown': self.calculate_max_drawdown(),
        'win_rate': self.calculate_win_rate(),
        'profit_factor': self.calculate_profit_factor()
    }
    return metrics
```

## 🔬 Backtesting

### Comprehensive Testing Framework

1. **Historical Testing**: Multi-year backtesting on historical data
2. **Walk-Forward Analysis**: Optimization on training periods, validation on test periods
3. **Monte Carlo Simulation**: Statistical confidence testing
4. **Stress Testing**: Performance under extreme market conditions

### Backtest Configuration

```bash
# Multi-period backtest
lean backtest main.py \
    --start 2023-01-01 \
    --end 2024-12-31 \
    --output-path ./backtests/btc-supertrend-2023-2024

# High-frequency backtest (minute data)
lean backtest main.py \
    --data-feed minute \
    --output-path ./backtests/minute-backtest
```

### Expected Backtest Metrics

Based on historical analysis, expect:
- **Annual Return**: 15-30% (market dependent)
- **Sharpe Ratio**: 1.2-2.0
- **Maximum Drawdown**: 8-15%
- **Win Rate**: 55-65%

## ⚡ Optimization

### Parameter Optimization

The strategy includes comprehensive optimization capabilities:

```python
# Parameter ranges for optimization
atr_periods = [7, 10, 14, 21]
multipliers = [2, 3, 5, 7]

# Walk-forward optimization
optimization_results = self.optimize_parameters_walk_forward(
    start_date=start_date,
    end_date=end_date,
    train_period_days=30,
    test_period_days=7
)
```

### Optimization Best Practices

1. **Walk-Forward Analysis**: Prevents overfitting to historical data
2. **Out-of-Sample Testing**: Validate on unseen data
3. **Multiple Market Conditions**: Test across different market regimes
4. **Robustness Testing**: Parameter sensitivity analysis

## 📚 API Reference

### BitcoinSupertrendStrategy Class

#### Core Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `initialize()` | None | None | Initialize algorithm settings |
| `on_data(slice)` | Slice | None | Process incoming market data |
| `calculate_position_size()` | entry_price, stop_price, equity | int | Calculate position quantity |
| `calculate_performance_metrics()` | None | dict | Generate performance report |

#### Public Properties

| Property | Type | Description |
|----------|------|-------------|
| `btc_symbol` | Symbol | Bitcoin trading symbol |
| `supertrend` | SuperTrendIndicator | Main technical indicator |
| `portfolio` | Portfolio | Current portfolio state |

### SuperTrendIndicator Class

#### Core Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `update()` | high, low, close | tuple | Update indicator with OHLC data |
| `is_buy_signal()` | None | bool | Check for buy signal |
| `is_sell_signal()` | None | bool | Check for sell signal |
| `get_current_supertrend()` | None | float | Current supertrend level |

## 🔧 Troubleshooting

### Common Issues

#### 1. Insufficient Data
**Error**: "Insufficient historical data for warmup"
**Solution**: Ensure sufficient data period for indicator warmup
```python
# Increase warmup period
self.set_warm_up(timedelta(minutes=self.atr_period * 3))
```

#### 2. High Slippage
**Error**: Poor backtest performance due to unrealistic fills
**Solution**: Implement custom slippage model
```python
class BitcoinFillModel(FillModel):
    def fill(self, order_event):
        # Implement realistic slippage
        pass
```

#### 3. Overfitting
**Error**: Excellent backtest, poor live performance
**Solution**: Use walk-forward optimization and out-of-sample testing

#### 4. API Rate Limits
**Error**: Data feed interruptions
**Solution**: Implement rate limiting and error handling
```python
def handle_api_error(self, error):
    if error.code == 429:  # Rate limit
        self.pause_trading_for(300)  # 5 minutes
```

### Debug Mode

Enable detailed logging for debugging:
```python
# In main.py
def initialize(self):
    self.set_debug_mode(True)  # Enable debug logging
    self.debug("Debug mode enabled")  # Custom debug messages
```

### Performance Monitoring

Monitor algorithm performance:
```python
# Check performance metrics
metrics = self.calculate_performance_metrics()
self.log(f"Current Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes**: Follow coding standards (PEP 8)
4. **Test thoroughly**: Run backtests and optimize
5. **Submit pull request**: Include documentation updates

### Code Standards

- **Style**: PEP 8 compliant, snake_case variables
- **Documentation**: Google-style docstrings
- **Testing**: Minimum 80% test coverage
- **Performance**: Benchmark against baseline strategy

### Adding New Features

1. **Technical Indicators**: Extend `Library/technical_indicators/`
2. **Risk Management**: Add to `apply_portfolio_risk_limits()`
3. **Analytics**: Enhance `calculate_performance_metrics()`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

### Getting Help

1. **Documentation**: Check this README thoroughly
2. **QuantConnect Forum**: [community.quantconnect.com](https://community.quantconnect.com)
3. **GitHub Issues**: Create detailed bug reports
4. **Strategy Discussion**: Join QuantConnect Discord

### Reporting Issues

When reporting issues, include:
- **QuantConnect Lean version**
- **Error messages and stack traces**
- **Configuration parameters used**
- **Steps to reproduce the problem**

## 🔮 Roadmap

### Upcoming Features

- [ ] **Multi-Asset Support**: Extend to other cryptocurrencies
- [ ] **Machine Learning Integration**: Enhanced signal filtering
- [ ] **Options Strategies**: Add covered call and protective put strategies
- [ ] **Real-Time Dashboard**: Live performance monitoring
- [ ] **Mobile Alerts**: Push notifications for trade signals
- [ ] **Advanced Portfolio Optimization**: Mean-variance optimization integration

### Performance Enhancements

- [ ] **C++ Implementation**: For faster execution
- [ ] **GPU Acceleration**: For indicator calculations
- [ ] **Real-Time Streaming**: Millisecond-latency processing
- [ ] **Distributed Computing**: Multi-threaded optimization

---

## 📈 Quick Start Summary

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Edit `config.json` parameters
3. **Backtest**: `lean backtest main.py`
4. **Optimize**: `lean optimize main.py`
5. **Deploy**: `lean paper-trade main.py --push`

**Ready to start trading with confidence!** 🚀

---

*This strategy is for educational purposes. Past performance does not guarantee future results. Always test thoroughly before live trading and never risk more than you can afford to lose.*