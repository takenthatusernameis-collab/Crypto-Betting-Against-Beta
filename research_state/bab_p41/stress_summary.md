# BAB P41 WP2 — Five-DGP Stress Meta-Analysis

Schema `bab_p41.stress_summary/1`. Controlled synthetic stimulus: not real market data and not market profitability evidence. The verdict is honest and may be negative.

**Stress verdict:** **FRAGILE_DGP_DEPENDENT**
**Reason:** Survival is DGP-dependent: 0 of 5 DGPs replicate (all cells survive + neutrality), 79 of 160 cells survive overall. Honest, may be negative; not tuned to a positive.

## Setup

- DGPs: 5 deterministic synthetic data-generating processes, 8 seeds each, 4 estimators (160 total cells)
- beta_window: 90d, quantile: 0.300000
- weighting: equal, beta_neutral: True, dollar_neutral: True, transaction_costs: 0.0
- DSR survive threshold: 0.500000
- n_trials_total (deflation, read-only from P38 WP1): 552

## DGPs (charter constants)

| DGP | Process | Kind | Idio Vol | Base Seed | Increment | Replicates Stress |
|---|---|---|---|---|---|---|
| GAUSSIAN_IID | baseline (frozen P40 family) | gaussian_iid | 0.003000 | 20261201 | 1009 | False |
| STUDENT_T | heavy-tailed idio (nu=4) | student_t | 0.003000 | 20271201 | 1013 | False |
| REGIME_SWITCH | 2-state Markov vol (calm/stress) | regime_switch | 0.003000 | 20281201 | 1019 | False |
| JUMP_DIFFUSION | Merton jump idio | jump_diffusion | 0.003000 | 20291201 | 1021 | False |
| STOCHASTIC_VOL | log-normal vol process | stochastic_vol | 0.003000 | 20301201 | 1031 | False |

- BTC prices read-only from tests/fixtures/wide_bab_universe.csv (the same deterministic random-walk fixture as P38/P40/WP1).
- Reuses the WP1 cell grid: asset returns = beta * BTC_return + idio, betas linspace(0.2, 2.4, 40).
- Not real market data; not market profitability evidence.

## Trial enumeration (read-only from P38 WP1)

Deflation over n_trials_total = **552**, read-only from research_state/bab_p38/deflated_summary.json (trial_enumeration.n_trials_total). Never re-enumerated or invented here.

## Per-DGP aggregates

### GAUSSIAN_IID

- Process: baseline (frozen P40 family) (gaussian_iid)
- Seeds: [20261201, 20262210, 20263219, 20264228, 20265237, 20266246, 20267255, 20268264]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 14
- replicates_stress_test: False
- DSR mean/min/max: 0.471239/0.087803/0.960772
- Sharpe mean/min/max: 0.002447/-1.113778/1.960054

### JUMP_DIFFUSION

- Process: Merton jump idio (jump_diffusion)
- Seeds: [20291201, 20292222, 20293243, 20294264, 20295285, 20296306, 20297327, 20298348]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 14
- replicates_stress_test: False
- DSR mean/min/max: 0.457944/0.067655/0.962023
- Sharpe mean/min/max: -0.276710/-2.032206/1.084885

### REGIME_SWITCH

- Process: 2-state Markov vol (calm/stress) (regime_switch)
- Seeds: [20281201, 20282220, 20283239, 20284258, 20285277, 20286296, 20287315, 20288334]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 22
- replicates_stress_test: False
- DSR mean/min/max: 0.659874/0.164065/0.909925
- Sharpe mean/min/max: 0.201565/-1.304598/1.279346

### STOCHASTIC_VOL

- Process: log-normal vol process (stochastic_vol)
- Seeds: [20301201, 20302232, 20303263, 20304294, 20305325, 20306356, 20307387, 20308418]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 12
- replicates_stress_test: False
- DSR mean/min/max: 0.460966/0.238156/0.814719
- Sharpe mean/min/max: -0.190887/-1.680186/1.121310

### STUDENT_T

- Process: heavy-tailed idio (nu=4) (student_t)
- Seeds: [20271201, 20272214, 20273227, 20274240, 20275253, 20276266, 20277279, 20278292]
- n_cells: 32, n_ok_cells: 32, n_error_cells: 0, n_neutrality_violations: 0
- all_neutrality_ok: True
- all_survive: False, any_survive: True, n_survive: 17
- replicates_stress_test: False
- DSR mean/min/max: 0.532782/0.079997/0.952848
- Sharpe mean/min/max: -0.093977/-1.545611/1.244259

## Cross-DGP aggregates

- n_dgps: 5
- n_total_cells: 160
- n_total_ok_cells: 160, n_total_error_cells: 0
- n_total_survive: 79
- n_dgps_replicating: 0 / 5
- all_dgps_neutrality_ok: True
- all_dgps_survive: False

## Verdict scale

- ROBUST_ACROSS_DGPS: every DGP replicates (all cells survive deflation + neutrality holds everywhere).
- FRAGILE_DGP_DEPENDENT: survival depends on DGP/seed (some cells survive, not all within any DGP).
- DOES_NOT_REPLICATE: no cell survives deflation in any DGP.

## Neutrality (every ok cell, every DGP, every estimator)

- model beta <= 1e-3: True
- dollar <= 1e-9 and |realized beta| <= 0.15 at every ok cell.

## Interpretation

- DSR = Deflated Sharpe Ratio: probability the observed Sharpe is genuine skill after correcting for multiple testing (n_trials_total). DSR >= 0.50 means more likely than not genuine skill.
- PSR = Probabilistic Sharpe Ratio: probability the Sharpe exceeds zero.
- The stress verdict reports whether BAB behaviour survives non-Gaussian idio across all five DGPs; an honest negative/neutral ranking is a valid finding.
- Synthetic-provenance caveat: results are on committed synthetic universes, not real market data. Never market alpha.
