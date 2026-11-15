# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T20:05:00Z (this refresh)
- **Prior refresh:** 2026-11-15T19:49:12Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research → backtest → execution/ops)
- **Git HEAD (verified this refresh):** `42ff06a` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean tracked state EXCEPT one new untracked file `tests/test_bab_beta_backtest_p14_coverage.py` (P14-C). Verify with `git status --short` and `git log -1 --oneline` before acting.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5` after bootstrap; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt installed via `bash scripts/bab_bootstrap.sh` (supported bootstrap called by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T20:05:00Z) — BINDING (DO NOT IGNORE)

**Campaign: P14 — Zero-Excuse Coverage & Safety Push (the only active campaign).** Goal: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` green (TOTAL >= 98.5%, i.e. <= 99 missed / 6658 stmts), ruff clean, quick preflight green. Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default. Fakes/mocks only — no network, no credentials, no live execution. Every session must produce concrete progress: new passing P14 test(s) and/or a production bug fix with regression — never a handoff-only turn.

**Status this refresh (2026-11-15T20:05:00Z, HEAD 42ff06a):**
- `bash scripts/bab_quick.sh` → **PASS** (`== quick preflight OK ==`: ruff clean, targeted trio 104 passed, smoke 195 passed).
- `python3 -m ruff check .` → **clean**.
- Full gate `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` → **6108 passed, 35 skipped, 0 failed, 415.47s, TOTAL 98% (132 missed / 6658)**, ruff clean, **floor 98.5% NOT MET** (gap = 33 more statements to reach <= 99 missed). Log preserved at `/tmp/bab_gate_p14c.log`.
- **P14-C `beta.py` + `backtest.py`:** `tests/test_bab_beta_backtest_p14_coverage.py` created (5 tests, all pass).
  - `backtest.py`: **144 stmts, 0 miss, 100%** — P14-C backtest target **MET** (covered 17-21, 163).
  - `beta.py`: **393 stmts, 14 miss, 96%** — covered 14 of 28 reachable (216-219, 544-551, 557-558). Remaining 14 missed: 125, 150-151, 163, 170-171, 189, 435-436 (9 lines assessed likely-dead/unreachable under normal inputs: `BABDataError` subclasses `ValueError` and is swallowed by the earlier handler; `_finalize_betas` always invoked 2-D) + 552-556 (inner `to_numpy`/`asarray` except, reachable only if single-key access fails). **Do not block on dead lines; TOTAL floor governs.**
- **TOTAL 98% (132 missed). Need <= 99 missed.** P14-D (42 missed across replay/portfolio/reconciliation/risk) is the highest-leverage next step.

**Next binding work (in order):**
1. **P14-D:** Create `tests/test_bab_ops_safety_p14_coverage.py` targeting each module to **>= 98%**:
   - `replay.py` (92%, 11 miss: 172, 174, 205, 218-219, 234, 247-251)
   - `portfolio.py` (95%, 11 miss: 152-153, 170-177, 180)
   - `reconciliation.py` (95%, 10 miss: 78-79, 82-83, 112-113, 309, 377, 381, 385)
   - `risk.py` (96%, 10 miss: 245, 326-328, 347, 353, 356, 566-568)
   Pattern: follow `test_bab_execution_p14_coverage.py` / `test_bab_data_loader_p14_coverage.py` style; fakes/mocks only.
2. Re-run `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` (600000 ms timeout; rerun once if noisy) and record exact TOTAL/pass/fail/skip in the ledger. Repeat P14-D → gate until TOTAL >= 98.5%.
3. **P14-E:** Once gate green, run perf `python3 scripts/perf_baseline.py --check` (rerun once if noisy), paper + live dry-run smokes, controller tests, then refresh this file (timestamp, HEAD/tree, verified state, coverage table/ledger) and start P15 on the next lowest-coverage module.

## Priority (execute in order)

1. **P14-C `beta.py` + `backtest.py`** — `tests/test_bab_beta_backtest_p14_coverage.py` created; backtest 100% done; beta 96% (14 likely-dead/hard remain). **IN PROGRESS.**
2. **P14-D `replay.py` + `portfolio.py` + `reconciliation.py` + `risk.py`** (42 missed combined): create `tests/test_bab_ops_safety_p14_coverage.py`, each >= 98%. **NEXT.**
3. **P14-A `data_loader.py`** (44 missed): extend `tests/test_bab_data_loader_p14_coverage.py`; `data_loader < 99%` acceptable only if **TOTAL >= 98.5%**.
4. **P14-E verification + handoff refresh:** full gate green at 98.5%, perf, smokes, controller tests, refresh this file.

## Verified state (2026-11-15T20:05:00Z, this session)

- `bash scripts/bab_quick.sh` → **PASS**. HEAD `42ff06a`, clean tracked tree at start (plus new untracked P14-C test file).
- `python3 -m ruff check .` → **clean**.
- Last full gate (this session): `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` → **6108 passed, 35 skipped, 0 failed, 415.47s, TOTAL 98% (132 missed / 6658)**, ruff clean, **floor 98.5% NOT MET**.
- Gate-context per-file coverage (this full gate):
  - `backtest.py`: **100%** (0 miss) — P14-C backtest MET
  - `beta.py`: **96%** (14 miss: 125, 150-151, 163, 170-171, 189, 435-436, 552-556) — P14-C partial
  - `execution.py`: **99%** (11 miss: 139-141, 182-185, 555-556, 1287-1288) — P14-B MET
  - `replay.py`: **92%** (11 miss) — P14-D NEXT
  - `portfolio.py`: **95%** (11 miss) — P14-D
  - `reconciliation.py`: **95%** (10 miss) — P14-D
  - `risk.py`: **96%** (10 miss) — P14-D
  - `data_loader.py`: **98%** (44 miss) — P14-A
  - `cli.py` 99%, `data_sources.py` 98%, `metrics.py` 98%, `signals.py` 98%, `config.py` 99%, others 100%
  - **TOTAL: 98% (132 miss) — floor 98.5% requires <= 99 missed**

