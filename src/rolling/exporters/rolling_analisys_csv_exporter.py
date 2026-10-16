"""
Exports aggregated rolling analysis
to CSV.
"""

import csv

from pathlib import Path

from rolling.models.analysis_metric import (
    AnalysisMetric
)


class RollingAnalysisCsvExporter:
    """
    Exports rolling analysis metrics
    to CSV format.
    """

    @staticmethod
    def export(
            analysis: list[AnalysisMetric],
            output_file: str | Path
    ) -> None:
        """
        Exports rolling analysis metrics.

        :param analysis:
            Analysis metrics.

        :param output_file:
            Output CSV file.
        """

        output_file = Path(
            output_file
        )

        # Create the output directory
        # if it does not already exist.
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # All metrics contain the same
        # strategy names.
        first_metric = analysis[0]

        strategy_names = sorted(
            first_metric.values.keys()
        )

        header = [
            "Strategy"
        ]

        # Add all metric names to
        # the CSV header.
        header.extend(
            metric.name
            for metric in analysis
        )

        with output_file.open(
                mode="w",
                newline="",
                encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(
                csv_file
            )

            writer.writerow(
                header
            )

            # Export one row per
            # strategy.
            for strategy_name in strategy_names:

                row: list[object] = [
                    strategy_name
                ]

                # Export the value
                # associated with the
                # current strategy for
                # each metric.
                for metric in analysis:
                    row.append(
                        metric.values[
                            strategy_name
                        ]
                    )

                writer.writerow(
                    row
                )
