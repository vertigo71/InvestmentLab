"""
Represents the outcome of a rolling window analysis.

A rolling window result contains the
backtest results obtained for a specific
investment period.
"""

from dataclasses import dataclass

from models.strategy_result import StrategyResult


@dataclass
class RollingWindowResult:
    """
    Stores the results of all strategies
    executed for a rolling window.
    """

    # Start year of the window.
    start_year: int

    # Exclusive end year of the window.
    end_year: int

    # Initial capital used to execute
    # all strategies within the window.
    initial_capital: float

    # Results produced by each strategy.
    strategy_results: dict[str, StrategyResult]

    @property
    def window_years(self) -> int:
        """
        Returns the window duration
        in years.
        """

        return (
                self.end_year -
                self.start_year
        )
