"""
Defines the base contract for all price
data sources.

A data source knows where its prices come
from (Yahoo, a CSV file...) and their data
frequency, so experiments only need to
choose one and call load().
"""

from abc import ABC
from abc import abstractmethod

from core.models.price_series import PriceSeries


class DataSource(ABC):
    """
    Base class for all price data sources.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Short, file-system safe name used
        in output file names.

        Examples:

            SP500TR
            SHILLER
        """

        pass

    @abstractmethod
    def load(
            self,
            start_date: str,
            end_date: str
    ) -> PriceSeries:
        """
        Loads the price series for a date
        range.

        :param start_date:
            First date to include, in
            YYYY-MM-DD format.

        :param end_date:
            End date (exclusive), in
            YYYY-MM-DD format.

        :return:
            Price series tagged with the
            source data frequency.
        """

        pass