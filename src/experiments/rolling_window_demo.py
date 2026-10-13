"""
Displays detailed results for each
rolling analysis window.
"""

from typing import Final

from analysis.rolling_backtest_engine import (
    RollingBacktestEngine
)

from data.yahoo_loader import YahooLoader

from factories.strategy_factory import (
    StrategyFactory
)

from provider.market_context_provider import (
    MarketContextProvider
)

from transformers.rolling_window_builder import (
    RollingWindowBuilder
)

INITIAL_CAPITAL: Final = 100000
WINDOW_YEARS: Final = 3

# Available datasets:
#
# URTH  -> 2012-
# VT    -> 2008-
# ^GSPC -> 1990-
TICKER: Final = "^GSPC"

START_DATE: Final = "1990-01-01"
END_DATE: Final = "2028-01-01"


def main():
    """
    Executes a rolling window analysis
    and prints detailed results for
    every window.
    """

    prices = YahooLoader.load(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE
    )

    windows = (
        RollingWindowBuilder.create_windows(
            prices=prices,
            window_years=WINDOW_YEARS
        )
    )

    strategies = StrategyFactory.create()

    results = RollingBacktestEngine.run(
        windows=windows,
        strategies=strategies,
        initial_capital=INITIAL_CAPITAL
    )

    for result in results:

        print(
            f"\n"
            f"{result.start_year}-"
            f"{result.end_year}"
        )

        for context in (
                MarketContextProvider.get_window_context(
                    start_year=result.start_year,
                    end_year=result.end_year
                )
        ):
            print(
                f"  • {context}"
            )

        for (
                strategy_name,
                strategy_result
        ) in result.strategy_results.items():

            cash_text = ""

            if strategy_result.cash > 0:
                cash_text = (
                    f" Cash: "
                    f"€{strategy_result.cash:,.2f}"
                )

            print(
                f"{strategy_name}: "
                f"{strategy_result.value:,.2f} "
                f"("
                f"{strategy_result.cagr(
                    result.initial_capital,
                    result.window_years
                ):.2%}"
                f")"
                f"{cash_text}"
            )


if __name__ == "__main__":
    main()
