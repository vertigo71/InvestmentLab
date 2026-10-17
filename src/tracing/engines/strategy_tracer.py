"""
Generates detailed traces for
strategy simulations.
"""

from core.engines.strategy_simulator import StrategySimulator
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy

from tracing.models.strategy_trace import (
    StrategyTrace
)
from tracing.models.strategy_trace_row import (
    StrategyTraceRow
)


class StrategyTracer:
    """
    Generates a detailed execution trace
    for a strategy simulation.

    The simulation itself is delegated to
    StrategySimulator, so the trace always
    reflects the exact same logic used by
    the rolling analysis.
    """

    @staticmethod
    def run(
            ticker: str,
            start_date: str,
            end_date: str,
            prices: list[PricePoint],
            strategy: Strategy,
            initial_capital: float
    ) -> StrategyTrace:
        """
        Executes a strategy simulation and
        generates a complete execution trace.

        :param ticker:
            Market ticker used during
            the simulation.

        :param start_date:
            Simulation start date.

        :param end_date:
            Simulation end date.

        :param prices:
            Historical market prices.

        :param strategy:
            Strategy to execute.

        :param initial_capital:
            Initial capital available
            to the strategy.

        :return:
            Generated strategy trace.
        """

        trace_rows: list[StrategyTraceRow] = []

        # Total capital invested so far.
        accumulated_contribution = 0.0

        for step in StrategySimulator.steps(
                prices=prices,
                strategy=strategy,
                initial_capital=initial_capital
        ):
            point = step.point

            accumulated_contribution += (
                step.contribution
            )

            # Drawdown relative to the
            # highest observed price.
            drawdown_max = (
                    1.0 -
                    point.close /
                    point.running_max
            )

            # Drawdown relative to the
            # running average price.
            drawdown_avg = (
                    1.0 -
                    point.close /
                    point.running_avg
            )

            trace_rows.append(
                StrategyTraceRow(
                    period_index=point.period_index,
                    date=point.date,
                    close=point.close,
                    running_max=point.running_max,
                    running_avg=point.running_avg,
                    drawdown_max=drawdown_max,
                    drawdown_avg=drawdown_avg,
                    contribution=step.contribution,
                    accumulated_contribution=accumulated_contribution,
                    shares_bought=step.shares_bought,
                    accumulated_shares=step.accumulated_shares,
                    position_value=step.position_value,
                    cash_remaining=step.cash_remaining
                )
            )

        return StrategyTrace(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            strategy=strategy,
            rows=trace_rows
        )
