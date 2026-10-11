'''
Created on 11 Oct 2026

@author: mxarl
'''

from models.portfolio import Portfolio

class BacktestEngine:

    def run(
        self,
        prices,
        strategy,
        initial_capital
    ) -> dict[str, float]:

        portfolio = Portfolio(initial_capital)

        for point in prices:

            contribution = strategy.contribution(
                point.week,
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
