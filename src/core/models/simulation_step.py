"""
Represents the portfolio state after
a single simulation period.
"""

from dataclasses import dataclass

from core.models.price_point import PricePoint


@dataclass(frozen=True)
class SimulationStep:
    """
    Stores the outcome of one simulation
    period, after the purchase has been
    executed.

    :param point:
        Market data for the period.

    :param contribution:
        Amount actually invested during
        the period.

    :param shares_bought:
        Shares purchased during the period.

    :param accumulated_shares:
        Total shares owned after the
        purchase.

    :param cash_remaining:
        Uninvested cash after the purchase.
    """

    point: PricePoint
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
