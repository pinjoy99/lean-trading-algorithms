#!/bin/bash

# QuantConnect Backtest Dashboard Startup Script
# This script starts the interactive dashboard for viewing backtest results

set -e

echo "🚀 Starting QuantConnect Backtest Dashboard"
echo "=================================="

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --install    Install dependencies only"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start dashboard"
    echo "  $0 --install          # Install dependencies only"
    echo ""
}

# Function to install dependencies
install_deps() {
    echo "📦 Installing dashboard dependencies..."
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "Installing Python packages..."
    pip install -r requirements.txt

    echo "✅ Dependencies installed successfully!"
}

# Function to check if dependencies are installed
check_deps() {
    python3 -c "import flask, plotly, pandas, numpy" 2>/dev/null
    return $?
}

# Function to start dashboard
start_dashboard() {
    echo "🔍 Checking dependencies..."

    if ! check_deps; then
        echo "❌ Dependencies not found. Installing..."
        install_deps
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Check if we're in the right directory
    if [ ! -f "app.py" ]; then
        echo "❌ Error: app.py not found. Please run this script from the dashboard directory."
        exit 1
    fi

    echo ""
    echo "📊 Dashboard Information:"
    echo "  • Local URL: http://localhost:5000/dashboard"
    echo "  • API URL: http://localhost:5000/api"
    echo "  • Supported Projects: rsi-minutely, sma-crossover"
    echo ""
    echo "💡 Usage Tips:"
    echo "  • Visit the dashboard URL in your browser"
    echo "  • Select a project to view its backtest results"
    echo "  • Explore interactive charts and metrics"
    echo "  • Press Ctrl+C to stop the dashboard"
    echo ""
    echo "🚀 Starting dashboard..."
    echo ""

    # Start the Flask application
    python app.py
}

# Parse command line arguments
case "${1:-}" in
    --install)
        install_deps
        ;;
    --help|-h)
        usage
        ;;
    "")
        start_dashboard
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        usage
        exit 1
        ;;
esac
