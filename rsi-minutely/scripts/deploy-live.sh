#!/bin/bash

# RSI Strategy Live Trading Deployment Script
# This script deploys the RSI strategy to paper or live trading

set -e

echo "🚀 RSI Strategy Live Trading Deployment"
echo "======================================"

# Function to display usage
usage() {
    echo "Usage: $0 [environment] [options]"
    echo ""
    echo "Environments:"
    echo "  paper      Deploy to paper trading (recommended for testing)"
    echo "  live       Deploy to live trading (use with caution!)"
    echo ""
    echo "Options:"
    echo "  --api-key KEY    Alpaca API key"
    echo "  --secret SECRET  Alpaca secret key"
    echo "  --net-id ID      Network ID for cloud deployment"
    echo "  --no-validate    Skip pre-deployment validation"
    echo ""
    echo "Examples:"
    echo "  $0 paper --api-key YOUR_KEY --secret YOUR_SECRET"
    echo "  $0 live --api-key YOUR_KEY --secret YOUR_SECRET --net-id NET_ID"
    echo ""
    echo "⚠️  WARNING: Live trading involves real money and risk!"
    echo "   Always start with paper trading first."
}

# Default parameters
ENVIRONMENT=""
API_KEY=""
SECRET_KEY=""
NETWORK_ID=""
VALIDATE=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        paper|live)
            ENVIRONMENT="$1"
            shift
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --secret)
            SECRET_KEY="$2"
            shift 2
            ;;
        --net-id)
            NETWORK_ID="$2"
            shift 2
            ;;
        --no-validate)
            VALIDATE=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$ENVIRONMENT" ]; then
    echo "❌ Error: Environment (paper or live) is required"
    usage
    exit 1
fi

if [ -z "$API_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ Error: API key and secret key are required"
    usage
    exit 1
fi

# Check environment type
if [ "$ENVIRONMENT" = "live" ]; then
    echo "⚠️  WARNING: You are deploying to LIVE TRADING!"
    echo "   This will use real money. Are you sure? (Type 'yes' to continue)"
    read -r confirmation
    if [ "$confirmation" != "yes" ]; then
        echo "❌ Deployment cancelled"
        exit 0
    fi
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the RSI strategy directory."
    exit 1
fi

# Pre-deployment validation
if [ "$VALIDATE" = true ]; then
    echo "🔍 Pre-deployment validation..."

    # Check if Lean CLI is installed
    if ! command -v lean &> /dev/null; then
        echo "❌ Lean CLI is not installed. Please install it first."
        exit 1
    fi

    # Validate algorithm
    echo "  Validating algorithm..."
    if ! lean validate --algorithm-file main.py; then
        echo "❌ Algorithm validation failed"
        exit 1
    fi

    # Check dependencies
    echo "  Checking dependencies..."
    python -c "import pandas, numpy" 2>/dev/null || {
        echo "❌ Required dependencies not installed. Run: pip install -r requirements.txt"
        exit 1
    }

    echo "✅ Pre-deployment validation passed"
fi

# Set Alpaca environment
ALPACA_ENV="paper"
if [ "$ENVIRONMENT" = "live" ]; then
    ALPACA_ENV="live"
fi

# Export environment variables
export ALPACA_API_KEY="$API_KEY"
export ALPACA_SECRET_KEY="$SECRET_KEY"
export ALPACA_ENVIRONMENT="$ALPACA_ENV"

echo "📋 Deployment Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Alpaca Environment: $ALPACA_ENV"
echo "  Algorithm: main.py"
echo ""

# Deploy based on environment
if [ "$ENVIRONMENT" = "paper" ]; then
    echo "📊 Deploying to paper trading..."
    echo "🔄 Executing: lean live --algorithm-file main.py --brokerage Alpaca --paper"

    if [ -n "$NETWORK_ID" ]; then
        echo "🔄 Using network ID: $NETWORK_ID"
        lean live --algorithm-file main.py --brokerage Alpaca --paper --net-id "$NETWORK_ID"
    else
        lean live --algorithm-file main.py --brokerage Alpaca --paper
    fi

elif [ "$ENVIRONMENT" = "live" ]; then
    echo "💰 Deploying to live trading..."
    echo "🔄 Executing: lean live --algorithm-file main.py --brokerage Alpaca"

    if [ -n "$NETWORK_ID" ]; then
        echo "🔄 Using network ID: $NETWORK_ID"
        lean live --algorithm-file main.py --brokerage Alpaca --net-id "$NETWORK_ID"
    else
        lean live --algorithm-file main.py --brokerage Alpaca
    fi
fi

echo ""
echo "✅ Deployment initiated successfully!"
echo ""
echo "📱 Next Steps:"
echo "  1. Monitor the deployment in QuantConnect dashboard"
echo "  2. Check the logs for any errors or warnings"
echo "  3. Verify that trading signals are being generated"
echo "  4. Monitor performance and risk metrics"
echo ""
echo "⚠️  Important Reminders:"
echo "  - Paper trading: Monitor but no real money at risk"
echo "  - Live trading: Monitor closely - real money at risk!"
echo "  - Keep logs and performance records"
echo "  - Review and adjust parameters as needed"
echo ""
echo "📞 Support:"
echo "  - QuantConnect Community: community.quantconnect.com"
echo "  - Documentation: lean.quantconnect.com"
