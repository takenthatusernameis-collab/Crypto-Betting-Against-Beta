# BAB P41 Closing Decision -- Non-Gaussian & Regime-Switching Stress Battery

**Campaign:** P41 "Non-Gaussian & Regime-Switching Synthetic Stress Battery"
**Decision row:** P41 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p41/stress_summary.json` (WP2; five-DGP stress meta-analysis)

**Verdict strings verified:** `FRAGILE_DGP_DEPENDENT`, `synthetic`,
`not real market data`, `not market profitability evidence`, `never market alpha`

**Decision:** **FRAGILE_DGP_DEPENDENT**. Survival is DGP-dependent: 0 of 5 DGPs replicate (all cells survive + neutrality), 79 of 160 cells survive overall. Honest, may be negative; not tuned to a positive. 0 of 5 DGPs replicate the stress test (every cell survives deflation + neutrality holds everywhere) after deflation over n_trials_total=552 at DSR survive threshold 0.5. 79 of 160 cells survive overall across the five DGPs. Neutrality invariants hold at every cell across all five DGPs. The shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS) is retained; nothing is flipped. Synthetic-provenance caveat applies throughout.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema | bab_p41.stress_summary/1 |
| Campaign | P41 Non-Gaussian & Regime-Switching Synthetic Stress Battery |
| WP | WP2 - Five-DGP Stress Meta-Analysis |
| Synthetic | True |
| Generator | scripts/bab_p41_stress.py |
| Fixture path | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Returns SHA256 | `b2d6616cc1800b36908ed9f8d22d8b65a1d58b3d1a171840e151ccfc793ed197` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| N DGPs | 5 |
| N seeds per DGP | 8 |
| N estimators | 4 |
| N total cells | 160 |
| DGP IDs | GAUSSIAN_IID, STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL |
| DGPs (id / process / kind / idio_vol / base_seed / increment) | GAUSSIAN_IID=baseline (frozen P40 family)/gaussian_iid/0.003/20261201/1009; STUDENT_T=heavy-tailed idio (nu=4)/student_t/0.003/20271201/1013; REGIME_SWITCH=2-state Markov vol (calm/stress)/regime_switch/0.003/20281201/1019; JUMP_DIFFUSION=Merton jump idio/jump_diffusion/0.003/20291201/1021; STOCHASTIC_VOL=log-normal vol process/stochastic_vol/0.003/20301201/1031 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Transaction costs | 0.000000 |
| Deflation trials (n_trials_total) | 552 |
| DSR survive threshold | 0.500000 |
| Stress verdict | FRAGILE_DGP_DEPENDENT |
<!-- table:provenance:end -->

---

## WP2 -- Five-DGP Stress Meta-Analysis

Five deterministic synthetic data-generating processes (GAUSSIAN_IID control,
STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL), 8 seeds each, 4
estimators (shipped rolling-OLS vs P35 runner-ups EWMA halflife=40; Shrinkage
intensity=0.3 target=1.0 and cross_sectional_mean) = 160 total cells. Per-cell
DSR/PSR deflated over `n_trials_total` read-only from P38 WP1 plus tail risk
and the three neutrality invariants at every cell.

<!-- table:dgp:start -->
| DGP | Process | Kind | Idio Vol | Base Seed | Increment | N Cells | N OK | N Survive | DSR Mean | DSR Max | Replicates Stress |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GAUSSIAN_IID | baseline (frozen P40 family) | gaussian_iid | 0.003000 | 20261201 | 1009 | 32 | 32 | 14 | 0.471239 | 0.960772 | False |
| JUMP_DIFFUSION | Merton jump idio | jump_diffusion | 0.003000 | 20291201 | 1021 | 32 | 32 | 14 | 0.457944 | 0.962023 | False |
| REGIME_SWITCH | 2-state Markov vol (calm/stress) | regime_switch | 0.003000 | 20281201 | 1019 | 32 | 32 | 22 | 0.659874 | 0.909925 | False |
| STOCHASTIC_VOL | log-normal vol process | stochastic_vol | 0.003000 | 20301201 | 1031 | 32 | 32 | 12 | 0.460966 | 0.814719 | False |
| STUDENT_T | heavy-tailed idio (nu=4) | student_t | 0.003000 | 20271201 | 1013 | 32 | 32 | 17 | 0.532782 | 0.952848 | False |
<!-- table:dgp:end -->

<!-- table:cell:start -->
| DGP | Cell Key | Seed | Estimator | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality OK |
|---|---|---|---|---|---|---|---|---|---|---|
| GAUSSIAN_IID | GAUSSIAN_IID_seed0_rolling_ols_w90 | 20261201 | rolling_ols_w90 | ok | -0.496386 | 0.089823 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed0_ewma_h40 | 20261201 | ewma_h40 | ok | -0.564767 | 0.091794 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed0_shrinkage_i0.3_t1.0 | 20261201 | shrinkage_i0.3_t1.0 | ok | -0.503582 | 0.089656 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed0_shrinkage_i0.3_csm | 20261201 | shrinkage_i0.3_csm | ok | -0.842026 | 0.087803 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed1_rolling_ols_w90 | 20262210 | rolling_ols_w90 | ok | 0.120381 | 0.960536 | 0.986547 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed1_ewma_h40 | 20262210 | ewma_h40 | ok | 0.164794 | 0.959680 | 0.998772 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed1_shrinkage_i0.3_t1.0 | 20262210 | shrinkage_i0.3_t1.0 | ok | 0.118180 | 0.960772 | 0.985088 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed1_shrinkage_i0.3_csm | 20262210 | shrinkage_i0.3_csm | ok | -0.254105 | 0.106011 | 0.000002 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed2_rolling_ols_w90 | 20263219 | rolling_ols_w90 | ok | -0.712538 | 0.117064 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed2_ewma_h40 | 20263219 | ewma_h40 | ok | -0.481929 | 0.129516 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed2_shrinkage_i0.3_t1.0 | 20263219 | shrinkage_i0.3_t1.0 | ok | -0.716581 | 0.117042 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed2_shrinkage_i0.3_csm | 20263219 | shrinkage_i0.3_csm | ok | -1.113778 | 0.114642 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed3_rolling_ols_w90 | 20264228 | rolling_ols_w90 | ok | 0.437289 | 0.930820 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed3_ewma_h40 | 20264228 | ewma_h40 | ok | 0.364848 | 0.933746 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed3_shrinkage_i0.3_t1.0 | 20264228 | shrinkage_i0.3_t1.0 | ok | 0.429594 | 0.931025 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed3_shrinkage_i0.3_csm | 20264228 | shrinkage_i0.3_csm | ok | 0.077145 | 0.957053 | 0.921868 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed4_rolling_ols_w90 | 20265237 | rolling_ols_w90 | ok | -0.372654 | 0.106768 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed4_ewma_h40 | 20265237 | ewma_h40 | ok | -0.468399 | 0.099368 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed4_shrinkage_i0.3_t1.0 | 20265237 | shrinkage_i0.3_t1.0 | ok | -0.378709 | 0.106271 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed4_shrinkage_i0.3_csm | 20265237 | shrinkage_i0.3_csm | ok | -0.720585 | 0.089040 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed5_rolling_ols_w90 | 20266246 | rolling_ols_w90 | ok | -0.468045 | 0.103511 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed5_ewma_h40 | 20266246 | ewma_h40 | ok | -0.466067 | 0.106587 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed5_shrinkage_i0.3_t1.0 | 20266246 | shrinkage_i0.3_t1.0 | ok | -0.473962 | 0.103234 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed5_shrinkage_i0.3_csm | 20266246 | shrinkage_i0.3_csm | ok | -0.848793 | 0.093195 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed6_rolling_ols_w90 | 20267255 | rolling_ols_w90 | ok | 0.372553 | 0.934192 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed6_ewma_h40 | 20267255 | ewma_h40 | ok | 0.434787 | 0.932296 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed6_shrinkage_i0.3_t1.0 | 20267255 | shrinkage_i0.3_t1.0 | ok | 0.367957 | 0.934406 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed6_shrinkage_i0.3_csm | 20267255 | shrinkage_i0.3_csm | ok | -0.063200 | 0.310166 | 0.122621 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed7_rolling_ols_w90 | 20268264 | rolling_ols_w90 | ok | 1.867019 | 0.890472 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed7_ewma_h40 | 20268264 | ewma_h40 | ok | 1.960054 | 0.892742 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed7_shrinkage_i0.3_t1.0 | 20268264 | shrinkage_i0.3_t1.0 | ok | 1.865931 | 0.890797 | 1.000000 | True | SURVIVES_DEFLATION | True |
| GAUSSIAN_IID | GAUSSIAN_IID_seed7_shrinkage_i0.3_csm | 20268264 | shrinkage_i0.3_csm | ok | 1.443888 | 0.909617 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed0_rolling_ols_w90 | 20291201 | rolling_ols_w90 | ok | 0.087227 | 0.954691 | 0.945682 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed0_ewma_h40 | 20291201 | ewma_h40 | ok | 0.070958 | 0.957086 | 0.904045 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed0_shrinkage_i0.3_t1.0 | 20291201 | shrinkage_i0.3_t1.0 | ok | 0.085646 | 0.954815 | 0.942401 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed0_shrinkage_i0.3_csm | 20291201 | shrinkage_i0.3_csm | ok | -0.283704 | 0.122301 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed1_rolling_ols_w90 | 20292222 | rolling_ols_w90 | ok | -0.944319 | 0.087326 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed1_ewma_h40 | 20292222 | ewma_h40 | ok | -0.887922 | 0.085055 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed1_shrinkage_i0.3_t1.0 | 20292222 | shrinkage_i0.3_t1.0 | ok | -0.952760 | 0.087162 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed1_shrinkage_i0.3_csm | 20292222 | shrinkage_i0.3_csm | ok | -1.290794 | 0.090253 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed2_rolling_ols_w90 | 20293243 | rolling_ols_w90 | ok | 0.854993 | 0.920155 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed2_ewma_h40 | 20293243 | ewma_h40 | ok | 0.827731 | 0.918138 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed2_shrinkage_i0.3_t1.0 | 20293243 | shrinkage_i0.3_t1.0 | ok | 0.853661 | 0.920110 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed2_shrinkage_i0.3_csm | 20293243 | shrinkage_i0.3_csm | ok | 0.445991 | 0.922027 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed3_rolling_ols_w90 | 20294264 | rolling_ols_w90 | ok | 1.036295 | 0.920962 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed3_ewma_h40 | 20294264 | ewma_h40 | ok | 1.084885 | 0.926710 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed3_shrinkage_i0.3_t1.0 | 20294264 | shrinkage_i0.3_t1.0 | ok | 1.030855 | 0.921062 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed3_shrinkage_i0.3_csm | 20294264 | shrinkage_i0.3_csm | ok | 0.606216 | 0.916013 | 1.000000 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed4_rolling_ols_w90 | 20295285 | rolling_ols_w90 | ok | 0.162093 | 0.961739 | 0.998575 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed4_ewma_h40 | 20295285 | ewma_h40 | ok | 0.022923 | 0.937398 | 0.663281 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed4_shrinkage_i0.3_t1.0 | 20295285 | shrinkage_i0.3_t1.0 | ok | 0.158767 | 0.962023 | 0.998262 | True | SURVIVES_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed4_shrinkage_i0.3_csm | 20295285 | shrinkage_i0.3_csm | ok | -0.266130 | 0.086967 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed5_rolling_ols_w90 | 20296306 | rolling_ols_w90 | ok | -0.338878 | 0.099475 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed5_ewma_h40 | 20296306 | ewma_h40 | ok | -0.308862 | 0.100323 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed5_shrinkage_i0.3_t1.0 | 20296306 | shrinkage_i0.3_t1.0 | ok | -0.339780 | 0.099416 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed5_shrinkage_i0.3_csm | 20296306 | shrinkage_i0.3_csm | ok | -0.715198 | 0.083173 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed6_rolling_ols_w90 | 20297327 | rolling_ols_w90 | ok | -1.676458 | 0.081891 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed6_ewma_h40 | 20297327 | ewma_h40 | ok | -1.618045 | 0.084129 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed6_shrinkage_i0.3_t1.0 | 20297327 | shrinkage_i0.3_t1.0 | ok | -1.680308 | 0.081864 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed6_shrinkage_i0.3_csm | 20297327 | shrinkage_i0.3_csm | ok | -2.032206 | 0.080558 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed7_rolling_ols_w90 | 20298348 | rolling_ols_w90 | ok | -0.591353 | 0.067838 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed7_ewma_h40 | 20298348 | ewma_h40 | ok | -0.592920 | 0.079966 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed7_shrinkage_i0.3_t1.0 | 20298348 | shrinkage_i0.3_t1.0 | ok | -0.595196 | 0.067655 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| JUMP_DIFFUSION | JUMP_DIFFUSION_seed7_shrinkage_i0.3_csm | 20298348 | shrinkage_i0.3_csm | ok | -1.068118 | 0.075919 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed0_rolling_ols_w90 | 20281201 | rolling_ols_w90 | ok | 0.666078 | 0.872423 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed0_ewma_h40 | 20281201 | ewma_h40 | ok | 0.723361 | 0.870518 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed0_shrinkage_i0.3_t1.0 | 20281201 | shrinkage_i0.3_t1.0 | ok | 0.662682 | 0.872445 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed0_shrinkage_i0.3_csm | 20281201 | shrinkage_i0.3_csm | ok | 0.438284 | 0.882904 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed1_rolling_ols_w90 | 20282220 | rolling_ols_w90 | ok | 0.126508 | 0.886793 | 0.989977 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed1_ewma_h40 | 20282220 | ewma_h40 | ok | 0.332919 | 0.864419 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed1_shrinkage_i0.3_t1.0 | 20282220 | shrinkage_i0.3_t1.0 | ok | 0.125807 | 0.886993 | 0.989628 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed1_shrinkage_i0.3_csm | 20282220 | shrinkage_i0.3_csm | ok | 0.327984 | 0.859941 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed2_rolling_ols_w90 | 20283239 | rolling_ols_w90 | ok | 0.259706 | 0.852122 | 0.999999 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed2_ewma_h40 | 20283239 | ewma_h40 | ok | -0.454224 | 0.202538 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed2_shrinkage_i0.3_t1.0 | 20283239 | shrinkage_i0.3_t1.0 | ok | 0.257489 | 0.852313 | 0.999999 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed2_shrinkage_i0.3_csm | 20283239 | shrinkage_i0.3_csm | ok | -0.039359 | 0.423081 | 0.234680 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed3_rolling_ols_w90 | 20284258 | rolling_ols_w90 | ok | 0.694187 | 0.854921 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed3_ewma_h40 | 20284258 | ewma_h40 | ok | 0.297129 | 0.853749 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed3_shrinkage_i0.3_t1.0 | 20284258 | shrinkage_i0.3_t1.0 | ok | 0.692343 | 0.854999 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed3_shrinkage_i0.3_csm | 20284258 | shrinkage_i0.3_csm | ok | 0.427648 | 0.872862 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed4_rolling_ols_w90 | 20285277 | rolling_ols_w90 | ok | 0.991610 | 0.812738 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed4_ewma_h40 | 20285277 | ewma_h40 | ok | 1.279346 | 0.824180 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed4_shrinkage_i0.3_t1.0 | 20285277 | shrinkage_i0.3_t1.0 | ok | 0.989497 | 0.812769 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed4_shrinkage_i0.3_csm | 20285277 | shrinkage_i0.3_csm | ok | 0.731274 | 0.825461 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed5_rolling_ols_w90 | 20286296 | rolling_ols_w90 | ok | -1.059929 | 0.190078 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed5_ewma_h40 | 20286296 | ewma_h40 | ok | -0.715122 | 0.198718 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed5_shrinkage_i0.3_t1.0 | 20286296 | shrinkage_i0.3_t1.0 | ok | -1.063847 | 0.190060 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed5_shrinkage_i0.3_csm | 20286296 | shrinkage_i0.3_csm | ok | -1.304598 | 0.189840 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed6_rolling_ols_w90 | 20287315 | rolling_ols_w90 | ok | 0.736717 | 0.906176 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed6_ewma_h40 | 20287315 | ewma_h40 | ok | 0.944824 | 0.905007 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed6_shrinkage_i0.3_t1.0 | 20287315 | shrinkage_i0.3_t1.0 | ok | 0.734905 | 0.906172 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed6_shrinkage_i0.3_csm | 20287315 | shrinkage_i0.3_csm | ok | 0.531157 | 0.909925 | 1.000000 | True | SURVIVES_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed7_rolling_ols_w90 | 20288334 | rolling_ols_w90 | ok | -0.436885 | 0.170429 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed7_ewma_h40 | 20288334 | ewma_h40 | ok | -0.362537 | 0.176756 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed7_shrinkage_i0.3_t1.0 | 20288334 | shrinkage_i0.3_t1.0 | ok | -0.434393 | 0.170568 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| REGIME_SWITCH | REGIME_SWITCH_seed7_shrinkage_i0.3_csm | 20288334 | shrinkage_i0.3_csm | ok | -0.650486 | 0.164065 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed0_rolling_ols_w90 | 20301201 | rolling_ols_w90 | ok | -0.423865 | 0.250973 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed0_ewma_h40 | 20301201 | ewma_h40 | ok | -0.539238 | 0.302559 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed0_shrinkage_i0.3_t1.0 | 20301201 | shrinkage_i0.3_t1.0 | ok | -0.422978 | 0.251025 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed0_shrinkage_i0.3_csm | 20301201 | shrinkage_i0.3_csm | ok | -0.592626 | 0.252201 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed1_rolling_ols_w90 | 20302232 | rolling_ols_w90 | ok | 0.545060 | 0.779892 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed1_ewma_h40 | 20302232 | ewma_h40 | ok | 0.791652 | 0.775852 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed1_shrinkage_i0.3_t1.0 | 20302232 | shrinkage_i0.3_t1.0 | ok | 0.546676 | 0.779875 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed1_shrinkage_i0.3_csm | 20302232 | shrinkage_i0.3_csm | ok | 0.174984 | 0.814719 | 0.999354 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed2_rolling_ols_w90 | 20303263 | rolling_ols_w90 | ok | -1.256880 | 0.351330 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed2_ewma_h40 | 20303263 | ewma_h40 | ok | -1.514413 | 0.354935 | 0.000001 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed2_shrinkage_i0.3_t1.0 | 20303263 | shrinkage_i0.3_t1.0 | ok | -1.257977 | 0.351335 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed2_shrinkage_i0.3_csm | 20303263 | shrinkage_i0.3_csm | ok | -1.410616 | 0.348623 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed3_rolling_ols_w90 | 20304294 | rolling_ols_w90 | ok | 1.121310 | 0.633528 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed3_ewma_h40 | 20304294 | ewma_h40 | ok | 1.068699 | 0.636723 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed3_shrinkage_i0.3_t1.0 | 20304294 | shrinkage_i0.3_t1.0 | ok | 1.118275 | 0.633573 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed3_shrinkage_i0.3_csm | 20304294 | shrinkage_i0.3_csm | ok | 0.962234 | 0.636162 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed4_rolling_ols_w90 | 20305325 | rolling_ols_w90 | ok | -0.271052 | 0.281326 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed4_ewma_h40 | 20305325 | ewma_h40 | ok | -0.603632 | 0.238156 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed4_shrinkage_i0.3_t1.0 | 20305325 | shrinkage_i0.3_t1.0 | ok | -0.269986 | 0.281459 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed4_shrinkage_i0.3_csm | 20305325 | shrinkage_i0.3_csm | ok | -0.424782 | 0.273079 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed5_rolling_ols_w90 | 20306356 | rolling_ols_w90 | ok | -0.147340 | 0.439407 | 0.002671 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed5_ewma_h40 | 20306356 | ewma_h40 | ok | -0.173803 | 0.433981 | 0.000463 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed5_shrinkage_i0.3_t1.0 | 20306356 | shrinkage_i0.3_t1.0 | ok | -0.147323 | 0.439411 | 0.002674 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed5_shrinkage_i0.3_csm | 20306356 | shrinkage_i0.3_csm | ok | -0.211254 | 0.434248 | 0.000024 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed6_rolling_ols_w90 | 20307387 | rolling_ols_w90 | ok | -1.407415 | 0.315593 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed6_ewma_h40 | 20307387 | ewma_h40 | ok | -0.738055 | 0.321374 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed6_shrinkage_i0.3_t1.0 | 20307387 | shrinkage_i0.3_t1.0 | ok | -1.408130 | 0.315598 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed6_shrinkage_i0.3_csm | 20307387 | shrinkage_i0.3_csm | ok | -1.680186 | 0.327225 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed7_rolling_ols_w90 | 20308418 | rolling_ols_w90 | ok | 0.487347 | 0.620266 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed7_ewma_h40 | 20308418 | ewma_h40 | ok | 0.870494 | 0.636302 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed7_shrinkage_i0.3_t1.0 | 20308418 | shrinkage_i0.3_t1.0 | ok | 0.485412 | 0.620282 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STOCHASTIC_VOL | STOCHASTIC_VOL_seed7_shrinkage_i0.3_csm | 20308418 | shrinkage_i0.3_csm | ok | 0.621011 | 0.619903 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed0_rolling_ols_w90 | 20271201 | rolling_ols_w90 | ok | 0.217566 | 0.944144 | 0.999968 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed0_ewma_h40 | 20271201 | ewma_h40 | ok | 0.146135 | 0.952848 | 0.996393 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed0_shrinkage_i0.3_t1.0 | 20271201 | shrinkage_i0.3_t1.0 | ok | 0.215271 | 0.944219 | 0.999962 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed0_shrinkage_i0.3_csm | 20271201 | shrinkage_i0.3_csm | ok | -0.129525 | 0.186052 | 0.008632 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed1_rolling_ols_w90 | 20272214 | rolling_ols_w90 | ok | -1.233469 | 0.103520 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed1_ewma_h40 | 20272214 | ewma_h40 | ok | -0.970809 | 0.122599 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed1_shrinkage_i0.3_t1.0 | 20272214 | shrinkage_i0.3_t1.0 | ok | -1.235256 | 0.103529 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed1_shrinkage_i0.3_csm | 20272214 | shrinkage_i0.3_csm | ok | -1.545611 | 0.097077 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed2_rolling_ols_w90 | 20273227 | rolling_ols_w90 | ok | 0.112670 | 0.941666 | 0.980853 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed2_ewma_h40 | 20273227 | ewma_h40 | ok | 0.148219 | 0.935032 | 0.996794 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed2_shrinkage_i0.3_t1.0 | 20273227 | shrinkage_i0.3_t1.0 | ok | 0.105135 | 0.942858 | 0.973390 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed2_shrinkage_i0.3_csm | 20273227 | shrinkage_i0.3_csm | ok | -0.267931 | 0.126795 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed3_rolling_ols_w90 | 20274240 | rolling_ols_w90 | ok | -0.532651 | 0.096097 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed3_ewma_h40 | 20274240 | ewma_h40 | ok | -0.455660 | 0.108919 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed3_shrinkage_i0.3_t1.0 | 20274240 | shrinkage_i0.3_t1.0 | ok | -0.537312 | 0.095871 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed3_shrinkage_i0.3_csm | 20274240 | shrinkage_i0.3_csm | ok | -0.890644 | 0.079997 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed4_rolling_ols_w90 | 20275253 | rolling_ols_w90 | ok | 1.244259 | 0.807945 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed4_ewma_h40 | 20275253 | ewma_h40 | ok | 1.182034 | 0.797976 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed4_shrinkage_i0.3_t1.0 | 20275253 | shrinkage_i0.3_t1.0 | ok | 1.241764 | 0.807919 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed4_shrinkage_i0.3_csm | 20275253 | shrinkage_i0.3_csm | ok | 0.849246 | 0.815594 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed5_rolling_ols_w90 | 20276266 | rolling_ols_w90 | ok | 0.478287 | 0.921461 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed5_ewma_h40 | 20276266 | ewma_h40 | ok | 0.418900 | 0.926254 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed5_shrinkage_i0.3_t1.0 | 20276266 | shrinkage_i0.3_t1.0 | ok | 0.468913 | 0.921484 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed5_shrinkage_i0.3_csm | 20276266 | shrinkage_i0.3_csm | ok | 0.062948 | 0.945645 | 0.876368 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed6_rolling_ols_w90 | 20277279 | rolling_ols_w90 | ok | -0.635193 | 0.095255 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed6_ewma_h40 | 20277279 | ewma_h40 | ok | -0.505604 | 0.102081 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed6_shrinkage_i0.3_t1.0 | 20277279 | shrinkage_i0.3_t1.0 | ok | -0.637651 | 0.095090 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed6_shrinkage_i0.3_csm | 20277279 | shrinkage_i0.3_csm | ok | -1.000726 | 0.088767 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed7_rolling_ols_w90 | 20278292 | rolling_ols_w90 | ok | 0.246179 | 0.937839 | 0.999997 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed7_ewma_h40 | 20278292 | ewma_h40 | ok | 0.387141 | 0.930471 | 1.000000 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed7_shrinkage_i0.3_t1.0 | 20278292 | shrinkage_i0.3_t1.0 | ok | 0.234816 | 0.938621 | 0.999992 | True | SURVIVES_DEFLATION | True |
| STUDENT_T | STUDENT_T_seed7_shrinkage_i0.3_csm | 20278292 | shrinkage_i0.3_csm | ok | -0.188693 | 0.135388 | 0.000259 | False | DOES_NOT_SURVIVE_DEFLATION | True |
<!-- table:cell:end -->

---

## Cross-DGP Aggregates

<!-- table:cross:start -->
| Metric | Value |
|---|---|
| n_dgps | 5 |
| n_total_cells | 160 |
| n_total_ok_cells | 160 |
| n_total_error_cells | 0 |
| n_total_survive | 79 |
| n_dgps_replicating | 0 |
| all_dgps_neutrality_ok | True |
| all_dgps_survive | False |
<!-- table:cross:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Schema is bab_p41.stress_summary/1 (committed generator: scripts/bab_p41_stress.py) | True |
| All five DGPs labelled controlled synthetic; not real market data; not market profitability evidence | True |
| Deflation over n_trials_total=552 read-only from P38 WP1 (trial_enumeration.n_trials_total); never re-enumerated | True |
| Exactly 160 total cells across 5 DGPs (8 seeds each x 4 estimators) | True |
| Consolidated verdict is explicit: FRAGILE_DGP_DEPENDENT | True |
| Verdict is honest — may be ROBUST_ACROSS_DGPS, FRAGILE_DGP_DEPENDENT, or DOES_NOT_REPLICATE; no seed/parameter tuning to chase a positive result | True |
| All three neutrality invariants hold at every cell (model beta <= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15) | True |
| No demonstrated real-world profitability; synthetic-provenance caveat applies; nothing flipped | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** All five universes are
  controlled synthetic stimuli (BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns =
  `beta * BTC_return + idio`). They are **not real market data** and
  **not market profitability evidence** -- these results are **never market
  alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market
  ingestion (P28 WP3) requires a maintainer-supplied licensed CSV and is out
  of scope for P41.
- **Honest verdict, not a positive claim.** The consolidated verdict reports
  honestly whether BAB behaviour survives non-Gaussian idio across all five
  DGPs; it may be negative (`FRAGILE_DGP_DEPENDENT` or
  `DOES_NOT_REPLICATE`). The campaign does not claim the factor survives
  deflation universally.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.
- **Only `ROBUST_ACROSS_DGPS` justifies a follow-on real-data validation
  campaign, and only with explicit maintainer approval.**

---

## Next Steps

Campaign P41 concludes here with the consolidated five-DGP stress verdict.
The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P41):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p41_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
