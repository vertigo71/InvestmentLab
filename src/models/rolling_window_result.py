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

    start_year: int
    end_year: int

    strategy_results: dict[str, StrategyResult]
