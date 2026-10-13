"""
Creates the strategies used in
backtesting experiments.
"""

from models.contribution_frequency import ContributionFrequency

from strategies.all_in import AllIn
from strategies.dca import DCA
from strategies.drawdown_dca import DrawdownDCA
from strategies.strategy import Strategy


class StrategyFactory:
    """
    Builds the collection of strategies
    to be compared in experiments.
    """

    @staticmethod
    def create() -> list[Strategy]:
        """
        Creates the strategy set used
        for performance comparisons.

        :return:
            Configured strategies.
        """

        return [

            AllIn(),

            DCA(
                frequency=ContributionFrequency.WEEKLY
            ),

            DrawdownDCA(
                levels=[
                    (0.01, 2),
                    (0.02, 3),
                    (0.03, 4)
                ],
                frequency=ContributionFrequency.WEEKLY
            ),

            DrawdownDCA(
                levels=[
                    (0.0, 0.5),
                    (0.01, 2),
                    (0.02, 4),
                    (0.03, 8)
                ],
                frequency=ContributionFrequency.MONTHLY
            )

        ]
