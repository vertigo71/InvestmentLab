from math import floor
from typing import Final

from data.yahoo_loader import YahooLoader
from factories.strategy_factory import StrategyFactory
from provider.market_context_provider import MarketContextProvider

from transformers.rolling_window_builder import RollingWindowBuilder

from analysis.rolling_backtest_engine import RollingBacktestEngine

from models.contribution_frequency import ContributionFrequency

from strategies.all_in import AllIn
from strategies.dca import DCA
from strategies.drawdown_dca import DrawdownDCA

INITIAL_CAPITAL: Final = 100000
WINDOW_YEARS: Final = 3
# Reserve the final period for portfolio valuation.
INVESTMENT_PERIODS: Final = 52 * WINDOW_YEARS - 1


# URTH   -> 2012-
# VT     -> 2008-
# ^GSPC  -> 1990-
def main():
    prices = YahooLoader.load(
        ticker="^GSPC",
        start_date="1990-01-01",
        end_date="2027-01-01"
    )

    windows = RollingWindowBuilder.create_windows(
        prices=prices,
        window_years=WINDOW_YEARS
    )

    weekly_contribution = floor(INITIAL_CAPITAL / INVESTMENT_PERIODS)

    strategies = StrategyFactory.create(
        contribution_amount=weekly_contribution
    )

    results = RollingBacktestEngine.run(
        windows=windows,
        strategies=strategies,
        initial_capital=INITIAL_CAPITAL
    )

    for result in results:

        print(
            f"\n{result.start_year}-{result.end_year}"
        )

        for context in MarketContextProvider.get_window_context(
                start_year=result.start_year,
                end_year=result.end_year
        ):
            print(f"  • {context}")

        for (
                strategy_name,
                strategy_result
        ) in result.strategy_results.items():
            cash_text = ""

            if strategy_result.cash > 0:
                cash_text = (
                    f" Cash: €{strategy_result.cash:,.2f}"
                )

            print(
                f"{strategy_name}: "
                f"{strategy_result.value:,.2f} "
                f"({strategy_result.cagr(INITIAL_CAPITAL, WINDOW_YEARS):.2%})"
                f"{cash_text}"
            )


if __name__ == "__main__":
    main()
