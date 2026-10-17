"""
Aggregates rolling window backtest results.
"""

from statistics import stdev

from rolling.models.analysis_metric import AnalysisMetric
from rolling.models.metric_format import MetricFormat
from rolling.models.rolling_window_result import RollingWindowResult


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

        if not results:
            return {}

        # Initialize all strategies
        # with zero wins so that
        # strategies that never win
        # are still included in the
        # returned dictionary.
        wins: dict[str, int] = {
            strategy_name: 0
            for strategy_name in (
                results[0]
                .strategy_results
                .keys()
            )
        }

        for result in results:
            winner_name = max(
                result.strategy_results.items(),
                key=lambda item: item[1].total_value
            )[0]

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

    @staticmethod
    def get_average_rank(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the average rank
        obtained by each strategy.

        :param results:
            Rolling window results.

        :return:
            Average rank per strategy.
        """

        # Rank history grouped
        # by strategy.
        ranks: dict[str, list[int]] = {}

        for result in results:

            # Sort strategies from best
            # to worst according to the
            # final portfolio value.
            # strategy_results: dict[str, StrategyResult]
            ordered_result = sorted(
                result.strategy_results.items(),
                key=lambda item: item[1].total_value,
                reverse=True
            )

            # Assign ranks:
            #
            # 1 = best strategy
            # 2 = second place
            # 3 = third place
            # ...
            # ordered_result: list[tuple[str, StrategyResult]]
            for rank, (strategy_name, _) in enumerate(
                    ordered_result,
                    start=1
            ):

                if strategy_name not in ranks:
                    ranks[strategy_name] = []

                ranks[strategy_name].append(
                    rank
                )

        # Calculate the average rank
        # achieved by each strategy
        # across all rolling windows.
        return {
            strategy_name:
                sum(values) / len(values)
            for strategy_name, values
            in ranks.items()
        }

    @staticmethod
    def build_analysis(
            results: list[RollingWindowResult]
    ) -> list[AnalysisMetric]:
        """
        Builds the complete rolling
        analysis.

        Each AnalysisMetric contains
        the metric values together with
        the display and sorting rules
        required by reporting components.

        :param results:
            Rolling window results.

        :return:
            Analysis metrics.
        """

        return [

            AnalysisMetric(
                name="Win Count",
                values=
                RollingResultsAnalyzer.get_win_count(
                    results
                ),
                reverse=True,
                format=MetricFormat.INTEGER
            ),

            AnalysisMetric(
                name="Average CAGR",
                values=
                RollingResultsAnalyzer.get_average_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Best CAGR",
                values=
                RollingResultsAnalyzer.get_best_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Worst CAGR",
                values=
                RollingResultsAnalyzer.get_worst_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="CAGR Std Dev",
                values=
                RollingResultsAnalyzer.get_cagr_std_dev(
                    results
                ),
                reverse=False,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Average Rank",
                values=
                RollingResultsAnalyzer.get_average_rank(
                    results
                ),
                reverse=False,
                format=MetricFormat.DECIMAL
            )
        ]
