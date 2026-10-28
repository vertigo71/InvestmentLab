"""
Adaptive DCA strategy.

Investment amount increases when the asset
falls below a reference price.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.portfolio import PortfolioBase
from core.models.price_point import PricePoint
from core.models.reference_price import ReferencePrice
from core.models.simulation_context import SimulationContext
from core.strategies.descriptions import deployment_text
from core.strategies.strategy import Strategy


class DrawdownDCA(Strategy):

    def __init__(
            self,
            levels: list[tuple[float, float]],
            frequency: ContributionFrequency,
            reference_price: ReferencePrice,
            base_multiplier: float = 1.0,
            deploy_years: float | None = None,
            take_profit: float | None = None
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

        :param deploy_years:
            Years over which the capital is
            invested at the base pace, then held.
            None spreads it over the whole window.
            Drawdown multipliers invest faster, so
            the capital may run out earlier.

        :param take_profit:
            Gain over the cost of the shares
            that triggers a sale, e.g. 0.20
            for 20%. When it is reached at a
            contribution, the gain is sold
            instead of buying, and returns to
            cash to be invested again at the
            strategy pace. None never sells.
            See PortfolioBase.cost_basis.

        :raises ValueError:
            If the levels, the base multiplier,
            the deploy years or the take profit
            are not valid.

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

        if deploy_years is not None and deploy_years <= 0:
            raise ValueError(
                f"Deploy years must be positive, "
                f"got {deploy_years}"
            )

        if take_profit is not None and take_profit <= 0:
            raise ValueError(
                f"Take profit must be positive, "
                f"got {take_profit}"
            )

        self.levels = levels
        self._frequency = frequency
        self.reference_price = reference_price
        self.base_multiplier = base_multiplier
        self.deploy_years = deploy_years
        self.take_profit = take_profit

    @property
    def frequency(self) -> ContributionFrequency:
        """
        Contribution frequency.
        """

        return self._frequency

    def propose_trade(
            self,
            point: PricePoint,
            context: SimulationContext,
            portfolio: PortfolioBase
    ) -> float:
        """
        Proposes the base amount scaled by the
        multiplier of the deepest drawdown
        level reached.

        With take profit, if the gain of the
        shares reaches the threshold, proposes
        selling that gain instead (negative
        amount).
        """

        # Take profit: sell the gain instead of
        # buying. Compared as gain >= rate * cost
        # rather than gain / cost >= rate, so an
        # empty position (cost 0) needs no
        # division. Without shares there is no
        # gain to sell, so the strategy buys.
        if (
                self.take_profit is not None and
                portfolio.cost_basis > 0
        ):
            gain = portfolio.unrealized_gain(point.close)

            if gain >= self.take_profit * portfolio.cost_basis:
                return -gain

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

        amount = context.base_contribution(
            frequency=self.frequency,
            deploy_years=self.deploy_years
        )

        # Never invest more cash
        # than available.
        return min(
            amount * multiplier,
            portfolio.cash_remaining
        )

    def name(self) -> str:
        """
        Returns the strategy name.

        Optional parts are only shown when they
        differ from the default, so existing
        strategy names remain unchanged.

        Example:

            DDCA_AVG_BIWEEKLY_3Y_(10%;2)_(20%;3)_TP20%
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

        deploy = (
            f"{self.deploy_years:g}Y"
            if self.deploy_years is not None
            else ""
        )

        base = (
            f"BASE{self.base_multiplier:g}"
            if self.base_multiplier != 1.0
            else ""
        )

        take_profit = (
            f"TP{self.take_profit:.0%}"
            if self.take_profit is not None
            else ""
        )

        parts = [
            "DDCA",
            reference,
            self.frequency.name,
            deploy,
            base,
            levels,
            take_profit
        ]

        # Empty parts are skipped, so there is
        # never a double or trailing "_".
        return "_".join(
            part
            for part in parts
            if part
        )

    def description(self) -> str:
        """
        Returns the strategy description.

        Example:

            Invests in monthly contributions over
            3 years, then holds. Each contribution
            is multiplied by 2 when the price is at
            least 10% below its running maximum, 3
            at 20%, 4 at 30%, 5 at 40%. When the
            shares are worth at least 20% more than
            they cost, the gain is sold instead and
            invested again later from cash.
        """

        text = (
            f"Invests in "
            f"{self.frequency.name.lower()} "
            f"contributions "
            f"{deployment_text(self.deploy_years)}."
        )

        if self.levels:

            reference = (
                "running average"
                if self.reference_price ==
                   ReferencePrice.RUNNING_AVG
                else "running maximum"
            )

            # First level in full, the rest abbreviated:
            # "2 when the price is at least 10% below
            # ..., 3 at 20%, 4 at 30%".
            steps = [
                f"{multiplier:g} at {self._distance(threshold)}"
                for threshold, multiplier
                in self.levels[1:]
            ]

            first_threshold, first_multiplier = self.levels[0]

            text += (
                f" Each contribution is multiplied by "
                f"{first_multiplier:g} when the price is "
                f"at least {self._distance(first_threshold)} "
                f"its {reference}"
            )

            if steps:
                text += f", {', '.join(steps)}"

            text += "."

            if self.base_multiplier != 1.0:
                text += (
                    f" Otherwise it is multiplied by "
                    f"{self.base_multiplier:g}."
                )

        if self.take_profit is not None:
            text += (
                f" When the shares are worth at least "
                f"{self.take_profit * 100:g}% more than "
                f"they cost, the gain is sold instead "
                f"and invested again later from cash."
            )

        return text

    @staticmethod
    def _distance(threshold: float) -> str:
        """
        Describes a drawdown threshold relative to
        the reference price:

            0.10  -> "10% below"
            -0.05 -> "5% above"
            0.0   -> "0% below"
        """

        side = "above" if threshold < 0 else "below"

        return f"{abs(threshold) * 100:g}% {side}"
