# BAB Fidelity — is the default book actually "Betting Against Beta"?

**Status:** WP1 of campaign P20 landed 2026-11-18 (UTC).
**Applies to:** `strategies/betting_against_beta` default configuration.

This document records the measured gap between the repository's name and its
shipped default, the change that closed it, and the numbers that must hold
afterwards. Every figure below was produced on `tests/fixtures/real_market_prices.csv`
with `transaction_costs=0.001` and `min_observations=60`.

> **Provenance / honesty note.** `tests/fixtures/real_market_prices.csv` is **not
> real market data**. It is a deterministic synthetic random walk built by
> `scripts/generate_real_market_fixture.py` with a fixed seed, plus a deliberate
> 2021-09-17 gap and an all-NaN `DEL` column. Numbers in this document are
> regression targets and fidelity evidence, **not** evidence of real
> profitability or of an investable edge. The in-sample `q=0.2` results below
> must never be reported as out-of-sample performance.

## 1. The defect

Before WP1 the default config set `beta_neutral=False`. The book was
dollar-neutral only (weights summed to zero) with construction equal-weight
±1.0 per leg. On the committed fixture the default book (w=90, q=0.3) carried a
realized beta of **−0.572** — a large *short* benchmark exposure, i.e. the
opposite of the neutrality the strategy claims. At q=0.2 it was **−0.908**.

## 2. The change

Two product hunks, one config default flip and one rebalance-aware hold:

```diff
--- a/strategies/betting_against_beta/config.py
+++ b/strategies/betting_against_beta/config.py
@@
-    beta_neutral: bool = False
+    beta_neutral: bool = True
```

```diff
--- a/strategies/betting_against_beta/strategy.py
+++ b/strategies/betting_against_beta/strategy.py
@@
             enable_tracking_error_monitoring=enable_te,
             correction=correction,
         )
+        if rebalance_freq != "daily" and len(weights) > 0:
+            weights = _apply_rebalance(weights, rebalance_freq)
```

The second hunk appears at **both** correction sites — inside `run()` and inside
`dry_run()` — because `enforce_beta_neutrality` runs per row, every day. Without
the hold, the corrected book drifts inside a weekly/monthly window and the
existing rebalance-invariance tests fail. `_apply_rebalance` reuses the exact
mask/hold already applied to signals (`where(mask).ffill().fillna(0)`), so
`rebalance_freq="daily"` is a provable no-op and daily numbers cannot move.

The legacy dollar-neutral book remains reachable for reproduction and for tests
whose subject is CLI/reporting, via explicit `beta_neutral=False` or
`scripts/load_real_bab_example.py --no-beta-neutral`.

## 3. Before / after (default config)

Fixture: 398 rows, 2021-01-05 → 2022-07-15, `beta_window=90`, q=0.3, 10 bps.

| Config | Wealth | Sharpe | Ann. vol | Max DD | Realized β | Model β (max) | Turnover |
|---|---|---|---|---|---|---|---|
| `beta_neutral=False` (pre-WP1 default) | 0.3136 (−68.6%) | −1.418 | 0.446 | −0.758 | **−0.572** | 1.11 | 0.201 |
| `beta_neutral=True` (post-WP1 default) | 0.7057 (−29.4%) | −0.725 | 0.258 | −0.413 | **+0.059** | 1.5e-04 | 0.264 |
| BTC buy-and-hold (reference) | 2.0975 (+109.7%) | +1.756 | 0.291 | — | 1.000 | — | — |

At q=0.2:

| Config | Wealth | Sharpe | Ann. vol | Max DD | Realized β | Model β (max) | Turnover |
|---|---|---|---|---|---|---|---|
| `beta_neutral=False` | 0.4214 (−57.9%) | −0.680 | 0.567 | −0.634 | **−0.908** | 1.48 | 0.126 |
| `beta_neutral=True` | 1.3093 (+30.9%) | +0.649 | 0.366 | −0.227 | **+0.006** | 2.1e-04 | 0.234 |

`wealth` is a cumulative index with 1.0 at the start; total return is
`wealth − 1`. Beta neutrality removes most of the market-directional P&L; the
remaining performance is still far below buy-and-hold and is **not** an edge
claim. The q=0.2 row is in-sample.

