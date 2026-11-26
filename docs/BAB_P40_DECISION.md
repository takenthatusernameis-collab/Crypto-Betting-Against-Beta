# BAB P40 Closing Decision -- Multi-Fixture Robustness & Consolidated Factor Verdict

**Campaign:** P40 "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict"
**Decision row:** P40 WP0 -- Deterministic meta-analysis generator (four fixtures, 32 cells)
**Artifacts consumed (read-only):**
- `research_state/bab_p40/meta_summary.json` (WP0; four-fixture deflated
  significance + tail risk + neutrality, consolidated verdict)

**Verdict strings verified:** `DOES_NOT_REPLICATE`, `FRAGILE_FIXTURE_DEPENDENT`,
`ROBUST_ACROSS_FIXTURES`, `synthetic`, `not market evidence`, `no real alpha`

**Decision:** **The P38 pooled verdict replicates on 0 of 4 independent fixtures -- it does not replicate.** P40 closes the fixture-robustness question left open by P38 (pooled survival on one synthetic fixture) and P39 (within-regime failure + cross-fixture non-replication). Per-fixture evidence: F1_PRIMARY DSR mean 0.637206 (5 of 8 cells survive); F2_P39_SECOND DSR mean 0.395858 (3 of 8 cells survive); F3_LOW_VOL_WIDE DSR mean 0.630585 (5 of 8 cells survive); F4_HIGH_VOL_NARROW DSR mean 0.421378 (3 of 8 cells survive). Neutrality holds at all 32 cells and the consolidated verdict is determined by a fixed fixture-count rule (0 of 4 replicate). The verdict is honest: the shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS) is retained; nothing is flipped. Synthetic-provenance caveat applies throughout: all P40 inputs are deterministic synthetic random walks, not real market data, and these results are never market alpha.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema | bab_p40.meta_analysis/1 |
| Campaign | P40 Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict |
| WP | WP0 - Deterministic meta-analysis generator (four fixtures, 32 cells) |
| Synthetic | True |
| Meta-analysis note | Four deterministic synthetic wide universes built from the same read-only BTC price fixture (tests/fixtures/wide_bab_universe.csv). Asset returns = beta * BTC_return + seeded idiosyncratic noise. Not real market data; not market profitability evidence. Pooled per-seed cells (no regime split): deflated significance (DSR/PSR over n_trials_total read-only from P38 WP1) plus tail risk (CVaR/expected shortfall/drawdown/skew/kurtosis) and neutrality invariants. Campaign verdict reports whether the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) replicates across fixtures. |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Deflation trials (n_trials_total) | 552 |
| DSR survive threshold | 0.500000 |
| Bootstrap resamples | 2000 |
| Bootstrap block length | 20 |
| Bootstrap seed | 20261123 |
| Fixtures | 4 |
| Seeds per fixture | 8 |
| Total cells | 32 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Transaction costs | 0.000000 |
| Campaign verdict | DOES_NOT_REPLICATE |
<!-- table:provenance:end -->

---

## WP0 -- Multi-Fixture Meta-Analysis

Four deterministic synthetic wide universes built from the same read-only BTC price
fixture (`tests/fixtures/wide_bab_universe.csv`), asset returns = beta * BTC_return +
seeded idiosyncratic noise, 8 seeds per fixture, 32 cells total. Deflated Sharpe Ratio
(DSR) and Probabilistic Sharpe Ratio (PSR) per cell, deflated over `n_trials_total`
read-only from P38 WP1, plus tail risk and the three neutrality invariants at every
cell. Shipped-default BAB config: `weighting="equal"`, `beta_neutral=True`,
`dollar_neutral=True`, `beta_window=90`, `quantile=0.3`, zero transaction costs.

<!-- table:fixture:start -->
| Fixture | Role | Base seed | Increment | Idio vol | Beta range | Assets | N cells | N ok | N survive | DSR mean | DSR min | DSR max | Replicates P38 pooled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | P38/P39 WP1 primary parameterization | 20261120 | 1009 | 0.003000 | [0.350000, 1.900000] | 40 | 8 | 8 | 5 | 0.637206 | 0.081837 | 0.944013 | False |
| F2_P39_SECOND | P39 WP2 second parameterization | 20270101 | 9973 | 0.006000 | [0.200000, 2.400000] | 32 | 8 | 8 | 3 | 0.395858 | 0.069944 | 0.928768 | False |
| F3_LOW_VOL_WIDE | Low-idio, wider beta cross-section | 20280201 | 10009 | 0.002000 | [0.250000, 2.100000] | 36 | 8 | 8 | 5 | 0.630585 | 0.095286 | 0.958546 | False |
| F4_HIGH_VOL_NARROW | High-idio, narrower beta cross-section | 20290301 | 10007 | 0.008000 | [0.400000, 1.700000] | 28 | 8 | 8 | 3 | 0.421378 | 0.073224 | 0.952911 | False |
<!-- table:fixture:end -->

---

## Per-cell results (pooled; no regime split)

DSR >= 0.500000 means more likely than not genuine skill after
deflation over n_trials_total=552.

