"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below previous highs.
"""

from models.contribution_frequency import ContributionFrequency
from strategies.strategy import Strategy


class DrawdownDCA(Strategy):

    def __init__(
            self,
            levels: list[tuple[float, float]],
            frequency: ContributionFrequency
    ):
        """
        Creates a drawdown-based DCA strategy.

        :param levels:
            Drawdown thresholds and
            associated multipliers.

            Example:

                [
                    (0.01, 2),
                    (0.02, 4),
                    (0.03, 8)
                ]

        :param frequency:
            Contribution frequency.

            Examples:

                WEEKLY

                BIWEEKLY

                MONTHLY
        """

        self.levels = levels
        self.frequency = frequency

    def contribution(
            self,
            weekly_contribution: float,
            period_index: int,
            price: float,
            max_price: float,
            cash_remaining: float
    ) -> float:
        """
        Calculates the contribution amount.

        :param weekly_contribution:
            Base weekly contribution amount
            proposed by the engine.

        :param period_index:
            Sequential index of the current period.

        :param price:
            Current asset price.

        :param max_price:
            Maximum asset price observed so far.

        :param cash_remaining:
            Available uninvested capital.

        :return:
            Amount to invest during
            the current period.
        """

        # Skip periods that are not
        # contribution periods.
        if (
                period_index %
                self.frequency.value
                != 0
        ):
            return 0.0

        # Calculate current drawdown
        # from the historical high.
        drawdown = (
                1.0 -
                price / max_price
        )

        multiplier: float = 1.0

        # Determine the contribution
        # multiplier.
        for threshold, value in self.levels:

            if drawdown >= threshold:
                multiplier = value

        # Convert the weekly contribution
        # into a contribution matching the
        # configured frequency.
        amount = (
                weekly_contribution *
                self.frequency.value *
                multiplier
        )

        # Never invest more cash
        # than available.
        return min(
            amount,
            cash_remaining
        )

    def name(self) -> str:
        """
        Returns the strategy name.
        """

        levels = "_".join(
            f"({threshold:.0%},{multiplier})"
            for threshold, multiplier
            in self.levels
        )

        return (
            f"DDCA_{self.frequency.name}_"
            f"{levels}"
        )
