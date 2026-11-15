# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T18:21:17Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research → backtest → execution/ops)
- **Git HEAD (verified this refresh):** `e920185` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** clean at this refresh (no uncommitted source changes). Verify with `git status --short` and `git log -1 --oneline` before acting; do not trust a stale SHA in this file if it diverges.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt expected installed. `bash scripts/bab_bootstrap.sh` is the supported bootstrap (called by quick/gate).
- **Latest verified evidence (from prior recorded session, re-verify before extending):** quick preflight green (ruff clean, targeted trio 104 passed, smoke 195 passed). Last recorded full gate: **6071 passed, 35 skipped, 0 failed, 501.15s, TOTAL 97% (201 missed)**, ruff clean, `strategy.py` 100%, `BAB_GATE_MIN_COVERAGE=98.5` **NOT met**. Controller tests 125 passed. Perf `failures: []`. Paper + live dry-run smokes passed (see commands below). **Do not treat these as current if HEAD/tree differs — rerun quick/gate and record exact results.**

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T18:21:17Z) — BINDING (DO NOT IGNORE)

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Execute **P14 — Zero-Excuse Coverage & Safety Push** until the release gate is met. P13 was superseded and never started — **do not create P13 files**. P14 is the **only** active campaign. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no analysis-only ending**.

### Campaign objective (heavy, measurable)
Raise BAB strategy coverage and safety confidence to **TOTAL >= 98.5%** (stretch 99%) with `bash scripts/bab_gate.sh` green and ruff clean, while preserving byte-identical default offline/deterministic behavior and **live dry-run-safe-by-default**. Every session must produce concrete progress: new passing P14 tests and/or a production bug fix with regression — never a handoff-only turn.

### Current bottleneck & priority (based on repo state)
1. **P14-B `execution.py` (FIRST, HEAVY, highest execution-safety risk):** 45 missed branches (adapter rejection/fill/diagnostic/reconciliation, partial-fill/error paths, batching edges, safety guards). Create `tests/test_bab_execution_p14_coverage.py`; target `execution.py` >= 98% (<= 10 missed). Use fakes/mocks only — **no network, no credentials, no real live execution**.
2. **P14-A `data_loader.py` (data-integrity):** dead-code handlers were previously removed; remaining gaps are coverable-by-test. Extend `tests/test_bab_data_loader_p14_coverage.py` for remaining missed lines (dayfirst/unparseable, exchange fallback, all-NaN, pending count, finite-count fallback) where feasible. `data_loader < 99%` is acceptable only if **TOTAL >= 98.5%**; do **not** lower the floor.
3. **P14-C correctness:** `tests/test_bab_beta_backtest_p14_coverage.py` targeting `beta.py` >= 98%, `backtest.py` >= 98% (finite/NaN/window/min-period inputs; prove equivalence to pandas rolling-OLS reference where applicable).
4. **P14-D ops safety residue:** `tests/test_bab_ops_safety_p14_coverage.py` targeting `replay.py`, `portfolio.py`, `reconciliation.py`, `risk.py` each >= 98%.
5. **P14-E verification + handoff refresh:** full gate, perf, smokes, and this file updated with exact evidence.

### P14-B seeds (start here)
`_price_for` Timestamp fallback (139-141); `_adv_for` dict/Series/DataFrame + errors (164-166); `_adv_from_frame_value` Timestamp/Series (177-187); `_date_key`/`_as_timestamp` fallbacks (380-381, 403-404); ADV/date/target coercion (463-480, 505-506); JSON sanitize numpy/non-finite/ImportError (555-560); diagnostics without betas index (783-784); paper PnL bad date/returns (836-848); `LiveFill.to_dict` (1047); `cancel_order`/status dry-run paths (1281-1288); API password env (1380-1381); idempotent connect (1386). Confirm actual missed lines with a fresh coverage run before/while working.

### First 10 minutes (mandatory)
1. `bash scripts/bab_quick.sh` — must end with `== quick preflight OK ==`. If deps missing, let bootstrap run; do not proceed on a red quick preflight except to fix the break.
2. `git status --short` and `git log -1 --oneline` — record real HEAD/tree.
3. Read this file fully, then start P14-B (or continue the first unblocked P14 step with missing coverage). Do not spend the session re-planning.

### Session output contract (binding)
A session that only edits this file is a **FAILED session**. Before finishing, ALL must hold:
1. At least one new P14 test file (named above) exists and passes, or a production bug is fixed with a new regression test.
2. `python3 -m ruff check .` is clean.
3. `bash scripts/bab_quick.sh` is green.
4. Run `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` (600000 ms timeout or background; rerun once if noisy) and record exact TOTAL, pass/fail/skip counts, and remaining gap in the ledger. A TOTAL below 98.5% is expected until P14 completes — record it and continue to the next unblocked step in the same session when feasible.
5. P14 ledger below has a new row with exact command evidence.
6. If all P14 steps done, start P15 by attacking the next lowest-coverage module from a fresh gate table; do not stop at "campaign complete".

