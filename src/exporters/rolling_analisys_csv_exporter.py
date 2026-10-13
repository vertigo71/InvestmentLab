"""
Exports aggregated rolling analysis
to CSV.
"""

import csv

from pathlib import Path


class RollingAnalysisCsvExporter:
    """
    Exports rolling analysis metrics
    to CSV format.
    """

    @staticmethod
    def export(
            analysis: dict[str, dict],
            output_file: str | Path
    ) -> None:
        """
        Exports rolling analysis metrics.

        :param analysis:
            Aggregated analysis.

        :param output_file:
            Output CSV file.
        """

        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Example:
        #
        # {
        #     "Win Count": {...},
        #     "Average CAGR": {...},
        #     ...
        # }
        #
        metric_names = list(
            analysis.keys()
        )

        # All metrics contain the same
        # strategy names.
        # {
        #     "Win Count": {
        #         "ALL_IN": 17,
        #         "DDCA": 9
        #     },
        #
        #     "Average CAGR": {
        #         "ALL_IN": 0.0897,
        #         "DDCA": 0.0754
        #     }
        # }
        first_metric = list(
            analysis.values()
        )[0]

        strategy_names = sorted(
            first_metric.keys()
        )

        header = [
            "Strategy"
        ]

        header.extend(
            metric_names
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

            for strategy_name in strategy_names:

                row: list[object] = [
                    strategy_name
                ]

                for metric_name in metric_names:
                    row.append(
                        analysis[
                            metric_name
                        ][
                            strategy_name
                        ]
                    )

                writer.writerow(
                    row
                )
