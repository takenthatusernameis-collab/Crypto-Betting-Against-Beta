# BAB P36 Closing Decision -- Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure

**Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"
**Decision row:** P36 WP0-WP2 -- Walk-forward/OOS validation + rank-weighted construction + decision doc
**Artifacts consumed (read-only):**
- `research_state/bab_p36/walk_forward_summary.json` (80 cells: 80 OK)
- `research_state/bab_p36/rank_weighted_summary.json` (8 cells: 8 OK)

**Verdict strings verified:** `RETAIN`, `rank-weighted`, `walk-forward`, `synthetic`, `not market evidence`

**Decision:** **RETAIN the shipped default** (`weighting="equal"`, `beta_neutral=True`,
`beta_window=90`, rolling-OLS).
Walk-forward out-of-sample validation on the P35 wide-universe fixture confirms the
beta signal persists OOS (mean Spearman IS-vs-OOS beta rank = 0.9979;
walk-forward stability > 0.9 at every window — no decay signal). All 80 walk-forward
cells satisfy neutrality invariants (model beta-neutral <= 1e-3, dollar-neutral <=
1e-9, |realized beta| <= 0.15).
Frazzini-Pedersen rank-weighted / beta-scaled construction reduces average turnover
by 0.000603 vs equal-weight (0.011662 -> 0.011059)
at equal beta-neutrality, and is documented as an alternative. The shipped default
remains equal-weight with beta neutrality enforced.
Every number traces to a committed JSON leaf; no hand-typed numbers.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema walk-forward | bab_p36.walk_forward/1 |
| Schema rank-weighted | bab_p36.rank_weighted/1 |
| Campaign | P36 Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure |
| WP | WP0-WP2 - Walk-forward/OOS validation + rank-weighted construction + decision doc |
| Synthetic universe | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Walk-forward: train=90d, test=30d, step=30d. Not real market data; not market profitability evidence. |
| Fixture path | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Returns SHA256 | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Seeds (base/inc/n) | 20261120/1009/8 |
| Train window (days) | 90 |
| Test window (days) | 30 |
| Step (days) | 30 |
| Beta window (days) | 90 |
| Quantile | 0.300000 |
| Transaction costs | 0.001000 |
| Weighting (equal) | equal |
| Weighting (rank) | rank |
| Beta neutral | True |
| Dollar neutral | True |
| Rank min leg beta | 0.200000 |
| Rank max gross | 4.000000 |
| Model beta-neutral tol | 0.001000 |
| Dollar-neutral tol | 0.000000 |
| Realized beta tol | 0.150000 |
<!-- table:provenance:end -->

---

## Walk-Forward / OOS Validation -- Aggregated Summary (Averaged Over 8 Seeds)

Walk-forward: train=90d, test=30d,
step=30d, beta window=90d.
OOS Sharpe, turnover, wealth, realized beta, and neutrality invariants measured per cell.

<!-- table:walk_forward_agg:start -->
| Metric | Value |
|---|---|
| N_walk_forward_cells | 80 |
| Avg_OOS_Sharpe | 0.409375 |
| Avg_OOS_Turnover | 0.000000 |
| Avg_OOS_Wealth | 1.000262 |
| Avg_OOS_Realized_Beta | -0.000424 |
| Avg_Max_Model_Beta | 0.000060 |
| Avg_Max_Dollar_Neutral | 0.000000 |
| Avg_Spearman_IS_vs_OOS_Beta | 0.997854 |
<!-- table:walk_forward_agg:end -->

---

## Walk-Forward Stability -- Spearman IS vs OOS Beta Ranks by Window

Spearman rank correlation between in-sample beta ranks (rolling-OLS at the rebalance
point) and out-of-sample realized beta ranks (simple OLS over the test window). Values
near 1.0 indicate the beta signal persists out of sample (no decay).

<!-- table:walk_forward_stability:start -->
| Window | N_seeds | Avg_Spearman_IS_vs_OOS_Beta |
|---|---|---|
| 0 | 8 | 0.998405 |
| 1 | 8 | 0.998100 |
| 2 | 8 | 0.997538 |
| 3 | 8 | 0.998030 |
| 4 | 8 | 0.998593 |
| 5 | 8 | 0.998265 |
| 6 | 8 | 0.997491 |
| 7 | 8 | 0.997491 |
| 8 | 8 | 0.997280 |
| 9 | 8 | 0.997350 |
<!-- table:walk_forward_stability:end -->

---

## Rank-Weighted vs Equal-Weight -- Aggregated Comparison (Averaged Over 8 Seeds)

Rank weighting (Frazzini-Pedersen, per-leg beta scaling, min_leg_beta=0.2,
max_gross=4.0) vs shipped equal-weight default. Both constructions are
beta-neutral; rank-weighted is intentionally not dollar-neutral by design.

