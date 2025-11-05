# Alpaca Setup Guide for Lean CLI Data Download

## 📋 Overview
This guide will walk you through setting up Alpaca brokerage integration with QuantConnect Lean CLI for downloading historical market data.

## 🎯 What You'll Accomplish
- Create a free Alpaca trading account
- Generate API credentials
- Configure Lean CLI for Alpaca authentication
- Download historical market data for backtesting

---

## Step 1: Create Alpaca Account

### 1.1 Sign Up for Alpaca
1. **Visit**: https://alpaca.markets/
2. **Click**: "Sign Up" or "Get Started"
3. **Choose Account Type**:
   - **Paper Trading** (Recommended for beginners - free, no real money)
   - **Live Trading** (Real money, requires verification)

### 1.2 Complete Registration
- **Email Verification**: Check your email and verify account
- **Personal Information**: Provide basic details (name, address, etc.)
- **Identity Verification**: Upload ID documents if required
- **Financial Information**: Employment status, income, etc.

### 1.3 Account Approval
- **Paper Trading**: Usually instant approval
- **Live Trading**: May take 1-2 business days

---

## Step 2: Generate API Credentials

### 2.1 Access API Dashboard
1. **Log in** to your Alpaca account
2. **Go to**: Dashboard → API Keys (or sidebar menu)

### 2.2 Create New API Key
1. **Click**: "Create New Key" or "Generate API Key"
2. **Name Your Key**: e.g., "QuantConnect-LEAN"
3. **Set Permissions**:
   - ✅ **Trading**: Enabled (if you plan to trade)
   - ✅ **Data**: Enabled (required for data download)
   - ⚠️ **Avoid**: Admin permissions unless necessary

### 2.3 Save Credentials
**🔐 IMPORTANT**: Save these immediately - you won't see the secret again!

```
✅ API Key ID: AK... (starts with 'AK')
✅ Secret Key: AS... (starts with 'AS')
```

**Example Format**:
```
API Key: AKBBBBBBBBBBBBBBBBBB
Secret: abcdef1234567890abcdef1234567890abcdef12

Live Key: AKTBPOLM6RJRBQNGRJYLUS3P3H
Live Secret: CAN2GEN18pum3P1Vp1EVqtdy94cfEQZ19gWGMHQ3AWRM

Paper Key: PKYVAOAKYTKZL6D6057P
Paper Secret: DoiMwYqyqi3Jk8cjd4FUybskdjCKeTW4vEkeuBLwYzeQ

```

### 2.4 Environment Setup
For paper trading (recommended):
```
Alpaca Paper API Base URL: https://paper-api.alpaca.markets
```

For live trading:
```
Alpaca Live API Base URL: https://api.alpaca.markets
```

---

## Step 3: Configure Lean CLI for Alpaca

### 3.1 Set Alpaca Credentials
Run these commands in your terminal:

```bash
# Set Alpaca API credentials
export ALPACA_API_KEY="your_api_key_here"
export ALPACA_API_SECRET="your_secret_here"

# Set environment (paper or live)
export ALPACA_ENVIRONMENT="paper"  # or "live"
```

### 3.2 Verify Credentials
```bash
# Test connection (if available)
curl -H "APCA-API-KEY-ID: $ALPACA_API_KEY" \
     -H "APCA-API-SECRET-KEY: $ALPACA_API_SECRET" \
     https://paper-api.alpaca.markets/v2/account
```

---

## Step 4: Download Historical Data

### 4.1 Interactive Mode (Recommended for first-time users)
```bash
source venv/bin/activate
lean data download
```

**The wizard will prompt you for:**
- Dataset: Choose "Alpaca Equities" or "Alpaca Crypto"
- Symbols: SPY, AAPL, QQQ, etc.
- Resolution: Minute, Hour, Daily
- Date Range: Start and end dates
- Data Type: Trades, Quotes, Bars

### 4.2 Non-Interactive Mode (Advanced)

#### Example 1: Download SPY minute data
```bash
source venv/bin/activate
lean data download \
  --dataset "us-equity-security-master" \
  --symbols "SPY" \
  --security-type "equity" \
  --resolution "minute" \
  --start "2023-01-01" \
  --end "2023-12-31" \
  --alpaca-api-key "$ALPACA_API_KEY" \
  --alpaca-api-secret "$ALPACA_API_SECRET" \
  --alpaca-environment "paper"
```

