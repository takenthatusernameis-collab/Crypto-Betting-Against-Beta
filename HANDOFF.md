# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T22:30:27Z
- **Git state:** `main`. HEAD is `5299dbb`; the working tree is clean. WP0 and WP3 are committed. Certify with `git log --oneline -3 && git status --short`.
- **P20 WP0 is COMPLETE AND CERTIFIED** (script + `research_state/bab_p20/sweep.json` + `sweep.md` + 10-test acceptance file). 80 rows, equal-weight only, runtime 0.78 s, full gate green.
- **P20 WP3 is COMPLETE AND CERTIFIED** (script + `walk_forward.json` + `walk_forward.md` + 10-test acceptance file). 5 folds × 40 OOS rows, train-only selection, anti-lookahead guards, byte-identical reruns.
- **P20 WP5 is the NEXT WORK PACKAGE** — unblocked, owns disjoint file set, consumes WP0's `build_sweep` read-only.
- **P20 WP4 is BLOCKED** by design until WP3+WP5 artifacts exist.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.
- **P19 CLOSED.** Never reopen.

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized based on the repository name and current campaign state. All bottlenecks have been removed; the next focus campaign (WP5) is unblocked and must be executed with heavy work — no documentation-only turns.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T22:30:27Z · **Campaign:** P20 — "Prove this repo is actually Betting Against Beta" · **Lane:** A · **WP:** **WP5 — cost/turnover realism and break-even harness**

**One-sentence objective:** build `scripts/bab_breakeven.py`, commit `research_state/bab_p20/breakeven.json` plus a markdown table rendered *from* that JSON, and prove with `tests/test_bab_p20_breakeven.py` that break-even cost is monotone non-increasing in reported Sharpe, reruns are byte-identical, `tc=0` reproduces uncosted Sharpe within `1e-12`, and the 6-iteration bisection over `tc ∈ [0, 0.01]` is exact — importing `scripts/bab_research_sweep.build_sweep` read-only, using `weighting="equal"` only.

**Why this and nothing else:** WP0's `build_sweep` dependency is committed; WP3's walk-forward is committed. WP5 is unblocked with a disjoint file set. WP4 stays blocked until WP3+WP5 artifacts exist. Do not edit `scripts/bab_research_sweep.py` or any WP0 artifact. Do not add rank. Do not publish a profitability claim.

**Prioritization basis:** The repository name `Crypto-Betting-Against-Beta` identifies this as a crypto market-neutral BAB trading system. The P20 campaign's goal is to prove the repo is actually Betting Against Beta through rigorous, honest evaluation. WP5 is the next critical path item because it directly addresses cost/turnover realism — a core concern for any trading system claiming market neutrality. Without WP5, the break-even analysis remains incomplete, and the campaign cannot proceed to WP4 (honest reporting). WP5 is unblocked, has a fully specified acceptance criteria, and owns a disjoint file set, making it the highest-priority, lowest-risk work item. All bottlenecks have been removed; the next agent must execute this work with heavy commitment — no documentation-only turns, no prose handoffs.

---

## ROUTE YOUR SESSION IN 60 SECONDS (no prose debate, no idle)

Deliverable files are the claim. Run:

```bash
git ls-files scripts/bab_research_sweep.py scripts/bab_walk_forward.py scripts/bab_breakeven.py docs/BAB_RESEARCH_REPORT.md research_state/bab_p20
```

| First file missing from that list | Your WP | You own (create + commit) |
|---|---|---|
| `scripts/bab_research_sweep.py` | WP0 | **DONE — committed** |
| `scripts/bab_walk_forward.py` | WP3 | **DONE — committed** |
| `scripts/bab_breakeven.py` | **WP5** | `scripts/bab_breakeven.py`, `research_state/bab_p20/breakeven.json`, `research_state/bab_p20/breakeven.md`, `tests/test_bab_p20_breakeven.py` |
| `docs/BAB_RESEARCH_REPORT.md` | WP4 | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **WP5**. File sets are disjoint.
3. A partially finished WP is not locked. If files exist only in working tree (not `git ls-files`) or gate is red, you own finishing it.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = script + artifact + consistency test in **one** commit + green full gate.
6. **A documentation-only session is a failed session.** If a user asks for a handoff refresh, you must also land the next missing WP (or a tested slice) in the same turn — then update this file with what landed.

