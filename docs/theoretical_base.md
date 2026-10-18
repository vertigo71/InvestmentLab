# Theoretical base

Background on the calculations used by InvestmentLab, with derivations
and worked examples. The [README](../README.md) describes how to use
the project; this document explains why the formulas are what they
are.

---

## Total return from price and dividends

A **total return** series measures the growth of an investment that
reinvests every dividend in the same asset. It is built from the price
and the dividend of each period.

### The growth factor

For each period `t`, with price `p[t]` and dividend per share `d[t]`
received in that period:

```
growth[t] = (p[t] + d[t]) / p[t-1]
```

The total return index is the cumulative product of these factors,
starting at any base value (for example the first price):

```
TR[0] = p[0]
TR[t] = TR[t-1] × growth[t]
```

The formula only uses the price and the dividend of **one share**, yet
it gives the growth of a portfolio whose number of shares keeps
increasing as dividends are reinvested. The derivation below shows
why.

### Derivation

Start with one share at price `p0`. Each period, every share pays the
dividend, and the dividend is reinvested at the current price.

| Period | Price | Dividend per share | Shares after reinvesting          | Portfolio value                   | Growth                            |
|--------|-------|--------------------|-----------------------------------|-----------------------------------|-----------------------------------|
| 0      | p0    | –                  | N0 = 1                            | V0 = p0                           |                                   |
| 1      | p1    | d1                 | N1 = 1 + d1/p1                    | V1 = p1 · N1 = p1 + d1            | V1 / V0 = (p1 + d1) / p0          |
| 2      | p2    | d2                 | N2 = N1 · (1 + d2/p2)             | V2 = p2 · N2 = N1 · (p2 + d2)     | V2 / V1 = (p2 + d2) / p1          |
| t      | p[t]  | d[t]               | N[t] = N[t-1] · (1 + d[t]/p[t])   | V[t] = N[t-1] · (p[t] + d[t])     | V[t] / V[t-1] = (p[t] + d[t]) / p[t-1] |

In every row, the number of shares of the previous period appears in
both the current and the previous value, and cancels out in the
growth. The steps below show it in detail.

**Period 1.** The single share is worth `p1` and pays `d1`. The
dividend buys `d1 / p1` new shares at the current price:

```
N1 = 1 + d1/p1
V1 = p1 · N1 = p1 + d1
growth[1] = V1 / V0 = (p1 + d1) / p0
```

**Period 2.** Now there are `N1` shares, and **each one** pays `d2`.
The total dividend is `N1 · d2`, which buys `N1 · d2 / p2` new shares:

```
N2 = N1 + N1 · d2/p2 = N1 · (1 + d2/p2)
V2 = p2 · N2 = N1 · (p2 + d2)
```

The value at the end of period 1 can also be written with `N1`:

```
V1 = p1 · N1
```

So the growth in period 2 is:

```
growth[2] = V2 / V1 = N1 · (p2 + d2) / (N1 · p1) = (p2 + d2) / p1
```

`N1` cancels out. The same happens in every period:

```
growth[t] = V[t] / V[t-1]
          = N[t-1] · (p[t] + d[t]) / (N[t-1] · p[t-1])
          = (p[t] + d[t]) / p[t-1]
```

The portfolio grows by the same factor as a single share, whatever
the number of shares. That is why the total return series can be
built without tracking the shares.

### Expanded version of period 2

The same result, without factoring out `N1`:

```
V2 = p2 · (1 + d1/p1) · (1 + d2/p2)
   = p2 + p2·d1/p1 + d2 + d1·d2/p1

V2 / V1 = (p2 + p2·d1/p1 + d2 + d1·d2/p1) / (p1 + d1)

        = (1/p1) · (p1·p2 + d1·p2 + d2·p1 + d1·d2) / (p1 + d1)

        = (1/p1) · (p2·(p1 + d1) + d2·(p1 + d1)) / (p1 + d1)

        = (1/p1) · (p2 + d2)·(p1 + d1) / (p1 + d1)

        = (p2 + d2) / p1
```

### A common mistake: adding instead of multiplying

It is tempting to count the shares by adding the new ones bought in
each period:

```
N2 = 1 + d1/p1 + d2/p2          ← wrong
```

This assumes that only the original share pays `d2`. Expanding the
correct expression shows the missing term:

```
N2 = (1 + d1/p1) · (1 + d2/p2)
   = 1 + d1/p1 + d2/p2 + (d1/p1) · (d2/p2)
```

