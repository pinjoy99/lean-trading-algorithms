# region imports
from AlgorithmImports import *
# endregion

class MyProject(QCAlgorithm):

    def initialize(self):
        # Locally Lean installs free sample data, to download more data please visit https://www.quantconnect.com/docs/v2/lean-cli/datasets/downloading-data
        self.set_start_date(2023, 1, 1)  # Set Start Date
        self.set_end_date(2023, 1, 31)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash
        self.add_equity("SPY", Resolution.MINUTE)

        # Set SPY as the benchmark
        self.SetBenchmark("SPY")

        # 1-minute data export tracking
        self.minute_data_file = "buyhold_minute_equity_data.csv"
        self.minute_data_written = False
        self._write_minute_data_header()
        self.debug(f"📊 Exporting 1-minute data to: {self.minute_data_file}")

    def _write_minute_data_header(self):
        """Write CSV header for 1-minute data export."""
        with open(self.minute_data_file, 'w') as f:
            f.write("timestamp,datetime_utc,open,high,low,close,volume,portfolio_value,equity\n")

    def _export_minute_data(self, data: Slice):
        """Export 1-minute data to CSV file."""
        symbol = "SPY"
        if symbol not in data:
            return

        bar = data[symbol]
        timestamp = int(bar.end_time.timestamp())
        portfolio_value = self.Portfolio.total_portfolio_value

        # Write to CSV
        with open(self.minute_data_file, 'a') as f:
            f.write(f"{timestamp},{bar.end_time.isoformat()},{bar.open:.2f},"
                   f"{bar.high:.2f},{bar.low:.2f},{bar.close:.2f},"
                   f"{bar.volume},{portfolio_value:.2f},{portfolio_value:.2f}\n")

    def on_data(self, data: Slice):
        """on_data event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        # Export 1-minute data (true minute intervals, not 12-minute)
        self._export_minute_data(data)

        if not self.portfolio.invested:
            self.set_holdings("SPY", 1)
            self.debug("Purchased Stock")
