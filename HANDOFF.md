# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T10:26:51Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `2d76d59` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean — changes committed at HEAD `2d76d59`.
- **Shell/toolchain (verified):** `python3`, `pytest 9.2.0`, `pytest-xdist`, `coverage 7.17.3`, `numpy/pandas/scipy/hypothesis/ccxt` present. `ruff 0.17.5` installed but **not on `$PATH`** — invoke as `python3 -m ruff` (`scripts/bab_quick.sh`/`bab_gate.sh` assume `ruff` on PATH; if they fail only on that, use `python3 -m ruff check .` or PATH-fix). No network/credentials in tests.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T10:26:51Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **Every session must produce code/tests and fresh gate evidence** (or a concrete command+output for any external blocker, then continue with the next unblocked item).

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close remaining real-path coverage/gate gaps on the lowest-covered production modules.

### P11 status at this handoff (re-established at HEAD `2d76d59`)
- **Fixed blocker (prior session):** `strategies/betting_against_beta/data_sources.py` — `CCXTFeed.fetch_latest` imports `time` in-scope for non-dry-run ticker timestamp path (was `UnboundLocalError`).
- **Fixed robustness edge (prior session):** `strategies/betting_against_beta/reconciliation.py` — `reconcile_fills_to_backtest` tolerates returns DataFrames missing weight columns (reindexes to weight universe / zero-fills) instead of `KeyError`.
- **Existing:** `tests/test_bab_data_sources_p11_coverage.py` (15 tests, passes). `tests/test_bab_reconciliation_p11_coverage.py` (10 tests, passes, targeted 95%).
- **NOT yet re-established at HEAD `2d76d59`:** full `bash scripts/bab_gate.sh` (authoritative per-file TOTAL), paper/live `--dry-run` CLI smokes. Quick preflight (`bab_quick.sh`) and `perf_baseline` **verified green this session**.
- `tests/test_bab_execution_p11_coverage.py` does **not exist** — heavy work required for `execution.py` ≥92%.

## Immediate execution order (mandatory)

0. **Toolchain/PATH:** deps present; `ruff` is `python3 -m ruff` (not on PATH). If `bab_quick.sh`/`bab_gate.sh` fail only due to `ruff: command not found`, run lint as `python3 -m ruff check .` and proceed, or PATH-fix — do not treat as product blocker.
1. **Re-establish baseline at HEAD `2d76d59` (FIRST BLOCKING ACTION):** `python3 -m ruff check .` → targeted trio (`tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py`) → smoke → full `bash scripts/bab_gate.sh` (or equivalent parallel coverage run). Capture exact evidence (pass/skip/fail/error, TOTAL %, per-file for `cli.py`, `data_sources.py`, `execution.py`, `reconciliation.py`, `backtest.py`, `beta.py`, `strategy.py`). If gate is red, fix first with minimal diffs before adding coverage.
2. **P11 step 3 — `data_sources.py` real uncovered paths (EXTEND):** extend `tests/test_bab_data_sources_p11_coverage.py` (do not duplicate). Inspect missed branches at HEAD and drive reachable retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation/error branches. **Fakes/mocks only.** Public API remains explicit opt-in with loud failures; deterministic-offline default unchanged. Target `data_sources.py` **≥ 90%** (measured in gate).
3. **P11 step 4 — `execution.py` dry-run-safe failure modes (NEW, HEAVY):** create `tests/test_bab_execution_p11_coverage.py`. Cover `LiveExecutionAdapter`/connector/health/error-rejection-fill-diagnostic/risk-gating edges reachable without real network/credentials and without enabling real execution. Drive real missed paths (large surface: ~772 stmts). Target `execution.py` **≥ 92%**.
4. **P11 step 5 — `reconciliation.py` confirm/close gaps:** keep/extend `tests/test_bab_reconciliation_p11_coverage.py` as needed so `reconciliation.py` remains **≥ 90%** under full gate (targeted now 95%).
5. **Deprecation hygiene (only if trivial/safe):** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and any others) only when semantics identical and covered.
6. **Final verification + handoff refresh:** re-run `python3 -m ruff check .`, quick/targeted checks, full `bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (`failures: []`), plus paper and live dry-run CLI smokes. Update this file with new UTC timestamp, HEAD, exact evidence and per-file coverage deltas vs baseline, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

Run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P11 step and at the end.

## Hard targets / acceptance (must all hold)

- `python3 -m ruff check .` clean.
- `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**.
- Per-file coverage (no regression elsewhere): `data_sources.py` **≥ 90%**, `execution.py` **≥ 92%**, `reconciliation.py` **≥ 90%**, `cli.py` stays **≥ 90%**.
- **TOTAL ≥ 93%**.
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Paper + live `--dry-run` smokes pass.
- Default offline/deterministic behavior unchanged; live path remains dry-run-safe-by-default; **no real (non-dry-run) live execution, no network, no credentials**.

