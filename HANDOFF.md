# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T19:22:44Z (this refresh)
- **Prior refresh:** 2026-11-15T19:22:00Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research → backtest → execution/ops)
- **Git HEAD (verified this refresh):** `41c38b1` (`chore(kilo): checkpoint agent session`)
- **Working tree:** clean at refresh (`git status --short` empty). Verify with `git status --short` and `git log -1 --oneline` before acting.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt installed (`deps_ok`). `bash scripts/bab_bootstrap.sh` is the supported bootstrap (called by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T19:22:44Z) — BINDING (DO NOT IGNORE)

**Gate status: COMPLETED — TOTAL 98% (152 missed / 6658 stmts), floor 98.5% NOT MET.** The full gate has now run to completion: **6103 passed, 35 skipped, 0 failed, 510.11s**. The primary blocker is **no longer the gate** — it is the **coverage gap of ~53 statements** to reach 98.5% (≤99 missed). `execution.py` is already **99% in gate** (11 missed: 139-141, 182-185, 555-556, 1287-1288) — P14-B target met. **Pivot immediately to P14-C and P14-D** which hold the largest coverage deficits.

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Execute **P14 — Zero-Excuse Coverage & Safety Push** until the release gate is met. P14 is the **only** active campaign. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no analysis-only ending**.

### Campaign objective (heavy, measurable)
Raise BAB strategy coverage and safety confidence to **TOTAL >= 98.5%** (stretch 99%) with `bash scripts/bab_gate.sh` green and ruff clean, while preserving byte-identical default offline/deterministic behavior and **live dry-run-safe-by-default**. Every session must produce concrete progress: new passing P14 tests and/or a production bug fix with regression — never a handoff-only turn.

### Verified state (2026-11-15T19:22:44Z, this session)
- `bash scripts/bab_quick.sh` → **PASS** (`== quick preflight OK ==`: ruff clean, targeted trio 104 passed, smoke 195 passed). HEAD `41c38b1`, tree clean, deps ok.
- `python3 -m ruff check .` → **clean**.
- `tests/test_bab_execution_p14_coverage.py` → **32 passed** (fakes/mocks only, no network/credentials, no real live execution).
- **Full gate (fresh, this session):** `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` → **6103 passed, 35 skipped, 0 failed, 510.11s, TOTAL 98% (152 missed / 6658 stmts)**, ruff clean, **floor 98.5% NOT MET**.
- **Gate-context per-file coverage (authoritative):**
  - `execution.py`: **99%** (11 missed) — P14-B target **MET** (≥98%)
  - `beta.py`: **93%** (28 missed: 125, 150-151, 163, 170-171, 189, 216-219, 435-436, 544-558) — **P14-C primary target**
  - `replay.py`: **92%** (11 missed: 172, 174, 205, 218-219, 234, 247-251) — **P14-D primary target**
  - `portfolio.py`: **95%** (11 missed: 152-153, 170-177, 180) — **P14-D target**
  - `reconciliation.py`: **95%** (10 missed: 78-79, 82-83, 112-113, 309, 377, 381, 385) — **P14-D target**
  - `risk.py`: **96%** (10 missed: 245, 326-328, 347, 353, 356, 566-568) — **P14-D target**
  - `backtest.py`: **96%** (6 missed: 17-21, 163) — **P14-C target**
  - `data_loader.py`: **98%** (44 missed) — **P14-A target** (TOTAL floor governs)
  - `metrics.py`: **98%** (4 missed), `signals.py`: **98%** (2), `cli.py`: **99%** (7), `data_sources.py`: **98%** (7), `config.py`: **99%** (1)

### Priority (heavy work required — execute in order)
1. **P14-C `beta.py` + `backtest.py` (HIGHEST IMPACT — 34 missed combined):** Create `tests/test_bab_beta_backtest_p14_coverage.py` targeting **beta.py ≥ 98%**, **backtest.py ≥ 98%**. Focus: finite/NaN/window/min-period inputs in `beta.py` (rolling OLS paths, lines 125, 150-151, 163, 170-171, 189, 216-219, 435-436, 544-558); `backtest.py` lines 17-21, 163. Prove equivalence to pandas rolling-OLS reference where applicable. Fakes/mocks only.
2. **P14-D `replay.py` + `portfolio.py` + `reconciliation.py` + `risk.py` (42 missed combined):** Create `tests/test_bab_ops_safety_p14_coverage.py` targeting **each ≥ 98%**. Focus: `replay.py` (172, 174, 205, 218-219, 234, 247-251), `portfolio.py` (152-153, 170-177, 180), `reconciliation.py` (78-79, 82-83, 112-113, 309, 377, 381, 385), `risk.py` (245, 326-328, 347, 353, 356, 566-568).
3. **P14-A `data_loader.py` (44 missed):** Extend `tests/test_bab_data_loader_p14_coverage.py` for remaining coverable lines where feasible; `data_loader < 99%` acceptable only if **TOTAL ≥ 98.5%**.
4. **P14-E verification + handoff refresh:** Full gate `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`, perf `python3 scripts/perf_baseline.py --check` (rerun once if noisy), paper + live dry-run smokes, controller tests; update this file with exact evidence.

