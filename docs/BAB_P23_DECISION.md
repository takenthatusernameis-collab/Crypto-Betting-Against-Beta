# BAB P23 — Decision report

**Campaign:** P23 "Breadth and instability stress" · **Verdict:** **NO-GO for market deployment**. The evidence is a controlled synthetic stimulus with known ground truth; it is not market evidence, not real market data, and never market alpha. No demonstrated real-world profitability is established here, and this is not a demonstrated profitable strategy.

This is the decision-grade closing document for campaign P23. It consumes the committed P23 JSON artifacts read-only, re-renders every published table from them, never re-runs a research harness and never edits an earlier artifact. Every numeric table cell is machine-matched to a committed JSON field at six decimal places by `tests/test_bab_p23_decision_consistency.py`; the unmatched-cell count is zero.

## Provenance

Sources: `research_state/bab_p23/charter.json`, `research_state/bab_p23/breadth_ladder.json`, `research_state/bab_p23/beta_drift.json`, `research_state/bab_p23/short_haircut.json`, and `research_state/bab_p21/rank_eval.json`. The universe is the frozen P21 planted/null pair. Both panels are sha256-pinned and the reference seed reproduces the committed P21 panel hashes.

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Charter schema | bab_p23.charter/1 |
| Breadth ladder schema | bab_p23.breadth_ladder/1 |
| Beta drift schema | bab_p23.beta_drift/1 |
| Short haircut schema | bab_p23.short_haircut/1 |
| Campaign | P23 |
| Charter question | Does the BAB estimator survive breadth concentration, beta-estimation drift and crypto short-availability scarcity? |
| Certified by prior campaign | Does the BAB estimator survive repeated null universes, nonlinear market impact and capacity constraints? Yes on controlled synthetic evidence, and the market verdict stays NO-GO. |
| Universe seed | 20261118 |
| Reference universe seed | 20261118 |
| Synthetic | True |
| Licensed data required | True |
| Not market evidence | True |
| Artifact gated | True |
| Nominal slack | 0.050000 |
| Planted panel sha256 | `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda` |
| Null panel sha256 | `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b` |
| Reference panel shas matched | True |
<!-- table:provenance:end -->

## Breadth ladder (WP1)

The breadth ladder tests the estimator as the cross-section widens from 9 to 41 assets, selected by evenly spaced beta-spanning indices. Planted recovery is strictly positive at every rung for both weightings; null recovery is exactly zero everywhere. All 541 active rows are preserved at every rung.

<!-- table:breadth:start -->
| breadth | variant | weighting | active_rows | recovery_mean | recovery_frac_positive | gross_max | min_leg_beta | gross_sharpe | wealth |
|---|---|---|---|---|---|---|---|---|---|
| 9 | planted | equal | 541 | 0.000852 | 1.000000 | 0.881117 | 1.364515 | 11.849343 | 1.627791 |
| 9 | planted | rank | 541 | 0.019102 | 1.000000 | 2.627291 | 0.466667 | 38.472484 | 31548.052226 |
| 9 | null | equal | 541 | 0.000000 | 0.000000 | 0.881117 | 1.364515 | 0.696904 | 1.027840 |
| 9 | null | rank | 541 | 0.000000 | 0.000000 | 2.627291 | 0.466667 | 0.935453 | 1.155184 |
| 17 | planted | equal | 541 | 0.000574 | 1.000000 | 0.908097 | 1.412831 | 9.352958 | 1.378100 |
| 17 | planted | rank | 541 | 0.018663 | 1.000000 | 2.558507 | 0.475200 | 41.365882 | 23997.088351 |
| 17 | null | equal | 541 | 0.000000 | 0.000000 | 0.908097 | 1.412831 | 0.323055 | 1.010705 |
| 17 | null | rank | 541 | 0.000000 | 0.000000 | 2.558507 | 0.475200 | 0.873485 | 1.108250 |
| 25 | planted | equal | 541 | 0.000426 | 1.000000 | 0.901197 | 1.430700 | 8.609136 | 1.285226 |
| 25 | planted | rank | 541 | 0.018240 | 1.000000 | 2.507432 | 0.487347 | 42.600863 | 19120.623173 |
| 25 | null | equal | 541 | 0.000000 | 0.000000 | 0.901197 | 1.430700 | 0.738474 | 1.021241 |
| 25 | null | rank | 541 | 0.000000 | 0.000000 | 2.507432 | 0.487347 | 0.980300 | 1.104535 |
| 33 | planted | equal | 541 | 0.000310 | 0.996303 | 0.837902 | 1.444941 | 7.549534 | 1.190974 |
| 33 | planted | rank | 541 | 0.017361 | 1.000000 | 2.428612 | 0.505455 | 43.961525 | 11367.799782 |
| 33 | null | equal | 541 | 0.000000 | 0.000000 | 0.837902 | 1.444941 | 0.324571 | 1.007344 |
| 33 | null | rank | 541 | 0.000000 | 0.000000 | 2.428612 | 0.505455 | 0.569659 | 1.045939 |
| 41 | planted | equal | 541 | 0.000261 | 0.996303 | 0.837141 | 1.447792 | 7.034781 | 1.167118 |
| 41 | planted | rank | 541 | 0.017360 | 1.000000 | 2.414949 | 0.507692 | 44.378201 | 11401.093638 |
| 41 | null | equal | 541 | 0.000000 | 0.000000 | 0.837141 | 1.447792 | 0.639801 | 1.013905 |
| 41 | null | rank | 541 | 0.000000 | 0.000000 | 2.414949 | 0.507692 | 0.649924 | 1.049395 |
<!-- table:breadth:end -->

