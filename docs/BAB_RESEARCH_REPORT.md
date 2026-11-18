# BAB Research Report — does this repository implement Betting Against Beta?

This report publishes the P20 evidence that the `Crypto-Betting-Against-Beta`
repository implements a **Betting Against Beta** construction rather than a
generic dollar-neutral long/short book. It is deliberately modest: the fixture
is synthetic, and nothing here is a claim of real-world profit.

Every number in every table below is generated from the committed artifacts
`research_state/bab_p20/sweep.json`, `research_state/bab_p20/walk_forward.json`
and `research_state/bab_p20/breakeven.json`. No harness is re-run to produce a
reported number, and `tests/test_bab_p20_report_consistency.py` fails if a
single published cell drifts from its JSON field. All published results use
`weighting="equal"`; rank weighting is out of scope (§9.1 below).

## Provenance

The evidence comes from one committed fixture. It is a **deterministic
synthetic random walk generated with a fixed seed — not real market data**.
Its returns are a controlled test bed, not a market observation, and no result
in this report is evidence of real-world profitability.

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Fixture path | `tests/fixtures/real_market_prices.csv` |
| Fixture sha256 | `bcf47693858108319c38ccbc02e9ebdb8ade7d4613acb031306d9d6827bd35e2` |
| Price rows | 399 |
| Return rows | 398 |
| First date | 2021-01-04 |
| Last date | 2022-07-15 |
| Seed | 20261028 |
| Known gap | 2021-09-17 |
| All-NaN columns | DEL |
| Synthetic | True |
<!-- table:provenance:end -->

The fixture contains `DEL`, a column that is all-NaN, and a deliberate missing
date (`2021-09-17`) that exercises gap handling. `price_rows` count prices and
`return_rows` count the differenced returns the strategy trades on. Because the
random walk is seeded, rerunning any P20 harness reproduces these artifacts
byte for byte.

## What the construction claims

The default strategy is beta-neutral BAB with equal weights:

- Estimate each asset beta against the BTC benchmark over a rolling window
  (`beta_window` from the committed grid) with a minimum observation count.
- Go long the low-beta names and short the high-beta names at the configured
  quantiles, holding the book for the rebalance window rather than refitting
  weights inside it.
- Scale the two legs so that the target `max|Σ wᵢβᵢ|` is approximately zero —
  the book beta the model targets, not the realized beta of the backtest.

Beta neutrality is therefore a construction property, and the tables below
check it both at the model level (`model_beta`) and at the realized level
(`realized_beta`, an OLS beta of backtest returns against BTC).

## In-sample grid (WP0)

`sweep.json` publishes the full committed grid of `80` configurations across
`beta_window`, quantile, `beta_neutral` and `transaction_costs`. The grid
**selects no winner**: it is a descriptive map of the parameter surface on one
synthetic fixture, not a tuning result. The shipped default (`w90 q0.3`, ten
basis points, `beta_neutral=True`) is **negative** on this fixture.

The equal-weight beta-neutral rows at ten basis points are:

<!-- table:in_sample:start -->
| beta_window | long_quantile | short_quantile | transaction_costs | sharpe | wealth | realized_beta | model_beta | turnover | gross |
|---|---|---|---|---|---|---|---|---|---|
| 30 | 0.200000 | 0.200000 | 0.001000 | 0.012234 | 0.903133 | -0.144460 | 0.000258 | 0.624799 | 2.732046 |
| 30 | 0.300000 | 0.300000 | 0.001000 | -0.713203 | 0.745473 | 0.040532 | 0.015008 | 0.525495 | 1.678279 |
| 60 | 0.200000 | 0.200000 | 0.001000 | 0.650741 | 1.318234 | -0.030995 | 0.000216 | 0.275765 | 2.442164 |
| 60 | 0.300000 | 0.300000 | 0.001000 | -1.905196 | 0.438710 | 0.120887 | 0.000145 | 0.362747 | 1.683033 |
| 90 | 0.200000 | 0.200000 | 0.001000 | 0.648501 | 1.309312 | 0.005644 | 0.000213 | 0.233905 | 2.222731 |
| 90 | 0.300000 | 0.300000 | 0.001000 | -0.725483 | 0.705655 | 0.058754 | 0.000151 | 0.264446 | 1.618354 |
| 120 | 0.200000 | 0.200000 | 0.001000 | 0.734153 | 1.370829 | -0.011390 | 0.000191 | 0.205068 | 2.073130 |
| 120 | 0.300000 | 0.300000 | 0.001000 | 0.389345 | 1.113042 | 0.028206 | 0.000138 | 0.164883 | 1.613669 |
| 180 | 0.200000 | 0.200000 | 0.001000 | 1.138293 | 1.703559 | -0.009401 | 0.000175 | 0.107871 | 1.805332 |
| 180 | 0.300000 | 0.300000 | 0.001000 | 0.037148 | 0.954513 | 0.078866 | 0.000148 | 0.123168 | 1.623082 |
<!-- table:in_sample:end -->

