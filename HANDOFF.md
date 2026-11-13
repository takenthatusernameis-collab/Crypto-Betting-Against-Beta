# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T02:10:00Z
**HEAD:** `83ff28e chore(kilo): checkpoint agent session`
**Working tree (dirty, uncommitted):** `strategies/betting_against_beta/data_loader.py` (validation vectorization, +64 lines), `tests/test_validation_performance.py` (new, 12 tests). **Commit nothing unless the user explicitly asks.**
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).

## CURRENT STATE (verified this session, 2026-11-13)

- **Full gate — GREEN:** `python3 -m pytest -q -p no:cacheprovider` → **5127 passed / 35 skipped / RC=0** in 286s (single command, no `--ignore`). Verified *after* all Step 3c edits below.
- **Targeted verification (RC=0):**
  - `tests/test_validation_performance.py` → **12 passed**.
  - Data-loader regression subset (`test_bab_data_loader_batch62.py test_bab_data_loader_numeric_qc.py test_bab_data_loader_bottleneck_branches.py test_bab_data_loader_edge_cases.py test_betting_against_beta_data_loader.py test_bab_zero_silent_error.py`) → **99 passed / 6 skipped**.
  - Portfolio/perf subset still green (`test_portfolio_performance.py`, `test_beta_performance.py`, `test_beta_perf_numpy_cache.py`).

### Step 3c — validation-hotspot optimization (implemented, measured, gate-confirmed)

**Target:** fresh 20-run cProfile after Step 3b showed `validate_returns_dataframe` was the new **#1 hotspot** — 0.078s of 0.167s (**47%**) of `BABStrategy.run`, driven by two per-column Python loops:
- `data_loader._drop_all_nan_columns` (0.019s)
- `data_loader._run_data_quality_campaign` finite/stale loop (0.030s)

**Change (in `data_loader.py`):** added a vectorized **numeric fast path** to both functions, gated by `all(is_numeric_dtype(col) …)` (the common case after `_coerce_numeric`):
- `_drop_all_nan_columns`: one `to_numpy(dtype=float)` pass → `np.isfinite(...).any(axis=0)` keep-mask with `pd.isna` non-null fallback; raises the identical "All columns are entirely NaN" error; returns `df` unchanged when all columns survive.
- `_run_data_quality_campaign`: one pass computing per-column `finite_counts`; `min_finite_fraction` raise and stale-run raise reproduced **in the same column order and with identical messages**; stale check still calls the vectorized `_max_consecutive_equal_finite` per candidate column.

**Contract preserved (do not reopen without a new reproducible defect + durable evidence):** both fast paths are wrapped in `try/except BABDataError: raise / except Exception: pass` so any access failure (e.g. a `DataFrame` subclass whose `__getitem__` raises — see `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`) falls back to the original slow per-column branch, which is itself defensive. Non-numeric/object frames always take the slow branch unchanged.

**Durable regression added:** `tests/test_validation_performance.py` — explicit per-column oracle equivalence for both functions across representative numeric frames and edge cases (all-NaN, inf, mixed dtypes, object non-null, all-columns-NaN raise, empty passthrough, `min_finite_fraction`/stale raises, `stale_run_threshold=0` skip), plus non-flaky perf guards.

**Measured (median, 2026-11-13T02:05Z):**

| stage | before | after | speedup |
|---|---|---|---|
| `_drop_all_nan_columns` (720x12) | 0.295 ms | 0.072 ms | **~4.1x** |
| `_run_data_quality_campaign` (720x12) | 0.606 ms | 0.421 ms | **~1.4x** |
| `validate_returns_dataframe` (720x12) | 1.502 ms | 1.013 ms | **~1.5x** |
| `validate_returns_dataframe` (2000x100) | 10.924 ms | 6.799 ms | **~1.6x** |
| full `BABStrategy.run` (720x12, `perf_bench.py`) | 4.05 ms | **3.49 ms** | ~1.16x |
| cProfile validate (20 runs, 720x12) | 0.078 s / 47% | 0.056 s / 38% | — |

