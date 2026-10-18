"""
Loads historical prices from a CSV file.
"""

import csv
import math
from datetime import date
from pathlib import Path

from core.models.data_frequency import DataFrequency
from core.models.price_series import PriceSeries
from core.transformers.price_point_builder import PricePointBuilder


class CsvLoader:
    """
    Loads a price series from a CSV file with
    two columns:

        date,close
        2016-01-01,65.15
        2016-01-08,65.02

    Dates use the ISO format (YYYY-MM-DD).
    The data frequency cannot be inferred
    from the file, so it must be provided.
    """

    @staticmethod
    def load(
            path: str | Path,
            frequency: DataFrequency,
            start_date: str | None = None,
            end_date: str | None = None
    ) -> PriceSeries:
        """
        Loads a price series.

        :param path:
            CSV file to read.

        :param frequency:
            Frequency of the rows in the file.

        :param start_date:
            Optional first date to include,
            in YYYY-MM-DD format.

        :param end_date:
            Optional end date (exclusive),
            in YYYY-MM-DD format, as in
            YahooLoader.

        :return:
            Price series tagged with the
            given frequency.

        :raises ValueError:
            If the file is empty, a price is
            missing or not positive, or dates
            are not strictly increasing.
        """

        start : date | None = (
            date.fromisoformat(start_date)
            if start_date
            else None
        )

        end : date | None = (
            date.fromisoformat(end_date)
            if end_date
            else None
        )

        observations: list[tuple[date, float]] = []

        with Path(path).open(
                newline="",
                encoding="utf-8"
        ) as csv_file:

            for row in csv.DictReader(csv_file):
                row_date = date.fromisoformat(
                    row["date"]
                )

                if start and row_date < start:
                    continue

                if end and row_date >= end:
                    continue

                close = float(row["close"])

                if not math.isfinite(close) or close <= 0:
                    raise ValueError(
                        f"Invalid close price "
                        f"{row['close']!r} on "
                        f"{row_date}"
                    )

                observations.append(
                    (row_date, close)
                )

        if not observations:
            raise ValueError(
                f"No data in '{path}' for the "
                f"requested date range"
            )

        if any(
                current[0] <= previous[0]
                for previous, current
                in zip(observations, observations[1:])
        ):
            raise ValueError(
                f"Dates in '{path}' are not "
                f"strictly increasing"
            )

        return PriceSeries(
            frequency=frequency,
            points=PricePointBuilder.build(
                observations
            )
        )
