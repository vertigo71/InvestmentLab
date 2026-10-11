"""
Represents a single periodic market observation.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PricePoint:
    """
    Historical price information for a given period.
    """

    period_index: int
    date: date
    close: float
    max_close: float
