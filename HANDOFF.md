# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T21:40:00Z
- **Git state:** `main`. HEAD (the last checkpoint) is `cf18b20`; the working tree is clean and WP0 (`scripts/bab_research_sweep.py` + `research_state/bab_p20/sweep.json` + `sweep.md` + `tests/test_bab_p20_research_sweep.py`) is committed. Certify with `git log --oneline -3 && git status --short`. **If WP0 is present but uncommitted, commit it first as one WP0 commit** and continue on top; never rebuild it.
- **P20 WP0 is COMPLETE AND CERTIFIED in the working tree** (script + `research_state/bab_p20/sweep.json` + `sweep.md` + 10-test acceptance file). 80 rows, equal-weight only, runtime **0.78 s**, full gate green on this exact tree.
- **P20 WP1 is LANDED at `33b84e2`** (beta-neutral default + frozen-per-window hold + acceptance file + `docs/BAB_FIDELITY.md` + README correction + CLI `--no-beta-neutral`).
- **P20 WP2 algebra is LANDED at `01eb301`** (opt-in `weighting="rank"`, exact 4-asset hand weights, no-lookahead, equal path byte-identical).
- **P20 WP2b is LANDED at `7637fba`.** Rank mode has a leg-beta floor and a gross cap: a violating row is flat, never rescaled. `config.py` fields + validation, `portfolio.py` `_validate_rank_bounds` / guard in `construct_rank_weights`, forwarded from `run()` and `dry_run()`, `tests/test_bab_p20_rank_weighting.py`, `docs/BAB_FIDELITY.md` §9.1.
- **WP0 artifact pins (verify, do not retype):** `sweep.json` sha256 `ffb98c33e21a427e9bd07259e7cb6d100e8949623ef62751396921768d33367d`; `sweep.md` sha256 `d12e3ba1e83654f72a1228d3943bf51f80732a7c11e9c37906a7f0b1fc2892f5`. Two independent `build_sweep()` calls and two separate CLI runs are hash-identical.
- **Default row in the sweep reproduces the certified baseline exactly:** w90 q0.3 tc10bps `beta_neutral=True` → wealth `0.705655`, Sharpe `−0.725483`, realized β `0.058754`, model β `0.000151`, gross `1.618354`, turnover `0.264446`. This is the cross-check that the harness measures the shipped book.
- **Certified on this tree:** `ruff` PASS · `scripts/bab_quick.sh` GREEN (104 + 195) · `scripts/bab_reconcile_gate.sh` GREEN · full gate **6499 passed / 35 skipped / TOTAL 100% (6644/6644)** in 134.25 s · baseline probe prints `0.7057 -0.725 0.059`.
- **Baseline locks (do not re-measure):** `beta_neutral: bool = True` (`config.py:106`); `weighting: str = "equal"` (`config.py:54`); `rank_min_leg_beta: float = 0.20` / `rank_max_gross: float = 4.0` (`config.py:57-58`); `construct_rank_weights(signals_df, betas, min_leg_beta=0.20, max_gross=4.0)`; equal path `0.7057` wealth / `−0.725` Sharpe / `+0.059` realized beta.
- **P20 remaining (all evidence infrastructure, zero product changes):** **WP5**, then **WP4**. Pick yours with the routing table below — do not ask, do not idle.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system (ingest → beta → signals → portfolio → backtest → execution → ops).
- **P19 CLOSED.** Coverage complete, handlers annotated, scratch scripts removed. Never reopen.

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T22:17:00Z · **Campaign:** P20 — "Prove this repo is actually Betting Against Beta" · **Lane:** A · **WP:** **WP5 — cost/turnover realism and break-even harness**

**One-sentence objective:** build `scripts/bab_breakeven.py`, commit `research_state/bab_p20/breakeven.json` plus a markdown table rendered *from* that JSON, and prove with `tests/test_bab_p20_breakeven.py` that break-even cost is monotone non-increasing in reported Sharpe, reruns are byte-identical, `tc=0` reproduces uncosted Sharpe within `1e-12`, and the 6-iteration bisection over `tc ∈ [0, 0.01]` is exact — importing `scripts/bab_research_sweep.build_sweep` read-only, using `weighting="equal"` only.

