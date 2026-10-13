"""
Aggregated rolling strategy analysis.
"""

from analysis.rolling_results_analyzer import (
    RollingResultsAnalyzer
)

from experiments.rolling.base import (
    RollingBase
)


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

    for (
            metric_name,
            metric
    ) in analysis.items():

        print(
            f"\n{metric_name}"
        )

        reverse = (
                metric_name !=
                "Average Rank"
        )

        for (
                strategy_name,
                value
        ) in sorted(
            metric.items(),
            key=lambda item: item[1],
            reverse=reverse
        ):

            if isinstance(
                    value,
                    int
            ):
                formatted = f"{value}"

            elif (
                    "Rank"
                    in metric_name
            ):
                formatted = (
                    f"{value:.2f}"
                )

            else:
                formatted = (
                    f"{value:.2%}"
                )

            print(
                f"{strategy_name}: "
                f"{formatted}"
            )


if __name__ == "__main__":
    main()
