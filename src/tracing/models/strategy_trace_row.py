"""
Represents a single strategy
execution period.

A StrategyTraceRow captures all
relevant information produced
during one simulation step and
can be used for debugging,
validation and CSV exports.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class StrategyTraceRow:
    """
    Stores the complete state of a
    strategy execution for a single
    investment period.

    :param period_index:
        Sequential period number.

    :param date:
        Market date associated with
        the period.

    :param close:
        Closing market price.

    :param running_max:
        Highest market price observed
        up to and including this period.

    :param running_avg:
        Average market price observed
        up to and including this period.

    :param drawdown_max:
        Percentage decline relative
        to the running maximum.

    :param drawdown_avg:
        Percentage decline relative
        to the running average.

    :param contribution:
        Amount invested during the
        current period.

    :param accumulated_contribution:
        Total capital invested up to
        and including this period.

    :param shares_bought:
        Number of shares purchased
        during the current period.

    :param accumulated_shares:
        Total accumulated shares
        owned after the purchase.

    :param position_value:
        Market value of the accumulated
        shares at the current market
        price.

    :param cash_remaining:
        Uninvested cash remaining
        after the purchase.
    """

    # Sequential period number.
    period_index: int

    # Market date.
    date: date

    # Closing market price.
    close: float

    # Highest observed market price.
    running_max: float

    # Average observed market price.
    running_avg: float

    # Drawdown from the running maximum.
    drawdown_max: float

    # Drawdown from the running average.
    drawdown_avg: float

    # Amount invested during
    # the current period.
    contribution: float

    # Total invested capital.
    accumulated_contribution: float

    # Shares purchased during
    # the current period.
    shares_bought: float

    # Total accumulated shares.
    accumulated_shares: float

    # Current market value of
    # accumulated shares.
    position_value: float

    # Remaining uninvested cash.
    cash_remaining: float
