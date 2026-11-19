# BAB P22 WP2 — nonlinear market-impact surface on the WP3 exposure series

Schema `bab_p22.impact_surface/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; component: `market_impact`; model: per-period impact drag = coefficient * turnover ** 1.5 (square-root market impact, participation to the 3/2 power); coefficient grid: [0.0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]; trading days: 252.

| variant | weighting | active_rows | gross_sharpe | gross_turnover_mean | impact_exposure_mean | gross_final_cumulative | censored | censor_reason |
|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 7.034781 | 0.009797 | 0.002701 | 1.167118 | False | None |
| planted | rank | 541 | 44.378201 | 0.007204 | 0.006392 | 11401.093638 | False | None |
| null | equal | 541 | 0.639801 | 0.009797 | 0.002701 | 1.013905 | False | None |
| null | rank | 541 | 0.649924 | 0.007204 | 0.006392 | 1.049395 | False | None |

| variant | weighting | component | level | costed_sharpe | cost_drag_mean | total_cost | final_cumulative |
|---|---|---|---|---|---|---|---|
| planted | equal | market_impact | 0.0 | 7.034781 | 0.0 | 0.0 | 1.167118 |
| planted | equal | market_impact | 0.02 | 3.763395 | 5.4e-05 | 0.032418 | 1.129761 |
| planted | equal | market_impact | 0.05 | 1.167251 | 0.000135 | 0.081044 | 1.075471 |
| planted | equal | market_impact | 0.1 | -0.062016 | 0.00027 | 0.162088 | 0.989475 |
| planted | equal | market_impact | 0.2 | -0.717923 | 0.00054 | 0.324177 | 0.833239 |
| planted | equal | market_impact | 0.5 | -1.116263 | 0.001351 | 0.810441 | 0.471526 |
| planted | equal | market_impact | 1.0 | -1.249026 | 0.002701 | 1.620883 | 0.124562 |
| planted | rank | market_impact | 0.0 | 44.378201 | 0.0 | 0.0 | 11401.093638 |
| planted | rank | market_impact | 0.02 | 37.232543 | 0.000128 | 0.07671 | 10530.799945 |
| planted | rank | market_impact | 0.05 | 24.951852 | 0.00032 | 0.191775 | 9238.335098 |
| planted | rank | market_impact | 0.1 | 14.564397 | 0.000639 | 0.383549 | 7118.487825 |
| planted | rank | market_impact | 0.2 | 7.445557 | 0.001278 | 0.767098 | 3004.998876 |
| planted | rank | market_impact | 0.5 | 2.652254 | 0.003196 | 1.917745 | -8369.885186 |
| planted | rank | market_impact | 1.0 | 0.993625 | 0.006392 | 3.83549 | -24385.695661 |
| null | equal | market_impact | 0.0 | 0.639801 | 0.0 | 0.0 | 1.013905 |
| null | equal | market_impact | 0.02 | -0.578003 | 5.4e-05 | 0.032418 | 0.981449 |
| null | equal | market_impact | 0.05 | -1.072364 | 0.000135 | 0.081044 | 0.934281 |
| null | equal | market_impact | 0.1 | -1.241371 | 0.00027 | 0.162088 | 0.859567 |
| null | equal | market_impact | 0.2 | -1.316368 | 0.00054 | 0.324177 | 0.723829 |
| null | equal | market_impact | 0.5 | -1.356794 | 0.001351 | 0.810441 | 0.409589 |
| null | equal | market_impact | 1.0 | -1.3694 | 0.002701 | 1.620883 | 0.10819 |
| null | rank | market_impact | 0.0 | 0.649924 | 0.0 | 0.0 | 1.049395 |
| null | rank | market_impact | 0.02 | -0.201427 | 0.000128 | 0.07671 | 0.969222 |
| null | rank | market_impact | 0.05 | -0.490675 | 0.00032 | 0.191775 | 0.850177 |
| null | rank | market_impact | 0.1 | -0.591459 | 0.000639 | 0.383549 | 0.654977 |
| null | rank | market_impact | 0.2 | -0.639653 | 0.001278 | 0.767098 | 0.276393 |
| null | rank | market_impact | 0.5 | -0.667427 | 0.003196 | 1.917745 | -0.769021 |
| null | rank | market_impact | 1.0 | -0.676461 | 0.006392 | 3.83549 | -2.236534 |

| variant | weighting | component | monotonic_sharpe | period_wise_non_increasing |
|---|---|---|---|---|
| planted | equal | market_impact | True | True |
| planted | rank | market_impact | True | True |
| null | equal | market_impact | True | True |
| null | rank | market_impact | True | True |

Per-book costed Sharpe is non-increasing in the impact-coefficient level (monotonic_sharpe = true), and every period's costed return is non-increasing in the level (period_wise_non_increasing = true), since each drag is a non-negative coefficient times a non-negative turnover**1.5 exposure. At coefficient == 0 the surface reproduces the gross baseline exactly. Censored books carry a documented censor_reason and never a zero tolerance.
