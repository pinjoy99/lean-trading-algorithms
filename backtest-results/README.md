# Backtest Results Archive

This directory contains the latest backtest results from all QuantConnect Lean trading strategies.

## 📁 Directory Structure

### 1. SMA Crossover (`sma-crossover/`)
- **Latest Backtest**: November 4, 2025 at 10:51:27
- **Strategy**: Simple Moving Average crossover with 5/40 minute periods
- **File**: `1186467672.json` - Complete backtest output
- **Source Code**: `code/main.py` - Strategy implementation
- **Research**: `code/research.ipynb` - Analysis notebook

**Key Files:**
- `1186467672-summary.json` - Performance metrics summary
- `1186467672-order-events.json` - All orders and transactions
- `1186467672-log.txt` - Execution logs

### 2. RSI Minutely (`rsi-minutely/`)
- **Latest Backtest**: November 3, 2025 at 15:21:35
- **Strategy**: Mean reversion using 14-period RSI
- **File**: `1983772575.json` - Complete backtest output
- **Source Code**: `code/main.py` - Strategy implementation
- **Analysis**: `code/research/rsi_analysis.ipynb` - Research notebook

**Key Files:**
- `1983772575-summary.json` - Performance metrics summary
- `1983772575-order-events.json` - All orders and transactions
- `1983772575-log.txt` - Execution logs

### 3. Buy & Hold SPY (`buy-and-hold-spy/`)
- **Latest Backtest**: November 4, 2025 at 20:59:36
- **Strategy**: Baseline buy-and-hold for comparison
- **File**: `1654346112.json` - Complete backtest output
- **Source Code**: `code/main.py` - Strategy implementation
- **Research**: `code/research.ipynb` - Analysis notebook

**Key Files:**
- `1654346112-summary.json` - Performance metrics summary
- `1654346112-order-events.json` - All orders and transactions
- `1654346112-log.txt` - Execution logs

### 4. Supertrend BTC (`supertrend-btc/`)
- **Latest Backtest**: November 4, 2025 at 20:49:37
- **Strategy**: Advanced Bitcoin trading with custom Supertrend indicator
- **File**: `1422993005.json` - Complete backtest output
- **Source Code**: `code/main.py` - Strategy implementation
- **Optimization**: `code/optimize.py` - Parameter optimization
- **Custom Library**: `code/Library/technical_indicators/supertrend.py`

**Key Files:**
- `1422993005-summary.json` - Performance metrics summary
- `1422993005-order-events.json` - All orders and transactions
- `1422993005-log.txt` - Execution logs

## 📊 Common File Types

### Summary Files (`*-summary.json`)
Contains key performance metrics:
- Total return and annualized return
- Sharpe ratio
- Maximum drawdown
- Total trades
- Win rate
- Trading fees

### Main Backtest Files (`*.json`)
Complete backtest output including:
- All equity curves
- Trade information
- Performance statistics
- Algorithm state

### Order Events Files (`*-order-events.json`)
Detailed record of every order:
- Order timestamp
- Symbol
- Quantity
- Price
- Status (filled, cancelled, etc.)
- Fill price and quantity

### Data Monitor Reports (`data-monitor-report-*.json`)
Quality assurance data:
- Data requests status
- Failed requests
- Succeeded requests
- Coverage statistics

## 🔍 How to Use

### View Performance Summary
```bash
cat sma-crossover/1186467672-summary.json | python -m json.tool
```

### Analyze Trades
```bash
cat rsi-minutely/1983772575-order-events.json | python -m json.tool
```

### Run Your Own Analysis
```bash
# Load backtest data in Python
import json

with open('sma-crossover/1186467672.json', 'r') as f:
    data = json.load(f)

# Access performance metrics
print(data['TotalPerformance']['PortfolioStatistics'])
```

## 📅 Update Schedule

These results represent the **latest** backtest runs from each strategy. To get fresh results:

1. Run a new backtest:
   ```bash
   lean backtest sma-crossover
   ```

2. Copy the results here:
   ```bash
   cp -r sma-crossover/backtests/[timestamp]/* backtest-results/sma-crossover/
   ```

3. Commit and push:
   ```bash
   git add backtest-results/
   git commit -m "Update backtest results"
   git push
   ```

## 🎯 Note

The original backtest runs are stored in each strategy's `backtests/` directory with full history. This `backtest-results/` directory contains only the **latest** run for each strategy in an organized format for easy access.

## 📚 Related Documentation

- **Main README**: `/README.md`
- **Strategy Documentation**: `/strategy-directories/`
- **QuantConnect Docs**: https://www.quantconnect.com/docs
