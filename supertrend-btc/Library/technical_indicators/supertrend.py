"""
Supertrend Indicator Library
Reusable Supertrend indicator implementation for QuantConnect Lean

Author: Claude Code
Created: 2024
Version: 1.0.0
"""

from QuantConnect import *
from QuantConnect.Algorithm import *
from collections import deque
import numpy as np


class SuperTrendIndicator:
    """
    Supertrend Indicator Implementation

    Calculates dynamic support/resistance levels based on:
    - Average True Range (ATR) for volatility
    - Price action (High/Low midpoint)
    - Configurable multiplier for band distance

    The Supertrend indicator helps identify trend direction and strength,
    making it effective for both entry and exit signals in trading strategies.

    Mathematical Foundation:
    - Basic Upper Band = (High + Low)/2 + (Multiplier × ATR)
    - Basic Lower Band = (High + Low)/2 - (Multiplier × ATR)
    - Final bands incorporate continuity logic to prevent whipsaws
    """

    def __init__(self, period=10, multiplier=3):
        """
        Initialize the Supertrend Indicator

        Args:
            period (int): ATR calculation period (default: 10)
            multiplier (float): Multiplier for ATR bands (default: 3)
        """
        self.period = period
        self.multiplier = multiplier

        # ATR calculation tracking
        self.atr_values = deque(maxlen=period)
        self._prev_atr = None

        # Band calculations
        self.final_upper_band = None
        self.final_lower_band = None
        self.supertrend = None

        # Signal tracking
        self.signal = 0  # 1 = Buy, -1 = Sell, 0 = No signal
        self.prev_signal = 0

        # State tracking
        self.is_ready = False
        self.bar_count = 0
        self.prev_close = None

        # Performance metrics
        self.returns_history = deque(maxlen=period * 4)  # Keep recent history

    def calculate_true_range(self, high, low, prev_close):
        """
        Calculate True Range for ATR calculation

        True Range is the maximum of:
        - High minus Low
        - Absolute difference between High and Previous Close
        - Absolute difference between Low and Previous Close

        Args:
            high (float): Current bar high price
            low (float): Current bar low price
            prev_close (float): Previous bar close price

        Returns:
            float: True Range value
        """
        if prev_close is None:
            return high - low

        return max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

    def calculate_atr(self, tr):
        """
        Calculate Average True Range using Wilder's smoothing

        Wilder's smoothing formula:
        ATR = (Previous ATR × (N-1) + Current TR) / N

        Args:
            tr (float): Current True Range value

        Returns:
            float: Average True Range
        """
        self.atr_values.append(tr)

        if len(self.atr_values) < self.period:
            # Initial ATR is simple average of available values
            return np.mean(list(self.atr_values))
        else:
            # Subsequent ATR uses Wilder's smoothing
            if self._prev_atr is None:
                self._prev_atr = np.mean(list(self.atr_values))

            current_atr = (self._prev_atr * (self.period - 1) + tr) / self.period
            self._prev_atr = current_atr
            return current_atr

    def update(self, high, low, close):
        """
        Update indicator with latest OHLC data

        Args:
            high (float): Current bar high price
            low (float): Current bar low price
            close (float): Current bar close price

        Returns:
            tuple: (current_supertrend_level, current_signal)
        """
        self.bar_count += 1

        # Calculate True Range and ATR
        tr = self.calculate_true_range(high, low, self.prev_close)
        atr = self.calculate_atr(tr)

        # Calculate basic bands using HL2 midpoint
        hl_midpoint = (high + low) / 2.0
        basic_upper = hl_midpoint + (self.multiplier * atr)
        basic_lower = hl_midpoint - (self.multiplier * atr)

        # Apply final band logic with continuity constraint
        if self.final_upper_band is None:
            # First calculation - initialize bands
            self.final_upper_band = basic_upper
            self.final_lower_band = basic_lower
        else:
            # Update bands with continuity logic to prevent whipsaws
            if basic_upper < self.final_upper_band or close > self.final_upper_band:
                self.final_upper_band = basic_upper
            # Else keep previous upper band (continuity)

            if basic_lower > self.final_lower_band or close < self.final_lower_band:
                self.final_lower_band = basic_lower
            # Else keep previous lower band (continuity)

        # Determine supertrend value and signal
        self.prev_signal = self.signal

        if close <= self.final_upper_band:
            self.supertrend = self.final_upper_band
            self.signal = -1  # Downtrend (Sell signal)
        else:
            self.supertrend = self.final_lower_band
            self.signal = 1   # Uptrend (Buy signal)

        # Mark indicator as ready after sufficient warmup data
        if self.bar_count >= self.period * 2:
            self.is_ready = True

        # Store previous close for next calculation
        self.prev_close = close

        # Store return for performance tracking
        if self.prev_close:
            self.returns_history.append(close / self.prev_close - 1)

        return self.supertrend, self.signal

    def get_current_supertrend(self):
        """
        Get current supertrend level

        Returns:
            float: Current supertrend level, or None if not ready
        """
        return self.supertrend if self.is_ready else None

    def get_current_signal(self):
        """
        Get current signal state

        Returns:
            int: 1 = Buy, -1 = Sell, 0 = No clear signal
        """
        return self.signal if self.is_ready else 0

    def is_buy_signal(self):
        """
        Check if current signal is a buy signal

        Returns:
            bool: True if signal transitioned from sell to buy
        """
        return self.signal == 1 and self.prev_signal == -1 and self.is_ready

    def is_sell_signal(self):
        """
        Check if current signal is a sell signal

        Returns:
            bool: True if signal transitioned from buy to sell
        """
        return self.signal == -1 and self.prev_signal == 1 and self.is_ready

    def get_volatility_measure(self):
        """
        Get current volatility measure (ATR)

        Returns:
            float: Current ATR value, or None if not ready
        """
        return self._prev_atr if self.is_ready else None

    def get_signal_strength(self):
        """
        Calculate signal strength based on distance from bands

        Returns:
            float: Signal strength ratio, higher values indicate stronger signals
        """
        if not self.is_ready or self.supertrend is None:
            return 0

        # This would need current price to calculate properly
        # For now, return a basic measure
        return abs(self.signal) * 0.5  # Placeholder for now

    def reset(self):
        """Reset indicator to initial state"""
        self.final_upper_band = None
        self.final_lower_band = None
        self.supertrend = None
        self.signal = 0
        self.prev_signal = 0
        self.is_ready = False
        self.bar_count = 0
        self.prev_close = None
        self.atr_values.clear()
        self.returns_history.clear()
        self._prev_atr = None

    def get_parameter_summary(self):
        """
        Get summary of current parameters and state

        Returns:
            dict: Summary of indicator parameters and current state
        """
        return {
            'period': self.period,
            'multiplier': self.multiplier,
            'is_ready': self.is_ready,
            'bar_count': self.bar_count,
            'current_signal': self.get_current_signal(),
            'current_supertrend': self.get_current_supertrend(),
            'current_atr': self.get_volatility_measure(),
            'signal_strength': self.get_signal_strength(),
            'buy_signal': self.is_buy_signal(),
            'sell_signal': self.is_sell_signal()
        }

    def __str__(self):
        """String representation of the indicator state"""
        summary = self.get_parameter_summary()
        return f"SuperTrend(period={summary['period']}, multiplier={summary['multiplier']}, " \
               f"signal={summary['current_signal']}, supertrend=${summary['current_supertrend']:.2f})"

    def __repr__(self):
        """Detailed representation of the indicator"""
        return self.__str__()


