"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below a reference price.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.reference_price import ReferencePrice

from core.strategies.strategy import Strategy


class DrawdownDCA(Strategy):

    def __init__(
            self,
            levels: list[tuple[float, float]],
            frequency: ContributionFrequency,
            reference_price: ReferencePrice
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

        :param reference_price:
            Price reference used to
            calculate the current drawdown.

            Examples:

                RUNNING_MAX

                RUNNING_AVG
        """

        self.levels = levels
        self.frequency = frequency
        self.reference_price = reference_price

    def contribution(
            self,
            weekly_contribution: float,
            period_index: int,
            price: float,
            running_max: float,
            running_avg: float,
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

        :param running_max:
            Maximum asset price observed so far.

        :param running_avg:
            Average price observed from
            the beginning of the simulation
            up to and including this period.

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

        # Select the reference price
        # used to calculate drawdown.
        reference_price = running_max

        if (
                self.reference_price ==
                ReferencePrice.RUNNING_AVG
        ):
            reference_price = running_avg

        # Calculate current drawdown
        # from the selected reference.
        drawdown = (
                1.0 -
                price / reference_price
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
            f"({threshold:.0%};{multiplier})"
            for threshold, multiplier
            in self.levels
        )

        reference = (
            "MAX"
            if self.reference_price ==
               ReferencePrice.RUNNING_MAX
            else "AVG"
        )

        return (
            f"DDCA_"
            f"{reference}_"
            f"{self.frequency.name}_"
            f"{levels}"
        )
