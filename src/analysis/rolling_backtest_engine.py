"""
Executes strategy comparisons across
multiple rolling windows.
"""

from analysis.backtest_engine import BacktestEngine

from models.rolling_window import RollingWindow
from models.rolling_window_result import RollingWindowResult
from models.strategy_result import StrategyResult

from strategies.strategy import Strategy


class RollingBacktestEngine:
    """
    Executes backtests across multiple
    rolling windows.
    """

    @staticmethod
    def run(
            windows: list[RollingWindow],
            strategies: list[Strategy],
            initial_capital: float
    ) -> list[RollingWindowResult]:
        """
        Executes all strategies for all
        rolling windows.

        :param windows:
            Rolling windows to evaluate.

        :param strategies:
            Investment strategies to compare.

        :param initial_capital:
            Initial portfolio capital.

        :return:
            Rolling window results.
        """

        results: list[RollingWindowResult] = []

        for window in windows:

            strategy_results: dict[str, StrategyResult] = {}

            for strategy in strategies:
                strategy_results[
                    strategy.name()
                ] = BacktestEngine.run(
                    prices=window.prices,
                    strategy=strategy,
                    initial_capital=initial_capital
                )

            results.append(
                RollingWindowResult(
                    start_year=window.start_year,
                    end_year=window.end_year,
                    strategy_results=strategy_results
                )
            )

        return results


