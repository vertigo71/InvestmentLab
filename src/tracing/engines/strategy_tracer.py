"""
Generates detailed traces for
strategy simulations.
"""

from math import floor

from core.models.portfolio import Portfolio
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

        portfolio = Portfolio(
            initial_capital
        )

        trace_rows: list[
            StrategyTraceRow
        ] = []

        # Reserve one period when
        # calculating the base
        # contribution amount.
        investment_periods = (
                len(prices) - 1
        )

        # Base contribution proposed
        # to the strategy.
        contribution_amount = floor(
            initial_capital /
            investment_periods
        )

        # Total capital invested so far.
        accumulated_contribution = 0.0

        for point in prices:
            contribution = (
                strategy.contribution(
                    weekly_contribution=
                    contribution_amount,
                    period_index=
                    point.period_index,
                    price=point.close,
                    running_max=
                    point.running_max,
                    running_avg=
                    point.running_avg,
                    cash_remaining=
                    portfolio.cash_remaining
                )
            )

            # Capture the share count
            # before the purchase in
            # order to calculate the
            # number of shares acquired
            # during this period.
            shares_before = (
                portfolio.shares
            )

            portfolio.buy(
                contribution,
                point.close
            )

            shares_bought = (
                    portfolio.shares -
                    shares_before
            )

            accumulated_contribution += (
                contribution
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

            position_value = (
                    portfolio.shares *
                    point.close
            )

            trace_rows.append(
                StrategyTraceRow(
                    period_index=
                    point.period_index,

                    date=
                    point.date,

                    close=
                    point.close,

                    running_max=
                    point.running_max,

                    running_avg=
                    point.running_avg,

                    drawdown_max=
                    drawdown_max,

                    drawdown_avg=
                    drawdown_avg,

                    contribution=
                    contribution,

                    accumulated_contribution=
                    accumulated_contribution,

                    shares_bought=
                    shares_bought,

                    accumulated_shares=
                    portfolio.shares,

                    position_value=
                    position_value,

                    cash_remaining=
                    portfolio.cash_remaining
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
