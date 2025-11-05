# Dataset Name Correction - Alpaca Data Download

## ❌ The Issue
When you tried to download data with:
```bash
lean data download \
  --dataset "alpacabrokerage-equity" \
  ...
```

You got this error:
```
Error: There is no dataset named 'alpacabrokerage-equity'
```

## ✅ The Fix

The issue was using the **incorrect dataset name**. I've corrected all documentation files and here's the proper command:

### Correct Command
```bash
source venv/bin/activate
lean data download \
  --dataset "us-equity-security-master" \
  --symbols "SPY" \
  --security-type "equity" \
  --resolution "minute" \
  --start "2023-01-01" \
  --end "2023-12-31"
```

### Quick Test Command (1 Month of Data)
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

## 📋 Correct Dataset Names

| Asset Type | Dataset Name |
|-----------|-------------|
| **Equities** | `us-equity-security-master` |
| **Crypto** | `us-crypto-security-master` |
| **Options** | `us-option-security-master` |

## 🔧 Files Updated

I've corrected the following files:
- ✅ `ALPACA_SETUP_GUIDE.md` - Fixed all dataset references
- ✅ `ALPACA_DATA_COMMANDS.md` - Updated command examples
- ✅ `ALPACA_QUICK_START.md` - Corrected quick reference commands

## 🚀 Next Steps

1. **Try the corrected command** above
2. **Use interactive mode** if you prefer:
   ```bash
   source venv/bin/activate
   lean data download
   ```
3. **Select** "US Equities" when prompted in the wizard

## 💡 Why the Confusion?

The name "alpacabrokerage-equity" makes sense conceptually (Alpaca + equity data), but QuantConnect uses different naming conventions for their datasets. The "us-equity-security-master" is the actual dataset identifier in their system.

## 🎯 Alternative Approach

You can also use the interactive wizard which will show you all available datasets:
```bash
source venv/bin/activate
lean data download
```

Then just follow the prompts to select "US Equities" dataset and your desired symbols.

---

**Try the corrected command now - it should work!**