class SuperTrendHistory:
    """
    Extended Supertrend indicator with history tracking for analysis
    """

    def __init__(self, period=10, multiplier=3, max_history=1000):
        self.supertrend_indicator = SuperTrendIndicator(period, multiplier)
        self.max_history = max_history

        # Historical data tracking
        self.history = deque(maxlen=max_history)
        self.signals_history = deque(maxlen=max_history)

    def update(self, high, low, close, timestamp=None):
        """
        Update indicator with historical tracking

        Args:
            high (float): Current bar high price
            low (float): Current bar low price
            close (float): Current bar close price
            timestamp (datetime, optional): Timestamp for the data point

        Returns:
            tuple: (current_supertrend_level, current_signal)
        """
        supertrend_level, signal = self.supertrend_indicator.update(high, low, close)

        # Store in history
        self.history.append({
            'timestamp': timestamp,
            'high': high,
            'low': low,
            'close': close,
            'supertrend': supertrend_level,
            'signal': signal
        })

        # Track signals
        if self.supertrend_indicator.is_buy_signal():
            self.signals_history.append({
                'timestamp': timestamp,
                'type': 'BUY',
                'price': close,
                'supertrend': supertrend_level
            })
        elif self.supertrend_indicator.is_sell_signal():
            self.signals_history.append({
                'timestamp': timestamp,
                'type': 'SELL',
                'price': close,
                'supertrend': supertrend_level
            })

        return supertrend_level, signal

    def get_recent_signals(self, count=10):
        """
        Get recent trading signals

        Args:
            count (int): Number of recent signals to retrieve

        Returns:
            list: Recent trading signals
        """
        return list(self.signals_history)[-count:]

    def get_performance_stats(self):
        """
        Calculate performance statistics from history

        Returns:
            dict: Performance statistics
        """
        if len(self.history) < 2:
            return {}

        # Basic statistics
        closes = [point['close'] for point in self.history]
        supertrends = [point['supertrend'] for point in self.history if point['supertrend']]

        # Calculate returns
        returns = []
        for i in range(1, len(closes)):
            daily_return = (closes[i] - closes[i-1]) / closes[i-1]
            returns.append(daily_return)

        # Basic stats
        stats = {
            'total_bars': len(self.history),
            'total_signals': len(self.signals_history),
            'buy_signals': len([s for s in self.signals_history if s['type'] == 'BUY']),
            'sell_signals': len([s for s in self.signals_history if s['type'] == 'SELL']),
            'price_range': {
                'min': min(closes),
                'max': max(closes),
                'mean': np.mean(closes)
            },
            'supertrend_range': {
                'min': min(supertrends) if supertrends else 0,
                'max': max(supertrends) if supertrends else 0,
                'mean': np.mean(supertrends) if supertrends else 0
            },
            'returns_stats': {
                'mean': np.mean(returns) if returns else 0,
                'std': np.std(returns) if returns else 0,
                'min': min(returns) if returns else 0,
                'max': max(returns) if returns else 0
            }
        }

        return stats

    # Delegate other methods to the underlying indicator
    def get_current_supertrend(self):
        return self.supertrend_indicator.get_current_supertrend()

    def get_current_signal(self):
        return self.supertrend_indicator.get_current_signal()

    def is_buy_signal(self):
        return self.supertrend_indicator.is_buy_signal()

    def is_sell_signal(self):
        return self.supertrend_indicator.is_sell_signal()

    def get_volatility_measure(self):
        return self.supertrend_indicator.get_volatility_measure()

    def reset(self):
        self.supertrend_indicator.reset()
        self.history.clear()
        self.signals_history.clear()

    def __getattr__(self, name):
        """Delegate all other attributes to the underlying indicator"""
        return getattr(self.supertrend_indicator, name)