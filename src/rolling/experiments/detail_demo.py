"""
Displays detailed results for each
rolling analysis window.
"""

from rolling.experiments.base import RollingBase

from core.providers.market_context_provider import (
    MarketContextProvider
)
from rolling.models.rolling_window_result import RollingWindowResult


def main():
    """
    Executes a rolling window analysis
    and prints detailed results for
    every window.
    """

    results: list[RollingWindowResult] = (
        RollingBase.build_results()
    )

    # Legend with what each strategy does.
    RollingBase.print_strategy_legend(
        results
    )

    for result in results:

        print(
            f"\n"
            f"{result.start_year}-"
            f"{result.end_year - 1}"
        )

        for context in (
                MarketContextProvider.get_window_context(
                    start_year=result.start_year,
                    end_year=result.end_year
                )
        ):
            print(
                f"  • {context}"
            )

        # {
        #     "ALL_IN": StrategyResult [value, shares, cash, ...],
        #     "DCA_BIWEEKLY": StrategyResult [value, shares, cash, ...]
        # }
        for (
                strategy_name,
                strategy_result
        ) in result.strategy_results.items():

            cash_text = ""

            if strategy_result.cash > 0:
                cash_text = (
                    f" Cash: "
                    f"€{strategy_result.cash:,.2f}"
                )

            print(
                f"{strategy_name}: "
                f"{strategy_result.value:,.2f} "
                f"("
                f"{strategy_result.cagr():.2%}"
                f")"
                f" MaxDD: "
                f"{strategy_result.max_drawdown:.2%}"
                f"{cash_text}"
            )


if __name__ == "__main__":
    main()
