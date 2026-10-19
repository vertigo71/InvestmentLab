"""
Converts Robert Shiller's ie_data.xls into a
monthly nominal total return CSV.

Download ie_data.xls from https://shillerdata.com/
into the inputs folder and run from the src folder:

    python -m scripts.shiller_converter

The output CSV has two columns, date and close,
and can be read with CsvLoader:

    date,close
    1871-01-01,4.44
    1871-02-01,4.5216...

Notes on the source data:

- P is the monthly average of daily closes,
  not the end-of-month close.
- D is the annualized dividend, interpolated
  from quarterly (since 1926) or annual
  (before 1926) figures.
- The "Real Total Return Price" column in the
  file is inflation-adjusted. This converter
  builds a nominal series instead, so it is
  comparable with Yahoo prices and cash.
"""

import csv
from datetime import date
from pathlib import Path
from typing import Final

import pandas as pd

from core.config import INPUT_FOLDER

# Original file downloaded from shillerdata.com.
SOURCE_FILE: Final = INPUT_FOLDER / "ie_data.xls"

# Converted file read by CsvLoader.
OUTPUT_FILE: Final = (
        INPUT_FOLDER / "shiller_sp_tr_monthly.csv"
)

# Columns used from the "Data" sheet,
# by position (0 = column A).
#
# Final[int] instead of plain Final, so the
# type checker sees them as int and not as
# the literal values 0, 1 and 2.
DATE_COLUMN: Final[int] = 0  # A: Date (1871.01)
PRICE_COLUMN: Final[int] = 1  # B: P (S&P Comp. price)
DIVIDEND_COLUMN: Final[int] = 2  # C: D (annualized dividend)


def _parse_date(value: float) -> date:
    """
    Converts Shiller's date format into a date
    on the first day of the month.

    The decimal part is the month, but Excel
    stores the value as a number, so trailing
    zeros are lost:

        1871.01 -> January 1871
        1871.1  -> October 1871 (1871.10)
        1871.12 -> December 1871

    :param value:
        Shiller date as a number.

    :return:
        First day of that month.

    :raises ValueError:
        If the month is not between 1 and 12.
    """

    # Integer part: the year.
    #
    #     int(1871.1) -> 1871
    year = int(value)

    # Decimal part times 100: the month.
    #
    #     (1871.1 - 1871) * 100 -> 9.9999...
    #
    # Floating point arithmetic does not give
    # exactly 10, so the result is rounded.
    month = round((value - year) * 100)

    if not 1 <= month <= 12:
        raise ValueError(
            f"Invalid Shiller date: {value}"
        )

    return date(year, month, 1)


