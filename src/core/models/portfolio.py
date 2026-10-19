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

    def buy(self, amount: float, price: float) -> float:
        """
        Purchases shares.

        Args:
            amount:
                Amount of money requested
                to invest.

            price:
                Current asset price.

        Returns:
            Amount actually invested, which
            may be lower than requested if
            there is not enough cash.
        """

        amount = min(amount, self.cash_remaining)

        self.shares += amount / price
        self.cash_remaining -= amount

        return amount

    def earn_interest(
            self,
            annual_rate: float,
            days: int
    ) -> float:
        """
        Adds the interest earned by the
        uninvested cash over a number of
        days.

        The annual rate is compounded over
        the actual elapsed time:

            factor = (1 + annual_rate) ** (days / 365.25)

        Args:
            annual_rate:
                Annual interest rate, e.g.
                0.02 for 2%.

            days:
                Days elapsed since the
                previous period.

        Returns:
            Interest earned, added to
            cash_remaining.
        """

        factor = (
                (1 + annual_rate) **
                (days / 365.25)
        )

        interest = (
                self.cash_remaining *
                (factor - 1)
        )

        self.cash_remaining += interest

        return interest

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
