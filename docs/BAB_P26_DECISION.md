
# BAB P26 Closing Decision -- Signal-to-Noise Validation of Rank-Weighted BAB

**Campaign:** P26 "Signal-to-Noise Validation of Rank-Weighted BAB"
**Decision row:** P26 WP3 - signal-to-noise closing decision
**Lane:** C
**Artifacts consumed (read-only):**
- `research_state/bab_p26/signal_null_battery.json` (WP0 signal vs null battery)
- `research_state/bab_p26/regime_stress.json` (WP1 regime-conditional rank stress)
- `research_state/bab_p26/rank_capacity.json` (WP2 capacity & turnover of rank book)
- `tests/fixtures/wide_bab_universe.csv` (P25 WP0 fixture, read-only)

**Verdict strings verified:** `SIGNAL`, `NO-SIGNAL`, `controlled synthetic`,
`not market evidence`

**Decision:** **NO-SIGNAL** - the Frazzini-Pedersen rank-weighted BAB book
(`weighting="rank"`) shows no reproducible signal on the committed no-alpha
synthetic fixture. The signal-vs-null battery returns NO-SIGNAL (rank p=0.285714,
equal p=0.358641; the SIGNAL condition `p_rank < 0.05 AND p_equal > 0.05` is
false because both p-values exceed 0.05 — correct anti-victory outcome). The
regime-conditional falsification gate does not pass: calm rank mean OOS Sharpe
0.817343 > 0 passes, but stress rank mean OOS Sharpe -0.132738 is not below
equal mean OOS Sharpe -0.841977, so Assertion B fails. Capacity & turnover show
rank survives capacity mechanically at the default cell (gross_cap=4.0,
rebalance_freq=daily): rank 0.437311 vs equal 0.170267 (delta +0.267044), rank
break-even AUM ~$1.63B vs equal None — but on a no-alpha fixture that premium is
mechanical idio spread, not signal. No real alpha is demonstrated, so no
real-market deployment claim is made. `rank_min_leg_beta=0.20` /
`rank_max_gross=4.0` are unchanged — never weakened to force a verdict. This is
a **decision-grade** NO-SIGNAL verdict: every published number traces to a
committed JSON leaf, and the wide universe is labelled **controlled synthetic**
throughout.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema | bab_p26.signal_null_battery/1 |
| Campaign | P26 |
| WP | WP3 - signal-to-noise closing decision |
| Seed | 20261120 |
| Synthetic | True |
| Fixture path | tests/fixtures/wide_bab_universe.csv |
| Fixture SHA256 | `a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b` |
| WP0 fixture SHA256 match | True |
| Price rows | 399 |
| Return rows | 398 |
| Beta window | 90 |
| Min observations | 60 |
| Train window | 180 |
| Test window | 40 |
| Long quantile | 0.300000 |
| Short quantile | 0.300000 |
| Rank min leg beta | 0.200000 |
| Rank max gross | 4.000000 |
| N folds | 5 |
| N null replications | 1000 |
| P level | 0.050000 |
| Weightings evaluated | equal, rank |
| No lookahead | Each fold runs both weightings over causal history [0, test_end); weights at row t use the one-day backtest lag and rolling betas computed from returns through t-1, so the OOS return at row t is never used to weight itself. The test slice [test_start, test_end) is scored but never read during weight construction for that row. Equal and rank are run on identical folds. |
<!-- table:provenance:end -->

---

## WP0 Signal vs Null Battery

<!-- table:wp0:start -->
| key | value |
|---|---|
| p_level | 0.050000 |
| verdict_rule | SIGNAL iff p_rank < 0.05 and p_equal > 0.05; otherwise NO-SIGNAL. |
| n_folds | 5 |
| n_null_replications | 1000 |
| equal_observed_oos_sharpe | 0.170267 |
| rank_observed_oos_sharpe | 0.437311 |
| equal_z_score | 0.399589 |
| rank_z_score | 0.605300 |
| equal_p_value | 0.358641 |
| rank_p_value | 0.285714 |
| equal_null_mean | -0.348462 |
| rank_null_mean | -0.348462 |
| equal_null_std | 1.298155 |
| rank_null_std | 1.298155 |
| equal_empirical_percentile | 64.200000 |
| rank_empirical_percentile | 71.500000 |
| equal_null_min | -4.004163 |
| rank_null_min | -4.004163 |
| equal_null_max | 3.426797 |
| rank_null_max | 3.426797 |
| wp0_verdict | NO-SIGNAL |
<!-- table:wp0:end -->

