# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T08:44:25Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `0551f44` — baseline clean at HEAD; no parallel handoff docs. Only handoff-document changes between `1285fd3` and `0551f44` (kilo checkpoint); no code changes. P11 step 2 (`cli.py` coverage) **DONE** via `tests/test_bab_cli_p11_coverage.py`; `cli.py` is **99%** (≥90% target met/exceeded). First act next session: execute P11 campaign top-down starting at **step 3** (`data_sources.py` coverage) (baseline steps 1 & 2 are DONE — do not repeat).
- **Branch:** `main`
- **Working tree:** clean except this `HANDOFF.md` + `AGENT_HANDOFF.md` pointer refresh (single durable handoff only); no code changes. Shell note: gate toolchain (`ruff`, `pytest`, `pytest-cov`, `pytest-xdist`, `coverage`, `hypothesis`, `ccxt`) must be installed in any fresh shell before running the gate — `pip install --break-system-packages pytest pytest-cov pytest-xdist coverage ruff numpy pandas scipy hypothesis ccxt` (or `pip install -e .[test]` + `ccxt`) as step 0. Do not treat a missing-toolchain shell as a gate failure.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T08:44:25Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record the exact command + output and continue with the next unblocked priority. **Never stop at analysis — every session must produce code, tests, and fresh gate evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = keep the Betting Against Beta (BAB) crypto strategy **ops-ready** (live path dry-run-safe-by-default; default offline/dry-run behavior byte-identical) and **close the remaining coverage/gate gaps to a release-ready state**. The gate is now fast (~6-9 min depending on host) — there is no longer any excuse to skip it. The remaining heavy work is raising real-path coverage on the three lowest files.

**WHERE TO START (this session):** P11 step 1 (baseline) and step 2 (`cli.py` coverage → `tests/test_bab_cli_p11_coverage.py`, `cli.py` **77% → 99%**) are **DONE** — do not repeat them. Begin at **P11 step 3**: `data_sources.py` real uncovered paths → `tests/test_bab_data_sources_p11_coverage.py` (new). Target `data_sources.py` 78% → **≥ 90%** via reachable branches only (see hard targets below).

## Bottleneck removal — DONE & VERIFIED (DO NOT REDO, DO NOT REVERT)

The prior session left the gate effectively un-runnable inside a session budget: `scripts/bab_gate.sh` ran the full suite **serially (~16 min)** and timed out. Two concrete bottlenecks were found and removed in `be9b5c2`, then re-verified this session:

1. **Gate too slow → now parallel.** `scripts/bab_gate.sh` runs `pytest-xdist` (`--dist loadscope`, `nproc` workers) with graceful serial fallback (`BAB_GATE_SERIAL=1`; `BAB_GATE_JOBS=N`). Coverage uses `pytest-cov` with `COVERAGE_CORE=sysmon` on CPython ≥ 3.12 (~2x faster).
2. **Suite was not parallel-safe → fixed distribution-agnostically.** Four modules kept module-level record lists appended by parametrized cells and asserted on full-list length. Under `-n` a worker sees a subset → failures. Fixed via `_*_cell_record(...)` + `_*_records_full()` (recompute deterministically if incomplete on this worker) in:
   - `tests/test_bab_execution_realism_r3.py` (`_r3a_records`/`_r3b_records`)
   - `tests/test_bab_stress_regimes.py` (`_regime_records`)
   - `tests/test_bab_stress_horizon.py` (`_horizon_records`)
   - `tests/test_bab_scale_perf_guard.py` (`_scale_records`)
   **Do not revert this pattern.** Any new module-level record list MUST use the same distribution-agnostic shape.

Also added `scripts/bab_quick.sh` (fast inner-loop: ruff + targeted trio + smoke, ~15s) and declared `pytest-cov`/`pytest-xdist` in `requirements.txt` + `pyproject.toml [test]`.

**Bottleneck removed this session (shell):** the gate could not run at all in a fresh shell because `ruff`/`pytest`/`pytest-cov`/`pytest-xdist`/`coverage`/`hypothesis`/`ccxt` were not installed. Fixed by installing the test toolchain (`pip install --break-system-packages pytest pytest-cov pytest-xdist coverage ruff numpy pandas scipy hypothesis ccxt`, or `pip install -e .[test]` + `ccxt`). Make this step 0 of any fresh session before running the gate; do not treat a missing-toolchain shell as a gate failure.

## Verified state (re-established fresh this session, 2026-11-15T08:44:25Z UTC; re-verify after every change)

- `python3 -m ruff check .` → **clean** (All checks passed) — verified this session.
- `bash scripts/bab_quick.sh` → **green** (ruff clean; targeted trio **104 passed**; smoke **195 passed**, ~26s) — verified this session.
- `bash scripts/bab_gate.sh` → **green at `0551f44`: 5844 passed, 35 skipped, 0 failed, 0 errors; TOTAL 92% in ~9m18s** (parallel xdist, sysmon; ~6m08s reference on faster CI). Per-file coverage below is live evidence from this gate run. Gate toolchain must be installed in the shell first (see header note).
- `python3 scripts/perf_baseline.py --check` → **not re-run this session** (last known `failures: []` per prior handoff); re-run in final gate pass.
- Default offline/dry-run behavior unchanged; live execution safe-by-default (dry-run, env-only creds, no implicit network). Real (non-dry-run) live execution is out of scope.

## Per-file coverage at this HEAD (the real targets)

Fresh gate (missing lines are the actual targets):

