from data.yahoo_loader import YahooLoader
from transformers.rolling_window_analyzer import RollingWindowAnalyzer


def main():
    prices = YahooLoader.load(
        ticker="URTH",
        start_date="2010-01-01",
        end_date="2027-01-01"
    )

    windows = RollingWindowAnalyzer.create_windows(
        prices,
        window_years=3
    )

    print(f"Windows: {len(windows)}")

    for window in windows:
        print(f"{window.start_year}-{window.end_year} " f"periods={len(window.prices)}")


if __name__ == "__main__":
    main()