---

## WP1 Regime-Conditional Rank Stress

<!-- table:wp1:start -->
| key | value |
|---|---|
| falsification_gate_passed | False |
| assertion_a_calm_rank_positive | True |
| assertion_b_stress_rank_below_equal | False |
| calm_rank_mean_oos_sharpe | 0.817343 |
| stress_equal_mean_oos_sharpe | -0.841977 |
| stress_rank_mean_oos_sharpe | -0.132738 |
| calm_delta_mean_oos_sharpe | -0.027753 |
| stress_delta_mean_oos_sharpe | 0.709239 |
| calm_equal_mean_oos_sharpe | 0.845096 |
| calm_rank_mean_oos_sharpe_full | 0.817343 |
| stress_equal_mean_oos_sharpe_full | -0.841977 |
| stress_rank_mean_oos_sharpe_full | -0.132738 |
| calm_n_folds_assigned | 3 |
| stress_n_folds_assigned | 2 |
| calm_folds_assigned | 0, 3, 4 |
| stress_folds_assigned | 1, 2 |
<!-- table:wp1:end -->

---

## WP2 Capacity & Turnover (default cell gross_cap=4.0, daily)

<!-- table:wp2:start -->
| key | value |
|---|---|
| gross_caps | 1.000000, 2.000000, 3.000000, 4.000000 |
| rebalance_freqs | daily, weekly, monthly |
| n_cells | 120 |
| default_cell | 9 |
| default_gross_cap | 4.000000 |
| default_rebalance_freq | daily |
| default_rank_max_gross | 4.000000 |
| default_equal_mean_oos_sharpe | 0.170267 |
| default_rank_mean_oos_sharpe | 0.437311 |
| default_delta_mean_oos_sharpe | 0.267044 |
| default_equal_mean_oos_wealth | 0.999998 |
| default_rank_mean_oos_wealth | 1.002108 |
| default_equal_mean_oos_turnover | 0.013120 |
| default_rank_mean_oos_turnover | 0.013610 |
| default_equal_mean_portfolio_beta | 0.000002 |
| default_rank_mean_portfolio_beta | 0.000000 |
| default_equal_break_even_aum | None |
| default_rank_break_even_aum | 1633086273.923364 |
<!-- table:wp2:end -->

---

## WP2 Per-Fold OOS Detail (default cell gross_cap=4.0, daily)

<!-- table:wp2_folds:start -->
| fold | weighting | mean_oos_return | nonflat_rows | oos_max_drawdown | oos_realized_beta | oos_sharpe | oos_turnover | oos_vol | oos_wealth | portfolio_beta | test_end | test_start |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | equal | 0.000057 | 40 | -0.001913 | -0.002335 | 2.464833 | 0.021467 | 0.005807 | 1.002272 | -0.000024 | 220 | 180 |
| 0 | rank | 0.000043 | 40 | -0.014579 | 0.008633 | 0.256134 | 0.005719 | 0.042264 | 1.001581 | -0.000000 | 220 | 180 |
| 1 | equal | -0.000008 | 40 | -0.001918 | 0.002774 | -0.321648 | 0.014622 | 0.006249 | 0.999678 | 0.000008 | 260 | 220 |
| 1 | rank | 0.000058 | 40 | -0.006228 | 0.004233 | 0.539000 | 0.030547 | 0.027043 | 1.002260 | -0.000000 | 260 | 220 |
| 2 | equal | -0.000039 | 40 | -0.003455 | 0.001902 | -1.362306 | 0.007181 | 0.007273 | 0.998424 | -0.000074 | 300 | 260 |
| 2 | rank | -0.000111 | 40 | -0.022465 | -0.050654 | -0.804475 | 0.011565 | 0.034706 | 0.995485 | 0.000000 | 300 | 260 |
| 3 | equal | -0.000089 | 40 | -0.004928 | -0.006254 | -3.020664 | 0.008331 | 0.007406 | 0.996451 | 0.000026 | 340 | 300 |
| 3 | rank | 0.000129 | 40 | -0.012527 | -0.024523 | 0.931271 | 0.011375 | 0.035034 | 1.005096 | 0.000000 | 340 | 300 |
| 4 | equal | 0.000079 | 40 | -0.002241 | 0.005264 | 3.091118 | 0.014000 | 0.006445 | 1.003164 | 0.000072 | 380 | 340 |
| 4 | rank | 0.000154 | 40 | -0.010102 | 0.019416 | 1.264624 | 0.008843 | 0.030755 | 1.006119 | -0.000000 | 380 | 340 |
<!-- table:wp2_folds:end -->

