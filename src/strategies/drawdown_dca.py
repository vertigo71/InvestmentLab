'''
Created on 11 Oct 2026

@author: mxarl
'''

"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below previous highs.
"""

from strategies.strategy import Strategy


class DrawdownDCA(Strategy):

    def __init__(
        self,
        base_amount,
        levels
    ):
        """
        Args:

            base_amount:
                Weekly base contribution.

            levels:
                List of tuples:

                [
                    (0.10, 2),
                    (0.20, 4),
                    (0.30, 8)
                ]
        """

        self.base_amount = base_amount
        self.levels = levels

    def contribution(
        self,
        week,
        price,
        max_price,
        cash_remaining
    ) -> float:

        drawdown = 1 - price / max_price

        multiplier = 1

        for threshold, value in self.levels:

            if drawdown >= threshold:
                multiplier = value

        amount = (
            self.base_amount
            * multiplier
        )

        return min(
            amount,
            cash_remaining
        )

