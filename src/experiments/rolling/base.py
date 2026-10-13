"""
Shared functionality used by
rolling-window experiments.
"""

from analysis.rolling_backtest_engine import (
    RollingBacktestEngine
)

from data.yahoo_loader import YahooLoader

from factories.strategy_factory import (
    StrategyFactory
)

from models.rolling_window_result import (
    RollingWindowResult
)

from transformers.rolling_window_builder import (
    RollingWindowBuilder
)

from experiments.rolling.config import (
    INITIAL_CAPITAL,
    WINDOW_YEARS,
    TICKER,
    START_DATE,
    END_DATE
)


class RollingBase:
    """
    Provides the common setup required
    by all rolling-window experiments.

    Responsibilities:

        - Load historical data.
        - Create rolling windows.
        - Create strategies.
        - Execute backtests.
    """

    @staticmethod
    def build_results() -> list[RollingWindowResult]:
        """
        Executes the standard rolling-window
        analysis pipeline.

        :return:
            Rolling-window results for all
            configured strategies.
        """

        prices = YahooLoader.load(
            ticker=TICKER,
            start_date=START_DATE,
            end_date=END_DATE
        )

        windows = (
            RollingWindowBuilder.create_windows(
                prices=prices,
                window_years=WINDOW_YEARS
            )
        )

        strategies = (
            StrategyFactory.create()
        )

        return (
            RollingBacktestEngine.run(
                windows=windows,
                strategies=strategies,
                initial_capital=INITIAL_CAPITAL
            )
        )
