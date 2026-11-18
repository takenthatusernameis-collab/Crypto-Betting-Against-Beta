# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T20:24:09Z
- **Git state:** `main`, clean tree. Head is the commit that carries this file; its parent is `a32a91d`. Certify with `git log --oneline -4 && git status --short`. **P20 WP1 is LANDED at `33b84e2`** (beta-neutral default + frozen-per-window hold + `tests/test_bab_p20_beta_neutral_default.py` + `docs/BAB_FIDELITY.md` + README correction + CLI `--no-beta-neutral`). **P20 WP2 is LANDED at `01eb301`** (opt-in `weighting="rank"` in `config.py` + `portfolio.py` + `strategy.py`, 8 tests, `docs/BAB_FIDELITY.md` §9, README clause).
- **This session repaired WP2's red gate and re-scoped it.** WP2 landed with (a) one failing test — `TestFreezeFallback` builds `MagicMock(spec=BABConfig)` and never set the new `weighting` field, so a mock object reached `construct_portfolio` — and (b) 6 uncovered statements. Repaired: pinned `cfg.weighting = "equal"` in that mock; proved the two rank leg-sum guards are **identically equal** (`Σ_L(m−r) == Σ_H(r−m)` because eligible ranks sum to `n·m`) and collapsed them to one live guard (dead code removed, `portfolio.py` 6625 → 6623 statements); added 3 tests for rank input guards, non-numeric signal coercion, the degenerate-leg flat row, and `dry_run` rank freeze. Full gate is GREEN again at **6473 passed / 35 skipped / TOTAL 100% (6623/6623)**.
- **WP2 is algebraically correct but numerically unusable on the committed fixture** — this is the next task, not a re-open of the algebra. Measured at `beta_window=90, q=0.3, tc=10bps`: only **25 of 398 rows** have both an eligible long and an eligible short leg; on all 25, `β_L ∈ [0.0197, 0.1138]` and `β_H = 1.0`, so leg-level `1/β` scaling produces **gross 9.79 → 51.67**; the 2021-05-03 row is `ADA +50.09 / BTC −1.00` (gross 51.09) and the next day's return is **−1.968**, collapsing wealth to ~`1.5e-24`. Rank Sharpe/wealth on this fixture is meaningless. Default `weighting="equal"` is untouched and still `0.7057 / −0.725 / realized β +0.059`.
- **Baseline locks at HEAD (do not re-measure):** `beta_neutral: bool = True` (`config.py:99`); `weighting: str = "equal"` (`config.py:54`) with validation at `config.py:381-382`; `_apply_rebalance(weights, rebalance_freq)` hold at both correction sites and both rank-freeze sites (`strategy.py:518-519`, `822-823`, `847-851`); `construct_rank_weights` public at `portfolio.py:260`; `docs/BAB_FIDELITY.md` §9 and `tests/test_bab_p20_rank_weighting.py` exist. **WP1 is closed. WP2's algebra is closed — never re-derive it.**
- **P20 remaining:** **WP2b (next, lane B)**, then WP0, WP3, WP5 (lane A), then WP4 (lane C).
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 CLOSED.** Coverage complete, handlers annotated, scratch scripts removed. Never reopen.

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T20:24:09Z · **Campaign:** P20 — "Make the repo actually Betting Against Beta" · **Lane:** B · **WP:** **WP2b — rank-book leverage bound + honest scope**

**One-sentence objective:** make the opt-in rank path numerically safe by flattening rows whose leg beta is below a floor or whose gross exceeds a cap (never rescaling — that breaks unit leg betas), prove the 4-asset algebra is unchanged, prove rank works on a wide synthetic cross-section, and document with the measured numbers that the 9-asset committed fixture **cannot evaluate rank mode**.

**Why this and nothing else:** WP2 shipped `w = d/β_L` with no lower bound on `β_leg`. On the committed 9-asset universe the low-beta quantile is routinely negative-beta, those assets are ineligible under the documented `beta > 0` rule, and the remaining eligible long leg is a single near-zero-beta asset (`β_L` as low as `0.0197`). Inverting that gives a **51x gross** book and a −196.8% day. A repo named `Crypto-Betting-Against-Beta` must not ship a BAB construction that silently 51x-levers. Fixing this is the only blocker between P20 and honest OOS work; WP0/WP3/WP4 are meaningless if the fidelity path can detonate.

