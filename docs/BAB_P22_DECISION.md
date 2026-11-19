# BAB P22 — Decision report

**Campaign:** P22 "Decision-grade validation" · **Verdict:** **NO-GO for market deployment**. The evidence is a controlled synthetic stimulus with known ground truth; it is not market evidence, not real market data, and never market alpha. No demonstrated real-world profitability is established here, and this is not a demonstrated profitable strategy.

This is the decision-grade closing document for campaign P22. It consumes the committed P22 JSON artifacts read-only, re-renders every published table from them, never re-runs a research harness and never edits an earlier artifact. Every numeric table cell is machine-matched to a committed JSON field at six decimal places by `tests/test_bab_p22_decision_consistency.py`; the unmatched-cell count is zero.

## Provenance

Sources: `research_state/bab_p22/charter.json`, `research_state/bab_p22/null_battery.json`, `research_state/bab_p22/impact_surface.json` and `research_state/bab_p22/capacity.json`. The universe is the frozen P21 planted/null pair. Both panels are sha256-pinned and the reference seed reproduces the committed P21 panel hashes.

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Charter schema | bab_p22.charter/1 |
| Capacity schema | bab_p22.capacity/1 |
| Campaign | P22 |
| Charter question | Does the BAB estimator survive repeated null universes, nonlinear market impact, and capacity constraints? |
| Certified by prior campaign | Is the estimator calibrated and cost-aware on a controlled universe? Yes — signal on planted, noise on null, NO-GO for market. |
| Universe seed | 20261118 |
| Reference universe seed | 20261118 |
| Synthetic | True |
| Licensed data required | True |
| Not market evidence | True |
| Artifact gated | True |
| Nominal slack | 0.050000 |
| Planted panel sha256 | `aae2a70ebcf81b3a9e2dd5f314933c439194fef8a7be1da34930e2c271a93fda` |
| Null panel sha256 | `b7732c152564c87606a6a47eac39a543344cbcd4b8e974f4780be35671953b1b` |
| Reference panel shas matched | True |
<!-- table:provenance:end -->

## Null battery

The null battery reruns the shipped strategy over the chartered independent seeds for both weightings. Null recovery is exactly zero for every null book on every seed. A non-zero null recovery would be a bug, not a finding, so any such value invalidates the decision. The empirical false-positive rate is computed from the null books and stays within the bound declared in the charter. Planted recovery is strictly positive on every seed for both weightings, and the smallest planted recovery exceeds the largest null recovery.

<!-- table:null_battery:start -->
| Statistic | Value |
|---|---|
| Chartered seeds | 20 |
| Null books | 40 |
| Planted books | 40 |
| Null recovery max abs | 0.000000 |
| Null books with zero recovery | 40 |
| Null recovery exactly zero every seed | True |
| False positives | 2 |
| False-positive denominator | 40 |
| False-positive rate | 0.050000 |
| False-positive expected count | 2.000000 |
| False-positive max declared | 4 |
| False-positive within bound | True |
| Planted recovery min equal | 0.000206 |
| Planted recovery min rank | 0.017227 |
| Planted recovery positive fraction equal | 1.000000 |
| Planted recovery positive fraction rank | 1.000000 |
| Null Sharpe max | 1.288970 |
| Planted Sharpe min | 5.552134 |
| Planted recovery exceeds null max | True |
<!-- table:null_battery:end -->

### Per-seed null-battery panel

Each row is one chartered seed: planted recovery, null Sharpe and the null bootstrap p-value for both weightings. The rank weighting carries a higher gross exposure by construction, so its recovery and Sharpe are larger on the planted universe while its null p-values remain above the nominal slack.

