"""
Represents a series of price observations
with a known data frequency.
"""

from dataclasses import dataclass

from core.models.data_frequency import DataFrequency
from core.models.price_point import PricePoint


@dataclass(frozen=True)
class PriceSeries:
    """
    Price points together with the time
    between two consecutive rows.

    The frequency is set by the loader that
    produced the data, so it travels with
    the prices through windows, simulator
    and tracer.

    :param frequency:
        Time between two consecutive rows.

    :param points:
        Chronologically ordered price points.
    """

    frequency: DataFrequency
    points: list[PricePoint]