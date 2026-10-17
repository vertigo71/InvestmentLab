"""
Supported contribution frequencies.
"""

from enum import Enum

from core.models.data_frequency import DataFrequency


class ContributionFrequency(Enum):
    """
    Time between two contributions, in
    calendar terms.

    The number of data rows between two
    contributions depends on the data
    frequency; see periods().
    """

    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"

    def periods(
            self,
            data_frequency: DataFrequency
    ) -> int:
        """
        Returns the number of data rows
        between two contributions.

        :param data_frequency:
            Frequency of the price data.

        :return:
            Rows between contributions.

        :raises ValueError:
            If the contribution frequency is
            finer than the data allows, e.g.
            WEEKLY contributions with monthly
            data.
        """

        periods = _PERIODS[data_frequency].get(self)

        if periods is None:
            raise ValueError(
                f"{self.name} contributions are "
                f"not possible with "
                f"{data_frequency.name} data"
            )

        return periods


# Data rows between two contributions for
# each data frequency. A missing entry means
# the combination is not possible.
#
# Values for MONTHLY with daily or weekly
# data are approximations (21 trading days,
# 4 weeks).
_PERIODS: dict[
    DataFrequency,
    dict[ContributionFrequency, int]
] = {
    DataFrequency.DAILY: {
        ContributionFrequency.WEEKLY: 5,
        ContributionFrequency.BIWEEKLY: 10,
        ContributionFrequency.MONTHLY: 21,
    },
    DataFrequency.WEEKLY: {
        ContributionFrequency.WEEKLY: 1,
        ContributionFrequency.BIWEEKLY: 2,
        ContributionFrequency.MONTHLY: 4,
    },
    DataFrequency.MONTHLY: {
        ContributionFrequency.MONTHLY: 1,
    },
}