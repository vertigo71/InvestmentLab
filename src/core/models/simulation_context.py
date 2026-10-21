"""
Data about a simulation window, passed to
strategies so they can compute their own
amounts.
"""

from dataclasses import dataclass
from math import floor

from core.models.contribution_frequency import ContributionFrequency
from core.models.data_frequency import DataFrequency


@dataclass(frozen=True)
class SimulationContext:
    """
    Fixed data of one simulation window,
    created by the simulator before the
    first period.

    :param initial_capital:
        Capital available at the start of
        the window.

    :param window_rows:
        Number of data rows in the window.

    :param data_frequency:
        Time between two data rows.
    """

    initial_capital: float
    window_rows: int
    data_frequency: DataFrequency

    def base_contribution(
            self,
            frequency: ContributionFrequency,
            deploy_years: float | None
    ) -> float:
        """
        Returns the base amount of each
        contribution, before any adjustment by
        the strategy (e.g. a drawdown multiplier).

        The initial capital is spread over the
        data rows of the deployment time, and
        multiplied by the rows between
        contributions. Example with 100,000,
        weekly data, MONTHLY contributions and
        deploy_years=3:

            deployment rows   3 * 52 = 156
            amount per row    100,000 / 156 = 641
            per contribution  641 * 4 = 2,564

        Without deploy_years, the capital is
        spread over the whole window
        (window_rows - 1).

        If deploy_years is longer than the
        window, part of the capital is still in
        cash at the end of the window.

        :param frequency:
            Contribution frequency of the
            strategy.

        :param deploy_years:
            Deployment time of the capital, in
            years. None means the whole window.

        :return:
            Base amount of each contribution.
        """

        if deploy_years is None:
            # Whole window. One row is subtracted
            # so that rounding never leaves the
            # capital short of the last periods.
            deploy_rows = self.window_rows - 1
        else:
            deploy_rows = max(
                1,
                round(
                    deploy_years *
                    self.data_frequency.periods_per_year()
                )
            )

        # Whole currency units per data row.
        amount_per_row = floor(
            self.initial_capital /
            deploy_rows
        )

        return (
                amount_per_row *
                frequency.periods(self.data_frequency)
        )