# InvestmentLab

A Python backtesting framework to compare investment contribution
strategies on historical market data: lump sum, classic Dollar Cost
Averaging (DCA) and drawdown-based DCA.

The main question it answers is:

> Given a fixed amount of capital, which way of deploying it into the
> market produces the best results, and how consistently, across many
> different historical periods?

To avoid conclusions that depend on a single lucky or unlucky period,
strategies are compared over **rolling windows** (e.g. every 5-year
period from 1990 onwards, or from 1871 with Shiller's data), and the
results are aggregated into statistics on return (win count, average
CAGR, CAGR dispersion) and risk (maximum drawdown).

---

## Features

- Historical data from Yahoo Finance (daily, weekly or monthly) or
  from local CSV files.
- Monthly US stock market data since 1871 from Robert Shiller,
  converted to a nominal total return series.
- Data frequency travels with the prices. Strategies that are not
  possible with the data (e.g. biweekly contributions on monthly data)
  are skipped with a warning.
- Experiments defined in YAML files: data source, dates, window,
  capital, cash interest and strategies, without editing Python code.
- Pluggable strategies through a common `Strategy` interface.
- Rolling-window backtests with aggregated return and risk analysis.
- Detailed per-period execution traces, exportable to CSV, used to
  validate the simulator against an independent spreadsheet.
- Historical market context per year since 1870, shown alongside
  window results.
- Fail-fast validation of inputs and data (missing prices, invalid
  strategy levels, impossible frequencies, insufficient windows).

---

## Strategies

| Strategy      | Name pattern                                | Behaviour                                                                                                            |
|---------------|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `AllIn`       | `ALL_IN`                                    | Invests all capital in the first period.                                                                             |
| `DCA`         | `DCA_<FREQUENCY>`                           | Invests a fixed amount at a fixed frequency.                                                                         |
| `DrawdownDCA` | `DDCA_<REF>_<FREQUENCY>_[BASE<x>_]<levels>` | Like DCA, but scales each contribution by a multiplier that depends on how far the price is below a reference price. |

### Data frequency and contribution frequency

Two different frequencies are involved:

- **Data frequency** (`DataFrequency`): time between two rows of price
  data. It is set by the loader that produced the data and travels
  with the prices inside a `PriceSeries`.
- **Contribution frequency** (`ContributionFrequency`): time between
  two contributions, in calendar terms. It is declared by the
  strategy.

`ContributionFrequency.periods(data_frequency)` translates one into
the other, as the number of data rows between two contributions:

| Contribution \ Data | `DAILY` | `WEEKLY` | `MONTHLY` |
|---------------------|---------|----------|-----------|
| `WEEKLY`            | 5       | 1        | error     |
| `BIWEEKLY`          | 10      | 2        | error     |
| `MONTHLY`           | 21      | 4        | 1         |

`MONTHLY` with daily or weekly data is an approximation (21 trading
days, 4 weeks). In the rolling analysis, strategies with an impossible
combination are skipped with a warning on stderr, so the same
strategy list can be used with any data source. Calling
the simulator directly with an impossible combination raises a
`ValueError`.

### Drawdown DCA

The drawdown is measured against a reference price:

```
drawdown = 1 - price / reference_price
```

| Reference     | Meaning                                                                                                |
|---------------|--------------------------------------------------------------------------------------------------------|
| `RUNNING_MAX` | Highest close since the start of the window. Drawdown is never negative.                               |
| `RUNNING_AVG` | Average close since the start of the window. Drawdown is negative when the price is above the average. |

Levels are `(threshold, multiplier)` pairs. The multiplier of the
deepest threshold reached is applied. When no threshold is reached,
`base_multiplier` (default `1.0`) is used.

```python
DrawdownDCA(
    levels=[
        (0.10, 2),
        (0.20, 3),
        (0.30, 4),
        (0.40, 5),
    ],
    frequency=ContributionFrequency.BIWEEKLY,
    reference_price=ReferencePrice.RUNNING_MAX,
    base_multiplier=1.0
)
```

In an experiment file, the same strategy is written as:

```yaml
- type: drawdown_dca
  frequency: BIWEEKLY
  reference_price: RUNNING_MAX
  base_multiplier: 1.0          # optional
  levels: [[0.10, 2], [0.20, 3], [0.30, 4], [0.40, 5]]
```

Levels are validated on creation:

- thresholds must be strictly increasing (no duplicates);
- thresholds must be lower than 1 (catches `10` instead of `0.10`);
  negative thresholds are allowed;
- multipliers and `base_multiplier` must be positive.

---

## Simulation model

### Timeline

Each row of data is a point in time: the closing price of that period
(week, month or day, depending on the data frequency).

```
row 0     first purchase, no evolution yet
row 1..N  contributions according to the strategy
row N     final valuation
```

With `N + 1` rows there are `N` intervals, which is also the elapsed
time used to annualize returns.

### Contributions

The simulator computes the contribution schedule; strategies only
decide how much to invest.

1. **Base contribution per data row:**

   ```
   period_contribution = floor(initial_capital / (number_of_rows - 1))
   ```

2. **Rows between contributions**, from the strategy frequency and the
   data frequency (see the table above). Strategies without a
   frequency (`AllIn`) are evaluated on every row.

3. **Amount proposed on each contribution:**

   ```
   contribution_amount = period_contribution × rows_between_contributions
   ```

4. On contribution rows only, the simulator calls
   `strategy.contribution(point, contribution_amount, cash_remaining)`:

   - `DCA` invests `contribution_amount`;
   - `DrawdownDCA` invests `contribution_amount × multiplier`;
   - `AllIn` invests all the cash on row 0 and nothing afterward.

A purchase can never exceed the remaining cash.

Example with 100,000 and 157 weekly rows, `BIWEEKLY`:
`floor(100000 / 156) = 641` per row, 2 rows between contributions,
so 1,282 is proposed on rows 0, 2, 4...

### Interest on cash

Uninvested cash earns a fixed annual rate, `cash_annual_rate` in the
experiment file (`0.0` means no interest). At the start of each period, before
the strategy decides, the cash grows by the actual days elapsed since
the previous period:

```
factor = (1 + annual_rate) ** (days / 365.25)
```

Compounding over actual days gives exactly the annual rate after one
year, with weekly or monthly data. There is no interest on the first
period, since no time has passed. Interest left uninvested at the end
of a window remains as cash and counts in `total_value`.

`AllIn` is not affected: it has no cash after the first period.

### Results

`StrategyResult` keeps the invested position and the cash separately:

| Field             | Meaning                                                        |
|-------------------|----------------------------------------------------------------|
| `value`           | Market value of the accumulated shares.                        |
| `cash`            | Uninvested cash.                                               |
| `total_value`     | `value + cash`, used for all performance metrics.              |
| `initial_capital` | Capital available at the start of the simulation.              |
| `years`           | Elapsed time between the first and last price dates.           |
| `max_drawdown`    | Largest peak-to-trough decline of `total_value` (0.25 = -25%). |

CAGR is computed from the actual elapsed time:

```
years = (end_date - start_date).days / 365.25
cagr  = (total_value / initial_capital) ** (1 / years) - 1
```

### Maximum drawdown

The maximum drawdown is measured on the **total portfolio value**
(shares plus cash), not on the shares alone. Moving cash into shares
does not change the total, so only market movements affect it. This
makes strategies that keep cash waiting comparable with lump sum: with
the shares alone, a DCA portfolio would keep growing through new
contributions and hide market declines.

### Single simulation loop

`StrategySimulator.steps()` is the only simulation loop in the project.
It yields one `SimulationStep` per period. Both the final result
(`StrategySimulator.run()`) and the detailed trace (`StrategyTracer`)
are built from these steps, so validating the trace validates the same
code used by the rolling analysis.

---

## Project structure

```
InvestmentLab/
├── configs/                    Experiment files (see Configuration)
│   ├── active_yaml.txt         Name of the experiment to run
│   ├── config_help.txt         Reference of all available options
│   ├── sp500_weekly.yaml
│   └── shiller_monthly.yaml
├── docs/
│   └── theoretical_base.md     Derivations and worked examples
├── inputs/                     Input data files (Shiller, CSV prices)
├── outputs/                    Generated files, one folder per experiment
└── src/
    ├── main.py
    ├── core/                   Simulation core, shared by all modules
    │   ├── config.py           Project paths and export date
    │   ├── settings.py         Loads and validates the active experiment
    │   ├── file_utils.py       File helpers (non-overwriting file names)
    │   ├── engines/
    │   │   └── strategy_simulator.py
    │   ├── experiments/
    │   │   └── basic_demo.py   Minimal end-to-end check
    │   ├── models/             PricePoint, PriceSeries, Portfolio,
    │   │                       SimulationStep, StrategyResult,
    │   │                       DataFrequency, ContributionFrequency,
    │   │                       ReferencePrice
    │   ├── providers/
    │   │   ├── data_source.py  DataSource base class
    │   │   ├── yahoo_source.py Yahoo Finance data source
    │   │   ├── csv_source.py   CSV file data source
    │   │   ├── yahoo_loader.py Yahoo Finance download and validation
    │   │   ├── csv_loader.py   Generic date,close CSV loader
    │   │   └── market_context_provider.py
    │   ├── strategies/         Strategy interface and implementations
    │   └── transformers/
    │       └── price_point_builder.py   Period indexes and running stats
    ├── rolling/                Rolling-window analysis
    │   ├── analysis/           Aggregate metrics
    │   ├── engines/            Runs all strategies on all windows
    │   ├── experiments/        Runnable demos and output file names
    │   ├── exporters/          CSV exports
    │   ├── models/
    │   └── transformers/       Rolling window creation
    ├── tracing/                Per-period execution traces
    │   ├── engines/
    │   ├── experiments/        Trace demo and configuration
    │   ├── exporters/
    │   └── models/
    ├── scripts/                Standalone scripts run by hand, not
    │   │                       imported by the backtest
    │   └── shiller_converter.py
    └── live/                   Reserved for future use
```

---

## Requirements

- Python 3.12 or later (developed with 3.13)
- `yfinance` (also installs `pandas`)
- `pyyaml`, to read the experiment files
- `xlrd`, only to convert Shiller's `.xls` file

```bash
pip install -r requirements.txt
```

---

## Usage

Run the experiments as modules from the `src` directory (or mark `src`
as the sources root in your IDE):

```bash
cd src

# Minimal end-to-end check
python -m core.experiments.basic_demo

# Rolling analysis
python -m rolling.experiments.detail_demo          # per-window results
python -m rolling.experiments.detail_export_demo   # per-window CSV
python -m rolling.experiments.analysis_demo        # aggregate metrics
python -m rolling.experiments.analysis_export_demo # aggregate CSV

# Execution trace
python -m tracing.experiments.trace_demo

# Convert Shiller data (after downloading ie_data.xls)
python -m scripts.shiller_converter
```

### Configuration

Each experiment is a YAML file in `configs/`. The one to run is named,
without the `.yaml` extension, in `configs/active_yaml.txt`:

```
# Lines starting with # are ignored.
sp500_weekly
```

To switch experiments, change that name and run any demo again. To
create a new one, copy an existing file and edit it. All available
options are described in `configs/config_help.txt`.

An experiment file defines:

```yaml
initial_capital: 100000
cash_annual_rate: 0.0          # 0.02 = 2%

rolling:
  window_years: 3
  start_date: "1990-01-01"
  end_date: "2026-01-01"       # excluded

  data_source:
    type: yahoo                # or csv
    ticker: "^SP500TR"
    frequency: WEEKLY

  strategies:
    - type: all_in
    - type: dca
      frequency: MONTHLY
    - type: drawdown_dca
      frequency: MONTHLY
      reference_price: RUNNING_MAX
      levels: [[0.10, 2], [0.20, 3], [0.30, 4], [0.40, 5]]
```

A CSV source is written as:

```yaml
  data_source:
    type: csv
    label: SHILLER                      # used in messages and names
    path: shiller_sp_tr_monthly.csv     # relative to inputs/
    frequency: MONTHLY                  # required
```

`core/settings.py` reads the active experiment when the program starts
and builds the data source and the strategies. Any error stops the
program with the file and field to fix, for example:

```
sp500_weekly.yaml: rolling.strategies, strategy 2: missing frequency;
unknown frequncy (allowed: frequency, type)
```

Unknown keys are reported too, so typos do not go unnoticed. Settings
that are not part of an experiment stay in Python:

| What                         | Where                               |
|------------------------------|-------------------------------------|
| Project paths, export date   | `core/config.py`                    |
| Output file names            | `rolling/experiments/config.py`     |
| Trace ticker and date range  | `tracing/experiments/config.py`     |
| Traced strategy              | `tracing/experiments/trace_demo.py` |

The trace demo takes the initial capital and the cash rate from the
active experiment. Keep `cash_annual_rate: 0.0` when validating a
trace against the spreadsheet, which does not compute interest.

### Data sources

| Source                | Description                                                                                   |
|-----------------------|-----------------------------------------------------------------------------------------------|
| `^SP500TR` (Yahoo)    | S&P 500 Total Return (dividends reinvested). Default for rolling analysis; history from 1990. |
| `^GSPC` (Yahoo)       | S&P 500 price index. **Excludes dividends.**                                                  |
| `^N225` (Yahoo)       | Nikkei 225 price index, in JPY. **Excludes dividends.**                                       |
| `URTH` (Yahoo)        | iShares MSCI World ETF (from 2012).                                                           |
| `VT` (Yahoo)          | Vanguard Total World Stock ETF (from 2008).                                                   |
| `0P...` codes (Yahoo) | European funds, using Morningstar identifiers.                                                |
| Shiller (CSV)         | S&P Composite nominal total return, monthly, from 1871. See [Shiller data](#shiller-data).    |
| Any CSV               | Two columns, `date` (YYYY-MM-DD) and `close`, read with `CsvLoader`.                          |

### Outputs

Rolling exports are written to `outputs/<experiment>/`, prefixed with
the generation date and the window length. Each CSV gets a twin
`.yaml` file with the exact experiment settings used, comments
included, so every result can be traced back and reproduced:

```
outputs/sp500_weekly/
├── 20261020_rolling_analysis_3y.csv
├── 20261020_rolling_analysis_3y.yaml
├── 20261020_rolling_analysis_3y (1).csv
└── 20261020_rolling_analysis_3y (1).yaml
```

Exports never overwrite previous files: if a name already exists,
`(1)`, `(2)`... is added, like Windows copies.

Traces are still written to the root of `outputs/`:

```
YYYYMMDD_tracing_3y_URTH_<strategy name>.csv
```

### Example

```
2020-2024
  • COVID crash and recovery.
  • Post-pandemic expansion.
  • Inflation shock. Bear market.
  • AI-driven recovery.
  • Broad bull market.
ALL_IN: 196,848.76 (14.56%)
DCA_BIWEEKLY: 150,525.26 (8.55%)
DCA_MONTHLY: 150,424.41 (8.54%)
DDCA_MAX_BIWEEKLY_(10%;2)_(20%;3)_(30%;4)_(40%;5): 168,407.80 (11.03%)
DDCA_MAX_MONTHLY_(10%;2)_(20%;3)_(30%;4)_(40%;5): 167,225.53 (10.87%)
DDCA_AVG_BIWEEKLY_(10%;2)_(20%;3)_(30%;4)_(40%;5): 154,479.94 (9.12%)
DDCA_AVG_MONTHLY_(10%;2)_(20%;3)_(30%;4)_(40%;5): 152,869.15 (8.89%)
```

Each line shows the final total value and the CAGR. The detail demo
also prints the maximum drawdown of each strategy (`MaxDD`) and, when
there is any, the remaining cash.

### Aggregate metrics

| Metric               | Better when |
|----------------------|-------------|
| Win Count            | Higher      |
| Average CAGR         | Higher      |
| Best CAGR            | Higher      |
| Worst CAGR           | Higher      |
| CAGR Std Dev         | Lower       |
| Average Max Drawdown | Lower       |
| Worst Max Drawdown   | Lower       |
| Average Rank         | Lower       |

The analysis requires at least two rolling windows.

### Market context

`MarketContextProvider` holds a short description of the main market
events of each year from 1870 onwards, shown next to each window.
Descriptions are US-centric; they may not fit other markets (e.g. 1990
in Japan).

---

## Validation

The tracing module exports every simulated period (prices, running
statistics, drawdowns, contributions, shares, position value and cash)
so results can be reproduced in an independent spreadsheet.

The trace uses **raw (unadjusted) prices** (`auto_adjust=False`):

- they match the prices used by the spreadsheet (Google Finance);
- they do not change between downloads.

Adjusted prices are recalculated by Yahoo on every download and differ
by tiny floating-point amounts, which breaks an exact comparison.

---

## Assumptions and limitations

- **Cash earns a fixed rate.** `cash_annual_rate` is the same for the
  whole history, while real short-term rates have ranged from near 0%
  (1930s-1940s, 2010s) to over 10% (early 1980s). With the default of
  0%, results slightly favour lump sum over strategies that keep cash
  waiting.
- **Decision and purchase use the same close.** A strategy sees a
  period's closing price and buys at that same price.
- **Gross dividends, in the index currency.** Total return series
  ignore dividend withholding tax, fund costs and exchange rate
  movements (e.g. EUR/USD).
- **Yahoo data is downloaded on every run.** Adjusted prices may
  differ marginally between runs. CSV data does not change.
- **`MONTHLY` is approximated** with daily (21 trading days) and
  weekly (4 weeks, 13 contributions per year) data. With monthly data
  it is exact.
- **Strategy names must be unique.** They are used as result keys; a
  duplicate silently overwrites another strategy's results.
- **Ties in win count go to the first strategy** in the order of the
  experiment file.

---

## Shiller data

Robert Shiller publishes monthly US stock market data since January
1871 at [shillerdata.com](https://shillerdata.com/) (`ie_data.xls`).
It allows backtests over periods not covered by Yahoo Finance,
such as 1929.

### Updating the data

1. Download `ie_data.xls` from shillerdata.com into the `inputs` folder.
2. From `src`, run the converter (requires `pip install xlrd`):

   ```bash
   python -m scripts.shiller_converter
   ```

3. It writes `inputs/shiller_sp_tr_monthly.csv`, which is read with
   `CsvLoader` using `DataFrequency.MONTHLY`.

The converted CSV acts as a local cache: every run uses the same data
until the file is regenerated.

### How the series is built

The converter uses the price (`P`, monthly average of daily closes)
and the annual dividend (`D`) of each month, and reinvests one twelfth
of the dividend every month:

```
growth = (P[t] + D[t] / 12) / P[t-1]
```

The cumulative product of these factors is the total return series.
It is **nominal**: the file's *Real Total Return Price* column is
inflation-adjusted and is not used.

See [docs/theoretical_base.md](docs/theoretical_base.md) for the
derivation of the formula, a worked example with the first months of
1871 and a comparison with Shiller's own real series.

### Limitations

- **Monthly averages smooth the data.** Crash lows are diluted in the
  month's average, so maximum drawdowns are smaller than with
  end-of-period prices, and drawdown DCA strategies react less.
  Results are not directly comparable with weekly Yahoo data.
- **Only monthly contributions.** With monthly data, `WEEKLY` and
  `BIWEEKLY` strategies are skipped with a warning.
- **Dividends are approximations.** They are interpolated, received
  as one twelfth of the annual amount and reinvested at the monthly
  price.
- **Pre-1900 data is less reliable.** The early index is reconstructed
  from the few companies listed at the time, mostly railroads.
- **Gross dividends in USD**, with no taxes or costs, as with
  `^SP500TR`.

---

## Possible improvements

### Methodology

- **Historical cash rates.** Replace the fixed `cash_annual_rate` with
  a historical short-term rate series (e.g. 3-month US Treasury bills)
  to approximate a money market fund over time.
- **Money-weighted return.** Report IRR (XIRR), which measures the
  return of the money while invested.
- **Execute at the next period's open.** Decide with the close of
  period `t` and buy at the `Open` of period `t + 1` (the first price
  available after the decision). Requires adding `open` to
  `PricePoint`; the last row would be used only for valuation.
- **Calendar months with weekly data.** Contribute in the first week
  of each calendar month (12 per year) instead of every 4 weeks (13 per
  year).
- **EUR perspective.** Convert USD prices with `EURUSD=X` to obtain
  the returns a euro-based investor would see.
- **More risk metrics.** Time to recovery and capital deployment speed
  per strategy.

### Data

- **Local cache for Yahoo data.** Store downloaded prices in a file so
  every run, the rolling analysis and the spreadsheet use exactly the
  same data.
- **Market context per market.** Separate yearly descriptions for
  non-US indexes such as the Nikkei.

### Robustness

- **Unique strategy name check.** Fail fast in `RollingBacktestEngine`
  when two strategies share a name.
- **More precise level formatting** in `DrawdownDCA.name()` (e.g.
  `1.5%` instead of `2%`).
- **Explicit tie handling** in win count.

### Engineering

- **Automated tests** (e.g. `pytest`): known-answer tests for each
  strategy, the simulator, CAGR and drawdown calculation, frequency
  conversion, window creation, level validation and the Shiller
  converter, plus a regression test against a stored trace.
- **Trace columns for risk.** Add total value and portfolio drawdown
  to the trace, to validate the maximum drawdown in the spreadsheet.
- **Tracing settings in YAML.** Move the trace ticker, dates and
  strategy into the experiment files, as for the rolling analysis.
- **Packaging** with a `pyproject.toml` and a pinned dependency list.
- **`live` module.** Apply a chosen strategy to current market data to
  suggest this period's contribution.
  
