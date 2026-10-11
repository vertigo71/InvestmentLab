"""
Created on 11 Oct 2026

@author: mxarl
"""

'''
Yahoo Finance historical data loader.
'''

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

        :Parameters:
            ticker : str
                Yahoo Finance ticker symbol.

            start_date : str
                Download start date.

                Format:
                    YYYY-MM-DD

            end_date : str
                Download end date.

                Format:
                    YYYY-MM-DD

        :Returns:
            list[PricePoint]
                Historical weekly prices.

        :Raises:
            ValueError
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

        # Backtest data.
        prices: list[PricePoint] = []

        # Running all-time-high.
        running_max: float = 0.0

        # Iterate over rows using named attributes.
        for week, row in enumerate(df.itertuples()):
            close: float = float(row.Close)

            running_max = max(
                running_max,
                close
            )

            prices.append(
                PricePoint(
                    week=week,
                    date=row.Index.date(),
                    close=close,
                    max_close=running_max
                )
            )

        return prices
