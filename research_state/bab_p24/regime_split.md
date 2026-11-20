# BAB P24 WP1 — regime-split stress

Schema `bab_p24.regime_split/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; charter schema `bab_p24.charter/1`; regimes ['calm', 'stress'].
Regime rule: benchmark rolling vol (window=20) percentile split; calm <= 0.333 quantile, stress >= 0.667 quantile; middle excluded; causal (no lookahead).

| regime | weighting | variant | recovery | full_panel | retention | sharpe | beta_exposure | regime_rows | active_rows | total_rows | active_frac | min_leg_beta | gross_max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| calm | equal | planted | 0.000262 | 0.000261 | 1.003831 | 4.553331 | 0.037119 | 219 | 213 | 600 | 0.355 | 0.0 | 0.0 |
| calm | rank | planted | 0.017356 | 0.01736 | 0.99977 | 11.59948 | 0.012578 | 219 | 213 | 600 | 0.355 | 0.510833 | 2.414949 |
| stress | equal | planted | 0.000251 | 0.000261 | 0.961686 | 3.480383 | 0.037776 | 206 | 179 | 600 | 0.298333 | 0.0 | 0.0 |
| stress | rank | planted | 0.017311 | 0.01736 | 0.997177 | 10.221435 | 0.011091 | 206 | 179 | 600 | 0.298333 | 0.507692 | 2.403391 |
| calm | equal | null | 0.0 | 0.0 | 0.0 | 0.76551 | 0.037119 | 219 | 213 | 600 | 0.355 | 0.0 | 0.0 |
| calm | rank | null | 0.0 | 0.0 | 0.0 | 1.304143 | 0.012578 | 219 | 213 | 600 | 0.355 | 0.510833 | 2.414949 |
| stress | equal | null | 0.0 | 0.0 | 0.0 | 0.234073 | 0.037776 | 206 | 179 | 600 | 0.298333 | 0.0 | 0.0 |
| stress | rank | null | 0.0 | 0.0 | 0.0 | -0.366438 | 0.011091 | 206 | 179 | 600 | 0.298333 | 0.507692 | 2.403391 |

Regime coverage: 600 rows; {'calm': 219, 'stress': 206} classified; 0 overlapping; 175 middle/unclassified.

## Regime zero-reference (full panel, matches P21 at 6 dp)

| variant | weighting | committed_p21_recovery | regime_zero_recovery | matches_at_6dp |
|---|---|---|---|---|
| planted | equal | 0.000261 | 0.000261 | True |
| planted | rank | 0.01736 | 0.01736 | True |
| null | equal | 0.0 | 0.0 | True |
| null | rank | 0.0 | 0.0 | True |
