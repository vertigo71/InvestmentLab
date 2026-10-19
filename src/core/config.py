"""
Global project configuration.
"""

from datetime import datetime
from pathlib import Path
from typing import Final

# Project root directory.
PROJECT_ROOT: Final = (
    Path(__file__).resolve()
    .parent  # core
    .parent  # src
    .parent  # project
)

# Input data directory.
INPUT_FOLDER: Final = (
        PROJECT_ROOT / "inputs"
)

# Output directory.
OUTPUT_FOLDER: Final = (
        PROJECT_ROOT / "outputs"
)

# Default initial portfolio value.
INITIAL_CAPITAL: Final = 100000

# Annual interest rate earned by uninvested
# cash, e.g. 0.02 for a money market fund
# yielding 2% per year.
#
# Applied every period from the actual
# elapsed days. 0.0 means cash earns
# nothing.
CASH_ANNUAL_RATE: Final = 0.0

# Current export date.
GENERATED_ON: Final = (
    datetime.now().strftime(
        "%Y%m%d"
    )
)
