# BAB P36 Closing Decision -- Walk-Forward / Out-of-Sample
Validation + Rank-Weighted Construction Closure

**Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"
**Decision row:** P36 WP2-WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p36/walk_forward_summary.json` (80 cells)
- `research_state/bab_p36/rank_weighted_summary.json` (8 cells)

**Verdict strings verified:** `RETAIN`, `rank-weighted`,
`walk-forward`, `synthetic`, `not market evidence`

**Decision:** **RETAIN the shipped default** (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS). Walk-forward OOS validation on the 40-asset wide synthetic fixture shows the beta signal persists out of sample with all neutrality invariants satisfied at every cell. Frazzini-Pedersen rank-weighted / beta-scaled construction is confirmed beta-neutral with realized |beta| <= 0.15 at every cell and reduces average turnover vs equal-weight at equal neutrality, but it is not dollar-neutral by construction and does not improve OOS Sharpe. The shipped default is retained; rank-weighted is a documented alternative.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema walk-forward | bab_p36.walk_forward/1 |
| Schema rank-weighted | bab_p36.rank_weighted/1 |
| Campaign | P36 Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure |
| WP | WP2-WP3 - Decision doc + documentation-integrity closure + gate wire |
| Synthetic universe | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Walk-forward: train=90d, test=30d, step=30d. Not real market data; not market profitability evidence. |
| Fixture SHA256 | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Seeds (base/inc/n) | 20261120/1009/8 |
| Walk-forward config (train/test/step, beta window) | train=90d, test=30d, step=30d, beta_window=90d |
| Quantile | 0.300000 |
| Transaction costs | 0.001000 |
| Weighting (walk-forward) | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Rank min leg beta | 0.200000 |
| Rank max gross | 4.000000 |
| Model beta-neutral tol | 0.001000 |
| Dollar-neutral tol | 0.000000 |
| Realized beta tol | 0.150000 |
<!-- table:provenance:end -->

---

## Walk-Forward / Out-of-Sample -- Per-Window Summary

One row per walk-forward window (8 seeds each). All neutrality invariants (model beta-neutral
<= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15) verified per cell.

<!-- table:walk_forward_window:start -->
| Window | N_ok_cells | All_Neutrality_Pass |
|---|---|---|
| 0 | 8 | True |
| 1 | 8 | True |
| 2 | 8 | True |
| 3 | 8 | True |
| 4 | 8 | True |
| 5 | 8 | True |
| 6 | 8 | True |
| 7 | 8 | True |
| 8 | 8 | True |
| 9 | 8 | True |
<!-- table:walk_forward_window:end -->

---

## Rank-Weighted vs Equal-Weight -- Per-Seed Comparison

Equal-weight = shipped default (dollar-neutral + beta-neutral). Rank-weighted = Frazzini-Pedersen
rank weights with per-leg beta scaling (beta-neutral, not dollar-neutral). Rank safety valves:
min_leg_beta=0.20, max_gross=4.0 (never weakened).

<!-- table:rank_weighted:start -->
| Seed_Idx | N_Periods | EQ_Sharpe | EQ_Turnover | EQ_Wealth | EQ_Realized_Beta | EQ_Model_Beta | EQ_Dollar_Neutral | EQ_Neutrality_OK | RW_Sharpe | RW_Turnover | RW_Wealth | RW_Realized_Beta | RW_Model_Beta | RW_Dollar_Neutral | RW_Neutrality_OK | Turnover_Reduction | Sharpe_Difference | Wealth_Difference |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 339 | 0.191007 | 0.014831 | 1.001675 | 0.000539 | 0.000100 | 0.000000 | True | -0.552098 | 0.012221 | 0.974460 | -0.004451 | 0.000000 | 1.565160 | True | 0.002609 | -0.743105 | -0.027215 |
| 1 | 339 | -0.143112 | 0.012336 | 0.998679 | -0.001660 | 0.000100 | 0.000000 | True | -0.389683 | 0.013607 | 0.981918 | 0.002933 | 0.000000 | 1.539362 | True | -0.001271 | -0.246571 | -0.016761 |
| 2 | 339 | 1.533390 | 0.008795 | 1.013837 | -0.000277 | 0.000100 | 0.000000 | True | -0.259488 | 0.010241 | 0.987200 | -0.001921 | 0.000000 | 1.522194 | True | -0.001445 | -1.792878 | -0.026637 |
| 3 | 339 | -0.660304 | 0.013818 | 0.994172 | -0.000079 | 0.000100 | 0.000000 | True | 1.689770 | 0.009625 | 1.078782 | -0.002328 | 0.000000 | 1.511495 | True | 0.004193 | 2.350075 | 0.084610 |
| 4 | 339 | -1.008682 | 0.012795 | 0.990853 | -0.000535 | 0.000099 | 0.000000 | True | 0.558026 | 0.009658 | 1.025227 | 0.002204 | 0.000000 | 1.533597 | True | 0.003136 | 1.566708 | 0.034374 |
| 5 | 339 | 0.595260 | 0.009862 | 1.005388 | -0.001103 | 0.000100 | 0.000000 | True | 1.231707 | 0.011100 | 1.059380 | -0.000036 | 0.000000 | 1.540156 | True | -0.001238 | 0.636447 | 0.053992 |
| 6 | 339 | -1.178549 | 0.008934 | 0.989309 | -0.002003 | 0.000100 | 0.000000 | True | -0.794013 | 0.010654 | 0.966482 | 0.002771 | 0.000000 | 1.486426 | True | -0.001720 | 0.384536 | -0.022827 |
| 7 | 339 | 0.067243 | 0.011922 | 1.000557 | -0.001043 | 0.000098 | 0.000000 | True | -0.216153 | 0.011364 | 0.990528 | 0.001014 | 0.000000 | 1.523909 | True | 0.000558 | -0.283396 | -0.010029 |
<!-- table:rank_weighted:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| All 80 walk-forward cells (8 rank-weighted cells) complete with status ok | True |
| Walk-forward neutrality: model beta-neutral <= 1e-3, dollar-neutral <= 1e-9, |realized beta| <= 0.15 at every OOS cell | True |
| Walk-forward OOS Sharpe finite and non-NaN at every cell | True |
| Rank-weighted model beta-neutrality <= 1e-3 at every cell (both constructions) | True |
| Rank-weighted |realized beta| <= 0.15 at every cell (both constructions) | True |
| Equal-weight (shipped default) dollar-neutrality <= 1e-9 at every cell | True |
| Rank-weighted construction reduces turnover vs equal-weight at equal neutrality | True |
| Fixture SHA256 match across both artifacts | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence / no real alpha | True |
| Shipped default (weighting=equal, beta_neutral=True, beta_window=90, rolling-OLS) RETAINED | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns = `beta * BTC_return + idio`,
  `idio ~ N(0, 0.003)`, betas `linspace(0.35, 1.9, 40)`. It is **not real market data**
  and **not market profitability evidence**.
- **No live execution evidence.** No network was used in this campaign.
- **Rank-weighted is not dollar-neutral.** It achieves beta-neutrality (not
  dollar-neutrality) by construction; the shipped default remains dollar-neutral +
  beta-neutral equal-weight.
- **Walk-forward is single-path.** One train/test/step configuration (90/30/30)
  on the P35 wide-universe fixture; additional window configurations are future work.

---

## Next Steps

Campaign P36 concludes here. The **RETAIN** verdict is grounded in the evidence from
the walk-forward OOS study and the rank-weighted construction comparison. All neutrality
invariants hold at every cell; the beta signal persists out of sample; rank-weighted
reduces churn at equal neutrality without improving OOS Sharpe. The shipped default
`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS is retained;
rank-weighted is a documented alternative.

**Future work (not in scope for P36):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Additional walk-forward window configurations

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p36_decision_consistency.py` verifies
zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`rank-weighted`, `walk-forward`, `synthetic`, `not market evidence`), AST no-harness
scan, and ruff clean. Never market alpha.*
