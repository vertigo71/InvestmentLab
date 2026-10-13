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

from experiments.rolling_base import RollingBase


def main():
    """
    Executes a rolling-window strategy
    comparison and prints aggregate
    performance statistics.
    """

    results = (
        RollingBase.build_results()
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

    print("\nAverage Rank")

    average_ranks = (
        RollingResultsAnalyzer.get_average_rank(
            results
        )
    )

    for (
            strategy_name,
            rank
    ) in sorted(
        average_ranks.items(),
        key=lambda item: item[1]
    ):
        print(
            f"{strategy_name}: "
            f"{rank:.2f}"
        )


if __name__ == "__main__":
    main()
