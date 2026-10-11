"""
Created on 11 Oct 2026

@author: mxarl
"""

"""
Yahoo Finance historical data loader.
"""

import yfinance as yf  # type: ignore

from models.price_point import PricePoint


class YahooLoader:

    @staticmethod
    def load(
            ticker: str,
            start_date: str,
            end_date: str
    ) -> list[PricePoint]:
        """
        Loads historical market data from Yahoo Finance.

        :param ticker:
            Yahoo Finance ticker symbol.

        :param start_date:
            Download start date in YYYY-MM-DD format.

        :param end_date:
            Download end date in YYYY-MM-DD format.

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
            interval="1wk"
        )

        if df is None:
            raise ValueError(
                f"No data returned for ticker '{ticker}'"
            )

        if df.empty:
            raise ValueError(
                f"No data returned for ticker '{ticker}'"
            )

        # Generated PricePoint objects.
        prices: list[PricePoint] = []

        # Highest price observed so far.
        running_max: float = 0.0

        for period_index, row in enumerate(df.itertuples()):
            close: float = float(row.Close)

            running_max = max(
                running_max,
                close
            )

            prices.append(PricePoint(
                period_index=period_index,
                date=row.Index.date(),
                close=close,
                max_close=running_max
            ))

        return prices
