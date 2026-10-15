"""
Tracks portfolio state during a backtest.
"""

from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    Stores portfolio information.

    Attributes:
        cash_remaining:
            Amount still available for investment.

        shares:
            Number of accumulated shares.
    """

    cash_remaining: float
    shares: float = 0.0

    def buy(self, amount: float, price: float) -> None:
        """
        Purchases shares.

        Args:
            amount:
                Amount of money to invest.

            price:
                Current asset price.
        """

        amount = min(amount, self.cash_remaining)

        self.shares += amount / price
        self.cash_remaining -= amount

    def value(self, current_price: float) -> float:
        """
        Returns the invested asset value
        at the specified market price.
        """

        return self.shares * current_price
