# BAB P21 WP2 — significance + deflation on the planted universe

Schema `bab_p21.significance/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; bootstrap seed 20261119; 2000 resamples, block length 20; P20 grid candidates 40; nominal slack 0.05.

Null calibration: no null book is significant at level nominal_slack, so the false-positive rate is bounded by the documented slack. Planted detection: both planted books are significant with bootstrap CIs excluding zero.

| variant | weighting | oos_sharpe | p_value | significant | critical_sharpe | ci_excludes_zero | dsr | dsr_p_value |
|---|---|---|---|---|---|---|---|---|
| planted | equal | 7.034781 | 0.0 | True | 1.278258 | True | 0.905272 | 0.094728 |
| planted | rank | 44.378201 | 0.0 | True | 9.279902 | True | 0.998329 | 0.001671 |
| null | equal | 0.639801 | 0.1635 | False | 1.042214 | False | 0.923379 | 0.076621 |
| null | rank | 0.649924 | 0.268 | False | 1.435861 | False | 0.926802 | 0.073198 |

null_calibrated: True
planted_detected: True
null_max_p_value: 0.268

The deflated Sharpe is reported for completeness; the calibration and detection claims rest on the bootstrap p-value test above.