## Beta-estimation drift grid (WP2)

The drift grid tests the estimator across four beta windows (60, 90, 120, 180) and three drift thresholds (0.0001, 0.0005, 0.001) using a relative drift model with `drift_scale = 0.1` (±6% relative beta displacement at δ=1e-3). All 48 cells are reported; every planted cell is strictly positive, every null cell is exactly zero. The worst planted seed recovery is `+0.000201` at beta_window=90, drift_threshold=0.001, weighting=equal. Rank recovery degrades monotonically from δ=1e-4 (`+0.017367`) to δ=1e-3 (`+0.017330`).

<!-- table:drift:start -->
| beta_window | drift_threshold | variant | weighting | active_rows_min | recovery_mean | recovery_min | recovery_positive_seed_fraction | gross_max | min_leg_beta |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 0.000100 | planted | equal | 541 | 0.000255 | 0.000247 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.000100 | planted | rank | 541 | 0.017359 | 0.017347 | 1.000000 | 2.441366 | 0.507692 |
| 60 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.441366 | 0.507692 |
| 60 | 0.000500 | planted | equal | 541 | 0.000261 | 0.000234 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.000500 | planted | rank | 541 | 0.017349 | 0.017290 | 1.000000 | 2.444202 | 0.507692 |
| 60 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.444202 | 0.507692 |
| 60 | 0.001000 | planted | equal | 541 | 0.000261 | 0.000201 | 1.000000 | 0.000000 | 0.000000 |
| 60 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 60 | 0.001000 | planted | rank | 541 | 0.017331 | 0.017216 | 1.000000 | 2.447716 | 0.507692 |
| 60 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.447716 | 0.507692 |
| 90 | 0.000100 | planted | equal | 541 | 0.000262 | 0.000256 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.000100 | planted | rank | 541 | 0.017358 | 0.017347 | 1.000000 | 2.415569 | 0.507692 |
| 90 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.415569 | 0.507692 |
| 90 | 0.000500 | planted | equal | 541 | 0.000262 | 0.000234 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.000500 | planted | rank | 541 | 0.017347 | 0.017293 | 1.000000 | 2.422654 | 0.507692 |
| 90 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.422654 | 0.507692 |
| 90 | 0.001000 | planted | equal | 541 | 0.000263 | 0.000206 | 1.000000 | 0.000000 | 0.000000 |
| 90 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 90 | 0.001000 | planted | rank | 541 | 0.017330 | 0.017219 | 1.000000 | 2.431671 | 0.507692 |
| 90 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.431671 | 0.507692 |
| 120 | 0.000100 | planted | equal | 541 | 0.000262 | 0.000255 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.000100 | planted | rank | 541 | 0.017362 | 0.017351 | 1.000000 | 2.410854 | 0.510833 |
| 120 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.410854 | 0.510833 |
| 120 | 0.000500 | planted | equal | 541 | 0.000263 | 0.000233 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.000500 | planted | rank | 541 | 0.017352 | 0.017301 | 1.000000 | 2.412671 | 0.507692 |
| 120 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.412671 | 0.507692 |
| 120 | 0.001000 | planted | equal | 541 | 0.000266 | 0.000206 | 1.000000 | 0.000000 | 0.000000 |
| 120 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 120 | 0.001000 | planted | rank | 541 | 0.017336 | 0.017230 | 1.000000 | 2.414938 | 0.507692 |
| 120 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.414938 | 0.507692 |
| 180 | 0.000100 | planted | equal | 541 | 0.000263 | 0.000258 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.000100 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.000100 | planted | rank | 541 | 0.017367 | 0.017358 | 1.000000 | 2.398736 | 0.510833 |
| 180 | 0.000100 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.398736 | 0.510833 |
| 180 | 0.000500 | planted | equal | 541 | 0.000263 | 0.000235 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.000500 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.000500 | planted | rank | 541 | 0.017359 | 0.017312 | 1.000000 | 2.401045 | 0.510833 |
| 180 | 0.000500 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.401045 | 0.510833 |
| 180 | 0.001000 | planted | equal | 541 | 0.000269 | 0.000213 | 1.000000 | 0.000000 | 0.000000 |
| 180 | 0.001000 | null | equal | 541 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 180 | 0.001000 | planted | rank | 541 | 0.017345 | 0.017249 | 1.000000 | 2.404112 | 0.510833 |
| 180 | 0.001000 | null | rank | 541 | 0.000000 | 0.000000 | 0.000000 | 2.404112 | 0.510833 |
<!-- table:drift:end -->

