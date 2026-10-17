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

# File-system safe ticker symbol.
SAFE_TICKER: Final = (
    TICKER.replace("^", "")
)

