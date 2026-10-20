"""
Tracks portfolio state during a backtest.

PortfolioBase holds the cash and shares and the
values derived from them. Portfolio adds the
operations that change them, used only by the
simulator.
"""

from dataclasses import dataclass


@dataclass
class PortfolioBase:
    """
    Cash and shares of a portfolio, and the
    values derived from them.

    Strategies receive a PortfolioBase copy of
    the portfolio: they can read it, but have
    no buy() or sell(). Trades are executed by
    the simulator through Portfolio.

    Attributes:
        cash_remaining:
            Amount still available for investment.

        shares:
            Number of accumulated shares.
    """

    cash_remaining: float
    shares: float = 0.0

    def position_value(self, price: float) -> float:
        """
        Market value of the shares at a price.
        """

        return self.shares * price

    def total_value(self, price: float) -> float:
        """
        Shares plus cash at a price.
        """

        return (
                self.position_value(price) +
                self.cash_remaining
        )

    def equity_weight(self, price: float) -> float:
        """
        Fraction of the total value invested
        in shares, from 0.0 (all cash) to 1.0
        (fully invested).

        Example: 70,000 in shares and 30,000
        in cash -> 0.70.
        """

        return (
                self.position_value(price) /
                self.total_value(price)
        )


@dataclass
class Portfolio(PortfolioBase):
    """
    Portfolio that can trade and earn interest.
    Used by the simulator only.
    """

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

    def sell(self, amount: float, price: float) -> float:
        """
        Sells shares for a given amount of money.
        The proceeds are added to the cash.

        Args:
            amount:
                Amount of money requested from
                the sale.

            price:
                Current asset price.

        Returns:
            Amount actually received, which may
            be lower than requested if the
            position is worth less.
        """

        amount = min(
            amount,
            self.position_value(price)
        )

        self.shares -= amount / price
        self.cash_remaining += amount

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