### Drift zero-reference (matches P21 and WP2 at 6 dp)

<!-- table:drift_zero_reference:start -->
| variant | weighting | committed_p21_recovery | drift_zero_recovery | matches_at_6dp |
|---|---|---|---|---|
| null | equal | 0.000000 | 0.000000 | True |
| null | rank | 0.000000 | 0.000000 | True |
| planted | equal | 0.000261 | 0.000261 | True |
| planted | rank | 0.017360 | 0.017360 | True |
<!-- table:drift_zero_reference:end -->

## Short-availability haircut ladder (WP3)

The haircut ladder tests short-availability stress at five haircut levels (0.0, 0.1, 0.25, 0.5, 0.75) across 20 seeds × 2 weightings × 2 variants = 400 book runs. Unavailable shorts are dropped and never re-levered; rows whose short book is wiped out are flattened and reported via `per_seed_degenerate_rows`. The zero-haircut baseline matches P21 and WP2 at 6 dp. Planted recovery is strictly positive on every non-censored seed. Null recovery is exactly zero everywhere. One cell is censored: rank `h=0.75` (both variants) on seed `20261245` loses its entire short book (0.75¹² ≈ 3.2% draw), so `active_rows_min = 0`, `degenerate_rows_max = 541`, `censor_reason = "no_active_rows_after_short_availability_restriction"`.

<!-- table:haircut:start -->
| haircut | variant | weighting | active_rows_min | availability_mean | short_survival_mean | recovery_mean | recovery_min | recovery_positive_seed_fraction | costed_sharpe_mean | costed_sharpe_non_increasing | censored | censor_reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000000 | planted | equal | 541 | 1.000000 | 1.000000 | 0.000261 | 0.000261 | 1.000000 | 7.034781 | True | False | None |
| 0.000000 | null | equal | 541 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.639801 | True | False | None |
| 0.000000 | planted | rank | 541 | 1.000000 | 1.000000 | 0.017360 | 0.017360 | 1.000000 | 44.378201 | True | False | None |
| 0.000000 | null | rank | 541 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.649924 | True | False | None |
| 0.100000 | planted | equal | 541 | 0.904878 | 0.895833 | 0.000357 | 0.000179 | 1.000000 | -993.970148 | True | False | None |
| 0.100000 | null | equal | 541 | 0.904878 | 0.895833 | 0.000000 | 0.000000 | 0.000000 | -1011.674983 | True | False | None |
| 0.100000 | planted | rank | 541 | 0.904878 | 0.888462 | 0.017103 | 0.016528 | 1.000000 | -69.059967 | True | False | None |
| 0.100000 | null | rank | 541 | 0.904878 | 0.888462 | 0.000000 | 0.000000 | 0.000000 | -316.091723 | True | False | None |
| 0.250000 | planted | equal | 541 | 0.734146 | 0.718750 | 0.000517 | 0.000228 | 1.000000 | -2495.477541 | True | False | None |
| 0.250000 | null | equal | 541 | 0.734146 | 0.718750 | 0.000000 | 0.000000 | 0.000000 | -2530.147157 | True | False | None |
| 0.250000 | planted | rank | 541 | 0.734146 | 0.665385 | 0.016615 | 0.016052 | 1.000000 | -239.217220 | True | False | None |
| 0.250000 | null | rank | 541 | 0.734146 | 0.665385 | 0.000000 | 0.000000 | 0.000000 | -791.204195 | True | False | None |
| 0.500000 | planted | equal | 541 | 0.479268 | 0.452083 | 0.000836 | 0.000372 | 1.000000 | -4997.989862 | True | False | None |
| 0.500000 | null | equal | 541 | 0.479268 | 0.452083 | 0.000000 | 0.000000 | 0.000000 | -5060.934115 | True | False | None |
| 0.500000 | planted | rank | 541 | 0.479268 | 0.411538 | 0.016103 | 0.015449 | 1.000000 | -522.812641 | True | False | None |
| 0.500000 | null | rank | 541 | 0.479268 | 0.411538 | 0.000000 | 0.000000 | 0.000000 | -1583.058313 | True | False | None |
| 0.750000 | planted | equal | 541 | 0.228049 | 0.225000 | 0.001129 | 0.000955 | 1.000000 | -7500.502184 | True | False | None |
| 0.750000 | null | equal | 541 | 0.228049 | 0.225000 | 0.000000 | 0.000000 | 0.000000 | -7591.721073 | True | False | None |
| 0.750000 | planted | rank | 0 | 0.228049 | 0.207692 | 0.014816 | 0.000000 | 0.950000 | -806.408062 | True | True | no_active_rows_after_short_availability_restriction |
| 0.750000 | null | rank | 0 | 0.228049 | 0.207692 | 0.000000 | 0.000000 | 0.000000 | -2374.912432 | True | True | no_active_rows_after_short_availability_restriction |
<!-- table:haircut:end -->

