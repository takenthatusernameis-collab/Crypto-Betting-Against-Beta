# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T04:46:06Z
**HEAD:** `f99de99 chore(kilo): checkpoint agent session` (working tree clean; last substantive work `43a2313` Step 3d)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (verified this session):** `bash scripts/bab_gate.sh` → **5140 passed, 35 skipped, RC=0** (207 s, single command).

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T04:46:06Z):**
> **Ship the code for Step 3e** — reduce `validate_returns_dataframe` from ~7.4 ms to ≤4 ms median (warm) on the 2000x100 numeric gate frame. The measurement/profiling phase is **DONE and verified** (numbers below are warm medians of 31 runs). Do **not** spend this session re-measuring or re-profiling: go straight to implementation, add oracle-equivalence tests, run the full gate, and record before/after numbers. Then proceed to Step 3f. Commit nothing unless explicitly requested.

## Priority basis (repo name first)

The repository name *is* the strategy: `crypto-betting-against-beta`. Every pipeline run passes through `validate_returns_dataframe` (`strategies/betting_against_beta/data_loader.py:1509`) before any beta/signal/portfolio/backtest work can start. The validation gate is therefore the highest-leverage remaining optimization target.

**Measured on this tree (warm medians of 31 runs, this container, 2026-11-13T04:45Z — replaces the cold-start numbers in the prior handoff):**

| target (2000x100 numeric frame) | warm median |
|---|---:|
| `validate_returns_dataframe` | **7.40 ms** (p10 7.37 / p90 7.48) |
| `_max_consecutive_equal_finite_frame` (stale-run helper) | **2.44 ms** (p10 2.42 / p90 2.45) |
| `_normalize_columns` | 0.26 ms |
| `Series.diff` gap check | 0.04 ms |
| `is_numeric_dtype` genexpr (100 calls) | 0.045 ms |
| frame `copy` | 0.04 ms |

cProfile of 20 calls on 2000x100: `_run_data_quality_campaign` 97 ms cumulative; `_max_consecutive_equal_finite_frame` 46 ms (cumsum 23 ms of it); `_normalize_columns` 36 ms; dtype genexpr `is_numeric_dtype` ≈13 ms; `Series.diff` gap ≈2 ms; `DataFrame.copy` ≈25 ms (mostly pandas block copies).

**Correction to the prior handoff:** earlier figures (`validate 7.95 ms`, `stale-run 2.67 ms`) were cold-start; the warm numbers above are the authoritative baseline. The stale-run helper is confirmed the **dominant** cost (~33% of validate).

## Step 3e — optimize numeric-frame `validate_returns_dataframe` (BINDING, measured, ship code)

### Entry criteria (already satisfied — do not re-run to "confirm" unless a code change needs it)
1. `python3 -m pytest -q -p no:cacheprovider tests/test_validation_performance.py` → RC=0 (25 passed on this tree at 04:45Z).
2. Warm medians recorded above.
3. cProfile ordering confirmed above: stale-run first, `_normalize_columns` second, dtype genexpr third, gap `Series.diff` fourth.

### Work items (ship ALL that the profile supports — expect ~1.8–2x on the gate)
1. **Stale-run fast path (PRIMARY — ~2.44 ms of 7.4 ms):** `_max_consecutive_equal_finite_frame` (`data_loader.py:1324`) materializes an `(n, m)` bool `changed`, an `(n, m)` int64 `group_id` (`cumsum`), and an `(n, m)` int64 broadcast `col_idx`, then a flat `bincount` — ~4.8 MB of temporaries on 2000x100. Replace with a per-column run scan that avoids the full-frame `cumsum`: only process columns whose `finite_counts >= stale_run_threshold` (already computed at the call site), and compute per-column max run via boundary diffs (`np.diff` on change positions) without the `(n,m)` `cumsum`/`bincount` temporaries. Preserve exact output (int64 ndarray, per-column max, 0 for all-non-finite/empty).
2. **Whole-frame dtype check:** replace `all(pd.api.types.is_numeric_dtype(dt) for dt in cleaned.dtypes)` (`data_loader.py:1446`) with a single `pd.api.types.is_numeric_dtype(cleaned.dtypes)` over the dtype Index.
3. **Gap check:** `cleaned.index.to_series().diff()` (`data_loader.py:1424`) allocates a Series per call. Use `cleaned.index.to_numpy(dtype="datetime64[ns]")` + `np.diff`, compare against `max_gap_days * 86400e9`; preserve the existing error message exactly (format `{max_gap_days_actual:.2f}` / `{float(max_gap_days):.2f}`).
4. **Redundant conversions:** `_run_data_quality_campaign` copies the frame and calls `cleaned.to_numpy(dtype=float)` (abs check); `validate_returns_dataframe` later calls `np.isinf(cleaned.to_numpy())` (`data_loader.py:1656`) and `np.isfinite(cleaned.to_numpy(dtype=float, copy=False))` (`data_loader.py:1721`). Hoist one `to_numpy(dtype=float)` view and reuse it; keep `copy=False`/read-only where safe. Callers must still receive an independent frame when they mutate the input.
5. **Do NOT over-optimize `_normalize_columns`:** warm cost is only 0.26 ms; leave it unless it falls out of another change.

