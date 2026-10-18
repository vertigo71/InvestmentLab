"""
Executes strategy comparisons across
multiple rolling windows.
"""

import sys

from core.engines.strategy_simulator import StrategySimulator
from core.models.data_frequency import DataFrequency
from core.models.strategy_result import StrategyResult
from core.strategies.strategy import Strategy

from rolling.models.rolling_window import RollingWindow
from rolling.models.rolling_window_result import RollingWindowResult


class RollingBacktestEngine:
    """
    Executes backtests across multiple
    rolling windows.
    """

    @staticmethod
    def _compatible_strategies(
            strategies: list[Strategy],
            data_frequency: DataFrequency
    ) -> list[Strategy]:
        """
        Keeps the strategies whose contribution
        frequency is possible with the data, and
        reports the skipped ones on stderr
        (shown in red by PyCharm).

        Strategies without a frequency (AllIn)
        are always compatible.

        :param strategies:
            Strategies to filter.

        :param data_frequency:
            Frequency of the price data.

        :return:
            Compatible strategies, in the
            original order.

        :raises ValueError:
            If no strategy is compatible.
        """

        compatible: list[Strategy] = []
        skipped: list[Strategy] = []

        for strategy in strategies:
            frequency = strategy.frequency

            if (
                    frequency is None or
                    frequency.supports(data_frequency)
            ):
                compatible.append(strategy)
            else:
                skipped.append(strategy)

        if skipped:
            print(
                f"Skipped (not possible with "
                f"{data_frequency.name} data):",
                file=sys.stderr
            )

            for strategy in skipped:
                print(
                    f"  - {strategy.name()}",
                    file=sys.stderr
                )

        if not compatible:
            raise ValueError(
                f"No strategy is compatible with "
                f"{data_frequency.name} data"
            )

        return compatible

    @staticmethod
    def run(
            windows: list[RollingWindow],
            strategies: list[Strategy],
            initial_capital: float
    ) -> list[RollingWindowResult]:
        """
        Executes all compatible strategies
        for all rolling windows.

        Strategies whose contribution frequency
        is not possible with the data frequency
        (e.g. BIWEEKLY with monthly data) are
        skipped with a warning.

        :param windows:
            Rolling windows to evaluate.

        :param strategies:
            Investment strategies to compare.

        :param initial_capital:
            Initial portfolio capital.

        :return:
            Rolling window results.
        """

        if not windows:
            return []

        # All windows come from the same
        # series, so they share its frequency.
        strategies = (
            RollingBacktestEngine._compatible_strategies(
                strategies=strategies,
                data_frequency=windows[0].series.frequency
            )
        )

        results: list[RollingWindowResult] = []

        for window in windows:

            strategy_results: dict[str, StrategyResult] = {}

            for strategy in strategies:
                strategy_results[
                    strategy.name()
                ] = StrategySimulator.run(
                    series=window.series,
                    strategy=strategy,
                    initial_capital=initial_capital
                )

            results.append(
                RollingWindowResult(
                    start_year=window.start_year,
                    end_year=window.end_year,
                    initial_capital=initial_capital,
                    strategy_results=strategy_results
                )
            )

        return results