**The design is specified and the numbers are measured below. You are NOT being asked to invent the construction or relax the algebra.**

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It also bootstraps numpy/pandas/scipy/pytest/ruff from PyPI; on a fresh runner raw `python3` snippets fail with `ModuleNotFoundError: numpy` until this has run once. Console scripts land in `~/.local/bin` (not on `PATH`) — always `python3 -m pytest`, `python3 -m ruff`.
3. Confirm the pathology yourself before changing anything (≈2 s):
   ```bash
   python3 - <<'EOF'
   import numpy as np
   from strategies.betting_against_beta.data_loader import load_prices
   from strategies.betting_against_beta import BABStrategy
   r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
   o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                   long_quantile=0.3, short_quantile=0.3,
                   transaction_costs=0.001, weighting="rank").run(returns_df=r)
   W = o.weights
   print("active rows:", int((W.abs().sum(axis=1) > 0).sum()), "/", len(W))
   print("max gross:", float(W.abs().sum(axis=1).max()))
   print("min daily return:", float(o.backtest["returns"].min()))
   EOF
   ```
   Expected: `25 / 398`, `~51.09`, `~ -1.968`. If those numbers differ by more than rounding, STOP and re-measure before applying the guard.
4. Read `docs/BAB_FIDELITY.md` §9 (construction + hand example) and §9.1 (this finding). Do not edit §9's formulas.

---

## WP2b — design (apply exactly)

### A. `config.py`
Add next to `weighting` (line ~54):

```python
    # Rank-mode safety valves (no effect on the "equal" default):
    # flat-row when a leg beta is too small to invert, or when gross > cap.
    rank_min_leg_beta: float = 0.20
    rank_max_gross: float = 4.0
```

Validation in `_validate_ranges`, next to the `weighting` check:
- `rank_min_leg_beta` must be a real number with `0 < value <= 1`;
- `rank_max_gross` must be a real number with `1 <= value <= 100`;
- else append to `errors` so construction raises `BABConfigError`. No silent coercion, no clamping.

### B. `portfolio.py`
Extend the signature: `construct_rank_weights(signals_df, betas, min_leg_beta=0.20, max_gross=4.0)`.
After computing `beta_L`, `beta_H` and the candidate row (`w_i = d_i/β_L`, `w_j = −e_j/β_H`):

1. if `beta_L < min_leg_beta` **or** `beta_H < min_leg_beta` → **flat row** (all zeros), continue;
2. else if `Σ|w| > max_gross` → **flat row**, continue;
3. else keep the row unchanged.

Rules: never raise on a pathological row, never rescale a row to the cap (rescaling changes leg betas away from `±1` and silently breaks the documented gate), never add beta correction, never change the equal branch. Extend `construct_portfolio(..., weighting="rank", ...)` to forward `rank_min_leg_beta` / `rank_max_gross` (read via kwargs or explicit params, but `weighting="equal"` must stay byte-identical and must ignore them). Invalid values passed directly to `construct_portfolio` still raise `BABDataError` (consistent with `weighting`).

### C. `strategy.py`
Pass `cfg.rank_min_leg_beta` / `cfg.rank_max_gross` into both `construct_portfolio` calls (`run()` ~line 415, `dry_run()` ~line 754). Leave both rank freeze blocks (`~531`, `~847`) and the equal-path `enforce_beta_neutrality` block untouched. `getattr(cfg, ..., default)` so duck-typed/mock configs without the new fields keep the defaults.

**Explicitly out of scope:** widening eligibility to negative betas, changing rank scores, changing quantiles, promoting rank to default.