- `cli.py` **99%** (555 stmts, 7 missed: 589-590, 746-748, 803-804) — **P11 step 2 DONE, target ≥90% met/exceeded**; remaining misses are stretch only.
- `data_sources.py` **78%** (282 stmts, 62 missed) — 164-165, 169, 173, 230-237, 260, 302-303, 311, 320, 322, 324, 329-330, 347, 366-377, 400-403, 422-427, 431-434, 438-447, 475-480, 483, 487-488, 497-499, 506-507 — **P11 step 3 (NEXT), target ≥90%**.
- `execution.py` **81%** (772 stmts, 145 missed) — 132, 138-144, 148, 153-166, 171-188, 333, 348, 354-355, 380-381, 391-392, 403-404, 423, 452-456, 463-464, 472-473, 479-480, 482, 497-498, 505-506, 532, 543-561, 719, 722-723, 745, 783-784, 827, 836-837, 844, 847-848, 850, 876-880, 893-894, 1047, 1130-1131, 1139, 1151, 1153, 1155, 1157, 1162, 1180-1185, 1190, 1223-1256, 1272, 1281-1288, 1297, 1302, 1307, 1313, 1318, 1380-1381, 1386, 1475, 1477, 1546, 1550 — **P11 step 4, target ≥92%**.
- Secondary: `reconciliation.py` **74%** (49 missed) — 54-84, 103-104, 107-113, 115, 136-137, 294, 318-319, 361, 368, 372, 376 — **P11 step 5, target ≥90%**; `backtest.py` 84%; `beta.py` 85%; `strategy.py` 88%; `risk.py` 89%.
- TOTAL **92%** — target **≥ 93%**.

## Next focus campaign (P11: real failure-path coverage + parallel-safe gate hardening) — HEAVY WORK, DO NOT DEFER

**Goal:** raise coverage on `data_sources.py`, `execution.py` (and secondary `reconciliation.py`) by exercising **genuinely reachable** error/edge branches, and push TOTAL from **92% toward ≥ 93%**, with the fast gate verifying every slice. Keep default offline/dry-run behavior byte-identical. This is multi-hour, multi-diff work — not a single test. `cli.py` is already at 99% (step 2 DONE) and is not a target this campaign.

### Hard coverage targets (gate-verified, per file)
- `data_sources.py` 78% → **≥ 90%**   (step 3 — active now)
- `execution.py` 81% → **≥ 92%**      (step 4)
- `reconciliation.py` 74% → **≥ 90%** (step 5)
- TOTAL **≥ 93%**, with no coverage regression elsewhere (cli.py stays ≥90%).

### Priority order (execute top-down; each step ends with `bab_quick.sh` then a full `bab_gate.sh`)

1. **Re-establish baseline (DONE — steps 1 & 2 complete at `0551f44` — do not repeat unless you make code changes)**
    - `python3 -m ruff check .` → clean
    - `bash scripts/bab_quick.sh` → green (104 + 195 passed)
    - `bash scripts/bab_gate.sh` → green, 5844 passed / 35 skipped / 0 failed / 0 errors, TOTAL 92%, ~9m18s this shell (~6m08s CI reference); per-file coverage recorded above.
2. **`data_sources.py` fetch/parse/error hardening → `tests/test_bab_data_sources_p11_coverage.py` (new).** Retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation — **fakes/mocks only**. Public API stays explicit opt-in with loud failures; `deterministic-offline` default unchanged.
3. **`execution.py` adapter failure modes (dry-run safe) → `tests/test_bab_execution_p11_coverage.py` (new).** `LiveExecutionAdapter` error/rejection/fill/diagnostic branches, risk-gating edges, connector/health edges — **fakes/mocks only; no real network, no credentials, no enabling real execution.**
4. **`reconciliation.py` error branches → `tests/test_bab_reconciliation_p11_coverage.py` (new).** Cost/fill mismatch, missing fills, empty weights — deterministic, no network.
5. **Deprecation hygiene:** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and any others) only if semantics stay identical.
6. **Final gate & handoff refresh:** re-run ruff, `bab_quick.sh`, `bab_gate.sh`, perf guardrail, paper + live dry-run smokes. Update this file with new UTC timestamp, HEAD, exact evidence (counts + per-file coverage deltas for the three targets vs the numbers above), and the next campaign. Keep `AGENT_HANDOFF.md` pointer-only.

**Acceptance (all must hold):** ruff clean; `bab_gate.sh` green (0 failed / 0 errors) in ~6-9 min; the three target files each hit their hard coverage target (`data_sources.py` ≥90%, `execution.py` ≥92%, `reconciliation.py` ≥90%, cli.py stays ≥90%); TOTAL ≥ 93%; no coverage regression elsewhere; perf guardrail `failures: []`; paper + live dry-run smokes pass; default offline/dry-run behavior unchanged.

## Bottlenecks / constraints (do not reopen)

- **No parallel handoff files** — only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. The dead superseded docs were removed; do not recreate them.
- **Gate is fast** — run `scripts/bab_gate.sh` (~6 min); do not reintroduce a serial-only gate or a full-suite timeout excuse. Inner-loop: `scripts/bab_quick.sh`.
- **Parallel-safety is fixed** — do NOT revert the `_*_cell_record`/`_*_records_full` pattern; any new module-level record list must be distribution-agnostic.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Real (non-dry-run) live execution is out of scope; never enable without explicit opt-in and credential review.

## Protocol
1. Read this file fully. 2. Re-establish baseline (`ruff check .`, `bab_quick.sh`, `bab_gate.sh`). 3. Execute the "Next focus campaign" top-down; minimal, tested diffs; every step ends with gate evidence. 4. Never stop at analysis. 5. Keep `AGENT_HANDOFF.md` pointer only.