def convert(
        source_file: Path,
        output_file: Path
) -> int:
    """
    Builds the nominal total return series and
    writes it to CSV.

    The monthly total return combines the price
    change with one twelfth of the annualized
    dividend:

        growth = (P[t] + D[t] / 12) / P[t-1]

    The series starts at the first price.

    :param source_file:
        Shiller ie_data.xls file.

    :param output_file:
        Output CSV file.

    :return:
        Number of rows written.

    :raises ValueError:
        If the data contains gaps or the dates
        are not in order.
    """

    # ----------------------------------------
    # 1. Read the three columns from Excel
    # ----------------------------------------

    # read_excel returns a DataFrame: a table
    # with rows and named columns.
    #
    # header=None:
    #     Do not use any row as column names.
    #     Shiller's header spans several rows,
    #     so pandas could not read it anyway.
    #     Columns are named by position: 0, 1, 2.
    #
    # usecols:
    #     Only read these columns.
    #
    # Every row of the sheet is read, including
    # titles and header rows. They are removed
    # in step 2.
    #
    # PyCharm misreads the usecols union in the
    # pandas stubs and only accepts int. The call
    # is valid: usecols accepts a list of column
    # indexes.
    # noinspection PyTypeChecker
    raw = pd.read_excel(
        source_file,
        sheet_name="Data",
        header=None,
        usecols=[
            DATE_COLUMN,
            PRICE_COLUMN,
            DIVIDEND_COLUMN
        ]
    )

    # Rename columns 0, 1, 2 to readable names,
    # in the same order, so they can be accessed
    # as raw["price"] instead of raw[1].
    raw.columns = ["date", "price", "dividend"]

    # ----------------------------------------
    # 2. Keep only the data rows
    # ----------------------------------------

    # Convert each column to numbers.
    #
    # errors="coerce":
    #     Anything that is not a number becomes
    #     NaN (Not a Number) instead of raising
    #     an error.
    #
    #     1871.01   -> 1871.01
    #     "Date"    -> NaN
    #     "NA"      -> NaN
    #     empty     -> NaN (already NaN on read)
    #
    # After this, title and header rows have NaN
    # in the date and price columns.
    for column in raw.columns:
        raw[column] = pd.to_numeric(
            raw[column],
            errors="coerce"
        )

    # Remove every row with NaN in date or price
    # (one of them is enough). This removes the
    # title, header and note rows.
    #
    # Rows with only a missing dividend are
    # kept on purpose: they are handled in
    # step 3.
    #
    # reset_index(drop=True):
    #     After dropna, rows keep their original
    #     numbers (the first data row would still
    #     be row 8). This renumbers them 0, 1, 2...
    #     drop=True discards the old numbering
    #     instead of keeping it as a column.
    data = raw.dropna(
        subset=["date", "price"]
    ).reset_index(drop=True)

    # ----------------------------------------
    # 3. Handle missing dividends
    # ----------------------------------------

    # The most recent months may not have a
    # dividend yet. Those trailing rows are
    # dropped; a missing dividend anywhere
    # else is a data error.

    # data["dividend"].notna():
    #     A True/False value per row: True where
    #     the dividend exists.
    #
    # data.index[...]:
    #     The row numbers where it is True.
    valid_dividends = data.index[
        data["dividend"].notna()
    ]

    # Row number of the last month with
    # a dividend.
    last_valid = valid_dividends[-1]

    # data.loc[:last_valid]:
    #     All rows from the first one up to and
    #     including last_valid. Unlike Python
    #     lists, loc includes the end row.
    #
    # This drops the trailing months without
    # dividend.
    data = data.loc[:last_valid]

    # Any remaining missing dividend is a gap
    # in the middle of the data.
    #
    # data["dividend"].isna().any():
    #     True if at least one row has NaN.
    if data["dividend"].isna().any():
        # data.loc[condition, "date"]:
        #     The date column of the rows where
        #     the condition is True.
        missing = data.loc[
            data["dividend"].isna(),
            "date"
        ].tolist()

        raise ValueError(
            f"Missing dividends for dates: "
            f"{missing}"
        )

    # ----------------------------------------
    # 4. Convert and validate dates
    # ----------------------------------------

    # Iterating over a column gives its values
    # one by one, as with a list.
    dates = [
        _parse_date(value)
        for value in data["date"]
    ]

    # Each date must be later than the previous.
    for i in range(1, len(dates)):
        if dates[i] <= dates[i - 1]:
            raise ValueError("Dates are not strictly increasing")

    # ----------------------------------------
    # 5. Build the total return series
    # ----------------------------------------

    # Operations between columns are applied row
    # by row, without an explicit loop.
    #
    # data["price"].shift(1):
    #     The price column moved down one row,
    #     so each row sees the previous month's
    #     price. The first row has no previous
    #     price and gets NaN.
    #
    #     row   price   shift(1)
    #     0     4.44    NaN
    #     1     4.50    4.44
    #     2     4.61    4.50
    #
    # growth is the monthly total return factor:
    # current price plus one month of dividend,
    # divided by the previous price.
    #
    #     row 1: (4.50 + 0.26 / 12) / 4.44 = 1.0184
    growth = (
            (data["price"] + data["dividend"] / 12) /
            data["price"].shift(1)
    )

    # growth.fillna(1.0):
    #     Replaces the NaN of the first row with
    #     1.0 (no change in the first month).
    #
    # cumprod():
    #     Cumulative product: each row is the
    #     product of all factors up to that row.
    #
    #     row   growth   cumprod
    #     0     1.0      1.0
    #     1     1.0184   1.0184
    #     2     1.0293   1.0482
    #
    # Multiplying by the first price makes the
    # series start at 4.44, like the index.
    total_return = (
            data["price"].iloc[0] *
            growth.fillna(1.0).cumprod()
    )

    # ----------------------------------------
    # 6. Write the CSV
    # ----------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
            mode="w",
            newline="",
            encoding="utf-8"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(["date", "close"])

        # dates and total_return have one value
        # per month, in the same order.
        for row_date, close in zip(
                dates,
                total_return
        ):
            writer.writerow([
                row_date.isoformat(),
                close
            ])

    return len(dates)


def main():
    """
    Converts the default Shiller file.
    """

    rows = convert(
        source_file=SOURCE_FILE,
        output_file=OUTPUT_FILE
    )

    print(
        f"{rows} monthly rows written to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
