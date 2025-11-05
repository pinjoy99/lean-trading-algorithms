# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **QuantConnect Lean** algorithmic trading system with multiple strategies, a web-based dashboard for backtest analysis, and Alpaca brokerage integration. The repository contains:

- 4 complete trading strategies (SMA Crossover, RSI, Buy & Hold, Supertrend for Bitcoin)
- Interactive dashboard for visualizing backtest results
- Parameter optimization framework
- Multiple backtest runs with timestamped directories
- Alpaca API integration for market data and paper trading

## Repository Structure

```
/home/pinjoy/projects/lean/
├── lean.json                     # QuantConnect Lean configuration
├── alpaca_credentials.txt       # API credentials (paper trading)
├── download_spy_data.sh         # Data download script
├── ALPACA_*.md                  # Alpaca setup documentation
├── venv/                        # Python virtual environment
├── data/                        # Market data storage
├── storage/                     # Lean storage directory
├── sma-crossover/              # SMA crossover strategy
├── buy-and-hold-spy/           # Buy and hold baseline
├── rsi-minutely/               # RSI strategy
├── supertrend-btc/             # Bitcoin supertrend strategy
│   ├── backtests/             # Timestamped backtest results
│   │   └── 2025-11-04_20-49-37/
│   │       └── code/          # Backtest code
│   └── optimize.py            # Parameter optimization
└── dashboard/                  # Web dashboard
    ├── app.py                 # Flask application
    ├── requirements.txt       # Python dependencies
    ├── templates/             # HTML templates
    ├── static/                # CSS/JS assets
    └── data/                  # Backtest parser
```

## Strategy Patterns

All strategies follow QuantConnect Lean Python API structure:

```python
class StrategyName(QCAlgorithm):
    def initialize(self):
        # Set dates, cash, and add securities
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2023, 1, 31)
        self.set_cash(100000)
        self.symbol = self.add_equity("SPY", Resolution.MINUTE).symbol

        # Create indicators
        self.sma = self.SMA(self.symbol, 20, Resolution.MINUTE)

        # Track state
        self.is_invested = False

    def on_data(self, data: Slice):
        # Trading logic here
        pass
```

**Common Features Across Strategies:**
- Minute-level data resolution for high-frequency trading
- CSV export of minute-by-minute portfolio values
- Comprehensive logging and debug messages
- Risk management (stop-loss, position sizing)
- Signal tracking and performance statistics

## Common Commands

### Running Backtests

```bash
# Activate environment
source venv/bin/activate

# Run backtest for a specific strategy
lean backtest sma-crossover
lean backtest rsi-minutely
lean backtest buy-and-hold-spy
lean backtest supertrend-btc

# Run with custom parameters
lean backtest sma-crossover --algorithm-id sma-crossover --debug

# Run optimization
cd supertrend-btc
python optimize.py
```

### Data Management

```bash
# Download market data via Alpaca
./download_spy_data.sh

# Or interactive mode
source venv/bin/activate
lean data download
# Select: Alpaca (19) → US Equities → SPY → minute → 2023 dates

# Check downloaded data
ls -la data/equity/minute/SPY/
```

### Dashboard

```bash
cd dashboard

# Install dependencies
pip install -r requirements.txt

# Start dashboard
python app.py

# Access at http://localhost:5000/dashboard
# Features: Equity curves, drawdowns, monthly returns, trade analysis
```

### Parameter Optimization

```bash
cd supertrend-btc

# Run optimization script
python optimize.py

# Options:
# 1. Grid Search (comprehensive)
# 2. Walk-Forward Analysis (robustness)
# 3. Monte Carlo (statistical)
# 4. Sensitivity Analysis
# 5. Full Optimization Suite

# Save/Load results
# Results saved to: optimization_results.json
```

## Key Configuration Files

### lean.json
- **Alpaca Paper Trading**: Enabled by default with access token configured
- **Data Provider**: AlpacaBrokerage for market data
- **Environments**: backtesting, live-paper, live-alpaca, etc.
- **API Keys**: Contains hardcoded Alpaca paper trading token (line 123)

### Strategy Configuration
Each strategy has these parameters:
- **Date Range**: January 2023 (2023-01-01 to 2023-01-31)
- **Starting Capital**: $100,000
- **Resolution**: MINUTE for all strategies
- **Benchmark**: Set to traded security (SPY/BTCUSD)

### Dashboard Configuration
- **Framework**: Flask with Plotly.js
- **Data Format**: Parses QuantConnect backtest JSON
- **Port**: 5000 (configurable)
- **Dependencies**: Flask, pandas, plotly, numpy

## Backtest Results Structure

Backtest results stored in timestamped directories:
```
supertrend-btc/backtests/2025-11-04_20-49-37/
├── code/
│   ├── main.py                  # Strategy code
│   ├── optimize.py              # Optimization
│   ├── test_supertrend.py       # Unit tests
│   ├── research.py              # Research
│   └── Library/                 # Custom indicators
└── [backtest output files]
```

## Technical Indicators Used

1. **SMA (Simple Moving Average)**
   - Used in sma-crossover strategy
   - 5-minute fast, 40-minute slow

2. **RSI (Relative Strength Index)**
   - Used in rsi-minutely strategy
   - 14-period with 30/70 thresholds

3. **Supertrend**
   - Custom implementation in supertrend-btc
   - ATR-based with configurable multiplier

## Performance Tracking

