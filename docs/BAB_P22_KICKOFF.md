# BAB P22 WP0 — Decision-grade validation

Schema `bab_p22.charter/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

## Binding row
- Campaign: P22
- Title: Decision-grade validation
- Binding row: P22 WP0
- Artifact-gated: true
- Not market evidence: true
- Licensed data required: true

## P21 verdict (restated from committed JSON only)
- Signal on planted: true
- Noise on null: true
- Null calibrated: true
- Planted detected: true
- Null max p-value: 0.268000
- Nominal slack: 0.050000
- Verdict: SIGNAL on the planted controlled-synthetic universe; NOISE on the null universe; NO-GO for market deployment.

### P21 per-book basis (committed JSON fields)
| null | equal | 0.163500 | False | False | 0.639801 | 0.923379 | 0.000000 | 541 | 0.639801 | False |
| null | rank | 0.268000 | False | False | 0.649924 | 0.926802 | 0.000000 | 541 | 0.649924 | False |
| planted | equal | 0.000000 | True | True | 7.034781 | 0.905272 | 0.000261 | 541 | 7.034781 | False |
| planted | rank | 0.000000 | True | True | 44.378201 | 0.998329 | 0.017360 | 541 | 44.378201 | False |

### P21 cost-surface monotonicity (committed JSON fields)
| variant | weighting | linear_transaction_cost | borrow_funding | notional_slippage | censored |
|---|---|---|---|---|---|
| null | equal | True | True | True | False |
| null | rank | True | True | True | False |
| planted | equal | True | True | True | False |
| planted | rank | True | True | True | False |

## P22 charter constants (declared here, not derived from P21 JSON)
- P22 null-battery seeds (n=20, >= 20): 20261120, 20261121, 20261122, 20261123, 20261124, 20261125, 20261126, 20261127, 20261128, 20261129, 20261130, 20261131, 20261132, 20261133, 20261134, 20261135, 20261136, 20261137, 20261138, 20261139
- Nominal slack: 0.050000

### Acceptance thresholds consumed by P21 WP1-WP4
| WP | Threshold | Value |
|---|---|---|
| WP1 | min_active_rows | 1 |
| WP1 | rank_min_leg_beta | 0.200000 |
| WP1 | rank_max_gross | 4.000000 |
| WP1 | beta_exposure_max | 0.050000 |
| WP1 | dollar_imbalance_equal_max | 0.000000 |
| WP1 | recovery_planted_strictly_positive | True |
| WP1 | recovery_null_exactly_zero | 0.000000 |
| WP2 | n_resamples_min | 2000 |
| WP2 | block_length | 20 |
| WP2 | null_not_significant_at_slack | True |
| WP2 | planted_significant_with_ci_excluding_zero | True |
| WP3 | min_components | 3 |
| WP3 | per_book_monotonicity_true | True |
| WP3 | period_wise_non_increasing_true | True |
| WP3 | censored_reports_document_reason_never_zero_tolerance | True |
| WP4 | numbers_matched_min | 100 |
| WP4 | zero_unmatched_cells | 0 |
| WP4 | no_harness_re_run | True |
| WP4 | explicit_signal_noise_verdict | True |
| WP4 | planted_recovery_labelled_controlled_synthetic | True |
| WP4 | no_go_for_market | True |

## Provenance
- Universe seed: 20261118
- P21 significance seed: 20261119
- Planted panel sha256: `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda`
- Null panel sha256: `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b`
- Generator: scripts/bab_p22_charter.py
- Caveat: P21 recovery on a planted synthetic universe proves the estimator works; it is never market alpha. A null-universe positive result is a bug, not a finding. NO-GO for market deployment until a maintainer supplies a licensed price series.

## WPs in order
- P22 WP0 — charter
- P22 WP1 — null battery (>=20 seeds)
- P22 WP2 — nonlinear impact
- P22 WP3 — capacity / break-even
- P22 WP4 — decision report

reads the committed P21 JSON artifacts (universe, significance, rank_eval, cost_surface) read-only; restates the P21 verdict from committed fields; declares the P22 null-battery seeds, nominal slack and WP1-WP4 acceptance thresholds as charter constants; never imports or re-runs any P21 build_* harness.

P21 recovery on a planted synthetic universe proves the estimator works; it is never market alpha. A null-universe positive result is a bug, not a finding. NO-GO for market deployment until a maintainer supplies a licensed price series.