The contrast that motivates the campaign is the default configuration with and
without the beta-neutral scaling:

<!-- table:contrast:start -->
| beta_neutral | model_beta | realized_beta | sharpe | wealth | gross |
|---|---|---|---|---|---|
| False | 1.110774 | -0.571570 | -1.418444 | 0.313575 | 2.000000 |
| True | 0.000151 | 0.058754 | -0.725483 | 0.705655 | 1.618354 |
<!-- table:contrast:end -->

Without the scaling the model beta is large and the realized beta is strongly
negative; with the scaling the model beta collapses toward zero, at the cost of
a different and still-unprofitable path. This is the construction doing its
job, not a profitable strategy.

## Out-of-sample walk-forward (WP3)

`walk_forward.json` evaluates expanding, train-before-test folds: each fold
scores the candidate grid on history only, picks a configuration by train-slice
Sharpe with a deterministic tie-break, and then scores that single choice on
the untouched test slice. The test window is never read during selection, and
weights at any row depend only on data through the prior day.

<!-- table:folds:start -->
| fold | n_train | n_test | selected_beta_window | selected_long_quantile | selected_short_quantile | train_sharpe | oos_sharpe | oos_wealth | oos_realized_beta | oos_turnover | oos_max_drawdown | oos_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 180 | 40 | 120 | 0.300000 | 0.300000 | 0.137859 | 2.472329 | 1.106561 | 0.205791 | 0.231497 | -0.051678 | 0.273110 |
| 1 | 220 | 40 | 120 | 0.300000 | 0.300000 | 0.605202 | 1.970121 | 1.092198 | -0.125316 | 0.097940 | -0.084725 | 0.305466 |
| 2 | 260 | 40 | 120 | 0.300000 | 0.300000 | 0.853681 | -0.697087 | 0.965926 | -0.141410 | 0.063214 | -0.079774 | 0.264370 |
| 3 | 300 | 40 | 120 | 0.200000 | 0.200000 | 1.011363 | 3.978038 | 1.244365 | -0.107956 | 0.080668 | -0.071644 | 0.363221 |
| 4 | 340 | 40 | 120 | 0.200000 | 0.200000 | 1.363170 | -1.195588 | 0.919310 | -0.536502 | 0.401281 | -0.147766 | 0.382662 |
<!-- table:folds:end -->

<!-- table:aggregate:start -->
| Metric | Value |
|---|---|
| candidates_evaluated | 40 |
| total_oos_rows | 200 |
| mean_oos_sharpe | 1.305563 |
| median_oos_sharpe | 1.970121 |
| fraction_positive_oos_sharpe | 0.600000 |
<!-- table:aggregate:end -->

The mean OOS Sharpe is positive, but the dispersion across folds is extreme and
the sign flips repeatedly. Three of five folds are positive while two are
sharply negative, and the strongest fold is the smallest sample. That is **not
a demonstrated profitable strategy**; it is the signature of a synthetic random
walk plus selection noise. The honest OOS verdict is the one the aggregate
table shows, with no post-hoc trimming.

## Costs and break-even (WP5)

`breakeven.json` locates the transaction cost at which each equal-weight
beta-neutral configuration's Sharpe crosses zero, using a fixed 6-iteration
bisection over `tc` in `[0, 0.01]`. The bisection always performs exactly six
evaluations; there is no early exit and no caller-supplied bracket.

