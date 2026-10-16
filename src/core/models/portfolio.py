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

    def buy(self,
            amount: float,
            price: float
            ) -> None:
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

    def position_value(self,
                       current_price: float
                       ) -> float:
        """
        Returns the market value of the
        accumulated shares only.
        """

        return self.shares * current_price

    def total_value(self,
                    current_price: float
                    ) -> float:
        """
        Returns the total portfolio value:
        invested position plus uninvested cash.
        """

        return (
                self.position_value(current_price) +
                self.cash_remaining
        )
