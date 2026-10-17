from abc import ABC
from abc import abstractmethod

from core.models.price_point import PricePoint


class Strategy(ABC):
    """
    Base class for all investment strategies.
    """

    @abstractmethod
    def contribution(
            self,
            point: PricePoint,
            weekly_contribution: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates how much money should
        be invested.

        :param point:
            Market data for the current
            period: period index, date,
            close price and running
            statistics.

        :param weekly_contribution:
            Base weekly contribution amount
            proposed by the backtest engine.

            Strategies may invest this amount,
            accumulate multiple periods based
            on their contribution frequency, or
            ignore it entirely.

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
        Returns the strategy name.
        """

        pass
