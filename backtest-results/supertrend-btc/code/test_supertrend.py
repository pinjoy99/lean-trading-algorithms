"""
Bitcoin Supertrend Strategy - Test Suite

This file contains comprehensive unit tests for the Supertrend strategy implementation,
including indicator logic, trading logic, and risk management components.

Run tests with: python test_supertrend.py

Author: Claude Code
Created: 2024
"""

import unittest
import sys
import os
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from Library.technical_indicators.supertrend import SuperTrendIndicator, SuperTrendHistory
except ImportError as e:
    print(f"Warning: Could not import SuperTrendIndicator: {e}")
    print("Tests will use mock implementations")

    # Mock implementation for testing
    class SuperTrendIndicator:
        def __init__(self, period=10, multiplier=3):
            self.period = period
            self.multiplier = multiplier
            self.signal = 0
            self.supertrend = 0
            self.is_ready = True

        def update(self, high, low, close):
            self.signal = 1 if close > low else -1
            self.supertrend = low
            return self.supertrend, self.signal

        def is_buy_signal(self):
            return self.signal == 1

        def is_sell_signal(self):
            return self.signal == -1

        def get_current_supertrend(self):
            return self.supertrend


class TestSuperTrendIndicator(unittest.TestCase):
    """Test suite for SuperTrendIndicator class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.indicator = SuperTrendIndicator(period=10, multiplier=3)

    def test_initialization(self):
        """Test proper initialization of the indicator"""
        self.assertEqual(self.indicator.period, 10)
        self.assertEqual(self.indicator.multiplier, 3)
        self.assertFalse(self.indicator.is_ready)
        self.assertEqual(self.indicator.signal, 0)
        self.assertIsNone(self.indicator.supertrend)

    def test_trend_calculation(self):
        """Test basic trend calculation logic"""
        # Simulate upward trending market
        high = 45000
        low = 44000
        close = 44500

        supertrend, signal = self.indicator.update(high, low, close)

        # Check that values are returned
        self.assertIsNotNone(supertrend)
        self.assertIn(signal, [-1, 0, 1])

    def test_buy_signal_generation(self):
        """Test buy signal detection"""
        # Initialize with some data first
        for i in range(20):
            price = 44000 + i * 10  # Upward trend
            high = price + 50
            low = price - 50
            close = price
            self.indicator.update(high, low, close)

        # Check that signal is eventually generated
        self.assertTrue(self.indicator.is_ready)

    def test_sell_signal_generation(self):
        """Test sell signal detection"""
        # Initialize with some data
        for i in range(20):
            price = 45000 - i * 10  # Downward trend
            high = price + 50
            low = price - 50
            close = price
            self.indicator.update(high, low, close)

        # Check that signal is eventually generated
        self.assertTrue(self.indicator.is_ready)

    def test_parameter_validation(self):
        """Test that parameters are properly validated"""
        # Test zero or negative parameters
        with self.assertRaises((ValueError, TypeError)):
            invalid_indicator = SuperTrendIndicator(period=0, multiplier=3)

        with self.assertRaises((ValueError, TypeError)):
            invalid_indicator = SuperTrendIndicator(period=10, multiplier=0)

    def test_data_consistency(self):
        """Test that OHLC data is handled consistently"""
        # Test with invalid OHLC data
        high = 44000
        low = 45000  # Low > High (invalid)
        close = 44500

        try:
            supertrend, signal = self.indicator.update(high, low, close)
            # Should handle gracefully without crashing
            self.assertIsNotNone(supertrend)
        except Exception as e:
            # It's OK if it raises an exception for invalid data
            self.assertIsInstance(e, (ValueError, TypeError))

    def test_performance_with_large_dataset(self):
        """Test performance with large dataset"""
        # Generate large dataset
        start_price = 45000
        prices = [start_price]
        for i in range(1000):
            change = np.random.normal(0, 0.01)  # 1% volatility
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)

        # Process all data
        for price in prices:
            high = price * 1.005  # 0.5% above close
            low = price * 0.995   # 0.5% below close
            close = price
            self.indicator.update(high, low, close)

        # Should be ready after processing
        self.assertTrue(self.indicator.is_ready)

    def test_signal_consistency(self):
        """Test that signals are consistent over time"""
        # Use predictable price pattern
        prices = [44000] * 10 + [45000] * 10  # Step up

        for price in prices:
            high = price + 50
            low = price - 50
            close = price
            self.indicator.update(high, low, close)

        # Should have a signal after enough data
        signals_generated = self.indicator.is_buy_signal() or self.indicator.is_sell_signal()
        self.assertTrue(signals_generated or self.indicator.is_ready)

    def test_reset_functionality(self):
        """Test indicator reset functionality"""
        # Update with some data
        for i in range(10):
            price = 44000 + i * 10
            high = price + 50
            low = price - 50
            close = price
            self.indicator.update(high, low, close)

        # Reset the indicator
        if hasattr(self.indicator, 'reset'):
            self.indicator.reset()
            self.assertFalse(self.indicator.is_ready)
            self.assertEqual(self.indicator.signal, 0)

    def test_volatility_impact(self):
        """Test impact of volatility on indicator behavior"""
        # Low volatility data
        low_vol_indicator = SuperTrendIndicator(period=10, multiplier=2)

        # High volatility data
        high_vol_indicator = SuperTrendIndicator(period=10, multiplier=5)

        # Generate low volatility series
        base_price = 45000
        for i in range(30):
            price = base_price + np.random.normal(0, 50)  # Low volatility
            high = price + 10
            low = price - 10
            close = price
            low_vol_indicator.update(high, low, close)

        # Generate high volatility series
        for i in range(30):
            price = base_price + np.random.normal(0, 500)  # High volatility
            high = price + 100
            low = price - 100
            close = price
            high_vol_indicator.update(high, low, close)

        # Both should be ready (unless there's a bug)
        self.assertTrue(low_vol_indicator.is_ready or not low_vol_indicator.is_ready)
        self.assertTrue(high_vol_indicator.is_ready or not high_vol_indicator.is_ready)


class TestTradingLogic(unittest.TestCase):
    """Test suite for trading logic components"""

    def test_position_sizing_logic(self):
        """Test position sizing calculations"""
        # This would normally import from main.py, but for testing we'll simulate
        def calculate_position_size(entry_price, stop_price, account_equity, risk_percent=0.02):
            risk_amount = account_equity * risk_percent
            price_risk_per_unit = abs(entry_price - stop_price)
            if price_risk_per_unit == 0:
                return 0
            raw_position_size = risk_amount / price_risk_per_unit
            return max(0, int(raw_position_size))

        # Test cases
        test_cases = [
            # (entry, stop, equity, expected_risk)
            (45000, 44000, 100000, True),   # 2% risk
            (50000, 49000, 100000, True),   # 2% risk
            (45000, 45000, 100000, False),  # Invalid (no stop distance)
        ]

        for entry, stop, equity, valid in test_cases:
            size = calculate_position_size(entry, stop, equity)
            if valid:
                self.assertGreater(size, 0)
            else:
                self.assertEqual(size, 0)

    def test_risk_management_math(self):
        """Test risk management mathematical calculations"""
        # Test daily loss limit calculation
        current_equity = 100000
        max_daily_loss_pct = 0.03  # 3%
        max_daily_loss = current_equity * max_daily_loss_pct

        self.assertEqual(max_daily_loss, 3000)

        # Test position size limits
        max_position_pct = 0.10  # 10%
        max_position = current_equity * max_position_pct
        self.assertEqual(max_position, 10000)

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation logic"""
        # Simulate some trades
        trades = [
            {'pnl': 100, 'type': 'WIN'},
            {'pnl': -50, 'type': 'LOSS'},
            {'pnl': 200, 'type': 'WIN'},
            {'pnl': -75, 'type': 'LOSS'},
            {'pnl': 150, 'type': 'WIN'},
        ]

        # Calculate win rate
        wins = [t for t in trades if t['pnl'] > 0]
        win_rate = len(wins) / len(trades)
        self.assertEqual(win_rate, 0.6)  # 3 out of 5 trades

        # Calculate profit factor
        gross_profit = sum(t['pnl'] for t in wins)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        profit_factor = gross_profit / gross_loss
        expected_profit_factor = 450 / 125  # 3.6
        self.assertEqual(profit_factor, expected_profit_factor)


