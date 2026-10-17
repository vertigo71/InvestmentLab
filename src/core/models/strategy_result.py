"""
Represents the outcome of a strategy execution.

A strategy result contains the final
portfolio state after a backtest.
"""

from dataclasses import dataclass


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
    """

    value: float
    shares: float
    cash: float

    @property
    def total_value(self) -> float:
        """
        Returns the invested position
        plus uninvested cash.
        """

        return self.value + self.cash

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
            initial_capital: float,
            years: int
    ) -> float:
        """
        Returns the annualized return.
        """

        return (
                self.total_value / initial_capital
        ) ** (1 / years) - 1
