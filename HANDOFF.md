# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T10:07:26Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `3fd7cc4` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean at this handoff refresh (only `HANDOFF.md`/pointer updated). Keep changes minimal and task-focused.
- **Shell/toolchain (verified this session):** `python3`, `pytest 9.2.0`, `pytest-xdist`, `coverage 7.17.3`, `numpy/pandas/scipy/hypothesis/ccxt` present. `ruff 0.17.5` installed but **not on `$PATH`** — invoke as `python3 -m ruff` (`scripts/bab_quick.sh`/`bab_gate.sh` assume `ruff` on PATH; if they fail only on that, use `python3 -m ruff check .` or PATH-fix). No network/credentials in tests. `python3 -m ruff check .` clean at HEAD.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T10:07:26Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **Every session must produce code/tests and fresh gate evidence** (or a concrete command+output for any external blocker, then continue with the next unblocked item).

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close remaining real-path coverage/gate gaps on the lowest-covered production modules.

**P11 status (do not redo unless regression):** step 2 `cli.py` coverage DONE (`tests/test_bab_cli_p11_coverage.py`, `cli.py` **99%**, 7 missed: 589-590,746-748,803-804). `tests/test_bab_data_sources_p11_coverage.py` exists (prior partial coverage work) — **extend it, do not duplicate**. `tests/test_bab_execution_p11_coverage.py` and `tests/test_bab_reconciliation_p11_coverage.py` **do not exist yet**. **Fresh full-gate/smoke/perf baseline NOT yet re-established at HEAD `3fd7cc4` this session (lint clean only) — START at P11 step 1 (baseline), then step 3.**

## Immediate execution order (mandatory)

0. **Toolchain/PATH:** environment already has deps; `ruff` is `python3 -m ruff` (not on PATH). If `bab_quick.sh`/`bab_gate.sh` fail only due to `ruff: command not found`, run lint as `python3 -m ruff check .` and proceed with the script steps that work, or add user bin to PATH — do not treat as product blocker.
1. **Re-establish baseline at HEAD `3fd7cc4` (NOT YET RUN this session):** `python3 -m ruff check .` → targeted trio (`tests/test_bab_live_adapter.py tests/test_bab_risk_manager.py tests/test_bab_realtime_feed.py tests/test_bab_paper_trading.py tests/test_bab_data_freshness.py tests/test_bab_diagnostics.py`) → smoke subset → full `bash scripts/bab_gate.sh` (or equivalent parallel coverage run). Capture exact evidence (pass/skip/fail/error, TOTAL %, per-file for `cli.py`, `data_sources.py`, `execution.py`, `reconciliation.py`, `backtest.py`, `beta.py`, `strategy.py`). If gate is red, fix first with minimal diffs before adding coverage.
2. **P11 step 3 — `data_sources.py` real uncovered paths (EXTEND):** extend `tests/test_bab_data_sources_p11_coverage.py`. Inspect `strategies/betting_against_beta/data_sources.py` missed branches at HEAD and drive reachable retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation/error branches. **Fakes/mocks only.** Public API remains explicit opt-in with loud failures; deterministic-offline default unchanged. Target `data_sources.py` **≥ 90%**.
3. **P11 step 4 — `execution.py` dry-run-safe failure modes (NEW):** create `tests/test_bab_execution_p11_coverage.py`. Cover `LiveExecutionAdapter`/connector/health/error-rejection-fill-diagnostic/risk-gating edges reachable without real network/credentials and without enabling real execution. Target `execution.py` **≥ 92%**.
4. **P11 step 5 — `reconciliation.py` error branches (NEW):** create `tests/test_bab_reconciliation_p11_coverage.py`. Cost/fill mismatch, missing fills, empty weights — deterministic, no network. Target `reconciliation.py` **≥ 90%**.
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

## Last verified baseline (from HEAD `0551f44`, 2026-11-15T09:15:57Z UTC — **stale vs HEAD `3fd7cc4`, re-verify now**)

- `ruff check .` clean.
- `bash scripts/bab_quick.sh` green (targeted trio **104 passed**; smoke **195 passed**, ~26s).
- `bash scripts/bab_gate.sh` green: **5844 passed, 35 skipped, 0 failed, 0 errors; TOTAL 92%** (~9m18s, parallel xdist/sysmon).
- Per-file (historical): `cli.py` **99%** (555 stmts, 7 missed); `data_sources.py` **78%** (282, 62 missed incl. 164-165,169,173,230-237,260,302-303,311,320,322,324,329-330,347,366-377,400-403,422-427,431-434,438-447,475-480,483,487-488,497-499,506-507); `execution.py` **81%** (772, 145 missed); `reconciliation.py` **74%** (49 missed); `backtest.py` 84%; `beta.py` 85%; `strategy.py` 88%; `risk.py` 89%.
- `python3 scripts/perf_baseline.py --check` last known `failures: []` (not re-run at HEAD).
- **Current-session note (2026-11-15T10:07:26Z):** HEAD `3fd7cc4`; `python3 -m ruff check .` clean; toolchain/deps present (`ruff` via `python3 -m ruff`). `tests/test_bab_data_sources_p11_coverage.py` exists, `tests/test_bab_execution_p11_coverage.py` and `tests/test_bab_reconciliation_p11_coverage.py` absent. **No fresh quick/gate/perf/per-file baseline executed yet at HEAD `3fd7cc4`** — P11 step 1 is the first blocking action (capture exact evidence before changing code). No parallel handoff/session docs found; `AGENT_HANDOFF.md` remains pointer-only.

## Bottlenecks removed / constraints (do not reopen)

- **Gate speed fixed:** `scripts/bab_gate.sh` runs parallel (`pytest-xdist`, `--dist loadscope`, sysmon on CPython ≥3.12) with serial fallback (`BAB_GATE_SERIAL=1`, `BAB_GATE_JOBS=N`). Use `scripts/bab_quick.sh` for inner loop. Do not reintroduce a serial-only gate or claim a suite-timeout excuse.
- **Parallel-safety fixed:** module-level record lists in `tests/test_bab_execution_realism_r3.py`, `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py` use `_*_cell_record`/`_*_records_full` (distribution-agnostic). **Do not revert; any new module-level record list must follow this pattern.**
- **Single durable handoff:** only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. No parallel session/handoff docs.
- **Historical noise:** root `probe_*.py`, `debug_*.py`, `ast_probe.py` — ignore (no archaeology).
- **Canonical CLI:** `python3 -m strategies.betting_against_beta.cli`.
- **Safety:** real (non-dry-run) live execution out of scope; never enable without explicit opt-in and credential review. No network/credentials in tests.

## Protocol

1. Read this file fully.
2. Clear toolchain blocker if present, then re-establish baseline (ruff, quick, full gate) at HEAD.
3. Execute P11 steps 3→4→5 top-down with minimal, tested diffs and gate evidence after each step.
4. Never stop at analysis; if blocked record exact command+output and continue unblocked work.
5. Refresh this file (and keep `AGENT_HANDOFF.md` pointer-only) before finishing.
