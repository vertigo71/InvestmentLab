"""
Yahoo Finance historical data loader.
"""

import yfinance as yf  # type: ignore

from core.models.price_point import PricePoint
from core.transformers.price_point_builder import PricePointBuilder


# noinspection unresolved-references
class YahooLoader:

    # noinspection unresolved-references,unresolved-references
    @staticmethod
    def load(
            ticker: str,
            start_date: str,
            end_date: str,
            auto_adjust: bool = True
    ) -> list[PricePoint]:
        """
        Loads historical market data from Yahoo Finance.

        :param ticker:
            Yahoo Finance ticker symbol.

        :param start_date:
            Download start date in YYYY-MM-DD format.

        :param end_date:
            Download end date in YYYY-MM-DD format.

        :param auto_adjust:
            Whether Yahoo Finance should
            automatically adjust historical
            prices to account for dividends
            and splits.

            True returns adjusted prices and
            reflects total return assuming
            dividends are reinvested.

            False returns raw market prices.

        :return:
            Historical periodic prices.

        :raises ValueError:
            If no data is returned.
        """

        # Download weekly candles.
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1wk",
            auto_adjust=auto_adjust
        )

        if df is None:
            raise ValueError(
                f"No data returned for ticker '{ticker}'"
            )

        if df.empty:
            raise ValueError(
                f"No data returned for ticker '{ticker}'"
            )

        # Recent versions of yfinance return a MultiIndex even when a
        # single ticker is requested.
        #
        # Example:
        #
        #     MultiIndex([
        #         ('Close', 'URTH'),
        #         ('High',  'URTH'),
        #         ('Low',   'URTH'),
        #         ('Open',  'URTH'),
        #         ('Volume','URTH')
        #     ])
        #
        # This project expects simple column names:
        #
        #     Close
        #     High
        #     Low
        #     Open
        #     Volume
        #
        # Flatten the MultiIndex by keeping only the first level
        # (the price field name) so rows can be accessed through:
        #
        #     row.Close
        #     row.High
        #     row.Low
        #
        # instead of:
        #
        #     ("Close", "URTH")
        #
        df.columns = df.columns.get_level_values(0)

        # Missing closing prices would silently
        # corrupt running averages, drawdowns
        # and share counts. Fail fast instead
        # of dropping rows, since removing a
        # week would also shift the
        # contribution schedule.
        missing = df.index[df["Close"].isna()]

        if len(missing) > 0:
            missing_dates = ", ".join(
                str(index.date())
                for index in missing
            )

            raise ValueError(
                f"Missing closing prices for "
                f"ticker '{ticker}' on: "
                f"{missing_dates}"
            )

        return PricePointBuilder.build(
            (
                row.Index.date(),
                float(row.Close)
            )
            for row in df.itertuples()
        )
