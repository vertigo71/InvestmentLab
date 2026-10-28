# InvestmentLab

A Python backtesting framework to compare investment contribution
strategies on historical market data: lump sum, classic Dollar Cost
Averaging (DCA), drawdown-based DCA and fixed-allocation portfolios
with periodic rebalancing (e.g. 70% shares, 30% money market).

The main question it answers is:

> Given a fixed amount of capital, which way of deploying it into the
> market produces the best results, and how consistently, across many
> different historical periods?

To avoid conclusions that depend on a single lucky or unlucky period,
strategies are compared over **rolling windows** (e.g. every 5-year
period from 1990 onwards, or from 1871 with Shiller's data), and the
results are aggregated into statistics on return (win count, average
CAGR, CAGR dispersion), risk (maximum drawdown) and, optionally, a
minimum annual return target.

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
- Pluggable strategies through a common `Strategy` interface: the
  strategy proposes each trade, the simulator executes it.
- Optional deployment period (`deploy_years`): invest the capital
  over a few years, then hold.
- Optional take profit for drawdown DCA: sell the gain when the shares
  are worth a given fraction more than they cost.
- Rolling-window backtests with aggregated return and risk analysis,
  and optional metrics against a minimum annual return target.
- Strategy and metric descriptions printed with the results.
- Detailed per-period execution traces, exportable to CSV, used to
  validate the simulator against an independent spreadsheet.
- Historical market context per year since 1870, shown alongside
  window results.
- Fail-fast validation of inputs and data (missing prices, invalid
  strategy levels, impossible frequencies, insufficient windows).

---

## Strategies

| Strategy      | Name pattern                                                | Behaviour                                                                                                                                                        |
|---------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `AllIn`       | `ALL_IN`                                                    | Invests all capital in the first period.                                                                                                                         |
| `DCA`         | `DCA_<FREQUENCY>[_<x>Y]`                                    | Invests a fixed amount at a fixed frequency.                                                                                                                     |
| `DrawdownDCA` | `DDCA_<REF>_<FREQUENCY>[_<x>Y][_BASE<x>]_<levels>[_TP<x>%]` | Like DCA, but scales each contribution by a multiplier that depends on how far the price is below a reference price. Optionally sells the gain above a threshold. |
| `Rebalance`   | `REBALANCE_<weight>_<FREQUENCY>[_TOL<x>]`, `HOLD_<weight>`  | Keeps a fixed fraction in shares and the rest in cash, buying or selling periodically to restore it.                                                             |

Parts in brackets only appear when they are set: `_<x>Y` is
`deploy_years` (see [Contributions](#contributions)), `_BASE<x>` a
`base_multiplier` other than 1, and `_TP<x>%` the take profit. Each
strategy also has a one-sentence description, printed as a legend by
the rolling demos.

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
| `QUARTERLY`         | 63      | 13       | 3         |
| `SEMIANNUAL`        | 126     | 26       | 6         |
| `ANNUAL`            | 252     | 52       | 12        |

With daily or weekly data the values are approximations (21 trading
days or 4 weeks per month, 52 weeks per year). In the rolling analysis, strategies with an impossible
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
    base_multiplier=1.0,
    deploy_years=3
)
```

In an experiment file, the same strategy is written as:

```yaml
- type: drawdown_dca
  frequency: BIWEEKLY
  reference_price: RUNNING_MAX
  base_multiplier: 1.0          # optional
  deploy_years: 3               # optional
  levels: [[0.10, 2], [0.20, 3], [0.30, 4], [0.40, 5]]
```

Multipliers invest faster than the base pace, so with `deploy_years`
the capital may run out before the deployment period ends.

Levels are validated on creation:

- thresholds must be strictly increasing (no duplicates);
- thresholds must be lower than 1 (catches `10` instead of `0.10`);
  negative thresholds are allowed;
- multipliers and `base_multiplier` must be positive.

#### Take profit

With `take_profit`, the strategy also sells gains. At each
contribution, if the shares are worth at least that fraction more
than they cost, it sells the gain instead of buying:

```
gain = shares × price − cost_basis
gain >= take_profit × cost_basis   →   sell the gain
otherwise                          →   the usual contribution
```

The money from the sale returns to cash, earns `cash_annual_rate` and
is invested again at the strategy pace in the following
contributions.

```yaml
- type: drawdown_dca
  frequency: BIWEEKLY
  reference_price: RUNNING_AVG
  deploy_years: 3
  levels: [[0.10, 2], [0.20, 3], [0.30, 4], [0.40, 5]]
  take_profit: 0.20             # optional, must be positive
```

The cost of the shares (`cost_basis`, kept by the portfolio) follows
a **gains-first** rule: a sale comes out of the gain first, and the
shares left count as bought at the sale price, as if the whole
position had been sold and the rest bought again. Selling only the
gain therefore leaves the cost unchanged, and the next gain is
measured from there:

| Step          | Price | Shares | Value  | Cost   | Gain  |
|---------------|-------|--------|--------|--------|-------|
| Buy 10,000    | 100   | 100    | 10,000 | 10,000 | 0     |
| Price rises   | 125   | 100    | 12,500 | 10,000 | 2,500 |
| Sell the gain | 125   | 80     | 10,000 | 10,000 | 0     |

Purchases add the amount paid to the cost. Selling more than the gain
(which `Rebalance` can do) lowers the cost to the value of the shares
left.

The rule is checked only on contribution rows, and only when there
are shares: a cost of zero has no gain to sell. After a sale, the
strategy keeps buying with the returned cash even after
`deploy_years`, since it buys as long as there is cash.

### Rebalance

A fixed fraction of the total value is kept in shares and the rest in
cash, which earns `cash_annual_rate` (a money market fund). On the
first period the target allocation is bought; on each review period
the strategy proposes the trade that restores it:

```
total value   = shares × price + cash
target shares = total value × equity_weight
trade         = target shares − current shares value
                (positive: buy, negative: sell)
```

```yaml
- type: rebalance
  equity_weight: 0.70        # 70/30
  frequency: SEMIANNUAL
  tolerance: 0.0             # optional
```

With a `tolerance`, the portfolio is rebalanced only when the share
weight deviates more than that from the target, in weight points
(`0.05` with `0.70`: below 65% or above 75%). A tolerance of `1.0` or
more never rebalances after the initial allocation; the strategy is
then named `HOLD_<weight>` and shows what rebalancing itself adds.

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

The simulator decides on which rows the strategy is called and
executes the trades; strategies only propose them.

1. **Rows between contributions**, from the strategy frequency and the
   data frequency (see the table above). Strategies without a
   frequency (`AllIn`) are called on every row.

2. **Window data for the strategies.** Before the first row, the
   simulator creates a `SimulationContext` with the initial capital,
   the number of rows of the window and the data frequency. It is the
   same for every call in that window.

3. On contribution rows only, the simulator calls
   `strategy.propose_trade(point, context, portfolio)`, which returns
   a signed amount of money: positive to buy, negative to sell, zero
   to do nothing.

   - `DCA` proposes the base contribution;
   - `DrawdownDCA` proposes the base contribution × multiplier, or,
     with take profit, minus the gain to sell it;
   - `AllIn` proposes all the cash on row 0 and nothing afterwards;
   - `Rebalance` ignores the base contribution and proposes the trade
     that restores its target weight.

4. The simulator executes the proposed trade with `Portfolio`. A
   purchase never exceeds the cash, and a sale never exceeds the
   position value.

**Base contribution.** `DCA` and `DrawdownDCA` compute it with
`context.base_contribution(frequency, deploy_years)`: the capital is
spread over the rows of the deployment period, and multiplied by the
rows between contributions:

```
deploy_rows       = window_rows - 1                           without deploy_years
                  = round(deploy_years × rows_per_year)       with deploy_years
amount_per_row    = floor(initial_capital / deploy_rows)
base_contribution = amount_per_row × rows_between_contributions
```

`rows_per_year` is 252 for daily data, 52 for weekly and 12 for
monthly. One row is subtracted without `deploy_years` so that rounding
never leaves the capital short of the last periods.

Example with 100,000, weekly data, `BIWEEKLY` and `deploy_years: 3`:
`3 × 52 = 156` rows, `floor(100000 / 156) = 641` per row, 2 rows
between contributions, so 1,282 is proposed on rows 0, 2, 4... until
the cash runs out, after about 3 years. Without `deploy_years`, the
capital is spread over the whole window. If `deploy_years` is longer
than the window, part of the capital is still in cash at the end.

**The portfolio seen by the strategies.** The `portfolio` passed to
`propose_trade` is a `PortfolioBase` copy: cash, shares, the cost of
the shares (`cost_basis`, see [Take profit](#take-profit)) and the
values derived from them (`position_value`, `total_value`,
`equity_weight`, `unrealized_gain`), but no `buy()` or `sell()`.
Strategies can read it but cannot trade by themselves or change the
real portfolio.

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

`AllIn` is not affected: it has no cash after the first period. For
`Rebalance`, the interest is the return of its cash part.

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
│   ├── sp500_weekly_10y.yaml      10-year windows, incl. 70/30
│   ├── sp500_biweekly_tp_10y.yaml Drawdown DCA with take profit
│   ├── shiller_monthly.yaml
│   └── shiller_monthly_10y.yaml   10-year windows, incl. 70/30
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
    │   ├── models/             PricePoint, PriceSeries, PortfolioBase,
    │   │                       Portfolio, SimulationContext,
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
    │   ├── strategies/         Strategy interface, implementations and
    │   │                       shared description texts
    │   └── transformers/
    │       └── price_point_builder.py   Period indexes and running stats
    ├── rolling/                Rolling-window analysis
    │   ├── analysis/           Aggregate metrics
    │   ├── engines/            Runs all strategies on all windows
    │   ├── experiments/        Runnable demos, their shared base and
    │   │                       output file names
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
  target_annual_return: 0.05   # optional, 0.05 = 5%
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
      deploy_years: 1          # optional
    - type: drawdown_dca
      frequency: MONTHLY
      reference_price: RUNNING_MAX
      levels: [[0.10, 2], [0.20, 3], [0.30, 4], [0.40, 5]]
      take_profit: 0.20        # optional
    - type: rebalance
      equity_weight: 0.70
      frequency: SEMIANNUAL
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
there is any, the remaining cash. The detail and analysis demos end
with a legend: the name and description of each simulated strategy.

### Aggregate metrics

| Metric               | Meaning                                                                         | Better when |
|----------------------|---------------------------------------------------------------------------------|-------------|
| Win Count            | Windows in which the strategy ends with the highest total value.                | Higher      |
| Average CAGR         | Average annual growth rate over all windows.                                    | Higher      |
| Best CAGR            | Highest annual growth rate in any window.                                       | Higher      |
| Worst CAGR           | Lowest annual growth rate in any window.                                        | Higher      |
| CAGR Std Dev         | How much the annual growth rate varies between windows (not within a window).   | Lower       |
| Average Max Drawdown | Average, over all windows, of the largest peak-to-trough fall of the portfolio. | Lower       |
| Worst Max Drawdown   | Largest peak-to-trough fall of the portfolio value in any window.               | Lower       |
| Average Rank         | Average position among all strategies (1 = best final value).                   | Lower       |

With `target_annual_return` in the experiment file, four metrics are
added. The target of a window is the initial capital growing at that
rate, and each window is measured by its ratio to it:

```
target = initial_capital × (1 + target_annual_return) ** years
ratio  = total_value / target
```

For example, 100,000 over 10 years at 5% gives a target of about
162,889; ending with 130,000 is a ratio of 80%.

| Metric                      | Meaning                                                                                                | Better when |
|-----------------------------|--------------------------------------------------------------------------------------------------------|-------------|
| Target X% Success Rate      | Fraction of windows reaching the target (ratio ≥ 100%).                                                | Higher      |
| Target X% Average Shortfall | In the windows that miss the target, how far below it they end on average (20% = 80% of the target).   | Lower       |
| Target X% Worst Ratio       | Lowest ratio in any window.                                                                            | Higher      |
| Target X% Worst 10% Ratio   | Average ratio over the worst 10% of windows (at least one). Less sensitive to a single extreme window. | Higher      |

Success rate says how often the target is reached; the worst ratios
say how badly a strategy ends when things go wrong. A negative target
is allowed, e.g. `-0.02`: lose at most 2% per year.

The analysis demo prints the description of each metric with the
results. The analysis requires at least two rolling windows.

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
- **No taxes or trading costs.** Sales (rebalancing, take profit) are
  treated as transfers between funds, with no tax on the gain and no
  fees.
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
- **More risk metrics.** In this order: probability of loss and 5th
  percentile; time to recovery after the worst drawdown; Calmar ratio
  (CAGR / maximum drawdown); Sharpe and Sortino ratios from period
  returns within each window, with `cash_annual_rate` as the risk-free
  rate; drawdown in the last 2-3 years of the window (sequence risk);
  and real returns, deflating the final value with the CPI (Shiller's
  CPI column, or FRED `CPIAUCSL` for Yahoo data). Before the step-based
  ones, move the calculations over the simulation steps (including
  the maximum drawdown) out of `StrategySimulator.run()` into their
  own module.
- **DCA in cycles.** Deploy the capital with DCA or drawdown DCA over
  `deploy_years`. At the end of the period, if the profit reaches a
  configurable target, move everything to the money market and start a
  new cycle; otherwise keep it invested until the target is reached. A
  further parameter would avoid moving to cash after a market decline.
  Related to the take profit, which sells only the gain and is checked
  on every contribution; `cost_basis` could be reused.
- **Take profit variants.** Sell everything or only the part above the
  threshold, apply the rule only after the capital is fully deployed,
  or measure the gain on the average cost (which does not change when
  selling, so the position is sold gradually while the price stays
  above the threshold).

### Data

- **Local cache for Yahoo data.** Store downloaded prices in a file so
  every run, the rolling analysis and the spreadsheet use exactly the
  same data.
- **Market context per market.** Separate yearly descriptions for
  non-US indexes such as the Nikkei.

### Robustness

- **Unique strategy name check.** Fail fast in `RollingBacktestEngine`
  when two strategies share a name.
- **Incomplete windows.** Skip, or warn about, windows that do not
  have complete years of data (e.g. when the data ends before the
  requested end date).
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
- **`DrawdownDCA` as a subclass of `DCA`.** Both share the frequency,
  the deployment period, its validation and the base amount; only the
  multiplier and the take profit are specific to drawdown DCA.
- **Experiment comparator.** Compare the results of two experiments
  or two exports of the same one.
- **Packaging** with a `pyproject.toml` and a pinned dependency list.
- **`live` module.** Apply a chosen strategy to current market data to
  suggest this period's contribution.
