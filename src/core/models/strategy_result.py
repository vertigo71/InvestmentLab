"""
Represents the outcome of a strategy execution.

A strategy result contains the final
portfolio state after a backtest.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class StrategyResult:
    """
    Stores the final portfolio metrics
    produced by a strategy.

    value:
        Market value of the accumulated
        shares (invested position only).

    cash:
        Uninvested cash remaining.

    initial_capital:
        Capital available at the start
        of the simulation.

    start_date:
        Date of the first price point
        (first possible purchase).

    end_date:
        Date of the last price point
        (final valuation).

    max_drawdown:
        Largest peak-to-trough decline of
        total_value during the simulation,
        as a positive fraction (0.25 = -25%).

    """

    value: float
    shares: float
    cash: float
    initial_capital: float
    start_date: date
    end_date: date
    max_drawdown: float

    @property
    def total_value(self) -> float:
        """
        Returns the invested position
        plus uninvested cash.
        """

        return self.value + self.cash

    @property
    def years(self) -> float:
        """
        Elapsed time between the first
        purchase and the final valuation,
        in years.
        """

        return (
                (self.end_date - self.start_date).days /
                365.25
        )

    def total_return(self) -> float:
        """
        Returns the total return.
        """

        return (
                self.total_value / self.initial_capital
        ) - 1

    def cagr(self) -> float:
        """
        Returns the annualized return over
        the elapsed simulation time.
        """

        return (
                self.total_value / self.initial_capital
        ) ** (1 / self.years) - 1

    def target_ratio(
            self,
            target_annual_return: float
    ) -> float:
        """
        Returns the final total value relative to
        a minimum target growth over the elapsed
        simulation time.

            target = initial_capital
                     * (1 + target_annual_return) ** years

            ratio  = total_value / target

        Example with 100,000, a 5% target and
        10 years: the target is 162,889. A final
        value of 179,178 gives 1.10 (10% above
        the target); 114,022 gives 0.70 (70% of
        the target).

        A ratio of at least 1.0 is equivalent to
        a CAGR of at least the target return.

        :param target_annual_return:
            Minimum annual growth wanted, e.g.
            0.05 for 5%.

        :return:
            Final value divided by the target.
        """

        target = (
                self.initial_capital *
                (1 + target_annual_return) ** self.years
        )

        return self.total_value / target
