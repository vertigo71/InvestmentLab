"""
Shared functionality used by
rolling-window experiments.
"""

from core.settings import SETTINGS

from rolling.engines.rolling_backtest_engine import (
    RollingBacktestEngine
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
        - Execute backtests.

    Everything is taken from the active
    experiment YAML file (see
    configs/active_yaml.txt).
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

        rolling = SETTINGS.rolling

        series = rolling.data_source.load(
            start_date=rolling.start_date,
            end_date=rolling.end_date
        )

        windows = (
            RollingWindowBuilder.create_windows(
                series=series,
                window_years=rolling.window_years
            )
        )

        return (
            RollingBacktestEngine.run(
                windows=windows,
                strategies=rolling.strategies,
                initial_capital=SETTINGS.initial_capital
            )
        )
