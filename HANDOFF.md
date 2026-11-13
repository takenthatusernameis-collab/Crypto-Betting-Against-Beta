# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T10:28:47Z
**HEAD:** `4fcaaaa` (working tree **clean**)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

**Gate baseline (verified):** `bash scripts/bab_gate.sh` → **5172 passed, 35 skipped, RC=0** (302.30s, python 3.12.3; `coverage` not installed → gate runs without a coverage report). **Re-run the gate before and after any shipped change and record the new result here.**

---

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T10:28:47Z) — BINDING, HEAVY WORK REQUIRED (NO MEASUREMENT-ONLY TURNS, NO CHURN):**
>
> **The current top production-scale hot spot is `construct_portfolio` (`portfolio.py:43`), NOT beta and NOT signals anymore.** Measured warm medians at 2500×50 (this environment): `beta` 3.25 ms, `signals` 4.40 ms, `portfolio` **3.27 ms** (~11 ms at 2500×120), `run_backtest` 1.79 ms. End-to-end `BABStrategy.run` ~18.6 ms. Do **not** re-open beta or signals: `beta.py` and `signals.py` are shipped and locked (see "What is ALREADY shipped").
>
> **Your actual job: ship one end-to-end stage optimization for `construct_portfolio`, with oracle tests + perf ceiling + full gate, OR (if it yields no win) for `run_backtest`'s repeated `to_numpy(dtype=float)`/index alignment (`backtest.py:39-78`), and record evidence for anything skipped.**
>
> 1. **Do NOT do the trivial `is_numeric_dtype` dtype-check micro-tweak.** A prior attempt plus a `trunc`-equality cleaning path measured **slower** and was reverted. The real cost is elsewhere: profile `construct_portfolio` at 2500×120 with `cProfile` (`python -m cProfile -s tottime`), and look at:
>    - the `_write_book` fan-out and `np.repeat` / boolean-mask assignment (`portfolio.py:110-158`), and
>    - the **per-column Python loops** in `enforce_beta_neutrality` (`portfolio.py:331-360`, one 50-iteration inner loop per row) and `enforce_beta_neutrality`'s `weights.loc[common_idx, common_cols]` / `to_numpy(copy=True)` (two full copies of the weights+beta frames).
> 2. **Try a genuinely different implementation** (e.g. build the weight matrix with `np.add.at` / `np.repeat`-free per-row scatter, or hoist the beta-neutral correction into a single vectorized pass over the `(n,k)` arrays instead of the per-row `for i in range(len(common_idx))` loop with a 50-step inner iteration). Measure warm medians before/after.
> 3. **Prove oracle equivalence** to the current implementation on the 2500×120 fixture and on randomized inputs with NaN/inf/degeneracy, tolerance `1e-12`, unchanged error messages/ordering (`tests/test_portfolio_performance.py` has a row-wise oracle; extend it).
> 4. **Add a generous, CI-stable perf-ceiling test** in `tests/test_portfolio_performance.py` (or a new class there), then run targeted tests, then full `bash scripts/bab_gate.sh` RC=0. Record before/after warm medians + delta here.
> 5. If `construct_portfolio` yields no measurable win after a genuine implementation attempt, record the evidence (what you tried, the numbers) and **immediately move to `run_backtest` / the next candidate**; do NOT stop the session at measurement/profiling only.
>
> **Trap to avoid:** the raw `beta_arr`/`signals_arr` are already minimal; do not re-add `DataFrame.copy()` "just in case" (it is a real cost). Do not re-implement beta's stacked `_rolling_sum_finite` or signals' double-argsort.
>
> **This task is mandatory and non-deferrable.** The session is not complete until: a real implementation attempt is made, oracle equivalence is proven, a perf-ceiling test exists, the full gate is RC=0, and before/after numbers + deltas are recorded in this file.

## Measured baselines (THIS environment, 2026-11-13T10:28:47Z — production scale 2500×50, warm medians of 25 reps)
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
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection (dead allocations/guards removed; ranking unchanged). Byte-for-byte vs original over 300 randomized NaN/inf/tie frames (0 mismatches).
- `backtest.py` `run_backtest`: reuses `w_shifted` for turnover, avoiding a second `shift` allocation (`:62-78`).
- `data_loader.py` `_run_data_quality_campaign`: vectorized `_max_consecutive_equal_finite_frame` stale-run scan, numeric fast path.
- Prior campaigns C42–C54 (`git log --oneline`): full-suite gate discipline, broad-silent audit, beta/portfolio/validation perf, `_series_is_parseable` vectorized, `docs/COVERAGE_NOTES.md`.

## Environment / bottlenecks (current)
- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage` **not installed** (gate runs, no coverage report); `pip install coverage` only if needed.
- **No active blocker:** tree clean at `4fcaaaa`, gate green (5172 passed / 35 skipped / RC=0).
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
