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

# Output directory.
OUTPUT_FOLDER: Final = (
        PROJECT_ROOT / "outputs"
)

# Default initial portfolio value.
INITIAL_CAPITAL: Final = 100000

# Current export date.
GENERATED_ON: Final = (
    datetime.now().strftime(
        "%Y%m%d"
    )
)
