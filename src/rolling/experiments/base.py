"""
Shared functionality used by
rolling-window experiments.
"""
from textwrap import fill

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

    @staticmethod
    def print_strategy_legend(
            results: list[RollingWindowResult]
    ) -> None:
        """
        Prints the name and description of each
        simulated strategy, in the order of the
        experiment file.

        Strategies skipped by the engine (e.g.
        incompatible with the data frequency)
        are not listed, as they have no results.

        :param results:
            Rolling-window results, used to know
            which strategies were simulated.
        """

        if not results:
            return

        # All windows have the same strategies.
        simulated = results[0].strategy_results.keys()

        print("Strategies")

        for strategy in SETTINGS.rolling.strategies:

            if strategy.name() not in simulated:
                continue

            print(strategy.name())

            print(
                fill(
                    strategy.description(),
                    width=72,
                    initial_indent="  ",
                    subsequent_indent="  "
                )
            )
