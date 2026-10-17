"""
All-In strategy.

Invests all available capital
on the first period.
"""
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy


class AllIn(Strategy):

    def contribution(
            self,
            point: PricePoint,
            weekly_contribution: float,
            cash_remaining: float
    ) -> float:
        """
        Invests all available capital
        during the first period.

        The proposed weekly contribution
        is ignored.
        """

        if point.period_index == 0:
            return cash_remaining

        # No additional purchases afterward.
        return 0.0

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        return "ALL_IN"
