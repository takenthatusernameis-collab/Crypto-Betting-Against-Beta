# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T17:00:17Z
- **Repo:** `Crypto-Betting-Against-Beta` (crypto market-neutral BAB research -> backtest -> execution/ops)
- **Git HEAD (verified this refresh, before checkpoint):** `d74c84e` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** this refresh adds `scripts/bab_bootstrap.sh`, wires it into `scripts/bab_quick.sh` and `scripts/bab_gate.sh`, adds an opt-in `BAB_GATE_MIN_COVERAGE` floor to the gate, refreshes `docs/COVERAGE_NOTES.md` to the P14 baseline, and updates this file plus the `AGENT_HANDOFF.md` pointer. No production code and no existing test changed.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt installed. `bash scripts/bab_bootstrap.sh` is a no-op here.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T17:00:17Z) — BINDING (DO NOT IGNORE)

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Execute **P14 — Zero-Excuse Coverage & Safety Push**. P14 supersedes P13: P13 was defined but never executed, so do not create P13 files and do not restart it. P14 is the **only** active task list. Follow it top-down. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no analysis-only ending**.

### First 10 minutes (do this before anything else)
1. `bash scripts/bab_quick.sh` — this now bootstraps missing deps; it must end with `== quick preflight OK ==`.
2. `git status --short` and `git log -1 --oneline` — record the real HEAD; do not trust a stale handoff SHA.
3. Read this file fully, then start P14-A. Do not spend the session re-planning.

### Why this order (inferred from the repo name)
`Crypto-Betting-Against-Beta` is a crypto BAB strategy. The highest-severity failures are:
1. **Data integrity** — silently wrong/partial market data corrupts every downstream result; `data_loader.py` has the most missed branches (62).
2. **Execution safety** — paper/live adapters can mis-fill, mis-cost, or mis-reconcile; `execution.py` has 45 missed branches.
3. **Beta/backtest correctness** — rolling beta and backtest edges must be proven on finite/NaN/window/min-period inputs.
4. **Ops residue** — replay/portfolio/reconciliation/risk edge paths.
Coverage is the measurable proxy; **TOTAL >= 98.5%** (stretch 99%) is the release gate.

### Session output contract (binding)
A session that only edits this file is a **FAILED session**. Before finishing, ALL must hold:
1. At least one new P14 test file (named below) exists and passes, or a production bug is fixed with a new regression test.
2. `python3 -m ruff check .` is clean.
3. `bash scripts/bab_quick.sh` is green.
4. You ran `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` (or the plain gate) and recorded the exact TOTAL, pass/fail counts, and remaining gap in the ledger. A TOTAL below 98.5% is expected until P14 is complete; record it and continue to the next unblocked step in the same session.
5. The P14 ledger below has a new row with exact command evidence.
6. If all P14 steps are done, start P15 by attacking the next lowest-coverage module from the fresh gate table; do not stop at "campaign complete".
No handoff-only sessions. No analysis-only endings. If blocked, record the exact command + output and move to the next unblocked item.

### Hard rules
- Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default.
- No real live execution, no network, no credentials in tests.
- Prefer small tested diffs. Do not change production logic unless a new failing test proves a bug.
- Do not re-litigate P12: `strategy.py` is 100% covered.
- Single durable handoff: only `HANDOFF.md` is canonical; keep `AGENT_HANDOFF.md` pointer-only.
- If you see `SAME-RUN RECOVERY`, preserve local commits and work; do not reset or rewrite history.
- Tool hygiene: if `edit` fails with invalid arguments, re-read the file and retry with a smaller unique `oldString`; after two failures use `write` for that file. Do not repeat a malformed call three times.

### P14 execution order (heavy work first)

**P14-A — `data_loader.py` (HEAVY, do FIRST).** Create `tests/test_bab_data_loader_p14_coverage.py`.
- Target: `data_loader.py` **>= 99%** (<= 10 missed). Cover every missed line in the table below.
- Test seeds: dayfirst/unparseable index -> `BABDataError` (283-300, 318-319); NaT/None/inf scalar coercion (373, 385-389, 453-454); exchange-format fallback (697-698, 749-750, 868-869); empty asset token (1032); all-NaN columns -> `BABDataError` (1268-1272); parseable-series pending count (1391); quality campaign finite/stale branches (1636-1712); finite-count fallback (1958-1959); freshness reference/tz fallbacks (2742-2761).
- Use temp files/fakes only; assert observable behavior; do not weaken existing tests.

