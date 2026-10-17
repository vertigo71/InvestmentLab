"""
Configuration used by
rolling-window experiments.
"""

from typing import Final

from core.config import (
    GENERATED_ON,
    OUTPUT_FOLDER
)

# Available datasets:
#
# URTH
# VT
# ^GSPC 1990 -
# 0P00000RQC.F
# "^SP500TR" 1990 -
# Nikkei 225 (^N225) 1990 - no dividends
#
TICKER: Final = "^N225"

# Historical data range.
START_DATE: Final = "1987-01-01"
END_DATE: Final = "1997-01-01"

# Rolling window length.
WINDOW_YEARS: Final = 3

# File-system safe ticker symbol.
SAFE_TICKER: Final = (
    TICKER.replace("^", "")
)

#
# modify strategies in strategy_factory file
#

# Rolling results CSV export file.
CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_results_"
        f"{WINDOW_YEARS}y_"
        f"{SAFE_TICKER}.csv"
)

# Rolling analysis CSV export file.
ANALYSIS_CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_analysis_"
        f"{WINDOW_YEARS}y_"
        f"{SAFE_TICKER}.csv"
)
