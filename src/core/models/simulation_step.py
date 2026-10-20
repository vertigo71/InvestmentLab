"""
Represents the portfolio state after
a single simulation period.
"""

from dataclasses import dataclass

from core.models.price_point import PricePoint


@dataclass(frozen=True)  # immutable objects
class SimulationStep:
    """
    Stores the outcome of one simulation
    period, after the trade has been
    executed.

    :param point:
        Market data for the period.

    :param interest:
        Interest earned by the uninvested
        cash since the previous period,
        before the purchase.

    :param contribution:
        Amount actually traded during the
        period, after the cash or position
        limits:

            positive  invested (shares bought)
            negative  received (shares sold)
            0.0       no trade

    :param shares_bought:
        Shares traded during the period:
        positive when buying, negative when
        selling.

    :param accumulated_shares:
        Total shares owned after the trade.

    :param cash_remaining:
        Uninvested cash after the purchase.
    """

    point: PricePoint
    interest: float
    contribution: float
    shares_bought: float
    accumulated_shares: float
    cash_remaining: float

    @property
    def position_value(self) -> float:
        """
        Market value of the accumulated
        shares at the period close.
        """

        return (
                self.accumulated_shares *
                self.point.close
        )

    @property
    def total_value(self) -> float:  # property -> getter
        """
        Invested position plus uninvested
        cash at the period close.
        """

        return (
                self.position_value +
                self.cash_remaining
        )
