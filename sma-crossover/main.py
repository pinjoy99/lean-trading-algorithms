# region imports
from AlgorithmImports import *
# endregion

class Smacrossover(QCAlgorithm):

    def initialize(self):
        """Initialize the algorithm with configuration."""
        # Set the start and end dates (same as original My Project)
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2023, 1, 31)

        # Set the initial cash balance
        self.set_cash(100000)

        # Add the equity security with MINUTE resolution
        self.symbol = self.add_equity("SPY", Resolution.MINUTE).symbol

        # Set SPY as the benchmark
        self.SetBenchmark("SPY")

        # Create Simple Moving Averages using minute data
        # OPTIMIZED PARAMETERS: Best combination from Lean optimization
        self.fast_sma = self.SMA(self.symbol, 5, Resolution.MINUTE)   # 5-minute fast SMA (OPTIMIZED)
        self.slow_sma = self.SMA(self.symbol, 40, Resolution.MINUTE)  # 40-minute slow SMA (OPTIMIZED)

        # Track if we are currently invested
        self.is_invested = False

        # Track the number of signals generated
        self.signals_count = 0

        # 1-minute data export tracking
        self.minute_data_file = "sma_minute_equity_data.csv"
        self.minute_data_written = False
        self._write_minute_data_header()

        # Debug logging
        self.debug("SMA Crossover Strategy initialized with minute data")
        self.debug(f"📊 Exporting 1-minute data to: {self.minute_data_file}")

    def _write_minute_data_header(self):
        """Write CSV header for 1-minute data export."""
        with open(self.minute_data_file, 'w') as f:
            f.write("timestamp,datetime_utc,open,high,low,close,volume,portfolio_value,equity\n")

    def _export_minute_data(self, data: Slice):
        """Export 1-minute data to CSV file."""
        if self.symbol not in data:
            return

        bar = data[self.symbol]
        timestamp = int(bar.end_time.timestamp())
        portfolio_value = self.Portfolio.total_portfolio_value

        # Write to CSV
        with open(self.minute_data_file, 'a') as f:
            f.write(f"{timestamp},{bar.end_time.isoformat()},{bar.open:.2f},"
                   f"{bar.high:.2f},{bar.low:.2f},{bar.close:.2f},"
                   f"{bar.volume},{portfolio_value:.2f},{portfolio_value:.2f}\n")

    def on_data(self, data: Slice):
        """Execute the SMA crossover strategy on each new data point.

        Args:
            data: Slice object containing the current market data
        """
        # Export 1-minute data (true minute intervals, not 12-minute)
        self._export_minute_data(data)

        # Ensure we have both indicators ready
        if not (self.fast_sma.is_ready and self.slow_sma.is_ready):
            return

        # Get current prices and SMA values
        if self.symbol not in data:
            return

        current_price = data[self.symbol].close
        fast_sma_value = self.fast_sma.current.value
        slow_sma_value = self.slow_sma.current.value

        # Get previous SMA values to detect crossover
        # Note: For minute data, we check if we have previous values
        if not self.fast_sma.previous or not self.slow_sma.previous:
            return

        fast_sma_prev = self.fast_sma.previous.value
        slow_sma_prev = self.slow_sma.previous.value

        # Check for bullish crossover (fast SMA crosses above slow SMA)
        if (fast_sma_value > slow_sma_value and
            fast_sma_prev <= slow_sma_prev and
            not self.is_invested):
            # Buy signal: enter long position
            self.set_holdings(self.symbol, 0.95)  # Use 95% of available capital
            self.is_invested = True
            self.signals_count += 1
            self.debug(f"BUY #{self.signals_count} - Time: {self.time}, Price: ${current_price:.2f}, "
                      f"Fast SMA: ${fast_sma_value:.2f}, Slow SMA: ${slow_sma_value:.2f}")

        # Check for bearish crossover (fast SMA crosses below slow SMA)
        elif (fast_sma_value < slow_sma_value and
              fast_sma_prev >= slow_sma_prev and
              self.is_invested):
            # Sell signal: close position
            self.liquidate(self.symbol)
            self.is_invested = False
            self.signals_count += 1
            self.debug(f"SELL #{self.signals_count} - Time: {self.time}, Price: ${current_price:.2f}, "
                      f"Fast SMA: ${fast_sma_value:.2f}, Slow SMA: ${slow_sma_value:.2f}")

    def on_end_of_day(self):
        """Log portfolio status at end of each day."""
        current_price = self.securities[self.symbol].price
        portfolio_value = self.Portfolio.total_portfolio_value

        if self.is_invested:
            unrealized_pnl = self.securities[self.symbol].holdings.unrealized_profit
            self.debug(f"End of Day - {self.time.date()} - Price: ${current_price:.2f}, "
                      f"Portfolio Value: ${portfolio_value:.2f}, Unrealized P&L: ${unrealized_pnl:.2f}")
        else:
            self.debug(f"End of Day - {self.time.date()} - Price: ${current_price:.2f}, "
                      f"Portfolio Value: ${portfolio_value:.2f}, Cash: ${self.portfolio.cash:.2f}")

    def on_end_of_algorithm(self):
        """Log final algorithm statistics."""
        total_portfolio_value = self.Portfolio.total_portfolio_value
        total_return = (total_portfolio_value / 100000 - 1) * 100
        self.debug(f"=== FINAL ALGORITHM RESULTS ===")
        self.debug(f"Total Signals Generated: {self.signals_count}")
        self.debug(f"Final Portfolio Value: ${total_portfolio_value:.2f}")
        self.debug(f"Total Return: {total_return:.2f}%")
        self.debug(f"Total Fees: ${self.portfolio.total_fees:.2f}")
        if self.is_invested:
            self.debug(f"Final Position: LONG {self.portfolio[self.symbol].quantity} shares")
