"""
Application entry point.

Used for manual experiments
and quick strategy comparisons.
"""

from data.yahoo_loader import YahooLoader
from analysis.backtest_engine import BacktestEngine
from models.contribution_frequency import ContributionFrequency
from strategies.drawdown_dca import DrawdownDCA
from strategies.all_in import AllIn
from strategies.dca import DCA


def main():
    """
        Runs a simple test execution.
    """

    prices = YahooLoader.load(
        ticker="URTH",
        start_date="2016-01-01",
        end_date="2019-01-01"
    )

    strategy_ai = AllIn()
    strategy_dc_aw = DCA(
        contribution_amount=641,
        frequency=ContributionFrequency.WEEKLY
    )
    strategy_dc_am = DCA(
        contribution_amount=641 * 4,
        frequency=ContributionFrequency.MONTHLY
    )
    strategy_ddc_aw = DrawdownDCA(
        base_amount=641,
        levels=[
            (0.01, 2),
            (0.02, 4),
            (0.03, 8)
        ],
        frequency=ContributionFrequency.WEEKLY
    )
    strategy_ddc_am = DrawdownDCA(
        base_amount=641 * 4,
        levels=[
            (0.01, 2),
            (0.02, 4),
            (0.03, 8)
        ],
        frequency=ContributionFrequency.MONTHLY
    )

    print(f'AllIn: {BacktestEngine.run(prices, strategy_ai, 100000)}')
    print(f'DCAw : {BacktestEngine.run(prices, strategy_dc_aw, 100000)}')
    print(f'DCAm : {BacktestEngine.run(prices, strategy_dc_am, 100000)}')
    print(f'DDCAw : {BacktestEngine.run(prices, strategy_ddc_aw, 100000)}')
    print(f'DDCAm : {BacktestEngine.run(prices, strategy_ddc_am, 100000)}')


if __name__ == "__main__":
    main()
