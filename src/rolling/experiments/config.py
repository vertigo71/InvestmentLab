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
from core.settings import SETTINGS

# Rolling results CSV export file.
CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_results_"
        f"{SETTINGS.rolling.window_years}y_"
        f"{SETTINGS.rolling.data_source.name}.csv"
)

# Rolling analysis CSV export file.
ANALYSIS_CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_analysis_"
        f"{SETTINGS.rolling.window_years}y_"
        f"{SETTINGS.rolling.data_source.name}.csv"
)