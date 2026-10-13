"""
All-In strategy.

Invests all available capital
on the first period.
"""

from strategies.strategy import Strategy


class AllIn(Strategy):

    def contribution(
            self,
            weekly_contribution: float,
            period_index: int,
            price: float,
            max_price: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates the contribution amount.

        :param weekly_contribution:
            Base weekly contribution amount
            proposed by the engine.

            This value is ignored by the
            All-In strategy.

        :param period_index:
            Sequential index of the current period.

        :param price:
            Current asset price.

        :param max_price:
            Maximum price observed up to
            this point.

        :param cash_remaining:
            Available uninvested capital.

        :return:
            Amount to invest during
            the current period.
        """

        # Invest everything during
        # the first period regardless
        # of the proposed contribution.
        if period_index == 0:
            return cash_remaining

        # No additional purchases afterward.
        return 0.0

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        return "ALL_IN"
