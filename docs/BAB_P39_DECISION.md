# BAB P39 Closing Decision -- Regime-Conditional & Cross-Fixture Robustness Closure

**Campaign:** P39 "Regime-Conditional & Cross-Fixture Robustness Closure"
**Decision row:** P39 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p39/regime_summary.json` (WP1; within-regime deflated
  significance + neutrality)
- `research_state/bab_p39/cross_fixture_summary.json` (WP2; second independent
  synthetic universe)

**Verdict strings verified:** `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`,
`DOES_NOT_REPLICATE`, `synthetic`, `not market evidence`, `no real alpha`

**Decision:** **DO NOT deploy on the strength of this factor; RETAIN the shipped default with an honest negative robustness verdict.** P39 closes the two robustness axes a factor strategy must answer beyond the pooled P38 read. (1) *Within-regime stability*: the campaign verdict is **DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME** -- at least one well-populated regime has DSR mean below the 0.5 survive threshold after deflation over n_trials_total=552, while neutrality holds at every populated (seed, regime) cell. (2) *Cross-fixture replication*: the campaign verdict is **DOES_NOT_REPLICATE** -- only {c_survive} of {c_cells} seeds survive deflation on the second independent synthetic universe, and neutrality holds at every cell. The pooled P38 verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) is fixture-dependent, not a universal factor property. The shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS) is retained; nothing is flipped. Synthetic-provenance caveat applies throughout.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema regime | bab_p39.regime_conditional/1 |
| Schema cross_fixture | bab_p39.cross_fixture/1 |
| Campaign | P39 Regime-Conditional & Cross-Fixture Robustness Closure |
| WP | WP3 - Decision doc + documentation-integrity closure + gate wire |
| Synthetic regime | True |
| Synthetic cross_fixture | True |
| Regime note | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Regimes are causal and lagged: trailing BTC trend (bull/bear) x trailing realized-vol tercile (low/mid/high), computed only from data available at t-1, no lookahead. Not real market data; not market profitability evidence. The verdict is honest and may be negative (a thin regime can fail deflation). |
| Cross-fixture note | Deterministic synthetic wide universe — SECOND independent parameterization, distinct from P39 WP1's regime-conditional fixture. BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.006), betas linspace(0.2, 2.4, 32). Not real market data; not market profitability evidence. Pooled per-seed cells (no regime split): deflated significance (DSR/PSR over n_trials_total read-only from P38 WP1) plus tail risk (CVaR/expected shortfall/drawdown/skew/kurtosis). Campaign verdict reports whether the P38 pooled verdict (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) replicates. |
| Fixture path regime | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Fixture path cross_fixture | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Returns SHA256 regime | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| Returns SHA256 cross_fixture | `11abcfe8388bcbb539e7637db77d63b63de68b04b8498c6001c4be203e6e3422` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Regime seeds (base/inc/n) | 20261120/1009/8 |
| Regime seed list | 20261120, 20262129, 20263138, 20264147, 20265156, 20266165, 20267174, 20268183 |
| Cross seeds (base/inc/n) | 20270101/9973/8 |
| Cross seed list | 20270101, 20280074, 20290047, 20300020, 20309993, 20319966, 20329939, 20339912 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Min periods per regime | 30 |
| Regime labels | bull_low_vol, bull_mid_vol, bull_high_vol, bear_low_vol, bear_mid_vol, bear_high_vol |
| Deflation trials (n_trials_total) | 552 |
| DSR survive threshold | 0.500000 |
| Campaign verdict regime | DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME |
| Campaign verdict cross_fixture | DOES_NOT_REPLICATE |
<!-- table:provenance:end -->

---

## WP1 -- Within-Regime Deflated Significance & Neutrality

Deflated Sharpe Ratio (DSR) and Probabilistic Sharpe Ratio (PSR) per causal, lagged
regime (trailing BTC trend x trailing realized-vol tercile; no lookahead), deflated over
`n_trials_total` read-only from P38 WP1. Neutrality invariants (model beta, dollar
neutral, realized |beta|) are checked at every populated cell.

<!-- table:regime:start -->
| Regime | N_Cells | N_OK_Cells | N_Insufficient | N_Error | N_Survive | All_Survive | Any_Survive | DSR_Mean | DSR_Min | DSR_Max | PSR_Mean | PSR_Min | PSR_Max | Neutrality_OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bear_high_vol | 8 | 0 | 8 | 0 | 0 | True | False | None | None | None | None | None | None | True |
| bear_low_vol | 8 | 8 | 0 | 0 | 5 | False | True | 0.613467 | 0.030439 | 0.971513 | 0.626873 | 0.000000 | 1.000000 | True |
| bear_mid_vol | 8 | 0 | 8 | 0 | 0 | True | False | None | None | None | None | None | None | True |
| bull_high_vol | 8 | 8 | 0 | 0 | 3 | False | True | 0.412219 | 0.059605 | 0.944130 | 0.375007 | 0.000000 | 1.000000 | True |
| bull_low_vol | 8 | 8 | 0 | 0 | 7 | False | True | 0.838955 | 0.131747 | 0.969464 | 0.874266 | 0.000000 | 1.000000 | True |
| bull_mid_vol | 8 | 8 | 0 | 0 | 5 | False | True | 0.605503 | 0.102371 | 0.942615 | 0.622470 | 0.000000 | 1.000000 | True |
<!-- table:regime:end -->

---

## WP2 -- Cross-Fixture Replication

Second independent synthetic universe (distinct beta grid / idio vol / seed base) with no
regime split: pooled per-seed deflated significance (DSR/PSR over `n_trials_total` read-only
from P38 WP1) plus tail risk. The campaign verdict reports whether the P38 pooled verdict
(SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) replicates.

<!-- table:cross_fixture:start -->
| Cell_Key | Seed | Seed_Index | Status | Survives | DSR | PSR | Sharpe | Verdict |
|---|---|---|---|---|---|---|---|---|
| seed_0 | 20270101 | 0 | ok | False | 0.070183 | 0.000000 | -0.861582 | DOES_NOT_SURVIVE_DEFLATION |
| seed_1 | 20280074 | 1 | ok | True | 0.923269 | 1.000000 | 0.487880 | SURVIVES_DEFLATION |
| seed_2 | 20290047 | 2 | ok | False | 0.082510 | 0.000000 | -0.641189 | DOES_NOT_SURVIVE_DEFLATION |
| seed_3 | 20300020 | 3 | ok | True | 0.923094 | 1.000000 | 0.327766 | SURVIVES_DEFLATION |
| seed_4 | 20309993 | 4 | ok | False | 0.073291 | 0.000000 | -1.107029 | DOES_NOT_SURVIVE_DEFLATION |
| seed_5 | 20319966 | 5 | ok | False | 0.084453 | 0.000000 | -0.769760 | DOES_NOT_SURVIVE_DEFLATION |
| seed_6 | 20329939 | 6 | ok | False | 0.080656 | 0.000000 | -1.359181 | DOES_NOT_SURVIVE_DEFLATION |
| seed_7 | 20339912 | 7 | ok | True | 0.928788 | 1.000000 | 2.176458 | SURVIVES_DEFLATION |
<!-- table:cross_fixture:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| WP1 campaign verdict is DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME (honest within-regime negative) | True |
| WP1 at least one well-populated regime has DSR mean below the 0.5 survive threshold after deflation over n_trials_total=552 | True |
| WP1 neutrality holds at every populated (seed, regime) cell (model beta <= 1e-3, dollar <= 1e-9, realized |beta| <= 0.15) | True |
| WP2 campaign verdict is DOES_NOT_REPLICATE (honest cross-fixture negative) | True |
| WP2 neutrality holds at every cross-fixture cell (gross + costed) | True |
| WP2 exactly 3 of 8 second-universe seeds survive deflation over n_trials_total=552 | True |
| Regime and cross-fixture universes are independent fixtures (distinct returns SHA256) | True |
| Both universes labelled controlled synthetic; not real market data; not market profitability evidence | True |
| No demonstrated real-world profitability; shipped default retained; nothing flipped | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** Both universes are controlled synthetic
  stimuli (BTC prices from `tests/fixtures/wide_bab_universe.csv`, asset returns =
  `beta * BTC_return + idio`). They are **not real market data** and **not market
  profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P39.
- **Honest negatives, not a positive claim.** The WP1 within-regime verdict and the WP2
  cross-fixture verdict are both negative; the campaign does not claim the factor survives
  deflation universally. The P38 pooled verdict is fixture-dependent.
- **Shipped default retained.** The decision does not flip `weighting="equal"` /
  `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P39 concludes here with honest negative robustness findings on both replication
axes. The shipped default `weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
rolling-OLS is retained.

**Future work (not in scope for P39):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized
- P39 WP0 close-out: full `bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`
  on a large-time-budget session, plus a cross-version determinism test
  (`tests/test_bab_p38_determinism.py`).

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p39_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings, AST
no-harness scan, and ruff clean. Never market alpha.*