(`calculate_rolling_beta` 0.70 ms and tracemalloc peak 0.73 MB unchanged; allocation-neutral.)

**What is closed (do not reopen without a new reproducible defect + durable evidence):**
`beta.py` rolling-OLS (`8c2830a`). `construct_portfolio` vectorized DN fixup (Step 3b, `83ff28e`). `validate_returns_dataframe` numeric fast path for `_drop_all_nan_columns` + `_run_data_quality_campaign` (Step 3c, working tree, gate-confirmed). Broad-silent `except` sweep stays blocked (C54 Step 2 — no justified conversions).

## NEXT FOCUS CAMPAIGN — Step 3d: kill the `_series_is_parseable` object-frame bottleneck (BINDING, HEAVY WORK)

Validation is now ~38% of a numeric-frame run and **~95% of an object/string-frame run**. The measured next #1 hotspot is **`data_loader._series_is_parseable`** (`data_loader.py:1196`), which loops **per cell** in Python and calls `_strip_units_and_parse` (regex per cell). On a 2000x100 object frame it is **~272 ms of a ~290 ms validate call (≈94%)**; it is called from `validate_returns_dataframe` twice (pre-coerce junk drop + post-`_coerce_numeric` failure fallback) and is skipped only for already-numeric dtypes.

### Required execution plan (end-to-end, measured; no probe/coverage churn)

1. **Confirm baseline on current tree:** `python3 -m pytest -q -p no:cacheprovider` (RC=0). Then measure `_series_is_parseable` in isolation on 2000x100 **object** and **string-dtype** frames, and full `validate_returns_dataframe` on the same. Record medians.
2. **Reproduce the cost precisely:** confirm the two call sites (`data_loader.py:1554` junk-drop loop and `:1571` `_coerce_numeric` failure fallback) and that object/string frames reach them while numeric frames do not.
3. **Implement one focused optimization** that preserves exact semantics: a column is parseable iff `parseable >= max(1, int(total_non_na * 0.5))` where `None`/NaN count as parseable and a cell is parseable iff `_strip_units_and_parse` does not raise. Candidates (choose by measurement, do **not** guess):
   - Vectorize the cheap majority case with pandas/numpy (e.g. try `pd.to_numeric(..., errors='coerce')` first; only fall back to per-cell `_strip_units_and_parse` for columns that fail or that need unit/`%`/comma handling).
   - Short-circuit: a column that is already numeric dtype is parseable by definition (avoids the call entirely at the call sites).
   - If a per-cell pass is unavoidable, reduce Python overhead (hoist regex/lookups, operate on numpy arrays) while keeping the 50% threshold and NaN/None rules identical.
   **Preserve exactly:** threshold, `None`/NaN-as-parseable rule, the `_strip_units_and_parse` return/raise behavior, and every observable error message.
4. **Prove correctness & improvement:** extend `tests/test_validation_performance.py` with an oracle equivalence test for `_series_is_parseable` (per-cell `_strip_units_and_parse` oracle) across: numeric, numeric-strings, units (`$`/`%`/commas/European decimals), NA markers, malformed numerics (`1.2.3`), pure garbage (`abc`), and the 50%-boundary. Record before/after medians. If no meaningful win after a serious attempt, record concrete evidence and stop — no speculative churn.
5. **Full honest gate:** `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.

### Locks / prohibitions (unchanged)

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. **New:** do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except` — it pins the defensive fallback added in Step 3c.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path (`_drop_all_nan_columns` + `_run_data_quality_campaign`) shipped in working tree with oracle-equivalence tests, gate-confirmed at **5127 passed / RC=0**. **Step 4:** `docs/COVERAGE_NOTES.md`.

## Before exit (mandatory)

1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + cProfile/isolated numbers for any perf work in this handoff (or state "no measurable win" with evidence).
3. Refresh timestamp/HEAD, shipped changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**