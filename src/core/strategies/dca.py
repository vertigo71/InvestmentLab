"""
Traditional Dollar Cost Averaging strategy.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.portfolio import PortfolioBase
from core.models.price_point import PricePoint
from core.models.simulation_context import SimulationContext
from core.strategies.descriptions import deployment_text
from core.strategies.strategy import Strategy


class DCA(Strategy):

    def __init__(
            self,
            frequency: ContributionFrequency,
            deploy_years: float | None = None
    ):
        """
        Creates a DCA strategy.

        :param frequency:
            Contribution frequency.

            Examples:

                WEEKLY

                BIWEEKLY

                MONTHLY

        :param deploy_years:
            Years over which the capital is
            invested, then held. None spreads
            it over the whole window.

        :raises ValueError:
            If deploy_years is not positive.
        """

        if deploy_years is not None and deploy_years <= 0:
            raise ValueError(
                f"Deploy years must be positive, "
                f"got {deploy_years}"
            )

        self._frequency = frequency
        self.deploy_years = deploy_years

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
        Proposes investing the 'base contribution'
        on every contribution period, until the
        cash runs out. The position is then held.
        """

        amount = context.base_contribution(
            frequency=self.frequency,
            deploy_years=self.deploy_years
        )

        # Never invest more cash
        # than available.
        return min(
            amount,
            portfolio.cash_remaining
        )

    def name(self) -> str:
        """
        Returns the strategy name.

        Examples:

            DCA_MONTHLY       (whole window)
            DCA_MONTHLY_3Y    (deployed in 3 years)
        """

        deploy = (
            f"_{self.deploy_years:g}Y"
            if self.deploy_years is not None
            else ""
        )

        return (
            f"DCA_"
            f"{self.frequency.name}"
            f"{deploy}"
        )

    def description(self) -> str:
        """
        Returns the strategy description.

        Example:

            Invests the initial capital in equal
            monthly contributions over 3 years,
            then holds.
        """

        return (
            f"Invests the initial capital in equal "
            f"{self.frequency.name.lower()} "
            f"contributions "
            f"{deployment_text(self.deploy_years)}."
        )


