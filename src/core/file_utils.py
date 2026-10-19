"""
File system helpers.
"""

from pathlib import Path


def next_free_path(path: Path) -> Path:
    """
    Returns the path itself if no file exists
    there, otherwise the first free variant
    numbered like Windows copies:

        report.csv
        report (1).csv
        report (2).csv

    Used so that exports never overwrite
    previous results.

    :param path:
        Desired file path.

    :return:
        A path where no file exists yet.
    """

    if not path.exists():
        return path

    counter = 1

    while True:
        candidate = path.with_name(
            f"{path.stem} ({counter}){path.suffix}"
        )

        if not candidate.exists():
            return candidate

        counter += 1

