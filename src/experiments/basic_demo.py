"""
Basic Backtest Demo.

Loads historical data and executes
a simple strategy to validate that
the application is working correctly.
"""

from typing import Final

from analysis.backtest_engine import BacktestEngine
from data.yahoo_loader import YahooLoader
from strategies.all_in import AllIn

INITIAL_CAPITAL: Final = 100000


def main():
    """
    Executes a minimal end-to-end
    backtest scenario.
    """

    prices = YahooLoader.load(
        ticker="URTH",
        start_date="2016-01-01",
        end_date="2019-01-01"
    )

    result = BacktestEngine.run(
        prices=prices,
        strategy=AllIn(),
        initial_capital=INITIAL_CAPITAL
    )

    print()
    print("Basic Backtest Demo")
    print("-------------------")
    print(result)


if __name__ == "__main__":
    main()