### Hard rules
- Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default.
- No real live execution, no network, no credentials in tests.
- Prefer small tested diffs. Do not change production logic unless a new failing test proves a bug.
- Do not re-litigate P12: `strategy.py` is 100% covered.
- Single durable handoff: only `HANDOFF.md` canonical; keep `AGENT_HANDOFF.md` pointer-only.
- Preserve local commits/work; do not reset or rewrite history.
- Tool hygiene: if `edit` fails with invalid arguments, re-read and retry with a smaller unique `oldString`; after two failures use `write`. Do not repeat a malformed call three times.
- Full gate ~8-9+ min; timeout is not a test failure — rerun. Perf can be noisy; rerun `perf_baseline.py --check` once before treating as regression.

### P14 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P14-0 | Baseline quick green | — | [x] | Prior recorded: quick preflight green (ruff clean, 104 targeted + 195 smoke). Re-verify this session. |
| P14-A | `data_loader.py` coverable gaps (TOTAL floor governs) | `tests/test_bab_data_loader_p14_coverage.py` | [~] | Prior: file exists (33 tests). Dead-code removed in earlier work. Extend for remaining coverable lines or accept if TOTAL >= 98.5%. |
| P14-B | `execution.py` >= 98% | `tests/test_bab_execution_p14_coverage.py` | [ ] | **START/CONTINUE HERE** |
| P14-C | `beta.py` >= 98%, `backtest.py` >= 98% | `tests/test_bab_beta_backtest_p14_coverage.py` | [ ] | |
| P14-D | replay/portfolio/reconciliation/risk >= 98% | `tests/test_bab_ops_safety_p14_coverage.py` | [ ] | |
| P14-E | TOTAL >= 98.5%, gate green, handoff refreshed | — | [ ] | |

### Per-file coverage baseline (stale full gate 6071p/35s/0f, TOTAL 97%, 201 missed — re-measure)

| Module | Cover | Miss | Notes / remaining |
|--------|-------|------|-------------------|
| `__init__, attribution, costs, data, errors, quality, regime, shorting, sizing, strategy` | 100% | 0 | — |
| `execution.py` | 94% | 45 | **P14-B priority** |
| `data_loader.py` | ~97% | ~42 est. | P14-A extendable gaps |
| `beta.py` | 93% | 28 | P14-C |
| `replay.py` | 92% | 11 | P14-D |
| `portfolio.py` | 95% | 11 | P14-D |
| `reconciliation.py` | 95% | 10 | P14-D |
| `risk.py` | 96% | 10 | P14-D |
| `cli.py` | 99% | 7 | — |
| `data_sources.py` | 98% | 7 | — |
| `backtest.py` | 96% | 6 | P14-C |
| `metrics.py` | 98% | 4 | — |
| `signals.py` | 98% | 2 | — |
| `config.py` | 99% | 1 | — |
| **TOTAL** | **97%** | **201** | floor 98.5% required |

### Known environment/ops bottlenecks (removed or constrained — do not reopen)
- **Missing deps in CI-like runs:** prior diagnostics show `ModuleNotFoundError: numpy/ccxt/hypothesis` in some agent runs → tests fail spuriously. Use `scripts/bab_bootstrap.sh` (via quick/gate) or install deps before running tests. Record actual env state.
- **Edit-tool invalid-arg loops:** diagnostics show repeated `edit` tool malformed calls/aborts in prior runs. After 2 failures, switch to `write` with full corrected content for that file.
- **Gate/perf flakiness:** gate timeout (~600s+) and occasional perf noise; rerun once before declaring regression. Use correct CLI flags only (no `--n-days/--csv/--source live/--live-dry-run/--health-check-only`).
- **Parallel gate:** `scripts/bab_gate.sh` uses pytest-xdist/loadscope/sysmon; serial fallback `BAB_GATE_SERIAL=1` or `BAB_GATE_JOBS=N`. Do not make serial-only default.
- **Parallel-safety in tests:** follow `_*_cell_record`/`_*_records_full` and deterministic recompute patterns under worker subsets.
- **Safety:** no real live trading, no network, no credentials in tests. Live adapter dry-run/health-check only.

### Verification commands (canonical)
- Quick: `bash scripts/bab_quick.sh`
- Gate: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`
- Controller: `python3 -m pytest -q tests/test_controller_progress_accounting.py tests/test_workflow_diagnostics_scanner.py tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py`
- Perf: `python3 scripts/perf_baseline.py --check`
- Paper smoke: `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC`
- Live dry-run: `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check`

### Protocol
1. Read this file and `AGENT_HANDOFF.md` (pointer only).
2. Run quick preflight; fix red state before feature work.
3. Execute P14 B → C → D top-down with minimal tested diffs; create only named P14 files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run applicable P14-E verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and keep `AGENT_HANDOFF.md` pointer-only.
