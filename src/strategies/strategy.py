'''
Created on 10 Oct 2026

@author: mxarl
'''
"""
Defines the base contract for all investment strategies.

Every strategy decides how much capital should be invested
at a given point in time.

Examples:
    - All In
    - Fixed DCA
    - Drawdown DCA
    - Moving Average DCA
"""

from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    Base class for all investment strategies.
    """

    @abstractmethod
    def contribution(
        self,
        week: int,
        price: float,
        max_price: float,
        cash_remaining: float
    ) -> float:
        """
        Calculates how much money should be invested.

        Args:
            week:
                Current week number.

            price:
                Current asset price.

            max_price:
                Maximum price observed up to this point.

            cash_remaining:
                Available uninvested capital.

        Returns:
            Amount to invest during this week.
        """
        pass
