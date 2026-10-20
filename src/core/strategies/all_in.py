"""
All-In strategy.

Invests all available capital
on the first period.
"""

from core.models.portfolio import PortfolioBase
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy


class AllIn(Strategy):

    def propose_trade(
            self,
            point: PricePoint,
            contribution_amount: float,
            portfolio: PortfolioBase
    ) -> float:
        """
        Proposes the trade of the current period.
        The simulator executes it, within the
        available cash or position.

        The proposed contribution amount
        is ignored.
        """

        if point.period_index == 0:
            return portfolio.cash_remaining

        # No additional purchases afterward.
        return 0.0

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        return "ALL_IN"
