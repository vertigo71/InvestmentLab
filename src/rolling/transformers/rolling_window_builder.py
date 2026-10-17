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

from core.models.price_series import PriceSeries
from core.transformers.price_point_builder import PricePointBuilder
from rolling.models.rolling_window import RollingWindow


class RollingWindowBuilder:
    """
    Generates rolling windows from a list
    of historical prices.
    """

    @staticmethod
    def _create_window(
            series: PriceSeries,
            start_year: int,
            window_years: int
    ) -> RollingWindow:
        """
        Creates a single rolling window.

        Running statistics and period indexes
        are recalculated from the first price
        of the window, as if the simulation
        started there. The data frequency is
        kept from the full series.

        :param series:
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

        window_points = PricePointBuilder.build(
            (point.date, point.close)
            for point in series.points
            if start_year <= point.date.year < end_year
        )

        return RollingWindow(
            start_year=start_year,
            end_year=end_year,
            series=PriceSeries(
                frequency=series.frequency,
                points=window_points
            )
        )

    @staticmethod
    def create_windows(
            series: PriceSeries,
            window_years: int
    ) -> list[RollingWindow]:
        """
        Generates rolling windows.

        Example:

            window_years = 3

            2016-2019
            2017-2020
            2018-2021

        :param series:
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

        first_year = series.points[0].date.year
        last_year = series.points[-1].date.year

        for start_year in range(
                first_year,
                last_year - window_years + 1
        ):
            windows.append(
                RollingWindowBuilder._create_window(
                    series=series,
                    start_year=start_year,
                    window_years=window_years
                )
            )

        return windows
