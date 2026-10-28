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

    :param cash_remaining:
        Amount still available for investment.

    :param shares:
        Number of accumulated shares.

    :param cost_basis:
        What the shares held cost.
        Purchases add the amount paid.
        Sales take the gain out first:
        the shares left count as bought
        at the sale price, as if the whole
        position had been sold and the
        rest bought again.

        Example, selling only the gain:

            Step             Price  Shares   Value   Cost   Gain
            Buy 10,000         100     100  10,000 10,000      0
            Price rises        125     100  12,500 10,000  2,500
            Sell the gain      125      80  10,000 10,000      0
            (20 shares x 125)

        The 80 shares left cost 10,000: as
        if all 100 had been sold at 125 and
        10,000 bought again. The next gain
        is measured from 10,000.

        Selling more than the gain lowers the
        cost to the value of the shares left:
        selling 5,000 instead of 2,500 leaves
        7,500 in shares, with a cost of 7,500.
    """

    cash_remaining: float
    shares: float = 0.0
    cost_basis: float = 0.0

    def position_value(self, price: float) -> float:
        """
        Market value of the shares at a price.

        :param price:
            Current asset price.

        :return:
            Shares times price.
        """

        return self.shares * price

    def unrealized_gain(self, price: float) -> float:
        """
        Market value of the shares minus what
        they cost. Negative when the position
        is at a loss.

        :param price:
            Current asset price.

        :return:
            Position value minus cost basis.
        """

        return (
                self.position_value(price) -
                self.cost_basis
        )

    def total_value(self, price: float) -> float:
        """
        Shares plus cash at a price.

        :param price:
            Current asset price.

        :return:
            Position value plus remaining cash.
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

        :param price:
            Current asset price.

        :return:
            Position value divided by total
            value.
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

        :param amount:
            Amount of money requested
            to invest.

        :param price:
            Current asset price.

        :return:
            Amount actually invested, which
            may be lower than requested if
            there is not enough cash.
        """

        amount = min(amount, self.cash_remaining)

        self.shares += amount / price
        self.cash_remaining -= amount
        self.cost_basis += amount

        return amount

    def sell(self, amount: float, price: float) -> float:
        """
        Sells shares for a given amount of money.
        The proceeds are added to the cash.

        :param amount:
            Amount of money requested from
            the sale.

        :param price:
            Current asset price.

        :return:
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

        # Gains first: the sale comes out of the
        # unrealized gain, so the cost only drops
        # if the shares left are worth less than
        # it (see cost_basis).
        self.cost_basis = min(
            self.cost_basis,
            self.position_value(price)
        )

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

        :param annual_rate:
            Annual interest rate, e.g.
            0.02 for 2%.

        :param days:
            Days elapsed since the
            previous period.

        :return:
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