## Session output contract (binding)

A session that only edits this file is a **FAILED session**. Before finishing, ALL must hold:
1. At least one new/extended P14 test file passes (or a production bug fixed with a new regression test). ✅ this session (`tests/test_bab_beta_backtest_p14_coverage.py`, 5 passed).
2. `python3 -m ruff check .` is clean. ✅
3. `bash scripts/bab_quick.sh` is green. ✅
4. Run `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` and record exact TOTAL, pass/fail/skip counts, and remaining gap in the ledger. A TOTAL below 98.5% is expected until P14 completes — record it and continue to the next unblocked step in the same session when feasible. ✅ recorded (TOTAL 98%, 132 miss, gap 33).
5. P14 ledger below has a new row with exact command evidence.
6. If all P14 steps done, start P15; do not stop at "campaign complete".

## Hard rules
- Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default.
- No real live execution, no network, no credentials in tests.
- Prefer small tested diffs. Do not change production logic unless a new failing test proves a bug.
- Do not re-litigate P12: `strategy.py` is 100% covered.
- Single durable handoff: only `HANDOFF.md` canonical; keep `AGENT_HANDOFF.md` pointer-only.
- Preserve local commits/work; do not reset or rewrite history.
- Tool hygiene: if `edit` fails, retry with smaller unique `oldString`; after two failures use `write`. Do not repeat malformed calls.
- Full gate ~8-9 min; timeout is not a test failure — rerun. Perf can be noisy; rerun `perf_baseline.py --check` once before treating as regression.

## P14 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P14-0 | Baseline quick green | — | [x] | 2026-11-15T19:47:04Z: `bash scripts/bab_quick.sh` PASS. HEAD `d8a8467`, clean tree. |
| P14-A | `data_loader.py` coverable gaps (TOTAL floor governs) | `tests/test_bab_data_loader_p14_coverage.py` | [~] | File exists (33 tests). Extend for remaining coverable lines or accept if TOTAL >= 98.5%. |
| P14-B | `execution.py` >= 98% | `tests/test_bab_execution_p14_coverage.py` | [x] | Gate: **99%** (11 miss). P14-B COMPLETE. |
| P14-C | `beta.py` >= 98%, `backtest.py` >= 98% | `tests/test_bab_beta_backtest_p14_coverage.py` | [~] | 2026-11-15T20:05:00Z: file created, 5 tests pass. backtest **100%** (0 miss) MET. beta **96%** (14 miss; 9 likely-dead + 552-556 hard). TOTAL 98% (132 miss), floor NOT MET. |
| P14-D | replay/portfolio/reconciliation/risk >= 98% | `tests/test_bab_ops_safety_p14_coverage.py` | [ ] | 42 missed combined. NEXT — create test file targeting missed lines. |
| P14-E | TOTAL >= 98.5%, gate green, handoff refreshed | — | [ ] | Requires full gate/perf/smokes/controller tests with exact evidence. |

## Coverage notes (this full gate baseline: 6108p/35s/0f, TOTAL 98%, 132 missed — 2026-11-15T20:05:00Z, HEAD 42ff06a)
- P14-C covered backtest 17-21, 163 and beta 216-219, 544-551, 557-558 (14 statements). beta remaining 125, 150-151, 163, 170-171, 189, 435-436, 552-556 assessed likely-dead/hard; TOTAL floor governs.
- No gate rerun yet this refresh beyond the one above.

## Known environment/ops bottlenecks (removed or constrained — do not reopen)
- Missing deps: use `scripts/bab_bootstrap.sh` / quick/gate (verified this session).
- Edit-tool loops: after 2 failures use `write`.
- Gate/perf flakiness: full gate ~8-9 min, timeout not failure; rerun once. `BAB_GATE_SERIAL=1` only for diagnosis.
- Parallel-safety: preserve `_*_cell_record`/deterministic recompute patterns.
- Safety: no real live trading, no network, no credentials in tests. Live adapter dry-run/health-check only.
- Stale diagnostics artifacts: `research_state/workflow_run_diagnostics.jsonl` appended by CI/checkpoint commits — informational only, do not treat as blockers.

## Verification commands (canonical)
- Quick: `bash scripts/bab_quick.sh`
- Gate: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`
- Controller: `python3 -m pytest -q tests/test_controller_progress_accounting.py tests/test_workflow_diagnostics_scanner.py tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py`
- Perf: `python3 scripts/perf_baseline.py --check`
- Paper smoke: `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC`
- Live dry-run: `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check`

## Protocol
1. Read this file and `AGENT_HANDOFF.md` (pointer only).
2. Run quick preflight; fix red state before feature work.
3. Execute P14 **C → D → A** top-down with minimal tested diffs; extend/create only named P14 files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run applicable P14-E verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and keep `AGENT_HANDOFF.md` pointer-only. A handoff-only session is a **FAILED session**.
