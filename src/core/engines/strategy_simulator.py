from collections.abc import Iterator
from math import floor

from core.models.portfolio import Portfolio
from core.models.price_point import PricePoint
from core.models.simulation_step import SimulationStep
from core.models.strategy_result import StrategyResult
from core.strategies.strategy import Strategy


class StrategySimulator:

    @staticmethod
    def steps(
            prices: list[PricePoint],
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

        :param prices:
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
            prices: list[PricePoint],
            strategy: Strategy,
            initial_capital: float
    ) -> StrategyResult:
        """
        Simulates a strategy and returns
        only the final portfolio state.

        :param prices:
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

        for last_step in StrategySimulator.steps(
                prices=prices,
                strategy=strategy,
                initial_capital=initial_capital
        ):
            pass

        # steps() guarantees at least
        # two periods.
        assert last_step is not None

        return StrategyResult(
            value=last_step.position_value,
            shares=last_step.accumulated_shares,
            cash=last_step.cash_remaining,
            start_date=prices[0].date,
            end_date=last_step.point.date
        )
