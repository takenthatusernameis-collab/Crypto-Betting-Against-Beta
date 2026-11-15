# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T11:09:06Z (refreshed)
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `38be994` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean at refresh (no uncommitted product/code changes).
- **Toolchain (verified present):** `python3`, `pytest 9.2.0`, `pytest-xdist`, `coverage 7.17.3`, `numpy/pandas/scipy/hypothesis/ccxt`. `ruff 0.17.5` available as **`python3 -m ruff`** (bare `ruff` may be missing from `$PATH`; use module form if needed).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T11:09:06Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **Every session must produce code/tests and fresh gate evidence** (or an exact command+output for any external blocker, then continue with the next unblocked item).

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close remaining P11 real-path coverage/gate gaps on the lowest-covered production modules.

### Current state at HEAD `38be994` (verified this refresh)
- `python3 -m ruff check .` → clean (exit 0).
- `bash scripts/bab_quick.sh` → green (targeted trio 104 passed; smoke 195 passed).
- Full `bash scripts/bab_gate.sh` (319 test files, parallel+coverage/sysmon) → **in progress at refresh**; capture exact evidence (pass/skip/fail/error, TOTAL %, per-file coverage) before declaring done.
- P11 tests present: `tests/test_bab_cli_p11_coverage.py`, `tests/test_bab_data_sources_p11_coverage.py`, `tests/test_bab_reconciliation_p11_coverage.py`.
- **Missing:** `tests/test_bab_execution_p11_coverage.py` — does **not exist** (major required work, P11 step 1).
- `python3 scripts/perf_baseline.py --check` and paper/live dry-run CLI smokes → **not re-verified at HEAD `38be994`** (stale until re-verified).

## Immediate execution order (mandatory)

0. **Toolchain/PATH:** use `python3 -m ruff check .` if bare `ruff` is unavailable. Keep `PYTHONPATH=$PWD` for ad-hoc pytest when needed.
1. **Capture full-gate evidence (FIRST BLOCKING ACTION):** wait for/collect `bash scripts/bab_gate.sh` output. Record pass/skip/fail/error, TOTAL %, and per-file coverage for `cli.py`, `data_sources.py`, `execution.py`, `reconciliation.py`, `backtest.py`, `beta.py`, `strategy.py`. Also run `python3 scripts/perf_baseline.py --check` and paper/live dry-run CLI smokes. **If gate is red, fix first with minimal diffs before adding coverage.**
2. **P11 — `execution.py` dry-run-safe failure modes (NEW, HEAVY):** create `tests/test_bab_execution_p11_coverage.py`. Drive real gate-missed branches in `LiveExecutionAdapter`/`CCXTConnector`/health/error-rejection/fill-diagnostic/risk-gating/idempotency/cancel/timeout/retry edges reachable **without real network/credentials and without enabling real execution**. Use fakes/mocks; keep live path dry-run-safe-by-default. Target `execution.py` **≥ 92%** under full gate.
3. **P11 — `data_sources.py` real uncovered paths (EXTEND, HEAVY):** extend `tests/test_bab_data_sources_p11_coverage.py` (do not duplicate). Inspect actual gate-missed branches at HEAD and cover reachable retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation/error, CCXT/non-dry-run error and edge branches with **fakes/mocks only**. Public API remains explicit opt-in with loud failures; deterministic-offline default unchanged. Target `data_sources.py` **≥ 90%** under full gate.
4. **P11 — `reconciliation.py` and `cli.py` confirm/close gaps:** extend `tests/test_bab_reconciliation_p11_coverage.py` and/or `tests/test_bab_cli_p11_coverage.py` only for actual gate-missed branches. Keep `reconciliation.py` **≥ 90%** and `cli.py` stays **≥ 90%** under full gate.
5. **Deprecation hygiene (only if trivial/safe):** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and others) only when semantics identical and covered; do not chase unrelated churn.
6. **Final verification + handoff refresh:** re-run `python3 -m ruff check .`, `bash scripts/bab_quick.sh`, full `bash scripts/bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (`failures: []`), and paper/live dry-run CLI smokes. Update this file with new UTC timestamp, HEAD, exact evidence and per-file coverage deltas vs baseline, remaining gaps (if any), and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

Run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P11 step and at the end.

## Hard targets / acceptance (must all hold)

- `python3 -m ruff check .` clean.
- `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**.
- Per-file coverage (no regression elsewhere): `data_sources.py` **≥ 90%**, `execution.py` **≥ 92%**, `reconciliation.py` **≥ 90%**, `cli.py` stays **≥ 90%**.
- **TOTAL ≥ 93%**.
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Paper + live `--dry-run` smokes pass.
- Default offline/deterministic behavior unchanged; live path remains dry-run-safe-by-default; **no real (non-dry-run) live execution, no network, no credentials**.

## Bottlenecks removed / constraints (do not reopen)

- **Gate speed:** `scripts/bab_gate.sh` runs parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Use `scripts/bab_quick.sh` for inner loop. Do not reintroduce serial-only gate or claim suite-timeout excuse. Full gate ~5–6 min; budget for it.
- **Parallel-safety:** any new module-level record list must follow the `_*_cell_record`/`_*_records_full` pattern used in `tests/test_bab_execution_realism_r3.py`, `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py`.
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only.
- **Historical noise (no archaeology):** root `probe_*.py`, `debug_*.py`, `ast_probe.py`.
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests. Live path dry-run-safe-by-default.

## Protocol

1. Read this file fully.
2. Capture full-gate evidence (ruff, quick, **full gate**, perf check, paper/live dry-run smokes) at HEAD and capture exact evidence.
3. Execute P11 steps 2→3→4 top-down with minimal, tested diffs and gate evidence after each step; create/extend only required P11 test files.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.
