# BAB P38 WP1 — Deflated / Multiple-Testing-Adjusted Significance

Schema `bab_p38.deflated_significance/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Campaign verdict:** **SURVIVES_DEFLATION**
**Reason:** Shipped default and best in-sample config both have DSR >= 0.5 after deflation over n_trials_total=552.

## Trial enumeration (read-only from committed artifacts)

Total effective number of trials searched across the campaign lineage: **552**.

| Campaign / artifact | Trials |
|---|---|
| P20_in_sample_grid | 80 |
| bab_p25/promotion_bakeoff | 0 |
| bab_p25/walk_forward_rank | 0 |
| bab_p26/rank_capacity | 0 |
| bab_p26/regime_stress | 0 |
| bab_p26/signal_null_battery | 0 |
| bab_p35/estimator_bakeoff_summary | 80 |
| bab_p35/signal_stability_summary | 96 |
| bab_p36/rank_weighted_summary | 8 |
| bab_p36/walk_forward_summary | 80 |
| bab_p37/capacity_summary | 8 |
| bab_p37/cost_surface_summary | 192 |
| bab_p37/turnover_summary | 8 |

Each term traces to a committed JSON leaf (P20 grid configurations plus distinct config cells evaluated across P25-P37 variant artifacts). Nothing is invented.

## Best in-sample config (from committed P20 sweep)

| Parameter | Value |
|---|---|
| beta_window | 180 |
| long_quantile | 0.200000 |
| short_quantile | 0.200000 |
| beta_neutral | True |
| transaction_costs | 0.000000 |
| weighting | equal |
| in-sample Sharpe (P20 sweep) | 1.216780 |
| in-sample wealth (P20 sweep) | 1.778458 |

## Results — shipped default vs best in-sample config

### Shipped Default

- beta_window: 90, quantile: 0.300000
- n_seed_cells: 8, n_ok_cells: 8
- mean_sharpe: 0.367434
- total_periods: 2712
- n_trials (deflation): 552
- sigma0: 0.3380294313
- gamma: -0.011292
- kappa: 3.163111
- DSR: 0.920930
- PSR: 1.000000
- trials-adjusted p-value: 0.079070
- min backtest length for PSR=0.50: 9
- survives_deflation: True
- verdict: **SURVIVES_DEFLATION**

### Best Insample Config

- beta_window: 180, quantile: 0.200000
- n_seed_cells: 8, n_ok_cells: 8
- mean_sharpe: 0.128445
- total_periods: 2712
- n_trials (deflation): 552
- sigma0: 0.3267936648
- gamma: -0.040693
- kappa: 2.892648
- DSR: 0.944379
- PSR: 1.000000
- trials-adjusted p-value: 0.055621
- min backtest length for PSR=0.50: 62
- survives_deflation: True
- verdict: **SURVIVES_DEFLATION**

---

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for the multiple trials searched (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero (analytical, Bailey & Lopez de Prado).
- trials-adjusted p-value = 1 - DSR: probability the result is noise given the number of trials.
- min backtest length for PSR=0.50: approximate backtest length T at which the standard error of Sharpe equals the observed Sharpe (PSR = 0.50 boundary).

Synthetic-provenance caveat: results are on the committed synthetic wide universe (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
