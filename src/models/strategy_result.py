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
    