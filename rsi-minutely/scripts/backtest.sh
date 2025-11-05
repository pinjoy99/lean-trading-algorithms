#!/bin/bash

# RSI Strategy Backtest Script
# This script provides convenient backtesting commands for the RSI strategy

set -e

echo "🔄 RSI Strategy Backtesting Script"
echo "=================================="

# Function to display usage
usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  basic       Run basic backtest (default)"
    echo "  optimize    Run parameter optimization"
    echo "  research    Open research notebook"
    echo "  validate    Validate algorithm configuration"
    echo "  clean       Clean output directories"
    echo ""
    echo "Options:"
    echo "  --start DATE    Start date (YYYY-MM-DD)"
    echo "  --end DATE      End date (YYYY-MM-DD)"
    echo "  --debug         Enable debug logging"
    echo ""
    echo "Examples:"
    echo "  $0 basic --start 2023-01-01 --end 2023-12-31"
    echo "  $0 optimize --start 2022-01-01 --end 2023-12-31"
    echo "  $0 basic --debug"
    echo ""
}

# Default parameters
START_DATE="2023-01-01"
END_DATE="2023-12-31"
DEBUG=false
COMMAND="basic"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --start)
            START_DATE="$2"
            shift 2
            ;;
        --end)
            END_DATE="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        basic|optimize|research|validate|clean)
            COMMAND="$1"
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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the RSI strategy directory."
    exit 1
fi

# Function to validate algorithm
validate() {
    echo "🔍 Validating algorithm configuration..."
    if lean validate; then
        echo "✅ Algorithm validation passed"
    else
        echo "❌ Algorithm validation failed"
        exit 1
    fi
}

# Function to run basic backtest
run_backtest() {
    echo "📊 Running basic backtest..."
    echo "📅 Date range: $START_DATE to $END_DATE"

    CMD="lean backtest --algorithm-file main.py --start $START_DATE --end $END_DATE"

    if [ "$DEBUG" = true ]; then
        CMD="$CMD --debug"
    fi

    echo "🔄 Executing: $CMD"
    if eval $CMD; then
        echo "✅ Backtest completed successfully"
        echo "📁 Results saved to: output/"
    else
        echo "❌ Backtest failed"
        exit 1
    fi
}

# Function to run optimization
run_optimization() {
    echo "⚙️ Running parameter optimization..."
    echo "📅 Date range: $START_DATE to $END_DATE"

    CMD="lean optimize --algorithm-file main.py --start $START_DATE --end $END_DATE"

    if [ "$DEBUG" = true ]; then
        CMD="$CMD --debug"
    fi

    echo "🔄 Executing: $CMD"
    if eval $CMD; then
        echo "✅ Optimization completed successfully"
        echo "📁 Results saved to: output/"
    else
        echo "❌ Optimization failed"
        exit 1
    fi
}

# Function to open research notebook
run_research() {
    echo "🔬 Opening research notebook..."
    if lean research; then
        echo "✅ Research notebook opened in browser"
    else
        echo "❌ Failed to open research notebook"
        exit 1
    fi
}

# Function to clean output directories
clean_output() {
    echo "🧹 Cleaning output directories..."
    rm -rf output/* 2>/dev/null || true
    rm -rf backtests/* 2>/dev/null || true
    rm -rf logs/* 2>/dev/null || true
    echo "✅ Output directories cleaned"
}

# Main execution
case $COMMAND in
    basic)
        # validate  # Skip validation - lean validate doesn't exist
        run_backtest
        ;;
    optimize)
        # validate  # Skip validation - lean validate doesn't exist
        run_optimization
        ;;
    research)
        run_research
        ;;
    validate)
        echo "✅ Skipping validation (not available in this Lean version)"
        exit 0
        ;;
    clean)
        clean_output
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        usage
        exit 1
        ;;
esac

echo ""
echo "🎉 RSI Strategy backtest script completed!"
echo "📊 Check the output/ directory for results"
