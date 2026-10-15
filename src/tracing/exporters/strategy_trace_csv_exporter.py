"""
Exports strategy traces to CSV.
"""

import csv
from pathlib import Path

from tracing.models.strategy_trace import (
    StrategyTrace
)


class StrategyTraceCsvExporter:
    """
    Exports strategy traces
    to CSV format.
    """

    @staticmethod
    def export(
            trace: StrategyTrace,
            output_file: str | Path
    ) -> None:
        """
        Exports a strategy trace.

        :param trace:
            Strategy trace to export.

        :param output_file:
            Output CSV file path.
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

        header = [
            "Ticker",
            "Strategy",

            "PeriodIndex",
            "Date",

            "Close",
            "RunningMax",
            "RunningAvg",

            "DrawdownMax",
            "DrawdownAvg",

            "Contribution",
            "AccumulatedContribution",

            "SharesBought",
            "AccumulatedShares",

            "PositionValue",

            "CashRemaining"
        ]

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

            for row in trace.rows:
                writer.writerow(
                    [
                        trace.ticker,
                        trace.strategy.name(),

                        row.period_index,
                        row.date,

                        row.close,
                        row.running_max,
                        row.running_avg,

                        row.drawdown_max,
                        row.drawdown_avg,

                        row.contribution,
                        row.accumulated_contribution,

                        row.shares_bought,
                        row.accumulated_shares,

                        row.position_value,

                        row.cash_remaining
                    ]
                )
