
# BAB P25 Closing Decision -- Rank-Weighting Promotion via Wide-Universe OOS Validation

**Campaign:** P25 "Rank-weighting promotion via wide-universe OOS validation"
**Decision row:** P25 WP3 - promotion decision + lint
**Artifacts consumed (read-only):**
- `research_state/bab_p25/promotion_bakeoff.json`
- `research_state/bab_p25/promotion_bakeoff.md`
- `tests/fixtures/wide_bab_universe.csv` (WP0 fixture)
- `tests/fixtures/wide_bab_universe_meta.json` (WP0 fixture metadata)

**Verdict strings verified:** `promote`, `no-promote`, `controlled synthetic`,
`not market evidence`

**Decision:** **PROMOTE** - the Frazzini-Pedersen rank-weighted BAB book
(`weighting="rank"`) is promoted over the equal-weight default based on the P25
WP2 equal-vs-rank OOS bake-off evidence. Rank mean OOS Sharpe 0.437311 vs equal
0.170267 (delta +0.267044). Both weightings beta-neutral per fold
(|portfolio beta| < 1e-2). 40 nonflat OOS rows per fold per weighting (200 total
per weighting). 5 folds, identical causal folds. Fixture SHA256 provenance
matches WP0. `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` unchanged. This is
a **decision-grade** promotion verdict: every published number traces to a
committed JSON leaf, and the wide universe is labelled **controlled synthetic**
throughout.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema | bab_p25.promotion_bakeoff/1 |
| Campaign | P25 |
| WP | WP3 - promotion decision + lint |
| Seed | 20261120 |
| Synthetic | True |
| Fixture path | tests/fixtures/wide_bab_universe.csv |
| Fixture SHA256 | `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` |
| WP0 fixture SHA256 match | True |
| Price rows | 399 |
| Return rows | 398 |
| Beta window | 90 |
| Train window | 180 |
| Test window | 40 |
| Long quantile | 0.300000 |
| Short quantile | 0.300000 |
| Rank min leg beta | 0.200000 |
| Rank max gross | 4.000000 |
| Weightings evaluated | equal, rank |
| N folds | 5 |
| Total OOS rows | 200 |
| Candidates evaluated | 10 |
| Rank beta-neutral folds | 5 |
| No lookahead | Each fold runs both weightings over causal history [0, test_end); weights at row t use the one-day backtest lag and rolling betas computed from returns through t-1, so the OOS return at row t is never used to weight itself. The test slice [test_start, test_end) is scored but never read during weight construction for that row. Equal and rank are run on identical folds. |
<!-- table:provenance:end -->

---

## Per-Fold OOS Comparison (Equal vs Rank)

<!-- table:folds:start -->
| fold | n_train | n_test | equal_oos_sharpe | rank_oos_sharpe | delta_oos_sharpe | equal_oos_wealth | rank_oos_wealth | delta_oos_wealth | equal_portfolio_beta | rank_portfolio_beta | delta_portfolio_beta | equal_oos_turnover | rank_oos_turnover | delta_oos_turnover | equal_nonflat_rows | rank_nonflat_rows | equal_beta_spread | rank_beta_spread |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 180 | 40 | 2.464833 | 0.256134 | -2.208699 | 1.002272 | 1.001581 | -0.000691 | -0.000024 | -0.000000 | 0.000024 | 0.021467 | 0.005719 | -0.015748 | 40 | 40 | 1.108159 | 1.108159 |
| 1 | 220 | 40 | -0.321648 | 0.539000 | 0.860648 | 0.999678 | 1.002260 | 0.002582 | 0.000008 | -0.000000 | -0.000008 | 0.014622 | 0.030547 | 0.015925 | 40 | 40 | 1.107565 | 1.107565 |
| 2 | 260 | 40 | -1.362306 | -0.804475 | 0.557831 | 0.998424 | 0.995485 | -0.002939 | -0.000074 | 0.000000 | 0.000074 | 0.007181 | 0.011565 | 0.004384 | 40 | 40 | 1.112389 | 1.112389 |
| 3 | 300 | 40 | -3.020664 | 0.931271 | 3.951935 | 0.996451 | 1.005096 | 0.008645 | 0.000026 | 0.000000 | -0.000026 | 0.008331 | 0.011375 | 0.003044 | 40 | 40 | 1.118880 | 1.118880 |
| 4 | 340 | 40 | 3.091118 | 1.264624 | -1.826494 | 1.003164 | 1.006119 | 0.002955 | 0.000072 | -0.000000 | -0.000072 | 0.014000 | 0.008843 | -0.005157 | 40 | 40 | 1.130011 | 1.130011 |
<!-- table:folds:end -->

