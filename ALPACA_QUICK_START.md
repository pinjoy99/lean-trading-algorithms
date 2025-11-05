# Alpaca Quick Start Checklist

## ✅ Step-by-Step Setup (30 Minutes)

### Before You Start
- [ ] Free Alpaca account created
- [ ] Paper Trading enabled (recommended)
- [ ] API Key generated
- [ ] API Secret saved securely

### Quick Commands

#### 1. Set Credentials
```bash
export ALPACA_API_KEY="your_api_key_here"
export ALPACA_API_SECRET="your_secret_here"
export ALPACA_ENVIRONMENT="paper"
```

#### 2. Download Data (Interactive Mode)
```bash
source venv/bin/activate
lean data download
```

#### 3. Download Data (Direct Example)
```bash
source venv/bin/activate
lean data download \
  --dataset "us-equity-security-master" \
  --symbols "SPY" \
  --security-type "equity" \
  --resolution "minute" \
  --start "2023-10-01" \
  --end "2023-10-31"
```

#### 4. Verify Data
```bash
ls -la Lean/Data/equity/minute/SPY/2023-10-01.csv
```

## 📋 What You Need

### From Alpaca Account
1. **API Key**: Starts with `AK`
2. **Secret Key**: Starts with `AS`
3. **Environment**: `paper` or `live`

### From Terminal
1. **Lean CLI**: Already installed
2. **Docker**: Running (for Lean)
3. **Terminal Access**: Command line access

## 🎯 Common Downloads

### SPY Daily (1 Year)
```bash
--symbols "SPY" \
--resolution "daily" \
--start "2023-01-01" \
--end "2023-12-31"
```

### Multiple Stocks Daily
```bash
--symbols "SPY,AAPL,QQQ,IWM" \
--resolution "daily"
```

### Crypto Hourly
```bash
--dataset "alpacabrokerage-crypto" \
--symbols "BTCUSD,ETHUSD" \
--security-type "crypto" \
--resolution "hour"
```

## ❓ Need Help?

- **Full Guide**: `ALPACA_SETUP_GUIDE.md`
- **Commands**: `ALPACA_DATA_COMMANDS.md`
- **Errors**: Check troubleshooting section in setup guide

## 🚀 Next Steps

1. Create Alpaca account
2. Generate API keys
3. Run download command
4. Test data with backtest
5. Build your strategy!

**Time to Complete**: ~30 minutes
**Cost**: Free (paper trading)
