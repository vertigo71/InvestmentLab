

from models.portfolio import Portfolio
from models.price_point import PricePoint
from strategies.strategy import Strategy


class BacktestEngine:

    @staticmethod
    def run(
            prices: list[PricePoint],
            strategy: Strategy,
            initial_capital: float
    ) -> dict[str, float]:
        """
        Executes a backtest.

        :param prices:
            Historical market data.

        :param strategy:
            Investment strategy to evaluate.

        :param initial_capital:
            Available capital at the beginning of the simulation.

        :return:
            Dictionary containing portfolio results.
        """

        portfolio = Portfolio(initial_capital)

        for point in prices:
            contribution = strategy.contribution(
                point.period_index,
                point.close,
                point.max_close,
                portfolio.cash_remaining
            )

            portfolio.buy(
                contribution,
                point.close
            )

        final_price = prices[-1].close

        return {
            "value": portfolio.value(final_price),
            "shares": portfolio.shares,
            "cash": portfolio.cash_remaining
        }
