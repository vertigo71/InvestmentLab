from collections.abc import Iterator
from math import floor

from core.models.portfolio import Portfolio
from core.models.price_series import PriceSeries
from core.models.simulation_step import SimulationStep
from core.models.strategy_result import StrategyResult
from core.strategies.strategy import Strategy


class StrategySimulator:

    @staticmethod
    def steps(
            series: PriceSeries,
            strategy: Strategy,
            initial_capital: float
    ) -> Iterator[SimulationStep]:
        """
        Simulates a strategy period by
        period.

        This is the single simulation loop
        of the project. Both the final
        result (run) and the detailed
        trace (StrategyTracer) are built
        from these steps.

        :param series:
            Historical market prices.

        :param strategy:
            Investment strategy to simulate.

        :param initial_capital:
            Initial capital available at
            the start of the simulation.

        :return:
            One step per price point.

        :raises ValueError:
            If fewer than two prices are
            provided.
        """

        prices = series.points

        if len(prices) < 2:
            raise ValueError(
                "At least two price points "
                "are required"
            )

        portfolio = Portfolio(
            initial_capital
        )

        # Number of contribution periods
        # used to calculate the base
        # contribution amount.
        #
        # Subtract one period to avoid
        # allocating more capital than
        # available due to rounding.
        investment_periods = (
                len(prices) - 1
        )

        # Base contribution amount
        # proposed to all strategies.
        weekly_contribution = floor(
            initial_capital /
            investment_periods
        )

        for point in prices:
            requested = strategy.contribution(
                point=point,
                weekly_contribution=weekly_contribution,
                cash_remaining=portfolio.cash_remaining
            )

            shares_before = portfolio.shares
            cash_before = portfolio.cash_remaining

            portfolio.buy(
                requested,
                point.close
            )

            yield SimulationStep(
                point=point,
                contribution=(
                        cash_before -
                        portfolio.cash_remaining
                ),
                shares_bought=(
                        portfolio.shares -
                        shares_before
                ),
                accumulated_shares=portfolio.shares,
                cash_remaining=portfolio.cash_remaining
            )

    @staticmethod
    def run(
            series: PriceSeries,
            strategy: Strategy,
            initial_capital: float
    ) -> StrategyResult:
        """
        Simulates a strategy and returns
        the final portfolio state.

        The maximum drawdown is measured on
        the total portfolio value (position
        plus cash). Moving cash into shares
        does not change the total, so only
        market movements affect it, which
        makes strategies with uninvested
        cash comparable with lump sum.

        :param series:
            Historical market prices.

        :param strategy:
            Investment strategy to simulate.

        :param initial_capital:
            Initial capital available at
            the start of the simulation.

        :return:
            Strategy result containing
            final portfolio metrics.
        """

        last_step: SimulationStep | None = None

        # Highest total value reached so far.
        # The portfolio starts fully in cash.
        peak_value = initial_capital

        # Largest decline from a previous
        # peak, as a positive fraction.
        max_drawdown = 0.0

        for step in StrategySimulator.steps(
                series=series,
                strategy=strategy,
                initial_capital=initial_capital
        ):
            peak_value = max(
                peak_value,
                step.total_value
            )

            max_drawdown = max(
                max_drawdown,
                1.0 - step.total_value / peak_value
            )

            last_step = step

        # steps() guarantees at least
        # two periods.
        assert last_step is not None

        return StrategyResult(
            value=last_step.position_value,
            shares=last_step.accumulated_shares,
            cash=last_step.cash_remaining,
            start_date=series.points[0].date,
            end_date=last_step.point.date,
            max_drawdown=max_drawdown
        )
