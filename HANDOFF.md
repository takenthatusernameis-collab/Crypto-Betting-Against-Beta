# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T10:52:00Z
**HEAD:** `314f433` (working tree dirty — this session's edits to `portfolio.py`, `tests/test_portfolio_performance.py`, `tests/test_bab_coverage_campaign7_microgaps.py`; **not committed**)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

**Gate baseline (verified 2026-11-13T10:51Z, with this session's edits):** `bash scripts/bab_gate.sh` → **5173 passed, 35 skipped, RC=0** (301.39s, python 3.12.3; `coverage` not installed → no coverage report). Re-run the gate before and after any shipped change and record the new result here.

---

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T10:52:00Z) — BINDING, HEAVY EXECUTION (NO MEASUREMENT-ONLY / NO CHURN):**
>
> **Mission:** Ship the next real, oracle-equivalent runtime win in the BAB pipeline. `construct_portfolio`'s build path is **now shipped** (broadcast-product book, −16.9% @ 2500×50, −16.1% @ 2500×120, bit-exact vs HEAD). `beta.py` and `signals.py` remain shipped/locked. **Do not reopen any of the three without a new reproducible regression and evidence.**
>
> **Primary target (current top remaining hot spots):** the per-row Python loop in `enforce_beta_neutrality` (`strategies/betting_against_beta/portfolio.py:256-370`) and the repeated `to_numpy(dtype=float)` / index-alignment in `run_backtest` (`strategies/betting_against_beta/backtest.py:39-78`). Measure both at production scale first (2500×40–60 for beta; 2500×50–120 for portfolio/backtest).
>
> **Required execution (complete in this order):**
> 1. **Baseline/profile now:** warm medians at 2500×50 and 2500×120 for `run_backtest` and for `BABStrategy.run` with `enforce_beta_neutrality` exercised (check how `strategy.py:364` calls it — is it hot end-to-end?). cProfile (`-s tottime`) the dominant one. Use `/home/runner/work/_temp/kilo-tmp/` scratch.
> 2. **Implement one materially different optimization** on the chosen hot spot (e.g. vectorize the per-row beta-neutral correction over the `(n,k)` arrays instead of `for i in range(len(common_idx))`; or hoist/reuse `to_numpy(dtype=float)` and shift arrays in `run_backtest`). Do **not** add extra copies or retry known-bad tweaks (`is_numeric_dtype` micro-check, `DataFrame.copy()`).
> 3. **Prove oracle equivalence:** outputs must match current behavior within `1e-12` (incl. NaN/inf/degenerate/tie cases, shape/index/column alignment, unchanged error messages/ordering). Extend/add tests in `tests/test_portfolio_performance.py` (or a dedicated module) with randomized oracle coverage.
> 4. **Add/adjust a generous CI-stable perf-ceiling test** for the optimized path, then run targeted portfolio/perf tests.
> 5. **Gate:** run `bash scripts/bab_gate.sh` → must be **RC=0**. Record pass/skip/RC/time.
> 6. **Record evidence in this file:** before/after warm medians + deltas, what changed, what was disproven, remaining candidates.
>
> **Fallback:** if the chosen target shows no measurable win after a genuine attempt, document numbers, revert non-winning code, and move to the next stage (`enforce_beta_neutrality` ↔ `run_backtest`). Do **not** end the session at profiling.
>
> **Session is incomplete until:** a real implementation attempt is made, oracle equivalence is proven, a perf ceiling exists/holds, full gate is RC=0, and before/after deltas are recorded here. Keep `AGENT_HANDOFF.md` pointer-only and in sync. No commits unless explicitly requested. No edits to `.github/workflows/*`. No tracked probe/debug artifacts at repo root.

## SHIPPED THIS SESSION (2026-11-13T10:52Z) — `construct_portfolio` broadcast-product build
- **What changed:** replaced the `_write_book` `np.repeat`-scatter + boolean-mask fan-out + double-`sum` sanity check with a single broadcast product per side: `w_arr = long_mask * long_w[:,None] + short_mask * short_scale[:,None]` (`portfolio.py:107-132`). Denominators guarded via nested `np.where`; non-DN short side gated by `short_rows`.
- **Why:** the `np.repeat`/`mask & row[:,None]` temporaries + `mask.sum()`/fanned-size checks dominated the profile (cProfile: `_write_book` was the #2 tottime contributor).
- **Oracle equivalence:** bit-exact (`np.array_equal` → True, maxdiff 0.0) vs the HEAD implementation at 2500×50 and 2500×120 for both `dollar_neutral=True/False`, plus NaN/inf/tie/fractional/degenerate cases.
- **Deltas (warm median, 35 reps, same process):** 2500×50 **5.50 → 4.57 ms (−16.9%)**; 2500×120 **13.02 → 10.93 ms (−16.1%)**.
- **Tests:** added `test_portfolio_performance.py::test_portfolio_stage_perf_ceiling` (2500×120 build < 1.0s); updated the two `_write_book`-era failure tests in `test_bab_coverage_campaign7_microgaps.py` to exercise the new build path (long/short build failure still surfaces as `BABPortfolioError`).
- **Disproven / not done:** a full-matrix `np.where` scatter and an in-place `pos/neg` rescale were both slower than the broadcast product; dropping the DN both-block entirely is faster but changes rounding (not bit-exact) and is intentionally **kept** for oracle fidelity.

## Measured baselines (THIS environment, 2026-11-13T10:52Z — production scale 2500×50, warm medians of 35 reps)
- `calculate_rolling_beta` — **3.25 ms** (shipped/locked)
- `generate_bab_signals` — **4.40 ms** (shipped/locked)
- `construct_portfolio` — **4.57 ms @ 2500×50** (was 5.50 ms; **shipped this session**), ~**10.93 ms @ 2500×120** (was 13.02 ms)
- `run_backtest` — **1.79 ms** (next-stage fallback target)
- `BABStrategy.run` (end-to-end, validated path) — **~18.6 ms**

Small-fixture (720×12, `scripts/perf_bench.py`) numbers are stale; always measure at 2500×40–120.

## What is ALREADY shipped (do NOT reopen without a new reproducible failure + evidence)
- `beta.py` `calculate_rolling_beta`: 2-D stacked `_rolling_sum`, hoisted benchmark rolling sums, single `to_numpy(dtype=float)`, per-column finiteness classification in one vectorized pass.
- `portfolio.py` `construct_portfolio`: **broadcast-product equal-weight book (this session)**; DN both-block renormalization + net-fix retained for oracle fidelity.
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection; int8 final scatter; all-zero early return for flat rows. Byte-for-byte vs original over 300 randomized NaN/inf/tie frames.
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover.
- `data_loader.py` `_run_data_quality_campaign`: vectorized `_max_consecutive_equal_finite_frame` stale-run scan, numeric fast path.
- Prior campaigns C42–C55 (`git log --oneline`): full-suite gate discipline, broad-silent audit, beta/portfolio/validation perf, `_series_is_parseable` vectorized, `docs/COVERAGE_NOTES.md`.

## Environment / bottlenecks (current)
- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed**.
- **No active blocker:** tree dirty with the (green) portfolio edits above; gate RC=0 at 5173 passed / 35 skipped.
- **Friction:** full gate ~5 min. Run targeted perf tests first; gate mandatory before/after shipped code.
- **Scratch:** use `/home/runner/work/_temp/kilo-tmp/` (e.g. `bench_portfolio_now.py`). Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.

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