---

## Aggregate OOS Metrics

<!-- table:aggregate:start -->
| key | value |
|---|---|
| equal_mean_oos_sharpe | 0.170267 |
| rank_mean_oos_sharpe | 0.437311 |
| delta_mean_oos_sharpe | 0.267044 |
| equal_mean_oos_wealth | 0.999998 |
| rank_mean_oos_wealth | 1.002108 |
| delta_mean_oos_wealth | 0.002110 |
| equal_mean_portfolio_beta | 0.000002 |
| rank_mean_portfolio_beta | 0.000000 |
| delta_mean_portfolio_beta | -0.000002 |
| equal_mean_oos_turnover | 0.013120 |
| rank_mean_oos_turnover | 0.013610 |
| delta_mean_oos_turnover | 0.000490 |
| equal_mean_nonflat_rows | 40.000000 |
| rank_mean_nonflat_rows | 40.000000 |
| equal_mean_beta_spread | 1.115401 |
| rank_mean_beta_spread | 1.115401 |
| rank_beta_neutral_folds | 5 |
| total_oos_rows | 200 |
| candidates_evaluated | 10 |
<!-- table:aggregate:end -->

---

## Decision Criteria (Chartered from P25 Spec)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Explicit promote/no-promote verdict for weighting="rank" | True |
| Delta mean OOS Sharpe > 0 (rank beats equal) | True |
| Both weightings beta-neutral per fold (|portfolio beta| < 1e-2) | True |
| 40 nonflat OOS rows per fold per weighting | True |
| 5 folds, identical causal folds for both weightings | True |
| Fixture SHA256 matches WP0 | True |
| rank_min_leg_beta=0.20 unchanged | True |
| rank_max_gross=4.0 unchanged | True |
| Deterministic byte-identical artifact | True |
| No lookahead (weights at t use data through t-1 only) | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The wide synthetic universe is a
  controlled synthetic stimulus with uniformly spanning betas (0.35 to 1.90 vs
  BTC), idiosyncratic vol 0.003, and a known ground truth. It is **not real
  market data** and **not market profitability evidence**.
- **No out-of-sample validation on real data.** All results are on the
  controlled synthetic wide universe (seed 20261120). The promotion is based on
  OOS evaluation on synthetic data only.
- **No walk-forward on real market data.** Campaign P25 closes the
  rank-weighting promotion question on the synthetic wide universe. Real-market
  deployment requires Campaign P26 signal-to-noise validation.
- **No capacity/turnover analysis on real markets.** The synthetic universe has
  no market impact model. P26 WP2 addresses capacity & turnover of the rank
  book.
- **No regime stress on real markets.** The synthetic universe has no regime
  structure beyond BTC volatility. P26 WP1 addresses regime-conditional rank
  stress.

---

## Next Steps

Campaign P25 concludes here. The PROMOTE verdict is grounded in the committed
P25 WP2 bake-off JSON artifact. All numbers are labelled **controlled
synthetic** - never market alpha. The Frazzini-Pedersen rank-weighted
construction with beta-neutrality by default is promoted as the default
weighting for the BAB strategy on wide cross-sections.

**Future work** (Campaign P26 - "Signal-to-Noise Validation of Rank-Weighted
BAB"):
- WP0: Signal vs null battery - test rank-weighted BAB against 1000 permuted
  null books
- WP1: Regime-conditional rank stress - split wide universe into calm/stress
  regimes
- WP2: Capacity & turnover of rank book - sweep gross exposure caps and
  rebalance frequencies
- WP3: Signal-to-noise closing decision

---

*This report is artifact-gated: every numeric table cell resolves to a
committed JSON leaf at 6 dp. The acceptance test
`tests/test_bab_p25_decision_consistency.py` verifies zero unmatched cells,
byte-identical table rendering, AST no-harness scan, and explicit verdict
strings.*