### D. Feasibility facts you may rely on (measured, do not re-derive)
- Hand example: `β_L = 23/40 = 0.575`, `β_H = 3/2 = 1.5`; long dollars `30/23 + 10/23 = 40/23 ≈ 1.7391`, short dollars `1/6 + 1/2 = 2/3 ≈ 0.6667`, gross **≈ 2.4058**. With `min_leg_beta=0.20` and `max_gross=4.0` the hand row is **not** flattened and all four exact fractions must stay unchanged to `1e-12`.
- Committed fixture: every one of the 25 fixture-active rows has `β_L < 0.20`, so under the guard **all 398 rows are flat**. The two fixture-based invariant tests must therefore move to a wide synthetic frame.
- Wide synthetic frame for the functional proof: 40 assets, betas spread over `0.35 … 1.9` (e.g. `0.35 + 1.55*i/39`), 60 daily rows, deterministic signals (`+1` for the lowest 30%, `-1` for the highest 30%). With such a cross-section `β_L ≈ 0.45`, `β_H ≈ 1.75`, gross ≈ `3.0` → active, under the cap.

### E. Tests — `tests/test_bab_p20_rank_weighting.py` (extend; baseline is 11 tests in this file)
1. **Keep** `test_hand_computed_four_asset_rank_weights` asserting `30/23, 10/23, −1/6, −1/2`, legs `±1`, total β `0`, net dollars `74/69` to `1e-12` — the floor/cap must not bind.
2. **Add** `test_rank_flat_when_leg_beta_below_floor`: single long asset with `β=0.05`, valid short leg → all-zero row; same frame with `min_leg_beta=0.01` → non-zero, legs `±1`.
3. **Add** `test_rank_flat_when_gross_exceeds_cap`: construct a case whose natural gross is ~9–10 (e.g. long leg `β_L=0.10`, short `β_H=2.0`) → zero row at `max_gross=4.0`; identical frame with `max_gross=12.0` → non-zero, legs `±1`, gross ≤ 12.
4. **Re-point** `test_rank_book_is_beta_neutral_on_rebalance_rows` and `test_rank_beats_equal_on_leg_beta_scaling` to the wide synthetic universe (weekly + monthly). They must keep the same assertions: model β `≤1e-12` on rebalance rows, exact frozen-hold identity off them, rank legs `±1` on active rebalance rows, equal legs not `±1`. Document in the docstring that the committed fixture cannot support rank (see §9.1) so the invariant is proved on a cross-section with rank dispersion. This is **authorized re-pointing, not loosening** — no assertion may be weakened or deleted.
5. **Add** `test_fixture_rank_is_flat_under_guard`: rank `run()` on the committed fixture, daily/weekly/monthly → `weights.abs().to_numpy().sum() == 0.0`, `cumulative.iloc[-1] == 1.0`, returns all zero (or NaN Sharpe), never raises.
6. **Add** `test_rank_guard_config_validation`: `BABConfig(rank_min_leg_beta=0)` / `1.5` / `"x"` and `BABConfig(rank_max_gross=0.5)` / `1000` raise `BABConfigError`; a direct `construct_portfolio(weighting="rank", rank_min_leg_beta=0, ...)` raises `BABDataError`.
7. **No** existing test deleted, skipped, `xfail`-ed, or weakened. Baseline **6473 passed / 35 skipped / TOTAL 100% (6623/6623)** may only grow.

### F. Docs
- `docs/BAB_FIDELITY.md`: keep §9 formulas; append **§9.1 Rank-mode leverage bound and scope (WP2b)** with: the measured 25/398 active-row count, `β_L ∈ [0.0197, 0.1138]`, `β_H = 1.0`, gross `9.79 → 51.67`, the 2021-05-03 `ADA +50.09 / BTC −1.00` row and the −196.8% next-day return; the two safety valves and the flat-row contract; the statement that the 9-asset synthetic fixture **cannot evaluate rank mode** and no rank Sharpe/wealth may be published; and that rank remains opt-in and unpromoted.
- `README.md`: one clause that rank weighting requires a wide beta cross-section and is not empirically evaluable on the committed 9-asset fixture. No profitability claim, no "default" claim.

### G. Commit rule
**One commit:** `config.py` + `portfolio.py` + `strategy.py` + `tests/test_bab_p20_rank_weighting.py` + `docs/BAB_FIDELITY.md` (+ optional one-line README). A docs-only / test-only / gate-only commit is an automatic failed session. Never hand off mid-gate and never leave the tree red.

