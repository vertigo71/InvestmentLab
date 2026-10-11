"""
Created on 11 Oct 2026

@author: mxarl
"""

"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below previous highs.
"""

from strategies.strategy import Strategy
from models.contribution_frequency import ContributionFrequency


class DrawdownDCA(Strategy):

    def __init__(
            self,
            base_amount: float,
            levels: list[tuple[float, float]],
            frequency: ContributionFrequency
    ):
        """
        Creates a drawdown-based DCA strategy.

        :param base_amount:
            Base contribution amount for each period.

        :param levels:
            Drawdown thresholds and associated multipliers.

            Example:

                [
                    (0.01, 2),
                    (0.02, 4),
                    (0.03, 8)
                ]

        :param frequency:
                Contribution frequency.

                Examples:

                    WEEKLY
                    BIWEEKLY
                    MONTHLY
        """

        self.base_amount = base_amount
        self.levels = levels
        self.frequency = frequency

    def contribution(
            self,
            period_index: int,
            price: float,
            max_price: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates the contribution amount.

        :param period_index:
            Sequential index of the current period.

        :param price:
            Current asset price.

        :param max_price:
            Maximum asset price observed so far.

        :param cash_remaining:
            Available uninvested capital.

        :return:
            Amount to invest during the current period.
        """

        # Skip periods that are not contribution periods.
        if period_index % self.frequency.value != 0:
            return 0.0

        # Calculate current drawdown from the historical high.
        drawdown = 1.0 - price / max_price

        multiplier: float = 1.0

        # Determine the contribution multiplier.
        for threshold, value in self.levels:

            if drawdown >= threshold:
                multiplier = value

        amount = self.base_amount * multiplier

        return min(
            amount,
            cash_remaining
        )
