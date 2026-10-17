"""
Displays detailed results for each
rolling analysis window.
"""

from rolling.experiments.base import RollingBase

from core.providers.market_context_provider import (
    MarketContextProvider
)


def main():
    """
    Executes a rolling window analysis
    and prints detailed results for
    every window.
    """

    results = (
        RollingBase.build_results()
    )

    for result in results:

        print(
            f"\n"
            f"{result.start_year}-"
            f"{result.end_year-1}"
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
                f"{strategy_result.cagr(
                    result.initial_capital,
                    result.window_years
                ):.2%}"
                f")"
                f"{cash_text}"
            )


if __name__ == "__main__":
    main()
