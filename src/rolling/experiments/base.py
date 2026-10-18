"""
Shared functionality used by
rolling-window experiments.
"""

from core.config import INITIAL_CAPITAL

from rolling.engines.rolling_backtest_engine import (
    RollingBacktestEngine
)
from rolling.experiments.config import (
    DATA_SOURCE,
    END_DATE,
    START_DATE,
    WINDOW_YEARS
)
from rolling.factories.strategy_factory import (
    StrategyFactory
)
from rolling.models.rolling_window_result import (
    RollingWindowResult
)
from rolling.transformers.rolling_window_builder import (
    RollingWindowBuilder
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

        The data source (Yahoo, CSV...) is
        chosen in the rolling config.

        :return:
            Rolling-window results for all
            configured strategies.
        """

        series = DATA_SOURCE.load(
            start_date=START_DATE,
            end_date=END_DATE
        )

        windows = (
            RollingWindowBuilder.create_windows(
                series=series,
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