"""
Exports rolling window results to CSV.
"""

import csv

from pathlib import Path

from core.providers.market_context_provider import (
    MarketContextProvider
)
from rolling.models.rolling_window_result import (
    RollingWindowResult
)


class RollingResultsCsvExporter:
    """
    Exports rolling window results
    to CSV format.
    """

    @staticmethod
    def export(
            results: list[RollingWindowResult],
            output_file: str | Path
    ) -> None:
        """
        Exports rolling window results.

        :param results:
            Rolling window results.

        :param output_file:
            Output CSV file path.
        """

        if not results:
            return

        output_file = Path(
            output_file
        )

        # Create the output directory
        # if it does not already exist.
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Strategy names are identical
        # across all rolling windows.
        #
        # strategy_results:
        #
        #     dict[str, StrategyResult]
        #
        strategy_names = sorted(
            results[0].strategy_results.keys()
        )

        header: list[str] = [
            "StartYear",
            "EndYear",
            "MarketContext"
        ]

        header.extend(
            strategy_names
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

            for result in results:

                context = "\n".join(
                    MarketContextProvider.get_window_context(
                        start_year=result.start_year,
                        end_year=result.end_year
                    )
                )

                row: list[object] = [
                    result.start_year,
                    result.end_year,
                    context
                ]

                for strategy_name in strategy_names:
                    strategy_result = (
                        result.strategy_results[
                            strategy_name
                        ]
                    )

                    row.append(
                        strategy_result.cagr(
                            result.initial_capital,
                        )
                    )

                writer.writerow(
                    row
                )
