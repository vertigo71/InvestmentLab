"""
Strategy trace generation demo.
"""

from core.config import (
    INITIAL_CAPITAL
)
from core.models.contribution_frequency import (
    ContributionFrequency
)
from core.models.reference_price import ReferencePrice
from core.providers.yahoo_loader import (
    YahooLoader
)
from core.strategies.dca import DCA
from core.strategies.drawdown_dca import DrawdownDCA

from tracing.engines.strategy_tracer import (
    StrategyTracer
)
from tracing.exporters.strategy_trace_csv_exporter import (
    StrategyTraceCsvExporter
)

from tracing.experiments.config import (
    CSV_OUTPUT_FILE,
    END_DATE,
    START_DATE,
    TICKER
)


def main():
    """
    Generates a strategy trace and
    exports it to CSV.
    """

    # NOTE:
    #
    # Validation traces use
    # unadjusted market prices.
    #
    # The objective of the tracing
    # module is to reproduce the
    # calculations performed in a
    # Google Finance spreadsheet.
    #
    # Google Finance returns raw
    # market prices that do not
    # include the effects of
    # dividend reinvestment.
    #
    # Therefore:
    #
    # Spreadsheet
    # == Yahoo Close
    #
    # Core application
    # == Yahoo Adjusted Close
    #
    # The purpose of tracing is
    # validation only. Once the
    # simulator has been validated,
    # the rolling analysis module
    # remains the production path
    # and continues to use adjusted
    # prices including dividends.
    prices = YahooLoader.load(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
        auto_adjust=False
    )

    strategy = DrawdownDCA(
                levels=[
                    (0.01, 2),
                    (0.02, 3),
                    (0.03, 4),
                    (0.04, 5),
                ],
                frequency=ContributionFrequency.BIWEEKLY,
                reference_price=ReferencePrice.RUNNING_AVG
            )

    trace = StrategyTracer.run(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
        prices=prices,
        strategy=strategy,
        initial_capital=
        INITIAL_CAPITAL
    )

    StrategyTraceCsvExporter.export(
        trace=trace,
        output_file=
        CSV_OUTPUT_FILE
    )

    print()

    print(
        "Strategy Trace Demo"
    )

    print(
        "-------------------"
    )

    print(
        f"Ticker: "
        f"{trace.ticker}"
    )

    print(
        f"Strategy: "
        f"{trace.strategy.name()}"
    )

    print(
        f"Rows: "
        f"{len(trace.rows)}"
    )

    print()

    print(
        f"Trace CSV exported to:\n"
        f"{CSV_OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
