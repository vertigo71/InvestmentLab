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
period from 1990 onwards), and the results are aggregated into
statistics such as win count, average CAGR and CAGR dispersion.

---

## Features

- Weekly historical data from Yahoo Finance (via `yfinance`).
- Pluggable strategies through a common `Strategy` interface.
- Rolling-window backtests with aggregated analysis.
- Detailed per-week execution traces, exportable to CSV, used to
  validate the simulator against an independent spreadsheet.
- Historical market context per year, shown alongside window results.
- Fail-fast validation of inputs and data (missing prices, invalid
  strategy levels, insufficient windows).

---

## Strategies

| Strategy | Name pattern | Behaviour |
|---|---|---|
| `AllIn` | `ALL_IN` | Invests all capital in the first period. |
| `DCA` | `DCA_<FREQUENCY>` | Invests a fixed amount at a fixed frequency. |
| `DrawdownDCA` | `DDCA_<REF>_<FREQUENCY>_[BASE<x>_]<levels>` | Like DCA, but scales each contribution by a multiplier that depends on how far the price is below a reference price. |

### Contribution frequency

The project works with **weekly periods**. `ContributionFrequency`
defines how many weeks pass between contributions:

| Frequency | Weeks |
|---|---|
| `WEEKLY` | 1 |
| `BIWEEKLY` | 2 |
| `MONTHLY` | 4 (approximation) |

### Drawdown DCA

The drawdown is measured against a reference price:

```
drawdown = 1 - price / reference_price
```

| Reference | Meaning |
|---|---|
| `RUNNING_MAX` | Highest close since the start of the window. Drawdown is never negative. |
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

Levels are validated on creation:

- thresholds must be strictly increasing (no duplicates);
- thresholds must be lower than 1 (catches `10` instead of `0.10`);
  negative thresholds are allowed;
- multipliers and `base_multiplier` must be positive.

---

## Simulation model

### Timeline

Each row of weekly data is a point in time: the closing price of that
week.

```
row 0     first purchase, no evolution yet
row 1..N  contributions according to the strategy
row N     final valuation
```

With `N + 1` rows there are `N` weekly intervals, which is also the
elapsed time used to annualize returns.

### Contributions

The engine proposes a base weekly contribution to every strategy:

```
weekly_contribution = floor(initial_capital / (number_of_rows - 1))
```

Strategies decide how much of it to invest (multiplying it by their
frequency and, for drawdown DCA, by the active multiplier). A purchase
can never exceed the remaining cash.

### Results

`StrategyResult` keeps the invested position and the cash separately:

| Field | Meaning |
|---|---|
| `value` | Market value of the accumulated shares. |
| `cash` | Uninvested cash. |
| `total_value` | `value + cash`, used for all performance metrics. |
| `years` | Elapsed time between the first and last price dates. |

CAGR is computed from the actual elapsed time:

```
years = (end_date - start_date).days / 365.25
cagr  = (total_value / initial_capital) ** (1 / years) - 1
```

### Single simulation loop

`StrategySimulator.steps()` is the only simulation loop in the project.
It yields one `SimulationStep` per period. Both the final result
(`StrategySimulator.run()`) and the detailed trace (`StrategyTracer`)
are built from these steps, so validating the trace validates the same
code used by the rolling analysis.

---

## Project structure

```
src/
├── main.py
├── core/                       Simulation core, shared by all modules
│   ├── config.py               Project paths, initial capital, export date
│   ├── engines/
│   │   └── strategy_simulator.py
│   ├── experiments/
│   │   └── basic_demo.py       Minimal end-to-end check
│   ├── models/                 PricePoint, Portfolio, SimulationStep,
│   │                           StrategyResult, enums
│   ├── providers/
│   │   ├── yahoo_loader.py     Weekly data download and validation
│   │   └── market_context_provider.py
│   ├── strategies/             Strategy interface and implementations
│   └── transformers/
│       └── price_point_builder.py   Period indexes and running stats
├── rolling/                    Rolling-window analysis
│   ├── analysis/               Aggregate metrics
│   ├── engines/                Runs all strategies on all windows
│   ├── experiments/            Runnable demos and configuration
│   ├── exporters/              CSV exports
│   ├── factories/
│   │   └── strategy_factory.py Strategies to compare
│   ├── models/
│   └── transformers/           Rolling window creation
├── tracing/                    Per-week execution traces
│   ├── engines/
│   ├── experiments/            Trace demo and configuration
│   ├── exporters/
│   └── models/
└── live/                       Reserved for future use
```

