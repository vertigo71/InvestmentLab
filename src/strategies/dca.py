'''
Created on 11 Oct 2026

@author: mxarl
'''

"""
Traditional Dollar Cost Averaging strategy.
"""

from strategies.strategy import Strategy


class DCA(Strategy):

    def __init__(
        self,
        weekly_amount: float
    ):
        self.weekly_amount = weekly_amount

    def contribution(
        self,
        week,
        price,
        max_price,
        cash_remaining
    ) -> float:
        """
        Invests a fixed amount every week.
        """

        return min(
            self.weekly_amount,
            cash_remaining
        )
        
        
