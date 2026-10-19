"""
Output files of rolling-window experiments.

All experiment settings (data source, dates,
window length, strategies) are defined in the
active experiment YAML file. See
configs/config_help.txt.
"""

from typing import Final

from core.config import (
    GENERATED_ON,
    OUTPUT_FOLDER
)
from core.file_utils import next_free_path
from core.settings import SETTINGS

# Output folder of the active experiment:
# outputs/<experiment name>/, e.g.
# outputs/sp500_weekly/. Created by the
# exporters if it does not exist.
EXPERIMENT_OUTPUT_FOLDER: Final = (
        OUTPUT_FOLDER /
        SETTINGS.experiment
)

# Rolling results CSV export file.
# Never overwrites a previous export: if the
# file exists, (1), (2)... is added.
CSV_OUTPUT_FILE: Final = next_free_path(
    EXPERIMENT_OUTPUT_FOLDER /
    f"{GENERATED_ON}_"
    f"rolling_results_"
    f"{SETTINGS.rolling.window_years}y.csv"
)

# Rolling analysis CSV export file.
# Never overwrites a previous export: if the
# file exists, (1), (2)... is added.
ANALYSIS_CSV_OUTPUT_FILE: Final = next_free_path(
    EXPERIMENT_OUTPUT_FOLDER /
    f"{GENERATED_ON}_"
    f"rolling_analysis_"
    f"{SETTINGS.rolling.window_years}y.csv"
)
