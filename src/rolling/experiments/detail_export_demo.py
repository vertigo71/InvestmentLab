"""
Exports rolling window results to CSV,
together with a copy of the experiment
YAML used to produce them.
"""

from core.settings import SETTINGS

from rolling.experiments.base import (
    RollingBase
)
from rolling.experiments.config import (
    CSV_OUTPUT_FILE
)
from rolling.exporters.rolling_results_csv_exporter import (
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

    # Saved after the CSV, so the folder
    # already exists.
    config_copy = SETTINGS.save_copy(
        CSV_OUTPUT_FILE
    )

    print(
        f"CSV exported to:\n"
        f"{CSV_OUTPUT_FILE}\n"
        f"Experiment settings saved to:\n"
        f"{config_copy}"
    )


if __name__ == "__main__":
    main()