<!-- table:breakeven:start -->
| beta_window | long_quantile | uncosted_sharpe | break_even_tc | sharpe_at_break_even | turnover_at_break_even | gross_at_break_even |
|---|---|---|---|---|---|---|
| 30 | 0.200000 | 0.435796 | 0.001016 | 0.005617 | 0.624799 | 2.732046 |
| 30 | 0.300000 | -0.124867 | None | None | None | None |
| 60 | 0.200000 | 0.834694 | 0.004609 | -0.012656 | 0.275765 | 2.442164 |
| 60 | 0.300000 | -1.555531 | None | None | None | None |
| 90 | 0.200000 | 0.810267 | 0.005078 | -0.008667 | 0.233905 | 2.222731 |
| 90 | 0.300000 | -0.467052 | None | None | None | None |
| 120 | 0.200000 | 0.878289 | 0.006172 | -0.007735 | 0.205068 | 2.073130 |
| 120 | 0.300000 | 0.546804 | 0.003516 | -0.007858 | 0.164883 | 1.613669 |
| 180 | 0.200000 | 1.216780 | None | None | None | None |
| 180 | 0.300000 | 0.146479 | 0.001328 | 0.001227 | 0.123168 | 1.623082 |
<!-- table:breakeven:end -->

A `None` never means the break-even cost is zero. It means no crossing exists
in the tested range, for one of two documented reasons. The three configurations with
non-positive uncosted Sharpe have no positive cost tolerance at all. One
configuration (`w180 q0.2`) is censored: its costed Sharpe is still positive at
the upper bound of the tested range, so its crossing lies beyond the search
window and is left unstated rather than fabricated.

<!-- table:null_rows:start -->
| Configuration | Empty fields | Documented reason |
|---|---|---|
| w30 q0.3 | break_even_tc, sharpe_at_break_even, turnover_at_break_even, gross_at_break_even | uncosted Sharpe is non-positive: the strategy loses money before costs, so no positive cost tolerance exists |
| w60 q0.3 | break_even_tc, sharpe_at_break_even, turnover_at_break_even, gross_at_break_even | uncosted Sharpe is non-positive: the strategy loses money before costs, so no positive cost tolerance exists |
| w90 q0.3 | break_even_tc, sharpe_at_break_even, turnover_at_break_even, gross_at_break_even | uncosted Sharpe is non-positive: the strategy loses money before costs, so no positive cost tolerance exists |
| w180 q0.2 | break_even_tc, sharpe_at_break_even, turnover_at_break_even, gross_at_break_even | costed Sharpe stays positive through the upper search bound, so the zero crossing lies beyond the tested cost range |
<!-- table:null_rows:end -->

For the configurations with a defined crossing, a tighter (lower) break-even
cost is not the same as a better strategy: turnover differs across
configurations, so cost drag differs too. The per-row law the harness proves is
simpler and load-bearing — for a fixed configuration the costed Sharpe is
non-increasing in `tc`, which makes the crossing unique inside the bracket.

## Conclusion

The repository **does implement the BAB construction**: the default and
beta-neutral rows are near-zero in model beta by construction, the realized
beta is small on the fixture, and the equal-weight path is reproducible. The
repository has **no demonstrated real-world profitability**. The in-sample grid
selects no winner, the walk-forward spread does not separate signal from noise,
and the cost analysis shows that even the in-sample Sharpe on this synthetic
fixture is fragile. The OOS result is the honest verdict.

## What this does NOT prove

- Nothing about real crypto markets. The fixture is a **deterministic synthetic
  random walk**, not real market data.
- Nothing about a broad universe. The fixture has nine assets, one benchmark,
  and a single time range.
- Nothing about live execution, slippage beyond the single linear cost model,
  borrowing costs, funding, or capacity.
- Nothing about rank weighting. It is not evaluated here at all.
- No positive claim about any parameter set, including the shipped default.

## Rank discipline (§9.1)

Per section `§9.1` of `docs/BAB_FIDELITY.md`, rank weighting is **not
empirically evaluable** on this fixture: the leg-beta floor and gross cap
flatten the book on this nine-asset universe, so rank mode produces no active
rows and no meaningful performance. Accordingly no rank Sharpe, rank wealth, or
rank row is published in this report, and none may be quoted from this fixture
as a result. The rank construction is verified algebraically in its own test
file, not here.

## Reproducing the check

```
python3 -m pytest -q tests/test_bab_p20_report_consistency.py
```

The suite parses every table above, requires that every numeric cell matches a
field in the committed JSON at six decimal places, requires that each table is
byte-identical to the same JSON renderer, and fails on any stray prose number,
any rank performance claim, or any null break-even rendered as a value.
