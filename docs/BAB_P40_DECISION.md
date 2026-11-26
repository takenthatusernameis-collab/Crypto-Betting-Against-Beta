# BAB P40 Closing Decision -- Meta-Analysis & Consolidated Verdict

**Campaign:** P40 "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict"
**Decision row:** P40 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p40/meta_summary.json` (WP0; multi-fixture meta-analysis)

**Verdict strings verified:** `ROBUST_ACROSS_FIXTURES`, `FRAGILE_FIXTURE_DEPENDENT`,
`DOES_NOT_REPLICATE`, `synthetic`, `not market evidence`, `no real alpha`

**Decision:** **DOES_NOT_REPLICATE**. 0 of 4 fixtures replicate the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over n_trials_total=552; DSR survive threshold=0.5. No fixture replicates — the P38 pooled verdict does not replicate (DOES_NOT_REPLICATE). Honest negative. 0 of 4 fixtures replicate the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over n_trials_total=552 at DSR survive threshold 0.5. Neutrality invariants hold at every cell across all four fixtures. The shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS) is retained; nothing is flipped. Synthetic-provenance caveat applies throughout.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema | bab_p40.meta_analysis/1 |
| Campaign | P40 Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict |
| WP | WP0 - Deterministic meta-analysis generator (four synthetic fixtures) |
| Synthetic | True |
| Generator | scripts/bab_p40_meta_analysis.py |
| Fixture path | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Returns SHA256 | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| N fixtures | 4 |
| N seeds per fixture | 8 |
| N total cells | 32 |
| Fixture IDs | F1_PRIMARY, F2_P39_SECOND, F3_LOW_VOL_WIDE, F4_HIGH_VOL_NARROW |
| Fixtures (id / base_seed / increment / idio_vol / beta range / n_assets) | F1_PRIMARY=20261120/1009/0.003/[0.35,1.9]/40; F2_P39_SECOND=20270101/9973/0.006/[0.2,2.4]/32; F3_LOW_VOL_WIDE=20280201/10009/0.002/[0.25,2.1]/36; F4_HIGH_VOL_NARROW=20290301/10007/0.008/[0.4,1.7]/28 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Transaction costs | 0.000000 |
| Deflation trials (n_trials_total) | 552 |
| DSR survive threshold | 0.500000 |
| Campaign verdict | DOES_NOT_REPLICATE |
<!-- table:provenance:end -->

---

## WP0 -- Multi-Fixture Robustness Meta-Analysis

Four independent deterministic synthetic universes built from the same read-only BTC
price fixture (`tests/fixtures/wide_bab_universe.csv`), each with 8 seed cells
(32 total cells). Asset returns = beta * BTC_return + idio; deflated significance
(DSR/PSR over `n_trials_total` read-only from P38 WP1) plus tail risk (CVaR /
expected shortfall / drawdown / skew / kurtosis) at every cell; neutrality
invariants (model beta, dollar neutral, realized |beta|) checked at every cell.

<!-- table:fixture:start -->
| Fixture | Role | Base Seed | Increment | Idio Vol | Beta Min | Beta Max | N Assets | N Cells | N OK | N Survive | DSR Mean | DSR Max | Replicates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | P38/P39 WP1 primary parameterization | 20261120 | 1009 | 0.003000 | 0.350000 | 1.900000 | 40 | 8 | 8 | 5 | 0.636728 | 0.943990 | False |
| F2_P39_SECOND | P39 WP2 second parameterization | 20270101 | 9973 | 0.006000 | 0.200000 | 2.400000 | 32 | 8 | 8 | 3 | 0.395780 | 0.928788 | False |
| F3_LOW_VOL_WIDE | Low-idio, wider beta cross-section | 20280201 | 10009 | 0.002000 | 0.250000 | 2.100000 | 36 | 8 | 8 | 5 | 0.630724 | 0.958728 | False |
| F4_HIGH_VOL_NARROW | High-idio, narrower beta cross-section | 20290301 | 10007 | 0.008000 | 0.400000 | 1.700000 | 28 | 8 | 8 | 3 | 0.419918 | 0.952693 | False |
<!-- table:fixture:end -->

<!-- table:cell:start -->
| Fixture | Cell Key | Seed | Status | Sharpe | DSR | PSR | Survives | Verdict | Neutrality OK |
|---|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | seed_0 | 20261120 | ok | 0.760518 | 0.943990 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | seed_1 | 20262129 | ok | 0.320261 | 0.933048 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | seed_2 | 20263138 | ok | 1.865525 | 0.926165 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | seed_3 | 20264147 | ok | -0.129599 | 0.236171 | 0.008562 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | seed_4 | 20265156 | ok | -0.531831 | 0.108773 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | seed_5 | 20266165 | ok | 0.967765 | 0.925786 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | seed_6 | 20267174 | ok | -0.845875 | 0.081475 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | seed_7 | 20268183 | ok | 0.532712 | 0.938416 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | seed_0 | 20270101 | ok | -0.861582 | 0.070183 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | seed_1 | 20280074 | ok | 0.487880 | 0.923269 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | seed_2 | 20290047 | ok | -0.641189 | 0.082510 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | seed_3 | 20300020 | ok | 0.327766 | 0.923094 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | seed_4 | 20309993 | ok | -1.107029 | 0.073291 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | seed_5 | 20319966 | ok | -0.769760 | 0.084453 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | seed_6 | 20329939 | ok | -1.359181 | 0.080656 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | seed_7 | 20339912 | ok | 2.176458 | 0.928788 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_0 | 20280201 | ok | -0.535429 | 0.095354 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_1 | 20290210 | ok | 0.052140 | 0.958728 | 0.831125 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_2 | 20300219 | ok | -0.533620 | 0.109025 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_3 | 20310228 | ok | 0.494379 | 0.943538 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_4 | 20320237 | ok | -0.288504 | 0.123886 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_5 | 20330246 | ok | 1.005151 | 0.936830 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_6 | 20340255 | ok | 1.051665 | 0.930717 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | seed_7 | 20350264 | ok | 0.214326 | 0.947714 | 0.999960 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_0 | 20290301 | ok | 1.313904 | 0.929818 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_1 | 20300308 | ok | 0.210269 | 0.952693 | 0.999946 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_2 | 20310315 | ok | -0.069405 | 0.311295 | 0.101022 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_3 | 20320322 | ok | -0.456647 | 0.072676 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_4 | 20330329 | ok | -1.043952 | 0.074221 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_5 | 20340336 | ok | -0.006414 | 0.792640 | 0.453067 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_6 | 20350343 | ok | -0.268372 | 0.150112 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | seed_7 | 20360350 | ok | -1.004819 | 0.075887 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
<!-- table:cell:end -->

---

## Cross-Fixture Aggregates

<!-- table:cross:start -->
| Metric | Value |
|---|---|
| n_fixtures | 4 |
| n_total_cells | 32 |
| n_total_ok_cells | 32 |
| n_total_error_cells | 0 |
| n_total_survive | 16 |
| n_fixtures_replicating | 0 |
| replication_fraction | 0.000000 |
| all_fixtures_neutrality_ok | True |
| all_fixtures_survive | False |
<!-- table:cross:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Schema is bab_p40.meta_analysis/1 (committed generator: scripts/bab_p40_meta_analysis.py) | True |
| All four fixtures labelled controlled synthetic; not real market data; not market profitability evidence | True |
| Deflation over n_trials_total=552 read-only from P38 WP1 (trial_enumeration.n_trials_total); never re-enumerated | True |
| Exactly 32 total cells across 4 fixtures (8 seeds each) | True |
| Consolidated verdict is explicit: DOES_NOT_REPLICATE | True |
| Verdict is honest — may be ROBUST_ACROSS_FIXTURES, FRAGILE_FIXTURE_DEPENDENT, or DOES_NOT_REPLICATE; no fixture tuning to chase a positive result | True |
| All three neutrality invariants hold at every cell (model beta <= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15) | True |
| No demonstrated real-world profitability; synthetic-provenance caveat applies; nothing flipped | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** All four universes are controlled
  synthetic stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset
  returns = `beta * BTC_return + idio`). They are **not real market data** and
  **not market profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P40.
- **Honest verdict, not a positive claim.** The consolidated verdict reports
  honestly whether the P38 pooled verdict replicates across fixtures; it may be
  negative (`DOES_NOT_REPLICATE` or `FRAGILE_FIXTURE_DEPENDENT`). The campaign does
  not claim the factor survives deflation universally.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.
- **Only `ROBUST_ACROSS_FIXTURES` justifies a follow-on real-data validation
  campaign, and only with explicit maintainer approval.**

---

## Next Steps

Campaign P40 concludes here with the consolidated multi-fixture robustness verdict.
The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P40):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized
- If `ROBUST_ACROSS_FIXTURES`, a real-data validation campaign (maintainer approval
  required); otherwise, terminal summary consolidating P38-P40.

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p40_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
