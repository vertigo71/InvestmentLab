'''
Created on 11 Oct 2026

@author: mxarl
'''

"""
All-In strategy.

Invests all available capital on the first week.
"""

from strategies.strategy import Strategy


class AllIn(Strategy):

    def contribution(
        self,
        week: int,
        price: float,
        max_price: float,
        cash_remaining: float
    ) -> float:

        # Invest everything on week zero.
        if week == 0:
            return cash_remaining

        # No further purchases.
        return 0.0
    
    