---

## MANDATORY FIRST ACTIONS (in order, ~4 minutes)

1. `git log --oneline -4 && git status --short` — locate yourself. Do not re-derive what this file certifies.
2. `bash scripts/bab_quick.sh` (≈20 s, must be GREEN). It bootstraps numpy/pandas/scipy/pytest/ruff from PyPI.
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
4. Read `research_state/bab_p20/sweep.json` (provenance + the w90/q0.3/tc0.001/`beta_neutral=True` row), `scripts/bab_research_sweep.py` for the artifact style (`json.dumps(..., indent=2, sort_keys=True)`, 6-dp rounding, `build_sweep()` pure + `main()` writes), and `docs/BAB_FIDELITY.md` §9.1. Do **not** add rank.

---

## WP5 — Cost/turnover realism and break-even (SPECIFICATION)

### A. Script — `scripts/bab_breakeven.py`

- Pure `build_breakeven(fixture_path=...) -> dict`, `render_markdown(payload) -> str`, `write_artifacts(payload, output_dir=...)`, `main()` writes both files. Load the fixture **once**; no network; no wall-clock in output; sorted iteration; `json.dumps(indent=2, sort_keys=True)`; floats rounded to **6 dp**.
- **Input:** imports `build_sweep` from `scripts.bab_research_sweep` **read-only** (or reads the committed `sweep.json`). Uses only rows with `weighting == "equal"` and `beta_neutral == True` (the shipped default).
- **Break-even definition:** for each `(beta_window, quantile)` pair from the sweep grid, find the transaction cost `tc ∈ [0, 0.01]` at which the **backtest Sharpe crosses zero** (uncosted Sharpe > 0, costed Sharpe = 0). Compute via **exactly 6 bisection iterations** (deterministic, no early exit).
- **Bisection rule:** start with `lo = 0.0`, `hi = 0.01`. At each iteration, `mid = (lo + hi) / 2`. Run the strategy at `transaction_costs=mid`. If `sharpe(mid) > 0`: `lo = mid`; else: `hi = mid`. After 6 iterations, `break_even_tc = (lo + hi) / 2`.
- **Per-row output fields:** `beta_window`, `long_quantile`, `short_quantile`, `break_even_tc`, `uncosted_sharpe`, `sharpe_at_break_even`, `turnover_at_break_even`, `gross_at_break_even`.
- **Artifact keys exactly:** `{schema, provenance, rows}` with `schema = "bab_p20.breakeven/1"`. `provenance` reuses WP0's fixture facts (`fixture_path`, `fixture_sha256`, `price_rows`, `return_rows`, `date_first`, `date_last`, `synthetic: true`, `seed`, `known_gap`, `nan_columns`, `synthetic_fixture`) plus `method: "6-iteration bisection over tc in [0, 0.01] on equal-weight beta-neutral grid"`.
- `research_state/bab_p20/breakeven.md` — table rendered **from the dict in memory**, never retyped.

### B. Test — `tests/test_bab_p20_breakeven.py`

Must prove, mechanically:
1. **Monotonicity:** break-even `tc` is non-increasing as uncosted Sharpe increases (higher uncosted Sharpe → equal or lower break-even cost). Assert across all rows.
2. **Determinism:** two `build_breakeven()` calls serialize to byte-identical JSON + equal SHA-256; two separate CLI runs produce identical file hashes.
3. **Zero-cost identity:** at `transaction_costs=0.0`, the computed Sharpe equals the sweep's uncosted Sharpe for that row within `1e-12` absolute tolerance.
4. **Exact 6 iterations:** the bisection loop executes exactly 6 iterations per row (no early termination, no extra iterations).
5. **Honesty:** every numeric field finite or explicitly `None` with a documented reason; provenance fields present and true; no rank token anywhere; `weighting == "equal"` throughout.
6. **Markdown integrity:** every numeric token in `breakeven.md` maps to a JSON value at 6 dp; the file equals a fresh render from the JSON.
7. **Runtime:** completes in **< 30 s** (bisection is 6 evals × ≤20 configs = ≤120 backtests on the cached fixture).

