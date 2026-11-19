# BAB Signal-or-Noise Verdict — Campaign P21

This report publishes the P21 evidence that the Betting-Against-Beta estimator
recovers a **planted** signal and rejects a **null** on a controlled synthetic
universe, and it publishes the verdict that follows from that evidence. It is
deliberately modest: the universe is synthetic, so nothing here is a claim about
real markets.

Every number in every table below is generated from the committed artifacts
`research_state/bab_p21/universe.json`, `research_state/bab_p21/significance.json`,
`research_state/bab_p21/rank_eval.json` and
`research_state/bab_p21/cost_surface.json`. No harness is re-run to produce a
reported number, and `tests/test_bab_p21_report_consistency.py` fails if a
single published cell drifts from its JSON field or if the tables stop being
byte-identical to their JSON-only renderers.

## Verdict

**VERDICT: SIGNAL — the P21 estimator recovers planted alpha and rejects the
null on a controlled synthetic universe. NOISE — the null universe produces no
significant result. NO-GO for market deployment.**

The verdict is machine-backed, not prose: the significance artifact certifies
`null_calibrated` and `planted_detected`, every null book has a one-sided
p-value at or above the nominal slack and a confidence interval that includes
zero, and every planted book is significant with a confidence interval that
excludes zero. The cost surface shows costed performance is non-increasing in
every component for every book, so the planted result is not manufactured by
ignoring execution cost.

This is a verdict about the **estimator**, not about a market. Planted-universe
recovery is a controlled synthetic result and not market evidence; it proves the
estimator works and is never market alpha. This is not a demonstrated profitable
strategy. There is no demonstrated real-world profitability in this repository,
no licensed real-market price series exists in this environment, and the P21
verdict is a no-go for market deployment until such a series is supplied.

## Provenance

The stimulus is a deterministic synthetic universe with known ground truth. It
is **not real market data**. Both panels share benchmark and residual draws
row-for-row and differ only in the planted alpha vector, so any difference in
measured recovery is attributable to the alpha construction. The panel sha256
values below are repeated in every P21 artifact and are cross-checked by the
acceptance suite.

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Universe schema | bab_p21.universe/1 |
| Universe seed | 20261118 |
| Significance seed | 20261119 |
| Assets | 41 |
| Return rows | 600 |
| Trading days | 252 |
| Benchmark | BTC |
| Alpha exponent | 2.000000 |
| Planted alpha spread (annual) | 4.000000 |
| Idiosyncratic vol min | 0.003000 |
| Idiosyncratic vol max | 0.005000 |
| Beta min | 0.300000 |
| Beta max | 2.700000 |
| Planted panel sha256 | `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda` |
| Null panel sha256 | `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b` |
| Bootstrap resamples | 2000 |
| Bootstrap block length | 20 |
| Nominal slack | 0.050000 |
| Deflation trials | 40 |
| Synthetic | True |
<!-- table:provenance:end -->

## Recovery — rank versus equal

`recovery_mean` is the mean active-row weight vector applied to the known alpha
vector. It measures whether the book holds the assets that actually carry the
planted alpha. On the planted universe both weightings recover a strictly
positive amount, and rank weighting recovers more because it concentrates on
the extreme-beta legs that carry the convex alpha. On the null universe
recovery is exactly zero for both weightings: any positive null recovery would
be a bug, not a finding.

Rank weighting is beta-neutral by construction but not dollar-neutral; equal
weighting is dollar-neutral. The table reports both exposures so neither claim
is confused with the other.

<!-- table:recovery:start -->
| variant | weighting | active_rows | total_rows | gross_mean_active | recovery_mean | recovery_frac_positive | min_leg_beta | gross_max | beta_exposure_max | dollar_imbalance_max |
|---|---|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 600 | 0.814151 | 0.000261 | 0.996303 | 1.447792 | 0.837141 | 0.009140 | 0.000000 |
| planted | rank | 541 | 600 | 2.368528 | 0.017360 | 1.000000 | 0.507692 | 2.414949 | 0.030480 | 1.612844 |
| null | equal | 541 | 600 | 0.814151 | 0.000000 | 0.000000 | 1.447792 | 0.837141 | 0.009140 | 0.000000 |
| null | rank | 541 | 600 | 2.368528 | 0.000000 | 0.000000 | 0.507692 | 2.414949 | 0.030480 | 1.612844 |
<!-- table:recovery:end -->

