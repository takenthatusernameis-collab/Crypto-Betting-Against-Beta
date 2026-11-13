# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T07:32:16Z
**HEAD:** `d412bb1283b8562a4b87b3c70ad17e700dc4e07b` (working tree **clean**)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (last verified, recorded):** `bash scripts/bab_gate.sh` → **5144 passed, 35 skipped, RC=0** (303.24s, 2026-11-13T07:24Z, python 3.12.3; coverage not installed). **Re-run gate before and after any shipped change and record the new result.**

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T07:32:16Z) — BINDING, HEAVY WORK REQUIRED (NO EXCUSES):**
> **Execute Step 3f: deliver a real, measured optimization for `BABStrategy.run()` hot spots with production code, oracle-equivalence tests, and a full green gate.** This is not a planning/profiling-only session. For each stage you touch: (1) re-baseline warm median before edit, (2) implement the optimization, (3) add/extend oracle-equivalence tests proving identical behavior on edge cases (NaN/inf/degeneracy/min_obs/tolerance 1e-12, constraints/errors unchanged), (4) add a generous perf-ceiling/non-regression test in the style of `tests/test_beta_performance.py`, (5) run targeted tests, then `bash scripts/bab_gate.sh` RC=0, (6) record before/after medians + delta in this file.
>
> **Required starting order:** `strategies/betting_against_beta/beta.py:331` `calculate_rolling_beta` → `strategies/betting_against_beta/portfolio.py:43` `construct_portfolio` → `strategies/betting_against_beta/backtest.py:9` `run_backtest` (all exercised by `BABStrategy.run`, `strategies/betting_against_beta/strategy.py:211`). Do not stop at measurement: ship at least one stage end-to-end unless you can document a concrete, attempted implementation with evidence of no measurable win; in that case move immediately to the next stage and ship it. Measurement-only, handoff-only, or test-churn-only turns are forbidden. No commits unless explicitly requested.

## Step 3e — SHIPPED / VERIFIED (present in codebase)
- **Code:** `strategies/betting_against_beta/data_loader.py` numeric fast path in `_run_data_quality_campaign` uses vectorized `_max_consecutive_equal_finite_frame` (`:1328`, invoked `:1489`) for stale-run detection; preserves exact `BABDataError` message/ordering and lowest-column-index-first semantics. Secondary whole-frame `is_numeric_dtype` micro-optimization at `:1468`/`:1080` remains low-value/optional only if safe.
- **Tests:** `tests/test_validation_performance.py` includes `TestNumericFrameStaleBatchEquivalence` (multi-column lowest-index-wins, threshold boundary, NaN/inf-split runs, randomized oracle equivalence).
- **Gate (last recorded):** `bash scripts/bab_gate.sh` → **5144 passed, 35 skipped, RC=0** (2026-11-13T07:24Z). Re-run to confirm before/after new work.

**Recorded Step 3e delta (warm medians, 2000×100 numeric frame + BTC, 2026-11-13):** `validate_returns_dataframe` 6.54→**5.61 ms** (~14%), `_run_data_quality_campaign` **1.82 ms**, `_max_consecutive_equal_finite_frame` **1.34 ms**.

## Step 3f — REQUIRED NEXT WORK (exact anchors, heavy implementation)
Re-baseline each stage in this environment before editing (prior numbers are indicative only):
1. `strategies/betting_against_beta/beta.py:331` `calculate_rolling_beta` (~12.1 ms prior): optimize block `to_numpy`/broadcast/rolling paths; preserve per-window degeneracy/min_obs behavior and float tolerance 1e-12.
2. `strategies/betting_against_beta/portfolio.py:43` `construct_portfolio` (~6.4 ms prior): reduce avoidable `copy()`/`to_numpy`/`np.trunc`/`_write_book`/fan-out allocations; preserve dollar-neutrality, turnover/position/gross/net/single-weight limits, and `BABPortfolioError` semantics.
3. `strategies/betting_against_beta/backtest.py:9` `run_backtest` (~2.1 ms prior): optimize `shift(1)`/`fillna`/diff/cost application while preserving lag/no-lookahead, gross/cost/slippage/clipping, finiteness hardening, and column/index alignment.

**End-to-end context:** `strategies/betting_against_beta/strategy.py:211` `BABStrategy.run()` orchestrates load→beta→signals→rebalance→portfolio→shorting/sizing/regime/beta-neutral→finiteness clamp→backtest; do not break pipeline contracts. Use `scripts/perf_bench.py` as a starting pattern if helpful, but prefer stage-level microbenchmarks matching existing perf-test style.

**Deliverables per shipped stage:** implementation + oracle-equivalence tests + perf-ceiling test (generous, CI-stable) + targeted suite pass + full gate RC=0 + recorded before/after warm medians and delta in this section. If no win after genuine attempt, record exact evidence and proceed to next stage immediately.

## Environment / bottlenecks (current)
- **Deps:** numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed** (gate still runs, no coverage report); install only if needed: `pip install coverage`.
- **No active blocker:** working tree clean, Step 3e present, recorded gate green. `research_state/workflow_run_diagnostics.jsonl` is historical/non-blocking.
- **Potential friction:** full gate ~5 min; run targeted tests first, but gate is mandatory before/after shipped code.

## Anti-churn / execution rules (binding)
- **Ship code, not commentary:** progress = merged optimization + tests + green gate + recorded deltas.
- **No** re-profiling of old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts that do not pin real behavior/perf needs.
- **No** reopening historical diagnostics as current failures.
- If a stage yields no measurable win after a genuine implementation attempt, document evidence (what changed, numbers) and immediately move to the next stage; do not stop the session.

## Session exit requirements (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
3. Refresh this file: timestamp, HEAD, gate result, shipped changes, remaining Step 3f anchors/status.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed / locked context (do not reopen without new reproducible failure + evidence)
- C42–C54 closed: full-suite gate discipline, broad-silent audit, `beta.py` perf (`8c2830a`), `construct_portfolio` DN vectorization (`83ff28e`), `validate_returns_dataframe` numeric fast path (`c40dd50`), `_series_is_parseable` vectorized (`43a2313`), `docs/COVERAGE_NOTES.md`.
- **Step 3e (stale-run vectorization) shipped in working tree this session** — `data_loader.py:1483-1498` now uses `_max_consecutive_equal_finite_frame` with lowest-index-first raise semantics; oracle tests added in `tests/test_validation_performance.py`; gate RC=0. Remaining secondary idea: whole-frame `is_numeric_dtype` check at `:1468`/`:1080` (minor, only if safe).

## Before exit (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0.
2. Record before/after warm medians + delta (or evidenced "no measurable win") and next target.
3. Refresh this file: timestamp/HEAD, gate result, shipped/uncommitted changes, residual debt with exact anchors.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**