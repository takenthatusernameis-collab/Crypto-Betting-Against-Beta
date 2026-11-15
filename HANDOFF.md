# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T03:58:53Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD (at refresh):** `be9b5c2` (this refresh; gate/parallel-safety work committed)
- **Branch:** `main`
- **Working tree:** clean at this HEAD; full gate re-run GREEN (5796 passed / 35 skipped / 90%).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T03:58:53Z UTC) — BINDING

This is the only active task. Execute top-down. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new parallel handoff/session docs. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

Repo-prioritized mission: `Crypto-Betting-Against-Beta` = keep the Betting Against Beta (BAB) crypto strategy ops-ready (live path dry-run-safe-by-default, default offline/dry-run behavior unchanged) and close remaining coverage/gate gaps to a release-ready state.

## What this session changed (bottleneck removal — DO NOT REDO)

The prior session left the gate effectively un-runnable inside a session budget: `scripts/bab_gate.sh` ran the full suite **serially (~16 min)** and timed out. Two concrete bottlenecks were found and removed:

1. **Gate too slow.** Rewrote `scripts/bab_gate.sh` to run **parallel by default**:
   - `pytest-xdist` with `--dist loadscope` (each module pinned to one worker) across `nproc` workers, with graceful fallback to serial if `xdist`/`pytest-cov` are absent (`BAB_GATE_SERIAL=1` forces serial; `BAB_GATE_JOBS=N` overrides worker count).
   - Coverage via `pytest-cov`, using `COVERAGE_CORE=sysmon` on CPython ≥ 3.12 (same line data, ~2x faster: full gate **~6 min** vs ~13 min with the C tracer).
   - Result: full gate now **5796 passed / 35 skipped / TOTAL 90% in ~6m08s**.
2. **Suite was not parallel-safe (would fail under any `-n`).** Four test modules kept **module-level record lists** appended by parametrized cells and asserted on full-list length in a summary test. Under xdist a worker sees only a subset → `KeyError`/`AssertionError`. Fixed distribution-agnostically in:
   - `tests/test_bab_execution_realism_r3.py` (`_r3a_records`/`_r3b_records`)
   - `tests/test_bab_stress_regimes.py` (`_regime_records`)
   - `tests/test_bab_stress_horizon.py` (`_horizon_records`)
   - `tests/test_bab_scale_perf_guard.py` (`_scale_records`)
   Pattern: per-cell work extracted to a `_*_cell_record(...)` function; a `_*_records_full()` helper returns the accumulated list **if complete on this worker, else recomputes deterministically**. Verified GREEN serial, `-n 4`, `-n 8` (default and loadscope).

Also added `scripts/bab_quick.sh` (fast inner-loop: ruff + targeted trio + smoke, ~15s) and declared `pytest-cov`/`pytest-xdist` in `requirements.txt` + `pyproject.toml [test]` extra.

## Verified state (as of 2026-11-15T03:58:53Z; re-verify after changes)

- `python3 -m ruff check .` → **clean**.
- `bash scripts/bab_quick.sh` → ruff clean, targeted trio 104 passed, smoke 195 passed (~15s).
- `bash scripts/bab_gate.sh` → **5796 passed, 35 skipped, TOTAL 90%, ~6m08s** (parallel, sysmon coverage).
- Perf guardrail `python3 scripts/perf_baseline.py --check ...` → `failures: []`.
- Default offline/dry-run behavior unchanged; live execution safe-by-default (dry-run, env-only creds, no implicit network).
- Prior serial baseline (still valid): full suite 5796/35/0 failed; coverage 90%.

## Per-file coverage at this HEAD (target the real gaps)

From the fresh gate run (missing lines are the actual targets):

- `cli.py` **77%** (555 stmts, 128 missed) — lines 34, 36-54, 76, 81-87, 96-123, 213-226, 328-329, 331, 333, 559, 580-581, 583-587, 589-590, 594-595, 599-600, 643, 686-687, 693, 724, 741-784, 803-804, 807-810, 829-859, 903
- `data_sources.py` **78%** (282 stmts, 62 missed) — 164-165, 169, 173, 230-237, 260, 302-303, 311, 320, 322, 324, 329-330, 347, 366-377, 400-403, 422-427, 431-434, 438-447, 475-480, 483, 487-488, 497-499, 506-507
- `execution.py` **81%** (772 stmts, 148 missed) — 132, 138-144, 148, 153-166, 171-188, 333, 348, 354-355, 380-381, 391-392, 403-404, 423, 452-456, 463-464, 472-473, 479-480, 482, 497-498, 505-506, 532, 543-561, 719, 722-723, 745, 783-784, 827, 836-837, 844, 847-848, 850, 876-880, 893-894, 1047, 1130-1131, 1139, 1151, 1153, 1155, 1157, 1162, 1180-1185, 1190, 1223-1256, 1272, 1281-1288, 1297, 1302, 1307, 1313, 1318, 1380-1381, 1386, 1475, 1477, 1546, 1550
- Also low but secondary: `reconciliation.py` **74%** (49 missed), `backtest.py` **84%**, `beta.py` **85%**, `strategy.py` **88%**, `risk.py` **89%**.

