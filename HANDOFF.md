# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-18T22:36:59Z
- **Git state:** `main`. Parent HEAD was `5299dbb`; this session's commit lands WP5. Certify with `git log --oneline -3 && git status --short`.
- **P20 WP0 is COMPLETE AND CERTIFIED** (script + `research_state/bab_p20/sweep.json` + `sweep.md` + 10-test acceptance file). 80 rows, equal-weight only, runtime 0.78 s, full gate green.
- **P20 WP3 is COMPLETE AND CERTIFIED** (script + `walk_forward.json` + `walk_forward.md` + 10-test acceptance file). 5 folds × 40 OOS rows, train-only selection, anti-lookahead guards, byte-identical reruns.
- **P20 WP5 is COMPLETE AND CERTIFIED** (script + `breakeven.json` + `breakeven.md` + 15-test acceptance file). 10 equal-weight beta-neutral rows, fixed 6-iteration bisection over `tc ∈ [0, 0.01]`, runtime 1.2 s, byte-identical reruns, json sha `6016abdb…`.
- **P20 WP4 is now the ONLY REMAINING WORK PACKAGE and is UNBLOCKED** (WP0 + WP3 + WP5 artifacts all committed).
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral BAB trading system.
- **P19 CLOSED.** Never reopen.

**Handoff reviewed and confirmed as the single durable handoff. The binding initial task message below is the most relevant, timestamped, clear directive for the next agentic work session, prioritized based on the repository name and current campaign state. Two WP5 specification defects were measured and removed (see "Bottlenecks removed"): the cross-row monotonicity criterion was mathematically false and one configuration is censored at the search ceiling. The next focus campaign (WP4) is unblocked and must be executed with heavy work — no documentation-only turns.**

---

# INITIAL TASK MESSAGE (BINDING — START HERE)

**Timestamp:** 2026-11-18T22:36:59Z · **Campaign:** P20 — "Prove this repo is actually Betting Against Beta" · **Lane:** C · **WP:** **WP4 — honest reporting + provenance (merge point)**

**One-sentence objective:** write `docs/BAB_RESEARCH_REPORT.md` that reports the committed P20 evidence — provenance, in-sample vs walk-forward OOS, costs, break-even, explicit conclusion, "What this does NOT prove" — with `tests/test_bab_p20_report_consistency.py` proving mechanically that **100% of published numbers are parsed out of the markdown tables and equal their committed JSON fields**, that the rank-not-evaluable statement is present, and that no rank performance number appears.

**Why this and nothing else:** WP0, WP3 and WP5 are landed and certified; WP4 is the last open row and the campaign merge point. It consumes committed JSON only — it must never re-run a harness or retype a number. Without it, P20 has evidence but no honest published conclusion, and done-check items 5 and 8 stay red.

