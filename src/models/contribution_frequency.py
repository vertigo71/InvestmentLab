

from enum import Enum


class ContributionFrequency(Enum):
    """
    Supported contribution frequencies.

    The enum value represents the number of periods
    between contributions.

    Examples:

        WEEKLY:
            Contribute every period.

        BIWEEKLY:
            Contribute every 2 periods.

        MONTHLY:
            Contribute every 4 periods when using
            weekly market data.
    """

    WEEKLY = 1
    BIWEEKLY = 2
    MONTHLY = 4