### Correctness gates
- Add oracle-equivalence tests to `tests/test_validation_performance.py` covering: all-NaN columns, mixed dtypes, inf/-inf, stale runs at/above/below threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation, empty and single-row frames.
- Keep `TestMaxConsecutiveEqualFiniteFrameOracle` green (randomized per-column oracle, `data_loader.py`-level).
- Full gate: `bash scripts/bab_gate.sh` → RC=0, single command, no ignores. (Or `python3 -m pytest -q -p no:cacheprovider`.)
- Record before/after warm medians + cProfile delta here.

## Step 3f — end-to-end `BABStrategy.run()` overhead (follow-on, only after 3e code is landed)

**Why:** the repo is the BAB pipeline, not just validation. Measured stage costs show the next leverage after validation: `construct_portfolio` 6.4 ms and `calculate_rolling_beta` 12.1 ms on 2000x100; `run_backtest` 2.1 ms. `_apply_rebalance` is only active for non-daily configs.

**Targets (choose by re-measurement, not by assumption):**
1. `calculate_rolling_beta` (`beta.py:331`): the finite-asset fast path already vectorizes; verify whether the per-column `returns_df[c].to_numpy()` loop and the `y_df.mul(bench_arr[:, None], axis=0)` temporary can be replaced by one `returns_df[finite_cols].to_numpy()` + `arr * bench_arr[:, None]`. Preserve per-window degeneracy/min_obs semantics and exact float output (tolerance 1e-12).
2. `construct_portfolio` (`portfolio.py:37`): the numeric fast path is already vectorized; check `signals_df.copy()` + `to_numpy` + `np.trunc` allocations and the `_write_book` fan-out. Preserve dollar-neutrality, turnover/position limits, and `BABPortfolioError` messages.
3. `run_backtest` (`backtest.py:8`): `weights.shift(1)` + `fillna(0.0)` allocate a full frame; use `np.concatenate`/in-place ops where semantics are identical. Preserve gross/cost/slippage columns and `clip(lower=-1+1e-12)` behavior.
4. Add stage-level timing tests with generous ceilings (like `tests/test_beta_performance.py`) and oracle-equivalence tests for any changed math.

## Anti-churn clause (removes the prior bottleneck)

The previous session measured and profiled Step 3e but shipped no code — that measurement-only churn is the bottleneck. For this session:
- **Do not** re-run the warm benchmark/cProfile to "confirm" the numbers above; they are already verified at 2026-11-13T04:45Z.
- **Do** implement, test, gate, and record in one pass. If you must re-measure, do it only for the specific change you just made (before/after of that one function).
- If Step 3e yields no measurable win after a genuine attempt, record "no measurable win" with the before/after evidence and move immediately to Step 3f item 1 (never idle in re-profiling).

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path shipped, gate-confirmed at **5127 passed** (`c40dd50`). **Step 3d:** `_series_is_parseable` object-frame hot path vectorized, gate-confirmed at **5137 passed / 35 skipped** (committed `43a2313`). **Step 4:** `docs/COVERAGE_NOTES.md`.
- **Step 3e (prior handoff):** measured and profiled only; no code shipped. Targets remain open and are re-baselined above.

## Locks / prohibitions (unchanged)
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. Do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except` — it pins the defensive fallback from Step 3c.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Before exit (mandatory for the next session)
1. Full gate green: `bash scripts/bab_gate.sh` (or `python3 -m pytest -q -p no:cacheprovider`) → RC=0, single command, no ignores.
2. Record before/after warm medians + isolated/cProfile numbers for the optimized target (or "no measurable win" with evidence and the next measured target).
3. Refresh timestamp/HEAD, shipped/uncommitted changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**