<!-- table:cell:start -->
| Fixture | Seed | Seed index | N periods | Sharpe | DSR | PSR | Survives | Verdict | Neutrality ok |
|---|---|---|---|---|---|---|---|---|---|
| F1_PRIMARY | 20261120 | 0 | 339 | 0.760518 | 0.944013 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20262129 | 1 | 339 | 0.320261 | 0.933528 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20263138 | 2 | 339 | 1.865525 | 0.926111 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20264147 | 3 | 339 | -0.129599 | 0.238889 | 0.008562 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20265156 | 4 | 339 | -0.531831 | 0.109034 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20266165 | 5 | 339 | 0.967765 | 0.925842 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F1_PRIMARY | 20267174 | 6 | 339 | -0.845875 | 0.081837 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F1_PRIMARY | 20268183 | 7 | 339 | 0.532712 | 0.938391 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20270101 | 0 | 339 | -0.861582 | 0.069944 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20280074 | 1 | 339 | 0.487880 | 0.923431 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20290047 | 2 | 339 | -0.641189 | 0.082488 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20300020 | 3 | 339 | 0.327766 | 0.923706 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F2_P39_SECOND | 20309993 | 4 | 339 | -1.107029 | 0.073579 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20319966 | 5 | 339 | -0.769760 | 0.084260 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20329939 | 6 | 339 | -1.359181 | 0.080687 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F2_P39_SECOND | 20339912 | 7 | 339 | 2.176458 | 0.928768 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20280201 | 0 | 339 | -0.535429 | 0.095286 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20290210 | 1 | 339 | 0.052140 | 0.958546 | 0.831125 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20300219 | 2 | 339 | -0.533620 | 0.108983 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20310228 | 3 | 339 | 0.494379 | 0.943269 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20320237 | 4 | 339 | -0.288504 | 0.122799 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20330246 | 5 | 339 | 1.005151 | 0.936855 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20340255 | 6 | 339 | 1.051665 | 0.930727 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F3_LOW_VOL_WIDE | 20350264 | 7 | 339 | 0.214326 | 0.948212 | 0.999960 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20290301 | 0 | 339 | 1.313904 | 0.929730 | 1.000000 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20300308 | 1 | 339 | 0.210269 | 0.952911 | 0.999946 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20310315 | 2 | 339 | -0.069405 | 0.318851 | 0.101022 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20320322 | 3 | 339 | -0.456647 | 0.073224 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20330329 | 4 | 339 | -1.043952 | 0.073906 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20340336 | 5 | 339 | -0.006414 | 0.794795 | 0.453067 | True | SURVIVES_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20350343 | 6 | 339 | -0.268372 | 0.151619 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
| F4_HIGH_VOL_NARROW | 20360350 | 7 | 339 | -1.004819 | 0.075987 | 0.000000 | False | DOES_NOT_SURVIVE_DEFLATION | True |
<!-- table:cell:end -->

---

## Cross-fixture aggregate (all 32 cells)

<!-- table:aggregate:start -->
| Metric | N cells | N ok | N errors | All neutrality ok | All survive | N survive | Mean | Min | Max |
|---|---|---|---|---|---|---|---|---|---|
| DSR | 32 | 32 | 0 | True | False | 16 | 0.521257 | 0.069944 | 0.958546 |
| PSR | 32 | 32 | 0 | True | False | 16 | 0.481053 | 0.000000 | 1.000000 |
| SHARPE | 32 | 32 | 0 | True | False | 16 | 0.041485 | -1.359181 | 2.176458 |
<!-- table:aggregate:end -->

### Neutrality (every cell)

<!-- table:neutrality:start -->
| Check | Passed | Tolerance |
|---|---|---|
| Model beta neutral | True | 0.001000 |
| Dollar neutral | True | 0.000000 |
| Realized |beta| | True | 0.150000 |
<!-- table:neutrality:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| WP0 meta-analysis deflates DSR/PSR over n_trials_total read-only from P38 WP1 (trial_enumeration.n_trials_total) | True |
| Consolidated verdict is an explicit enum value (ROBUST_ACROSS_FIXTURES / FRAGILE_FIXTURE_DEPENDENT / DOES_NOT_REPLICATE) | True |
| All 32 cells are status ok with zero errors | True |
| Neutrality holds at every cell (model beta <= 1e-3, dollar <= 1e-9, |realized beta| <= 0.15) | True |
| DSR and PSR bounded in [0, 1] at every ok cell | True |
| Fixture replication count (0 of 4) matches the per-fixture all-ok + all-survive + no-error rule | True |
| Synthetic provenance labelled (controlled synthetic, not real market data) | True |
| No demonstrated real-world profitability claim is made | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** All P40 universes are controlled
  synthetic stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset
  returns = `beta * BTC_return + idio`). They are **not real market data** and **not
  market profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No universal factor claim.** The consolidated verdict is DOES_NOT_REPLICATE;
  the P38 pooled survival on the primary synthetic fixture is fixture-dependent and
  does not generalize across independent parameterizations.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P40 concludes here with the consolidated verdict **DOES_NOT_REPLICATE**.
Only a `ROBUST_ACROSS_FIXTURES` verdict would justify a follow-on real-data validation campaign, and only with explicit maintainer approval; the committed `tests/fixtures/real_market_prices.csv` is also synthetic.

The terminal state of the P38-P40 lineage is recorded in `HANDOFF.md`: P38
(SURVIVES_DEFLATION on one fixture), P39 (within-regime failure + non-replication),
P40 (DOES_NOT_REPLICATE across four fixtures). No new fixtures, no re-tuning, and no
reopening of frozen P20-P39 artifacts are in scope without a new charter.

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p40_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
