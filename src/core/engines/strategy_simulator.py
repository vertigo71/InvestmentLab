from collections.abc import Iterator
from datetime import date

from core.models.portfolio import PortfolioBase
from core.models.simulation_context import SimulationContext
from core.settings import SETTINGS
from core.models.portfolio import Portfolio
from core.models.price_series import PriceSeries
from core.models.simulation_step import SimulationStep
from core.models.strategy_result import StrategyResult
from core.strategies.strategy import Strategy


class StrategySimulator:

    @staticmethod
    def steps(
            series: PriceSeries,
            strategy: Strategy,
            initial_capital: float,
            cash_annual_rate: float = SETTINGS.cash_annual_rate
    ) -> Iterator[SimulationStep]:
        """
        Simulates a strategy period by
        period.

        This is the single simulation loop
        of the project. Both the final
        result (run) and the detailed
        trace (StrategyTracer) are built
        from these steps.

        :param series:
            Historical market prices.

        :param strategy:
            Investment strategy to simulate.

        :param initial_capital:
            Initial capital available at
            the start of the simulation.

        :param cash_annual_rate:
            Annual interest rate earned by
            uninvested cash. Defaults to the
            global active experiment setting.

        :return:
            One step per price point.

        :raises ValueError:
            If fewer than two prices are
            provided.
        """

        prices = series.points

        if len(prices) < 2:
            raise ValueError(
                "At least two price points "
                "are required"
            )

        portfolio = Portfolio(
            cash_remaining=initial_capital
        )

        # Data rows between two contributions.
        # Fails here if the strategy frequency
        # is not possible with this data, e.g.
        # weekly contributions on monthly data.
        frequency = strategy.frequency

        contribution_periods = (
            frequency.periods(
                series.frequency
            )
            if frequency is not None
            else 1
        )

        # Fixed data of this window, shared by
        # all the calls to the strategy. Each
        # strategy computes its own amounts
        # from it.
        context = SimulationContext(
            initial_capital=initial_capital,
            window_rows=len(prices),
            data_frequency=series.frequency
        )

        # Date of the previous period, used to
        # compute the days of interest. None on
        # the first period: no time has passed.
        previous_date: date | None = None

        for point in prices:

            # Interest earned by the cash that
            # waited since the previous period.
            # Collected before the strategy
            # decides, so it can be invested.
            interest = 0.0

            if previous_date is not None:
                interest = portfolio.earn_interest(
                    annual_rate=cash_annual_rate,
                    days=(point.date - previous_date).days
                )

            previous_date = point.date

            proposed = 0.0

            # Only contribution periods are
            # passed to the strategy.
            if (
                    point.period_index %
                    contribution_periods
                    == 0
            ):
                proposed = strategy.propose_trade(
                    point=point,
                    context=context,
                    portfolio=PortfolioBase(
                        cash_remaining=portfolio.cash_remaining,
                        shares=portfolio.shares
                    )
                )

            shares_before = portfolio.shares
            cash_before = portfolio.cash_remaining

            # The strategy proposes, the simulator
            # executes, within the available cash
            # (buy) or position (sell).
            if proposed > 0:
                portfolio.buy(
                    proposed,
                    point.close
                )
            elif proposed < 0:
                portfolio.sell(
                    -proposed,
                    point.close
                )

            yield SimulationStep(
                point=point,
                interest=interest,
                contribution=(
                        cash_before -
                        portfolio.cash_remaining
                ),
                shares_bought=(
                        portfolio.shares -
                        shares_before
                ),
                accumulated_shares=portfolio.shares,
                cash_remaining=portfolio.cash_remaining
            )

    @staticmethod
    def run(
            series: PriceSeries,
            strategy: Strategy,
            initial_capital: float,
            cash_annual_rate: float = SETTINGS.cash_annual_rate
    ) -> StrategyResult:
        """
        Simulates a strategy and returns
        the final portfolio state.

        The maximum drawdown is measured on
        the total portfolio value (position
        plus cash). Moving cash into shares
        does not change the total, so only
        market movements affect it, which
        makes strategies with uninvested
        cash comparable with lump sum.

        :param series:
            Historical market prices.

        :param strategy:
            Investment strategy to simulate.

        :param initial_capital:
            Initial capital available at
            the start of the simulation.

        :param cash_annual_rate:
            Annual interest rate earned by
            uninvested cash. Defaults to the
            active experiment setting.

        :return:
            Strategy result containing
            final portfolio metrics.
        """

        last_step: SimulationStep | None = None

        # Highest total value reached so far.
        # The portfolio starts fully in cash.
        peak_value = initial_capital

        # Largest decline from a previous
        # peak, as a positive fraction.
        max_drawdown = 0.0

        for step in StrategySimulator.steps(
                series=series,
                strategy=strategy,
                initial_capital=initial_capital,
                cash_annual_rate=cash_annual_rate
        ):
            peak_value = max(
                peak_value,
                step.total_value
            )

            max_drawdown = max(
                max_drawdown,
                1.0 - step.total_value / peak_value
            )

            last_step = step

        # steps() guarantees at least
        # two periods.
        assert last_step is not None

        return StrategyResult(
            value=last_step.position_value,
            shares=last_step.accumulated_shares,
            cash=last_step.cash_remaining,
            initial_capital=initial_capital,
            start_date=series.points[0].date,
            end_date=last_step.point.date,
            max_drawdown=max_drawdown
        )
