# BAB P41 WP1 — Estimator Bakeoff Under Non-Gaussian Idio

Schema `bab_p41.estimator_bakeoff/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Bakeoff verdict:** **shrinkage_i0.3_t1.0_LEAST_BROKEN**
**Reason:** shrinkage_i0.3_t1.0 is least-broken by non-Gaussianity (highest mean DSR across non-Gaussian DGPs among neutrality-passing estimators). The least-broken estimator is ranked on deflated Sharpe over non-Gaussian DGPs only. A null/negative ranking is a valid finding; nothing is tuned to chase a positive and the shipped default is retained regardless of outcome.

## Setup

- DGPs: 5 deterministic synthetic data-generating processes, 8 seeds each, 4 estimators (160 total cells)
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True, transaction_costs: 0.0
- DSR survive threshold: 0.500000
- n_trials_total (deflation, read-only from P38 WP1): 552

## DGPs (charter constants)

| DGP | Process | Kind | Idio Vol | Base Seed | Increment |
|---|---|---|---|---|---|
| GAUSSIAN_IID | baseline (frozen P40 family) | gaussian_iid | 0.003000 | 20261201 | 1009 |
| STUDENT_T | heavy-tailed idio (nu=4) | student_t | 0.003000 | 20271201 | 1013 |
| REGIME_SWITCH | 2-state Markov vol (calm/stress) | regime_switch | 0.003000 | 20281201 | 1019 |
| JUMP_DIFFUSION | Merton jump idio | jump_diffusion | 0.003000 | 20291201 | 1021 |
| STOCHASTIC_VOL | log-normal vol process | stochastic_vol | 0.003000 | 20301201 | 1031 |

- BTC prices read-only from tests/fixtures/wide_bab_universe.csv (the same deterministic random-walk fixture as P38/P40).
- Asset returns = beta * BTC_return + idio, betas linspace(0.2, 2.4, 40).
- Not real market data; not market profitability evidence.

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Estimator families under test

- rolling_ols: params={'window': 90}
- ewma: params={'halflife': 40}
- shrinkage: params={'window': 90, 'shrink_target': 1.0, 'shrink_intensity': 0.3}
- shrinkage: params={'window': 90, 'shrink_target': 'cross_sectional_mean', 'shrink_intensity': 0.3}

## Per-DGP aggregates

### GAUSSIAN_IID

- Process: baseline (frozen P40 family) (gaussian_iid)
- Seeds: [20261201, 20262210, 20263219, 20264228, 20265237, 20266246, 20267255, 20268264]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 14
- DSR mean/min/max: 0.471239/0.087803/0.960772
- Sharpe mean/min/max: 0.002447/-1.113778/1.960054

### JUMP_DIFFUSION

- Process: Merton jump idio (jump_diffusion)
- Seeds: [20291201, 20292222, 20293243, 20294264, 20295285, 20296306, 20297327, 20298348]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 14
- DSR mean/min/max: 0.457944/0.067655/0.962023
- Sharpe mean/min/max: -0.276710/-2.032206/1.084885

### REGIME_SWITCH

- Process: 2-state Markov vol (calm/stress) (regime_switch)
- Seeds: [20281201, 20282220, 20283239, 20284258, 20285277, 20286296, 20287315, 20288334]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 22
- DSR mean/min/max: 0.659874/0.164065/0.909925
- Sharpe mean/min/max: 0.201565/-1.304598/1.279346

### STOCHASTIC_VOL

- Process: log-normal vol process (stochastic_vol)
- Seeds: [20301201, 20302232, 20303263, 20304294, 20305325, 20306356, 20307387, 20308418]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 12
- DSR mean/min/max: 0.460966/0.238156/0.814719
- Sharpe mean/min/max: -0.190887/-1.680186/1.121310

### STUDENT_T

- Process: heavy-tailed idio (nu=4) (student_t)
- Seeds: [20271201, 20272214, 20273227, 20274240, 20275253, 20276266, 20277279, 20278292]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 17
- DSR mean/min/max: 0.532782/0.079997/0.952848
- Sharpe mean/min/max: -0.093977/-1.545611/1.244259

## Estimator comparison (least-broken by non-Gaussianity)

- Least-broken estimator: **shrinkage_i0.3_t1.0**
- Reason: Highest mean deflated Sharpe across non-Gaussian DGPs (STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL) among estimators passing all neutrality invariants; honest ranking, not tuned to a positive.

| Estimator | Non-Gaussian DSR mean | Non-Gaussian neutrality OK |
|---|---|---|
| rolling_ols_w90 | 0.567500 | True |
| ewma_h40 | 0.548774 | True |
| shrinkage_i0.3_t1.0 | 0.567580 | True |
| shrinkage_i0.3_csm | 0.427711 | True |

The least-broken estimator is ranked on deflated Sharpe over non-Gaussian DGPs only. A null/negative ranking is a valid finding; nothing is tuned to chase a positive and the shipped default is retained regardless of outcome.

## Cross-DGP aggregates

- n_dgps: 5
- n_total_cells: 160
- n_total_ok_cells: 160, n_total_error_cells: 0
- n_total_survive: 79
- n_dgps_replicating: 5 / 5
- all_dgps_neutrality_ok: True
- all_dgps_survive: False

## Neutrality (every ok cell, every DGP, every estimator)

- model beta <= 1e-3: True
- dollar <= 1e-9 and |realized beta| <= 0.15 at every ok cell.

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for multiple testing (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero.
- Rank-stability (Spearman / Jaccard vs OLS baseline) measures how far each estimator's beta estimates depart from the shipped rolling-OLS reference.
- The bakeoff verdict reports which estimator (if any) is least-broken by non-Gaussian idio; an honest negative ranking is a valid finding.
- Synthetic-provenance caveat: results are on committed synthetic universes, not real market data. Never market alpha.
