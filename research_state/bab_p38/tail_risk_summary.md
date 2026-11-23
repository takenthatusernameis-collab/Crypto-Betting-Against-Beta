# BAB P38 WP2 - Tail-Risk & Drawdown Characterization (CVaR / Expected Shortfall)

Schema `bab_p38.tail_risk/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence.

**Tail-risk status:** **ALL_NEUTRALITY_OK**

## Setup

- Seeds: 8 (base=20261120, increment=1009)
- beta_window: 90d, quantile: 0.300000
- Gross transaction_costs: 0.000000, costed transaction_costs: 0.001000
- weighting: equal, beta_neutral: True, dollar_neutral: True

## Definitions

- `cvar_95`: mean of the worst 5% of returns (expected shortfall @95%)
- `cvar_99`: mean of the worst 1% of returns (expected shortfall @99%)
- `var_95`: 5th percentile of returns (value at risk @95%)
- `var_99`: 1st percentile of returns (value at risk @99%)
- `expected_shortfall_975`: mean of the worst 2.5% of returns (expected shortfall @97.5%)
- `worst_day_return`: minimum single-period return
- `best_day_return`: maximum single-period return
- `skew`: population skewness of returns
- `excess_kurtosis`: population excess kurtosis (raw kurtosis - 3)
- `tail_asymmetry`: (|left 5% tail mean| - |right 5% tail mean|) / (|left 5% tail mean| + |right 5% tail mean|); in [-1, +1], positive = heavier left tail
- `conditional_drawdown_95`: mean of the worst 5% of the per-period drawdown series (conditional drawdown at risk @95%)
- `max_drawdown`: minimum of the per-period drawdown series
- `sharpe`: annualized Sharpe ratio of the strategy return series

## Gross (structural)

transaction_costs = 0.000000; cells: 8 total, 8 OK, 0 neutrality violations, 0 errors.

| Tail metric | mean | min (worst) | max |
|---|---|---|---|
| cvar_95 | -0.000863 | -0.000936 | -0.000784 |
| cvar_99 | -0.001100 | -0.001252 | -0.000932 |
| expected_shortfall_975 | -0.000972 | -0.001083 | -0.000858 |
| worst_day_return | -0.001263 | -0.001490 | -0.001008 |
| skew | -0.015498 | -0.191856 | 0.226654 |
| excess_kurtosis | 0.160747 | -0.216511 | 1.238815 |
| tail_asymmetry | -0.000493 | -0.105366 | 0.084234 |
| conditional_drawdown_95 | -0.007803 | -0.013260 | -0.002881 |
| max_drawdown | -0.008564 | -0.013893 | -0.003722 |

## Costed (10 bps)

transaction_costs = 0.001000; cells: 8 total, 8 OK, 0 neutrality violations, 0 errors.

| Tail metric | mean | min (worst) | max |
|---|---|---|---|
| cvar_95 | -0.000876 | -0.000945 | -0.000805 |
| cvar_99 | -0.001122 | -0.001263 | -0.000984 |
| expected_shortfall_975 | -0.000988 | -0.001092 | -0.000888 |
| worst_day_return | -0.001294 | -0.001499 | -0.001183 |
| skew | -0.021136 | -0.234482 | 0.204963 |
| excess_kurtosis | 0.163182 | -0.266321 | 1.144439 |
| tail_asymmetry | 0.013265 | -0.087612 | 0.096093 |
| conditional_drawdown_95 | -0.009169 | -0.015020 | -0.003048 |
| max_drawdown | -0.009961 | -0.015790 | -0.003875 |

---

## Interpretation

- CVaR@95 / CVaR@99 / expected shortfall are (negative) average losses in the worst 5% / 1% / 2.5% of periods. More negative = fatter left tail.
- tail_asymmetry in [-1, +1]: positive means the left tail dominates the right (the short-high-beta / short-vol crash signature); near zero means symmetric.
- excess_kurtosis > 0 means fat tails relative to a Gaussian; skew < 0 means a long left tail.
- conditional_drawdown_95 is the average of the worst 5% of per-period drawdowns; max_drawdown is the single worst peak-to-trough.
- Every seed cell asserts model beta <= 1e-3, dollar <= 1e-9, realized |beta| <= 0.15; tail_risk_status is ALL_NEUTRALITY_OK only if all cells pass.

Synthetic-provenance caveat: results are on the committed synthetic wide universe (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
