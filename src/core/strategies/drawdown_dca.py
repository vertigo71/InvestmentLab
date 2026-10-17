"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below a reference price.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.price_point import PricePoint
from core.models.reference_price import ReferencePrice
from core.strategies.strategy import Strategy


class DrawdownDCA(Strategy):

    def __init__(
            self,
            levels: list[tuple[float, float]],
            frequency: ContributionFrequency,
            reference_price: ReferencePrice,
            base_multiplier: float = 1.0
    ):
        """
        Creates a drawdown-based DCA strategy.

        :param levels:
            Drawdown thresholds and
            associated multipliers.

            Thresholds must be strictly
            increasing and lower than 1.
            Negative thresholds are allowed:
            with RUNNING_AVG the drawdown is
            negative when the price is above
            the average.

            Example:

                [
                    (0.10, 2),
                    (0.20, 3),
                    (0.30, 4)
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

        :param base_multiplier:
            Multiplier applied when the
            drawdown is below the first
            threshold, i.e. when no level
            is reached.

            With RUNNING_AVG this includes
            periods where the price is
            above the average.

        :raises ValueError:
            If the levels or the base
            multiplier are not valid.
        """

        # Thresholds must be strictly increasing.
        # The contribution loop keeps the
        # multiplier of the last threshold
        # exceeded, so unsorted levels would
        # silently select the wrong multiplier.
        thresholds = [
            threshold
            for threshold, _ in levels
        ]

        if thresholds != sorted(set(thresholds)):
            raise ValueError(
                f"Drawdown thresholds must be "
                f"strictly increasing, got "
                f"{thresholds}"
            )

        for threshold, multiplier in levels:

            # Drawdown is 1 - price / reference,
            # so it can never reach 1 (100%).
            # Negative thresholds are valid:
            # with RUNNING_AVG the drawdown is
            # negative when the price is above
            # the average.
            if threshold >= 1.0:
                raise ValueError(
                    f"Drawdown threshold must be "
                    f"lower than 1, got "
                    f"{threshold}"
                )

            if multiplier <= 0:
                raise ValueError(
                    f"Multiplier must be positive, "
                    f"got {multiplier}"
                )

        if base_multiplier <= 0:
            raise ValueError(
                f"Base multiplier must be "
                f"positive, got "
                f"{base_multiplier}"
            )

        self.levels = levels
        self._frequency = frequency
        self.reference_price = reference_price
        self.base_multiplier = base_multiplier

    @property
    def frequency(self) -> ContributionFrequency:
        """
        Contribution frequency.
        """

        return self._frequency

    def contribution(
            self,
            point: PricePoint,
            contribution_amount: float,
            cash_remaining: float
    ) -> float:
        """
        Scales the proposed amount by the
        multiplier of the deepest drawdown
        level reached.
        """

        # Select the reference price
        # used to calculate drawdown.
        reference_price = (
            point.running_avg
            if self.reference_price ==
               ReferencePrice.RUNNING_AVG
            else point.running_max
        )

        # Calculate current drawdown
        # from the selected reference.
        drawdown = (
                1.0 -
                point.close / reference_price
        )

        multiplier: float = self.base_multiplier

        # Determine the contribution
        # multiplier.
        for threshold, value in self.levels:

            if drawdown >= threshold:
                multiplier = value

        # Never invest more cash
        # than available.
        return min(
            contribution_amount * multiplier,
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

        # Only shown when it differs from
        # the default, so existing strategy
        # names remain unchanged.
        base = (
            f"BASE{self.base_multiplier:g}_"
            if self.base_multiplier != 1.0
            else ""
        )

        return (
            f"DDCA_"
            f"{reference}_"
            f"{self.frequency.name}_"
            f"{base}"
            f"{levels}"
        )