**Prioritization basis:** The repository name `Crypto-Betting-Against-Beta` identifies a crypto market-neutral BAB trading system. P20 exists to prove the repo actually implements BAB rather than a dollar-neutral long/short book. That proof is worthless if it is not published honestly and machine-checked: the fixture is a synthetic random walk, in-sample grid winners are not OOS evidence, and rank mode is not empirically evaluable on 9 assets. WP4 is the only remaining critical-path item; every other lane is closed or complete.

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
| `scripts/bab_breakeven.py` | WP5 | **DONE — committed** |
| `docs/BAB_RESEARCH_REPORT.md` | **WP4** | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` |

Rules:
1. Never take a WP whose deliverable script already exists (`git ls-files`, or on disk and passing its test). Commit an uncommitted WP first, verify it, then take the next missing one.
2. Solo default: **WP4**. It is the only open row.
3. A partially finished WP is not locked. If files exist only in working tree (not `git ls-files`) or gate is red, you own finishing it.
4. Everything blocked? Repair the red gate first (`bash scripts/bab_quick.sh`), then take the first missing row.
5. Never end a session with prose. A landed WP = deliverable + consistency test in **one** commit + green full gate.
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
4. Read `research_state/bab_p20/breakeven.json`, `research_state/bab_p20/sweep.json`, `research_state/bab_p20/walk_forward.json` (schemas, provenance, every numeric field you will publish), `scripts/bab_breakeven.py` for the artifact style (`json.dumps(..., indent=2, sort_keys=True)`, 6-dp rounding, pure `build_*` + `main()` writes), and `docs/BAB_FIDELITY.md` §9.1. WP4 reads JSON only — **never re-run a harness to produce a report number**.

---

## WP4 — Honest reporting + provenance (SPECIFICATION — the only open row)

### A. Deliverable — `docs/BAB_RESEARCH_REPORT.md`

Write the report from the three committed JSON artifacts. Sections, in order:

1. **Provenance.** Fixture path, sha256, 399 price rows → 398 return rows, 2021-01-04 → 2022-07-15, fixed seed `20261028`, deliberate gap `2021-09-17`, all-NaN `DEL`, and the sentence that it is a **deterministic synthetic random walk, not real market data**. Copy facts from `provenance`; do not retype from this file.
2. **What the strategy claims.** Beta-neutral BAB construction: rank-free equal weighting, long low-beta / short high-beta, frozen-per-window beta estimates, `max|Σ wᵢβᵢ|` target.
3. **In-sample grid (WP0).** State that the 80-row sweep selects **no winner** and that the shipped default (`w90 q0.3 tc0.001 beta_neutral=True`) is negative on this fixture. Publish only numbers that exist in `sweep.json`.
4. **Out-of-sample walk-forward (WP3).** Train-before-test folds, train-only selection, and the honest OOS result (including "no configuration is a profitable winner" if that is what the JSON says).
5. **Costs and break-even (WP5).** The 6-iteration bisection, which configurations have a defined `break_even_tc`, and which are `None` — split the `None` rows into **non-positive uncosted Sharpe** and **no crossing inside `[0, 0.01]`** using `provenance.null_field_reasons`. Never describe a `None` as a zero break-even.
6. **Conclusion.** Explicit and modest: the repo implements the BAB construction and is beta-neutral by construction; it has **no demonstrated real-world profitability**; the OOS result is the honest verdict, positive or negative.
7. **What this does NOT prove.** Synthetic fixture, one universe, 9 assets, no real data, no live execution, no rank evaluation, single cost model.
8. **§9.1 statement.** Rank mode is **not empirically evaluable** on this universe; no rank Sharpe/wealth may appear as a result.

### B. Test — `tests/test_bab_p20_report_consistency.py`

Must prove, mechanically:
1. **100% number coverage.** Parse every markdown table in the report; each numeric cell must equal a field in the committed JSON at 6 dp. Assert the count of matched numbers equals the count of published numbers — **zero** unmatched.
2. **No hand-typed drift.** Re-derive the tables from JSON in the test (same renderer logic the report describes) and assert set equality of `(config, field, value)` triples; a number present in prose but in no JSON field fails.
3. **Provenance sentence present** and all provenance facts true (`sha256` regex, row counts, dates, seed, gap, `DEL`, `synthetic is True`).
4. **Rank discipline:** the report contains the "not empirically evaluable" statement, and contains **no** rank Sharpe/wealth number (no `rank` row values, no token `rank_min_leg_beta`/`rank_max_gross`).
5. **Null honesty:** every `None` row in `breakeven.json` is described in the report with its documented reason, and nothing is published as a zero break-even.
6. **No harness re-execution:** the test must not call `build_sweep`, `build_walk_forward`, or `build_breakeven`; it reads JSON + markdown only (assert by import inspection or by runtime under 2 s).

### C. Scope boundaries
- Own **only** `docs/BAB_RESEARCH_REPORT.md` and `tests/test_bab_p20_report_consistency.py` (+ this `HANDOFF.md`).
- Do **not** edit any script, product code, JSON artifact, or fixture. Do not add rank. Do not claim profitability. Do not create a second handoff doc.

### D. Commit rule
**One commit:** `docs/BAB_RESEARCH_REPORT.md` + `tests/test_bab_p20_report_consistency.py` + this `HANDOFF.md` + the ledger row. A report-only commit is a failed session. Never hand off mid-gate and never leave the tree red.

---

## WP5 — LANDED RESULT (do not rebuild; consume for WP4)

`scripts/bab_breakeven.py` (pure `build_breakeven`, `bisect_break_even`, `render_markdown`, `write_artifacts`, `main`), `research_state/bab_p20/breakeven.json` (schema `bab_p20.breakeven/1`, 10 rows, sha `6016abdb…`), `breakeven.md` (rendered from the dict), `tests/test_bab_p20_breakeven.py` (15 tests). Runtime 1.2 s.

| Config (beta_neutral=True, equal) | uncosted Sharpe | break_even_tc | sharpe at break-even | status |
|---|---|---|---|---|
| w30 q0.2 | 0.435796 | 0.001016 | +0.005617 | defined |
| w30 q0.3 | −0.124867 | `None` | — | non-positive uncosted Sharpe |
| w60 q0.2 | 0.834694 | 0.004609 | −0.012656 | defined |
| w60 q0.3 | −1.555531 | `None` | — | non-positive uncosted Sharpe |
| w90 q0.2 | 0.810267 | 0.005078 | −0.008667 | defined |
| w90 q0.3 | −0.467052 | `None` | — | non-positive uncosted Sharpe |
| w120 q0.2 | 0.878289 | 0.006172 | −0.007735 | defined |
| w120 q0.3 | 0.546804 | 0.003516 | −0.007858 | defined |
| w180 q0.2 | 1.216780 | `None` | — | **censored**: Sharpe still positive at `tc=0.01` |
| w180 q0.3 | 0.146479 | 0.001328 | +0.001227 | defined |

Read these from `breakeven.json` in WP4; the table above is a map, not a source.

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
- Full-gate baseline at HEAD: **6524 passed / 35 skipped / TOTAL 100% (6644/6644)**, 139.79 s. It may only grow.
- `pytest --cov` in ad-hoc invocations can raise `ImportError: cannot load module more than once per process`; certify coverage with `scripts/bab_gate.sh`, never hand-rolled `--cov`.
- `research_state/bab_p20/` holds the committed WP0, WP3 and WP5 artifacts (`sweep.{json,md}`, `walk_forward.{json,md}`, `breakeven.{json,md}`). `scripts` is an importable package (`scripts/__init__.py`) — tests import `from scripts import bab_research_sweep, bab_walk_forward, bab_breakeven`.

---

## Campaign P20 map — lanes, status, file ownership

One session owns exactly one WP for its turn. Two sessions must never take the same WP; **the committed deliverable files are the claim.**

| Lane | WPs in order | Owned files | Status |
|---|---|---|---|
| **A — Research/evaluation** | WP0 ✅ → WP3 ✅ → WP5 ✅ | `scripts/bab_research_sweep.py`, `scripts/bab_walk_forward.py`, `scripts/bab_breakeven.py`, `research_state/bab_p20/**`, `tests/test_bab_p20_research_sweep.py`, `tests/test_bab_p20_walk_forward.py`, `tests/test_bab_p20_breakeven.py` | **closed** |
| **C — Reporting/consistency** | **WP4** | `docs/BAB_RESEARCH_REPORT.md`, `tests/test_bab_p20_report_consistency.py` | **UNBLOCKED — the only open WP** |
| **B — Strategy fidelity** | WP1 ✅, WP2 ✅, WP2b ✅ | `config.py`, `portfolio.py`, `strategy.py`, `docs/BAB_FIDELITY.md`, `tests/test_bab_p20_rank_weighting.py` | **closed** |

Rules: Lane A never edits product code; Lane B never edits research scripts or `research_state/`; Lane C edits docs + its consistency test only and reads JSON read-only. **Solo default: WP4.** All published numbers must be `weighting="equal"`.

### WP4 — Honest reporting + provenance (merge point)
Full specification is in the binding initial task message above (sections A–D). Short form: report must state fixture provenance (deterministic random walk, fixed seed, deliberate gap, NaN column), in-sample vs OOS distinction, cost assumptions and the WP5 break-even result including its four `None` rows, explicit conclusion, a "What this does NOT prove" section, and the §9.1 statement that rank mode is **not empirically evaluable** (no rank performance numbers as results). Consume committed JSON only; do not re-run harnesses. **Acceptance:** `tests/test_bab_p20_report_consistency.py` parses every markdown table and matches **100%** of published numbers to JSON fields. Do **not** rename fixture files.

---

## Campaign P20 done-check (all must hold)

1. Default-config book: `max|Σ wᵢβᵢ| ≤ 1e-3` (daily, 6 grid points), `|realized β| ≤ 0.15` grid-wide (`≤0.07` at `w∈{90,120}`), committed test, weekly/monthly invariance, explicit opt-out byte-identical. **DONE (WP1).**
2. `weighting="rank"` exists, is opt-in, matches the hand weights to `1e-12`, unit-beta legs, zero total beta on rebalance rows, equal path byte-identical, no-lookahead proof. **DONE (WP2).**
3. Rank path is **numerically bounded**: leg-beta floor + gross cap flatten pathological rows, hand example unchanged, wide-universe proof, fixture-flat documented. **DONE (WP2b).**
4. `scripts/bab_research_sweep.py` exists and is deterministic (hash-equal reruns), JSON artifact committed under `research_state/bab_p20/`. **DONE (WP0).** Walk-forward **DONE (WP3)**; cost/break-even harness **DONE (WP5)** — 10 rows, 6 fixed bisection iterations, hash-equal reruns.
5. `docs/BAB_RESEARCH_REPORT.md` exists; **100%** of published numbers machine-checked against committed JSON; no rank performance claim. **WP4 — the only open item.**
6. All `tests/test_bab_p20_*.py` pass; no existing test deleted/skipped/`xfail`-ed/weakened; coverage **100%** (6524/35 may only grow). **Every WP re-certifies.**
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

**Hard minimums that make a WP impossible to fake:** WP0 `= 80 rows` (landed); WP3 `= 5 folds × ≥40 OOS rows` + train-before-test + lookahead-trap + selection-independence proof (landed); WP5 `= 6 fixed bisection iterations per row, 10 rows, 15 tests` (landed); **WP4 `= 100%` of published numbers matched to JSON, zero unmatched, no harness re-run.** If you are writing prose instead of a test, you are avoiding the work — stop and take the next routing row.

## No-idle ladder (if the assigned WP is blocked, do the next rung — never end a session empty-handed)

1. WP4 number-matching feels hard? It is table parsing, not research: read each JSON row, build `{(config, field): rounded_value}`, regex every markdown table cell, assert membership for **all** cells. Start with `sweep.json` (80 rows) — it is the bulk.
2. Blocked on report structure? Write sections 1, 3, 4, 5 as pure table renderers from JSON first; prose after the tables match. Prose that quotes a number must quote a matched table cell.
3. Blocked on the four `None` break-even rows? Use `provenance.null_field_reasons` from `breakeven.json`: three are non-positive uncosted Sharpe, one (`w180 q0.2`) is censored because Sharpe stays positive at `tc=0.01`. Never write "zero break-even".
4. Blocked on WP4 for any other reason? Commit the consistency test **plus** the sections it already proves — a tested slice with the exact remainder in the ledger row is a valid session.
5. Blocked on everything? Repair the gate and add one missing test in a P20 test file (e.g. tighten the WP5 bracket assertion). Something landable always exists.

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
- Editing any `scripts/bab_*.py` research harness or any `research_state/` artifact from WP4 (cross-lane collision), or re-running a harness from the report generator instead of reading its JSON.
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, type-annotation/style churn, broad refactors, network fetching, committing probe/debug scratch scripts, or creating parallel handoff docs.

---

## Bottlenecks removed (do not re-create)

- **[REMOVED 2026-11-18T22:36:59Z] WP5's "cross-row monotonicity" acceptance criterion was mathematically false.** Cost drag is `tc * turnover` and turnover varies by configuration, so a higher uncosted Sharpe can break even sooner. Measured fixture counterexample: `(w60,q0.2)` Sharpe `0.834694` / break-even `0.004609` beats `(w90,q0.2)` Sharpe `0.810267` / break-even `0.005078`. A literal implementation of that test fails, so any agent following it would loop or weaken the test. Replaced with the provable per-row law: **costed Sharpe is non-increasing in `tc` for a fixed configuration**, asserted across a 5-point ladder on all 10 rows.
- **[REMOVED 2026-11-18T22:36:59Z] WP5's `[0, 0.01]` search range censors the best configuration.** `w180 q0.2` keeps a positive Sharpe (`+0.4397`) at `tc=0.01`, so no crossing exists in range. The harness reports `break_even_tc: null` with a documented `REASON_NO_CROSSING` instead of publishing the meaningless bisection midpoint `0.009922` as a break-even. WP4 must report this as censored, not as a zero.
- **[REMOVED 2026-11-18T22:36:59Z] Three configurations have non-positive uncosted Sharpe** (`w30 q0.3`, `w60 q0.3`, `w90 q0.3`), so a "break-even cost" does not exist for them. `break_even_tc` is `null` with `REASON_NON_POSITIVE`; the report must not imply any cost tolerance.
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
| 2026-11-18T22:36:59Z | `5299dbb` + working tree | **WP5 landed (heavy work, not a refresh).** Added `scripts/bab_breakeven.py` (pure `build_breakeven`, `bisect_break_even` with a 6-step trace, `render_markdown`, `write_artifacts`, `main`), wrote `breakeven.json` (10 rows, sha `6016abdb…`) and `breakeven.md`, added `tests/test_bab_p20_breakeven.py` (15 tests). Measured and removed two impossible spec criteria (cross-row monotonicity; censored range ceiling). Re-routed to **WP4, the only open row**. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full gate **GREEN 6524 passed / 35 skipped / 100% (6644/6644)** (139.79 s) |
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

P19-7 (222 broad/bare `except` handlers annotated, 0 unannotated), P19-2/3/4, P17-1/2, P18-1/2/3, kill-switch R4-B, bootstrap, reconciliation R5-B/R5-C, live-adapter two-key safety, 100% line coverage of `strategies/betting_against_beta`, Milestones 1–5 hygiene, **P20 WP0 (deterministic 80-row equal-weight sweep + hash-pinned artifacts + 10-test acceptance file)**, **P20 WP3 (walk-forward with train-only selection + anti-lookahead guards + 10-test acceptance file)**, **P20 WP1 (beta-neutral default + frozen rebalance windows + fidelity doc + README correction)**, **P20 WP2 algebra (rank construction, exact 4-asset hand example, no-lookahead, equal-path byte-identity)**, **P20 WP2b (rank leg-beta floor + gross cap + wide-universe proof + fixture-flat scope)**, **P20 WP5 (10-row break-even bisection, 6 fixed iterations, 15-test acceptance file, censoring and non-positive rows reported as documented nulls)**. `scripts/bab_except_inventory.py` is retained as a read-only audit tool; running it is not a deliverable.