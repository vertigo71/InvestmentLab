from math import floor

from core.models.portfolio import Portfolio
from core.models.price_point import PricePoint
from core.models.strategy_result import StrategyResult
from core.strategies.strategy import Strategy


class StrategySimulator:

    @staticmethod
    def run(
            prices: list[PricePoint],
            strategy: Strategy,
            initial_capital: float
    ) -> StrategyResult:
        """
        Simulates the execution of an
        investment strategy over a
        sequence of historical prices.

        :param prices:
            Historical market prices.

        :param strategy:
            Investment strategy to
            simulate.

        :param initial_capital:
            Initial capital available
            at the start of the
            simulation.

        :return:
            Strategy result containing
            final portfolio metrics.
        """

        portfolio = Portfolio(
            initial_capital
        )

        # Reserve the final period
        # for portfolio valuation.
        investment_periods = (
                len(prices) - 1
        )

        # Base contribution amount
        # proposed to all strategies.
        contribution_amount = floor(
            initial_capital /
            investment_periods
        )

        for point in prices:
            contribution = strategy.contribution(
                weekly_contribution=contribution_amount,
                period_index=point.period_index,
                price=point.close,
                running_max=point.running_max,
                running_avg=point.running_avg,
                cash_remaining=portfolio.cash_remaining
            )

            portfolio.buy(
                contribution,
                point.close
            )

        final_price = (
            prices[-1].close
        )

        final_value = portfolio.value(
            final_price
        )

        return StrategyResult(
            value=final_value,
            shares=portfolio.shares,
            cash=portfolio.cash_remaining
        )