<!-- table:null_seeds:start -->
| seed | planted_recovery_equal | planted_recovery_rank | null_sharpe_equal | null_sharpe_rank | null_p_equal | null_p_rank |
|---|---|---|---|---|---|---|
| 20261120 | 0.000234 | 0.017281 | -0.311248 | 0.192302 | 0.714500 | 0.365000 |
| 20261121 | 0.000252 | 0.017348 | -0.304673 | -0.023217 | 0.639000 | 0.516500 |
| 20261122 | 0.000246 | 0.017323 | -0.538605 | -0.008430 | 0.741000 | 0.501000 |
| 20261123 | 0.000264 | 0.017393 | 0.055382 | -0.942137 | 0.473500 | 0.899000 |
| 20261124 | 0.000259 | 0.017310 | 0.713294 | -0.097618 | 0.150000 | 0.595000 |
| 20261125 | 0.000232 | 0.017234 | 0.108230 | 0.261310 | 0.503500 | 0.347500 |
| 20261126 | 0.000256 | 0.017373 | -0.169524 | -1.155615 | 0.606000 | 0.903500 |
| 20261127 | 0.000248 | 0.017278 | 0.564512 | 1.192924 | 0.156000 | 0.009000 |
| 20261128 | 0.000253 | 0.017413 | 0.294281 | 0.321756 | 0.333000 | 0.308500 |
| 20261129 | 0.000257 | 0.017380 | 0.297174 | -0.360951 | 0.261500 | 0.676500 |
| 20261130 | 0.000237 | 0.017330 | -0.369068 | 0.653305 | 0.609500 | 0.100500 |
| 20261131 | 0.000249 | 0.017297 | 0.179330 | 0.628225 | 0.410500 | 0.136500 |
| 20261132 | 0.000234 | 0.017298 | 0.381937 | -0.148436 | 0.339500 | 0.524000 |
| 20261133 | 0.000231 | 0.017234 | 1.288970 | -0.473363 | 0.024500 | 0.726000 |
| 20261134 | 0.000254 | 0.017328 | 0.062595 | 0.271827 | 0.423500 | 0.368500 |
| 20261135 | 0.000206 | 0.017227 | 0.519202 | 0.491636 | 0.223000 | 0.226000 |
| 20261136 | 0.000251 | 0.017238 | -0.551676 | -2.047595 | 0.812000 | 0.999000 |
| 20261137 | 0.000247 | 0.017273 | 0.989214 | -0.807706 | 0.050500 | 0.906500 |
| 20261138 | 0.000221 | 0.017241 | -0.202465 | -0.664954 | 0.548500 | 0.847000 |
| 20261139 | 0.000245 | 0.017307 | -1.125581 | -0.060205 | 0.934500 | 0.484500 |
<!-- table:null_seeds:end -->

## Nonlinear impact surface

The impact model charges a square-root market-impact drag that scales with turnover raised to the three-halves power, layered on the committed exposure series. The zero-coefficient row reproduces the gross book exactly, costed Sharpe is non-increasing in the impact coefficient for every book and every period, and total cost rises monotonically. Costed Sharpe crosses zero for the planted equal book, the null equal book and the null rank book; the planted rank book stays positive across the whole declared grid and is therefore censored rather than assigned a midpoint.

