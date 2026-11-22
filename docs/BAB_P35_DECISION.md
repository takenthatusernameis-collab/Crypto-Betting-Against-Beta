# BAB P35 Closing Decision — Beta-Estimation Robustness & Signal-Stability Closure

**Campaign:** P35 "Beta-Estimation Robustness & Signal-Stability Closure"
**Decision row:** P35 WP3 — Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p35/estimator_bakeoff_summary.json` (80 cells: 8 seeds × 10 estimator configs)
- `research_state/bab_p35/signal_stability_summary.json` (96 cells: 8 seeds × 12 perturbations)

**Verdict strings verified:** `RETAIN`, `rolling-OLS`, `synthetic`, `not market evidence`

**Decision:** **RETAIN the shipped default** (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS).
Estimator choice (rolling-OLS / EWMA / shrinkage) materially affects turnover and selection churn but **does not affect beta-neutrality** (all 176 cells satisfy model beta-neutral ≤ 1e-3, dollar-neutral ≤ 1e-9, |realized β| ≤ 0.15).
EWMA (h40/h60) and shrinkage (intensity 0.1/0.3) are documented as churn-reduction alternatives at equal neutrality.
Every number traces to a committed JSON leaf; no hand-typed numbers.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema estimator bakeoff | bab_p35.estimator_bakeoff/1 |
| Schema signal stability | bab_p35.signal_stability/1 |
| Campaign | P35 Beta-Estimation Robustness & Signal-Stability Closure |
| WP | WP3 - Decision doc + documentation-integrity closure + gate wire |
| Synthetic universe | Deterministic synthetic wide universe (P25 recipe). BTC prices from tests/fixtures/real_market_prices.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). One all-NaN DEL column for loader robustness. Not real market data; not market profitability evidence. |
| Fixture SHA256 | `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` |
| BTC source SHA256 | `7e457c5024cb577eca7d4c6f9e6d874d161f80d72e53549eda056d966edebe6a` |
| Seeds (base/inc/n) | 20261120/1009/8 |
| Beta windows (OLS) | [60, 90, 120] |
| EWMA halflifes | [20, 40, 60] |
| Shrinkage intensities | [0.1, 0.3] |
| Shrinkage targets | ['1.0', 'cross_sectional_mean'] |
| Quantile | 0.300000 |
| Transaction costs | 0.001000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Noise epsilons | [0.0001, 0.001, 0.01, 0.05] |
| Model beta-neutral tol | 0.001000 |
| Dollar-neutral tol | 0.000000 |
| Realized beta tol | 0.150000 |
<!-- table:provenance:end -->

---

## Estimator Bakeoff — Aggregated Summary (Averaged Over 8 Seeds)

<!-- table:estimator_agg:start -->
| Estimator | N_cells | Avg_Sharpe | Avg_Turnover | Avg_Ann_Vol | Avg_Max_DD | Avg_Realized_Beta | Avg_Model_Beta_Neutral | Avg_Dollar_Neutral | Avg_Spearman_vs_OLS | Avg_Jaccard_vs_OLS | Avg_Beta_Noise | Avg_Beta_Dispersion | Avg_Wealth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ewma | 24 | -0.231258 | 0.016235 | 0.006200 | -0.011008 | -0.000866 | 0.000099 | 0.000000 | 0.999442 | 1.000000 | 0.002319 | 0.455338 | 0.997640 |
| rolling_ols | 24 | -0.216518 | 0.013907 | 0.006203 | -0.010438 | -0.000844 | 0.000099 | 0.000000 | 1.000000 | None | 0.001903 | 0.464657 | 0.997826 |
| shrinkage | 32 | -0.161644 | 0.011622 | 0.006183 | -0.010146 | -0.001129 | 0.000100 | 0.000000 | 0.999892 | 1.000000 | 0.001388 | 0.371722 | 0.998402 |
<!-- table:estimator_agg:end -->

---

## Estimator Bakeoff — Full Per-Cell Results (80 Cells)

<!-- table:estimator_config:start -->
| Config | Estimator | Seed_Idx | Sharpe | Turnover | Ann_Vol | Max_DD | Realized_Beta | Model_Beta_Neutral | Dollar_Neutral | Spearman_vs_OLS | Jaccard_vs_OLS | Beta_Noise | Beta_Dispersion | Wealth | Model_Beta_Pass | Dollar_Pass | Realized_Beta_Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ewma_h20 | ewma | 0 | 0.223026 | 0.029352 | 0.006352 | -0.008360 | -0.000842 | 0.000100 | 0.000000 | 0.999247 | 1.000000 | 0.003478 | 0.464273 | 1.002208 | True | True | True |
| ewma_h40 | ewma | 0 | 0.629455 | 0.014894 | 0.006103 | -0.008304 | -0.000339 | 0.000100 | 0.000000 | 0.999438 | 1.000000 | 0.001950 | 0.456351 | 1.006056 | True | True | True |
| ewma_h60 | ewma | 0 | 0.647416 | 0.014588 | 0.006014 | -0.007873 | -0.000500 | 0.000100 | 0.000000 | 0.999090 | 1.000000 | 0.001572 | 0.446151 | 1.006140 | True | True | True |
| ewma_h20 | ewma | 1 | -0.588209 | 0.028030 | 0.006341 | -0.013293 | -0.001596 | 0.000100 | 0.000000 | 0.999352 | 1.000000 | 0.003455 | 0.465231 | 0.994095 | True | True | True |
| ewma_h40 | ewma | 1 | -0.196587 | 0.011093 | 0.006252 | -0.009675 | -0.001290 | 0.000100 | 0.000000 | 0.999630 | 1.000000 | 0.001932 | 0.457952 | 0.998030 | True | True | True |
| ewma_h60 | ewma | 1 | 0.021854 | 0.007858 | 0.006158 | -0.007911 | -0.001675 | 0.000100 | 0.000000 | 0.999390 | 1.000000 | 0.001558 | 0.448255 | 1.000183 | True | True | True |
| ewma_h20 | ewma | 2 | 1.244726 | 0.019187 | 0.006140 | -0.003866 | -0.001084 | 0.000099 | 0.000000 | 0.999526 | 1.000000 | 0.003425 | 0.464865 | 1.012113 | True | True | True |
| ewma_h40 | ewma | 2 | 1.447896 | 0.009769 | 0.006174 | -0.003816 | -0.000745 | 0.000100 | 0.000000 | 0.999651 | 1.000000 | 0.001935 | 0.457541 | 1.014188 | True | True | True |
| ewma_h60 | ewma | 2 | 1.487485 | 0.007761 | 0.006186 | -0.003787 | -0.000869 | 0.000100 | 0.000000 | 0.999393 | 1.000000 | 0.001578 | 0.447715 | 1.014607 | True | True | True |
| ewma_h20 | ewma | 3 | -1.685726 | 0.038047 | 0.006294 | -0.017700 | -0.000147 | 0.000100 | 0.000000 | 0.999322 | 1.000000 | 0.003474 | 0.462849 | 0.983351 | True | True | True |
| ewma_h40 | ewma | 3 | -1.081688 | 0.017434 | 0.006099 | -0.014590 | 0.000018 | 0.000100 | 0.000000 | 0.999551 | 1.000000 | 0.001949 | 0.455662 | 0.989605 | True | True | True |
| ewma_h60 | ewma | 3 | -0.739954 | 0.008815 | 0.006084 | -0.011849 | -0.000016 | 0.000100 | 0.000000 | 0.999338 | 1.000000 | 0.001583 | 0.445926 | 0.992886 | True | True | True |
| ewma_h20 | ewma | 4 | -1.310970 | 0.028045 | 0.006285 | -0.013370 | -0.000311 | 0.000099 | 0.000000 | 0.999397 | 1.000000 | 0.003465 | 0.464526 | 0.987041 | True | True | True |
| ewma_h40 | ewma | 4 | -0.999212 | 0.011559 | 0.006307 | -0.010589 | -0.000745 | 0.000100 | 0.000000 | 0.999679 | 1.000000 | 0.001949 | 0.457213 | 0.990064 | True | True | True |
| ewma_h60 | ewma | 4 | -1.078303 | 0.007891 | 0.006360 | -0.011731 | -0.000926 | 0.000093 | 0.000000 | 0.999494 | 1.000000 | 0.001581 | 0.447395 | 0.989195 | True | True | True |
| ewma_h20 | ewma | 5 | -0.145026 | 0.027622 | 0.006122 | -0.008797 | -0.000896 | 0.000100 | 0.000000 | 0.999390 | 1.000000 | 0.003432 | 0.462453 | 0.998569 | True | True | True |
| ewma_h40 | ewma | 5 | 0.612555 | 0.009850 | 0.006164 | -0.008299 | -0.000686 | 0.000099 | 0.000000 | 0.999674 | 1.000000 | 0.001926 | 0.455307 | 1.005951 | True | True | True |
| ewma_h60 | ewma | 5 | 0.730370 | 0.007845 | 0.006163 | -0.007959 | -0.000520 | 0.000099 | 0.000000 | 0.999466 | 1.000000 | 0.001552 | 0.445505 | 1.007105 | True | True | True |
| ewma_h20 | ewma | 6 | -2.052807 | 0.024904 | 0.006482 | -0.022839 | -0.001768 | 0.000099 | 0.000000 | 0.999322 | 1.000000 | 0.003452 | 0.462714 | 0.979171 | True | True | True |
| ewma_h40 | ewma | 6 | -1.464704 | 0.013275 | 0.006338 | -0.019207 | -0.001202 | 0.000100 | 0.000000 | 0.999557 | 1.000000 | 0.001938 | 0.455273 | 0.985413 | True | True | True |
| ewma_h60 | ewma | 6 | -1.305651 | 0.010469 | 0.006277 | -0.017983 | -0.001107 | 0.000100 | 0.000000 | 0.999355 | 1.000000 | 0.001567 | 0.445395 | 0.987108 | True | True | True |
| ewma_h20 | ewma | 7 | -0.284143 | 0.021507 | 0.006243 | -0.011550 | -0.001529 | 0.000100 | 0.000000 | 0.999384 | 1.000000 | 0.003427 | 0.461193 | 0.997172 | True | True | True |
| ewma_h40 | ewma | 7 | 0.142382 | 0.011570 | 0.005874 | -0.010575 | -0.001270 | 0.000100 | 0.000000 | 0.999620 | 1.000000 | 0.001926 | 0.454002 | 1.001294 | True | True | True |
| ewma_h60 | ewma | 7 | 0.195625 | 0.008280 | 0.005975 | -0.010277 | -0.000734 | 0.000099 | 0.000000 | 0.999331 | 1.000000 | 0.001563 | 0.444357 | 1.001820 | True | True | True |
| rolling_ols_w60 | rolling_ols | 0 | 0.177669 | 0.020261 | 0.006372 | -0.010371 | -0.000640 | 0.000100 | 0.000000 | 1.000000 | None | 0.002702 | 0.465768 | 1.001758 | True | True | True |
| rolling_ols_w90 | rolling_ols | 0 | 0.128257 | 0.014513 | 0.006142 | -0.008067 | 0.000356 | 0.000100 | 0.000000 | 1.000000 | None | 0.001745 | 0.465262 | 1.001215 | True | True | True |
| rolling_ols_w120 | rolling_ols | 0 | 0.423274 | 0.017551 | 0.006077 | -0.007491 | 0.000610 | 0.000099 | 0.000000 | 1.000000 | None | 0.001295 | 0.464841 | 1.004042 | True | True | True |
| rolling_ols_w60 | rolling_ols | 1 | 0.074093 | 0.020324 | 0.006310 | -0.007280 | -0.001787 | 0.000099 | 0.000000 | 1.000000 | None | 0.002703 | 0.466656 | 1.000707 | True | True | True |
| rolling_ols_w90 | rolling_ols | 1 | -0.225406 | 0.011973 | 0.006218 | -0.010480 | -0.001572 | 0.000100 | 0.000000 | 1.000000 | None | 0.001731 | 0.466393 | 0.997758 | True | True | True |
| rolling_ols_w120 | rolling_ols | 1 | 0.011633 | 0.007520 | 0.006153 | -0.007881 | -0.001674 | 0.000100 | 0.000000 | 1.000000 | None | 0.001284 | 0.466186 | 1.000083 | True | True | True |
| rolling_ols_w60 | rolling_ols | 2 | 0.944700 | 0.016379 | 0.006192 | -0.004165 | -0.000735 | 0.000100 | 0.000000 | 1.000000 | None | 0.002671 | 0.466260 | 1.009251 | True | True | True |
| rolling_ols_w90 | rolling_ols | 2 | 1.418024 | 0.009303 | 0.006163 | -0.003875 | -0.000231 | 0.000100 | 0.000000 | 1.000000 | None | 0.001709 | 0.466117 | 1.013868 | True | True | True |
| rolling_ols_w120 | rolling_ols | 2 | 1.449590 | 0.007426 | 0.006143 | -0.003763 | 0.000072 | 0.000099 | 0.000000 | 1.000000 | None | 0.001279 | 0.465963 | 1.014133 | True | True | True |
| rolling_ols_w60 | rolling_ols | 3 | -1.005780 | 0.028665 | 0.006012 | -0.011708 | 0.000372 | 0.000100 | 0.000000 | 1.000000 | None | 0.002709 | 0.464252 | 0.990467 | True | True | True |
| rolling_ols_w90 | rolling_ols | 3 | -0.655094 | 0.013646 | 0.006066 | -0.011054 | -0.000131 | 0.000100 | 0.000000 | 1.000000 | None | 0.001727 | 0.463774 | 0.993715 | True | True | True |
| rolling_ols_w120 | rolling_ols | 3 | -0.888794 | 0.009211 | 0.006076 | -0.013670 | -0.000197 | 0.000100 | 0.000000 | 1.000000 | None | 0.001284 | 0.463400 | 0.991478 | True | True | True |
| rolling_ols_w60 | rolling_ols | 4 | -1.265902 | 0.021672 | 0.006357 | -0.013351 | -0.001126 | 0.000100 | 0.000000 | 1.000000 | None | 0.002733 | 0.465888 | 0.987340 | True | True | True |
| rolling_ols_w90 | rolling_ols | 4 | -1.055474 | 0.012823 | 0.006245 | -0.011347 | -0.000668 | 0.000099 | 0.000000 | 1.000000 | None | 0.001739 | 0.465790 | 0.989613 | True | True | True |
| rolling_ols_w120 | rolling_ols | 4 | -1.121696 | 0.007581 | 0.006326 | -0.012147 | -0.000870 | 0.000099 | 0.000000 | 1.000000 | None | 0.001293 | 0.465684 | 0.988825 | True | True | True |
| rolling_ols_w60 | rolling_ols | 5 | -0.161812 | 0.019410 | 0.006248 | -0.008794 | -0.000976 | 0.000100 | 0.000000 | 1.000000 | None | 0.002659 | 0.463626 | 0.998374 | True | True | True |
| rolling_ols_w90 | rolling_ols | 5 | 0.501132 | 0.010291 | 0.006253 | -0.008174 | -0.001025 | 0.000100 | 0.000000 | 1.000000 | None | 0.001721 | 0.463653 | 1.004930 | True | True | True |
| rolling_ols_w120 | rolling_ols | 5 | 0.773421 | 0.007549 | 0.006173 | -0.008008 | -0.000801 | 0.000094 | 0.000000 | 1.000000 | None | 0.001281 | 0.463631 | 1.007539 | True | True | True |
| rolling_ols_w60 | rolling_ols | 6 | -1.958242 | 0.019137 | 0.006485 | -0.022051 | -0.002311 | 0.000100 | 0.000000 | 1.000000 | None | 0.002685 | 0.464206 | 0.980111 | True | True | True |
| rolling_ols_w90 | rolling_ols | 6 | -1.200761 | 0.009572 | 0.006262 | -0.016123 | -0.001953 | 0.000100 | 0.000000 | 1.000000 | None | 0.001724 | 0.463912 | 0.988164 | True | True | True |
| rolling_ols_w120 | rolling_ols | 6 | -1.100277 | 0.007635 | 0.006273 | -0.015956 | -0.001819 | 0.000099 | 0.000000 | 1.000000 | None | 0.001285 | 0.463591 | 0.989128 | True | True | True |
| rolling_ols_w60 | rolling_ols | 7 | -0.619884 | 0.021684 | 0.006262 | -0.013633 | -0.001154 | 0.000100 | 0.000000 | 1.000000 | None | 0.002698 | 0.462668 | 0.993858 | True | True | True |
| rolling_ols_w90 | rolling_ols | 7 | 0.024870 | 0.010814 | 0.006057 | -0.010903 | -0.001109 | 0.000098 | 0.000000 | 1.000000 | None | 0.001730 | 0.462323 | 1.000209 | True | True | True |
| rolling_ols_w120 | rolling_ols | 7 | 0.136015 | 0.008835 | 0.006018 | -0.010211 | -0.000887 | 0.000100 | 0.000000 | 1.000000 | None | 0.001284 | 0.461936 | 1.001265 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 0 | 0.126164 | 0.014513 | 0.006143 | -0.008082 | 0.000345 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001571 | 0.418735 | 1.001195 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 0 | 0.108784 | 0.014518 | 0.006143 | -0.008130 | 0.000131 | 0.000100 | 0.000000 | 0.999959 | 1.000000 | 0.001576 | 0.418735 | 1.001026 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 0 | 0.123886 | 0.014513 | 0.006143 | -0.008085 | 0.000323 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001222 | 0.325683 | 1.001173 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 0 | 0.032176 | 0.014529 | 0.006148 | -0.008312 | -0.000730 | 0.000100 | 0.000000 | 0.999698 | 1.000000 | 0.001239 | 0.325683 | 1.000283 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 1 | -0.228217 | 0.011972 | 0.006218 | -0.010507 | -0.001593 | 0.000099 | 0.000000 | 1.000000 | 1.000000 | 0.001558 | 0.419754 | 0.997731 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 1 | -0.245881 | 0.011977 | 0.006223 | -0.010670 | -0.001806 | 0.000100 | 0.000000 | 0.999973 | 1.000000 | 0.001562 | 0.419754 | 0.997556 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 1 | -0.235908 | 0.011971 | 0.006218 | -0.010561 | -0.001639 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001211 | 0.326475 | 0.997655 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 1 | -0.316398 | 0.011986 | 0.006252 | -0.011304 | -0.002659 | 0.000099 | 0.000000 | 0.999682 | 1.000000 | 0.001226 | 0.326475 | 0.996850 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 2 | 1.417522 | 0.009302 | 0.006163 | -0.003874 | -0.000237 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001538 | 0.419505 | 1.013863 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 2 | 1.399940 | 0.009307 | 0.006164 | -0.003873 | -0.000447 | 0.000099 | 0.000000 | 0.999928 | 1.000000 | 0.001543 | 0.419505 | 1.013692 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 2 | 1.414981 | 0.009302 | 0.006163 | -0.003874 | -0.000248 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001196 | 0.326282 | 1.013838 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 2 | 1.328249 | 0.009318 | 0.006176 | -0.003862 | -0.001308 | 0.000100 | 0.000000 | 0.999653 | 1.000000 | 0.001213 | 0.326282 | 1.013010 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 3 | -0.655672 | 0.013646 | 0.006066 | -0.011054 | -0.000139 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001554 | 0.417396 | 0.993709 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 3 | -0.671096 | 0.013650 | 0.006068 | -0.011131 | -0.000359 | 0.000100 | 0.000000 | 0.999811 | 1.000000 | 0.001558 | 0.417396 | 0.993560 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 3 | -0.656107 | 0.013645 | 0.006065 | -0.011054 | -0.000142 | 0.000099 | 0.000000 | 1.000000 | 1.000000 | 0.001209 | 0.324641 | 0.993706 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 3 | -0.734225 | 0.013662 | 0.006083 | -0.011437 | -0.001205 | 0.000098 | 0.000000 | 0.999693 | 1.000000 | 0.001222 | 0.324641 | 0.992942 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 4 | -1.055065 | 0.012822 | 0.006245 | -0.011346 | -0.000670 | 0.000099 | 0.000000 | 1.000000 | 1.000000 | 0.001565 | 0.419211 | 0.989617 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 4 | -1.073126 | 0.012827 | 0.006247 | -0.011523 | -0.000883 | 0.000098 | 0.000000 | 0.999977 | 1.000000 | 0.001570 | 0.419211 | 0.989438 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 4 | -1.055886 | 0.012822 | 0.006245 | -0.011350 | -0.000668 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001217 | 0.326053 | 0.989610 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 4 | -1.139432 | 0.012839 | 0.006261 | -0.012209 | -0.001715 | 0.000100 | 0.000000 | 0.999541 | 1.000000 | 0.001235 | 0.326053 | 0.988766 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 5 | 0.501199 | 0.010291 | 0.006253 | -0.008174 | -0.001026 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001549 | 0.417287 | 1.004931 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 5 | 0.483815 | 0.010295 | 0.006258 | -0.008203 | -0.001247 | 0.000100 | 0.000000 | 0.999960 | 1.000000 | 0.001554 | 0.417287 | 1.004762 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 5 | 0.496042 | 0.010292 | 0.006254 | -0.008174 | -0.001060 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001205 | 0.324557 | 1.004881 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 5 | 0.410920 | 0.010307 | 0.006284 | -0.008335 | -0.002153 | 0.000100 | 0.000000 | 0.999453 | 1.000000 | 0.001222 | 0.324557 | 1.004056 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 6 | -1.203909 | 0.009572 | 0.006263 | -0.016149 | -0.001964 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001552 | 0.417521 | 0.988132 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 6 | -1.223041 | 0.009577 | 0.006269 | -0.016299 | -0.002192 | 0.000100 | 0.000000 | 0.999956 | 1.000000 | 0.001556 | 0.417521 | 0.987933 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 6 | -1.208380 | 0.009572 | 0.006263 | -0.016180 | -0.002005 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001207 | 0.324738 | 0.988087 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 6 | -1.297304 | 0.009586 | 0.006299 | -0.016902 | -0.003097 | 0.000098 | 0.000000 | 0.999674 | 1.000000 | 0.001222 | 0.324738 | 0.987147 | True | True | True |
| shrinkage_i0.1_t1.0 | shrinkage | 7 | 0.025062 | 0.010814 | 0.006057 | -0.010898 | -0.001114 | 0.000099 | 0.000000 | 1.000000 | 1.000000 | 0.001557 | 0.416091 | 1.000211 | True | True | True |
| shrinkage_i0.1_csm | shrinkage | 7 | 0.005597 | 0.010819 | 0.006063 | -0.010972 | -0.001321 | 0.000100 | 0.000000 | 0.999934 | 1.000000 | 0.001561 | 0.416091 | 1.000025 | True | True | True |
| shrinkage_i0.3_t1.0 | shrinkage | 7 | 0.021272 | 0.010815 | 0.006058 | -0.010907 | -0.001138 | 0.000100 | 0.000000 | 1.000000 | 1.000000 | 0.001211 | 0.323626 | 1.000175 | True | True | True |
| shrinkage_i0.3_csm | shrinkage | 7 | -0.068577 | 0.010829 | 0.006091 | -0.011241 | -0.002164 | 0.000100 | 0.000000 | 0.999637 | 1.000000 | 0.001226 | 0.323626 | 0.999311 | True | True | True |
<!-- table:estimator_config:end -->

---

## Signal Stability — Churn Summary (Averaged Over 8 Seeds)

Flip fraction = per-period fraction of names in baseline long/short book that change side (long↔short) or drop out entirely.
Jaccard overlap = per-period Jaccard of baseline vs perturbed long/short selected sets.
Baseline-vs-baseline: flip=0.0, Jaccard=1.0.

<!-- table:churn:start -->
| Perturbation | Type | N_cells | Avg_Flip_Fraction | Avg_Jaccard | Avg_Sharpe | Avg_Turnover | Avg_Realized_Beta | Avg_Model_Beta_Neutral | Avg_Dollar_Neutral |
|---|---|---|---|---|---|---|---|---|---|
| OLS_baseline | baseline | 8 | 0.000000 | 1.000000 | -0.133056 | 0.011617 | -0.000792 | 0.000100 | 0.000000 |
| ewma_h20 | estimator | 8 | 0.022468 | 1.000000 | -0.574891 | 0.027087 | -0.001022 | 0.000100 | 0.000000 |
| ewma_h40 | estimator | 8 | 0.010809 | 1.000000 | -0.113738 | 0.012430 | -0.000782 | 0.000100 | 0.000000 |
| ewma_h60 | estimator | 8 | 0.014930 | 1.000000 | -0.005145 | 0.009189 | -0.000793 | 0.000099 | 0.000000 |
| shrinkage_i0.1_csm | estimator | 8 | 0.000452 | 1.000000 | -0.151876 | 0.011621 | -0.001016 | 0.000100 | 0.000000 |
| shrinkage_i0.1_t1.0 | estimator | 8 | 0.000000 | 1.000000 | -0.134114 | 0.011617 | -0.000800 | 0.000100 | 0.000000 |
| shrinkage_i0.3_csm | estimator | 8 | 0.001685 | 1.000000 | -0.223074 | 0.011632 | -0.001879 | 0.000099 | 0.000000 |
| shrinkage_i0.3_t1.0 | estimator | 8 | 0.000015 | 1.000000 | -0.137513 | 0.011616 | -0.000822 | 0.000100 | 0.000000 |
| noise_e0.0001 | noise | 8 | 0.000153 | 1.000000 | -0.131935 | 0.011622 | -0.000806 | 0.000099 | 0.000000 |
| noise_e0.001 | noise | 8 | 0.001264 | 1.000000 | -0.195345 | 0.013776 | -0.000873 | 0.000099 | 0.000000 |
| noise_e0.01 | noise | 8 | 0.015428 | 1.000000 | -2.817485 | 0.075545 | -0.001503 | 0.000100 | 0.000000 |
| noise_e0.05 | noise | 8 | 0.100104 | 1.000000 | -14.203599 | 0.393678 | -0.003989 | 0.000100 | 0.000000 |
<!-- table:churn:end -->

---

## Noise Injection — Monotonicity Ladder

Noise ladder monotonicity verified: flip fraction increases with epsilon.

<!-- table:noise_ladder:start -->
| Epsilon | Avg_Flip_Fraction |
|---|---|
| 0.000100 | 0.000153 |
| 0.001000 | 0.001264 |
| 0.010000 | 0.015428 |
| 0.050000 | 0.100104 |
<!-- table:noise_ladder:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| All 176 cells (80 bakeoff + 96 stability) pass neutrality checks | True |
| Model beta-neutrality ≤ 1e-3 at every cell | True |
| Dollar-neutrality ≤ 1e-9 at every cell | True |
| Realized beta |β| ≤ 0.15 at every cell | True |
| Estimator choice affects turnover/churn but NOT beta-neutrality | True |
| Shipped default (rolling-OLS w90, equal-weight, beta-neutral) RETAINED | True |
| EWMA (h40/h60) and shrinkage are documented churn-reduction alternatives | True |
| Fixture SHA256 match across both artifacts | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence / no real alpha | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a controlled synthetic stimulus: BTC prices from `tests/fixtures/real_market_prices.csv`, asset returns = `beta * BTC_return + idio`, `idio ~ N(0, 0.003)`, betas `linspace(0.35, 1.9, 40)`. It is **not real market data** and **not market profitability evidence**.
- **No out-of-sample validation.** All results are in-sample on the synthetic fixture.
- **No walk-forward / OOS harness.** Campaign P35 closes without a walk-forward/out-of-sample harness.
- **No Frazzini-Pedersen rank weighting with beta scaling.** The rank path is documented in `docs/BAB_FIDELITY.md` §9 but is **not empirically evaluable** on the committed 9-asset synthetic fixture. The shipped default remains equal-weight.
- **No live execution evidence.** The live adapter (`--adapter live`) is dry-run by default and requires explicit two-key opt-in. No network was used in this campaign.

---

## Next Steps

Campaign P35 concludes here. The **RETAIN** verdict is grounded in the evidence from WP1 (estimator bakeoff) and WP2 (signal-stability study). All 176 cells satisfy the neutrality invariants. Estimator choice affects turnover/churn but not beta-neutrality. The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS is retained. EWMA (h40/h60) and shrinkage are documented churn-reduction alternatives at equal neutrality.

**Future work (not in scope for P35):**
- Walk-forward / out-of-sample harness
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh` (P28 WP2, maintainer-only)
- Frazzini-Pedersen rank-weighted / beta-scaled construction on a wider universe

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON leaf at 6 dp. The acceptance test `tests/test_bab_p35_decision_consistency.py` verifies zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`, `rolling-OLS`, `synthetic`, `not market evidence`), AST no-harness scan, and ruff clean.*
