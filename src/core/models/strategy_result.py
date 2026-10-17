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

    def total_return(
            self,
            initial_capital: float
    ) -> float:
        """
        Returns the total return.
        """

        return (
                self.total_value / initial_capital
        ) - 1

    def cagr(
            self,
            initial_capital: float
    ) -> float:
        """
        Returns the annualized return over
        the elapsed simulation time.
        """

        return (
                self.total_value / initial_capital
        ) ** (1 / self.years) - 1