## 4. Daily grid (post-WP1 default)

`model β = max_t |Σ_i w_{t,i} β_{t,i}|`; `realized β` is the OLS beta of the
strategy return series against BTC.

| beta_window | q | Wealth | Sharpe | Realized β | Model β | max\|Σw\| |
|---|---|---|---|---|---|---|
| 60 | 0.2 | 1.3182 | +0.651 | −0.031 | 2.16e-04 | 8e-16 |
| 60 | 0.3 | 0.4387 | −1.905 | **+0.121** | 1.45e-04 | 5e-16 |
| 90 | 0.2 | 1.3093 | +0.649 | +0.006 | 2.13e-04 | 9e-16 |
| 90 | 0.3 | 0.7057 | −0.725 | +0.059 | 1.51e-04 | 5e-16 |
| 120 | 0.2 | 1.3708 | +0.734 | −0.011 | 1.91e-04 | 9e-16 |
| 120 | 0.3 | 1.1130 | +0.389 | +0.028 | 1.38e-04 | 5e-16 |

Acceptance gates asserted by `tests/test_bab_p20_beta_neutral_default.py`:

* `max_t |Σ_i w_{t,i} β_{t,i}| ≤ 1e-3` at every grid point (observed ≤ 2.2e-04);
* `|realized β| ≤ 0.15` grid-wide and `≤ 0.07` for `beta_window ∈ {90, 120}`;
* `|Σ_i w_{t,i}| ≤ 1e-9` on every row (dollar neutrality preserved).

The model-β gate cannot be tightened to 1e-4: the correction stops when the
residual is within its `beta_tolerance=1e-4` default, so residuals up to
~2.2e-04 are expected. The *exact* (`≤ 1e-9`) proof requires
`beta_tolerance=0.0`; see §6.

## 5. Weekly / monthly books are frozen per window

With `rebalance_freq="weekly" | "monthly"` the corrected book is computed on
rebalance dates and then held. Weights on non-rebalance rows are byte-identical
to `weights.where(mask).ffill().fillna(0)` (`mask = _rebalance_mask(index, freq)`),
and the beta-neutral residual is at its tolerance floor **on rebalance rows**.

| freq | Wealth | Sharpe | Ann. vol | Max DD | Realized β | Model β @ rebalance rows | Book β drift inside window (max) | Turnover |
|---|---|---|---|---|---|---|---|---|
| weekly | 0.8049 | −0.447 | 0.242 | −0.375 | +0.049 | 1.47e-04 | 0.094 | 0.131 |
| monthly | 1.1492 | +0.496 | 0.231 | −0.233 | +0.083 | 1.26e-04 | 0.121 | 0.045 |

Inside a window the *frozen* book's model beta rises because asset betas drift
while the weights are held. That is the intended behaviour of a discrete
rebalance policy, not a fidelity defect: the invariant is enforced at each
rebalance date, and the drift is bounded by the betas' own variation over one
week/month.

## 6. Why realized β ≠ model β (estimation error)

The model beta is exact by construction: `Σ w·β` uses the *estimated* betas that
the correction consumed. Realized beta is computed ex post from the strategy's
own realized return series, so it inherits beta-estimation error: when a
rolling beta is stale or noisy, the corrected model book is neutral with respect
to the *estimated* betas while the *true* betas differ.

That is why the worst grid cell (`beta_window=60`, q=0.3) shows realized
`+0.121` while its model beta is `1.45e-04`. Longer windows reduce the error:
at `beta_window ∈ {90, 120}` the observed realized beta is ≤ 0.059, hence the
`≤ 0.07` gate for that subset and the looser `≤ 0.15` grid-wide gate.

A note on exactness: on a synthetic frame with hand-assigned betas
`{0.5, 0.8, 1.2, 1.6}` (returns constructed as exact multiples of the
benchmark), rolling betas reproduce those values to ~1e-16 and the corrected
book reaches `max|Σ w·β| = 2.8e-17` with `beta_tolerance=0.0`. With the default
tolerance the same frame lands at `≤ 1e-3` (observed 9.8e-06). Both are asserted
in the test file, which documents that the residual is tolerance-driven, not a
construction flaw.

