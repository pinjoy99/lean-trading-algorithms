# ✅ Alpaca Data Download - CORRECTED METHOD

## The Issue
We tried non-interactive commands with incorrect dataset names. The solution is to use **interactive mode**.

## ✅ CORRECT COMMAND

### Step 1: Run Interactive Download
```bash
source venv/bin/activate
lean data download
```

### Step 2: Follow the Wizard Prompts
When the wizard starts, select these options:

1. **Organization**: Choose your org
2. **Dataset**: Select "US Equities" (this is where Alpaca equity data lives)
3. **Data Type**: 
   ```
   1) Trade
   2) Quote  
   3) Bulk
   ```
   Choose `1` for Trade data
4. **Ticker(s)**: 
   ```
   SPY,AAPL,QQQ
   ```
5. **Resolution**:
   ```
   1) Tick
   2) Second
   3) Minute
   4) Hour
   5) Daily
   ```
   Choose `3` for Minute or `5` for Daily
6. **Start Date** (YYYYMMDD):
   ```
   20231001
   ```
7. **End Date** (YYYYMMDD):
   ```
   20231231
   ```
8. **Review & Confirm**: Check the QCC cost, accept agreements

### What This Downloads
- SPY, AAPL, QQQ data
- Minute or Daily resolution  
- Oct-Dec 2023 period
- Stored in `Lean/Data/` directory

## 📋 Why This Works

The **interactive wizard** automatically selects the correct dataset (`US Equities`) and handles Alpaca authentication when you provide your API credentials later.

## 🔐 After Data Download

### Set Alpaca Credentials for Live Trading
```bash
export ALPACA_API_KEY="your_key_here"
export ALPACA_API_SECRET="your_secret_here"
export ALPACA_ENVIRONMENT="paper"
```

### Use in Algorithm
Your downloaded data is now available for backtesting:
```bash
source venv/bin/activate
lean backtest sma-crossover
```

## ❌ What We Learned

**Don't use non-interactive mode** with specific dataset names like:
- ❌ `--dataset "alpacabrokerage-equity"`
- ❌ `--dataset "us-equity-security-master"`

**DO use interactive mode**:
- ✅ `lean data download` (then select options)

## 🎯 Next Steps

1. Run the interactive command above
2. Follow the wizard prompts  
3. Download your data
4. Test with backtest
5. Deploy live with Alpaca credentials

This is the **recommended and supported approach** for downloading market data in Lean CLI!
