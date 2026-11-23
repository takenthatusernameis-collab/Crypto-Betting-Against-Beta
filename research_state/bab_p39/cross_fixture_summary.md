# BAB P39 WP2 — Cross-Fixture Replication (Second Independent Synthetic Universe)

Schema `bab_p39.cross_fixture/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative (DOES_NOT_REPLICATE).

**Campaign verdict:** **DOES_NOT_REPLICATE**
**Reason:** At least one seed cell fails neutrality, errors, or has DSR < 0.5 after deflation over n_trials_total=552; honest negative — the P38 pooled verdict does not replicate on this fixture.

## Setup

- Seeds: 8 (base=20270101, increment=9973)
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True
- idio_vol: 0.006000, beta range: [0.200000, 2.400000], n_assets: 32

## Fixture (second independent parameterization)

- BTC prices read-only from tests/fixtures/wide_bab_universe.csv (the same deterministic random-walk fixture as P39 WP1).
- Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.006), betas linspace(0.2, 2.4, 32).
- Distinct seed base (20270101), increment (9973), asset count (32), idio vol (0.006), and beta grid (0.20–2.40) versus P39 WP1 — an independent parameterization, not a re-run of the same fixture.
- Not real market data; not market profitability evidence.

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Per-seed results (pooled; no regime split)

| Seed | N periods | Sharpe | DSR | PSR | Survives | Verdict | Neutrality |
|---|---|---|---|---|---|---|---|
| 20270101 | 339 | -0.861582 | 0.070183 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| 20280074 | 339 | 0.487880 | 0.923269 | 1.000000 | True | SURVIVES_DEFLATION | True |
| 20290047 | 339 | -0.641189 | 0.082510 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| 20300020 | 339 | 0.327766 | 0.923094 | 1.000000 | True | SURVIVES_DEFLATION | True |
| 20309993 | 339 | -1.107029 | 0.073291 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| 20319966 | 339 | -0.769760 | 0.084453 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| 20329939 | 339 | -1.359181 | 0.080656 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| 20339912 | 339 | 2.176458 | 0.928788 | 1.000000 | True | SURVIVES_DEFLATION | True |

## Aggregates (across the eight seeds)

- n_cells: 8, n_ok_cells: 8, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 3
- DSR mean/min/max: 0.395780/0.070183/0.928788
- PSR mean/min/max: 0.375000/0.000000/1.000000
- Sharpe mean/min/max: -0.218329/-1.359181/2.176458

## Tail-metric aggregates (worst 5% / 1% / 2.5% tails, drawdown)

| Metric | Mean | Min | Max |
|---|---|---|---|
| cvar_95 | -0.002037 | -0.002204 | -0.001764 |
| cvar_99 | -0.002503 | -0.002770 | -0.002182 |
| expected_shortfall_975 | -0.002266 | -0.002446 | -0.001939 |
| worst_day_return | -0.002906 | -0.003820 | -0.002511 |
| skew | 0.067473 | -0.110049 | 0.170186 |
| excess_kurtosis | -0.060852 | -0.313390 | 0.309875 |
| tail_asymmetry | -0.010903 | -0.107095 | 0.031878 |
| conditional_drawdown_95 | -0.024601 | -0.040366 | -0.007340 |
| max_drawdown | -0.026261 | -0.041704 | -0.009096 |

## Neutrality (every cell)

- model beta <= 0.001: True
- dollar <= 1e-09: True
- |realized beta| <= 0.15: True

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for the multiple trials searched (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero (analytical, Bailey & Lopez de Prado).
- CVaR/expected-shortfall/drawdown characterize the left tail per seed cell; neutrality invariants hold at every cell.
- This is a cross-fixture replication test, not an in-sample fit: if the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) holds on this second, independently parameterized synthetic universe, the result is a property of the factor rather than an artifact of the single committed fixture; if it fails, the P38 verdict is fixture-dependent.
- Synthetic-provenance caveat: results are on committed synthetic universes (BTC prices + seeded idiosyncratic noise), not real market data. Never market alpha.
