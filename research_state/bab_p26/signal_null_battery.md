# P26 WP0 Signal vs Null Battery

**Verdict:** NO-SIGNAL

**Seed:** 20261120 | **Folds:** 5 | Train: 180 | Test: 40 | Beta Window: 90 | Min Obs: 60 | Quantiles: 0.3/0.3 | Rank Min Leg Beta: 0.2 | Rank Max Gross: 4.0 | Costs: 0.001 | Null Reps: 1000 | p-level: 0.05

**Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b

## Observed Mean OOS Sharpe

| Weighting | Mean OOS Sharpe |
|---|---|
| equal | 0.170267 |
| rank | 0.437311 |

## Null Distribution Statistics

| Weighting | Observed | Null Mean | Null Std | Null Min | Null Max | Z-Score | P-Value | Percentile |
|---|---|---|---|---|---|---|---|---|
| equal | 0.170267 | -0.348462 | 1.298155 | -4.004163 | 3.426797 | 0.399590 | 0.358641 | 64.200000 |
| rank | 0.437311 | -0.348462 | 1.298155 | -4.004163 | 3.426797 | 0.605300 | 0.285714 | 71.500000 |

## Per-Fold Observed OOS Sharpe

| Fold | Test Start | Test End | Equal OOS Sharpe | Rank OOS Sharpe |
|---|---|---|---|---|
| 0 | 180 | 220 | 2.464833 | 0.256134 |
| 1 | 220 | 260 | -0.321648 | 0.539000 |
| 2 | 260 | 300 | -1.362306 | -0.804475 |
| 3 | 300 | 340 | -3.020664 | 0.931271 |
| 4 | 340 | 380 | 3.091118 | 1.264624 |
