# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T18:58:00Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research → backtest → execution/ops)
- **Git HEAD (verified this refresh):** `5ebd881` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** clean at refresh (`git status --short` empty). Verify with `git status --short` and `git log -1 --oneline` before acting.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt installed (`deps_ok`). `bash scripts/bab_bootstrap.sh` is the supported bootstrap (called by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T18:58:00Z) — BINDING (DO NOT IGNORE)

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Execute **P14 — Zero-Excuse Coverage & Safety Push** until the release gate is met. P14 is the **only** active campaign. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no analysis-only ending**.

### Campaign objective (heavy, measurable)
Raise BAB strategy coverage and safety confidence to **TOTAL >= 98.5%** (stretch 99%) with `bash scripts/bab_gate.sh` green and ruff clean, while preserving byte-identical default offline/deterministic behavior and **live dry-run-safe-by-default**. Every session must produce concrete progress: new passing P14 tests and/or a production bug fix with regression — never a handoff-only turn.

### Verified state (2026-11-15T18:58:00Z, this session)
- `bash scripts/bab_quick.sh` → **PASS** (`== quick preflight OK ==`: ruff clean, targeted trio 104 passed, smoke 195 passed).
- `python3 -m ruff check .` → **clean**.
- `tests/test_bab_execution_p14_coverage.py` → **32 passed** (fixed this session: removed E501 line-too-long and corrected `LiveExecutionAdapter` kwarg `exchange_name`→`exchange`). Fakes/mocks only, no network/credentials, no real live execution.
- **Coverage signals (re-measure under gate for truth):**
  - Isolated P14-B file: `coverage run -m pytest tests/test_bab_execution_p14_coverage.py -q -p no:xdist` → 32 passed; `execution.py` **98% (13 missed: 139-141,182-185,555-556,1287-1288,1386,1389)**.
  - Combined execution set: `coverage run -m pytest tests/test_bab_execution_p14_coverage.py tests/test_bab_execution_integration_r5.py tests/test_bab_execution_realism_r3.py tests/test_bab_execution_realism_r5e.py tests/test_bab_execution_p11_coverage.py -q -p no:xdist` → **202 passed, 8 warnings**; `execution.py` **92% (62 missed)** in this combined run (large divergence from isolated run — investigate under `bab_gate`/full suite context, avoid false confidence from single-file coverage).
- Full gate: **not run to completion this session**. No current gate TOTAL/pass/fail/skip recorded. Prior recorded full gate (stale, re-measure): **6071 passed, 35 skipped, 0 failed, 501.15s, TOTAL 97% (201 missed)**, ruff clean, floor 98.5% not met.

### Priority (continue in order, heavy work required)
1. **P14-B `execution.py` (CONTINUE, highest execution-safety risk):** Reconcile/raise gate-relevant coverage. Use `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` and/or targeted `coverage run -m pytest` that matches gate collection to identify true remaining missed lines in `execution.py`, then extend `tests/test_bab_execution_p14_coverage.py` to hit feasible branches (paper realism/adapter fallbacks, sanitize/import-edge, CCXT idempotent connect/guards, LiveFill/report edge paths, `_finite/_date_key/_adv` exception branches, engine pnl/batch skips) targeting **execution.py >= 98% in gate**. Fakes/mocks only — **no network, no credentials, no real live execution**.
2. **P14-C correctness:** create `tests/test_bab_beta_backtest_p14_coverage.py` targeting `beta.py` >= 98%, `backtest.py` >= 98% (finite/NaN/window/min-period inputs; prove equivalence to pandas rolling-OLS reference where applicable).
3. **P14-D ops safety residue:** create `tests/test_bab_ops_safety_p14_coverage.py` targeting `replay.py`, `portfolio.py`, `reconciliation.py`, `risk.py` each >= 98%.
4. **P14-A `data_loader.py`:** extend `tests/test_bab_data_loader_p14_coverage.py` for remaining missed coverable lines where feasible; `data_loader < 99%` acceptable only if **TOTAL >= 98.5%**.
5. **P14-E verification + handoff refresh:** full gate `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`, perf `python3 scripts/perf_baseline.py --check` (rerun once if noisy), paper + live dry-run smokes, controller tests if relevant; update this file with exact evidence.