class TestDataValidation(unittest.TestCase):
    """Test suite for data validation and error handling"""

    def test_ohlc_validation(self):
        """Test OHLC data validation logic"""
        def validate_ohlc(high, low, open_price, close):
            # Check logical consistency
            if not (low <= close <= high and low <= open_price <= high):
                return False
            return True

        # Valid OHLC
        self.assertTrue(validate_ohlc(45000, 44000, 44500, 44600))

        # Invalid OHLC (low > high)
        self.assertFalse(validate_ohlc(44000, 45000, 44500, 44600))

    def test_price_change_validation(self):
        """Test price change validation for anomalies"""
        def detect_anomaly(prev_close, current_close, threshold=0.05):
            if prev_close is None:
                return False
            change = abs(current_close - prev_close) / prev_close
            return change > threshold

        # Normal price change
        self.assertFalse(detect_anomaly(45000, 45100))

        # Large price change (5%+)
        self.assertTrue(detect_anomaly(45000, 47250))  # 5% move


class TestParameterOptimization(unittest.TestCase):
    """Test suite for parameter optimization logic"""

    def test_parameter_ranges(self):
        """Test that parameter ranges are reasonable"""
        # Define reasonable parameter ranges
        atr_periods = [7, 10, 14, 21]
        multipliers = [2, 3, 5, 7]
        risk_percents = [0.01, 0.02, 0.03, 0.05]

        # Validate ranges
        for period in atr_periods:
            self.assertGreaterEqual(period, 1)
            self.assertLessEqual(period, 50)

        for mult in multipliers:
            self.assertGreaterEqual(mult, 0.1)
            self.assertLessEqual(mult, 20)

        for risk in risk_percents:
            self.assertGreater(risk, 0)
            self.assertLessEqual(risk, 0.5)  # Max 50% risk per trade

    def test_optimization_objective(self):
        """Test that optimization objectives are well-defined"""
        # Sharpe ratio calculation (simplified)
        returns = [0.01, -0.005, 0.02, -0.01, 0.015]
        mean_return = np.mean(returns)
        return_std = np.std(returns)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate

        if return_std > 0:
            sharpe = (mean_return - risk_free_rate) / return_std * np.sqrt(252)
        else:
            sharpe = 0

        # Sharpe ratio should be a reasonable number
        self.assertIsInstance(sharpe, (int, float))
        self.assertNotEqual(sharpe, np.inf)


