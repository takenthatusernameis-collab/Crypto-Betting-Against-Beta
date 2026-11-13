# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T04:35:23Z
**HEAD:** `918c6bc chore(kilo): checkpoint agent session` (clean working tree at handoff write; last substantive work: `43a2313` Step 3d)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T04:35:23Z):**
> Execute **Step 3e — reduce `validate_returns_dataframe` from ~8 ms to ≤4 ms median on the 2000x100 numeric gate frame**, then **Step 3f — reduce `BABStrategy.run()` end-to-end synthetic-path overhead**. This is the next heavy-work campaign. Work through the measured plan below end-to-end; do not substitute probe/coverage churn, do not reopen closed campaigns without a new reproducible defect, do not edit workflows or weaken locked tests, and commit nothing unless explicitly requested.

## Priority basis (repo name first)

The repository name *is* the strategy: `crypto-betting-against-beta`. Every run of that pipeline passes through `validate_returns_dataframe` (`strategies/betting_against_beta/data_loader.py:1509`) before any beta/signal/portfolio/backtest work can start. The validation gate is therefore the highest-leverage remaining optimization target.

**Measured on this tree (medians of 7 runs, this container):**

| target | 720x12 | 2000x100 | 4000x200 |
|---|---:|---:|---:|
| `validate_returns_dataframe` | 0.71 ms | **7.95 ms** | 18.9 ms |
| `_run_data_quality_campaign` | 0.26 ms | **4.38 ms** | 11.8 ms |
| `_drop_all_nan_columns` | 0.02 ms | 0.08 ms | 0.18 ms |
| `_normalize_columns` | 0.06 ms | 0.28 ms | 0.58 ms |
| `_max_consecutive_equal_finite_frame` only | 0.07 ms | **2.67 ms** | 7.6 ms |

cProfile of 20 calls on 2000x100: `_run_data_quality_campaign` 73 ms cumulative; `_max_consecutive_equal_finite_frame` 47 ms (cumsum 19 ms, its own body 25 ms); `all(is_numeric_dtype(col) for col in cleaned.columns)` genexpr ≈3 ms; `Series.diff` for gap check ≈2 ms; `DataFrame.copy` ≈2 ms.

**Pipeline baseline (synthetic, this container):** 720x12 `beta` 2.1 ms, `signals` 0.4 ms, `portfolio` 0.4 ms, `backtest` 1.5 ms. 2000x100: `beta` 12.1 ms, `signals` 3.4 ms, `portfolio` 6.4 ms, `backtest` 2.1 ms. `BABStrategy.run()` is ~2.1 ms on 720x12 and ~24 ms on 2000x100; validation is ~8 ms of that 2000x100 run.

## Step 3e — optimize numeric-frame `validate_returns_dataframe` (BINDING, measured)

### Entry criteria
1. `python3 -m pytest -q -p no:cacheprovider tests/test_validation_performance.py` → RC=0 (25 passed on this tree at 04:35Z).
2. Re-measure the table above; record medians in this file before changing code.
3. Run `python3 -m cProfile` (or equivalent) and confirm the same ordering: stale-run computation first, dtype genexpr second, gap `Series.diff` third.

