"""
Defines the base contract for all investment strategies.

Every strategy decides how much capital should be
invested at a given point in time.

Examples:

    - All In
    - Fixed DCA
    - Drawdown DCA
    - Moving Average DCA
"""

from abc import ABC
from abc import abstractmethod


class Strategy(ABC):
    """
    Base class for all investment strategies.
    """

    @abstractmethod
    def contribution(
            self,
            weekly_contribution: float,
            period_index: int,
            price: float,
            max_price: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates how much money should
        be invested.

        :param weekly_contribution:
            Base weekly contribution amount
            proposed by the backtest engine.

            Strategies may invest this amount,
            accumulate multiple periods based
            on their contribution frequency, or
            ignore it entirely.

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

        pass

    @abstractmethod
    def name(self) -> str:
        """
        Returns a human-readable
        strategy name.
        """

        pass