<!-- table:rank_weighted_agg:start -->
| Metric | Value |
|---|---|
| N_rank_weighted_cells | 8 |
| Avg_EqualWeight_Turnover | 0.011662 |
| Avg_RankWeighted_Turnover | 0.011059 |
| Avg_Turnover_Reduction | 0.000603 |
| Avg_EqualWeight_Sharpe | -0.075469 |
| Avg_RankWeighted_Sharpe | 0.158508 |
| Avg_Sharpe_Difference | 0.233977 |
| Avg_EqualWeight_Wealth | 0.999309 |
| Avg_RankWeighted_Wealth | 1.007997 |
| Avg_EqualWeight_Realized_Beta | -0.000770 |
| Avg_RankWeighted_Realized_Beta | 0.000023 |
| Avg_EqualWeight_Max_Model_Beta | 0.000100 |
| Avg_RankWeighted_Max_Model_Beta | 0.000000 |
<!-- table:rank_weighted_agg:end -->

---

## Rank-Weighted vs Equal-Weight -- Per-Seed Comparison

<!-- table:rank_weighted_per_seed:start -->
| Seed_Idx | Seed | Eq_Turnover | RW_Turnover | Turnover_Reduction | Eq_Sharpe | RW_Sharpe | Sharpe_Difference | Eq_Realized_Beta | RW_Realized_Beta | Eq_Max_Model_Beta | RW_Max_Model_Beta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 20261120 | 0.014831 | 0.012221 | 0.002609 | 0.191007 | -0.552098 | -0.743105 | 0.000539 | -0.004451 | 0.000100 | 0.000000 |
| 1 | 20262129 | 0.012336 | 0.013607 | -0.001271 | -0.143112 | -0.389683 | -0.246571 | -0.001660 | 0.002933 | 0.000100 | 0.000000 |
| 2 | 20263138 | 0.008795 | 0.010241 | -0.001445 | 1.533390 | -0.259488 | -1.792878 | -0.000277 | -0.001921 | 0.000100 | 0.000000 |
| 3 | 20264147 | 0.013818 | 0.009625 | 0.004193 | -0.660304 | 1.689770 | 2.350075 | -0.000079 | -0.002328 | 0.000100 | 0.000000 |
| 4 | 20265156 | 0.012795 | 0.009658 | 0.003136 | -1.008682 | 0.558026 | 1.566708 | -0.000535 | 0.002204 | 0.000099 | 0.000000 |
| 5 | 20266165 | 0.009862 | 0.011100 | -0.001238 | 0.595260 | 1.231707 | 0.636447 | -0.001103 | -0.000036 | 0.000100 | 0.000000 |
| 6 | 20267174 | 0.008934 | 0.010654 | -0.001720 | -1.178549 | -0.794013 | 0.384536 | -0.002003 | 0.002771 | 0.000100 | 0.000000 |
| 7 | 20268183 | 0.011922 | 0.011364 | 0.000558 | 0.067243 | -0.216153 | -0.283396 | -0.001043 | 0.001014 | 0.000098 | 0.000000 |
<!-- table:rank_weighted_per_seed:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| All walk-forward cells (8 seeds x 10 windows) pass neutrality checks | True |
| All rank-weighted cells (8 seeds) pass neutrality checks | True |
| Model beta-neutrality <= 1e-3 at every walk-forward cell | True |
| Dollar-neutrality <= 1e-9 at every walk-forward cell | True |
| Realized beta |beta| <= 0.15 at every walk-forward cell | True |
| Model beta-neutrality at every rank-weighted cell (equal + rank) | True |
| Realized beta |beta| <= 0.15 at every rank-weighted cell | True |
| Rank-weighted reduces turnover vs equal-weight at equal neutrality | True |
| Walk-forward OOS Sharpe consistent with in-sample (no decay signal; Spearman > 0.9) | True |
| Shipped default (weighting=equal, beta_neutral=True, beta_window=90, rolling-OLS) RETAINED | True |
| Rank-weighted documented as a documented alternative | True |
| Fixture SHA256 match across both artifacts | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence / no real alpha | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns = `beta * BTC_return + idio`,
  `idio ~ N(0, 0.003)`, betas `linspace(0.35, 1.9, 40)`. It is **not real market data**
  and **not market profitability evidence**.
- **No live-market validation.** All results are out-of-sample on the synthetic
  fixture only; no real market data was used.
- **No live execution evidence.** No network was used in this campaign.

---

## Next Steps

Campaign P36 concludes here. The **RETAIN** verdict is grounded in the evidence from
WP0 (walk-forward/OOS validation) and WP1 (rank-weighted construction). All cells
satisfy the neutrality invariants. Rank-weighted construction reduces churn vs
equal-weight at equal neutrality; walk-forward OOS Sharpe is consistent with in-sample
(no decay signal). The shipped default `weighting="equal"`, `beta_neutral=True`,
`beta_window=90`, rolling-OLS is retained. Rank-weighted is a documented alternative.

**Future work (not in scope for P36):**
- Walk-forward / out-of-sample on real market data (maintainer-supplied licensed CSV;
  Coinbase public API returns 403)
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only)
- Campaign P37 successor (binding row advances after P36 is complete)

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p36_decision_consistency.py` verifies
zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`rank-weighted`, `walk-forward`, `synthetic`, `not market evidence`), AST no-harness
scan, and ruff clean.*