## 7. What this does NOT prove

* No evidence of real profitability: the fixture is synthetic (§ provenance).
* No out-of-sample validity: nothing here is a walk-forward test. WP3 exists to
  build that harness, and a null or negative OOS result is a valid outcome.
* No claim that equal-weight construction is the only faithful construction:
  WP2 landed an opt-in ``weighting="rank"`` path (Frazzini-Pedersen rank
  weighting with per-leg beta scaling, see §9), while ``weighting="equal"``
  remains the shipped default. Rank is not promoted to the default without WP3
  out-of-sample evidence.
* No claim about live execution, capacity, or cost realism (P21).

## 8. Reproduce

```bash
bash scripts/bab_quick.sh
python3 -m pytest -q tests/test_bab_p20_beta_neutral_default.py
```

```bash
python3 - <<'EOF'
from strategies.betting_against_beta.data_loader import load_prices
from strategies.betting_against_beta import BABStrategy, metrics

r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
for q in (0.2, 0.3):
    for bn in (False, True):
        o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                        long_quantile=q, short_quantile=q,
                        transaction_costs=0.001, beta_neutral=bn).run(returns_df=r)
        rets = o.backtest["returns"]
        print(q, bn, round(float(o.backtest["cumulative"].iloc[-1]), 4),
              round(float(metrics.sharpe_ratio(rets)), 3),
              round(float(metrics.strategy_beta(rets, r["BTC"])), 3))
EOF
```

## 9. Rank weighting (opt-in, WP2)

WP2 adds a faithful Frazzini-Pedersen rank weighting construction as an opt-in
``weighting="rank"`` path. The default remains ``weighting="equal"``; rank is
not promoted to the default (promotion requires WP3 out-of-sample evidence).

### Construction

For each row ``t``:

1. Eligible assets = selected by signal (``+1`` long / ``-1`` short) and beta
   finite and ``> 0``.
2. Fewer than 1 eligible long or fewer than 1 eligible short -> all-zero row.
3. Rank eligible betas ascending (``pandas.rank(method="average")``); ``m`` =
   mean(rank) over all eligible assets (longs and shorts together).
4. Long score ``a_i = m - rank_i``; short score ``a_j = rank_j - m``.
5. Dollar-normalize each leg: ``d_i = a_i / sum_L a``,
   ``e_j = a_j / sum_H a``. Degenerate zero-sum leg -> flat row.
6. Leg betas ``beta_L = sum_L d_i b_i``, ``beta_H = sum_H e_j b_j``; non-finite
   or ``<= 0`` -> flat row.
7. ``w_i = d_i / beta_L`` (long), ``w_j = -e_j / beta_H`` (short). No beta
   correction afterwards: the book is beta-neutral by construction.

### Hand-computed 4-asset example

Signals ``A,B = +1`` (long), ``C,D = -1`` (short); betas ``A=0.5, B=0.8,
C=1.2, D=1.6``. Ranks ``[1, 2, 3, 4]``, ``m = 2.5``.

| asset | weight (exact) | decimal |
|---|---|---|
| A | 30/23 | 1.3043478260869565 |
| B | 10/23 | 0.4347826086956522 |
| C | -1/6 | -0.16666666666666666 |
| D | -1/2 | -0.5 |

Leg betas: long ``+1``, short ``-1``, total model beta ``0`` (on the row where
weights are formed). Net dollar exposure ``74/69 ≈ 1.07246`` (= ``1/beta_L -
1/beta_H``), not zero: FP's factor is beta-neutral, not dollar-neutral, and the
net is funded by cash/borrow.

### Contract

* ``weighting="equal"`` is byte-identical to the post-WP1 default.
* Rank weights skip ``enforce_beta_neutrality`` (the min-norm correction can
  flip long/short signs); rank is beta-neutral by construction.
* Weekly/monthly books are frozen inside rebalance windows (WP1 hold).
* Rank is opt-in and is NOT the default; promotion requires WP3 OOS evidence.
```
