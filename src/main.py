'''
Created on 10 Oct 2026

@author: mxarl
'''

"""
Application entry point.

Used for manual experiments
and quick strategy comparisons.
"""

'''

src
│
├── analysis
│   ├── backtest_engine.py
│   ├── rolling_windows.py
│   └── metrics.py
│
├── data
│   ├── csv_loader.py
│   └── yahoo_loader.py
│
├── models
│   ├── portfolio.py
│   ├── price_point.py
│   └── backtest_result.py
│
├── strategies
│   ├── strategy.py
│   ├── dca.py
│   ├── drawdown_dca.py
│   └── all_in.py
│
└── main.py

'''

from data.yahoo_loader import YahooLoader
from strategies.all_in import AllIn
from strategies.dca import DCA
from analysis.backtest_engine import BacktestEngine


def main():
    """
        Runs a simple test execution.
    """

    prices = YahooLoader().load(
        ticker="URTH",
        start_date="2016-01-01",
        end_date="2019-01-01"
    )

    strategy = AllIn()

    engine = BacktestEngine()

    result = engine.run(
        prices,
        strategy,
        100000
    )

    print(result)


if __name__ == "__main__":
    main()
