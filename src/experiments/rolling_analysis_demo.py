"""
Aggregated rolling strategy analysis.

Runs all configured strategies across
multiple rolling windows and prints
summary statistics.
"""

from typing import Final

from analysis.rolling_backtest_engine import (
    RollingBacktestEngine
)

from analysis.rolling_results_analyzer import (
    RollingResultsAnalyzer
)

from data.yahoo_loader import YahooLoader

from factories.strategy_factory import (
    StrategyFactory
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
    Executes a rolling-window strategy
    comparison and prints aggregate
    performance statistics.
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

    print("\nWin Count")

    wins = (
        RollingResultsAnalyzer.get_win_count(
            results
        )
    )

    for (
            strategy_name,
            win_count
    ) in sorted(
        wins.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{win_count}"
        )

    print("\nAverage CAGR")

    average_cagrs = (
        RollingResultsAnalyzer.get_average_cagr(
            results
        )
    )

    for (
            strategy_name,
            cagr
    ) in sorted(
        average_cagrs.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{cagr:.2%}"
        )

    print("\nBest CAGR")

    best_cagrs = (
        RollingResultsAnalyzer.get_best_cagr(
            results
        )
    )

    for (
            strategy_name,
            cagr
    ) in sorted(
        best_cagrs.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{cagr:.2%}"
        )

    print("\nWorst CAGR")

    worst_cagrs = (
        RollingResultsAnalyzer.get_worst_cagr(
            results
        )
    )

    for (
            strategy_name,
            cagr
    ) in sorted(
        worst_cagrs.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{cagr:.2%}"
        )

    print("\nCAGR Std Dev")

    std_devs = (
        RollingResultsAnalyzer.get_cagr_std_dev(
            results
        )
    )

    for (
            strategy_name,
            std_dev
    ) in sorted(
        std_devs.items(),
        key=lambda item: item[1]
    ):
        print(
            f"{strategy_name}: "
            f"{std_dev:.2%}"
        )


if __name__ == "__main__":
    main()
