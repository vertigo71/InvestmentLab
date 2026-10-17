"""
Builds PricePoint series with running statistics.
"""

from collections.abc import Iterable
from datetime import date

from core.models.price_point import PricePoint


class PricePointBuilder:
    """
    Converts raw (date, close) observations into
    PricePoint objects.

    This is the single place where period
    indexes and running statistics are
    calculated. Statistics always start from
    the first observation provided, so a
    rolling window gets its own running
    maximum and average.
    """

    @staticmethod
    def build(
            observations: Iterable[tuple[date, float]]
    ) -> list[PricePoint]:
        """
        Builds a PricePoint series.

        :param observations:
            Chronologically ordered
            (date, close) pairs.

        :return:
            PricePoint objects with period
            indexes starting at 0 and running
            statistics calculated from the
            first observation.
        """

        prices: list[PricePoint] = []

        # Highest closing price observed so far.
        running_max: float = 0.0

        # Sum of closing prices observed so far.
        running_sum: float = 0.0

        for period_index, (point_date, close) in enumerate(
                observations
        ):
            running_max = max(
                running_max,
                close
            )

            running_sum += close

            running_avg = (
                    running_sum /
                    (period_index + 1)
            )

            prices.append(
                PricePoint(
                    period_index=period_index,
                    date=point_date,
                    close=close,
                    running_max=running_max,
                    running_avg=running_avg
                )
            )

        return prices