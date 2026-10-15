"""
Creates the strategies used in
backtesting experiments.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.reference_price import ReferencePrice

from core.strategies.all_in import AllIn
from core.strategies.dca import DCA
from core.strategies.drawdown_dca import DrawdownDCA
from core.strategies.strategy import Strategy


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
                frequency=ContributionFrequency.BIWEEKLY
            ),

            DCA(
                frequency=ContributionFrequency.MONTHLY
            ),

            DrawdownDCA(
                levels=[
                    (0.1, 2),
                    (0.2, 3),
                    (0.3, 4),
                    (0.4, 5),
                ],
                frequency=ContributionFrequency.BIWEEKLY,
                reference_price=ReferencePrice.RUNNING_MAX
            ),

            DrawdownDCA(
                levels=[
                    (0.1, 2),
                    (0.2, 3),
                    (0.3, 4),
                    (0.4, 5),
                ],
                frequency=ContributionFrequency.MONTHLY,
                reference_price=ReferencePrice.RUNNING_MAX
            ),

            DrawdownDCA(
                levels=[
                    (0.1, 2),
                    (0.2, 3),
                    (0.3, 4),
                    (0.4, 5),
                ],
                frequency=ContributionFrequency.BIWEEKLY,
                reference_price=ReferencePrice.RUNNING_AVG
            ),

            DrawdownDCA(
                levels=[
                    (0.1, 2),
                    (0.2, 3),
                    (0.3, 4),
                    (0.4, 5),
                ],
                frequency=ContributionFrequency.MONTHLY,
                reference_price=ReferencePrice.RUNNING_AVG
            ),

        ]
