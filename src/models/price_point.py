"""
Represents a single periodic market observation.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PricePoint:
    """
    Historical market data for a single period.

    A PricePoint is the basic unit processed by the
    backtesting engine.

    :param period_index:
        Sequential period number.

        Example:

            0, 1, 2, 3, ...

    :param date:
        Market date associated with this period.

    :param close:
        Closing price for the period.

    :param max_close:
        Highest closing price observed from the
        beginning of the simulation up to and
        including this period.
    """

    period_index: int
    date: date
    close: float
    max_close: float