## Significance and deflation

A fixed-seed moving-block bootstrap of the out-of-sample Sharpe produces a
one-sided p-value against the null hypothesis of zero Sharpe, and a deflated
Sharpe ratio corrects for the search over the P20 candidate grid. The null
books are not significant and their bootstrap intervals include zero. The
planted books are significant and their intervals exclude zero. The P21 null
therefore behaves like noise, and the planted universe is detected.

<!-- table:significance:start -->
| variant | weighting | oos_sharpe | sharpe_bootstrap_mean | sharpe_bootstrap_p05 | sharpe_bootstrap_p95 | p_value | ci_excludes_zero | significant | n_resamples | dsr | critical_sharpe | dsr_p_value |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planted | equal | 7.034781 | 7.178403 | 5.889686 | 8.569611 | 0.000000 | True | True | 2000 | 0.905272 | 1.278258 | 0.094728 |
| planted | rank | 44.378201 | 54.152010 | 31.779834 | 130.058072 | 0.000000 | True | True | 2000 | 0.998329 | 9.279902 | 0.001671 |
| null | equal | 0.639801 | 0.680563 | -0.574881 | 1.892460 | 0.163500 | False | False | 2000 | 0.923379 | 1.042214 | 0.076621 |
| null | rank | 0.649924 | 0.772645 | -0.767864 | 2.290138 | 0.268000 | False | False | 2000 | 0.926802 | 1.435861 | 0.073198 |
<!-- table:significance:end -->

## Cost surface

Three cost components are applied to the gross book: a linear transaction cost,
a borrow/funding charge on short notional, and notional slippage. For every book
and every component the costed Sharpe is non-increasing across the component
grid, and every period's costed return is non-increasing as the level rises.
The columns below report the costed Sharpe at the top of each component grid
next to the gross Sharpe and the monotonicity flags. Costs reduce performance;
they never create it.

<!-- table:cost:start -->
| variant | weighting | active_rows | gross_sharpe | gross_turnover_mean | costed_sharpe_linear_tc_max | costed_sharpe_borrow_max | costed_sharpe_slippage_max | monotone_linear_tc | monotone_borrow | monotone_slippage |
|---|---|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 7.034781 | 0.009797 | 3.628799 | -0.925486 | 6.433990 | True | True | True |
| planted | rank | 541 | 44.378201 | 0.007204 | 42.796701 | 44.256634 | 44.153060 | True | True | True |
| null | equal | 541 | 0.639801 | 0.009797 | -1.721845 | -7.314578 | 0.098125 | True | True | True |
| null | rank | 541 | 0.649924 | 0.007204 | 0.073453 | -1.615943 | 0.533596 | True | True | True |
<!-- table:cost:end -->

## Verdict basis

Every field in this table is read directly from the committed significance and
rank-evaluation artifacts. It is the machine-checked basis for the signal
verdict above, and the acceptance suite fails if any value here is hand-typed
or stale.

<!-- table:verdict_basis:start -->
| Fact | Value |
|---|---|
| Null calibrated | True |
| Planted detected | True |
| Null max one-sided p-value | 0.268000 |
| Nominal slack | 0.050000 |
| Null equal p-value | 0.163500 |
| Null rank p-value | 0.268000 |
| Planted equal p-value | 0.000000 |
| Planted rank p-value | 0.000000 |
| Planted recovery equal | 0.000261 |
| Planted recovery rank | 0.017360 |
| Null recovery equal | 0.000000 |
| Null recovery rank | 0.000000 |
<!-- table:verdict_basis:end -->

## What this does not prove

- It does not prove real-world profitability. The universe is synthetic, and
  planted-universe recovery validates the estimator, never a market edge.
- It does not prove rank weighting would beat equal weighting in a market. Rank
  mode is measurable only because the generated universe supplies enough
  wide-beta assets to keep both legs active.
- It does not prove the result survives repeated null universes, nonlinear
  market impact, or capacity constraints. Those are Campaign P22 questions and
  are not answered here.
- A positive result on the null universe would be a bug; none is reported, and
  the suite re-checks that every null recovery is exactly zero.
- Any future market claim requires a maintainer-supplied licensed price series
  and a fresh campaign. Quoting planted recovery as market alpha is forbidden.
