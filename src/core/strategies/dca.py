"""
Traditional Dollar Cost Averaging strategy.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.portfolio import PortfolioBase
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy


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

        self._frequency = frequency

    @property
    def frequency(self) -> ContributionFrequency:
        """
        Contribution frequency.
        """

        return self._frequency

    def propose_trade(
            self,
            point: PricePoint,
            contribution_amount: float,
            portfolio: PortfolioBase
    ) -> float:
        """
        Proposes investing the base amount on
        every contribution period.
        """

        # Never invest more cash
        # than available.
        return min(
            contribution_amount,
            portfolio.cash_remaining
        )

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        return (
            f"DCA_"
            f"{self.frequency.name}"
        )
