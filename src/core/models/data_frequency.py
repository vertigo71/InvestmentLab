"""
Supported price data frequencies.
"""

from enum import Enum


class DataFrequency(Enum):
    """
    Time between two consecutive rows
    of price data.
    """

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    