## Next focus campaign (P11: coverage of real failure paths + parallel-safe gate hardening) — HEAVY WORK, DO NOT DEFER

**Goal:** raise coverage on `cli.py`/`data_sources.py`/`execution.py` (and secondary `reconciliation.py`) by exercising **genuinely reachable** error/edge branches, with the gate now fast enough to verify each slice. Keep default offline/dry-run behavior byte-identical.

### Priority order (execute top-down)

1. **Re-establish baseline (mandatory first step)**
   - `python3 -m ruff check .`
   - `bash scripts/bab_quick.sh`
   - `bash scripts/bab_gate.sh` (now ~6 min — no longer an excuse to skip; record pass/skip/fail, TOTAL %, per-file deltas).
2. **`cli.py` 77% → real uncovered paths.** Add focused tests for reachable branches only:
   - `_build_adapter` mock-fills parsing (`cli.py` 36-54): list-of-dicts, dict-keyed map, malformed JSON/OSError → `BABDataError`; missing `--fills` file.
   - `_json_safe` numpy scalar coercion (328-333) and `_write_json_artifact` failure (81-87).
   - Paper-trading path (741-784): `--paper-trading` without `--output` → exit 1; happy path writes JSONL + `diagnostics.jsonl`.
   - Output/execution/reconciliation artifact write failures (803-810, 829-859): simulate unwritable path → clean exit 1.
   - Exercise via `main(argv)`/`_build_adapter` directly; no behavior change to default path.
3. **`data_sources.py` 78% → fetch/parse/error hardening.** Add tests for retry/rate-limit/backoff, HTTP 4xx/5xx, non-JSON/invalid candle payload, empty window, partial-symbol coverage, schema/monotonic validation — using fakes/mocks only. Public API must remain explicit opt-in with loud failures; default `deterministic-offline` unchanged.
4. **`execution.py` 81% → adapter failure modes (dry-run safe).** Add tests for `LiveExecutionAdapter` error/rejection/fill/diagnostic branches, risk-gating edges, connector/health edges — **fakes/mocks only; no real network, no credentials, no enabling real execution.**
5. **`reconciliation.py` 74% → reconcile error branches** (cost/fill mismatch, missing fills, empty weights) — deterministic, no network.
6. **Deprecation hygiene:** migrate `pd.Timestamp.utcnow` → `pd.Timestamp.now("UTC")` in `tests/test_bab_data_freshness.py` (and any others) only if semantics stay identical.
7. **Final gate & handoff refresh:** re-run ruff, `bab_quick.sh`, `bab_gate.sh`, perf guardrail, paper + live dry-run smokes. Update this file with new UTC timestamp, HEAD, exact evidence (counts + coverage deltas for the target files), and the next campaign. Keep `AGENT_HANDOFF.md` pointer-only.

**Acceptance:** ruff clean; `bab_gate.sh` green (0 failed) in ~6 min; coverage improved on `cli.py`/`data_sources.py`/`execution.py` (and `reconciliation.py`) with no regression elsewhere; perf guardrail `failures: []`; paper + live dry-run smokes pass; default offline/dry-run behavior unchanged.

## Bottlenecks / constraints (do not reopen)

- **No parallel handoff files** — only `HANDOFF.md` canonical; `AGENT_HANDOFF.md` pointer-only. `AGENT_TASK_2026-11-14.md`, `HANDOFF_TASK_20261114.md` SUPERSEDED — do not edit.
- **Gate is fast now** — run `scripts/bab_gate.sh`; do not reintroduce a serial-only gate or a full-suite timeout excuse. For inner-loop use `scripts/bab_quick.sh`.
- **Parallel-safety is fixed** — do NOT revert the `_*_cell_record`/`_*_records_full` pattern in the 4 test modules; any new module-level record list must use the same distribution-agnostic pattern.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- Canonical CLI: `python3 -m strategies.betting_against_beta.cli`.
- Real (non-dry-run) live execution is out of scope; never enable without explicit opt-in and credential review.

## Protocol
1. Read this file fully. 2. Execute "Next focus campaign" top-down; minimal, tested diffs. 3. Never stop at analysis. 4. Keep `AGENT_HANDOFF.md` pointer only.