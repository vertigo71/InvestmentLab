"""
Data source verification demo.
"""

import yfinance as yf


def main():
    """
    Prints raw Yahoo Finance
    data for inspection.
    """

    df = yf.download(
        "URTH",
        start="2015-12-01",
        end="2016-02-01",
        interval="1wk",
        auto_adjust=False
    )

    print(df.head(10))


if __name__ == "__main__":
    main()