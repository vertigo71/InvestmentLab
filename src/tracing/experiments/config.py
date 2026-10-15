"""
Configuration used by
tracing experiments.
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
# ^GSPC
# 0P00000RQC.F
#
TICKER: Final = "URTH"

# Historical data range.
START_DATE: Final = "2016-01-01"

END_DATE: Final = "2019-01-01"

# Trace period length.
WINDOW_YEARS: Final = 3

# Strategy name used in exports.
STRATEGY_NAME: Final = (
    "DCA_BIWEEKLY"
)

# File-system safe ticker symbol.
SAFE_TICKER: Final = (
    TICKER.replace("^", "")
)

# Trace CSV export file.
CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"tracing_"
        f"{WINDOW_YEARS}y_"
        f"{SAFE_TICKER}_"
        f"{STRATEGY_NAME}.csv"
)
