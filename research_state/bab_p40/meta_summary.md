# BAB P40 — Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict

Schema `bab_p40.meta_analysis/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Campaign verdict:** **DOES_NOT_REPLICATE**
**Reason:** 0 of 4 fixtures replicate the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over n_trials_total=552; consolidated verdict DOES_NOT_REPLICATE.

## Setup

- Fixtures: 4 deterministic synthetic wide universes, 8 seeds each, 32 cells total
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True, transaction_costs: 0.000000
- DSR survive threshold: 0.500000 (DSR >= 0.50 means more likely than not genuine skill after deflation)
- Bootstrap: 2000 resamples, block length 20, seed 20261123

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Fixture grid (fixed; not tuned)

| Fixture | Base seed | Increment | Idio vol | Beta range | Assets | Replicates P38 pooled | Role |
|---|---|---|---|---|---|---|---|
| F1_PRIMARY | 20261120 | 1009 | 0.003000 | [0.350000, 1.900000] | 40 | False | P38/P39 WP1 primary parameterization |
| F2_P39_SECOND | 20270101 | 9973 | 0.006000 | [0.200000, 2.400000] | 32 | False | P39 WP2 second parameterization |
| F3_LOW_VOL_WIDE | 20280201 | 10009 | 0.002000 | [0.250000, 2.100000] | 36 | False | Low-idio, wider beta cross-section |
| F4_HIGH_VOL_NARROW | 20290301 | 10007 | 0.008000 | [0.400000, 1.700000] | 28 | False | High-idio, narrower beta cross-section |

- BTC prices read-only from tests/fixtures/wide_bab_universe.csv (the same deterministic random-walk fixture as P38/P39).
- Asset returns = beta * BTC_return + idio, seeded per fixture; neutrality invariants (model beta <= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15) checked at every cell.
- Not real market data; not market profitability evidence.

## Per-cell results (pooled; no regime split)

| Fixture | Seed | N periods | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | 20261120 | 339 | 0.760518 | 0.944013 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20262129 | 339 | 0.320261 | 0.933528 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20263138 | 339 | 1.865525 | 0.926111 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20264147 | 339 | -0.129599 | 0.238889 | 0.008562 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20265156 | 339 | -0.531831 | 0.109034 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20266165 | 339 | 0.967765 | 0.925842 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20267174 | 339 | -0.845875 | 0.081837 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20268183 | 339 | 0.532712 | 0.938391 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20270101 | 339 | -0.861582 | 0.069944 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20280074 | 339 | 0.487880 | 0.923431 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20290047 | 339 | -0.641189 | 0.082488 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20300020 | 339 | 0.327766 | 0.923706 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20309993 | 339 | -1.107029 | 0.073579 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20319966 | 339 | -0.769760 | 0.084260 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20329939 | 339 | -1.359181 | 0.080687 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20339912 | 339 | 2.176458 | 0.928768 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20280201 | 339 | -0.535429 | 0.095286 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20290210 | 339 | 0.052140 | 0.958546 | 0.831125 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20300219 | 339 | -0.533620 | 0.108983 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20310228 | 339 | 0.494379 | 0.943269 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20320237 | 339 | -0.288504 | 0.122799 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20330246 | 339 | 1.005151 | 0.936855 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20340255 | 339 | 1.051665 | 0.930727 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20350264 | 339 | 0.214326 | 0.948212 | 0.999960 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20290301 | 339 | 1.313904 | 0.929730 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20300308 | 339 | 0.210269 | 0.952911 | 0.999946 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20310315 | 339 | -0.069405 | 0.318851 | 0.101022 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20320322 | 339 | -0.456647 | 0.073224 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20330329 | 339 | -1.043952 | 0.073906 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20340336 | 339 | -0.006414 | 0.794795 | 0.453067 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20350343 | 339 | -0.268372 | 0.151619 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20360350 | 339 | -1.004819 | 0.075987 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |

## Per-fixture aggregates

| Fixture | N cells | N ok | N errors | N violate | All neutrality ok | All survive | N survive | DSR mean | DSR min | DSR max |
|---|---|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | 8 | 8 | 0 | 0 | True | False | 5 | 0.637206 | 0.081837 | 0.944013 |
| F2_P39_SECOND | 8 | 8 | 0 | 0 | True | False | 3 | 0.395858 | 0.069944 | 0.928768 |
| F3_LOW_VOL_WIDE | 8 | 8 | 0 | 0 | True | False | 5 | 0.630585 | 0.095286 | 0.958546 |
| F4_HIGH_VOL_NARROW | 8 | 8 | 0 | 0 | True | False | 3 | 0.421378 | 0.073224 | 0.952911 |

## Cross-fixture aggregate (all 32 cells)

- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 16
- DSR mean/min/max: 0.521257/0.069944/0.958546
- PSR mean/min/max: 0.481053/0.000000/1.000000
- Sharpe mean/min/max: 0.041485/-1.359181/2.176458
- Fixtures replicating P38 pooled verdict: 0 of 4

## Neutrality (every cell)

- model beta <= 0.001: True
- dollar <= 1e-09: True
- |realized beta| <= 0.15: True

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for the multiple trials searched (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero (analytical, Bailey & Lopez de Prado).
- A fixture replicates the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) when every cell is status ok, neutrality holds at every cell, and every cell survives deflation.
- Consolidated verdict: ROBUST_ACROSS_FIXTURES (all four replicate), FRAGILE_FIXTURE_DEPENDENT (one to three replicate), or DOES_NOT_REPLICATE (none replicate).
- This is a multi-fixture robustness test, not an in-sample fit: if the P38 pooled verdict holds on all four independently parameterized synthetic universes, the result is a property of the factor; if it holds on some, the verdict is fixture-dependent; if on none, the P38 verdict does not replicate.
- Synthetic-provenance caveat: results are on committed synthetic universes (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