### Work items (expected ~2–4x win, do all that measurement supports)
1. **Stale-run fast path (primary):** `_max_consecutive_equal_finite_frame` (data_loader.py:1324) materializes an `(n, m)` bool `changed` array, an `(n, m)` int64 `group_id`, and an `(n, m)` int64 broadcast `col_idx`, then a flat `bincount`. On 2000x100 that is ~4.8 MB of temporary arrays and the dominant cost. Replace with a per-column run scan that avoids the full `cumsum` when possible — e.g. compute `(arr[1:] != arr[:-1])` per column only for columns with `finite_counts >= stale_run_threshold` (already known at the call site), or compute the run length with `np.max` over `np.diff`-style boundaries without the `cumsum`/`bincount` temporaries. Preserve exact output (int64 ndarray, per-column max, 0 for all-non-finite/empty).
2. **Whole-frame dtype check:** replace `all(pd.api.types.is_numeric_dtype(dt) for dt in cleaned.dtypes)` (data_loader.py:1446) with `pd.api.types.is_numeric_dtype(cleaned.dtypes)` — one call over the dtype Index instead of 100 Python calls.
3. **Gap check:** `cleaned.index.to_series().diff()` (data_loader.py:1424) allocates a Series per call. Use `cleaned.index.to_numpy(dtype="datetime64[ns]")` and `np.diff` in nanoseconds, compare against `max_gap_days * 86400e9`; preserve the existing error message exactly.
4. **Avoid redundant copies/conversions:** `_run_data_quality_campaign` copies the frame and calls `cleaned.to_numpy(dtype=float, copy=False)`; `validate_returns_dataframe` then calls `np.isinf(cleaned.to_numpy())` and `np.isfinite(cleaned.to_numpy(...))` again. Hoist one conversion where safe, or use `copy=False`/read-only views; do not change observable semantics (callers must still receive an independent frame when they mutate the input).

### Correctness gates
- Add oracle-equivalence tests to `tests/test_validation_performance.py` (or the most specific existing loader module) covering: all-NaN columns, mixed dtypes, inf/-inf, stale runs at/above/below threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation, empty and single-row frames.
- Keep `TestMaxConsecutiveEqualFiniteFrameOracle` green (randomized per-column oracle).
- Full gate: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
- Record before/after medians + cProfile delta here.

## Step 3f — end-to-end `BABStrategy.run()` overhead (follow-on, only after 3e)

**Why:** the repo is the BAB pipeline, not just validation. Measured stage costs show the next leverage after validation: `construct_portfolio` 6.4 ms and `calculate_rolling_beta` 12.1 ms on 2000x100; `run_backtest` 2.1 ms. `_apply_rebalance` is only active for non-daily configs.

**Targets (choose by re-measurement, not by assumption):**
1. `calculate_rolling_beta` (beta.py:331): the finite-asset fast path already vectorizes; verify whether the per-column `returns_df[c].to_numpy()` loop and the `y_df.mul(bench_arr[:, None], axis=0)` temporary can be replaced by one `returns_df[finite_cols].to_numpy()` + `arr * bench_arr[:, None]`. Preserve per-window degeneracy/min_obs semantics and exact float output (tolerance 1e-12 in tests).
2. `construct_portfolio` (portfolio.py:37): the numeric fast path is already vectorized; check `signals_df.copy()` + `to_numpy` + `np.trunc` allocations and the `_write_book` fan-out. Preserve dollar-neutrality, turnover/position limits, and the `BABPortfolioError` messages.
3. `run_backtest` (backtest.py:8): `weights.shift(1)` + `fillna(0.0)` allocate a full frame; use `np.concatenate`/in-place operations where semantics are identical. Preserve gross/cost/slippage columns and the `clip(lower=-1+1e-12)` behavior.
4. Add stage-level timing tests with generous ceilings (like `tests/test_beta_performance.py`) and oracle-equivalence tests for any changed math.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path (`_drop_all_nan_columns` + `_run_data_quality_campaign`) shipped, gate-confirmed at **5127 passed / RC=0** (`c40dd50`). **Step 3d:** `_series_is_parseable` object-frame hot path vectorized with oracle-equivalence tests, gate-confirmed at **5137 passed / 35 skipped / RC=0** (committed `43a2313`). **Step 4:** `docs/COVERAGE_NOTES.md`.
- **Step 3e partial (this handoff):** measured and profiled only; no code changes shipped. The stale-run frame helper, dtype genexpr, gap diff, and redundant conversions remain the documented targets.

## Locks / prohibitions (unchanged)
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. Do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except` — it pins the defensive fallback added in Step 3c.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Before exit (mandatory for the next session)
1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + isolated/cProfile numbers for the optimized target (or "no measurable win" with evidence and the next measured target).
3. Refresh timestamp/HEAD, shipped/uncommitted changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
