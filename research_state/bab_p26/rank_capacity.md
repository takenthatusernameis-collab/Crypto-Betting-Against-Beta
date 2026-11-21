# P26 WP2 Capacity & Turnover of Rank Book

**Verdict:** rank survives capacity

**Seed:** 20261120 | **Folds:** 5 | Train: 180 | Test: 40 | Beta Window: 90 | Min Obs: 60 | Quantiles: 0.3/0.3 | Rank Min Leg Beta: 0.2 | Rank Max Gross (default): 4.0 | Costs: 0.001 | Gross Caps: [1.0, 2.0, 3.0, 4.0] | Rebalance Freqs: ['daily', 'weekly', 'monthly']

**Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b

## Aggregate

| key | value |
|---|---|
| gross_caps | 1.000000, 2.000000, 3.000000, 4.000000 |
| rebalance_freqs | daily, weekly, monthly |
| rank_min_leg_beta | 0.200000 |
| rank_max_gross_default | 4.000000 |
| cells_evaluated | 12.000000 |
| candidates_evaluated | 120.000000 |
| rank_survives_capacity | True |
| verdict | rank survives capacity |
| default_cell_gross_cap | 4.000000 |
| default_cell_rebalance_freq | daily |
| rank_beats_equal_default_cell | True |

| cells_evaluated | 12 |
| last_cell_index | 11 |

## Per-Cell Results (rank vs equal)

| Cell | Gross Cap | Rebalance | Weighting | Mean OOS Sharpe | Mean OOS Turnover | Mean OOS Wealth | Mean Portfolio Beta | Break-Even AUM |
|---|---|---|---|---|---|---|---|---|
| 0 | 1.000000 | daily | equal | 0.170267 | 0.013120 | 0.999998 | 0.000002 | None |
| 0 | 1.000000 | daily | rank | 0.437311 | 0.013610 | 1.002108 | 0.000000 | 1633086273.923364 |
| 0 | 1.000000 | daily | DELTA | 0.267044 | 0.000490 | 0.002110 | - | - |
| 1 | 1.000000 | weekly | equal | 0.390626 | 0.007066 | 1.000217 | -0.000045 | 50071746.804561 |
| 1 | 1.000000 | weekly | rank | 0.496973 | 0.006666 | 1.002453 | -0.000156 | 8932036317.943226 |
| 1 | 1.000000 | weekly | DELTA | 0.106347 | -0.000400 | 0.002236 | - | - |
| 2 | 1.000000 | monthly | equal | 0.067110 | 0.004624 | 0.999925 | 0.000172 | None |
| 2 | 1.000000 | monthly | rank | 0.518086 | 0.003601 | 1.002528 | -0.000677 | 32582204902.970184 |
| 2 | 1.000000 | monthly | DELTA | 0.450976 | -0.001023 | 0.002603 | - | - |
| 3 | 2.000000 | daily | equal | 0.170267 | 0.013120 | 0.999998 | 0.000002 | None |
| 3 | 2.000000 | daily | rank | 0.437311 | 0.013610 | 1.002108 | 0.000000 | 1633086273.923364 |
| 3 | 2.000000 | daily | DELTA | 0.267044 | 0.000490 | 0.002110 | - | - |
| 4 | 2.000000 | weekly | equal | 0.390626 | 0.007066 | 1.000217 | -0.000045 | 50071746.804561 |
| 4 | 2.000000 | weekly | rank | 0.496973 | 0.006666 | 1.002453 | -0.000156 | 8932036317.943226 |
| 4 | 2.000000 | weekly | DELTA | 0.106347 | -0.000400 | 0.002236 | - | - |
| 5 | 2.000000 | monthly | equal | 0.067110 | 0.004624 | 0.999925 | 0.000172 | None |
| 5 | 2.000000 | monthly | rank | 0.518086 | 0.003601 | 1.002528 | -0.000677 | 32582204902.970184 |
| 5 | 2.000000 | monthly | DELTA | 0.450976 | -0.001023 | 0.002603 | - | - |
| 6 | 3.000000 | daily | equal | 0.170267 | 0.013120 | 0.999998 | 0.000002 | None |
| 6 | 3.000000 | daily | rank | 0.437311 | 0.013610 | 1.002108 | 0.000000 | 1633086273.923364 |
| 6 | 3.000000 | daily | DELTA | 0.267044 | 0.000490 | 0.002110 | - | - |
| 7 | 3.000000 | weekly | equal | 0.390626 | 0.007066 | 1.000217 | -0.000045 | 50071746.804561 |
| 7 | 3.000000 | weekly | rank | 0.496973 | 0.006666 | 1.002453 | -0.000156 | 8932036317.943226 |
| 7 | 3.000000 | weekly | DELTA | 0.106347 | -0.000400 | 0.002236 | - | - |
| 8 | 3.000000 | monthly | equal | 0.067110 | 0.004624 | 0.999925 | 0.000172 | None |
| 8 | 3.000000 | monthly | rank | 0.518086 | 0.003601 | 1.002528 | -0.000677 | 32582204902.970184 |
| 8 | 3.000000 | monthly | DELTA | 0.450976 | -0.001023 | 0.002603 | - | - |
| 9 | 4.000000 | daily | equal | 0.170267 | 0.013120 | 0.999998 | 0.000002 | None |
| 9 | 4.000000 | daily | rank | 0.437311 | 0.013610 | 1.002108 | 0.000000 | 1633086273.923364 |
| 9 | 4.000000 | daily | DELTA | 0.267044 | 0.000490 | 0.002110 | - | - |
| 10 | 4.000000 | weekly | equal | 0.390626 | 0.007066 | 1.000217 | -0.000045 | 50071746.804561 |
| 10 | 4.000000 | weekly | rank | 0.496973 | 0.006666 | 1.002453 | -0.000156 | 8932036317.943226 |
| 10 | 4.000000 | weekly | DELTA | 0.106347 | -0.000400 | 0.002236 | - | - |
| 11 | 4.000000 | monthly | equal | 0.067110 | 0.004624 | 0.999925 | 0.000172 | None |
| 11 | 4.000000 | monthly | rank | 0.518086 | 0.003601 | 1.002528 | -0.000677 | 32582204902.970184 |
| 11 | 4.000000 | monthly | DELTA | 0.450976 | -0.001023 | 0.002603 | - | - |

## Capacity Break-Even Model

Square-root impact estimate (not market evidence):
- impact_cost(AUM) = 1e-4 * turnover * sqrt(AUM / 1,000,000)
- break-even AUM solves impact_cost(AUM) = net mean OOS daily return
- None when net mean OOS daily return <= 0 or turnover == 0

## Verdict Rule

rank survives capacity iff rank mean OOS Sharpe > equal mean OOS Sharpe at the default cell (gross_cap=4.0, rebalance_freq=daily); otherwise rank does not survive capacity. Data-driven, not a forced outcome.
