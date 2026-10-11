"""
Created on 11 Oct 2026

@author: mxarl
"""

"""
Traditional Dollar Cost Averaging strategy.
"""

from strategies.strategy import Strategy


class DCA(Strategy):

    def __init__(
            self,
            contribution_amount: float
    ):
        """
        Creates a DCA strategy.

        :param contribution_amount:
            Fixed amount invested each period.
        """

        self.contribution_amount = contribution_amount

    def contribution(
            self,
            period_index: int,
            price: float,
            max_price: float,
            cash_remaining: float
    ) -> float:
        """
        Invests a fixed amount every period.

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

        return min(
            self.contribution_amount,
            cash_remaining
        )
