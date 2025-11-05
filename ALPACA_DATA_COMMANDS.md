# Alpaca Data Download Commands

## Quick Reference Commands

### 1. Set Environment Variables
```bash
# Your Alpaca API credentials (replace with actual values)
export ALPACA_API_KEY="AKBBBBBBBBBBBBBBBBBB"
export ALPACA_API_SECRET="abcdef1234567890abcdef1234567890abcdef12"
export ALPACA_ENVIRONMENT="paper"  # or "live"
```

### 2. Interactive Download (Recommended)
```bash
source venv/bin/activate
lean data download
```

### 3. Non-Interactive Downloads

#### A. Download SPY Minute Data (1 Month)
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

#### B. Download Multiple Equities Daily Data (1 Year)
```bash
source venv/bin/activate
lean data download \
  --dataset "us-equity-security-master" \
  --symbols "SPY,AAPL,QQQ,IWM" \
  --security-type "equity" \
  --resolution "daily" \
  --start "2023-01-01" \
  --end "2023-12-31"
```

#### C. Download Crypto Hourly Data
```bash
source venv/bin/activate
lean data download \
  --dataset "alpacabrokerage-crypto" \
  --symbols "BTCUSD,ETHUSD" \
  --security-type "crypto" \
  --resolution "hour" \
  --start "2023-01-01" \
  --end "2023-12-31"
```

#### D. Download SPY Options Data
```bash
source venv/bin/activate
lean data download \
  --dataset "alpacabrokerage-option" \
  --symbols "SPY" \
  --security-type "option" \
  --resolution "minute" \
  --start "2023-10-01" \
  --end "2023-10-31"
```

### 4. Check Downloaded Data
```bash
# List all downloaded data
find Lean/Data/ -name "*.csv" -type f | head -20

# Check SPY data
ls -la Lean/Data/equity/minute/spy/2023/

# View data sample
head -10 Lean/Data/equity/minute/spy/2023-10-01.csv
```

### 5. Clean Up Data (if needed)
```bash
# Remove specific symbol data
rm -rf Lean/Data/equity/minute/SPY/

# Remove all downloaded data
rm -rf Lean/Data/*
```

## Command Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--dataset` | Data source | `us-equity-security-master` |
| `--symbols` | Trading symbols | `SPY,AAPL,QQQ` |
| `--security-type` | Asset type | `equity`, `crypto`, `option` |
| `--resolution` | Data frequency | `minute`, `hour`, `daily` |
| `--start` | Start date | `2023-01-01` |
| `--end` | End date | `2023-12-31` |
| `--alpaca-api-key` | API key | `AK...` |
| `--alpaca-api-secret` | API secret | `AS...` |
| `--alpaca-environment` | Paper or live | `paper` or `live` |

## Data Storage Location
```
Lean/
└── Data/
    ├── equity/
    │   ├── minute/
    │   │   └── SPY/
    │   │       └── 2023-10-01.csv
    │   └── daily/
    └── crypto/
        └── hour/
            └── BTCUSD/
                └── 2023-01-01.csv
```

## Tips
1. Start with paper trading environment
2. Use smaller date ranges for testing
3. Check data before running full backtests
4. Free tier has limited data - upgrade if needed
