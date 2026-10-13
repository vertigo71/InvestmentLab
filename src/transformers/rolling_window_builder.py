"""
Rolling window analysis support.

A rolling window is a fixed-size investment period
that moves forward through time.

Example:

    2016-2019
    2017-2020
    2018-2021
    2019-2022

This component is responsible for generating
those windows from a complete historical dataset.
"""

from models.price_point import PricePoint
from models.rolling_window import RollingWindow


class RollingWindowBuilder:
    """
    Generates rolling windows from a list
    of historical prices.
    """

    @staticmethod
    def _create_window(
            prices: list[PricePoint],
            start_year: int,
            window_years: int
    ) -> RollingWindow:
        """
        Creates a single rolling window.

        :param prices:
            Complete historical dataset.

        :param start_year:
            First year included in the window.

        :param window_years:
            Number of years contained in
            the rolling window.

        :return:
            Rolling window with recalculated
            PricePoint objects.
        """

        end_year = start_year + window_years

        # Extract only the price points
        # belonging to this rolling window.
        window_prices = [
            point
            for point in prices
            if start_year <= point.date.year < end_year
        ]

        # Highest price observed within
        # the current rolling window.
        running_max: float = 0.0

        # Price points rebuilt for this window.
        # with recalculated max_close and period_index.
        recalculated_prices: list[PricePoint] = []

        for period_index, point in enumerate(window_prices):
            running_max = max(
                running_max,
                point.close
            )

            recalculated_prices.append(
                PricePoint(
                    period_index=period_index,
                    date=point.date,
                    close=point.close,
                    max_close=running_max
                )
            )

        return RollingWindow(
            start_year=start_year,
            end_year=end_year,
            prices=recalculated_prices
        )

    @staticmethod
    def create_windows(
            prices: list[PricePoint],
            window_years: int
    ) -> list[RollingWindow]:
        """
        Generates rolling windows.

        Example:

            window_years = 3

            2016-2019
            2017-2020
            2018-2021

        :param prices:
            Complete historical dataset.

        :param window_years:
            Number of years contained in
            each rolling window.

        :return:
            List of windows.
            Each window contains the
            corresponding PricePoint objects.
        """

        windows: list[RollingWindow] = []

        first_year = prices[0].date.year
        last_year = prices[-1].date.year

        for start_year in range(
                first_year,
                last_year - window_years + 1
        ):
            windows.append(
                RollingWindowBuilder._create_window(
                    prices=prices,
                    start_year=start_year,
                    window_years=window_years
                )
            )

        return windows
