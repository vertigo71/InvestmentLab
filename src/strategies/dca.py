from models.contribution_frequency import ContributionFrequency

"""
Traditional Dollar Cost Averaging strategy.
"""

from strategies.strategy import Strategy


class DCA(Strategy):

    def __init__(
            self,
            frequency: ContributionFrequency
    ):
        """
        Creates a DCA strategy.

        :param frequency:
            Contribution frequency.

            Examples:

                WEEKLY

                BIWEEKLY

                MONTHLY
        """

        self.frequency = frequency

    def contribution(
            self,
            weekly_contribution: float,
            period_index: int,
            price: float,
            running_max: float,
            running_avg: float,
            cash_remaining: float
    ) -> float:
        """
        Invests a fixed amount at the
        configured frequency.

        :param weekly_contribution:
            Base weekly contribution amount
            proposed by the engine.

        :param period_index:
            Sequential index of the current period.

        :param price:
            Current asset price.

        :param running_max:
            Maximum asset price observed so far.

        :param running_avg:
            Average price observed from
            the beginning of the simulation
            up to and including this period.

        :param cash_remaining:
            Available uninvested capital.

        :return:
            Amount to invest during
            the current period.
        """

        # Skip periods that are not
        # contribution periods.
        if (
                period_index %
                self.frequency.value
                != 0
        ):
            return 0.0

        # Convert the weekly contribution
        # into a contribution matching the
        # configured frequency.
        amount = (
                weekly_contribution *
                self.frequency.value
        )

        # Never invest more cash
        # than available.
        return min(
            amount,
            cash_remaining
        )

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        return (
            f"DCA_"
            f"{self.frequency.name}"
        )
