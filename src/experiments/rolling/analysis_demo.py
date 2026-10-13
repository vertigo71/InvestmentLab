"""
Aggregated rolling strategy analysis.
"""
from analysis.rolling_results_analyzer import RollingResultsAnalyzer
from experiments.rolling.base import RollingBase


def main():
    """
    Prints aggregate rolling analysis.
    """

    results = (
        RollingBase.build_results()
    )

    analysis = (
        RollingResultsAnalyzer.build_analysis(
            results
        )
    )

    print("\nWin Count")

    for strategy_name, value in sorted(
            analysis["wins"].items(),
            key=lambda item: item[1],
            reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{value}"
        )

    print("\nAverage CAGR")

    for strategy_name, value in sorted(
            analysis["average_cagr"].items(),
            key=lambda item: item[1],
            reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{value:.2%}"
        )

    print("\nBest CAGR")

    for strategy_name, value in sorted(
            analysis["best_cagr"].items(),
            key=lambda item: item[1],
            reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{value:.2%}"
        )

    print("\nWorst CAGR")

    for strategy_name, value in sorted(
            analysis["worst_cagr"].items(),
            key=lambda item: item[1],
            reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{value:.2%}"
        )

    print("\nCAGR Std Dev")

    for strategy_name, value in sorted(
            analysis["std_dev"].items(),
            key=lambda item: item[1]
    ):
        print(
            f"{strategy_name}: "
            f"{value:.2%}"
        )

    print("\nAverage Rank")

    for strategy_name, value in sorted(
            analysis["average_rank"].items(),
            key=lambda item: item[1]
    ):
        print(
            f"{strategy_name}: "
            f"{value:.2f}"
        )


if __name__ == "__main__":
    main()
