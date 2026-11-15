# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T10:02:30Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `1335ac5` (`chore(kilo): checkpoint agent session`, `main`)
- **Working tree:** clean at session start (except this handoff refresh). Keep changes minimal and task-focused.
- **Shell/toolchain note (current shell):** `python3` and `pytest` present; `ruff` **missing**. Before any gate run, install the full gate toolchain as step 0: `pip install --break-system-packages pytest pytest-cov pytest-xdist coverage ruff numpy pandas scipy hypothesis ccxt` (or `pip install -e .[test]` + `ccxt`). A missing-toolchain shell is a setup blocker to clear first — not a reason to stop or to skip verification.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T10:02:30Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs, no analysis-only stopping point. **Every session must produce code/tests and fresh gate evidence** (or a concrete command+output for any external blocker, then continue with the next unblocked item).

**Repo-prioritized mission (inferred from `Crypto-Betting-Against-Beta`):** make the Betting Against Beta (crypto) strategy release-ready and ops-ready. Preserve byte-identical default offline/deterministic behavior and live execution that is **dry-run-safe-by-default** (env-only creds, no implicit network). Close remaining real-path coverage/gate gaps on the lowest-covered production modules.

**P11 status:** step 1 (baseline at `0551f44`) and step 2 (`cli.py` coverage via `tests/test_bab_cli_p11_coverage.py`, `cli.py` 77% → **99%**) are **DONE — do not redo** unless you introduce regressions. **Start now at P11 step 3.**

## Immediate execution order (mandatory)

0. **Unblock environment (if needed):** install gate toolchain (see note above). Confirm `ruff`, `pytest`, `pytest-cov`, `xdist`, `coverage` available.
1. **Re-establish baseline at current HEAD (`1335ac5`):** `python3 -m ruff check .` → `bash scripts/bab_quick.sh` → `bash scripts/bab_gate.sh`. Capture exact evidence (pass/skip/fail/error counts, total %, per-file % for targets). If gate is red, fix first with minimal diffs before adding coverage.
2. **P11 step 3 — `data_sources.py` real uncovered paths (NEW):** create/extend `tests/test_bab_data_sources_p11_coverage.py`. Drive reachable retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation branches. **Fakes/mocks only.** Public API remains explicit opt-in with loud failures; deterministic-offline default unchanged. Target `data_sources.py` **78% → ≥ 90%**.
3. **P11 step 4 — `execution.py` dry-run-safe failure modes (NEW):** `tests/test_bab_execution_p11_coverage.py`. Cover `LiveExecutionAdapter`/connector/health/error-rejection-fill-diagnostic/risk-gating edges that are reachable without real network/credentials and without enabling real execution. Target `execution.py` **81% → ≥ 92%**.
4. **P11 step 5 — `reconciliation.py` error branches (NEW):** `tests/test_bab_reconciliation_p11_coverage.py`. Cost/fill mismatch, missing fills, empty weights — deterministic, no network. Target `reconciliation.py` **74% → ≥ 90%**.
5. **Deprecation hygiene (only if trivial/safe):** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and any others) only when semantics are identical.
6. **Final verification + handoff refresh:** re-run ruff, `bab_quick.sh`, full `bab_gate.sh`, `python3 scripts/perf_baseline.py --check` (`failures: []`), plus paper and live dry-run CLI smokes. Update this file with new UTC timestamp, HEAD, exact evidence and per-file coverage deltas vs prior baseline, and the next binding campaign. Keep `AGENT_HANDOFF.md` pointer-only.

Run `bash scripts/bab_quick.sh` after each meaningful slice; run full `bash scripts/bab_gate.sh` at least after each P11 step and at the end.

## Hard targets / acceptance (must all hold)

- `python3 -m ruff check .` clean.
- `bash scripts/bab_gate.sh` green: **0 failed, 0 errors**.
- Per-file coverage (no regression elsewhere): `data_sources.py` **≥ 90%**, `execution.py` **≥ 92%**, `reconciliation.py` **≥ 90%**, `cli.py` stays **≥ 90%**.
- **TOTAL ≥ 93%**.
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Paper + live `--dry-run` smokes pass.
- Default offline/deterministic behavior unchanged; live path remains dry-run-safe-by-default; **no real (non-dry-run) live execution, no network, no credentials**.

## Last verified baseline (from HEAD `0551f44`, 2026-11-15T09:15:57Z UTC — re-verify at current HEAD)

- `ruff check .` clean.
- `bash scripts/bab_quick.sh` green (targeted trio **104 passed**; smoke **195 passed**, ~26s).
- `bash scripts/bab_gate.sh` green: **5844 passed, 35 skipped, 0 failed, 0 errors; TOTAL 92%** (~9m18s, parallel xdist/sysmon).
- Per-file: `cli.py` **99%** (555 stmts, 7 missed: 589-590,746-748,803-804); `data_sources.py` **78%** (282, 62 missed: 164-165,169,173,230-237,260,302-303,311,320,322,324,329-330,347,366-377,400-403,422-427,431-434,438-447,475-480,483,487-488,497-499,506-507); `execution.py` **81%** (772, 145 missed: 132,138-144,148,153-166,171-188,333,348,354-355,380-381,391-392,403-404,423,452-456,463-464,472-473,479-480,482,497-498,505-506,532,543-561,719,722-723,745,783-784,827,836-837,844,847-848,850,876-880,893-894,1047,1130-1131,1139,1151,1153,1155,1157,1162,1180-1185,1190,1223-1256,1272,1281-1288,1297,1302,1307,1313,1318,1380-1381,1386,1475,1477,1546,1550); `reconciliation.py` **74%** (49 missed: 54-84,103-104,107-113,115,136-137,294,318-319,361,368,372,376); `backtest.py` 84%; `beta.py` 85%; `strategy.py` 88%; `risk.py` 89%.
- `python3 scripts/perf_baseline.py --check` not re-run at `1335ac5` (last known `failures: []`) — re-run in final verification.

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
