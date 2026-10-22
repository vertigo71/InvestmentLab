"""
Exports aggregated rolling analysis to CSV,
together with a copy of the experiment
YAML used to produce it.
"""

from core.settings import SETTINGS

from rolling.analysis.rolling_results_analyzer import (
    RollingResultsAnalyzer
)
from rolling.experiments.base import (
    RollingBase
)
from rolling.experiments.config import (
    ANALYSIS_CSV_OUTPUT_FILE
)
from rolling.exporters.rolling_analysis_csv_exporter import (
    RollingAnalysisCsvExporter
)


def main():
    """
    Builds the rolling analysis and
    exports all generated metrics
    to CSV format.
    """

    results = (
        RollingBase.build_results()
    )

    # Generate the aggregate
    # rolling analysis metrics.
    analysis = (
        RollingResultsAnalyzer.build_analysis(
            results,
            target_annual_return=
            SETTINGS.rolling.target_annual_return
        )
    )

    # Export all generated
    # analysis metrics.
    RollingAnalysisCsvExporter.export(
        analysis=analysis,
        output_file=
        ANALYSIS_CSV_OUTPUT_FILE
    )

    # Saved after the CSV, so the folder
    # already exists.
    config_copy = SETTINGS.save_copy(
        ANALYSIS_CSV_OUTPUT_FILE
    )

    print(
        f"Analysis CSV exported to:\n"
        f"{ANALYSIS_CSV_OUTPUT_FILE}\n"
        f"Experiment settings saved to:\n"
        f"{config_copy}"
    )


if __name__ == "__main__":
    main()