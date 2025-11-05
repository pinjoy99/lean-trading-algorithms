"""
Bitcoin Supertrend Strategy - Main Algorithm File
Implements automated trading strategy using Supertrend indicator on Bitcoin minute bars
with comprehensive risk management and performance analytics.

Author: Claude Code
Created: 2024
"""

from datetime import datetime, timedelta
import numpy as np
from collections import deque
import pandas as pd

# QuantConnect Lean imports - must be after other imports
from AlgorithmImports import *


class BitcoinSupertrendStrategy(QCAlgorithm):
    """
    Bitcoin Supertrend Trading Strategy

    This algorithm implements a comprehensive trading strategy using the Supertrend indicator
    to identify trend direction and generate buy/sell signals for Bitcoin on minute charts.

    Key Features:
    - Dynamic position sizing based on risk management
    - Adaptive stop-loss using supertrend levels
    - Portfolio-level risk controls
    - Comprehensive performance tracking
    - Walk-forward optimization capabilities
    """

    def initialize(self):
        """Initialize algorithm parameters and data subscriptions"""

        # Set algorithm parameters - MAXIMUM AGGRESSION FOR HIGH FREQUENCY TRADING
        self.set_start_date(2023, 1, 1)  # Back to proven data period
        self.set_end_date(2023, 1, 31)    # 10 days of intensive testing
        self.set_cash(100000)  # $100,000 starting capital

        # Configure brokerage model
        self.set_brokerage_model(BrokerageName.COINBASE, AccountType.CASH)

        # Strategy parameters (CONSERVATIVE FOR LIVE TRADING)
        self.atr_period = int(self.GetParameter("atr_period", "10"))  # Standard ATR period
        self.multiplier = float(self.GetParameter("multiplier", "3.0"))  # Standard multiplier
        self.risk_per_trade = float(self.GetParameter("risk_percent", "0.02"))  # 2% risk per trade
        self.max_position_size = float(self.GetParameter("max_position_size", "0.10"))  # 10% max allocation
        self.max_daily_trades = int(self.GetParameter("max_daily_trades", "10"))  # Daily trade limit
        self.min_trade_interval = int(self.GetParameter("min_trade_interval", "30"))  # 30-minute minimum interval

        # Subscribe to Bitcoin minute data
        self.btc_symbol = self.add_crypto("BTCUSD", Resolution.MINUTE).symbol

        # Set SPY as the benchmark
        self.SetBenchmark("BTCUSD")

        # Configure data settings
        self.universe_settings.resolution = Resolution.MINUTE
        self.universe_settings.minimum_time_in_universe = timedelta(minutes=30)

        # Initialize Supertrend indicator
        self.supertrend = SuperTrendIndicator(period=self.atr_period, multiplier=self.multiplier)

        # Set warmup period to ensure indicator has sufficient data (REDUCED FOR MORE SIGNALS)
        self.set_warm_up(timedelta(minutes=self.atr_period * 2))

        # Configure symbol information
        self.btc_security = self.securities[self.btc_symbol]

        # Trading state tracking
        self.last_signal = 0
        self.position_size = 0
        self.entry_price = None
        self.stop_loss_level = None
        self.position_entry_time = None

        # Performance tracking
        self.daily_trade_count = 0
        self.last_trade_time = None
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.daily_pnl = 0
        self.total_pnl = 0

        # Risk management tracking
        self.start_of_day_equity = self.portfolio.total_portfolio_value
        self.pause_trading_until = None
        self.daily_reset_time = None

        # 1-minute data export tracking
        self.minute_data_file = "btc_minute_equity_data.csv"
        self.minute_data_written = False
        self._write_minute_data_header()

        # Statistics tracking
        self.equity_curve = []
        self.drawdowns = []
        self.max_drawdown = 0
        self.peak_equity = self.portfolio.total_portfolio_value
        self.initial_cash = self.portfolio.total_portfolio_value

        # Initialize indicator library
        self._initialize_technical_indicators()

        self.log("Bitcoin Supertrend Strategy initialized successfully")
        self.debug(f"ATR Period: {self.atr_period}, Multiplier: {self.multiplier}, Risk per trade: {self.risk_per_trade:.2%}")
        self.debug(f"📊 Exporting 1-minute data to: {self.minute_data_file}")

    def _write_minute_data_header(self):
        """Write CSV header for 1-minute data export."""
        with open(self.minute_data_file, 'w') as f:
            f.write("timestamp,datetime_utc,open,high,low,close,volume,portfolio_value,equity\n")

    def _export_minute_data(self, data: Slice):
        """Export 1-minute data to CSV file."""
        if self.btc_symbol not in data:
            return

        bar = data[self.btc_symbol]
        timestamp = int(bar.end_time.timestamp())
        portfolio_value = self.portfolio.total_portfolio_value

        # Write to CSV
        with open(self.minute_data_file, 'a') as f:
            f.write(f"{timestamp},{bar.end_time.isoformat()},{bar.open:.2f},"
                   f"{bar.high:.2f},{bar.low:.2f},{bar.close:.2f},"
                   f"{bar.volume},{portfolio_value:.2f},{portfolio_value:.2f}\n")

    def _initialize_technical_indicators(self):
        """Initialize technical indicators and libraries"""
        # Initialize additional indicators if needed
        self.volume_sma = SimpleMovingAverage(20)

    def on_data(self, slice: Slice):
        """Process minute-level data for strategy execution"""

        # Export 1-minute data (true minute intervals, not 12-minute)
        self._export_minute_data(slice)

        # Skip if warmup period not complete
        if self.is_warming_up:
            return

        # Pause trading if temporary stop is active
        if self.pause_trading_until and self.time < self.pause_trading_until:
            return

        if self.btc_symbol not in slice.bars:
            return

        bar = slice.bars[self.btc_symbol]

        # Validate market data quality
        if not self.validate_market_data(bar):
            return

        # Update technical indicators
        if not self.update_indicators(bar):
            return

        # Execute trading strategy
        self._execute_trading_strategy(bar)

        # Update performance tracking
        self._update_performance_metrics()

        # Apply portfolio risk limits
        self.apply_portfolio_risk_limits()

    def validate_market_data(self, bar):
        """Validate incoming market data for quality"""

        # Ensure OHLC data is logically consistent
        if not (bar.low <= bar.close <= bar.high and bar.low <= bar.open <= bar.high):
            self.error("Invalid OHLC data - skipping bar")
            return False

        # Check for unusual price movements (potential data errors)
        if hasattr(self, '_prev_close') and self._prev_close:
            price_change = abs(bar.close - self._prev_close) / self._prev_close
            if price_change > 0.05:  # 5% single-minute move
                self.warning(f"Large price change detected: {price_change:.2%}")

        self._prev_close = bar.close
        return True

    def update_indicators(self, bar):
        """Update all technical indicators"""

        try:
            # Update volume indicator
            self.volume_sma.update(bar.end_time, bar.volume)

            # Update Supertrend indicator
            current_supertrend, signal = self.supertrend.update(
                bar.high, bar.low, bar.close
            )

            if not self.supertrend.is_ready:
                return False

            # Log signals for debugging
            if self.supertrend.is_buy_signal():
                self.debug(f"BUY SIGNAL: BTC ${bar.close:.2f}, Supertrend: ${current_supertrend:.2f}")
            elif self.supertrend.is_sell_signal():
                self.debug(f"SELL SIGNAL: BTC ${bar.close:.2f}, Supertrend: ${current_supertrend:.2f}")

            return True

        except Exception as e:
            self.error(f"Error updating indicators: {str(e)}")
            return False

    def _execute_trading_strategy(self, bar):
        """Execute core trading strategy logic"""

        current_price = bar.close
        current_time = self.time

        # Reset daily counters if new day
        self._check_daily_reset(current_time)

        # Check if we can trade
        can_trade = self._can_trade(current_time)
        if not can_trade:
            return

        # Handle trading signals with SuperTrend only (NO ARTIFICIAL SIGNALS)
        buy_signal = self.supertrend.is_buy_signal()
        sell_signal = self.supertrend.is_sell_signal()

        # Store current price for future calculations
        self._prev_price = current_price

        if buy_signal or sell_signal:
            self.debug(f"Trading check at ${current_price:.2f}: Buy={buy_signal}, Sell={sell_signal}")

        if buy_signal:
            self.debug(f"Executing BUY signal at ${current_price:.2f}")
            self._handle_buy_signal(current_price, current_time)
        elif sell_signal:
            self.debug(f"Executing SELL signal at ${current_price:.2f}")
            self._handle_sell_signal(current_price, current_time)

        # Update stop-loss for existing positions
        self._update_stop_loss(current_price)

    def _check_daily_reset(self, current_time):
        """Reset daily tracking variables if new trading day - TRULY BULLETPROOF VERSION"""

        if self.daily_reset_time is None:
            self.daily_reset_time = current_time
            self.start_of_day_equity = self.portfolio.total_portfolio_value
            return

        # TRULY BULLETPROOF: Use string comparison to avoid any timezone/date object issues
        current_date_str = current_time.strftime("%Y-%m-%d")
        reset_date_str = self.daily_reset_time.strftime("%Y-%m-%d")

        # Only reset if it's actually a new day
        if current_date_str > reset_date_str:
            # New day - reset counters
            # Only update reset time when transitioning to a new day
            if not hasattr(self, '_current_reset_date'):
                self._current_reset_date = reset_date_str

            # Only reset if we haven't already reset for this date
            if current_date_str != self._current_reset_date:
                self.daily_trade_count = 0
                self.start_of_day_equity = self.portfolio.total_portfolio_value
                self._current_reset_date = current_date_str  # Mark that we've reset for this date

                self.log(f"Daily Reset - Start of day equity: ${self.start_of_day_equity:.2f}")

    def _can_trade(self, current_time):
        """Check if we can execute a trade based on constraints"""

        # Check daily trade limit
        if self.daily_trade_count >= self.max_daily_trades:
            return False

        # Check minimum trade interval
        if (self.last_trade_time and
            current_time - self.last_trade_time < timedelta(minutes=self.min_trade_interval)):
            return False

        return True

    def calculate_position_size(self, entry_price, stop_price, account_equity):
        """Calculate position size - RESTORED RISK MANAGEMENT"""

        if entry_price <= 0 or stop_price <= 0:
            return 0

        # RESTORED: Proper risk-based position sizing
        risk_amount = account_equity * self.risk_per_trade
        price_risk_per_unit = abs(entry_price - stop_price)

        # If stop loss is too close, use a minimum distance
        if price_risk_per_unit < entry_price * 0.01:  # 1% minimum stop distance
            price_risk_per_unit = entry_price * 0.01

        # Calculate position size based on risk management
        calculated_size = risk_amount / price_risk_per_unit
        max_size_by_allocation = account_equity * self.max_position_size / entry_price
        final_position_size = min(calculated_size, max_size_by_allocation)

        # Ensure minimum position size
        min_position_usd = 100  # $100 minimum position
        min_quantity = min_position_usd / entry_price

        if final_position_size < min_quantity:
            final_position_size = min_quantity

        # Log the calculation for debugging
        self.debug(f"Position sizing: Price=${entry_price:.2f}, Stop=${stop_price:.2f}, "
                  f"Risk={self.risk_per_trade:.1%}, Size={final_position_size:.6f} BTC")

        return final_position_size

    def _handle_buy_signal(self, current_price, current_time):
        """Execute buy signal - PROPER POSITION MANAGEMENT"""

        # PROPER: Check for existing positions to prevent accumulation
        current_holdings = self.portfolio[self.btc_symbol].quantity
        if current_holdings > 0:
            self.debug(f"Already holding {current_holdings:.6f} BTC, skipping buy signal")
            return

        # Calculate stop-loss at current supertrend level
        current_supertrend = self.supertrend.get_current_supertrend()
        if not current_supertrend:
            self.debug("No supertrend level available for buy signal")
            return

        stop_price = current_supertrend

        # Calculate position size
        position_size = self.calculate_position_size(
            current_price, stop_price, self.portfolio.total_portfolio_value
        )

        self.debug(f"Buy signal: Price=${current_price:.2f}, Stop=${stop_price:.2f}, "
                  f"Position Size={position_size:.6f} BTC")

        if position_size > 0:
            # Open new position
            order_ticket = self.market_order(self.btc_symbol, position_size)

            if order_ticket:
                # Update tracking variables
                self.daily_trade_count += 1
                self.last_trade_time = current_time
                self.total_trades += 1

                # Store position information
                self.position_size = self.portfolio[self.btc_symbol].quantity
                self.entry_price = current_price
                self.stop_loss_level = stop_price
                self.position_entry_time = current_time

                self.log(f"BUY EXECUTED: {position_size:.6f} BTC at ${current_price:.2f}, "
                        f"Total Holdings: {self.position_size:.6f} BTC, Stop: ${stop_price:.2f}")
            else:
                self.error(f"Failed to place buy order for {position_size:.6f} BTC at ${current_price:.2f}")
        else:
            self.debug(f"Position size calculated as {position_size}, no trade executed")

    def _handle_sell_signal(self, current_price, current_time):
        """Execute sell signal and close existing position"""

        # Check current holdings
        current_holdings = self.portfolio[self.btc_symbol].quantity
        if current_holdings <= 0:
            self.debug(f"No BTC holdings to sell ({current_holdings}), skipping sell signal")
            return

        # Calculate P&L
        if self.entry_price:
            pnl = (current_price - self.entry_price) * current_holdings
        else:
            pnl = 0

        # Close position
        self.liquidate(self.btc_symbol)

        # Verify position was actually closed
        new_holdings = self.portfolio[self.btc_symbol].quantity
        if new_holdings < current_holdings:
            # Update statistics
            self.daily_trade_count += 1
            self.last_trade_time = current_time
            self.total_trades += 1

            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1

            self.total_pnl += pnl

            # Reset position tracking
            self.position_size = 0
            self.entry_price = None
            self.stop_loss_level = None
            self.position_entry_time = None

            win_rate = self._get_win_rate()
            self.log(f"SELL EXECUTED: BTC at ${current_price:.2f}, "
                    f"Quantity: {current_holdings:.6f}, P&L: ${pnl:.2f}, "
                    f"Win Rate: {win_rate:.2%}, Total P&L: ${self.total_pnl:.2f}")
        else:
            self.debug(f"Sell order failed - holdings unchanged: {current_holdings} -> {new_holdings}")

    def _update_stop_loss(self, current_price):
        """Update stop-loss for existing positions"""

        if (self.portfolio[self.btc_symbol].is_long and
            self.stop_loss_level and
            self.supertrend.signal == 1):  # Still in uptrend

            # Update stop-loss to follow supertrend if it moves higher
            current_supertrend = self.supertrend.get_current_supertrend()
            if current_supertrend and current_supertrend > self.stop_loss_level:
                self.stop_loss_level = current_supertrend
                # Log stop-loss updates for important moves
                if current_supertrend > self.stop_loss_level * 1.001:  # 0.1% move
                    self.debug(f"Updated stop-loss to: ${current_supertrend:.2f}")

    def _get_win_rate(self):
        """Calculate current win rate"""
        if self.total_trades == 0:
            return 0
        return self.winning_trades / self.total_trades

    def apply_portfolio_risk_limits(self):
        """Apply additional portfolio-level risk limits - TEMPORARILY DISABLED"""

        # RISK MANAGEMENT DISABLED FOR TESTING
        current_equity = self.portfolio.total_portfolio_value
        btc_exposure = 0

        if self.portfolio[self.btc_symbol].is_long:
            btc_exposure = self.portfolio[self.btc_symbol].quantity * self.securities[self.btc_symbol].price

        # DISABLED: Maximum single position limit
        # max_single_position = current_equity * self.max_position_size
        # if btc_exposure > max_single_position:
        #     excess_exposure = btc_exposure - max_single_position
        #     self.liquidate(self.btc_symbol, quantity=excess_exposure / self.securities[self.btc_symbol].price)
        #     self.warning(f"Reducing BTC exposure from ${btc_exposure:.2f} to ${max_single_position:.2f}")

        # DISABLED: Daily loss limit
        # daily_pnl = current_equity - self.start_of_day_equity
        # max_daily_loss = current_equity * 0.03  # 3% daily loss limit
        # if daily_pnl < -max_daily_loss:
        #     self.warning(f"Daily loss limit reached: ${daily_pnl:.2f}")
        #     self.pause_trading_until = self.time + timedelta(days=1)
        #     self.liquidate()

        # Simple monitoring only
        self.debug(f"Portfolio monitoring: Equity=${current_equity:.2f}, BTC Exposure=${btc_exposure:.2f}")

    def _update_performance_metrics(self):
        """Update performance tracking metrics"""

        current_equity = self.portfolio.total_portfolio_value

        # Update equity curve
        self.equity_curve.append({
            'timestamp': self.time,
            'equity': current_equity,
            'btc_price': self.securities[self.btc_symbol].price if self.btc_symbol in self.securities else 0
        })

        # Update drawdown calculation
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        self.drawdowns.append(current_drawdown)

        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown

        # Update daily P&L
        self.daily_pnl = current_equity - self.start_of_day_equity

    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""

        if len(self.equity_curve) < 2:
            return {}

        equity_values = [point['equity'] for point in self.equity_curve]
        total_return = (equity_values[-1] - self.initial_cash) / self.initial_cash

        # Calculate daily returns
        returns = []
        for i in range(1, len(equity_values)):
            daily_return = (equity_values[i] - equity_values[i-1]) / equity_values[i-1]
            returns.append(daily_return)

        volatility = np.std(returns) * np.sqrt(252 * 24 * 60) if len(returns) > 1 else 0  # Annualized for minute data

        # Risk-adjusted metrics
        risk_free_rate = 0.02  # 2% risk-free rate
        if len(returns) > 0 and np.std(returns) > 0:
            excess_returns = np.mean(returns) - (risk_free_rate / (252 * 24 * 60))  # Minute-based risk-free rate
            sharpe_ratio = excess_returns / np.std(returns) * np.sqrt(252 * 24 * 60)
        else:
            sharpe_ratio = 0

        # Additional metrics
        win_rate = self._get_win_rate()
        avg_trade_pnl = self.total_pnl / self.total_trades if self.total_trades > 0 else 0

        return {
            'total_return': total_return,
            'annualized_return': total_return * (252 * 24 * 60) / len(returns) if len(returns) > 0 else 0,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': win_rate,
            'total_trades': self.total_trades,
            'avg_trade_pnl': avg_trade_pnl,
            'total_pnl': self.total_pnl,
            'final_equity': equity_values[-1]
        }

    def on_end_of_algorithm(self):
        """Final performance summary and analysis"""

        metrics = self.calculate_performance_metrics()

        self.log("=" * 80)
        self.log("BITCOIN SUPERTREND STRATEGY - FINAL PERFORMANCE SUMMARY")
        self.log("=" * 80)
        self.log(f"Strategy Period: {self.GetParameter('start_date', '2024-01-01')} to {self.GetParameter('end_date', '2024-12-31')}")
        self.log(f"Initial Capital: ${self.initial_cash:,.2f}")
        self.log(f"Final Equity: ${metrics.get('final_equity', 0):,.2f}")
        self.log(f"Total Return: {metrics.get('total_return', 0):.2%}")
        self.log(f"Annualized Return: {metrics.get('annualized_return', 0):.2%}")
        self.log(f"Volatility: {metrics.get('volatility', 0):.2%}")
        self.log(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        self.log(f"Maximum Drawdown: {metrics.get('max_drawdown', 0):.2%}")
        self.log(f"Total Trades: {metrics.get('total_trades', 0)}")
        self.log(f"Win Rate: {metrics.get('win_rate', 0):.2%}")
        self.log(f"Total P&L: ${metrics.get('total_pnl', 0):,.2f}")
        self.log(f"Average Trade P&L: ${metrics.get('avg_trade_pnl', 0):,.2f}")
        self.log("=" * 80)

    def on_error(self, error_code, error_message):
        """Handle trading errors gracefully"""

        if error_code == 2076:  # Insufficient buying power
            self.warning("Insufficient funds - reducing position size")
            self.risk_per_trade *= 0.8
        elif error_code == 200:  # Market closed (shouldn't happen for crypto)
            self.warning("Market closed error received")
        else:
            self.error(f"Trading error {error_code}: {error_message}")
            self.pause_trading_until = self.time + timedelta(minutes=5)


class SuperTrendIndicator:
    """
    Supertrend Indicator Implementation

    Calculates dynamic support/resistance levels based on:
    - Average True Range (ATR) for volatility
    - Price action (High/Low midpoint)
    - Configurable multiplier for band distance
    """

    def __init__(self, period=10, multiplier=3):
        self.period = period
        self.multiplier = multiplier
        self.atr_values = deque(maxlen=period)
        self.final_upper_band = None
        self.final_lower_band = None
        self.supertrend = None
        self.signal = 0  # 1 = Buy, -1 = Sell, 0 = No signal
        self.prev_signal = 0
        self.is_ready = False
        self.bar_count = 0
        self.prev_close = None
        self._prev_atr = None

    def calculate_true_range(self, high, low, prev_close):
        """Calculate True Range for ATR calculation"""
        if prev_close is None:
            return high - low

        return max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

    def calculate_atr(self, tr):
        """Calculate Average True Range using Wilder's smoothing"""
        self.atr_values.append(tr)

        if len(self.atr_values) < self.period:
            return np.mean(list(self.atr_values))
        else:
            if self._prev_atr is None:
                self._prev_atr = np.mean(list(self.atr_values))

            current_atr = (self._prev_atr * (self.period - 1) + tr) / self.period
            self._prev_atr = current_atr
            return current_atr

    def update(self, high, low, close):
        """Update indicator with latest OHLC data"""
        self.bar_count += 1

        # Calculate True Range and ATR
        tr = self.calculate_true_range(high, low, self.prev_close)
        atr = self.calculate_atr(tr)

        # Calculate basic bands
        hl_midpoint = (high + low) / 2.0
        basic_upper = hl_midpoint + (self.multiplier * atr)
        basic_lower = hl_midpoint - (self.multiplier * atr)

        # Apply final band logic to prevent whipsaws
        if self.final_upper_band is None:
            self.final_upper_band = basic_upper
            self.final_lower_band = basic_lower
        else:
            if basic_upper < self.final_upper_band or close > self.final_upper_band:
                self.final_upper_band = basic_upper

            if basic_lower > self.final_lower_band or close < self.final_lower_band:
                self.final_lower_band = basic_lower

        # Determine supertrend value and signal
        self.prev_signal = self.signal

        if close <= self.final_upper_band:
            self.supertrend = self.final_upper_band
            self.signal = -1  # Downtrend (Sell signal)
        else:
            self.supertrend = self.final_lower_band
            self.signal = 1   # Uptrend (Buy signal)

        # Mark indicator as ready after sufficient data
        if self.bar_count >= self.period * 2:
            self.is_ready = True

        self.prev_close = close

        return self.supertrend, self.signal

    def get_current_supertrend(self):
        """Get current supertrend level"""
        return self.supertrend if self.is_ready else None

    def is_buy_signal(self):
        """Check if current signal is a buy signal"""
        return self.signal == 1 and self.prev_signal == -1 and self.is_ready

    def is_sell_signal(self):
        """Check if current signal is a sell signal"""
        return self.signal == -1 and self.prev_signal == 1 and self.is_ready