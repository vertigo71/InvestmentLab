from core.models.contribution_frequency import ContributionFrequency
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy

"""
Traditional Dollar Cost Averaging strategy.
"""


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
            point: PricePoint,
            weekly_contribution: float,
            cash_remaining: float
    ) -> float:
        """
        Invests a fixed amount at the
        configured frequency.
        """

        # Skip periods that are not
        # contribution periods.
        if (
                point.period_index %
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
