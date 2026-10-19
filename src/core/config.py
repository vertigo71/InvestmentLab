"""
Global project configuration.

Fixed project paths and the export date.
Experiment settings (capital, cash interest,
data source, strategies...) are defined in
the YAML files of the configs folder and
loaded by core/settings.py.
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

# Experiment configuration directory.
# Contains one YAML file per experiment and
# active_yaml.txt with the experiment to run.
CONFIG_FOLDER: Final = (
        PROJECT_ROOT / "configs"
)

# Current export date.
GENERATED_ON: Final = (
    datetime.now().strftime(
        "%Y%m%d"
    )
)
