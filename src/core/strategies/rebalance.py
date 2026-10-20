"""
Fixed-allocation strategy with periodic
rebalancing.

A fixed fraction of the portfolio is kept in
shares and the rest in cash (e.g. a money
market fund earning cash_annual_rate). On each
rebalancing period, shares are bought or sold
to restore that fraction.
"""

from core.models.contribution_frequency import ContributionFrequency
from core.models.portfolio import PortfolioBase
from core.models.price_point import PricePoint
from core.strategies.strategy import Strategy


class Rebalance(Strategy):

    def __init__(
            self,
            equity_weight: float,
            frequency: ContributionFrequency,
            tolerance: float = 0.0
    ):
        """
        Creates a rebalancing strategy.

        :param equity_weight:
            Target fraction of the total value
            invested in shares, e.g. 0.70 for a
            70/30 portfolio.

        :param frequency:
            How often the portfolio is reviewed,
            e.g. SEMIANNUAL.

        :param tolerance:
            Maximum deviation of the share weight
            from the target before rebalancing,
            e.g. 0.05 rebalances a 70% target
            only below 65% or above 75%.

            0.0 always rebalances. 1.0 or more
            never rebalances after the initial
            allocation (buy and hold).

        :raises ValueError:
            If equity_weight is not in (0, 1] or
            tolerance is negative.
        """

        if not 0.0 < equity_weight <= 1.0:
            raise ValueError(
                f"Equity weight must be in (0, 1], "
                f"got {equity_weight}"
            )

        if tolerance < 0.0:
            raise ValueError(
                f"Tolerance must not be negative, "
                f"got {tolerance}"
            )

        self.equity_weight = equity_weight
        self._frequency = frequency
        self.tolerance = tolerance

    @property
    def frequency(self) -> ContributionFrequency:
        """
        Rebalancing frequency.
        """

        return self._frequency

    def propose_trade(
            self,
            point: PricePoint,
            contribution_amount: float,
            portfolio: PortfolioBase
    ) -> float:
        """
        Proposes the trade that brings the share
        weight back to the target.

        The proposed contribution amount is
        ignored.
        """

        price = point.close

        # The initial allocation is always made,
        # whatever the tolerance: the portfolio
        # starts fully in cash.
        if point.period_index != 0:

            deviation = abs(
                portfolio.equity_weight(price) -
                self.equity_weight
            )

            if deviation <= self.tolerance:
                return 0.0

        # the new position_value should be target_value
        target_value = (
                portfolio.total_value(price) *
                self.equity_weight
        )

        # Positive: buy shares.
        # Negative: sell shares.
        return (
                target_value -
                portfolio.position_value(price)
        )

    def name(self) -> str:
        """
        Returns the strategy name.

        Examples:

            REBALANCE_70%_SEMIANNUAL
            REBALANCE_70%_SEMIANNUAL_TOL5%
            HOLD_70%
        """

        weight = f"{self.equity_weight * 100:g}%"

        if self.tolerance >= 1.0:
            return f"HOLD_{weight}"

        tolerance = (
            f"_TOL{self.tolerance * 100:g}%"
            if self.tolerance > 0.0
            else ""
        )

        return (
            f"REBALANCE_"
            f"{weight}_"
            f"{self.frequency.name}"
            f"{tolerance}"
        )