**P14-B — `execution.py` (HEAVY).** Create `tests/test_bab_execution_p14_coverage.py`.
- Target: `execution.py` **>= 98%** (<= 10 missed). Cover adapter rejection/fill/diagnostic/reconciliation, partial-fill/error paths, batching edges, and safety guards with fakes/mocks only (no network, no credentials, no real live execution).
- Test seeds: `_price_for` Timestamp fallback (139-141); `_adv_for` dict/Series/DataFrame + errors (164-166); `_adv_from_frame_value` Timestamp/Series (177-187); `_date_key`/`_as_timestamp` fallbacks (380-381, 403-404); ADV/date/target coercion (463-480, 505-506); JSON sanitize numpy/non-finite/ImportError (555-560); diagnostics without betas index (783-784); paper PnL bad date/returns (836-848); `LiveFill.to_dict` (1047); `cancel_order`/status dry-run paths (1281-1288); API password env (1380-1381); idempotent connect (1386).

**P14-C — `beta.py` + `backtest.py` correctness (HEAVY).** Create `tests/test_bab_beta_backtest_p14_coverage.py`.
- Targets: `beta.py` **>= 98%** (<= 5 missed), `backtest.py` **>= 98%** (<= 2 missed).
- Test seeds: `calculate_beta` empty/`BABDataError` (125, 150-151); `calculate_beta_fast` None/ragged/empty/non-finite (163, 170-171, 189, 216-219); `_finalize_betas` 1D degenerate/obs-short/non-finite (435-436) and fallback when the fast path fails (544-558); `backtest.py` 17-21 (ADV Series/DataFrame/None) and 163 (partial-fill ADV alignment). Prove equivalence to a pandas rolling-OLS reference on finite/NaN/window/min-period inputs.

**P14-D — ops safety residue (MEDIUM).** Create `tests/test_bab_ops_safety_p14_coverage.py`.
- Targets: `replay.py`, `portfolio.py`, `reconciliation.py`, `risk.py` each **>= 98%**.
- Test seeds: replay weight resize/non-finite/equity fallback/date+payload sanitize (172-251); portfolio extreme weights/dtype/index failure -> `BABPortfolioError` (152-180); reconciliation sanitize numpy/ImportError/fill weight+cost fallbacks (78-113, 309, 377-385); risk HHI/position-age/drawdown/turnover/kill-switch/event filtering (245, 326-356, 566-568).

**P14-E — final verification + handoff refresh (REQUIRED).**
1. `python3 -m ruff check .`
2. `bash scripts/bab_quick.sh`
3. `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` — use a 600000 ms tool timeout or run it as a background process; rerun once if the runner is noisy.
4. `python3 scripts/perf_baseline.py --check` — rerun once if noisy; must be `failures: []`.
5. Paper smoke: `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC`
6. Live dry-run smoke: `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check`
7. Update this file's timestamp, HEAD, table, ledger, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

### P14 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P14-0 | Baseline quick green | — | [x] | 2026-11-15T17:00Z: `bash scripts/bab_quick.sh` -> ruff clean, 104 targeted + 195 smoke passed; perf `failures: []` |
| P14-A | `data_loader.py` >= 99% | `tests/test_bab_data_loader_p14_coverage.py` | [ ] | |
| P14-B | `execution.py` >= 98% | `tests/test_bab_execution_p14_coverage.py` | [ ] | |
| P14-C | `beta.py` >= 98%, `backtest.py` >= 98% | `tests/test_bab_beta_backtest_p14_coverage.py` | [ ] | |
| P14-D | replay/portfolio/reconciliation/risk >= 98% | `tests/test_bab_ops_safety_p14_coverage.py` | [ ] | |
| P14-E | TOTAL >= 98.5%, gate green, handoff refreshed | — | [ ] | |

### Current verified state (this refresh)

- **Git:** `d74c84e` (`chore(kilo): checkpoint agent session`, `main...origin/main`) at refresh before checkpoint. This refresh will be checkpointed as a new commit.
- **Full gate (fresh this refresh; 6678 statements):** `bash scripts/bab_gate.sh` -> **6038 passed, 35 skipped, 0 failed, 508.47s**, TOTAL **97%** (204 missed), ruff clean, `strategy.py` **100%**. The later script-only edits (bootstrap + optional floor) do not change test collection or coverage; P14 final must rerun the floor command.
- **Quick preflight:** `bash scripts/bab_quick.sh` -> ruff clean; targeted trio **104 passed**; smoke (strategy/cli/costs) **195 passed**; `== quick preflight OK ==`.
- **Controller tests:** `python3 -m pytest -q tests/test_controller_progress_accounting.py tests/test_workflow_diagnostics_scanner.py tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py` -> **125 passed**.
- **Perf:** `python3 scripts/perf_baseline.py --check` -> `failures: []` (rerun once if the runner is noisy).
- **Paper smoke:** `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC` passes.
- **Live dry-run smoke:** `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check` -> `{"connected": false, "dry_run": true, "n_submitted": 0, "n_fills": 0}`.

### Per-file coverage baseline (fresh full gate; re-measure in every full gate you run)

