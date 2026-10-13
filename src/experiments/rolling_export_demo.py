"""
Exports rolling window results to CSV.
"""

from experiments.config import (
    CSV_OUTPUT_FILE
)

from experiments.rolling_base import (
    RollingBase
)

from exporters.rolling_results_csv_exporter import (
    RollingResultsCsvExporter
)


def main():
    """
    Exports rolling window results.
    """

    results = (
        RollingBase.build_results()
    )

    RollingResultsCsvExporter.export(
        results=results,
        output_file=CSV_OUTPUT_FILE
    )

    print(
        f"CSV exported to:\n"
        f"{CSV_OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
