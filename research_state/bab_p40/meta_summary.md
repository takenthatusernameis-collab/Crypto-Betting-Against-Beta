# BAB P40 WP0 — Multi-Fixture Robustness Meta-Analysis (Four Synthetic Fixtures)

Schema `bab_p40.meta_analysis/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Campaign verdict:** **DOES_NOT_REPLICATE**
**Reason:** 0 of 4 fixtures replicate the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over n_trials_total=552; DSR survive threshold=0.5. No fixture replicates — the P38 pooled verdict does not replicate (DOES_NOT_REPLICATE). Honest negative.

## Setup

- Fixtures: 4 independent deterministic synthetic universes, 8 seeds each (32 total cells)
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True, transaction_costs: 0.0
- DSR survive threshold: 0.500000
- n_trials_total (deflation, read-only from P38 WP1): 552

## Fixtures (four independent deterministic parameterizations)

| Fixture | Base Seed | Increment | Idio Vol | Beta Range | N Assets | Column Prefix | Role |
|---|---|---|---|---|---|---|---|
| F1_PRIMARY | 20261120 | 1009 | 0.003000 | [0.350000, 1.900000] | 40 | A | P38/P39 WP1 primary parameterization |
| F2_P39_SECOND | 20270101 | 9973 | 0.006000 | [0.200000, 2.400000] | 32 | X | P39 WP2 second parameterization |
| F3_LOW_VOL_WIDE | 20280201 | 10009 | 0.002000 | [0.250000, 2.100000] | 36 | Y | Low-idio, wider beta cross-section |
| F4_HIGH_VOL_NARROW | 20290301 | 10007 | 0.008000 | [0.400000, 1.700000] | 28 | Z | High-idio, narrower beta cross-section |

- BTC prices read-only from tests/fixtures/wide_bab_universe.csv (the same deterministic random-walk fixture as P38/P39).
- Asset returns = beta * BTC_return + idio, idio ~ N(0, idio_vol), betas linspace(beta_min, beta_max, n_assets).
- Four distinct seed bases, increments, idio vols, beta grids, and asset counts — independent parameterizations, not re-runs of the same fixture.
- Not real market data; not market profitability evidence.

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Per-fixture results (pooled per-seed cells; no regime split)

### F1_PRIMARY

- Role: P38/P39 WP1 primary parameterization
- Seeds: [20261120, 20262129, 20263138, 20264147, 20265156, 20266165, 20267174, 20268183]
- n_cells: 8, n_ok_cells: 8, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 5
- DSR mean/min/max: 0.636728/0.081475/0.943990
- PSR mean/min/max: 0.626070/0.000000/1.000000
- Sharpe mean/min/max: 0.367434/-0.845875/1.865525
- Replicates P38 pooled verdict: False

#### Per-seed cells

| Cell Key | Seed | Seed Index | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|---|---|
| seed_0 | 20261120 | 0 | ok | 0.760518 | 0.943990 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_1 | 20262129 | 1 | ok | 0.320261 | 0.933048 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_2 | 20263138 | 2 | ok | 1.865525 | 0.926165 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_3 | 20264147 | 3 | ok | -0.129599 | 0.236171 | 0.008562 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_4 | 20265156 | 4 | ok | -0.531831 | 0.108773 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_5 | 20266165 | 5 | ok | 0.967765 | 0.925786 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_6 | 20267174 | 6 | ok | -0.845875 | 0.081475 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_7 | 20268183 | 7 | ok | 0.532712 | 0.938416 | 1.000000 | True | SURVIVES_DEFLATION | True |

### F2_P39_SECOND

- Role: P39 WP2 second parameterization
- Seeds: [20270101, 20280074, 20290047, 20300020, 20309993, 20319966, 20329939, 20339912]
- n_cells: 8, n_ok_cells: 8, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 3
- DSR mean/min/max: 0.395780/0.070183/0.928788
- PSR mean/min/max: 0.375000/0.000000/1.000000
- Sharpe mean/min/max: -0.218329/-1.359181/2.176458
- Replicates P38 pooled verdict: False

#### Per-seed cells

| Cell Key | Seed | Seed Index | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|---|---|
| seed_0 | 20270101 | 0 | ok | -0.861582 | 0.070183 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_1 | 20280074 | 1 | ok | 0.487880 | 0.923269 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_2 | 20290047 | 2 | ok | -0.641189 | 0.082510 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_3 | 20300020 | 3 | ok | 0.327766 | 0.923094 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_4 | 20309993 | 4 | ok | -1.107029 | 0.073291 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_5 | 20319966 | 5 | ok | -0.769760 | 0.084453 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_6 | 20329939 | 6 | ok | -1.359181 | 0.080656 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_7 | 20339912 | 7 | ok | 2.176458 | 0.928788 | 1.000000 | True | SURVIVES_DEFLATION | True |

### F3_LOW_VOL_WIDE

- Role: Low-idio, wider beta cross-section
- Seeds: [20280201, 20290210, 20300219, 20310228, 20320237, 20330246, 20340255, 20350264]
- n_cells: 8, n_ok_cells: 8, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 5
- DSR mean/min/max: 0.630724/0.095354/0.958728
- PSR mean/min/max: 0.603886/0.000000/1.000000
- Sharpe mean/min/max: 0.182513/-0.535429/1.051665
- Replicates P38 pooled verdict: False

#### Per-seed cells

| Cell Key | Seed | Seed Index | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|---|---|
| seed_0 | 20280201 | 0 | ok | -0.535429 | 0.095354 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_1 | 20290210 | 1 | ok | 0.052140 | 0.958728 | 0.831125 | True | SURVIVES_DEFLATION | True |
| seed_2 | 20300219 | 2 | ok | -0.533620 | 0.109025 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_3 | 20310228 | 3 | ok | 0.494379 | 0.943538 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_4 | 20320237 | 4 | ok | -0.288504 | 0.123886 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_5 | 20330246 | 5 | ok | 1.005151 | 0.936830 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_6 | 20340255 | 6 | ok | 1.051665 | 0.930717 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_7 | 20350264 | 7 | ok | 0.214326 | 0.947714 | 0.999960 | True | SURVIVES_DEFLATION | True |

### F4_HIGH_VOL_NARROW

- Role: High-idio, narrower beta cross-section
- Seeds: [20290301, 20300308, 20310315, 20320322, 20330329, 20340336, 20350343, 20360350]
- n_cells: 8, n_ok_cells: 8, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 3
- DSR mean/min/max: 0.419918/0.072676/0.952693
- PSR mean/min/max: 0.319254/0.000000/1.000000
- Sharpe mean/min/max: -0.165679/-1.043952/1.313904
- Replicates P38 pooled verdict: False

#### Per-seed cells

| Cell Key | Seed | Seed Index | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|---|---|
| seed_0 | 20290301 | 0 | ok | 1.313904 | 0.929818 | 1.000000 | True | SURVIVES_DEFLATION | True |
| seed_1 | 20300308 | 1 | ok | 0.210269 | 0.952693 | 0.999946 | True | SURVIVES_DEFLATION | True |
| seed_2 | 20310315 | 2 | ok | -0.069405 | 0.311295 | 0.101022 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_3 | 20320322 | 3 | ok | -0.456647 | 0.072676 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_4 | 20330329 | 4 | ok | -1.043952 | 0.074221 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_5 | 20340336 | 5 | ok | -0.006414 | 0.792640 | 0.453067 | True | SURVIVES_DEFLATION | True |
| seed_6 | 20350343 | 6 | ok | -0.268372 | 0.150112 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| seed_7 | 20360350 | 7 | ok | -1.004819 | 0.075887 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |

## Cross-Fixture Aggregates

- n_fixtures: 4
- n_total_cells: 32
- n_total_ok_cells: 32, n_total_error_cells: 0
- n_total_survive: 16
- n_fixtures_replicating: 0 / 4
- replication_fraction: 0.000000
- all_fixtures_neutrality_ok: True
- all_fixtures_survive: False

## Tail-metric aggregates (worst 5% / 1% / 2.5% tails, drawdown)

| Metric | Mean | Min | Max |
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

## Neutrality (every cell, every fixture)

- model beta <= 1e-3: True
- dollar <= 1e-9: True
- |realized beta| <= 0.15: True

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for the multiple trials searched (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero (analytical, Bailey & Lopez de Prado).
- CVaR/expected-shortfall/drawdown characterize the left tail per seed cell; neutrality invariants hold at every cell.
- This is a multi-fixture robustness meta-analysis: if the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) holds on all four independently parameterized synthetic universes, the result is robust across fixtures; if it holds on some but not all, the P38 verdict is fixture-dependent (FRAGILE_FIXTURE_DEPENDENT); if it holds on none, the verdict does not replicate (DOES_NOT_REPLICATE).
- Synthetic-provenance caveat: results are on committed synthetic universes (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