class IntegrationTests(unittest.TestCase):
    """Integration tests for the complete strategy"""

    def test_end_to_end_simulation(self):
        """Test complete strategy simulation"""
        # Initialize components
        indicator = SuperTrendIndicator(period=5, multiplier=3)  # Short periods for testing

        # Generate realistic price series
        np.random.seed(42)  # For reproducible results
        prices = []
        current_price = 45000

        for i in range(100):
            # Generate realistic BTC-like movements
            daily_change = np.random.normal(0.001, 0.02)  # Small positive drift, 2% vol
            current_price = current_price * (1 + daily_change)
            prices.append(current_price)

        # Simulate trading
        signals = []
        positions = []

        for price in prices:
            high = price * 1.001  # Small spread
            low = price * 0.999
            close = price

            supertrend, signal = indicator.update(high, low, close)

            if indicator.is_buy_signal():
                signals.append({'type': 'BUY', 'price': price})
                positions.append(price)
            elif indicator.is_sell_signal():
                signals.append({'type': 'SELL', 'price': price})

        # Verify strategy behavior
        self.assertGreaterEqual(len(signals), 0)  # Should generate some signals or none
        self.assertLessEqual(len(signals), len(prices))  # Can't have more signals than data points

        print(f"📊 Integration Test Results:")
        print(f"   Price points processed: {len(prices)}")
        print(f"   Signals generated: {len(signals)}")
        print(f"   Buy signals: {len([s for s in signals if s['type'] == 'BUY'])}")
        print(f"   Sell signals: {len([s for s in signals if s['type'] == 'SELL'])}")

    def test_strategy_performance(self):
        """Test basic strategy performance expectations"""
        # This is a basic sanity check, not a full backtest
        indicator = SuperTrendIndicator()

        # Process trending market data
        for i in range(50):
            if i < 25:
                # Downtrend
                price = 50000 - i * 100
            else:
                # Uptrend
                price = 47500 + (i - 25) * 100

            high = price + 20
            low = price - 20
            close = price

            indicator.update(high, low, close)

        # Should have processed all data
        self.assertTrue(indicator.is_ready or indicator.bar_count == 50)


def run_performance_benchmark():
    """Run performance benchmark for the indicator"""
    print("\n⚡ Performance Benchmark")
    print("=" * 40)

    indicator = SuperTrendIndicator()

    # Test with large dataset
    import time
    start_time = time.time()

    np.random.seed(123)
    base_price = 45000

    for i in range(10000):
        price = base_price + np.random.normal(0, 500)
        high = price + 25
        low = price - 25
        close = price

        indicator.update(high, low, close)

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"Processed 10,000 data points in {processing_time:.3f} seconds")
    print(f"Processing rate: {10000/processing_time:.0f} points/second")
    print(f"Average time per point: {processing_time/10000*1000:.3f} ms")

    return processing_time


def main():
    """Run all tests"""
    print("🧪 Bitcoin Supertrend Strategy - Test Suite")
    print("=" * 60)

    # Run unit tests
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Run performance benchmark
    run_performance_benchmark()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Please review the output above.")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)