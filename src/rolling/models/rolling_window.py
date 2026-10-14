"""
Represents a rolling analysis window.

Examples:

    2016-2019
    2017-2020
    2018-2021
"""

from dataclasses import dataclass
from core.models.price_point import PricePoint


@dataclass
class RollingWindow:
    """
    Contains all market data belonging
    to a rolling analysis period.
    """

    start_year: int
    end_year: int
    prices: list[PricePoint]
