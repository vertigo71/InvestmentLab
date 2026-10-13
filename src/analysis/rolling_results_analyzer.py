"""
Aggregates rolling window backtest results.
"""

from statistics import stdev

from models.rolling_window_result import RollingWindowResult


class RollingResultsAnalyzer:
    """
    Produces aggregate statistics from
    rolling window backtest results.
    """

    @staticmethod
    def get_win_count(
            results: list[RollingWindowResult]
    ) -> dict[str, int]:
        """
        Counts how many rolling windows
        are won by each strategy.

        :param results:
            Rolling window results.

        :return:
            Number of wins per strategy.
        """

        wins: dict[str, int] = {}

        for result in results:

            winner_name: str = ""
            winner_value: float = float("-inf")

            for (
                    strategy_name,
                    strategy_result
            ) in result.strategy_results.items():

                if strategy_result.value > winner_value:
                    winner_name = strategy_name
                    winner_value = strategy_result.value

            if winner_name not in wins:
                wins[winner_name] = 0

            wins[winner_name] += 1

        return wins

    @staticmethod
    def _get_strategy_cagrs(
            results: list[RollingWindowResult]
    ) -> dict[str, list[float]]:
        """
        Returns all CAGR values grouped
        by strategy.

        :param results:
            Rolling window results.

        :return:
            CAGR values grouped by strategy.
        """

        cagrs: dict[str, list[float]] = {}

        for result in results:

            for (
                    strategy_name,
                    strategy_result
            ) in result.strategy_results.items():

                if strategy_name not in cagrs:
                    cagrs[strategy_name] = []

                cagrs[strategy_name].append(
                    strategy_result.cagr(
                        result.initial_capital,
                        result.window_years
                    )
                )

        return cagrs

    @staticmethod
    def get_average_cagr(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the average CAGR
        obtained by each strategy.

        :param results:
            Rolling window results.

        :return:
            Average CAGR per strategy.
        """

        strategy_cagrs = (
            RollingResultsAnalyzer._get_strategy_cagrs(
                results
            )
        )

        return {
            strategy_name:
                sum(values) / len(values)

            for strategy_name, values
            in strategy_cagrs.items()
        }

    @staticmethod
    def get_best_cagr(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the best CAGR obtained
        by each strategy.

        :param results:
            Rolling window results.

        :return:
            Best CAGR per strategy.
        """

        strategy_cagrs = (
            RollingResultsAnalyzer._get_strategy_cagrs(
                results
            )
        )

        return {
            strategy_name: max(values)

            for strategy_name, values
            in strategy_cagrs.items()
        }

    @staticmethod
    def get_worst_cagr(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the worst CAGR obtained
        by each strategy.

        :param results:
            Rolling window results.

        :return:
            Worst CAGR per strategy.
        """

        strategy_cagrs = (
            RollingResultsAnalyzer._get_strategy_cagrs(
                results
            )
        )

        return {
            strategy_name: min(values)

            for strategy_name, values
            in strategy_cagrs.items()
        }

    @staticmethod
    def get_cagr_std_dev(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the standard deviation
        of CAGR values for each strategy.

        :param results:
            Rolling window results.

        :return:
            CAGR standard deviation per strategy.
        """

        strategy_cagrs = (
            RollingResultsAnalyzer._get_strategy_cagrs(
                results
            )
        )

        return {
            strategy_name: stdev(values)

            for strategy_name, values
            in strategy_cagrs.items()
        }
