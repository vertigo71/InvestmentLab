from abc import ABC
from abc import abstractmethod

from core.models.contribution_frequency import ContributionFrequency
from core.models.price_point import PricePoint


class Strategy(ABC):
    """
    Base class for all investment strategies.
    """

    @property
    def frequency(self) -> ContributionFrequency | None:
        """
        Contribution frequency. The simulator
        only calls contribution() on
        contribution periods.

        None means the strategy is evaluated
        on every period.
        """

        return None

    @abstractmethod
    def contribution(
            self,
            point: PricePoint,
            contribution_amount: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates how much money should
        be invested.

        Only called on contribution periods,
        according to the strategy frequency.

        :param point:
            Market data for the current
            period: period index, date,
            close price and running
            statistics.

        :param contribution_amount:
            Base amount proposed by the engine
            for this contribution, already
            scaled to the strategy frequency.

            Strategies may invest this amount,
            scale it, or ignore it entirely.

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
