# BAB P23 WP0 — Breadth and instability stress

Schema `bab_p23.charter/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

## Binding row
- Campaign: P23
- Title: Breadth and instability stress
- Binding row: P23 WP0
- Artifact-gated: true
- Not market evidence: true
- Licensed data required: true

## P22 verdict (restated from committed P22 JSON only)
<!-- table:p22_verdict:start -->
| Fact | Value |
|---|---|
| Verdict | NO-GO for market deployment |
| NO-GO for market | True |
| Signal on planted | True |
| Noise on null | True |
| Nominal slack | 0.050000 |
<!-- table:p22_verdict:end -->

### P22 null battery (committed JSON fields)
<!-- table:p22_null_battery:start -->
| Statistic | Value |
|---|---|
| Chartered seeds | 20 |
| Null books | 40 |
| Planted books | 40 |
| Null recovery max abs | 0.000000 |
| Null books with zero recovery | 40 |
| False positives | 2 |
| False-positive denominator | 40 |
| False-positive rate | 0.050000 |
| False-positive max declared | 4 |
| False-positive within bound | True |
| Planted recovery min equal | 0.000206 |
| Planted recovery min rank | 0.017227 |
| Null Sharpe max | 1.288970 |
| Planted Sharpe min | 5.552134 |
<!-- table:p22_null_battery:end -->

### P22 nonlinear impact monotonicity (committed JSON fields)
<!-- table:p22_impact:start -->
| variant | weighting | monotone | period_wise_non_increasing | gross_sharpe |
|---|---|---|---|---|
| null | equal | True | True | 0.639801 |
| null | rank | True | True | 0.649924 |
| planted | equal | True | True | 7.034781 |
| planted | rank | True | True | 44.378201 |
<!-- table:p22_impact:end -->

### P22 capacity break-even (committed JSON fields)
<!-- table:p22_capacity:start -->
| variant | weighting | gross_sharpe | break_even_coefficient | censored | bracket_halving_verified |
|---|---|---|---|---|---|
| null | equal | 0.639801 | 0.010507 | False | True |
| null | rank | 0.649924 | 0.015268 | False | True |
| planted | equal | 7.034781 | 0.097478 | False | True |
| planted | rank | 44.378201 | None | True | False |
<!-- table:p22_capacity:end -->

## P23 charter constants (declared here, not derived from P22 JSON)
<!-- table:p23_grids:start -->
| Grid | Values |
|---|---|
| Breadth ladder (WP1) | 9, 17, 25, 33, 41 |
| Beta-window grid (WP2) | 60, 90, 120, 180 |
| Drift-threshold grid (WP2) | 0.0001, 0.0005, 0.001 |
| Borrow-haircut ladder (WP3) | 0.0, 0.1, 0.25, 0.5, 0.75 |
| Nominal slack | 0.05 |
<!-- table:p23_grids:end -->

### P23 per-work-package seeds (declared here)
<!-- table:p23_seeds:start -->
| WP | n | seeds |
|---|---|---|
| WP1 | 20 | 20261201, 20261202, 20261203, 20261204, 20261205, 20261206, 20261207, 20261208, 20261209, 20261210, 20261211, 20261212, 20261213, 20261214, 20261215, 20261216, 20261217, 20261218, 20261219, 20261220 |
| WP2 | 20 | 20261221, 20261222, 20261223, 20261224, 20261225, 20261226, 20261227, 20261228, 20261229, 20261230, 20261231, 20261232, 20261233, 20261234, 20261235, 20261236, 20261237, 20261238, 20261239, 20261240 |
| WP3 | 20 | 20261241, 20261242, 20261243, 20261244, 20261245, 20261246, 20261247, 20261248, 20261249, 20261250, 20261251, 20261252, 20261253, 20261254, 20261255, 20261256, 20261257, 20261258, 20261259, 20261260 |
<!-- table:p23_seeds:end -->

### Shipped strategy defaults (committed P22 config, never relaxed)
<!-- table:p23_strategy:start -->
| Parameter | Value |
|---|---|
| benchmark | BTC |
| beta_neutral | True |
| beta_window | 90 |
| long_quantile | 0.300000 |
| min_observations | 60 |
| rank_max_gross | 4.000000 |
| rank_min_leg_beta | 0.200000 |
| short_quantile | 0.300000 |
<!-- table:p23_strategy:end -->

### Acceptance thresholds consumed by P23 WP1-WP4
<!-- table:p23_thresholds:start -->
| WP | Threshold | Value |
|---|---|---|
| WP1 | ladder_min_rungs | 3 |
| WP1 | min_active_rows | 1 |
| WP1 | recovery_planted_strictly_positive | True |
| WP1 | recovery_null_exactly_zero | 0.000000 |
| WP1 | rank_min_leg_beta | 0.200000 |
| WP1 | rank_max_gross | 4.000000 |
| WP1 | rank_guards_never_relaxed | True |
| WP2 | min_beta_windows | 3 |
| WP2 | min_drift_thresholds | 3 |
| WP2 | beta_window_default_preserved | 90 |
| WP2 | every_cell_reported | True |
| WP2 | recovery_planted_strictly_positive | True |
| WP2 | recovery_null_exactly_zero | 0.000000 |
| WP3 | min_haircut_levels | 3 |
| WP3 | haircut_zero_baseline_required | True |
| WP3 | costed_sharpe_non_increasing_in_haircut | True |
| WP3 | recovery_null_exactly_zero | 0.000000 |
| WP3 | censored_reports_document_reason_never_zero_tolerance | True |
| WP4 | numbers_matched_min | 100 |
| WP4 | zero_unmatched_cells | 0 |
| WP4 | no_harness_re_run | True |
| WP4 | no_go_for_market | True |
| WP4 | planted_recovery_labelled_controlled_synthetic | True |
| WP4 | explicit_signal_noise_verdict | True |
<!-- table:p23_thresholds:end -->

## Provenance
- Universe seed: 20261118
- P22 source schema: bab_p22.charter/1
- Planted panel sha256: `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda`
- Null panel sha256: `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b`
- Generator: scripts/bab_p23_charter.py

## WPs in order
- P23 WP0 — charter
- P23 WP1 — breadth ladder
- P23 WP2 — beta-window/drift grid
- P23 WP3 — short-availability haircut ladder
- P23 WP4 — decision report (must keep NO-GO in force)

reads the committed P22 JSON artifacts (charter, null_battery, impact_surface, capacity) read-only; restates the P22 NO-GO verdict from committed fields; declares the P23 breadth ladder, beta-window/drift grid, borrow-haircut ladder, per-WP seed lists and WP1-WP4 acceptance thresholds as charter constants; never imports or re-runs any P21/P22 build_* harness.

P23 stress results on a controlled synthetic universe prove instability handling of the estimator; they are never market alpha. A null-universe positive result is a bug, not a finding. NO-GO for market deployment remains in force until a maintainer supplies a licensed price series.