### First 10 minutes (mandatory)
1. `bash scripts/bab_quick.sh` — must end with `== quick preflight OK ==`.
2. `git status --short` and `git log -1 --oneline` — record real HEAD/tree.
3. Read this file fully, then continue P14-B (measure gate-relevant execution misses, extend P14 test) or proceed to first unblocked step. Do not spend the session re-planning.

### Session output contract (binding)
A session that only edits this file is a **FAILED session**. Before finishing, ALL must hold:
1. At least one new/extended P14 test file passes (or a production bug fixed with a new regression test).
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
- Tool hygiene: if `edit` fails, retry with smaller unique `oldString`; after two failures use `write`. Do not repeat malformed calls.
- Full gate ~8-9+ min; timeout is not a test failure — rerun. Perf can be noisy; rerun `perf_baseline.py --check` once before treating as regression.

### P14 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P14-0 | Baseline quick green | — | [x] | 2026-11-15T18:58:00Z: `bash scripts/bab_quick.sh` PASS (ruff clean, 104 targeted + 195 smoke). HEAD `5ebd881`, deps ok, tree clean. |
| P14-A | `data_loader.py` coverable gaps (TOTAL floor governs) | `tests/test_bab_data_loader_p14_coverage.py` | [~] | Prior: file exists (33 tests). Extend for remaining coverable lines or accept if TOTAL >= 98.5%. |
| P14-B | `execution.py` >= 98% (gate-relevant) | `tests/test_bab_execution_p14_coverage.py` | [~] | 2026-11-15T18:58:00Z: fixed existing P14 test (E501 + `exchange_name`→`exchange`); `pytest tests/test_bab_execution_p14_coverage.py -q -p no:xdist` 32 passed, ruff clean, quick green. Coverage: isolated 98% (13 missed); combined exec suite 202 passed,8w but 92% (62 missed) — **gate-context coverage not yet confirmed, continue P14-B**. Full gate not completed this session. |
| P14-C | `beta.py` >= 98%, `backtest.py` >= 98% | `tests/test_bab_beta_backtest_p14_coverage.py` | [ ] | |
| P14-D | replay/portfolio/reconciliation/risk >= 98% | `tests/test_bab_ops_safety_p14_coverage.py` | [ ] | |
| P14-E | TOTAL >= 98.5%, gate green, handoff refreshed | — | [ ] | |

### Coverage notes (stale full-gate baseline 6071p/35s/0f, TOTAL 97%, 201 missed — re-measure)
- `execution.py` P14-B in progress; isolated vs combined coverage diverges this session — trust gate/full-suite measurement.
- Other per-file baselines unchanged from prior handoff until fresh gate.

| Module | Cover | Miss | Notes / remaining |
|--------|-------|------|-------------------|
| `__init__, attribution, costs, data, errors, quality, regime, shorting, sizing, strategy` | 100% | 0 | — |
| `execution.py` | ? (gate TBD) | ? | **P14-B continue**; isolated 98%/13, combined exec 92%/62 (this session) |
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
| **TOTAL** | **97% (stale)** | **201 (stale)** | floor 98.5% required |

### Known environment/ops bottlenecks (removed or constrained — do not reopen)
- **Missing deps:** use `scripts/bab_bootstrap.sh` / quick/gate.
- **Edit-tool loops:** after 2 failures use `write`.
- **Gate/perf flakiness:** full gate ~8-9+ min, timeout not failure; rerun once. Perf rerun once if noisy. `BAB_GATE_SERIAL=1` only for diagnosis.
- **Parallel-safety:** preserve `_*_cell_record`/deterministic recompute patterns.
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
3. Execute P14 B → C → D top-down with minimal tested diffs; extend/create only named P14 files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run applicable P14-E verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and keep `AGENT_HANDOFF.md` pointer-only.
