#!/bin/bash
# Script to download SPY data for 2023 using Alpaca

echo "Starting interactive data download with Alpaca..."

# First, set up environment variables if not already set
if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_API_SECRET" ]; then
    echo "⚠️  Alpaca credentials not found!"
    echo "Please run:"
    echo "export ALPACA_API_KEY=\"your_key_here\""
    echo "export ALPACA_API_SECRET=\"your_secret_here\""
    echo "export ALPACA_ENVIRONMENT=\"paper\""
    exit 1
fi

source venv/bin/activate

# Run the download with pre-configured responses
echo "19" | lean data download

# Note: This will prompt you through the wizard
# Select:
# 1. Provider: Alpaca (option 19)
# 2. Dataset: US Equities
# 3. Symbol: SPY
# 4. Resolution: minute
# 5. Date Range: 2023-01-01 to 2023-12-31