#### Example 2: Download multiple symbols
```bash
source venv/bin/activate
lean data download \
  --dataset "us-equity-security-master" \
  --symbols "SPY,AAPL,QQQ,IWM" \
  --security-type "equity" \
  --resolution "daily" \
  --start "2022-01-01" \
  --end "2023-12-31"
```

#### Example 3: Download crypto data
```bash
source venv/bin/activate
lean data download \
  --dataset "us-crypto-security-master" \
  --symbols "BTCUSD,ETHUSD" \
  --security-type "crypto" \
  --resolution "hour" \
  --start "2023-01-01" \
  --end "2023-12-31"
```

### 4.3 Common Dataset Names
- **Equities**: `us-equity-security-master`
- **Crypto**: `us-crypto-security-master`
- **Options**: `us-option-security-master` (if available)

---

## Step 5: Verify Data Download

### 5.1 Check Data Location
```bash
# List downloaded data
ls -la Lean/Data/

# Find your specific data
find Lean/Data/ -name "*.csv" | grep -i spy
```

### 5.2 View Data Format
```bash
# Preview the data
head -10 Lean/Data/equity/minute/spy/2023-01-01.csv
```

### 5.3 Data Structure
Typical columns:
- **Timestamp**: ISO 8601 format
- **Open, High, Low, Close**: Price data
- **Volume**: Trading volume
- **Trade Count**: Number of trades
- **VWAP**: Volume weighted average price

---

## Step 6: Use Downloaded Data in Lean

### 6.1 Configure Your Algorithm
Update `main.py`:
```python
# Use Alpaca data provider
self.set_dataNormalization(DataNormalizationMode.Adjusted)
```

### 6.2 Run Backtest
```bash
# Use downloaded data
source venv/bin/activate
lean backtest your-project
```

---

## 🎯 Data Pricing & Limits

### Alpaca Data Costs
- **Free Tier**: Limited historical data
- **Paid Plans**:
  - **Starter**: $9/month
  - **Gold**: $49/month
  - **Platinum**: $149/month

### Limits (Free Tier)
- Historical data: Up to 1 year
- Rate limits: 200 requests/minute
- Real-time data: Delayed

### Recommendations
- **Start with paper trading** and free tier
- **Test with smaller datasets** first
- **Upgrade** if you need more data/real-time feeds

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Authentication Failed
**Error**: "Invalid API key"
**Solution**:
- Verify your API key format (starts with AK)
- Check environment (paper vs live)
- Regenerate keys if needed

#### 2. Insufficient Permissions
**Error**: "API key lacks required permissions"
**Solution**:
- Create new API key with Trading and Data permissions
- Avoid "Admin" permissions (unnecessary)

#### 3. Rate Limits
**Error**: "Too many requests"
**Solution**:
- Add delays between requests
- Use smaller date ranges
- Upgrade plan for higher limits

#### 4. No Data Returned
**Possible Causes**:
- Symbol not supported by Alpaca
- Date range outside available data
- Wrong security type (equity vs crypto)

### Getting Help
- **Alpaca Documentation**: https://alpaca.markets/docs/
- **QuantConnect Forum**: https://www.quantconnect.com/forum
- **Lean CLI Help**: `lean --help`

---

## ✅ Next Steps

### After Successful Setup
1. **Test Data Quality**: Verify data matches expectations
2. **Run Backtests**: Use downloaded data for strategy testing
3. **Implement Strategy**: Build algorithms using Alpaca data
4. **Deploy Live**: Switch to live trading when ready

### Recommended First Project
1. Download SPY daily data for 1 year
2. Create simple moving average strategy
3. Run backtest
4. Analyze results
5. Iterate and improve

---

## 📞 Support

If you encounter issues:
1. **Check this guide** for common solutions
2. **Review Alpaca API documentation**
3. **Post in QuantConnect forum**
4. **Contact Alpaca support** for brokerage-specific issues

---

**Setup Time**: ~30 minutes  \n**Skill Level**: Beginner to Intermediate  \n**Cost**: Free (with limitations) to $9+/month  \n**Last Updated**: November 2025
