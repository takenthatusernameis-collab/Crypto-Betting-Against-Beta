# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T16:49:08Z (refreshed; next session starts here)
- **Repo:** `Crypto-Betting-Against-Beta` (prioritized: a credible crypto Betting-Against-Beta research→backtest→ops workflow with deterministic offline defaults, dry-run-safe live execution, and gateable quality)
- **Git HEAD (verified this refresh):** `abca6ea` (`chore(kilo): checkpoint agent session`, `main...origin/main`)
- **Working tree:** four modified P12 test files (`tests/test_bab_backtest_p12_coverage.py`, `tests/test_bab_beta_p12_coverage.py`, `tests/test_bab_p12d_coverage.py`, `tests/test_bab_strategy_p12_coverage.py`). These are **required repairs**, not scratch edits: they fix a test collection syntax error and align tests with real production contracts. Do not blindly revert them. No production code changed.
- **Toolchain (verified this runner):** `python3 3.12.3`; `ruff 0.17.5`; runtime/test deps installed (`numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt`). Env/bootstrap bottleneck removed.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T16:49:08Z UTC) — BINDING (DO NOT IGNORE)

You are the next agentic worker on **Crypto-Betting-Against-Beta**. Your job is **heavy, measurable progress** on the P13 **data-integrity + execution-safety coverage campaign**. This is the **only** active task list. Follow it top-down. **No archaeology** (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), **no new parallel handoff/session docs**, **no “analysis-only” ending**.

### Hard rules (non-negotiable)
- **A session that ends without new tests/code AND fresh gate evidence is a FAILED session.** If something is externally blocked, record the exact command + output and continue with the next unblocked item—never stop at analysis.
- Preserve **byte-identical default offline/deterministic behavior** and **live execution dry-run-safe-by-default** (env-only creds, no implicit network). **No real (non-dry-run) live execution, no network, no credentials** in tests.
- Prefer small, tested diffs. Do not re-litigate P12: `strategy.py` is now **100%** covered.
- **Single durable handoff:** only `HANDOFF.md` is canonical; keep `AGENT_HANDOFF.md` pointer-only.

### Repo-prioritized mission (inferred from name `Crypto-Betting-Against-Beta`)
1. **Data integrity first:** loader/format/schema/error paths must fail loudly or coerce deterministically; no silent partial alignment.
2. **Backtest correctness:** rolling-beta and backtest edge semantics must be proven on finite/NaN/window/min-period inputs.
3. **Ops/execution safety:** adapter rejection/fill/diagnostic/replay/reconciliation/risk branches must be covered without network or credentials.
4. **Coverage gates:** drive **TOTAL to ≥ 98.5%** (stretch 99%) with **zero regressions**, then re-run the full gate.

### Current verified state (this refresh)
- **Git:** `abca6ea` (`chore(kilo): checkpoint agent session`, `main...origin/main`); four modified P12 test files only.
- **Full gate (fresh, 2026-11-15T16:49Z UTC):** `bash scripts/bab_gate.sh` → **6038 passed, 35 skipped, 0 failed, ~506s**, TOTAL **97% (204 missed)**, ruff clean, `strategy.py` **100%**.
- **Quick preflight:** `bash scripts/bab_quick.sh` → ruff clean; targeted trio **104 passed**; smoke (strategy/cli/costs) **195 passed**; `== quick preflight OK ==`.
- **Perf:** `python3 scripts/perf_baseline.py --check` → `failures: []` on the final rerun. This runner is noisy; one earlier run exceeded the 1.75x limit transiently, then passed. **Rerun before declaring a real perf regression.**
- **Paper smoke:** `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC` passes.
- **Live dry-run smoke:** `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check` → `{"connected": false, "dry_run": true, "n_submitted": 0, "n_fills": 0}`.

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

## Immediate execution order (mandatory, heavy work first)

1. **Baseline sanity (fast):** `bash scripts/bab_quick.sh` must stay green before feature work.
2. **P13-A — `data_loader.py` (HEAVY, do FIRST).** Create `tests/test_bab_data_loader_p13_coverage.py`.
   - Cover the 62 missed loader branches above with synthetic temp files and fakes only: format dispatch/errors, schema/index validation, empty/duplicate/non-monotonic data, benchmark/universe alignment, missing-column and parse-failure paths, and the remaining format-specific helpers.
   - Target: `data_loader.py` **≥ 99%** (≤ 10 missed). Assert observable behavior; do not weaken existing tests.
3. **P13-B — `execution.py` (HEAVY).** Create `tests/test_bab_execution_p13_coverage.py`.
   - Cover adapter rejection/fill/diagnostic/reconciliation branches, partial-fill and error paths, order-batching edges, and safety guards with fakes/mocks only (no network, no credentials, no real live execution).
   - Target: `execution.py` **≥ 98%** (≤ 10 missed).