---

## Ground truth @ HEAD (certified; fixture is a deterministic synthetic random walk)

`tests/fixtures/real_market_prices.csv`: 398 rows, 2021-01-05 → 2022-07-15, costs 10 bps, `beta_window=90`, `min_observations=60`, 9 assets (BTC benchmark). **Not real market data.**

| Config | Wealth | Sharpe | Realized β | Max model β | Notes |
|---|---|---|---|---|---|
| **DEFAULT** w90 q0.3 (`beta_neutral=True`, daily) | 0.7057 (−29.4%) | −0.725 | +0.059 | 1.5e-04 | shipped default |
| w90 q0.2, post-WP1 | 1.3093 (+30.9%) | +0.649 | +0.006 | 2.1e-04 | in-sample only |
| w90 q0.3 weekly, equal | 0.8049 | −0.447 | +0.049 | 9.4e-02 | held-row drift |
| w90 q0.3 monthly, equal | 1.1492 | +0.496 | +0.083 | 1.2e-01 | held-row drift |
| w90 q0.3, opt-out (`beta_neutral=False`) | 0.3136 (−68.6%) | −1.418 | −0.572 | 1.11 | pre-WP1 behaviour |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 1.000 | — | benchmark |
| **rank** w90 q0.3, daily | ~1.5e-24 | not meaningful | +0.157 | 1.1e-16 | 25 active rows, gross ≤ 51.67 |
| **rank** w90 q0.3, weekly | ~0 | not meaningful | +0.064 | 2.02 | frozen 51x book |
| **rank** w90 q0.3, monthly | ~0 | not meaningful | +0.459 | 4.54 | frozen 51x book |

Reproduce the equal-weight core (≈3 ms **after** `bash scripts/bab_quick.sh`):
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

Model beta and book weights live on `BABResult.weights` / `BABResult.betas` (NOT in `result.backtest`). Model beta = `(W * betas.reindex(columns=W.columns).fillna(0.0)).sum(axis=1)`. `backtest["cumulative"]` is a **wealth index** (1.0 = start); `final − 1` is total return. `backtest` keys: `cost_drag, cumulative, gross_return, returns, slippage_drag`.

**Honesty constraints (non-negotiable):**
1. Never present fixture results as real profitability. It is a fixed-seed random walk with a deliberate 2021-09-17 gap and an all-NaN `DEL` column.
2. The q0.2 row is **in-sample**. Never report in-sample selection as OOS — WP3 exists to prevent that.
3. **Rank-mode wealth/Sharpe on this fixture is evidence of a leverage pathology, nothing else.** Never quote it as performance.
4. A null/negative OOS result is a valid, successful outcome. A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff`. `https://api.exchange.coinbase.com` → **HTTP 403**; real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests.
- Console scripts land in `~/.local/bin` → always `python3 -m pytest` / `python3 -m ruff`.
- `rg` not installed → use `grep -rn` or editor search.
- `bash scripts/bab_quick.sh` ≈ 20 s (ruff + 104 + 195). Full gate ≈ 130 s with `BAB_GATE_MIN_COVERAGE=100`. Fixture pipeline ≈ 3 ms. Verification is never the bottleneck.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.

---

## Campaign P20 map — lanes, status, file ownership

