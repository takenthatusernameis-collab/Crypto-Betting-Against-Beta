# P26 WP1 Regime-Conditional Rank Stress

**Falsification gate passed:** False

**Seed:** 20261120 | **Folds:** 5 | Train: 180 | Test: 40 | Beta Window: 90 | Min Obs: 60 | Vol Window: 60 | Quantiles: 0.3/0.3 | Rank Min Leg Beta: 0.2 | Rank Max Gross: 4.0 | Costs: 0.001

**Fixture SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b

## Regime Split

| Regime | Folds Assigned | Fold Indices |
|---|---|---|
| calm | 3 | [0, 3, 4] |
| stress | 2 | [1, 2] |

## Per-Regime Mean OOS Sharpe

| Regime | Weighting | Mean OOS Sharpe | N Folds |
|---|---|---|---|
| calm | equal | 0.845096 | 3 |
| calm | rank | 0.817343 | 3 |
| stress | equal | -0.841977 | 2 |
| stress | rank | -0.132738 | 2 |

## Falsification Gate Assertions

| Assertion | Passed | Value |
|---|---|---|
| A: rank mean OOS Sharpe > 0 in calm | True | 0.817343 |
| B: rank mean OOS Sharpe < equal in stress | False | rank=-0.132738 < equal=-0.841977 |
| Falsification gate passed | False | - |

## Per-Fold Detail

| Regime | Fold | Weighting | Test Start | Test End | OOS Sharpe | Portfolio Beta | Nonflat Rows |
|---|---|---|---|---|---|---|---|
| calm | 0 | equal | 180 | 220 | 2.464833 | -0.000024 | 40 |
| calm | 3 | equal | 300 | 340 | -3.020664 | 0.000026 | 40 |
| calm | 4 | equal | 340 | 380 | 3.091118 | 0.000072 | 40 |
| calm | 0 | rank | 180 | 220 | 0.256134 | -0.000000 | 40 |
| calm | 3 | rank | 300 | 340 | 0.931271 | 0.000000 | 40 |
| calm | 4 | rank | 340 | 380 | 1.264624 | -0.000000 | 40 |
| stress | 1 | equal | 220 | 260 | -0.321648 | 0.000008 | 40 |
| stress | 2 | equal | 260 | 300 | -1.362306 | -0.000074 | 40 |
| stress | 1 | rank | 220 | 260 | 0.539000 | -0.000000 | 40 |
| stress | 2 | rank | 260 | 300 | -0.804475 | 0.000000 | 40 |