Each strategy exports CSV files with minute-by-minute data:
- `sma_minute_equity_data.csv`
- `minute_equity_data.csv`
- `btc_minute_equity_data.csv`
- `buyhold_minute_equity_data.csv`

**CSV Format:**
```csv
timestamp,datetime_utc,open,high,low,close,volume,portfolio_value,equity
```

## Development Workflow

### Adding a New Strategy

1. **Create directory**: `mkdir new-strategy`
2. **Create main.py**: Follow QuantConnect template
3. **Configure**:
   - Set date range (e.g., January 2023)
   - Set starting cash ($100,000)
   - Add security with MINUTE resolution
4. **Test**: `lean backtest new-strategy`
5. **Optimize**: Create optimize.py if needed

### Testing Changes

```bash
# Run single backtest
lean backtest sma-crossover --debug

# Check logs
tail -f sma-crossover/backtest/main.py.log

# Review CSV exports
head -10 sma-crossover/sma_minute_equity_data.csv
```

### Dashboard Integration

After running backtests, results automatically appear in dashboard:
1. Start dashboard: `cd dashboard && python app.py`
2. Open: http://localhost:5000/dashboard
3. Select project from dropdown
4. View interactive charts and metrics

## API Integration

### Alpaca Setup

Already configured in lean.json:
- **Paper Trading**: Enabled (line 124: `"alpaca-paper-trading": "True"`)
- **Access Token**: Configured (line 123)
- **Environment**: paper (line 620)

To update credentials:
1. Edit: `alpaca_credentials.txt`
2. Or export environment variables:
   ```bash
   export ALPACA_API_KEY="your_key"
   export ALPACA_API_SECRET="your_secret"
   export ALPACA_ENVIRONMENT="paper"
   ```

### Data Download

Use Alpaca for market data:
```bash
source venv/bin/activate
lean data download
# Select: Alpaca (19) → Dataset → Symbols → Resolution → Dates
```

## Important Directories

- **`data/`**: Market data downloaded from Alpaca
- **`storage/`**: Lean persistent storage
- **`supertrend-btc/backtests/`**: All backtest results with timestamps
- **`dashboard/data/`**: Backtest result parser
- **`venv/`**: Python dependencies (do not modify)

## Best Practices

### Strategy Development
- Use `Resolution.MINUTE` for all strategies
- Implement `_export_minute_data()` for detailed tracking
- Add comprehensive debug logging
- Include on_end_of_algorithm() for final summary
- Use position sizing (max 95% of capital)

### Backtesting
- Test date range: January 2023 (consistent across strategies)
- Starting capital: $100,000
- Include warmup period for indicators
- Export minute-level data for analysis

### Optimization
- Use optimize.py for parameter tuning
- Include walk-forward analysis for robustness
- Test multiple time periods
- Save results for comparison

## Risk Management Features

**Implemented Across Strategies:**
- Stop-loss: 2% (rsi-minutely)
- Take-profit: 4% (rsi-minutely)
- Position sizing: 95% max allocation
- Daily loss limits: 5% (rsi-minutely)
- Minimum trade intervals: 5 minutes (rsi-minutely)
- Dynamic stop-loss: Supertrend levels (supertrend-btc)

## Common Issues & Solutions

**Data Not Found:**
```bash
# Download required data
lean data download --dataset "us-equity-security-master" --symbols "SPY"
```

**Backtest Fails:**
- Check lean.json configuration
- Verify date range has data
- Ensure API credentials are set

**Dashboard Empty:**
- Verify backtest completed successfully
- Check for backtest results in strategy directory
- Restart dashboard server

**Optimization Slow:**
- Reduce parameter ranges in optimize.py
- Use walk-forward analysis selectively
- Check disk space in backtests/

## Architecture Patterns

### Indicator Pattern
```python
# Create in initialize()
self.indicator = self.Indicator(self.symbol, period, Resolution.MINUTE)

# Use in on_data()
if self.indicator.is_ready:
    signal = self.indicator.current.value
```

### Data Export Pattern
```python
# In initialize()
self.minute_data_file = "strategy_data.csv"
self._write_minute_data_header()

# In on_data()
def _export_minute_data(self, data):
    if self.symbol in data:
        bar = data[self.symbol]
        # Write CSV line
```

### Trading Signal Pattern
```python
# Check signal conditions
if signal_condition and not self.is_invested:
    self.set_holdings(self.symbol, 0.95)
    self.is_invested = True

# Exit condition
elif exit_condition and self.is_invested:
    self.liquidate(self.symbol)
    self.is_invested = False
```

## Testing & Validation

Each strategy includes:
- Signal generation tracking
- Performance metrics logging
- Risk management validation
- CSV data export for external analysis

**Validation Commands:**
```bash
# Count signals generated
grep "BUY\|SELL" sma-crossover/backtest/main.py.log | wc -l

# Check CSV data
wc -l sma-crossover/sma_minute_equity_data.csv

# View equity curve
tail -20 sma-crossover/sma_minute_equity_data.csv
```

## Notes

- All strategies use **January 2023** for consistency
- Paper trading is enabled by default
- Minute-level data provides high granularity
- Dashboard requires separate Flask environment
- Backtest results are timestamped for version tracking
- Alpaca credentials are configured in lean.json
- No hardcoded API keys in strategy code (credentials via lean.json)

## Further Reading

- **QuantConnect Docs**: https://www.quantconnect.com/docs/v2/lean/cli/overview
- **Alpaca API**: https://alpaca.markets/docs/
- **Dashboard README**: dashboard/README.md
- **Strategy Documentation**: Individual strategy directories
