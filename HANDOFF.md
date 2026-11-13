# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T10:36:11Z
**HEAD:** `36d6eec` (working tree **clean**)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

**Gate baseline (verified 2026-11-13T10:29Z, HEAD 36d6eec):** `bash scripts/bab_gate.sh` → **5172 passed, 35 skipped, RC=0** (303.71s, python 3.12.3; `coverage` not installed → no coverage report). **Re-run the gate before and after any shipped change and record the new result here.**

---

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T10:36:11Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN):**
>
> **Mission:** Ship a real, oracle-equivalent performance improvement in the BAB runtime hot path with full regression protection. This is implementation work, not another survey.
>
> **Primary target (current top hot spot): `construct_portfolio` (`strategies/betting_against_beta/portfolio.py:43`, perf-critical paths around `_write_book` ~110-158 and `enforce_beta_neutrality` ~331-360).** Production-scale warm medians measured 2026-11-13T10:29:56Z @ 2500×50: `beta` 3.25 ms (shipped/locked), `signals` 4.40 ms (shipped/locked), **`portfolio` 3.27 ms** (~11 ms @ 2500×120, optimization pending), `run_backtest` 1.79 ms, `BABStrategy.run` ~18.6 ms. **Do not reopen `beta.py` or `signals.py` without a new reproducible regression and evidence.**
>
> **Required execution (complete in this order):**
> 1. **Baseline/profile now:** capture warm medians for `construct_portfolio` at 2500×50 and 2500×120 (and cProfile at 2500×120, `-s tottime`) in `/home/runner/work/_temp/kilo-tmp/` scratch; identify the dominant cost you will attack (e.g. `_write_book` boolean-mask/repeat scatter, per-row `enforce_beta_neutrality` loop over `i` with 50-step inner iteration, or redundant `weights.loc`/`to_numpy(copy=True)` copies).
> 2. **Implement one materially different optimization** in `construct_portfolio` (vectorized/array-based scatter or hoisted/vectorized beta-neutral correction over `(n,k)` arrays, etc.). **Do NOT retry the known-bad `is_numeric_dtype` dtype-check micro-tweak or add `DataFrame.copy()`/extra copies** — prior attempts measured slower/regressed.
> 3. **Prove oracle equivalence:** outputs must match current behavior within `1e-12` (including NaN/inf/degenerate/tie cases, shape/index/column alignment, and unchanged error messages/ordering where applicable). Extend/add tests in `tests/test_portfolio_performance.py` (row-wise/randomized oracle coverage) as needed.
> 4. **Add/adjust a generous CI-stable perf-ceiling test** for the optimized path (same perf test module unless a better home is required), then run targeted portfolio/perf tests.
> 5. **Gate:** run `bash scripts/bab_gate.sh` → must be **RC=0**. Record pass/skip/RC/time.
> 6. **Record evidence in this file:** before/after warm medians + deltas (2500×50, 2500×120), what changed, what was disproven, and remaining candidates.
>
> **Fallback (only if portfolio shows no measurable win after a genuine attempt):** document numbers/evidence, revert non-winning code, and immediately apply the same cycle to `run_backtest` (`strategies/betting_against_beta/backtest.py:39-78`, repeated `to_numpy(dtype=float)` / index alignment / shift reuse opportunities) — do **not** end the session at profiling.
>
> **Session is incomplete until:** a real implementation attempt is made, oracle equivalence is proven, a perf ceiling exists/holds, full gate is RC=0, and before/after deltas are recorded here. Keep `AGENT_HANDOFF.md` pointer-only and in sync. No commits unless explicitly requested. No edits to `.github/workflows/*`. No tracked probe/debug artifacts at repo root.

## Measured baselines (THIS environment, 2026-11-13T10:29:56Z — production scale 2500×50, warm medians of 25 reps)
- `calculate_rolling_beta` — **3.25 ms**
- `generate_bab_signals` — **4.40 ms** (optimized; orig 4.63 ms, −5.2%)
- `construct_portfolio` — **3.27 ms** (~11 ms at 2500×120; **top non-beta target — OPTIMIZATION PENDING**)
- `run_backtest` — **1.79 ms** (fallback target if portfolio yields no win)
- `BABStrategy.run` (end-to-end, validated path) — **~18.6 ms**
- Signals at 2500×50 / 2000×120: orig 4.63 / 13.48 ms → new 4.39 / 10.75 ms (**−5.2% / −20.3%**)

Small-fixture (720×12, `scripts/perf_bench.py`) numbers from the prior session are stale and are **not** the production truth; always measure at 2500×40–60.

## What is ALREADY shipped (do NOT reopen without a new reproducible failure + evidence)
- `beta.py` `calculate_rolling_beta`: 2-D stacked `_rolling_sum`, hoisted benchmark rolling sums, single `to_numpy(dtype=float)`, per-column finiteness classification in one vectorized pass (`:412-520`).
- `portfolio.py` `construct_portfolio`: removed redundant `signals_df.copy()`, single `to_numpy(dtype=float)`, `np.trunc` on array; `_write_book` vectorized DN path.
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection (dead allocations/guards removed; ranking unchanged). Byte-for-byte vs original over 300 randomized NaN/inf/tie frames (0 mismatches). Recent cleanup removed redundant `DataFrame.copy()`, switched final scatter to `int8` (halves allocation), early-returns all-zero frame for flat rows.
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover, avoiding a second `shift` allocation (`:62-78`).
- `data_loader.py` `_run_data_quality_campaign`: vectorized `_max_consecutive_equal_finite_frame` stale-run scan, numeric fast path.
- Prior campaigns C42–C54 (`git log --oneline`): full-suite gate discipline, broad-silent audit, beta/portfolio/validation perf, `_series_is_parseable` vectorized, `docs/COVERAGE_NOTES.md`.

## Environment / bottlenecks (current)
- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed** (gate runs, no coverage report); `pip install coverage` only if needed.
- **No active blocker:** tree clean at `36d6eec`, gate green (5172 passed / 35 skipped / RC=0).
- **Friction:** full gate ~5 min. Run targeted perf tests first; gate is mandatory before/after shipped code.
- **Scratch:** use `/home/runner/work/_temp/kilo-tmp/` for new probe scripts. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root (existing ones are scratch).

## Anti-churn / execution rules (binding)
- **Ship code, not commentary:** progress = measured win + oracle tests + perf-ceiling test + green gate + recorded deltas.
- **Do not** re-optimize beta or signals; they are shipped and locked.
- **No** re-profiling old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- If a stage yields no measurable win after a genuine implementation attempt, document evidence and immediately move to the next stage; do not stop the session.

## Session exit requirements (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0 (record pass/skip/RC/time).
2. Record per-stage before/after warm medians + delta, or evidenced no-win with next action taken.
3. Refresh this file: timestamp, HEAD, gate result, shipped changes, remaining candidates/status.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
