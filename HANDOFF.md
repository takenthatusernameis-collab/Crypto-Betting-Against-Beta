# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T11:05:52Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `3e39cbd` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean at handoff refresh (no tracked/untracked product diffs expected beyond this handoff update).
- **Shell/toolchain (verified):** `python3`, `pytest 9.2.0`, `pytest-xdist`, `coverage 7.17.3`, `numpy/pandas/scipy/hypothesis/ccxt` present. `ruff 0.17.5` available as **`python3 -m ruff`** (may not be on `$PATH`); if `scripts/bab_quick.sh`/`bab_gate.sh` fail only on `ruff: command not found`, use `python3 -m ruff check .` or PATH-fix — not a product blocker.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T11:05:52Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **Every session must produce code/tests and fresh gate evidence** (or a concrete command+output for any external blocker, then continue with the next unblocked item).

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close remaining real-path coverage/gate gaps on the lowest-covered production modules.

### P11 status at this handoff (verified at HEAD `3e39cbd`)
- **Known fixes present (do not regress):** `strategies/betting_against_beta/data_sources.py` `CCXTFeed.fetch_latest` has in-scope `time` import for non-dry-run ticker timestamp path; `strategies/betting_against_beta/reconciliation.py` `reconcile_fills_to_backtest` tolerates returns DataFrames missing weight columns.
- **Existing P11 tests:** `tests/test_bab_data_sources_p11_coverage.py` (15 tests, collected/passing previously), `tests/test_bab_reconciliation_p11_coverage.py` (10 tests). These target specific branches but do **not** yet satisfy per-file gate targets.
- **Missing:** `tests/test_bab_execution_p11_coverage.py` does **not exist** — heavy new work required for `execution.py` ≥92%.
- **NOT yet re-established at HEAD `3e39cbd`:** full `bash scripts/bab_gate.sh` (authoritative TOTAL/per-file coverage), paper/live `--dry-run` CLI smokes, quick preflight script run (`bab_quick.sh`) as a single command. Partial baseline re-established this session (see evidence below).

## Immediate execution order (mandatory)

0. **Toolchain/PATH:** deps present; prefer `python3 -m ruff check .` if bare `ruff` unavailable.
1. **Re-establish authoritative baseline at HEAD `3e39cbd` (FIRST BLOCKING ACTION):** `python3 -m ruff check .` → targeted trio (`tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py`) → smoke (`tests/test_betting_against_beta.py`) → **full `bash scripts/bab_gate.sh`** (or equivalent parallel coverage run) → `python3 scripts/perf_baseline.py --check` → paper and live dry-run CLI smokes. Capture exact evidence (pass/skip/fail/error, TOTAL %, per-file for `cli.py`, `data_sources.py`, `execution.py`, `reconciliation.py`, `backtest.py`, `beta.py`, `strategy.py`). If gate is red, fix first with minimal diffs before adding coverage.
2. **P11 step 3 — `data_sources.py` real uncovered paths (EXTEND, HEAVY):** extend `tests/test_bab_data_sources_p11_coverage.py` (do not duplicate). Inspect **actual gate-missed** branches at HEAD and drive reachable retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation/error, CCXT/non-dry-run error and edge branches. **Fakes/mocks only.** Public API remains explicit opt-in with loud failures; deterministic-offline default unchanged. Target `data_sources.py` **≥ 90%** under full gate.
3. **P11 step 4 — `execution.py` dry-run-safe failure modes (NEW, HEAVY):** create `tests/test_bab_execution_p11_coverage.py`. Cover `LiveExecutionAdapter`/connector/health/error-rejection-fill-diagnostic/risk-gating/idempotency/cancel/timeout edges reachable without real network/credentials and without enabling real execution. Drive real missed paths on the large surface (~1563 LOC). Target `execution.py` **≥ 92%** under full gate.
4. **P11 step 5 — `reconciliation.py` confirm/close gaps:** keep/extend `tests/test_bab_reconciliation_p11_coverage.py` as needed so `reconciliation.py` remains **≥ 90%** under full gate (isolated prior snapshot showed ~95% on P11-only; confirm against gate suite).
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

## Fresh evidence (this session, 2026-11-15T11:05:52Z UTC, HEAD `3e39cbd`)

- `python3 -m ruff --version` → `ruff 0.17.5` (module available).
- `python3 -m ruff check .` → **clean** (exit 0).
- Targeted trio: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py` → **104 passed in 1.70s**.
- Smoke: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_betting_against_beta.py` → **86 passed, 2 warnings in 17.92s** (existing data_loader `dateutil` fallback warning).
- Perf baseline: `python3 scripts/perf_baseline.py --check` → **`failures: []`** (median full 4.6176ms vs 3.19ms baseline, beta 0.7423ms vs 0.49ms — within tolerance).
- **Not run this session:** `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, paper/live dry-run CLI smokes, and gate-authoritative per-file/TOTAL coverage at HEAD `3e39cbd`.

## Last known full-gate baseline (historical, stale vs HEAD `3e39cbd`)

- Historical (HEAD `0551f44`, 2026-11-15T09:15:57Z UTC): `bash scripts/bab_gate.sh` green — **5844 passed, 35 skipped, 0 failed, 0 errors; TOTAL 92%**. Per-file then: `cli.py` 99%, `data_sources.py` 78%, `execution.py` 81%, `reconciliation.py` 74%, `backtest.py` 84%, `beta.py` 85%, `strategy.py` 88%. `python3 scripts/perf_baseline.py --check` `failures: []`. **Must be re-verified at current HEAD.**

## Bottlenecks removed / constraints (do not reopen)

- **Gate speed:** `scripts/bab_gate.sh` runs parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Use `scripts/bab_quick.sh` for inner loop. Do not reintroduce serial-only gate or claim suite-timeout excuse.
- **Parallel-safety:** module-level record lists in `tests/test_bab_execution_realism_r3.py`, `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py` use `_*_cell_record`/`_*_records_full` pattern. **Any new module-level record list must follow this pattern.**
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only.
- **Historical noise (no archaeology):** root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests. Live path dry-run-safe-by-default.

## Protocol

1. Read this file fully.
2. Re-establish authoritative baseline (ruff, targeted trio, smoke, quick, **full gate**, perf check, paper/live dry-run smokes) at HEAD and capture exact evidence.
3. Execute P11 steps 3→4→5 top-down with minimal, tested diffs and gate evidence after each step; create/extend only the required P11 test files.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.
