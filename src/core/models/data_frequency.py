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

    def periods_per_year(self) -> int:
        """
        Returns the number of data rows in
        one year.

        Values for daily and weekly data are
        approximations (252 trading days,
        52 weeks).

        Example: 3 years of monthly data are
        3 * 12 = 36 rows.
        """

        return _PERIODS_PER_YEAR[self]


# Data rows in one year for each
# data frequency.
_PERIODS_PER_YEAR: dict[DataFrequency, int] = {
    DataFrequency.DAILY: 252,
    DataFrequency.WEEKLY: 52,
    DataFrequency.MONTHLY: 12,
}