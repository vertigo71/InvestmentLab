"""
Defines the base contract for all investment strategies.

Every strategy decides how much capital should be
invested on each contribution period. The contribution
schedule is computed by the simulator from the strategy
frequency and the data frequency.

Examples:

    - All In
    - Fixed DCA
    - Drawdown DCA
    - Moving Average DCA
"""

from abc import ABC
from abc import abstractmethod

from core.models.contribution_frequency import ContributionFrequency
from core.models.portfolio import PortfolioBase
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
    def propose_trade(
            self,
            point: PricePoint,
            contribution_amount: float,
            portfolio: PortfolioBase
    ) -> float:
        """
        Proposes the trade of the current period.
        The simulator executes it, within the
        available cash or position.

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

        :param portfolio:
            Snapshot of the portfolio before the
            trade: cash and shares. Read-only.

        :return:
            Amount of money to trade:

                positive  buy shares
                negative  sell shares
                0.0       do nothing
        """

        pass

    @abstractmethod
    def name(self) -> str:
        """
        Returns the strategy name.
        """

        pass
