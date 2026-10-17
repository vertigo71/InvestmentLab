"""
Represents the portfolio state after
a single simulation period.
"""

from dataclasses import dataclass

from core.models.price_point import PricePoint


@dataclass(frozen=True)
class SimulationStep:
    """
    Portfolio state after processing
    one price point.

    :param point:
        Market data for the period.

    :param contribution:
        Amount actually invested
        during the period.

    :param accumulated_contribution:
        Total capital invested up to
        and including this period.

    :param shares_bought:
        Shares purchased during
        the period.

    :param shares:
        Total accumulated shares.

    :param position_value:
        Market value of the accumulated
        shares at the period close.

    :param cash_remaining:
        Uninvested cash after
        the purchase.

    :param total_value:
        Position value plus
        remaining cash.
    """

    point: PricePoint
    contribution: float
    accumulated_contribution: float
    shares_bought: float
    shares: float
    position_value: float
    cash_remaining: float
    total_value: float
