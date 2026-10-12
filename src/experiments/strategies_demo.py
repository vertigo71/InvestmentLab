"""
Application entry point.

Used for manual experiments
and quick strategy comparisons.
"""

from typing import Final
from math import floor
from data.yahoo_loader import YahooLoader
from analysis.backtest_engine import BacktestEngine
from models.contribution_frequency import ContributionFrequency
from strategies.drawdown_dca import DrawdownDCA
from strategies.all_in import AllIn
from strategies.dca import DCA

INITIAL_CAPITAL: Final = 100000


def main():
    """
        Runs a simple test execution.
    """

    prices = YahooLoader.load(
        ticker="URTH",
        start_date="2016-01-01",
        end_date="2019-01-01"
    )

    number_of_weeks: Final = len(prices)
    weekly_contribution: Final = floor(INITIAL_CAPITAL / (number_of_weeks - 1))

    print(f"Number of weeks = {number_of_weeks}")
    print(f"Initial capital: €{INITIAL_CAPITAL:,.2f}")
    print(f'Weekly contribution: {weekly_contribution}')

    strategy_ai = AllIn()
    strategy_dc_aw = DCA(
        contribution_amount=weekly_contribution,
        frequency=ContributionFrequency.WEEKLY
    )
    strategy_dc_am = DCA(
        contribution_amount=weekly_contribution * 4,
        frequency=ContributionFrequency.MONTHLY
    )
    strategy_ddc_aw = DrawdownDCA(
        base_amount=weekly_contribution,
        levels=[
            (0.01, 2),
            (0.02, 4),
            (0.03, 8)
        ],
        frequency=ContributionFrequency.WEEKLY
    )
    strategy_ddc_am = DrawdownDCA(
        base_amount=weekly_contribution * 4,
        levels=[
            (0.01, 2),
            (0.02, 4),
            (0.03, 8)
        ],
        frequency=ContributionFrequency.MONTHLY
    )

    print(f'AllIn: {BacktestEngine.run(prices, strategy_ai, INITIAL_CAPITAL)}')
    print(f'DCAw : {BacktestEngine.run(prices, strategy_dc_aw, INITIAL_CAPITAL)}')
    print(f'DCAm : {BacktestEngine.run(prices, strategy_dc_am, INITIAL_CAPITAL)}')
    print(f'DDCAw : {BacktestEngine.run(prices, strategy_ddc_aw, INITIAL_CAPITAL)}')
    print(f'DDCAm : {BacktestEngine.run(prices, strategy_ddc_am, INITIAL_CAPITAL)}')


if __name__ == "__main__":
    main()