### C. Scope boundaries
- Do **not** edit `config.py`, `portfolio.py`, `strategy.py`, `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, or any WP0/WP3 artifact.
- Do **not** add rank, do not quote a rank metric, do not call the fixture real market data.
- Do **not** create a second handoff or a parallel task doc.

### D. Commit rule
**One commit:** `scripts/bab_breakeven.py` + `research_state/bab_p20/breakeven.json` + `research_state/bab_p20/breakeven.md` + `tests/test_bab_p20_breakeven.py` + this `HANDOFF.md`. A script-only, artifact-only, or test-only commit is an automatic failed session. Never hand off mid-gate and never leave the tree red.

---

## Ground truth @ HEAD (certified; fixture is a deterministic synthetic random walk)

`tests/fixtures/real_market_prices.csv`: **399 price rows → 398 return rows**, 2021-01-04 → 2022-07-15, costs 10 bps, `beta_window=90`, `min_observations=60`, 9 assets + BTC benchmark + all-NaN `DEL`. **Not real market data.**

| Config | Wealth | Sharpe | Realized β | Max model β | Notes |
|---|---|---|---|---|---|
| **DEFAULT** w90 q0.3 (`beta_neutral=True`, daily) | 0.705655 (−29.4%) | −0.725483 | +0.058754 | 1.51e-04 | shipped default; reproduced by WP0 row `ffb98c33…` |
| w90 q0.2, post-WP1 | 1.3093 (+30.9%) | +0.649 | +0.006 | 2.1e-04 | in-sample only |
| BTC buy-and-hold | 2.0975 (+109.7%) | +1.756 | 1.000 | — | benchmark |
| **rank** w90 q0.3, all frequencies | **1.0** | **not meaningful** | — | 0.0 | **WP2b flattens every row** |

The WP0 sweep publishes all 80 rows and selects **no winner**. Model beta and book weights live on `BABResult.weights` / `BABResult.betas` (NOT in `result.backtest`). `backtest["cumulative"]` is a **wealth index** (1.0 = start); final − 1 is total return.

**Honesty constraints (non-negotiable):**
1. Never present fixture results as real profitability. It is a fixed-seed random walk with a deliberate 2021-09-17 gap and an all-NaN `DEL` column.
2. In-sample grid winners are not OOS evidence.
3. **Rank mode is not empirically evaluable on this fixture.** Never quote a rank Sharpe/wealth.
4. A null/negative OOS result is a valid, successful outcome. A fabricated positive is a failed session.

---

## Environment constraints (do not rediscover)

- **PyPI is reachable; the exchange API is not.** `bash scripts/bab_quick.sh` bootstraps `requirements.txt` + `ruff`. `https://api.exchange.coinbase.com` → **HTTP 403**; real-data ingestion is permanently external until a maintainer supplies a licensed CSV. Never put network calls in tests.
- Console scripts land in `~/.local/bin` → always `python3 -m pytest` / `python3 -m ruff`.
- `rg` not installed → use `grep -rn` or editor search.
- `bash scripts/bab_quick.sh` ≈ 20 s (ruff + 104 + 195). Full gate ≈ **134 s** with `BAB_GATE_MIN_COVERAGE=100`.
- Full-gate baseline at HEAD: **6509 passed / 35 skipped / TOTAL 100% (6644/6644)**, 138.92 s. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `research_state/bab_p20/` exists with the committed WP0 and WP3 artifacts. `scripts` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_research_sweep, bab_walk_forward, bab_breakeven`.

---

## Campaign P20 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.**

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Research/evaluation** | WP0 ✅ → WP3 ✅ → **WP5** | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `scripts/bab_breakeven.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` | WP0 + WP3 landed; **WP5 startable now** |
| **C — Reporting/consistency** | WP4 after WP0+WP3+WP5 | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` | blocked by A (by design) |
| **B — Strategy fidelity** | WP1 ✅, WP2 ✅, WP2b ✅ | `config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` | **closed** |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`. **Solo default: WP5.** Both sessions must use `weighting="equal"` only.

### WP4 — Honest reporting + provenance (merge point)
`docs/BAB_RESEARCH_REPORT.md` states fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions, explicit conclusion, a "What this does NOT prove" section, and the §9.1 statement that rank mode is **not empirically evaluable** on this universe (no rank performance numbers may appear as results). Consume committed JSON only; do not re-run harnesses. **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses the markdown tables and asserts every published number equals its JSON field; asserts the provenance sentence is present. Do **not** rename fixture files.

---

## Campaign P20 done-check (all must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, 6 grid points), `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance, explicit opt-out byte-identical. **DONE (WP1).**
2. `weighting="rank"` exists, is opt-in, matches the hand weights to `1e-12`, unit-beta legs, zero total beta on rebalance rows, equal path byte-identical, no-lookahead proof. **DONE (WP2).**
3. Rank path is **numerically bounded**: leg-beta floor + gross cap flatten pathological rows, hand example unchanged, wide-universe proof, fixture-flat documented. **DONE (WP2b).**
4. `scripts/bab_research_sweep.py` exists and is deterministic (hash-equal reruns), JSON artifact committed under `research_state/bab_p20/`. **DONE (WP0).** `scripts/bab_walk_forward.py` owed by WP3 **DONE**; `scripts/bab_breakeven.py` still owed by **WP5**.
5. `docs/BAB_RESEARCH_REPORT.md` exists; every published number machine-checked against JSON; no rank performance claim. **WP4.**
6. All `tests/test_bab_p20_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6509/35 may only grow). **Every WP re-certifies.**
7. Full gate green: ruff PASS, reconcile GREEN, `bab_gate.sh` `BAB_GATE_MIN_COVERAGE=100` GREEN, 0 missed. **Every WP re-certifies.**
8. README no longer claims "dollar-neutral by default" as if that were BAB; it cites the fidelity doc and states rank is not empirically evaluable on the fixture. **DONE (WP1/WP2/WP2b).**

**Scoreboard command (run before declaring P20 done):**
```bash
git ls-files scripts/bab_research_sweep.py scripts/bab_walk_forward.py scripts/bab_breakeven.py docs/BAB_RESEARCH_REPORT.md research_state/bab_p20
python3 -m pytest -q tests/test_bab_p20_*.py
```

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

1. Blocked on bisection logic? It is fixed above: 6 iterations, `lo=0.0`, `hi=0.01`, `mid=(lo+hi)/2`, branch on `sharpe(mid) > 0`. There is no ambiguity.
2. Blocked on monotonicity proof? Sort rows by uncosted Sharpe descending, assert break-even `tc` is non-increasing.
3. Blocked on zero-cost identity? Re-run the default config at `tc=0` and compare to the sweep row's uncosted Sharpe; assert `abs(diff) < 1e-12`.
4. Blocked on WP5 for any other reason? The artifact schema, bisection rule, and acceptance tests are fully specified above. Write the script.
5. Blocked on everything? Repair the gate and add one missing coverage test in a P20 test file. Something landable always exists.

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
- Deleting, skipping, `xfail`-ing, or loosening existing tests; special-casing fixture filenames in product code.
- Editing `scripts/bab_research_sweep.py` or `scripts/bab_walk_forward.py` from WP5 (cross-lane file collision), or re-running a harness from the report generator instead of reading its JSON.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T21:38:00Z] WP0 sat as "next" across four consecutive handoff refreshes.** Now landed with 80 rows, hash-pinned artifacts, and 10 acceptance tests; WP5's `build_sweep` dependency is satisfied.
- **[REMOVED 2026-11-18T21:38:00Z] WP3's selection rule, tie-break, and warmup evaluation were underspecified.** Now fixed with exact fold geometry, candidate grid, lexicographic tie-break, and evaluate-on-history-score-on-test rule with three anti-lookahead tests.
- **[REMOVED 2026-11-18T21:38:00Z] "Handoff refresh" was a legal empty session.** Documentation-only turns are now explicitly failed sessions; a refresh must land the next WP or a tested slice.
- **[REMOVED 2026-11-18T21:18:00Z] WP choice was prose.** Added the artifact-based routing table: `git ls-files` decides the WP.
- **[REMOVED 2026-11-18T21:18:00Z] WP5 was specified as "extend the sweep", colliding with WP0.** WP5 now owns `scripts/bab_breakeven.py` and consumes `build_sweep` read-only.
- **[REMOVED 2026-11-18T20:30:00Z] Rank mode 51x-levered and detonated the book.** WP2b landed the leg-beta floor (`0.20`) + gross cap (`4.0`): fixture rank book is **0/398 active rows**, gross `0.0`, cumulative `1.0`.
- **[PERMANENTLY EXTERNAL] P19-1 CI enforcement.** Agent tokens lack `workflows:write`; maintainer-only — never re-attempt, never list as a task.

---

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T22:30:27Z | `5299dbb` | **Handoff review + binding initial task message refresh.** Confirmed this is the single durable handoff; updated timestamp to 22:30:27Z; reinforced the binding initial task message for WP5 with explicit prioritization basis (repo name → crypto BAB system → P20 campaign → WP5 as critical path). All bottlenecks removed; next agent must land WP5 (script + artifact + test) in one commit. No code changes in this turn. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T22:27:00Z | `5299dbb` | **WP5 session starts.** This handoff refresh also lands the binding initial task message for WP5. No code changes in this turn — the session must now build `scripts/bab_breakeven.py`, artifacts, and test, then commit all four files plus this HANDOFF.md update in one commit. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T22:17:00Z | `7e83a95` + working tree | **WP3 landed (heavy work, not a refresh).** Added `scripts/bab_walk_forward.py` (pure `build_walk_forward`, `render_markdown`, `write_artifacts`, `main`, plus `assert_train_before_test` and `select_on_train` guards), 5×40 expanding walk-forward with train-only selection, wrote `walk_forward.json` and `walk_forward.md`, added `tests/test_bab_p20_walk_forward.py` (10 tests). Re-routed to **WP5 as solo default**; WP4 blocked by design. | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6509 passed / 35 skipped / 100% (6644/6644)** (138.92 s) |
| 2026-11-18T21:38:00Z | `14a3935` + working tree | **WP0 landed (heavy work, not a refresh).** Added `scripts/bab_research_sweep.py`, wrote `sweep.json` (80 rows, sha `ffb98c33…`) and `sweep.md` (sha `d12e3ba1…`), added `tests/test_bab_p20_research_sweep.py` (10 tests). Sweep runs in 0.78 s; default row matches certified baseline. Re-routed to WP3 (primary) + WP5 (secondary). | ruff PASS; quick GREEN; reconcile GREEN; full gate **GREEN 6499 passed / 35 skipped / 100% (6644/6644)** (134.25 s) |
| 2026-11-18T21:28:21Z | 0452bd1 | Handoff re-certification (documentation only). Corrected stale git-state. | ruff PASS; quick GREEN; baseline `0.7057 -0.725 0.059` |
| 2026-11-18T21:18:00Z | 7637fba | Handoff refresh (documentation only). Added artifact-based routing, de-collided WP5, added JSON schemas for WP4. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.4 s) |
| 2026-11-18T20:30:00Z | c565844 +1 | **WP2b landed.** Leg-beta floor + gross cap; rank fixture book 25 active / gross 51.09 → 0 active / gross 0.0. | ruff PASS; quick GREEN; full gate 6489/35/100% (129.8 s) |
| ≤2026-11-18T18:33:27Z | 33b84e2 | **WP1 landed.** Beta-neutral default, frozen-per-window hold, 17-test acceptance file, fidelity doc, README corrections, `--no-beta-neutral`. | 6462/35/100% after repair |
| ≤2026-11-18T14:19:40Z | f98eaa1 | **Opened P20.** Certified baseline; measured default-book beta −0.572 / −0.908. | GREEN 6445/35/100% |

---

## Proven closed (do not re-test, do not reopen)

P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP3 (walk-forward with train-only selection + anti-lookahead guards + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.