# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T04:12:48Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **Git HEAD (verified):** `7fac037` — the code/bench/gate work is in `be9b5c2` (`7fac037` is a docs pointer on top of it).
- **Branch:** `main`
- **Working tree:** code clean at HEAD `7fac037`; this handoff refresh (`HANDOFF.md`, `AGENT_HANDOFF.md`, `docs/COVERAGE_NOTES.md` reconciled to 90% reality) plus removal of the two dead superseded docs is on disk **uncommitted** (deletions already staged). First act of the next session: `git add -A && git commit -m "docs(handoff): refresh durable handoff + heavy P11 campaign (2026-11-15T04:12:48Z)"`.

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T04:12:48Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_beta*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record the exact command + output and continue with the next unblocked priority. **Never stop at analysis — every session must produce code, tests, and fresh gate evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = keep the Betting Against Beta (BAB) crypto strategy **ops-ready** (live path dry-run-safe-by-default; default offline/dry-run behavior byte-identical) and **close the remaining coverage/gate gaps to a release-ready state**. The gate is now fast (~6 min) — there is no longer any excuse to skip it. The remaining heavy work is raising real-path coverage on the four lowest files.

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

## Verified state (fresh this session, 2026-11-15T04:12:48Z; re-verify after every change)

- `python3 -m ruff check .` → **clean** (All checks passed).
- `bash scripts/bab_quick.sh` → ruff clean; targeted trio **104 passed**; smoke **195 passed** (~14s).
- `bash scripts/bab_gate.sh` → **5796 passed, 35 skipped, 0 failed; TOTAL 90% in 6m07s** (parallel xdist, sysmon coverage; `nproc`=4, Python 3.12.3, xdist 3.8.0).
- `python3 scripts/perf_baseline.py --check` → `failures: []`.
- Default offline/dry-run behavior unchanged; live execution safe-by-default (dry-run, env-only creds, no implicit network). Real (non-dry-run) live execution is out of scope.

## Per-file coverage at this HEAD (the real targets)

Fresh gate (missing lines are the actual targets):

- `cli.py` **77%** (555 stmts, 128 missed) — 34, 36-54, 76, 81-87, 96-123, 213-226, 328-329, 331, 333, 559, 580-581, 583-587, 589-590, 594-595, 599-600, 643, 686-687, 693, 724, 741-784, 803-804, 807-810, 829-859, 903
- `data_sources.py` **78%** (282 stmts, 62 missed) — 164-165, 169, 173, 230-237, 260, 302-303, 311, 320, 322, 324, 329-330, 347, 366-377, 400-403, 422-427, 431-434, 438-447, 475-480, 483, 487-488, 497-499, 506-507
- `execution.py` **81%** (772 stmts, 148 missed) — 132, 138-144, 148, 153-166, 171-188, 333, 348, 354-355, 380-381, 391-392, 403-404, 423, 452-456, 463-464, 472-473, 479-480, 482, 497-498, 505-506, 532, 543-561, 719, 722-723, 745, 783-784, 827, 836-837, 844, 847-848, 850, 876-880, 893-894, 1047, 1130-1131, 1139, 1151, 1153, 1155, 1157, 1162, 1180-1185, 1190, 1223-1256, 1272, 1281-1288, 1297, 1302, 1307, 1313, 1318, 1380-1381, 1386, 1475, 1477, 1546, 1550
- Secondary: `reconciliation.py` **74%** (49 missed) — 54-84, 103-104, 107-113, 115, 136-137, 294, 318-319, 361, 368, 372, 376; `backtest.py` 84%; `beta.py` 85%; `strategy.py` 88%; `risk.py` 89%.

## Next focus campaign (P11: real failure-path coverage + parallel-safe gate hardening) — HEAVY WORK, DO NOT DEFER

**Goal:** raise coverage on `cli.py`, `data_sources.py`, `execution.py` (and secondary `reconciliation.py`) by exercising **genuinely reachable** error/edge branches, and push TOTAL from 90% toward **≥ 93%**, with the fast gate verifying every slice. Keep default offline/dry-run behavior byte-identical. This is multi-hour, multi-diff work — not a single test.