### Haircut zero-reference (matches P21 and WP2 at 6 dp)

<!-- table:haircut_zero_reference:start -->
| variant | weighting | committed_p21_recovery | committed_wp2_drift_zero_recovery | haircut_zero_recovery | matches_p21_at_6dp | matches_wp2_at_6dp |
|---|---|---|---|---|---|---|
| null | equal | 0.000000 | 0.000000 | 0.000000 | True | True |
| null | rank | 0.000000 | 0.000000 | 0.000000 | True | True |
| planted | equal | 0.000261 | 0.000261 | 0.000261 | True | True |
| planted | rank | 0.017360 | 0.017360 | 0.017360 | True | True |
<!-- table:haircut_zero_reference:end -->

## Decision

The chartered acceptance thresholds for this report are restated below from the P23 charter, not retyped. Each one is re-verified against the committed artifacts by the consistency suite.

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Explicit signal-or-noise verdict | True |
| NO-GO for market | True |
| No harness re-run | True |
| Planted recovery labelled controlled synthetic | True |
| Numbers matched minimum | 100 |
| Unmatched cells maximum | 0 |
| Nominal slack | 0.050000 |
<!-- table:decision:end -->

**Verdict:** the estimator is **SIGNAL on controlled synthetic planted / NOISE on null** across all three instability axes — breadth concentration, beta-estimation drift, and crypto short-availability scarcity — and the verdict is **NO-GO for market deployment** until a maintainer supplies a licensed price series. This is a decision about the estimator's calibration and instability handling under controlled conditions, not a decision about a live trading opportunity.

The single censored rank `h=0.75` cell (seed `20261245`, `censor_reason = "no_active_rows_after_short_availability_restriction"`) is a genuine finding: at 75% short withdrawal the market-neutral book can vanish outright on a whole seed. The cell stays visible with its machine-readable reason and is never zeroed silently.

## What this does not prove

- It does not prove a demonstrated profitable strategy: the planted universe is a controlled synthetic stimulus with known ground truth.
- It does not prove that planted recovery is market alpha; it is never market alpha and must never be quoted as such.
- It does not prove that a null-universe positive result is a finding. It would be a bug.
- It does not prove that the breadth/drift/availability stress results transfer to a real order book, since the stimuli are modelled and not calibrated market parameters.
- It does not prove that the censored rank `h=0.75` cell would recover with a different availability draw; the censor is documented, not hidden.

## Required next

Campaign P24 "Regime-conditional BAB and holdout discipline" is the declared successor. It must measure regime-conditional beta estimation, holdout discipline with no parameter selection on the evaluation window, rebalance hysteresis, and a licensed-price CSV schema fixture for offline adapter testing, and it must close with its own decision report that keeps this NO-GO in force until licensed market data exists. The next session must land the first unrouted P24 work package with its script, artifact and acceptance test in one commit; prose alone is not a session.