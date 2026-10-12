"""
Executes strategy comparisons across
multiple rolling windows.
"""

from strategies.strategy import Strategy

from models.rolling_window import RollingWindow
from models.rolling_window_result import RollingWindowResult


class RollingBacktestEngine:
    """
    Executes backtests for multiple
    strategies across rolling windows.
    """

    @staticmethod
    def run(
            windows: list[RollingWindow],
            strategies: list[Strategy],
            initial_capital: float
    ) -> list[RollingWindowResult]:
        """
        Executes strategy comparisons
        across rolling windows.

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

        # To be implemented.

        return results
