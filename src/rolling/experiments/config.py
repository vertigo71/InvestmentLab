"""
Configuration used by
rolling-window experiments.
"""

from typing import Final

from core.config import (
    GENERATED_ON,
    INPUT_FOLDER,
    OUTPUT_FOLDER
)
from core.models.data_frequency import DataFrequency
from core.providers.csv_source import CsvSource
from core.providers.data_source import DataSource
from core.providers.yahoo_source import YahooSource

# Price data source.
#
# Uncomment exactly one.
#
# Yahoo tickers (weekly):
#
#     ^SP500TR      S&P 500 total return, 1990 -
#     ^GSPC         S&P 500 price only, no dividends
#     ^N225         Nikkei 225, no dividends
#     URTH          MSCI World ETF, 2012 -
#     VT            Total World ETF, 2008 -
#     0P00000RQC.F  European fund (Morningstar code)
#
# Shiller (monthly, 1871 -):
#
#     Only MONTHLY strategies can be used.
#     Update the strategy factory accordingly.

# DATA_SOURCE: Final[DataSource] = YahooSource(
#     ticker="^SP500TR"
# )

DATA_SOURCE: Final[DataSource] = CsvSource(
    label="SHILLER",
    path=INPUT_FOLDER / "shiller_sp_tr_monthly.csv",
    frequency=DataFrequency.MONTHLY
)

# Historical data range.
START_DATE: Final = "1800-01-01"
END_DATE: Final = "2026-01-01"

# Rolling window length.
WINDOW_YEARS: Final = 3

#
# modify strategies in strategy_factory file
#

# Rolling results CSV export file.
CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_results_"
        f"{WINDOW_YEARS}y_"
        f"{DATA_SOURCE.name}.csv"
)

# Rolling analysis CSV export file.
ANALYSIS_CSV_OUTPUT_FILE: Final = (
        OUTPUT_FOLDER /
        f"{GENERATED_ON}_"
        f"rolling_analysis_"
        f"{WINDOW_YEARS}y_"
        f"{DATA_SOURCE.name}.csv"
)