### Hard coverage targets (gate-verified, per file)
- `cli.py` 77% → **≥ 90%**
- `data_sources.py` 78% → **≥ 90%**
- `execution.py` 81% → **≥ 92%**
- `reconciliation.py` 74% → **≥ 90%**
- TOTAL **≥ 93%**, with no regression elsewhere.

### Priority order (execute top-down; each step ends with `bab_quick.sh` then a full `bab_gate.sh`)

1. **Re-establish baseline (mandatory first step, every session)**
   - `python3 -m ruff check .`
   - `bash scripts/bab_quick.sh`
   - `bash scripts/bab_gate.sh` (now ~6 min — run it; record pass/skip/fail, TOTAL %, per-file deltas for the four targets).
2. **`cli.py` real uncovered paths → `tests/test_bab_cli_p11_coverage.py` (new).** Reachable branches only:
   - `_build_adapter` mock-fills parsing (36-54): list-of-dicts, dict-keyed map, malformed JSON/OSError → `BABDataError`; missing `--fills` file.
   - `_json_safe` numpy scalar coercion (328-333) and `_write_json_artifact` failure (81-87).
   - Paper-trading path (741-784): `--paper-trading` without `--output` → exit 1; happy path writes JSONL + `diagnostics.jsonl`.
   - Output/execution/reconciliation artifact write failures (803-810, 829-859): unwritable path → clean exit 1.
   - Exercise via `main(argv)`/`_build_adapter` directly; no behavior change to default path.
3. **`data_sources.py` fetch/parse/error hardening → `tests/test_bab_data_sources_p11_coverage.py` (new).** Retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation — **fakes/mocks only**. Public API stays explicit opt-in with loud failures; `deterministic-offline` default unchanged.
4. **`execution.py` adapter failure modes (dry-run safe) → `tests/test_bab_execution_p11_coverage.py` (new).** `LiveExecutionAdapter` error/rejection/fill/diagnostic branches, risk-gating edges, connector/health edges — **fakes/mocks only; no real network, no credentials, no enabling real execution.**
5. **`reconciliation.py` error branches → `tests/test_bab_reconciliation_p11_coverage.py` (new).** Cost/fill mismatch, missing fills, empty weights — deterministic, no network.
6. **Deprecation hygiene:** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and any others) only if semantics stay identical.
7. **Final gate & handoff refresh:** re-run ruff, `bab_quick.sh`, `bab_gate.sh`, perf guardrail, paper + live dry-run smokes. Update this file with new UTC timestamp, HEAD, exact evidence (counts + per-file coverage deltas for the four targets vs the numbers above), and the next campaign. Keep `AGENT_HANDOFF.md` pointer-only.

**Acceptance (all must hold):** ruff clean; `bab_gate.sh` green (0 failed) in ~6 min; the four target files each hit their hard coverage target; TOTAL ≥ 93%; no coverage regression elsewhere; perf guardrail `failures: []`; paper + live dry-run smokes pass; default offline/dry-run behavior unchanged.

## Bottlenecks / constraints (do not reopen)

- **No parallel handoff files** — only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. The dead superseded docs were removed; do not recreate them.
- **Gate is fast** — run `scripts/bab_gate.sh` (~6 min); do not reintroduce a serial-only gate or a full-suite timeout excuse. Inner-loop: `scripts/bab_quick.sh`.
- **Parallel-safety is fixed** — do NOT revert the `_*_cell_record`/`_*_records_full` pattern; any new module-level record list must be distribution-agnostic.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Real (non-dry-run) live execution is out of scope; never enable without explicit opt-in and credential review.

## Protocol
1. Read this file fully. 2. Commit the refresh first (see Working tree note). 3. Execute the "Next focus campaign" top-down; minimal, tested diffs; every step ends with gate evidence. 4. Never stop at analysis. 5. Keep `AGENT_HANDOFF.md` pointer only.