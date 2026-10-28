"""
Aggregated rolling strategy analysis.
"""
from textwrap import fill

from core.settings import SETTINGS
from rolling.analysis.rolling_results_analyzer import (
    RollingResultsAnalyzer
)

from rolling.experiments.base import (
    RollingBase
)
from rolling.models.metric_format import MetricFormat


def main():
    """
    Prints aggregate rolling analysis.
    """

    results = (
        RollingBase.build_results()
    )

    analysis = (
        RollingResultsAnalyzer.build_analysis(
            results,
            target_annual_return=
            SETTINGS.rolling.target_annual_return
        )
    )

    # Legend with what each strategy does.
    RollingBase.print_strategy_legend(
        results
    )

    # Display each analysis metric.
    for metric in analysis:

        print(
            f"\n{metric.name}"
        )

        # Description wrapped to a readable width
        # and indented under the metric name.
        print(
            fill(
                metric.description,
                width=72,
                initial_indent="  ",
                subsequent_indent="  "
            )
        )

        # Sort strategies according
        # to the metric preferences.
        for (
                strategy_name,
                value
        ) in sorted(
            metric.values.items(),
            key=lambda item: item[1],
            reverse=metric.reverse
        ):

            # Format the metric value
            # according to the metric
            # display configuration.
            if (
                    metric.format ==
                    MetricFormat.INTEGER
            ):
                formatted = (
                    f"{value}"
                )

            elif (
                    metric.format ==
                    MetricFormat.DECIMAL
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
