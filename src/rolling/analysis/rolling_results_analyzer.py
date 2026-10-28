"""
Aggregates rolling window backtest results.
"""
from math import ceil
from statistics import stdev

from core.models.strategy_result import StrategyResult
from rolling.models.analysis_metric import AnalysisMetric
from rolling.models.metric_format import MetricFormat
from rolling.models.rolling_window_result import RollingWindowResult
from collections.abc import Callable


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
            # {
            #     "ALL_IN": StrategyResult [total_value, value, shares, cash, ...],
            #     "DCA_BIWEEKLY": StrategyResult [total_value, value, shares, cash, ...]
            # }
            # Find the strategy with the highest
            # total value in this window.
            #
            # items() yields (name, result) pairs:
            #
            #     ("ALL_IN", StrategyResult(...))
            #
            # max() compares pairs by the total
            # value of the result (item[1]) and
            # returns the winning pair. [0] keeps
            # only its name.
            #
            # On ties, max() keeps the first
            # strategy in factory order.
            winner_name: str = max(
                result.strategy_results.items(),
                key=lambda item: item[1].total_value
            )[0]

            wins[winner_name] += 1

        return wins

    @staticmethod
    def _group_by_strategy(
            results: list[RollingWindowResult],
            metric: Callable[
                [StrategyResult],
                float
            ]
    ) -> dict[str, list[float]]:
        """
        Extracts a metric from every window
        and groups the values by strategy.

        :param results:
            Rolling window results.

        :param metric:
            Function returning the value to
            extract from a strategy result.

        :return:
            Metric values grouped by strategy.
            {
            #     "ALL_IN":  [ 12, 13,...]
            #     "DCA_BIWEEKLY":  [ 12, 16,...]
            # }
        """

        grouped: dict[str, list[float]] = {}

        result: RollingWindowResult
        for result in results:
            # {
            #     "ALL_IN": StrategyResult [value, shares, cash, ...],
            #     "DCA_BIWEEKLY": StrategyResult [value, shares, cash, ...]
            # }
            for (
                    strategy_name,
                    strategy_result
            ) in result.strategy_results.items():
                # grouped[strategy_name].append(metric(result, strategy_result))
                grouped.setdefault(  # add if it didn't exist
                    strategy_name,
                    []
                ).append(
                    metric(strategy_result)
                )

        return grouped

    # {
    #     "ALL_IN": [0.1456, 0.1123, ...],
    #     "DCA_BIWEEKLY": [0.0855, 0.0790, ...],
    # }
    @staticmethod
    def _get_strategy_cagrs(
            results: list[RollingWindowResult]
    ) -> dict[str, list[float]]:
        """
        Returns all CAGR values grouped
        by strategy.
        """

        return RollingResultsAnalyzer._group_by_strategy(
            results,
            lambda strategy_result: strategy_result.cagr()
        )

    @staticmethod
    def _get_strategy_max_drawdowns(
            results: list[RollingWindowResult]
    ) -> dict[str, list[float]]:
        """
        Returns all maximum drawdown values
        grouped by strategy.
        """

        return RollingResultsAnalyzer._group_by_strategy(
            results,
            lambda strategy_result: strategy_result.max_drawdown
        )

    @staticmethod
    def _get_strategy_target_ratios(
            results: list[RollingWindowResult],
            target_annual_return: float
    ) -> dict[str, list[float]]:
        """
        Returns all final-value-to-target ratios
        grouped by strategy.
        """

        return RollingResultsAnalyzer._group_by_strategy(
            results,
            lambda strategy_result:
            strategy_result.target_ratio(
                target_annual_return
            )
        )

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
            # item[0]=strategy_name, item[1]=StrategyResult
            ordered_result: list[tuple[str, StrategyResult]] = sorted(
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
                ranks.setdefault(
                    strategy_name, []
                ).append(
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
    def get_average_max_drawdown(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the average maximum drawdown
        obtained by each strategy.
        """

        drawdowns = (
            RollingResultsAnalyzer._get_strategy_max_drawdowns(
                results
            )
        )

        return {
            strategy_name:
                sum(values) / len(values)
            for strategy_name, values
            in drawdowns.items()
        }

    @staticmethod
    def get_worst_max_drawdown(
            results: list[RollingWindowResult]
    ) -> dict[str, float]:
        """
        Returns the largest maximum drawdown
        suffered by each strategy in any
        window.
        """

        drawdowns = (
            RollingResultsAnalyzer._get_strategy_max_drawdowns(
                results
            )
        )

        return {
            strategy_name: max(values)
            for strategy_name, values
            in drawdowns.items()
        }

    @staticmethod
    def get_target_success_rate(
            results: list[RollingWindowResult],
            target_annual_return: float
    ) -> dict[str, float]:
        """
        Returns the fraction of windows in which
        each strategy reaches the target.
        """
        # {
        #     "ALL_IN": [1.02, 0.81, ...]],
        #     "DCA_BIWEEKLY": [1.03, 0.95, ...]],
        # }
        ratios: dict[str, list[float]] = (
            RollingResultsAnalyzer._get_strategy_target_ratios(
                results,
                target_annual_return
            )
        )

        return {
            strategy_name:
                sum(1 for ratio in values if ratio >= 1.0) /
                len(values)
            for strategy_name, values
            in ratios.items()
        }

    @staticmethod
    def get_average_shortfall(
            results: list[RollingWindowResult],
            target_annual_return: float
    ) -> dict[str, float]:
        """
        Returns, for each strategy, how far below
        the target it ends on average in the
        windows where it fails.

        0.20 means ending, on average, with 80% of
        the target. 0.0 if the target is always
        reached.
        """

        ratios: dict[str, list[float]] = (
            RollingResultsAnalyzer._get_strategy_target_ratios(
                results,
                target_annual_return
            )
        )

        shortfalls: dict[str, float] = {}

        for strategy_name, values in ratios.items():
            failures = [
                1.0 - ratio
                for ratio in values
                if ratio < 1.0
            ]

            shortfalls[strategy_name] = (
                sum(failures) / len(failures)
                if failures
                else 0.0
            )

        return shortfalls

    @staticmethod
    def get_worst_target_ratio(
            results: list[RollingWindowResult],
            target_annual_return: float
    ) -> dict[str, float]:
        """
        Returns the lowest final-value-to-target
        ratio of each strategy in any window.

        0.70 means ending with 70% of the target.
        """

        ratios: dict[str, list[float]] = (
            RollingResultsAnalyzer._get_strategy_target_ratios(
                results,
                target_annual_return
            )
        )

        return {
            strategy_name: min(values)
            for strategy_name, values
            in ratios.items()
        }

    @staticmethod
    def get_worst_decile_target_ratio(
            results: list[RollingWindowResult],
            target_annual_return: float
    ) -> dict[str, float]:
        """
        Returns the average final-value-to-target
        ratio over the worst 10% of windows of
        each strategy.

        Less sensitive to a single extreme window
        than the worst ratio.
        """

        ratios = (
            RollingResultsAnalyzer._get_strategy_target_ratios(
                results,
                target_annual_return
            )
        )

        worst_decile: dict[str, float] = {}

        for strategy_name, values in ratios.items():
            # At least one window, so it is also
            # defined with fewer than 10 windows.
            count = max(1, ceil(len(values) * 0.10))

            # Keep the `count` lowest values (worst results)
            worst = sorted(values)[:count]

            worst_decile[strategy_name] = (
                    sum(worst) / len(worst)
            )

        return worst_decile

    @staticmethod
    def build_analysis(
            results: list[RollingWindowResult],
            target_annual_return: float | None = None
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

          :param target_annual_return:
              Minimum annual growth wanted, e.g.
              0.05. When set, target metrics are
              added to the analysis.

        :return:
            Analysis metrics.

        :raises ValueError:
            If fewer than two rolling windows
            are provided.
        """

        # Aggregate statistics such as the
        # CAGR standard deviation are not
        # defined for a single window.
        if len(results) < 2:
            raise ValueError(
                f"Widen the date range or reduce "
                f"rolling.window_years in the "
                f"experiment file."
            )

        metrics = [

            AnalysisMetric(
                name="Win Count",
                description=(
                    "Windows in which the strategy ends "
                    "with the highest total value. "
                    "Higher is better."
                ),
                values=
                RollingResultsAnalyzer.get_win_count(
                    results
                ),
                reverse=True,
                format=MetricFormat.INTEGER
            ),

            AnalysisMetric(
                name="Average CAGR",
                description=(
                    "Average annual growth rate over all "
                    "windows. Higher is better."
                ),
                values=
                RollingResultsAnalyzer.get_average_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Best CAGR",
                description=(
                    "Highest annual growth rate in any "
                    "window. Higher is better."
                ),
                values=
                RollingResultsAnalyzer.get_best_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Worst CAGR",
                description=(
                    "Lowest annual growth rate in any "
                    "window. Higher is better."
                ),
                values=
                RollingResultsAnalyzer.get_worst_cagr(
                    results
                ),
                reverse=True,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="CAGR Std Dev",
                description=(
                    "How much the annual growth rate "
                    "varies between windows (not within "
                    "a window). Lower is better."
                ),
                values=
                RollingResultsAnalyzer.get_cagr_std_dev(
                    results
                ),
                reverse=False,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Average Max Drawdown",
                description=(
                    "Average, over all windows, of the "
                    "largest peak-to-trough fall of the "
                    "portfolio value. Lower is better."
                ),
                values=
                RollingResultsAnalyzer.get_average_max_drawdown(
                    results
                ),
                reverse=False,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Worst Max Drawdown",
                description=(
                    "Largest peak-to-trough fall of the "
                    "portfolio value in any window. "
                    "Lower is better."
                ),
                values=
                RollingResultsAnalyzer.get_worst_max_drawdown(
                    results
                ),
                reverse=False,
                format=MetricFormat.PERCENTAGE
            ),

            AnalysisMetric(
                name="Average Rank",
                description=(
                    "Average position among all "
                    "strategies (1 = best final value). "
                    "Lower is better."
                ),
                values=
                RollingResultsAnalyzer.get_average_rank(
                    results
                ),
                reverse=False,
                format=MetricFormat.DECIMAL
            )
        ]

        if target_annual_return is not None:
            target = f"{target_annual_return * 100:g}%"

            metrics.extend([

                AnalysisMetric(
                    name=f"Target {target} Success Rate",
                    description=(
                        f"Fraction of windows reaching the "
                        f"target: initial capital growing "
                        f"{target} per year. Higher is better."
                    ),
                    values=
                    RollingResultsAnalyzer.get_target_success_rate(
                        results,
                        target_annual_return
                    ),
                    reverse=True,
                    format=MetricFormat.PERCENTAGE
                ),

                AnalysisMetric(
                    name=f"Target {target} Average Shortfall",
                    description=(
                        "In the windows that miss the "
                        "target, how far below it they end "
                        "on average. 20% = ending with 80% "
                        "of the target. Lower is better."
                    ),
                    values=
                    RollingResultsAnalyzer.get_average_shortfall(
                        results,
                        target_annual_return
                    ),
                    reverse=False,
                    format=MetricFormat.PERCENTAGE
                ),

                AnalysisMetric(
                    name=f"Target {target} Worst Ratio",
                    description=(
                        "Lowest final value / target in any "
                        "window. 50% = ending with half of "
                        "the target. Higher is better."
                    ),
                    values=
                    RollingResultsAnalyzer.get_worst_target_ratio(
                        results,
                        target_annual_return
                    ),
                    reverse=True,
                    format=MetricFormat.PERCENTAGE
                ),

                AnalysisMetric(
                    name=f"Target {target} Worst 10% Ratio",
                    description=(
                        "Average final value / target over "
                        "the worst 10% of windows. Less "
                        "sensitive to a single extreme "
                        "window. Higher is better."
                    ),
                    values=
                    RollingResultsAnalyzer.get_worst_decile_target_ratio(
                        results,
                        target_annual_return
                    ),
                    reverse=True,
                    format=MetricFormat.PERCENTAGE
                ),
            ])

        return metrics