4. **P13-C — `beta.py` and `backtest.py` correctness edges (HEAVY).**
   - Cover `beta.py` 125, 150-151, 163, 170-171, 189, 216-219, 435-436, 544-558 with finite/NaN/window/min-period equivalence assertions.
   - Cover `backtest.py` 17-21, 163 (local cleaning/import/error fallback).
   - Targets: `beta.py` **≥ 98%** (≤ 5 missed), `backtest.py` **≥ 98%** (≤ 2 missed).
5. **P13-D — ops safety residue (MEDIUM).** Cover `replay.py`, `portfolio.py`, `reconciliation.py`, `risk.py` missed lines above.
   - Targets: each **≥ 98%**; no silent exception swallowing without an assertion.
6. **Optional only if trivial/safe (do NOT churn):** `cli.py` 589-590, 746-748, 803-804; `data_sources.py` 480-508; `metrics.py` 94, 139-145; `signals.py` 37, 75; `config.py` 173.
7. **Final verification + handoff refresh (REQUIRED):** run in order: `python3 -m ruff check .`, `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (rerun once if noisy; must be `failures: []`), then paper/live dry-run smokes:
   - `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC`
   - `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check`
   - Update this file with new UTC timestamp, HEAD, exact command evidence, per-file coverage delta vs the table above, remaining gaps, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

**Cadence:** run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P13 step (A→B→C→D) and at the end.

## Definition of Done (session not done until ALL hold)
1. New P13 test files for steps completed exist and pass.
2. `python3 -m ruff check .` clean.
3. `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**, TOTAL **≥ 98.5%** (stretch 99%).
4. Per-file targets met with **no regression** on any previously-green module (especially `strategy.py` 100%).
5. `python3 scripts/perf_baseline.py --check` → `failures: []`.
6. Paper (`--dry-run --synthetic`) + live `--dry-run` health-check smokes pass.
7. This `HANDOFF.md` refreshed (and `AGENT_HANDOFF.md` pointer-only) with fresh evidence.

## Hard targets / acceptance
- `ruff check .` clean.
- `bash scripts/bab_gate.sh`: 0 failed, 0 errors, TOTAL ≥ 98.5%.
- No regression elsewhere; P13 targets: `data_loader.py ≥ 99%`, `execution.py ≥ 98%`, `beta.py ≥ 98%`, `backtest.py ≥ 98%`, `replay.py/portfolio.py/reconciliation.py/risk.py ≥ 98%`, `strategy.py = 100%`.
- `perf_baseline --check` `failures: []`.
- Dry-run CLIs pass as above.
- Default offline/deterministic unchanged; live dry-run-safe-by-default.

## Bottlenecks removed / constraints (do not reopen)
- **P12 collection blocker:** `tests/test_bab_p12d_coverage.py` had a `SyntaxError` at line 376 (`match("...")`); fixed. `python3 -m compileall -q tests` now exits 0.
- **P12 contract mismatches:** invalid `shorting_constraints`/`cost_model` dicts are rejected by `BABConfig.__post_init__` as `BABConfigError`, not later as `BABDataError`; tests corrected. `TransactionCostModel` uses fields such as `linear_fee`, not `{"type": "linear"}`.
- **P12 target mismatch:** several P12 tests called `run()` where the branch lives in `dry_run()`; corrected. `strategy.py` moved 89% → **100%**.
- **CLI smoke drift:** the old handoff commands (`--n-days`, `--csv`, `--source live`, `--live-dry-run`, `--health-check-only`) are invalid. Use the actual commands in this file.
- **Perf noise:** this runner occasionally reports a transient >1.75x slowdown; rerun `perf_baseline.py --check` before treating it as a regression.
- Env/bootstrap: **REMOVED** (ruff + deps installed; quick green verified). If missing in a new env, install with `python3 -m pip install --quiet -e ".[test,live]" ruff` and record.
- Gate speed: `scripts/bab_gate.sh` parallel (`pytest-xdist`, loadscope, sysmon on CPython≥3.12), serial fallback via `BAB_GATE_SERIAL=1` / `BAB_GATE_JOBS=N`. Do not make gate serial-only by default.
- Parallel-safety: follow `_*_cell_record`/`_*_records_full` patterns in stress/realism tests; summary tests must recompute deterministically under any worker subset.
- Historical noise: ignore root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Safety: no real live trading, no network, no credentials in tests. Live defaults to dry-run/health-check only.

## Protocol (for this session and every next session)
1. Read this file fully (and `AGENT_HANDOFF.md` pointer only).
2. Run `bash scripts/bab_quick.sh`; if red, fix before feature work.
3. Execute P13 A→B→C→D top-down with minimal tested diffs; create only the named P13 test files unless absolutely necessary (justify any extra file in this handoff).
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work.
5. Before finishing: run full verification suite above and rewrite this file’s “Current verified state”, tables/deltas, and the new INITIAL TASK MESSAGE timestamp if you hand off again (otherwise keep this timestamp but update evidence sections accurately).