"""
Yahoo Finance price data source.
"""

from dataclasses import dataclass

from core.models.data_frequency import DataFrequency
from core.models.price_series import PriceSeries
from core.providers.data_source import DataSource
from core.providers.yahoo_loader import YahooLoader


@dataclass(frozen=True)
class YahooSource(DataSource):
    """
    Downloads prices from Yahoo Finance.

    :param ticker:
        Yahoo Finance ticker symbol.

        Examples:

            ^SP500TR
            URTH
            0P00000RQC.F

    :param frequency:
        Data frequency to download.
        Defaults to weekly.

    :param auto_adjust:
        Whether prices are adjusted for
        dividends and splits. See
        YahooLoader.load().
    """

    ticker: str
    frequency: DataFrequency = DataFrequency.WEEKLY
    auto_adjust: bool = True

    @property
    def name(self) -> str:
        """
        Ticker without characters that are
        not valid in file names.

            ^SP500TR -> SP500TR
        """

        return self.ticker.replace("^", "")

    def load(
            self,
            start_date: str,
            end_date: str
    ) -> PriceSeries:
        """
        Downloads the price series for a
        date range.
        """

        return YahooLoader.load(
            ticker=self.ticker,
            start_date=start_date,
            end_date=end_date,
            frequency=self.frequency,
            auto_adjust=self.auto_adjust
        )