<!-- table:impact:start -->
| variant | weighting | level | costed_sharpe | cost_drag_mean | total_cost | final_cumulative |
|---|---|---|---|---|---|---|
| planted | equal | 0.000000 | 7.034781 | 0.000000 | 0.000000 | 1.167118 |
| planted | equal | 0.020000 | 3.763395 | 0.000054 | 0.032418 | 1.129761 |
| planted | equal | 0.050000 | 1.167251 | 0.000135 | 0.081044 | 1.075471 |
| planted | equal | 0.100000 | -0.062016 | 0.000270 | 0.162088 | 0.989475 |
| planted | equal | 0.200000 | -0.717923 | 0.000540 | 0.324177 | 0.833239 |
| planted | equal | 0.500000 | -1.116263 | 0.001351 | 0.810441 | 0.471526 |
| planted | equal | 1.000000 | -1.249026 | 0.002701 | 1.620883 | 0.124562 |
| planted | rank | 0.000000 | 44.378201 | 0.000000 | 0.000000 | 11401.093638 |
| planted | rank | 0.020000 | 37.232543 | 0.000128 | 0.076710 | 10530.799945 |
| planted | rank | 0.050000 | 24.951852 | 0.000320 | 0.191775 | 9238.335098 |
| planted | rank | 0.100000 | 14.564397 | 0.000639 | 0.383549 | 7118.487825 |
| planted | rank | 0.200000 | 7.445557 | 0.001278 | 0.767098 | 3004.998876 |
| planted | rank | 0.500000 | 2.652254 | 0.003196 | 1.917745 | -8369.885186 |
| planted | rank | 1.000000 | 0.993625 | 0.006392 | 3.835490 | -24385.695661 |
| null | equal | 0.000000 | 0.639801 | 0.000000 | 0.000000 | 1.013905 |
| null | equal | 0.020000 | -0.578003 | 0.000054 | 0.032418 | 0.981449 |
| null | equal | 0.050000 | -1.072364 | 0.000135 | 0.081044 | 0.934281 |
| null | equal | 0.100000 | -1.241371 | 0.000270 | 0.162088 | 0.859567 |
| null | equal | 0.200000 | -1.316368 | 0.000540 | 0.324177 | 0.723829 |
| null | equal | 0.500000 | -1.356794 | 0.001351 | 0.810441 | 0.409589 |
| null | equal | 1.000000 | -1.369400 | 0.002701 | 1.620883 | 0.108190 |
| null | rank | 0.000000 | 0.649924 | 0.000000 | 0.000000 | 1.049395 |
| null | rank | 0.020000 | -0.201427 | 0.000128 | 0.076710 | 0.969222 |
| null | rank | 0.050000 | -0.490675 | 0.000320 | 0.191775 | 0.850177 |
| null | rank | 0.100000 | -0.591459 | 0.000639 | 0.383549 | 0.654977 |
| null | rank | 0.200000 | -0.639653 | 0.001278 | 0.767098 | 0.276393 |
| null | rank | 0.500000 | -0.667427 | 0.003196 | 1.917745 | -0.769021 |
| null | rank | 1.000000 | -0.676461 | 0.006392 | 3.835490 | -2.236534 |
<!-- table:impact:end -->

## Capacity and break-even

Break-even participation is computed by fixed-iteration bisection on the committed impact surface. Each bracket provably halves every iteration, and uncensored break-even coefficients sit inside the sign-test bracket between the last positive costed Sharpe and the first negative one. A censored book reports a documented reason and never a zero tolerance.

<!-- table:capacity:start -->
| variant | weighting | active_rows | gross_sharpe | break_even_coefficient | break_even_sharpe | censored | censor_reason | bracket_halving_verified |
|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 7.034781 | 0.097478 | -0.000012 | False | None | True |
| planted | rank | 541 | 44.378201 | None | None | True | no_negative_sharpe_at_max_coefficient | False |
| null | equal | 541 | 0.639801 | 0.010507 | 0.000028 | False | None | True |
| null | rank | 541 | 0.649924 | 0.015268 | 0.000003 | False | None | True |
<!-- table:capacity:end -->

## Decision

The chartered acceptance thresholds for this report are restated below from the P22 charter, not retyped. Each one is re-verified against the committed artifacts by the consistency suite.

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| Explicit signal-or-noise verdict | True |
| NO-GO for market | True |
| No harness re-run | True |
| Planted recovery labelled controlled synthetic | True |
| Numbers matched minimum | 100 |
| Unmatched cells maximum | 0 |
| Nominal slack | 0.050000 |
<!-- table:decision:end -->

**Verdict:** the estimator is SIGNAL on the planted controlled-synthetic universe, NOISE on the null universe, and bounded by the measured capacity break-even under nonlinear impact. The verdict is **NO-GO for market deployment** until a maintainer supplies a licensed price series. This is a decision about the estimator's calibration and cost behaviour under controlled conditions, not a decision about a live trading opportunity.

## What this does not prove

- It does not prove a demonstrated profitable strategy: the planted universe is a controlled synthetic stimulus with known ground truth.
- It does not prove that planted recovery is market alpha; it is never market alpha and must never be quoted as such.
- It does not prove that a null-universe positive result is a finding. It would be a bug.
- It does not prove that the capacity break-even transfers to a real order book, since the impact coefficient is a modelled stimulus and not a calibrated market parameter.

## Required next

Campaign P23 "Breadth and instability stress" is the declared successor. It must measure how the estimator behaves as the cross-section widens, as beta estimates drift, and as short availability tightens, and it must close with its own decision report that keeps this NO-GO in force until licensed market data exists. The next session must land the first unrouted P23 work package with its script, artifact and acceptance test in one commit; prose alone is not a session.