---

## Requirements

- Python 3.12 or later (developed with 3.13)
- `yfinance`

```bash
pip install yfinance
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
```

### Configuration

| What | Where |
|---|---|
| Initial capital, output folder | `core/config.py` |
| Rolling ticker, date range, window length | `rolling/experiments/config.py` |
| Strategies to compare | `rolling/factories/strategy_factory.py` |
| Trace ticker and date range | `tracing/experiments/config.py` |
| Traced strategy | `tracing/experiments/trace_demo.py` |

### Tickers

| Ticker | Description |
|---|---|
| `^SP500TR` | S&P 500 Total Return (dividends reinvested). Default for rolling analysis; history from 1990. |
| `^GSPC` | S&P 500 price index. **Excludes dividends.** |
| `URTH` | iShares MSCI World ETF (from 2012). |
| `VT` | Vanguard Total World Stock ETF (from 2008). |

### Outputs

CSV files are written to `outputs/` at the project root, prefixed with
the generation date:

```
YYYYMMDD_rolling_results_5y_SP500TR.csv
YYYYMMDD_rolling_analysis_5y_SP500TR.csv
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

### Aggregate metrics

| Metric | Better when |
|---|---|
| Win Count | Higher |
| Average CAGR | Higher |
| Best CAGR | Higher |
| Worst CAGR | Higher |
| CAGR Std Dev | Lower |
| Average Rank | Lower |

The analysis requires at least two rolling windows.

---

## Validation

The tracing module exports every simulated week (prices, running
statistics, drawdowns, contributions, shares, position value and cash)
so results can be reproduced in an independent spreadsheet.

The trace uses **raw (unadjusted) prices** (`auto_adjust=False`):

- they match the prices used by the spreadsheet (Google Finance);
- they do not change between downloads.

Adjusted prices are recalculated by Yahoo on every download and differ
by tiny floating-point amounts, which breaks an exact comparison.

---

## Assumptions and limitations

- **Cash earns 0%.** Uninvested cash is counted at face value, which
  slightly favours lump sum over strategies that keep cash waiting.
- **Decision and purchase use the same close.** A strategy sees a
  week's closing price and buys at that same price.
- **Gross dividends, in USD.** `^SP500TR` ignores dividend withholding
  tax, fund costs and EUR/USD exchange rate movements.
- **Data is downloaded on every run.** Adjusted prices may differ
  marginally between runs.
- **`MONTHLY` means every 4 weeks**, i.e. 13 contributions per year.
- **Strategy names must be unique.** They are used as result keys; a
  duplicate silently overwrites another strategy's results.
- **Ties in win count go to the first strategy** in factory order.

---

## Possible improvements

### Methodology

- **Execute at the next week's open.** Decide with the close of week
  `t` and buy at the `Open` of week `t + 1` (the first price available
  after the decision). Requires adding `open` to `PricePoint`; the
  last row would be used only for valuation.
- **Cash remuneration or money-weighted return.** Apply an interest
  rate to uninvested cash (e.g. a money market proxy), and/or report
  IRR (XIRR), which measures the return of the money while invested.
- **EUR perspective.** Convert USD prices with `EURUSD=X` to obtain
  the returns a euro-based investor would see.
- **Risk metrics.** Maximum drawdown of the portfolio value, time to
  recovery, and capital deployment speed per strategy.

### Robustness

- **Local data cache.** Store downloaded prices in a file so every
  run, the rolling analysis and the spreadsheet use exactly the same
  data.
- **Unique strategy name check.** Fail fast in `RollingBacktestEngine`
  when two strategies share a name.
- **More precise level formatting** in `DrawdownDCA.name()` (e.g.
  `1.5%` instead of `2%`).
- **Explicit tie handling** in win count.

### Engineering

- **Automated tests** (e.g. `pytest`): known-answer tests for each
  strategy, the simulator, CAGR calculation, window creation and level
  validation, plus a regression test against a stored trace.
- **Packaging** with a `pyproject.toml` and a pinned dependency list.
- **Configurable data frequency.** Generalise `ContributionFrequency`
  if daily or monthly data is ever needed.
- **`live` module.** Apply a chosen strategy to current market data to
  suggest this week's contribution.
