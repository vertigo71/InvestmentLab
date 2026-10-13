"""
Shared configuration used by
rolling-window experiments.
"""

from pathlib import Path
from typing import Final

# Project root directory.
PROJECT_ROOT: Final = (
    Path(__file__).resolve()
    .parent.parent.parent
)

# Output directory.
OUTPUT_FOLDER: Final = (
        PROJECT_ROOT / "outputs"
)

# Initial portfolio value used by
# all experiments.
INITIAL_CAPITAL: Final = 100000

# Investment horizon used by the
# rolling-window analysis.
WINDOW_YEARS: Final = 3

# Available datasets:
#
# URTH  -> 2012-
# VT    -> 2008-
# ^GSPC -> 1990-
TICKER: Final = "^GSPC"

# Historical data download range.
START_DATE: Final = "1990-01-01"

END_DATE: Final = "2028-01-01"

# File-system safe ticker symbol.
SAFE_TICKER: Final = (
    TICKER.replace("^", "")
)

# CSV export file.
CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"rolling_results_"
        f"{WINDOW_YEARS}y_"
        f"{SAFE_TICKER}.csv"
)