### First 10 minutes (mandatory)
1. `bash scripts/bab_quick.sh` — must end with `== quick preflight OK ==`.
2. `git status --short` and `git log -1 --oneline` — record real HEAD/tree.
3. Read this file fully, then **start P14-C immediately** (create `tests/test_bab_beta_backtest_p14_coverage.py` targeting `beta.py`/`backtest.py` missed lines). Do not spend the session re-planning.

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
| P14-0 | Baseline quick green | — | [x] | 2026-11-15T19:22:44Z: `bash scripts/bab_quick.sh` PASS (ruff clean, 104 targeted + 195 smoke). HEAD `41c38b1`, deps ok, tree clean. |
| P14-A | `data_loader.py` coverable gaps (TOTAL floor governs) | `tests/test_bab_data_loader_p14_coverage.py` | [~] | Prior: file exists (33 tests). Extend for remaining coverable lines or accept if TOTAL ≥ 98.5%. |
| P14-B | `execution.py` ≥ 98% (gate-relevant) | `tests/test_bab_execution_p14_coverage.py` | [x] | 2026-11-15T19:22:44Z: Gate confirms `execution.py` **99%** (11 missed). P14-B **COMPLETE** — target met. |
| P14-C | `beta.py` ≥ 98%, `backtest.py` ≥ 98% | `tests/test_bab_beta_backtest_p14_coverage.py` | [ ] | **NEXT** — 34 missed combined (beta 28 + backtest 6). Create test file targeting missed lines. |
| P14-D | replay/portfolio/reconciliation/risk ≥ 98% | `tests/test_bab_ops_safety_p14_coverage.py` | [ ] | 42 missed combined. Create test file targeting missed lines. |
| P14-E | TOTAL ≥ 98.5%, gate green, handoff refreshed | — | [ ] | |

### Coverage notes (fresh gate baseline: 6103p/35s/0f, TOTAL 98%, 152 missed — 2026-11-15T19:22:44Z)
- `execution.py` P14-B **COMPLETE** at 99% gate coverage (11 missed: 139-141, 182-185, 555-556, 1287-1288).
- Per-file baselines updated from fresh gate run.

| Module | Cover | Miss | Notes / remaining |
|--------|-------|------|-------------------|
| `__init__, attribution, costs, data, errors, quality, regime, shorting, sizing, strategy` | 100% | 0 | — |
| `execution.py` | **99%** | **11** | **P14-B COMPLETE** (139-141, 182-185, 555-556, 1287-1288) |
| `beta.py` | **93%** | **28** | **P14-C NEXT** (125, 150-151, 163, 170-171, 189, 216-219, 435-436, 544-558) |
| `replay.py` | **92%** | **11** | **P14-D NEXT** (172, 174, 205, 218-219, 234, 247-251) |
| `portfolio.py` | **95%** | **11** | **P14-D** (152-153, 170-177, 180) |
| `reconciliation.py` | **95%** | **10** | **P14-D** (78-79, 82-83, 112-113, 309, 377, 381, 385) |
| `risk.py` | **96%** | **10** | **P14-D** (245, 326-328, 347, 353, 356, 566-568) |
| `data_loader.py` | **98%** | **44** | P14-A extendable gaps |
| `backtest.py` | **96%** | **6** | **P14-C** (17-21, 163) |
| `cli.py` | 99% | 7 | — |
| `data_sources.py` | 98% | 7 | — |
| `metrics.py` | 98% | 4 | — |
| `signals.py` | 98% | 2 | — |
| `config.py` | 99% | 1 | — |
| **TOTAL** | **98%** | **152** | **Floor 98.5% required (≤99 missed)** |

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
3. Execute P14 **C → D → A** top-down with minimal tested diffs; extend/create only named P14 files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run applicable P14-E verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message) and keep `AGENT_HANDOFF.md` pointer-only.