| Module | Cover | Miss | Remaining missed lines |
|--------|-------|------|------------------------|
| `__init__.py`, `attribution.py`, `costs.py`, `data.py`, `errors.py`, `quality.py`, `regime.py`, `shorting.py`, `sizing.py`, `strategy.py` | 100% | 0 | — |
| `data_loader.py` | **97%** | **62** | 100-101, 283-295, 299-300, 318-319, 373, 385-389, 453-454, 697-698, 749-750, 868-869, 1032, 1268, 1271-1272, 1391, 1636-1637, 1647, 1678-1679, 1684-1685, 1690-1692, 1702-1712, 1958-1959, 2742-2743, 2747, 2749-2750, 2756-2757, 2760-2761 |
| `execution.py` | **94%** | **45** | 139-141, 164-166, 177-178, 182-187, 380-381, 403-404, 463-464, 472-473, 479-480, 505-506, 555-556, 559-560, 783-784, 836-837, 847-848, 1047, 1281-1288, 1380-1381, 1386 |
| `beta.py` | **93%** | **28** | 125, 150-151, 163, 170-171, 189, 216-219, 435-436, 544-558 |
| `replay.py` | **92%** | **11** | 172, 174, 205, 218-219, 234, 247-251 |
| `portfolio.py` | **95%** | **11** | 152-153, 170-177, 180 |
| `reconciliation.py` | **95%** | **10** | 78-79, 82-83, 112-113, 309, 377, 381, 385 |
| `risk.py` | **96%** | **10** | 245, 326-328, 347, 353, 356, 566-568 |
| `cli.py` | 99% | 7 | 589-590, 746-748, 803-804 |
| `data_sources.py` | 98% | 7 | 480-481, 484, 499-500, 507-508 |
| `backtest.py` | 96% | 6 | 17-21, 163 |
| `metrics.py` | 98% | 4 | 94, 139, 142, 145 |
| `signals.py` | 98% | 2 | 37, 75 |
| `config.py` | 99% | 1 | 173 |
| **TOTAL** | **97%** | **204** | — |

### Bottlenecks removed / constraints (do not reopen)
- **Dependency bootstrap (new):** `scripts/bab_bootstrap.sh` detects missing imports and installs only missing modules from `requirements.txt` + `ruff`; `scripts/bab_quick.sh` and `scripts/bab_gate.sh` call it. This directly removes the repeated `ModuleNotFoundError` / `ccxt is required` blocks seen in prior runs. `CI=true` allows `--break-system-packages` on PEP-668 hosts; `BAB_SKIP_ENV_BOOTSTRAP=1` skips the check.
- **Stale handoff state:** the previous refresh claimed four modified P12 files while the tree was clean at `d74c84e`; this refresh records the real HEAD/tree and does not re-list committed work as pending.
- **P13 never started:** P13 is folded into P14. Do not create P13 files; use the P14 names above.
- **Coverage floor:** `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` now fails when TOTAL is below the floor. A red floor is expected until P14 is complete; do not lower it.
- **Tool invalid-argument loops:** after two failed `edit` calls, re-read and retry with a smaller unique `oldString` or use `write`; do not repeat the same malformed call three times.
- **Gate timeout:** the full gate takes ~8-9 minutes; use a 600000 ms tool timeout or run it in the background. A tool timeout is not a test failure; rerun.
- **Perf noise:** this runner occasionally reports a transient >1.75x slowdown; rerun `perf_baseline.py --check` before treating it as a regression.
- **CLI smoke drift:** the old handoff commands (`--n-days`, `--csv`, `--source live`, `--live-dry-run`, `--health-check-only`) are invalid. Use the actual commands in this file.
- **Gate speed:** `scripts/bab_gate.sh` parallel (`pytest-xdist`, loadscope, sysmon on CPython >= 3.12), serial fallback via `BAB_GATE_SERIAL=1` / `BAB_GATE_JOBS=N`. Do not make the gate serial-only by default.
- **Parallel-safety:** follow `_*_cell_record`/`_*_records_full` patterns in stress/realism tests; summary tests must recompute deterministically under any worker subset.
- **Historical noise:** ignore root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** no real live trading, no network, no credentials in tests. Live defaults to dry-run/health-check only.

### Protocol (for this session and every next session)
1. Read this file fully (and `AGENT_HANDOFF.md` pointer only).
2. Run `bash scripts/bab_quick.sh`; if red, fix before feature work.
3. Execute P14 A -> B -> C -> D top-down with minimal tested diffs; create only the named P14 test files unless absolutely necessary (justify any extra file in this handoff).
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run the P14-E verification suite and rewrite this file's "Current verified state", tables/deltas, ledger, and the new INITIAL TASK MESSAGE timestamp. Keep `AGENT_HANDOFF.md` pointer-only.