The last term is the dividend paid in period 2 by the shares bought
with the dividend of period 1: the compounding effect ("interest on
interest"). It is small for one period, but over decades it is what
makes dividend reinvestment matter.

### Numerical example

Prices 100, 110 and 140, with dividends of 10 and 15 per share
(exaggerated to make the effect visible):

| Period | Price | Dividend | New shares                   | Shares | Value                  | Growth          |
|--------|-------|----------|------------------------------|--------|------------------------|-----------------|
| 0      | 100   | –        | –                            | 1.0000 | 100.00                 |                 |
| 1      | 110   | 10       | 10 / 110 = 0.0909            | 1.0909 | 1.0909 × 110 = 120.00  | 120 / 100 = 1.2000 |
| 2      | 140   | 15       | 1.0909 × 15 / 140 = 0.1169   | 1.2078 | 1.2078 × 140 = 169.09  | 155 / 110 = 1.4091 |

Check: `100 × 1.2000 × 1.4091 = 169.09`.

A frequent slip is to compute period 2 as `(140 + 15) / 120 = 1.2917`.
The 155 is the value of **one** share with its dividend, while 120 is
the value of **1.0909** shares, so the two are not comparable. The
formula always compares one share with itself: 110 before, 155 after.

---

## Shiller's monthly total return

Shiller's `ie_data.xls` provides, for each month since January 1871:

| Column | Meaning                                                                                                                            | Example (April 2025)  |
|--------|------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| `Date` | Year and month as a number. `1871.01` is January, `1871.1` is October (Excel drops the trailing zero).                             | `2025.04`             |
| `P`    | S&P Composite price: **monthly average** of daily closes, not the end-of-month close.                                              | `5369.50`             |
| `D`    | Dividends of the last 12 months, in index points. Since 1926 interpolated from S&P quarterly totals; before 1926 from annual data. | `76.55` (1.43% yield) |

`D` is an annual amount, so the dividend received in one month is
`D / 12`. The growth factor becomes:

```
growth[t] = (P[t] + D[t] / 12) / P[t-1]
```

In pandas, as in `tools/shiller_converter.py`:

```python
growth = (data["price"] + data["dividend"] / 12) / data["price"].shift(1)
total_return = data["price"].iloc[0] * growth.fillna(1.0).cumprod()
```

### Worked example (first months of 1871)

Monthly dividend: `0.26 / 12 = 0.02167`.

| Row | Date    | P    | D    | P.shift(1) | growth  | after fillna | cumprod | close (CSV) |
|-----|---------|------|------|------------|---------|--------------|---------|-------------|
| 0   | 1871-01 | 4.44 | 0.26 | NaN        | NaN     | 1.00000      | 1.00000 | 4.4400      |
| 1   | 1871-02 | 4.50 | 0.26 | 4.44       | 1.01839 | 1.01839      | 1.01839 | 4.5217      |
| 2   | 1871-03 | 4.61 | 0.26 | 4.50       | 1.02926 | 1.02926      | 1.04819 | 4.6540      |
| 3   | 1871-04 | 4.74 | 0.26 | 4.61       | 1.03290 | 1.03290      | 1.08268 | 4.8071      |

- `shift(1)` moves the price down one row, so each month sees the
  previous price. The first row has none and gets `NaN`.
- `growth` for February: `(4.50 + 0.02167) / 4.44 = 1.01839`, a 1.84%
  gain, of which 1.35% comes from the price and the rest from the
  dividend.
- `fillna(1.0)` sets the first month's factor to 1: it is the starting
  point.
- `cumprod()` multiplies all factors up to each row:
  `1.01839 × 1.02926 = 1.04819`.
- `iloc[0]` is the first price (4.44). Multiplying by it makes the
  series start at the index level, so the first row matches the
  spreadsheet.

After three months the total return series is up 8.27%, against 6.76%
for the price alone.

### Nominal versus real

The file also contains a *Real Total Return Price* column. It is a
total return series too, but **inflation-adjusted** with the CPI.
InvestmentLab uses a **nominal** series instead, so it is comparable
with Yahoo prices, cash and interest rates.

Multiplying the real series by the CPI of the same month converts it
back to nominal (up to a constant scale, which does not affect
returns). From March to April 2025:

| Method                     | Calculation                                          | Monthly factor |
|----------------------------|------------------------------------------------------|----------------|
| Real total return × CPI    | (3,781,091.48 / 4,010,249.00) × (320.80 / 319.80)    | 0.94581        |
| `(P + D/12) / P[t-1]`      | (5,369.50 + 76.55 / 12) / 5,683.98                   | 0.94579        |

The small difference comes from how Shiller distributes the dividend
within the month.

### Approximations

- **Prices are monthly averages**, which smooths crash lows.
- **Dividends are interpolated** and received as one twelfth of the
  annual amount each month, while companies mostly pay quarterly.
- **Dividends are reinvested at the monthly average price.**
- **Gross dividends in USD**, with no taxes or costs.
