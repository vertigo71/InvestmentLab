"""
CSV file price data source.
"""

from dataclasses import dataclass
from pathlib import Path

from core.models.data_frequency import DataFrequency
from core.models.price_series import PriceSeries
from core.providers.csv_loader import CsvLoader
from core.providers.data_source import DataSource


@dataclass(frozen=True)
class CsvSource(DataSource):
    """
    Reads prices from a local CSV file with
    date and close columns (see CsvLoader).

    :param label:
        Short, file-system safe name used in
        output file names, e.g. SHILLER.

    :param path:
        CSV file to read.

    :param frequency:
        Frequency of the rows in the file.
        It cannot be inferred from the file,
        so it has no default.
    """

    label: str
    path: Path
    frequency: DataFrequency

    @property
    def name(self) -> str:
        """
        Name given when the source was
        created.
        """

        return self.label

    def load(
            self,
            start_date: str,
            end_date: str
    ) -> PriceSeries:
        """
        Reads the price series for a date
        range.
        """

        return CsvLoader.load(
            path=self.path,
            frequency=self.frequency,
            start_date=start_date,
            end_date=end_date
        )