---

## Decision Criteria (Chartered from P26 Spec)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Explicit SIGNAL / NO-SIGNAL verdict for weighting="rank" | True |
| WP0 verdict == NO-SIGNAL (NO-SIGNAL) | True |
| p_rank == 0.285714 (< 0.05 false) (actual 0.285714) | True |
| p_equal == 0.358641 (> 0.05 true) (actual 0.358641) | True |
| SIGNAL condition p_rank < 0.05 AND p_equal > 0.05 is false | True |
| WP1 falsification_gate_passed == False (actual False) | True |
| WP1 assertion_a (calm rank > 0) == True (actual True) | True |
| WP1 assertion_b (stress rank < equal) == False (actual False) | True |
| WP2 default-cell rank mean OOS Sharpe == 0.437311 (actual 0.437311) | True |
| WP2 default-cell equal mean OOS Sharpe == 0.170267 (actual 0.170267) | True |
| WP2 default-cell delta mean OOS Sharpe == +0.267044 (actual 0.267044) | True |
| WP2 rank survives capacity at default cell (rank > equal) | True |
| Both weightings beta-neutral per fold at default cell (|portfolio beta| < 1e-2) | True |
| Fixture SHA256 matches WP0 (a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b) | True |
| rank_min_leg_beta=0.20 unchanged | True |
| rank_max_gross=4.0 unchanged | True |
| Deterministic byte-identical artifact | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The wide synthetic universe is a
  controlled synthetic stimulus (`r = beta·r_BTC + idio`, `idio ~ N(0, 0.003)`
  iid) with no cross-sectional alpha planted. It is **not real market data** and
  **not market profitability evidence**.
- **No signal distinguishable from noise.** The null battery shows both weightings
  are consistent with the beta-neutral-preserving null (rank p=0.285714, equal
  p=0.358641). The rank premium is not statistically significant.
- **No regime robustness.** The rank premium does not survive regime stress: in
  the high-volatility regime rank (-0.132738) is not below equal (-0.841977),
  so Assertion B fails and the falsification gate does not pass.
- **No real-market capacity evidence.** Capacity break-even figures are synthetic
  square-root impact estimates on the controlled fixture, not market data.
- **No market alpha claimed.** Real-market deployment requires licensed market
  data; this synthetic result is **never market alpha**.
- **No out-of-sample validation on real data.** All results are on the controlled
  synthetic wide universe (seed 20261120).

---

## Next Steps

Campaign P26 concludes here with a NO-SIGNAL verdict. Real-market efficacy of
rank-weighted BAB requires licensed market data (maintainer-supplied; never
network-fetch Coinbase — returns 403). Do not edit the frozen P25 WP0 fixture to
"plant" alpha to force SIGNAL; if a mechanics-only planted-alpha fixture is
desired, it is a NEW campaign (P27) with its own frozen fixture, clearly
labelled "planted mechanics, not market evidence."

---

*This report is artifact-gated: every numeric table cell resolves to a committed
JSON leaf at 6 dp. The acceptance test
`tests/test_bab_p26_decision_consistency.py` verifies zero unmatched cells,
byte-identical table rendering, AST no-harness scan, and explicit verdict
strings.*
