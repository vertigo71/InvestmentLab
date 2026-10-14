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
    """

    value: float
    shares: float
    cash: float

    def total_return(
            self,
            initial_capital: float
    ) -> float:
        """
        Returns the total return.
        """

        return (
                self.value / initial_capital
        ) - 1

    def cagr(
            self,
            initial_capital: float,
            years: int
    ) -> float:
        """
        Returns the annualized return.
        """

        return (self.value / initial_capital) ** (1 / years) - 1