## Fresh evidence (this session, 2026-11-15T10:26:51Z UTC, HEAD `2d76d59`)

- `python3 -m ruff check .` → **clean** (exit 0).
- Targeted trio: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → **104 passed in 1.63s**.
- Smoke: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_betting_against_beta.py` → **86 passed, 2 warnings in 18.43s** (existing data_loader warning).
- Quick preflight: `bash scripts/bab_quick.sh` → **ruff clean, targeted trio 104 passed, smoke 195 passed in 24.74s**.
- P11 data_sources: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_sources_p11_coverage.py` → **15 passed in 0.47s**.
- P11 reconciliation: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_reconciliation_p11_coverage.py` → **10 passed in 0.48s**.
- Perf baseline: `python3 scripts/perf_baseline.py --check` → **`failures: []`** (current median 4.59ms vs baseline 3.19ms full, 0.73ms vs 0.49ms beta — within tolerance).
- Isolated coverage snapshot (P11 tests only, not gate-authoritative):
  - `data_sources.py` **71%** (282 stmts, 83 missed) — **below ≥90% target**.
  - `reconciliation.py` **95%** (196 stmts, 10 missed: 78-79,82-83,112-113,309,377,381,385) — **meets ≥90% target**.
  - `execution.py` **24%** (772 stmts, 587 missed) — **well below ≥92% target, heavy work required**.
- **Not run this session:** full `bash scripts/bab_gate.sh`, paper/live dry-run CLI smokes.

## Last known full-gate baseline (historical, stale vs HEAD `2d76d59`)

- From HEAD `0551f44` (2026-11-15T09:15:57Z UTC): `bash scripts/bab_gate.sh` green — **5844 passed, 35 skipped, 0 failed, 0 errors; TOTAL 92%**. Per-file then: `cli.py` 99%, `data_sources.py` 78%, `execution.py` 81%, `reconciliation.py` 74%, `backtest.py` 84%, `beta.py` 85%, `strategy.py` 88%. `python3 scripts/perf_baseline.py --check` last known `failures: []`. **Re-verify now at HEAD `2d76d59`.**

## Bottlenecks removed / constraints (do not reopen)

- **`CCXTFeed.fetch_latest` time-import bug (P11 blocker) fixed** — keep `time` available in both dry-run and non-dry-run branches.
- **Gate speed fixed:** `scripts/bab_gate.sh` runs parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Use `scripts/bab_quick.sh` for inner loop. Do not reintroduce a serial-only gate or claim suite-timeout excuse.
- **Parallel-safety fixed:** module-level record lists in `tests/test_bab_execution_realism_r3.py`, `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py` use `_*_cell_record`/`_*_records_full` (distribution-agnostic). **Do not revert; any new module-level record list must follow this pattern.**
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. No parallel session/handoff docs.
- **Historical noise:** root `probe_*.py`, `debug_*.py`, `ast_probe.py` — ignore (no archaeology).
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests.

## Protocol

1. Read this file fully.
2. Re-establish baseline (ruff, targeted trio, smoke, full gate, perf check) at HEAD and capture exact evidence.
3. Execute P11 steps 3→4→5 top-down with minimal, tested diffs and gate evidence after each step; create/extend only the required P11 test files.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.