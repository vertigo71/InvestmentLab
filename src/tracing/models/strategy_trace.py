"""
Represents the complete execution
trace of a strategy simulation.
"""

from dataclasses import dataclass

from core.strategies.strategy import Strategy
from tracing.models.strategy_trace_row import (
    StrategyTraceRow
)


@dataclass
class StrategyTrace:
    """
    Stores the complete execution
    trace produced by a strategy
    simulation.

    A StrategyTrace contains the
    simulation metadata, the executed
    strategy and all generated trace
    rows.

    It can be used for debugging,
    validation and CSV exports.

    :param ticker:
        Market ticker used during
        the simulation.

    :param start_date:
        Simulation start date.

    :param end_date:
        Simulation end date.

    :param initial_capital:
        Initial capital available
        to the strategy.

    :param strategy:
        Executed strategy.

    :param rows:
        Generated trace rows.
    """

    # Market ticker.
    ticker: str

    # Simulation start date.
    start_date: str

    # Simulation end date.
    end_date: str

    # Initial simulation capital.
    initial_capital: float

    # Executed strategy.
    strategy: Strategy

    # Generated trace rows.
    rows: list[StrategyTraceRow]
