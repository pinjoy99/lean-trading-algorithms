# region imports
from AlgorithmImports import *
# endregion

class MinutelyRSIStrategy(QCAlgorithm):
    """
    Minutely RSI Trading Strategy

    This strategy implements a Relative Strength Index (RSI) based trading system
    using minute-level data to identify overbought and oversold conditions.

    Strategy Overview:
    - Uses RSI with configurable period (default: 14)
    - Generates BUY signals when RSI < oversold_threshold (default: 30)
    - Generates SELL signals when RSI > overbought_threshold (default: 70)
    - Implements position sizing and risk management
    - Prevents over-trading with minimum signal intervals

    Risk Management:
    - Stop-loss: 2% per trade
    - Take-profit: 4% per trade
    - Maximum position size: 95% of portfolio
    - Daily loss limit: 5% of portfolio
    """

    def initialize(self):
        """Initialize the algorithm with configuration."""
        # Set the start and end dates - January 2023 only
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2023, 1, 31)

        # Set the initial cash balance
        self.set_cash(100000)

        # Add the equity security with MINUTE resolution
        self.symbol = self.add_equity("SPY", Resolution.MINUTE).symbol

        # Strategy parameters (optimizable)
        self.rsi_period = 14          # RSI calculation period
        self.oversold_threshold = 30   # RSI level for buy signals
        self.overbought_threshold = 70 # RSI level for sell signals

        # Risk management parameters
        self.max_position_size = 0.95  # Maximum position size (95%)
        self.stop_loss_pct = 0.02      # Stop-loss percentage (2%)
        self.take_profit_pct = 0.04    # Take-profit percentage (4%)
        self.max_daily_loss = 0.05     # Maximum daily loss (5%)

        # Create RSI indicator
        self.rsi = self.RSI(self.symbol, self.rsi_period)

        # State tracking
        self.is_invested = False
        self.signals_count = 0
        self.daily_pnl = 0
        self.daily_start_portfolio = self.Portfolio.total_portfolio_value
        self.last_signal_time = None
        self.min_signal_interval = 5  # Minimum minutes between signals

        # Performance tracking
        self.entry_price = 0
        self.position_quantity = 0

        # Debug logging
        self.debug("Minutely RSI Strategy initialized")
        self.debug(f"RSI Period: {self.rsi_period}")
        self.debug(f"Oversold: {self.oversold_threshold}, Overbought: {self.overbought_threshold}")
        self.debug(f"Stop Loss: {self.stop_loss_pct:.1%}, Take Profit: {self.take_profit_pct:.1%}")

    def on_data(self, data: Slice):
        """Execute the RSI strategy on each new data point.

        Args:
            data: Slice object containing the current market data
        """
        # Ensure we have RSI data ready
        if not self.rsi.is_ready:
            return

        # Check for data availability
        if self.symbol not in data:
            return

        current_price = data[self.symbol].close
        current_rsi = self.rsi.current.value

        # Prevent over-trading: minimum interval between signals
        if self.last_signal_time:
            time_since_last = self.time - self.last_signal_time
            if time_since_last.total_seconds() / 60 < self.min_signal_interval:
                return

        # Check daily loss limit
        if self._is_daily_loss_limit_breached():
            self.debug("Daily loss limit breached - pausing trading")
            return

        # Check for buy signal (RSI oversold)
        if (current_rsi <= self.oversold_threshold and
            not self.is_invested and
            self._validate_trade_signal('buy', current_price, current_rsi)):

            self._execute_buy_signal(current_price, current_rsi)

        # Check for sell signal (RSI overbought)
        elif (current_rsi >= self.overbought_threshold and
              self.is_invested and
              self._validate_trade_signal('sell', current_price, current_rsi)):

            self._execute_sell_signal(current_price, current_rsi)

        # Check stop-loss and take-profit conditions
        if self.is_invested:
            self._check_exit_conditions(current_price)

    def _execute_buy_signal(self, price, rsi):
        """Execute buy signal with position sizing and risk management."""
        try:
            # Calculate position size based on available cash
            available_cash = self.portfolio.cash
            position_value = available_cash * self.max_position_size
            quantity = int(position_value / price)

            if quantity > 0:
                # Submit market order
                self.set_holdings(self.symbol, self.max_position_size)
                self.is_invested = True
                self.signals_count += 1
                self.entry_price = price
                self.position_quantity = quantity
                self.last_signal_time = self.time

                self.debug(f"BUY #{self.signals_count} - Time: {self.time}, "
                          f"Price: ${price:.2f}, RSI: {rsi:.1f}, "
                          f"Quantity: {quantity}, "
                          f"Stop Loss: ${price * (1 - self.stop_loss_pct):.2f}, "
                          f"Take Profit: ${price * (1 + self.take_profit_pct):.2f}")

        except Exception as e:
            self.error(f"Error executing buy signal: {e}")

    def _execute_sell_signal(self, price, rsi):
        """Execute sell signal to close position."""
        try:
            # Liquidate position
            self.liquidate(self.symbol)
            self.is_invested = False
            self.signals_count += 1
            self.last_signal_time = self.time

            # Calculate trade P&L
            if self.entry_price > 0:
                pnl = (price - self.entry_price) * self.position_quantity
                self.debug(f"SELL #{self.signals_count} - Time: {self.time}, "
                          f"Price: ${price:.2f}, RSI: {rsi:.1f}, "
                          f"Quantity: {self.position_quantity}, "
                          f"P&L: ${pnl:.2f}")

            # Reset position tracking
            self.entry_price = 0
            self.position_quantity = 0

        except Exception as e:
            self.error(f"Error executing sell signal: {e}")

    def _check_exit_conditions(self, current_price):
        """Check if stop-loss or take-profit conditions are met."""
        if self.entry_price == 0:
            return

        # Calculate price changes
        price_change_pct = (current_price - self.entry_price) / self.entry_price

        # Check stop-loss
        if price_change_pct <= -self.stop_loss_pct:
            self.debug(f"STOP-LOSS triggered at ${current_price:.2f} "
                      f"(Change: {price_change_pct:.1%})")
            self._execute_sell_signal(current_price, self.rsi.current.value)

        # Check take-profit
        elif price_change_pct >= self.take_profit_pct:
            self.debug(f"TAKE-PROFIT triggered at ${current_price:.2f} "
                      f"(Change: {price_change_pct:.1%})")
            self._execute_sell_signal(current_price, self.rsi.current.value)

    def _validate_trade_signal(self, signal_type, price, rsi):
        """Validate trade signal against risk management rules."""
        # Additional validation can be added here
        # For example: volatility filters, trend confirmation, etc.

        # Ensure minimum price level (avoid extremely low prices)
        if price < 10:
            self.debug(f"Ignoring signal due to low price: ${price:.2f}")
            return False

        # Ensure RSI is within reasonable bounds
        if rsi < 0 or rsi > 100:
            self.debug(f"Ignoring signal due to invalid RSI: {rsi}")
            return False

        return True

    def _is_daily_loss_limit_breached(self):
        """Check if daily loss limit has been breached."""
        current_portfolio_value = self.portfolio.total_portfolio_value
        daily_change_pct = (current_portfolio_value - self.daily_start_portfolio) / self.daily_start_portfolio

        return daily_change_pct <= -self.max_daily_loss

    def on_end_of_day(self):
        """Log portfolio status and reset daily tracking at end of each day."""
        current_price = self.securities[self.symbol].price
        portfolio_value = self.Portfolio.total_portfolio_value
        current_rsi = self.rsi.current.value if self.rsi.is_ready else 0

        # Calculate daily P&L
        daily_pnl = (portfolio_value - self.daily_start_portfolio) / self.daily_start_portfolio

        if self.is_invested:
            unrealized_pnl = self.securities[self.symbol].holdings.unrealized_profit
            self.debug(f"End of Day - {self.time.date()} - "
                      f"Price: ${current_price:.2f}, RSI: {current_rsi:.1f}, "
                      f"Portfolio: ${portfolio_value:.2f}, "
                      f"Daily P&L: {daily_pnl:.1%}, "
                      f"Unrealized P&L: ${unrealized_pnl:.2f}")
        else:
            self.debug(f"End of Day - {self.time.date()} - "
                      f"Price: ${current_price:.2f}, RSI: {current_rsi:.1f}, "
                      f"Portfolio: ${portfolio_value:.2f}, "
                      f"Daily P&L: {daily_pnl:.1%}, Cash: ${self.portfolio.cash:.2f}")

        # Reset daily tracking for next day
        self.daily_start_portfolio = portfolio_value

    def on_end_of_algorithm(self):
        """Log final algorithm statistics and performance metrics."""
        total_portfolio_value = self.Portfolio.total_portfolio_value
        total_return = (total_portfolio_value / 100000 - 1) * 100
        total_fees = self.portfolio.total_fees

        self.debug("=== FINAL ALGORITHM RESULTS ===")
        self.debug(f"Total Signals Generated: {self.signals_count}")
        self.debug(f"Initial Portfolio Value: $100,000.00")
        self.debug(f"Final Portfolio Value: ${total_portfolio_value:.2f}")
        self.debug(f"Total Return: {total_return:.2f}%")
        self.debug(f"Total Fees Paid: ${total_fees:.2f}")
        self.debug(f"RSI Period Used: {self.rsi_period}")
        self.debug(f"Oversold/Overbought Thresholds: {self.oversold_threshold}/{self.overbought_threshold}")
        self.debug(f"Stop Loss/Take Profit: {self.stop_loss_pct:.1%}/{self.take_profit_pct:.1%}")

        if self.is_invested:
            current_price = self.securities[self.symbol].price
            unrealized_pnl = self.securities[self.symbol].holdings.unrealized_profit
            self.debug(f"Final Position: LONG {self.portfolio[self.symbol].quantity} shares at ${current_price:.2f}")
            self.debug(f"Unrealized P&L: ${unrealized_pnl:.2f}")

        self.debug("Strategy execution completed.")
