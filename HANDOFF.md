# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T06:35:30Z
**HEAD:** `230e2c07d1379d29367fb73e362da29c131a87ca` (working tree **dirty** — uncommitted Step 3e changes below)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (verified this session, NOT assumed):** `bash scripts/bab_gate.sh` → **5144 passed, 35 skipped, RC=0** (313.09s, 2026-11-13T06:35Z, python 3.12.3; coverage not installed). Re-run gate before/after any further change.

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T06:35:30Z) — BINDING, HEAVY WORK REQUIRED:**
> **Start Step 3f (end-to-end `BABStrategy.run()` hot spots) with shipped code + oracle-equivalence/perf-ceiling tests + full green gate.** Do not re-profile the recorded Step 3e baselines except before/after code you ship. Measurement-only or handoff-only churn is forbidden. No commits unless explicitly requested.

## Step 3e — SHIPPED IN WORKING TREE (uncommitted), verified
- **Code:** `strategies/betting_against_beta/data_loader.py:1483-1498` — replaced per-column Python stale-run loop in `_run_data_quality_campaign` numeric fast path with vectorized ` _max_consecutive_equal_finite_frame(arr2)` scan; raises on lowest column index meeting threshold, preserving exact `BABDataError` message/ordering. Secondary dtype-check micro-optimization (`:1468`/`:1080`) not done (low value).
- **Tests:** `tests/test_validation_performance.py` extended with `TestNumericFrameStaleBatchEquivalence` cases: multi-column lowest-index-wins, threshold boundary (at/ below), NaN/inf-split runs, randomized stale-vs-oracle equivalence (40 seeds). Targeted suites passed (validation perf 29, related loader/quality 130).
- **Gate:** `bash scripts/bab_gate.sh` → **5144 passed, 35 skipped, RC=0**.

**Measured delta (warm medians, 2000×100 numeric frame + BTC, same container, 2026-11-13):**
| Measurement | Before (prior handoff) | After (this session) |
|---|---:|---:|
| `validate_returns_dataframe` | 6.54 ms (p10 6.47 / p90 6.66) | **5.61 ms** (p10 5.17 / p90 5.99) |
| `_run_data_quality_campaign` | — (dominant inside validate) | **1.82 ms** (p10 1.80 / p90 1.88) |
| `_max_consecutive_equal_finite_frame` (full 2000×100) | n/a | **1.34 ms** (p10 1.33 / p90 1.37) |

Validate improved ~14%; stale scan now vectorized (no per-column Python loop on clean numeric frames).

## Step 3f — REQUIRED NEXT WORK (exact anchors, start here)
Re-measure each stage before changing; prior anchors (pre-3e context, re-baseline before edits):
1. `strategies/betting_against_beta/beta.py:331` `calculate_rolling_beta` (~12.1 ms prior): block `to_numpy`/broadcast path; preserve per-window degeneracy/min_obs, float tol 1e-12.
2. `strategies/betting_against_beta/portfolio.py:43` `construct_portfolio` (~6.4 ms prior): reduce avoidable `copy()`/`to_numpy`/`np.trunc`/`_write_book` allocations; preserve dollar-neutrality, turnover/position/gross limits, `BABPortfolioError`.
3. `strategies/betting_against_beta/backtest.py:9` `run_backtest` (~2.1 ms prior): `weights.shift(1)`/`fillna` vs NumPy/in-place equivalent; preserve gross/cost/slippage/clipping.

Per stage: oracle-equivalence + generous perf-ceiling tests (pattern `tests/test_beta_performance.py`), then full gate `bash scripts/bab_gate.sh` RC=0. Record before/after warm medians + delta here.

## Environment / bottlenecks (current)
- **Deps present:** `pip install -r requirements.txt` done earlier (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis). `coverage` not installed (gate runs without coverage report). Optional: `pip install coverage`.
- **No active blocker:** gate green, Step 3e delivered. `research_state/workflow_run_diagnostics.jsonl` is historical/non-blocking context only.

## Anti-churn / execution rules (binding)
- **Do not** re-profile/re-measure recorded baselines except before/after code you ship now.
- **Do not** reopen probe-count campaigns, rotate C-numbers, or add "no reduction identified" logs/tests that do not pin real behavior/perf-oracle needs.
- **Do not** treat historical `research_state/workflow_run_diagnostics.jsonl` entries as current failures.
- If a Step 3f item yields no measurable win after genuine implementation, document evidence here and move to next item (never idle).

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