One session owns exactly one lane for its whole turn. Two sessions must never take the same WP; **the committed deliverable files are the claim**.

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **B — Strategy fidelity** | **WP2b (now)** | `config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` | WP1 ✅, WP2 algebra ✅, WP2b ⬅ |
| **A — Research/evaluation** | WP0 → WP3 → WP5 | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` | not started |
| **C — Reporting/consistency** | WP4 after WP0+WP3+WP2b | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` | not started |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`. **Solo default: WP2b. If two sessions run concurrently: one takes WP2b (lane B), one takes WP0 (lane A).**

### WP0 — Evidence harness (lane A, can run concurrently)
`scripts/bab_research_sweep.py`: deterministic sweep over `beta_window ∈ {30,60,90,120,180}`, `q ∈ {0.2,0.3}`, `tc ∈ {0,0.001,0.0025,0.005}`, `beta_neutral ∈ {False,True}` → `research_state/bab_p20/sweep.json` + a markdown table rendered **from** that JSON. Sorted keys, floats at 6 dp, byte-identical reruns, no network. **Use `weighting="equal"` only — do not add rank to the sweep (it is flat on this fixture; see §9.1).** **Acceptance:** `tests/test_bab_p20_research_sweep.py` proves runtime <10 s, identical SHA-256 across runs, every row carries `wealth/sharpe/model_beta/realized_beta/gross/turnover`, and no hand-typed digits in the markdown. `beta_window=180` is descriptive/in-sample only.

### WP3 — Walk-forward / OOS harness (the anti-cherry-pick gate)
`scripts/bab_walk_forward.py`: rolling-origin splits, **5 folds**, parameter selection **only** on train, evaluation **only** on untouched test → `research_state/bab_p20/walk_forward.json` (per-fold selected params, OOS Sharpe/vol/mdd/turnover/beta; aggregate mean/median and fraction of folds with positive Sharpe) + rendered markdown. Feasible split on the 398-row fixture: `train=180` rows, then `5 × 40` test rows (ends at row 380), `beta_window ∈ {30,60,90,120}`, `min_observations=60`, `weighting="equal"`. **Do not use `beta_window=180` in WP3.** **Acceptance:** `tests/test_bab_p20_walk_forward.py` proves `max(train_index) < min(test_index)` for every fold; a planted `t+1` lookahead trap is detected and rejected; deterministic rerun hash equality; ≥40 test observations per fold.

### WP5 — Cost/turnover realism and break-even
Extend the sweep with the cost level at which OOS Sharpe crosses zero (bisection over `tc ∈ [0, 0.01]`, 6 iterations, deterministic), turnover per rebalance, gross exposure → `research_state/bab_p20/breakeven.json`. **Acceptance:** break-even cost monotone non-increasing in reported Sharpe, deterministic, and `tc=0` reproduces uncosted Sharpe within `1e-12`.

### WP4 — Honest reporting + provenance (merge point)
`docs/BAB_RESEARCH_REPORT.md` states fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions, explicit conclusion, a "What this does NOT prove" section, and the §9.1 statement that rank mode is **not empirically evaluable** on this universe (no rank performance numbers may appear as results). **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals its JSON field; asserts the provenance sentence is present. Do **not** rename fixture files.

---

## Campaign P20 done-check (all must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, 6 grid points), `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance, explicit opt-out byte-identical. **DONE (WP1).**
2. `weighting="rank"` exists, is opt-in, matches the hand weights to `1e-12`, unit-beta legs, zero total beta on rebalance rows, equal path byte-identical, no-lookahead proof. **DONE (WP2 algebra).**
3. Rank path is **numerically bounded**: leg-beta floor + gross cap flatten pathological rows, hand example unchanged, wide-universe proof, fixture-flat documented. **WP2b.**
4. `scripts/bab_research_sweep.py` + `scripts/bab_walk_forward.py` exist, deterministic (hash-equal reruns), JSON artifacts committed under `research_state/bab_p20/`. **WP0/WP3.**
5. `docs/BAB_RESEARCH_REPORT.md` exists; every published number machine-checked against JSON; no rank performance claim. **WP4.**
6. All `tests/test_bab_p20_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6473/35 may only grow). **WP2b re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **WP2b re-certifies.**
8. README no longer claims "dollar-neutral by default" as if that were BAB; it cites the fidelity doc. **DONE (WP1/WP2).**

## P21 preview (deferred — activate only after all P20 checks pass)
**P21 — "Execution-grade BAB":** (1) real-data adapter for a maintainer-supplied licensed CSV, no network in-session, `research_state/p21/real_data_provenance.json`, rerun WP3/WP5 unchanged — if no CSV exists, deliver a validated import contract + clearly-labelled synthetic fallback, never a profitability claim; (2) capacity/liquidity model — per-asset ADV participation caps + square-root impact wired into `cost_model`, tests proving size scaling and rejection above caps; (3) execution realism — deterministic paper-trading soak over ≥250 rebalances with replay, reconciliation, restart/resume, modeled-vs-executed drift within tolerance; (4) robustness matrix — regime × cost × rebalance-frequency × weighting sweep, OOS-only conclusions, machine-checked report. Derive acceptance criteria from the P20 pattern (deterministic script + committed artifact + consistency test + honest report).

---

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. Blocked on the meaning of the floor/cap? You are not — the exact semantics are in WP2b §B, and the numbers for both the hand example and the fixture are measured above.
2. Blocked on which tests to re-point? Only the two named fixture-based invariant tests; every assertion stays. Everything else is additive.
3. Blocked on the wide synthetic frame? Use the exact recipe in WP2b §D (40 assets, betas `0.35 … 1.9`, 60 rows, 30% legs).
4. Blocked on WP2b for any other reason? Take **WP0** (lane A) — a deterministic sweep + hash test is always landable and needs no product code.
5. Blocked on everything? Add the `rank_min_leg_beta` / `rank_max_gross` config validation plus its regression test. Something landable always exists.

Every session must end with a committed **code/test/artifact** diff and a ledger row. If a WP is only partially done, commit the slice and write the exact remainder in its ledger row.

---

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

Inner loop: `bash scripts/bab_quick.sh` + `python3 -m pytest -q tests/test_bab_p20_*.py`. Full gate once per WP boundary; never hand off mid-gate. Never lower the coverage floor.

## Forbidden (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP0/WP4 artifacts count only **with** their consistency tests).
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing the synthetic fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting rank-mode wealth/Sharpe from the 9-asset fixture as performance, or adding rank to the WP0/WP3 sweeps.
- Satisfying the gross cap by rescaling a rank row (breaks unit leg betas) or by silently widening eligibility to negative betas inside WP2b.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- "Fixing" rebalance-invariance failures by turning off beta correction in tests instead of making the product rebalance-aware.
- Reintroducing the retracted WP2 gate "zero dollars **and** unit-beta legs" (impossible in general; see WP2 §0 legacy rationale in the ledger row of 2026-11-18T19:21:09Z).
- Running `enforce_beta_neutrality` on a rank book (it flips signs).
- Promoting `weighting="rank"` to the default without WP3 OOS evidence.
- Updating the CLI golden numbers, or chasing the retracted `|realized β| ≤ 0.06` / `≤ 0.10` grid-wide gates — both are measurement artefacts.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T20:24:09Z] The handoff still declared WP2 "next" after WP2 had landed.** `weighting` exists, `construct_rank_weights` is committed at `portfolio.py:260`, `tests/test_bab_p20_rank_weighting.py` has 8 passing tests and `docs/BAB_FIDELITY.md` §9 documents the construction. A next session would have re-implemented or reverted it. Initial task rewritten to WP2b.
- **[REMOVED 2026-11-18T20:24:09Z] The previous handoff's WP2 hand table was arithmetically wrong.** It claimed `d = [24/29, 5/29]`, `β_L = 16/29`, `A = 3/2`, net `109/96`; the correct values from scores `[1.5, 0.5, 0.5, 1.5]` are `d = [3/4, 1/4]`, `e = [1/4, 3/4]`, `β_L = 23/40`, `β_H = 3/2`, weights `30/23, 10/23, −1/6, −1/2`, net `74/69`. The landed test and §9 already carry the correct values; the stale table is gone from this file. Never re-assert `16/29` or `109/96`.
- **[REMOVED 2026-11-18T20:24:09Z] WP2 landed RED.** One failing test (`TestFreezeFallback` mock config had no `weighting`, so a `MagicMock` reached `construct_portfolio` and failed validation) and 6 uncovered statements. Pinned `cfg.weighting = "equal"`; added rank input-guard / non-numeric / degenerate-row / `dry_run` coverage tests. Gate restored to **GREEN 6473/35/100% (6623 stmts)**.
- **[REMOVED 2026-11-18T20:24:09Z] Rank leg-sum guards were provably duplicate dead code.** `Σ_L(m−r) == Σ_H(r−m)` because eligible ranks sum to `n·m`, so the second guard could never fire independently (and blocked 100% coverage). Collapsed to one live guard with the identity documented.
- **[REMOVED 2026-11-18T20:24:09Z] Rank mode 51x-levered and detonated the book.** Measured: 25/398 active rows, `β_L ≤ 0.1138`, gross 9.79–51.67, −196.8% day on 2021-05-04, wealth ~1e-24. Converted into the binding WP2b (leg-beta floor + gross cap + wide-universe proof + fixture-flat documentation) so it cannot be published as a BAB result.
- **[REMOVED 2026-11-18T20:24:09Z] Unclosed markdown fence at the end of `docs/BAB_FIDELITY.md` §9** (9 fences). Closed while adding §9.1.
- **[REMOVED earlier] Stale handoff claimed WP1 was unlanded.** Re-certified from the committed tree at `33b84e2`.
- **[REMOVED earlier] WP1 coverage regression** (TOTAL 99%, 8 missed statements) — two class-B finiteness-guard tests pinned to `beta_neutral=False`; restored to 100%.
- **[REMOVED earlier] WP2 acceptance gate was infeasible** — "zero dollars + unit-beta legs" cannot both hold under leg-level inverse-beta scaling unless `β_L = β_H`; corrected gate is unit-beta legs + zero model beta, with net cash exposure documented.
- **[REMOVED earlier] WP1 hidden test explosion** — blast radius measured (10 tests), fix landed.
- **[REMOVED earlier] Daily correction vs rebalance windows** — resolved by the frozen-window hold.
- **[REMOVED earlier] Lane collisions** — lanes A/B/C with disjoint file ownership.
- **[REMOVED earlier] Real-data rabbit hole** — Coinbase API is 403 here; deferred to P21.
- **[REMOVED earlier] Duplicate durable task docs** — deleted; this file is the single source of truth.
- **[REMOVED earlier] Fresh-runner dependency trap** — documented above.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T20:24:09Z | a32a91d +1 | **WP2 verified landed; red gate repaired; WP2b opened.** Found WP2 committed at `01eb301` while the handoff still said "WP2 next". Verified the algebra against the correct 4-asset fractions (`30/23, 10/23, −1/6, −1/2`, net `74/69`) and recorded that the prior handoff's table (`16/29`, `109/96`) was wrong. Fixed the one failing test (mock config missing `weighting`), proved the duplicate leg-sum guard dead, added 3 coverage tests (input guards, non-numeric coercion, degenerate row, `dry_run` rank freeze). Measured the rank pathology: 25/398 active rows, `β_L ≤ 0.1138`, gross 9.79–51.67, −196.8% day, wealth ~1e-24; wrote it into `docs/BAB_FIDELITY.md` §9.1 and specified WP2b (floor 0.20 / cap 4.0, flat-row contract, wide-universe proof). | ruff PASS; quick GREEN; full gate **GREEN 6473 passed / 35 skipped / 100% (6623/6623)** with `BAB_GATE_MIN_COVERAGE=100` (129.2 s) |
| 2026-11-18T19:21:09Z | 33b84e2 | **WP1 verified landed; coverage regression repaired; WP2 de-risked.** Retracted the infeasible "zero-dollar + unit-beta legs" gate; specified the FP rank construction and a feasible WP3 5×40 split. | GREEN 6462/35/100% (6566/6566) |
| 2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T18:22:06Z | e376564 | WP1 de-risked on a scratch copy; duplicate task doc deleted; bot diagnostics ignored. | GREEN 6445/35/100% |
| ≤2026-11-18T14:47:47Z | 3393f8d | Handoff consolidation; grid measured; rebalance-aware fix pinned. | GREEN 6445/35/100% |
| ≤2026-11-18T14:43:40Z | 1a70054 | Campaign refresh; lanes + file ownership; network-403 note; P21 preview. | GREEN 6445/35/100% |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated; 13 scratch scripts removed. | GREEN 6445/35/100% |
| ≤2026-11-17T14:46:59Z | 73e4db2 | Original stakes closed; `strategies/betting_against_beta` 100% coverage. | 6282/35 |

## Proven closed (do not re-test, do not reopen)
P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