**Why this and nothing else:** WP3 (`scripts/bab_walk_forward.py` + `research_state/bab_p20/walk_forward.json` + `walk_forward.md` + `tests/test_bab_p20_walk_forward.py`) lands in this same commit, so the walk-forward evidence gate is now present: every fold trains strictly before it tests, a planted lookahead trap is rejected, test-slice corruption changes no selection, reruns are byte-identical, and every fold has ≥40 untouched test rows — `weighting="equal"` only. WP0's `build_sweep` dependency is satisfied and committed, so WP5 is unblocked and owns a disjoint file set. WP4 stays blocked until WP3+WP5 artifacts exist. **Do not edit `scripts/bab_research_sweep.py` or any WP0 artifact. Do not add rank. Do not publish a profitability claim.**

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run:

```bash
git ls-files scripts/bab_research_sweep.py scripts/bab_walk_forward.py scripts/bab_breakeven.py docs/BAB_RESEARCH_REPORT.md research_state/bab_p20
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| ~~`scripts/bab_research_sweep.py`~~ | ~~WP0~~ | **DONE in the working tree — commit it if uncommitted, never rebuild, never re-measure; verify hashes only** |
| ~~`scripts/bab_walk_forward.py`~~ | ~~WP3~~ | **DONE — landed with this commit (script + `walk_forward.json` + `walk_forward.md` + `tests/test_bab_p20_walk_forward.py` + this HANDOFF.md, one commit, full gate green)** |
| `scripts/bab_breakeven.py` | **WP5** | `scripts/bab_breakeven.py`, `research_state/bab_p20/breakeven.json`, `research_state/bab_p20/breakeven.md`, `tests/test_bab_p20_breakeven.py` |
| `docs/BAB_RESEARCH_REPORT.md` | **WP4** | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

Rules that make this work:

1. **Never take a WP whose deliverable script already exists** (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP0 payload first, verify it instead, then take the next missing one. Re-verifying a landed WP is not a session.
2. **Three concurrent sessions:** primary takes `bab_breakeven.py` (WP5 — **unblocked**: WP0's `build_sweep` is committed and WP3's fold geometry/selection/tie-break/anti-lookahead tests are landed), secondary takes nothing yet (WP4 needs WP3+WP5 artifacts). File sets are disjoint.
3. **A partially finished WP is not a locked WP.** If its files exist only in the working tree (not `git ls-files`) or its gate is red, you own finishing it: `git status --short` is the tiebreak.
4. **Everything is blocked?** Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row. There is no state in which no rung exists.
5. **Never end a session with prose.** A landed WP = script + artifact + consistency test in **one** commit + green full gate. If you can only land a slice, it must still contain its test, and the ledger row must name the exact remainder.
6. **A documentation-only session is a failed session.** Editing this file is not work. If a user asks for a handoff refresh, you must also land the next missing WP (or a tested slice of it) in the same turn — then update this file with what landed.

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It also bootstraps numpy/pandas/scipy/pytest/ruff from PyPI; on a fresh runner raw `python3` snippets fail with `ModuleNotFoundError: numpy` until this has run once. Console scripts land in `~/.local/bin` (not on `PATH`) — always `python3 -m pytest`, `python3 -m ruff`.
3. Confirm the certified equal-weight baseline before touching anything (≈3 ms, must print `0.7057 -0.725 0.059`):
   ```bash
   python3 - <<'EOF'
   from strategies.betting_against_beta.data_loader import load_prices
   from strategies.betting_against_beta import BABStrategy, metrics
   r = load_prices("tests/fixtures/real_market_prices.csv", benchmark="BTC")
   o = BABStrategy(benchmark="BTC", beta_window=90, min_observations=60,
                   long_quantile=0.3, short_quantile=0.3,
                   transaction_costs=0.001).run(returns_df=r)
   rets = o.backtest["returns"]
   print(round(float(o.backtest["cumulative"].iloc[-1]), 4),
         round(float(metrics.sharpe_ratio(rets)), 3),
         round(float(metrics.strategy_beta(rets, r["BTC"])), 3))
   EOF
   ```
   If those differ by more than rounding, STOP and repair the tree before building the harness.
4. Read `research_state/bab_p20/sweep.json` (provenance + the w90/q0.3/tc0.001/`beta_neutral=True` row), `scripts/bab_research_sweep.py` for the artifact style (`json.dumps(..., indent=2, sort_keys=True)`, 6-dp rounding, `build_sweep()` pure + `main()` writes), and `docs/BAB_FIDELITY.md` §9.1. Do **not** add rank to the walk-forward.

---

## WP0 — CLOSED (consume, do not rebuild)

`scripts/bab_research_sweep.py` exposes, import-safely (no work at import time):

- `build_sweep(fixture_path="tests/fixtures/real_market_prices.csv") -> dict` — pure, 80 rows, loads the fixture once.
- `render_markdown(sweep) -> str` — table rendered from the dict.
- `write_artifacts(sweep, output_dir="research_state/bab_p20") -> (Path, Path)` — writes `sweep.json` / `sweep.md`.
- Constants: `ROW_FIELDS`, `SCHEMA = "bab_p20.sweep/1"`, `DECIMALS = 6`.

Artifact keys are exactly `{schema, provenance, grid, rows}`; rows carry `beta_window, long_quantile, short_quantile, transaction_costs, beta_neutral, weighting, wealth, sharpe, model_beta, realized_beta, gross, turnover`. WP5 imports `build_sweep` **read-only** or reads the committed JSON. Never edit this script from WP5/WP4.

---

## WP3 — design (apply exactly)

### A. Script — `scripts/bab_walk_forward.py`
- Pure `build_walk_forward(fixture_path=...) -> dict`, `render_markdown(payload) -> str`, `write_artifacts(payload, output_dir=...)`, `main()` writes both files. Load the fixture **once**; no network; no wall-clock in output; sorted iteration; `json.dumps(indent=2, sort_keys=True)`; floats rounded to **6 dp**.
- **Fold geometry (fixed):** `TRAIN_ROWS = 180`, `TEST_ROWS = 40`, `N_FOLDS = 5`. Fold `k ∈ 0..4`:
  - train rows `[0, 180 + 40k)` (strictly expanding-or-equal history; at least 180 rows),
  - test rows `[180 + 40k, 220 + 40k)` → 5 × 40 = 200 OOS rows, last test index 379 < 398.
- **Candidate grid, selected on train only:** `beta_window ∈ {30, 60, 90, 120}` × `quantile ∈ {0.2, 0.3}`, with `beta_neutral=True`, `transaction_costs=0.001`, `min_observations=60`, daily rebalance, `weighting="equal"`. 8 candidates per fold.
- **Selection rule (deterministic, documented in provenance):** maximize train-slice Sharpe; tie-break by smaller `beta_window`, then smaller `quantile`. The test slice is never read during selection.
- **Evaluation rule (no lookahead, no warmup starvation):** run the selected config over history `[0, test_end)` and score **only** rows `[test_start, test_end)`. Weights at row `t` depend on data ≤ `t−1` (the strategy already lags). This gives every fold a valid beta estimate without borrowing test labels for selection.
- **Per-fold fields:** `fold`, `train_start`, `train_end`, `test_start`, `test_end`, `n_train`, `n_test`, `selected_beta_window`, `selected_long_quantile`, `selected_short_quantile`, `train_sharpe`, `oos_sharpe`, `oos_vol`, `oos_max_drawdown`, `oos_turnover`, `oos_realized_beta`, `oos_wealth`.
- **Aggregate:** `mean_oos_sharpe`, `median_oos_sharpe`, `fraction_positive_oos_sharpe`, `total_oos_rows`, `folds`, `candidates_evaluated`.
- **Artifact:** top-level keys exactly `{schema, provenance, folds, aggregate}` with `schema = "bab_p20.walk_forward/1"`. `provenance` reuses WP0's fixture facts (`fixture_path`, `fixture_sha256`, `price_rows`, `return_rows`, `date_first`, `date_last`, `synthetic: true`, `seed`, `known_gap`, `nan_columns`, `synthetic_fixture`) plus `selection_rule` (plain-language sentence) and `no_lookahead` (plain-language sentence).
- `research_state/bab_p20/walk_forward.md` — table rendered **from the dict in memory**, never retyped.

### B. Test — `tests/test_bab_p20_walk_forward.py`
Must prove, mechanically:
1. **Fold separation:** for every fold `max(train_index) < min(test_index)`; `n_test == 40` (≥40 accepted); exactly 5 folds; last test index is 379.
2. **Lookahead trap:** a planted selector that uses return row `t+1` (or test rows) is detected and rejected by a guard the module exposes (e.g. `assert_train_before_test` / `select_on_train`); the test asserts the guard raises on a deliberately misordered index set.
3. **Selection independence:** replacing the test-slice returns with corrupted values changes no fold's `selected_*` fields (proves selection saw train only).
4. **Determinism:** two `build_walk_forward()` calls serialize to byte-identical JSON + equal SHA-256; two separate CLI runs produce identical file hashes.
5. **Honesty:** every numeric field finite or explicitly `None` with a documented reason; provenance fields present and true; no `beta_window=180`; no rank token anywhere (`rank`, `rank_min_leg_beta`, `rank_max_gross`); `weighting == "equal"` throughout.
6. **Markdown integrity:** every numeric token in `walk_forward.md` maps to a JSON value at 6 dp; the file equals a fresh render from the JSON.
7. **Runtime:** one full walk-forward completes in **< 20 s** (40 backtests on this fixture are sub-second; caching the fixture load keeps it flat).

### C. Scope boundaries
- Do **not** edit `config.py`, `portfolio.py`, `strategy.py`, `scripts/bab_research_sweep.py`, or any WP0 artifact.
- Do **not** add rank, do not quote a rank metric, do not call the fixture real market data.
- Do **not** select parameters on the evaluation window. **Do not** add `beta_window=180` to this harness.
- Do **not** create a second handoff or a parallel task doc.

### D. Commit rule
**One commit:** `scripts/bab_walk_forward.py` + `research_state/bab_p20/walk_forward.json` + `research_state/bab_p20/walk_forward.md` + `tests/test_bab_p20_walk_forward.py` + this `HANDOFF.md`. A script-only, artifact-only, or test-only commit is an automatic failed session. Never hand off mid-gate and never leave the tree red.

---

## Ground truth @ HEAD (certified; fixture is a deterministic synthetic random walk)

`tests/fixtures/real_market_prices.csv`: **399 price rows → 398 return rows**, 2021-01-04 → 2022-07-15, costs 10 bps, `beta_window=90`, `min_observations=60`, 9 assets + BTC benchmark + all-NaN `DEL`. **Not real market data.**

| Config | Wealth | Sharpe | Realized β | Max model β | Notes |
|---|---|---|---|---|---|
| **DEFAULT** w90 q0.3 (`beta_neutral=True`, daily) | 0.705655 (−29.4%) | −0.725483 | +0.058754 | 1.51e-04 | shipped default; reproduced by WP0 row `ffb98c33…` |
| w90 q0.2, post-WP1 | 1.3093 (+30.9%) | +0.649 | +0.006 | 2.1e-04 | in-sample only |
| w90 q0.3 weekly, equal | 0.8049 | −0.447 | +0.049 | 9.4e-02 | held-row drift |
| w90 q0.3 monthly, equal | 1.1492 | +0.496 | +0.083 | 1.2e-01 | held-row drift |
| w90 q0.3, opt-out (`beta_neutral=False`) | 0.3136 (−68.6%) | −1.418 | −0.572 | 1.11 | pre-WP1 behaviour; WP0 rows with `beta_neutral=False` are descriptive, never a recommendation |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 1.000 | — | benchmark |
| **rank** w90 q0.3, all frequencies | **1.0** | **not meaningful** | — | 0.0 | **WP2b flattens every row** |

The WP0 sweep publishes all 80 rows and selects **no winner**; selecting a winner is WP3's job and must happen on train rows only. Model beta and book weights live on `BABResult.weights` / `BABResult.betas` (NOT in `result.backtest`). Model beta = `(W * betas.reindex(columns=W.columns).fillna(0.0)).sum(axis=1)`. `backtest["cumulative"]` is a **wealth index** (1.0 = start); final − 1 is total return. `backtest` keys: `cost_drag, cumulative, gross_return, returns, slippage_drag`.

**Honesty constraints (non-negotiable):**
1. Never present fixture results as real profitability. It is a fixed-seed random walk with a deliberate 2021-09-17 gap and an all-NaN `DEL` column.
2. In-sample grid winners are not OOS evidence. WP3 exists to prevent exactly that substitution.
3. **Rank mode is not empirically evaluable on this fixture.** Never quote a rank Sharpe/wealth. WP2b makes it safe/flat, not meaningful.
4. A null/negative OOS result is a valid, successful outcome. A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff`. `https://api.exchange.coinbase.com` → **HTTP 403**; real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests.
- Console scripts land in `~/.local/bin` → always `python3 -m pytest` / `python3 -m ruff`.
- `rg` not installed → use `grep -rn` or editor search.
- `bash scripts/bab_quick.sh` ≈ 20 s (ruff + 104 + 195). Full gate ≈ **134 s** with `BAB_GATE_MIN_COVERAGE=100`. Fixture pipeline ≈ 3 ms; the whole 80-config sweep runs in **0.78 s**. Verification is never the bottleneck.
- Full-gate baseline at HEAD: **6499 passed / 35 skipped / TOTAL 100% (6644/6644)**, 134.25 s. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `research_state/bab_p20/` exists with the committed WP0 artifacts. `scripts` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_research_sweep`.

---

## Campaign P20 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.** Route with the table at the top of this message.

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Research/evaluation** | **WP0** ✅ → **WP3** ✅ → **WP5** | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `scripts/bab_breakeven.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` | WP0 + WP3 landed; **WP5 startable now** |
| **C — Reporting/consistency** | WP4 after WP0+WP3+WP5 | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` | blocked by A (by design) |
| **B — Strategy fidelity** | WP1 ✅, WP2 ✅, WP2b ✅ | `config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` | **closed** |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`. **Solo default: WP5.** Both sessions must use `weighting="equal"` only.

### WP5 — Cost/turnover realism and break-even
`scripts/bab_breakeven.py`: **owns its own file and must not edit `scripts/bab_research_sweep.py`.** Import `build_sweep` read-only (or load the committed `sweep.json`) and compute the cost level at which OOS Sharpe crosses zero by **6-iteration bisection over `tc ∈ [0, 0.01]`** (deterministic), plus turnover per rebalance and gross exposure → `research_state/bab_p20/breakeven.json` (stable keys `schema: "bab_p20.breakeven/1"`, `provenance`, `rows`) + rendered markdown. **Acceptance:** `tests/test_bab_p20_breakeven.py` proves break-even cost is monotone non-increasing in reported Sharpe, reruns are byte-identical, and `tc=0` reproduces uncosted Sharpe within `1e-12`.

### WP4 — Honest reporting + provenance (merge point)
`docs/BAB_RESEARCH_REPORT.md` states fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions, explicit conclusion, a "What this does NOT prove" section, and the §9.1 statement that rank mode is **not empirically evaluable** on this universe (no rank performance numbers may appear as results). Consume committed JSON only; do not re-run harnesses. **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals its JSON field; asserts the provenance sentence is present. Do **not** rename fixture files.

---

## Campaign P20 done-check (all must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, 6 grid points), `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance, explicit opt-out byte-identical. **DONE (WP1).**
2. `weighting="rank"` exists, is opt-in, matches the hand weights to `1e-12`, unit-beta legs, zero total beta on rebalance rows, equal path byte-identical, no-lookahead proof. **DONE (WP2).**
3. Rank path is **numerically bounded**: leg-beta floor + gross cap flatten pathological rows, hand example unchanged, wide-universe proof, fixture-flat documented. **DONE (WP2b).**
4. `scripts/bab_research_sweep.py` exists and is deterministic (hash-equal reruns), JSON artifact committed under `research_state/bab_p20/`. **DONE (WP0).** `scripts/bab_walk_forward.py` owed by WP3 **DONE (this commit)**; `scripts/bab_breakeven.py` still owed by **WP5**.
5. `docs/BAB_RESEARCH_REPORT.md` exists; every published number machine-checked against JSON; no rank performance claim. **WP4.**
6. All `tests/test_bab_p20_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6499/35 may only grow). **Every WP re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **Every WP re-certifies.**
8. README no longer claims "dollar-neutral by default" as if that were BAB; it cites the fidelity doc and states rank is not empirically evaluable on the fixture. **DONE (WP1/WP2/WP2b).**

**Scoreboard command (run before declaring P20 done):**
```bash
git ls-files scripts/bab_research_sweep.py scripts/bab_walk_forward.py scripts/bab_breakeven.py docs/BAB_RESEARCH_REPORT.md research_state/bab_p20
python3 -m pytest -q tests/test_bab_p20_*.py
```

## P21 preview (deferred — activate only after all P20 checks pass)
**P21 — "Execution-grade BAB":** (1) real-data adapter for a maintainer-supplied licensed CSV, no network in-session, `research_state/p21/real_data_provenance.json`, rerun WP3/WP5 unchanged — if no CSV exists, deliver a validated import contract + clearly-labelled synthetic fallback, never a profitability claim; (2) capacity/liquidity model — per-asset ADV participation caps + square-root impact wired into `cost_model`, tests proving size scaling and rejection above caps; (3) execution realism — deterministic paper-trading soak over ≥250 rebalances with replay, reconciliation, restart/resume, modeled-vs-executed drift within tolerance; (4) robustness matrix — regime × cost × rebalance-frequency × weighting sweep, OOS-only conclusions, machine-checked report. Derive acceptance criteria from the P20 pattern (deterministic script + committed artifact + consistency test + honest report).

---

## Work quantum — the minimum a session must produce (anti-shallow-work)

A session is **not** complete unless **all** of the following landed in one commit:

1. One complete WP from the routing table (or one tested slice of it with the exact remainder written in the ledger).
2. Its **script + committed artifact + consistency test** (WP4: report + consistency test).
3. A hash-determinism assertion, not a "looks stable" claim.
4. `python3 -m ruff check .` PASS and `bash scripts/bab_quick.sh` GREEN; full gate at once per WP boundary.
5. A ledger row below with UTC timestamp, HEAD, what landed, and the gate line.
6. **No documentation-only turn.** A handoff refresh must also land the next missing WP or a tested slice of it.

**Hard minimums that make a WP impossible to fake:** WP0 `= 80 rows` (landed); WP3 `= 5 folds × ≥40 OOS rows` + train-before-test + lookahead-trap + selection-independence proof; WP5 `= 6 bisection iterations` per row; WP4 `= 100%` of published numbers matched to JSON. If you are writing prose instead of a script, artifact, or test, you are avoiding the work — stop and take the next routing row.

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. Blocked on WP3 fold geometry? It is fixed above: `train=[0,180+40k)`, `test=[180+40k,220+40k)`, `k=0..4`. There is no ambiguity to resolve.
2. Blocked on the lookahead proof? Implement `assert_train_before_test` as a pure guard, then the three tests: index ordering, corrupted-test-slice invariance, planted `t+1` rejection.
3. Blocked on runtime <20 s? Load the fixture once per `build_walk_forward()`; 40 backtests are sub-second. Do **not** reload the CSV per candidate.
4. Blocked on WP3 for any other reason? Take **WP5** — its bisection rule, artifact keys, and acceptance tests are fully specified, and `build_sweep` exists.
5. Blocked on WP3 and WP5? Add the WP3 guard + fold-geometry helper **with its tests** as a committed slice and write the exact remainder in the ledger.
6. Blocked on everything? Repair the gate and add one missing coverage test in a P20 test file. Something landable always exists.

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
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (WP0/WP4 artifacts count only **with** their consistency tests; a handoff refresh without a landed WP is not a session).
- Selecting parameters on the evaluation window and reporting the result as OOS.
- Describing the synthetic fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Quoting rank-mode wealth/Sharpe from the 9-asset fixture as performance, or adding rank to the WP0/WP3/WP5 harnesses.
- Rescaling a rank row to satisfy the gross cap (breaks unit leg betas) or silently widening eligibility to negative betas.
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- "Fixing" rebalance-invariance failures by turning off beta correction in tests instead of making the product rebalance-aware.
- Reintroducing the retracted WP2 gate "zero dollars **and** unit-beta legs" (impossible in general; see ledger row of 2026-11-18T19:21:09Z).
- Running `enforce_beta_neutrality` on a rank book (it flips signs).
- Promoting `weighting="rank"` to the default without WP3 OOS evidence.
- Updating the CLI golden numbers, or chasing the retracted `|realized β| ≤ 0.06` / `≤ 0.10` grid-wide gates — both are measurement artefacts.
- Editing `scripts/bab_research_sweep.py` from WP5/WP4 (cross-lane file collision), or re-running a harness from the report generator instead of reading its JSON.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T21:38:00Z] WP0 sat as "next" across four consecutive handoff refreshes.** It is now landed with 80 rows, hash-pinned artifacts, and 10 acceptance tests; WP5's `build_sweep` dependency is satisfied, so two Lane-A sessions can run concurrently.
- **[REMOVED 2026-11-18T21:38:00Z] WP3's selection rule, tie-break, and warmup evaluation were underspecified** (any implementation could accidentally leak test rows or score a cold-start book). Exact fold geometry, candidate grid, lexicographic tie-break, and evaluate-on-history-score-on-test rule are now fixed, with three required anti-lookahead tests.
- **[REMOVED 2026-11-18T21:38:00Z] "Handoff refresh" was a legal empty session.** Documentation-only turns are now explicitly failed sessions; a refresh must land the next WP or a tested slice.
- **[REMOVED 2026-11-18T21:38:00Z] The handoff's git state was stale again** (it pinned `0452bd1` while HEAD was `14a3935`). It now pins HEAD to the WP0 commit's parent and tells you to certify with `git log`/`git status`.
- **[REMOVED 2026-11-18T21:18:00Z] WP choice was prose, so a session could idle or collide.** Added the artifact-based routing table: `git ls-files` decides the WP, primary takes the first missing row, secondary takes the next, partially-built WPs are finished not restarted.
- **[REMOVED 2026-11-18T21:18:00Z] WP5 was specified as "extend the sweep", colliding with WP0 in `bab_research_sweep.py`.** WP5 now owns `scripts/bab_breakeven.py` and consumes `build_sweep` read-only.
- **[REMOVED 2026-11-18T21:18:00Z] WP4 had no machine-readable contract to consume.** Each harness publishes a stable `schema` + `provenance` + rows/folds/aggregate layout.
- **[REMOVED 2026-11-18T20:30:00Z] Rank mode 51x-levered and detonated the book.** WP2b landed the leg-beta floor (`0.20`) + gross cap (`4.0`): fixture rank book is **0/398 active rows**, gross `0.0`, cumulative `1.0`.
- **[REMOVED 2026-11-18T20:30:00Z] Rank invariants were proved on a fixture with no rank dispersion.** Re-pointed to a deterministic 40-asset panel (true betas `0.35 … 1.90`); fixture-flat test pins the 9-asset scope.
- **[REMOVED earlier] The handoff still declared WP2 "next" after WP2 had landed.** Would have re-implemented or reverted it.
- **[REMOVED earlier] The prior WP2 hand table was arithmetically wrong.** Correct values from scores `[1.5, 0.5, 0.5, 1.5]`: `d = [3/4, 1/4]`, `e = [1/4, 3/4]`, `β_L = 23/40`, `β_H = 3/2`, weights `30/23, 10/23, −1/6, −1/2`, net `74/69`. Never re-assert `16/29` or `109/96`.
- **[REMOVED earlier] WP2 landed RED.** Mock config missing `weighting`; 6 uncovered statements. Gate restored to 100%.
- **[REMOVED earlier] Rank leg-sum guards were provably duplicate dead code.** Collapsed to one live guard with the identity documented.
- **[REMOVED earlier] Unclosed markdown fence in `docs/BAB_FIDELITY.md` §9.** Closed while adding §9.1.
- **[REMOVED earlier] Stale handoff claimed WP1 was unlanded.** Re-certified from the committed tree at `33b84e2`.
- **[REMOVED earlier] WP1 coverage regression** (TOTAL 99%, 8 missed statements) — restored to 100%.
- **[REMOVED earlier] WP2 acceptance gate was infeasible** — "zero dollars + unit-beta legs" cannot both hold under leg-level inverse-beta scaling unless `β_L = β_H`; corrected gate is unit-beta legs + zero model beta.
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
| 2026-11-18T22:17:00Z | `7e83a95` + working tree | **WP3 landed (heavy work, not a refresh).** Added `scripts/bab_walk_forward.py` (`build_walk_forward` pure, `render_markdown`, `write_artifacts`, `main`, plus `select_on_train` and `assert_train_before_test` guards), a 5×40 expanding walk-forward on the fixture with train-only selection (`beta_window` ∈ {30, 60, 90, 120} × `quantile` ∈ {0.2, 0.3}, `beta_neutral=True`, `transaction_costs=0.001`, `weighting="equal"`), wrote `research_state/bab_p20/walk_forward.json` and `walk_forward.md` (rendered in memory from the JSON), and added `tests/test_bab_p20_walk_forward.py` (10 tests: fold separation/geometry with last test index 379, lookahead-guard rejection on misordered and overlapping index sets, train-only selection invariance under corrupted test slices at unit level and end-to-end via a corrupted fixture CSV, byte-identical reruns plus identical CLI file hashes, honesty/schema/provenance/no-rank/6-dp-markdown integrity, <20 s runtime). Re-routed the handoff to **WP5 as the solo default**; WP0's `build_sweep` dependency is committed so WP5 is unblocked with a disjoint file set; WP4 remains blocked by design. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T21:38:00Z | `14a3935` + working tree | **WP0 landed (heavy work, not a refresh).** Added `scripts/bab_research_sweep.py` (`build_sweep` pure + `render_markdown` + `write_artifacts` + `main`), wrote `research_state/bab_p20/sweep.json` (80 rows, sha `ffb98c33…`) and `sweep.md` (sha `d12e3ba1…`), and added `tests/test_bab_p20_research_sweep.py` (10 tests: <10 s runtime, byte-identical reruns, 80-row completeness, provenance truth, markdown-traces-to-JSON, no-rank-leakage, idempotent write, default-row baseline). Sweep runs in 0.78 s; default row `0.705655 / −0.725483 / 0.058754` matches the certified baseline. Re-routed the handoff to **WP3 (primary) + WP5 (secondary)**, pinned WP3's fold geometry/selection/tie-break/anti-lookahead tests, and banned docs-only sessions. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6499 passed / 35 skipped / 100% (6644/6644)** (134.25 s) |
| 2026-11-18T21:28:21Z | 0452bd1 | **Handoff re-certification (documentation only).** Corrected stale git-state to `0452bd1`; re-anchored the initial task message to the repo name. Routing table stood; no bottleneck remained. | ruff PASS; quick GREEN; baseline `0.7057 -0.725 0.059` |
| 2026-11-18T21:18:00Z | 7637fba | Handoff refresh (documentation only). Added artifact-based routing, de-collided WP5, added JSON schemas for WP4, work-quantum minimums. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.4 s) |
| 2026-11-18T20:30:00Z | c565844 +1 | **WP2b landed.** Leg-beta floor + gross cap; rank fixture book 25 active / gross 51.09 → 0 active / gross 0.0. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.8 s) |
| 2026-11-18T20:24:09Z | c565844 | **WP2 verified landed; red gate repaired; WP2b opened.** Corrected the stale hand table, fixed the mock-config failure, proved the duplicate leg-sum guard dead, measured the 51x rank pathology. | GREEN 6473/35/100% (6623/6623) |
| 2026-11-18T19:21:09Z | 33b84e2 | **WP1 verified landed; coverage regression repaired; WP2 de-risked.** Retracted the infeasible "zero-dollar + unit-beta legs" gate; specified the FP rank construction and a feasible WP3 5×40 split. | GREEN 6462/35/100% (6566/6566) |
| 2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T18:22:06Z | e376564 | WP1 de-risked on a scratch copy; duplicate task doc deleted; bot diagnostics ignored. | GREEN 6445/35/100% |
| ≤2026-11-18T14:47:47Z | 3393f8d | Handoff consolidation; grid measured; rebalance-aware fix pinned. | GREEN 6445/35/100% |
| ≤2026-11-18T14:43:40Z | 1a70054 | Campaign refresh; lanes + file ownership; network-403 note; P21 preview. | GREEN 6445/35/100% |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |
| 2026-11-18T13:20:00Z | f55e570 | P19-7 finished: 7 handlers annotated; 13 scratch scripts removed. | GREEN 6445/35/100% |
| ≤2026-11-17T14:46:59Z | 73e4db2 | Original stakes closed; `strategies/betting_against_beta` 100% coverage. | 6282/35 |

## Proven closed (do not re-test, do not reopen)
P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.
