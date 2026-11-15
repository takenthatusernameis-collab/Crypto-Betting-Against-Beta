# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T20:47:00Z (this refresh)
- **Prior refresh:** 2026-11-15T20:05:00Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research → backtest → execution/ops)
- **Git HEAD (verified this refresh):** `63cdecb` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean (`git status --short` empty). P14 seed test `tests/test_bab_p15_hard_lines_coverage.py` is new but uncommitted — do not reset history; commit only when explicitly asked.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5` after bootstrap; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt installed via `bash scripts/bab_bootstrap.sh` (supported bootstrap called by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T20:47:00Z) — BINDING (DO NOT IGNORE)

**Campaign: P15 — Zero-Miss Hardening & Determinism Lock (the only active campaign).** Goal: eliminate the remaining 99 missed statements (TOTAL 99% → 100%) across `beta`/`cli`/`data_loader`/`data_sources`/`execution`/`metrics`/`portfolio`/`reconciliation`/`replay`/`signals`, holding `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` green at every step (target TOTAL 100%, floor 98.5% must never drop), ruff clean, quick green, perf baseline within tolerance. Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default. Fakes/mocks only — no network, no credentials, no live execution. Every session must produce concrete progress: new passing P15 test(s) and/or a production bug fix with regression — never a handoff-only turn.

**Status this refresh (2026-11-15T20:47:00Z, HEAD 63cdecb):**
- P14 **COMPLETE** (P14-0 → P14-E all done). Gate GREEN: **6133 passed, 35 skipped, 0 failed, 394.46s, TOTAL 99% (99 missed / 6658)**, ruff clean, **floor 98.5% MET**.
- `bash scripts/bab_quick.sh` → **PASS** (`== quick preflight OK ==`: ruff clean, targeted trio 104 passed, smoke 195 passed).
- Controller tests: **125 passed**. Perf `python3 scripts/perf_baseline.py --check`: **failures: []**.
- P15 seed file `tests/test_bab_p15_hard_lines_coverage.py` created (3 tests pass); metrics line 94 and data_sources tz-coverable branches confirmed executable but coverage attribution did not flip them — hard-line triage pending.
- **Remaining 99 misses:** `beta.py` 14 (125, 150-151, 163, 170-171, 189, 435-436, 552-556); `cli.py` 7 (589-590, 746-748, 803-804); `data_loader.py` 43; `data_sources.py` 6 (480-481, 499-500, 507-508); `execution.py` 11 (139-141, 182-185, 555-556, 1287-1288); `metrics.py` 1 (94); `portfolio.py` 11 (152-153, 170-177, 180); `reconciliation.py` 3 (82-83, 309); `replay.py` 1 (172); `signals.py` 2 (37, 75).

**Next binding work (in order):**
1. **P15-1 triage:** classify each of the 99 misses as coverable (write a targeted test) vs dead (document rationale, do not chase). Module order: `beta` → `data_loader` → `execution` → `portfolio` → `cli` → `data_sources` → `reconciliation` → `replay` → `signals` → `metrics`. Extend `tests/test_bab_p15_hard_lines_coverage.py` (or per-module P15 files); fakes/mocks only.
2. **P15-2:** Re-run full gate after each test batch; require TOTAL >= 98.5% (floor) at all times, target 100%. Record exact TOTAL/pass/fail/skip in the ledger. Repeat P15-1 → P15-2 until TOTAL 100% (or all coverable lines done and residue documented dead).
3. **P15-3:** Perf guard — `python3 scripts/perf_baseline.py --check` within tolerance; rerun once if noisy before treating as regression.
4. **P15-4:** Controller/ops hardening — diagnostics scanner, campaign resume, nonfinite serialization edge cases; add regression tests.
5. **P15-5:** Refresh this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and start P16 on the next lowest-coverage module. Do not stop at "campaign complete".

**Priority (execute in order):**
1. **P15 hard-line triage + tests** (beta, data_loader, execution, portfolio, cli, data_sources, reconciliation, replay, signals, metrics) — TOTAL → 100%.
2. **Gate green at 100% TOTAL** (floor 98.5% invariant).
3. **Perf + controller hardening.**
4. **Handoff refresh → P16.**

## Verified state (2026-11-15T20:47:00Z, this session)

- `bash scripts/bab_quick.sh` → **PASS**. HEAD `63cdecb`, clean tracked tree.
- `python3 -m ruff check .` → **clean**.
- Last full gate (this session): `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` → **6133 passed, 35 skipped, 0 failed, 394.46s, TOTAL 99% (99 missed / 6658)**, ruff clean, **floor 98.5% MET**.
- Gate-context per-file coverage (this full gate):
  - `backtest.py` 100% (0 miss); `attribution.py` 100%; `config.py` 100%; `costs.py` 100%; `data.py` 100%; `errors.py` 100%; `quality.py` 100%; `regime.py` 100%; `risk.py` 100%; `shorting.py` 100%; `sizing.py` 100%; `strategy.py` 100%
  - `beta.py` 96% (14 miss); `cli.py` 99% (7 miss); `data_loader.py` 98% (43 miss); `data_sources.py` 98% (6 miss); `execution.py` 99% (11 miss); `metrics.py` 99% (1 miss); `portfolio.py` 95% (11 miss); `reconciliation.py` 98% (3 miss); `replay.py` 99% (1 miss); `signals.py` 98% (2 miss)
  - **TOTAL: 99% (99 miss) — floor 98.5% MET (target 100%)**
- Controller: 125 passed. Perf `--check`: failures: [].

## Session output contract (binding)

A session that only edits this file is a **FAILED session**. Before finishing, ALL must hold:
1. At least one new/extended P15 test file passes (or a production bug fixed with a new regression test). ✅ this session (`tests/test_bab_p15_hard_lines_coverage.py`, 3 passed).
2. `python3 -m ruff check .` is clean. ✅
3. `bash scripts/bab_quick.sh` is green. ✅
4. Run `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` and record exact TOTAL, pass/fail/skip counts, and remaining gap in the ledger. ✅ recorded (TOTAL 99%, 99 miss, floor met; gap to 100% = 99).
5. P15 ledger below has a new row with exact command evidence.
6. If all P15 steps done, start P16; do not stop at "campaign complete".

## Hard rules
- Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default.
- No real live execution, no network, no credentials in tests.
- Prefer small tested diffs. Do not change production logic unless a new failing test proves a bug.
- Do not re-litigate P12: `strategy.py` is 100% covered.
- Single durable handoff: only `HANDOFF.md` canonical; keep `AGENT_HANDOFF.md` pointer-only.
- Preserve local commits/work; do not reset or rewrite history.
- Tool hygiene: if `edit` fails, retry with smaller unique `oldString`; after two failures use `write`. Do not repeat malformed calls.
- Full gate ~7 min; timeout is not a test failure — rerun. Perf can be noisy; rerun `perf_baseline.py --check` once before treating as regression. `BAB_GATE_SERIAL=1` only for diagnosis.
- Parallel-safety: preserve `_*_cell_record`/deterministic recompute patterns.

## P15 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P15-0 | Seed hard-line triage file | `tests/test_bab_p15_hard_lines_coverage.py` | [x] | 2026-11-15T20:47:00Z: file created, 3 tests pass, ruff clean, quick PASS. |
| P15-1 | Triage 99 misses coverable vs dead (beta → data_loader → execution → portfolio → cli → data_sources → reconciliation → replay → signals → metrics) | `tests/test_bab_p15_hard_lines_coverage.py` (+ per-module P15 files as needed) | [ ] | Gate TOTAL 99% (99 miss). Next: write targeted tests per coverable line. |
| P15-2 | Gate green, TOTAL → 100% (floor 98.5% invariant) | — | [ ] | Requires full gate after each test batch; record exact TOTAL/pass/fail/skip. |
| P15-3 | Perf within tolerance | — | [ ] | `python3 scripts/perf_baseline.py --check` failures: [] (baseline). |
| P15-4 | Controller/ops hardening + regression tests | — | [ ] | Diagnostics scanner, campaign resume, nonfinite serialization. |
| P15-5 | Handoff refresh → P16 | — | [ ] | Refresh this file; start P16. Do not stop at "campaign complete". |

## Coverage notes (this full gate baseline: 6133p/35s/0f, TOTAL 99%, 99 missed — 2026-11-15T20:47:00Z, HEAD 63cdecb)
- `beta.py` 14 miss assessed likely-dead/hard (P14-C): `BABDataError` subclasses `ValueError` and is swallowed by the earlier handler; `_finalize_betas` always invoked 2-D; `to_numpy`/`asarray` inner except reachable only if single-key access fails. Triage in P15-1.
- `reconciliation.py` 82-83 (`except ImportError: pass`, numpy always importable → dead) and 309 (empty-columns early-return → line not reached) likely dead.
- `replay.py` 172 (row-resize branch) likely unreachable via normal DataFrame path → dead candidate.
- `signals.py` 37 (object-dtype after `to_numeric` coerce → rare) / 75 (`n == 0` unreachable since empty `clean` returns None earlier) dead candidates.
- `metrics.py` 94 (`turnover` NaN-mean → 0.0) executable but coverage attribution did not flip; re-verify in P15-1.
- `cli.py` 589-590, 746-748, 803-804 and `data_loader.py` 43 / `data_sources.py` 6 / `execution.py` 11 / `portfolio.py` 11: coverable-edge candidates for P15-1.
- TOTAL floor governs: do not block on dead lines; P15-1 decides coverable vs dead.

## Known environment/ops bottlenecks (removed or constrained — do not reopen)
- Missing deps: use `scripts/bab_bootstrap.sh` / quick/gate (verified this session).
- Edit-tool loops: after 2 failures use `write`.
- Gate/perf flakiness: full gate ~7 min, timeout not failure; rerun once. `BAB_GATE_SERIAL=1` only for diagnosis.
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
3. Execute P15 **1 → 2 → 3 → 4 → 5** top-down with minimal tested diffs; extend/create only named P15 files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run applicable P15 verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and keep `AGENT_HANDOFF.md` pointer-only. A handoff-only session is a **FAILED session**.
