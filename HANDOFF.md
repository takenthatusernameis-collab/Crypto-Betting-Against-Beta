# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T03:00:20Z
**HEAD:** `951a506 chore(kilo): checkpoint agent session` (working tree clean; last work `43a2313` Step 3d committed)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).

## INITIAL TASK MESSAGE FOR THE NEXT AGENTIC SESSION (timestamped, repo-name-prioritized)

> **Priority basis:** The repository *name* is the strategy — `crypto-betting-against-beta` = the BAB pipeline. Every run of that pipeline funnels through one gatekeeper: `validate_returns_dataframe` (`strategies/betting_against_beta/data_loader.py:1471`). Nothing in the strategy (beta, signals, portfolio, backtest) executes before validation passes. Therefore the highest-leverage work available is to speed up that gatekeeper's remaining measured hotspot.
>
> **Binding next action — Step 3e: optimize the numeric-frame `validate_returns_dataframe` hot path.** Do not defer, do not substitute probe/coverage churn, do not reopen closed campaigns without a new reproducible defect. Execute end-to-end. This is the remaining measured leverage in the BAB data pipeline; the future agent must not avoid it.
>
> **Entry criteria (mandatory before writing code):**
> 1. Re-confirm full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0 (verified this session: **5130 passed / 35 skipped / RC=0**, 287.44s).
> 2. Re-measure isolated baselines (record medians): `validate_returns_dataframe` on numeric 720x12 and 2000x100, plus a cProfile breakdown confirming `_run_data_quality_campaign` (data_loader.py:1322), `_drop_all_nan_columns` (data_loader.py:1058), `_normalize_columns` (data_loader.py:986), `_max_consecutive_equal_finite` (data_loader.py:1296) as the current top contributors.
>
> **Execution plan (measured; choose by evidence, no guessing):**
> 1. Pick the highest-leverage target by measurement (likely `_run_data_quality_campaign` per-column stale/finite checks and/or batching `_max_consecutive_equal_finite` over whole numeric frames, or removing redundant column copies/coercions between helpers). Treat pandas per-column access as the cost driver; prefer whole-frame/numpy operations where semantics are identical.
> 2. Implement a focused optimization preserving exact semantics — see the "Locks / prohibitions" section for what must not change (canonical header mapping, asset-name normalization, duplicate-after-normalization error, all-NaN raise, index/tz/sort, duplicate-timestamp behavior, implausible-return/gap guards, `min_finite_fraction`, stale/frozen detection, every observable error message; no silent behavior changes; broad `except` sweep stays blocked unless tied to a specific reproducible defect + tests).
> 3. Prove correctness & improvement: add/extend oracle-equivalence and regression tests (prefer `tests/test_validation_performance.py` or the most specific existing loader test module) covering mixed dtypes, all-NaN, inf, stale runs at/above threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation. Record before/after medians and cProfile deltas.
> 4. If no meaningful win after a serious measured attempt: stop speculative churn, record concrete evidence (what was tried, numbers), and pivot to the next measured hotspot in the same gate-clean session.
> 5. Full honest gate: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
>
> **Before exit (mandatory):** full gate green; record before/after benchmark + isolated/cProfile numbers (or "no measurable win" with evidence and the next measured target); refresh timestamp/HEAD, shipped/uncommitted changes, residual debt with numbers; keep `AGENT_HANDOFF.md` pointer-only; commit nothing unless explicitly requested.

## CURRENT STATE (verified this session, 2026-11-13T03:00:20Z)

- **Full gate — GREEN:** `python3 -m pytest -q -p no:cacheprovider` → **5130 passed / 35 skipped / RC=0** in 287.44s (single command, no `--ignore`). Re-confirmed at handoff refresh. Warnings are pre-existing (RuntimeWarning, PytestRemovedIn10Warning on class-scoped fixtures).
- **Step 3d-focused tests green:** `tests/test_validation_performance.py` → 15 passed (includes `TestSeriesIsParseableEquivalence` oracle cases).
- **Data-loader regression subset expected green:** `test_bab_data_loader_batch62.py test_bab_data_loader_numeric_qc.py test_bab_data_loader_bottleneck_branches.py test_bab_data_loader_edge_cases.py test_betting_against_beta_data_loader.py test_bab_zero_silent_error.py`.

### Step 3d — `_series_is_parseable` object-frame bottleneck (SHIPPED, COMMITTED, gate-confirmed)

**Change:** `strategies/betting_against_beta/data_loader.py` — `_series_is_parseable` (data_loader.py:1196) now uses a vectorized `pd.to_numeric` cheap pass for plain numeric/NA cells and only falls back to per-cell `_strip_units_and_parse` for non-NA cells `to_numeric` cannot coerce but may be parseable via units/`%`/commas/European-decimal handling. Preserves: 50% threshold (`parseable >= max(1, int(total_non_na * 0.5))`), `None`/NaN treated as parseable and excluded from non-NA total, exact `_strip_units_and_parse` semantics, defensive `try/except: return False` wrapper.

**Proof:** `tests/test_validation_performance.py` extended with `TestSeriesIsParseableEquivalence`.

**Measured (median, 2026-11-13, 2000x100 datetime-indexed frames):**

| metric | before (Step 3c tree) | after (Step 3d) | speedup |
|---|---:|---:|---:|
| `validate_returns_dataframe` (object, all parseable) | 371 ms | **91 ms** | ~4.1x |
| `_series_is_parseable` across all object columns | 306 ms | **30 ms** | ~10.2x |
| `validate_returns_dataframe` (numeric 2000x100) | — | **8.1 ms** | unchanged fast path |
| `BABStrategy.run` synthetic (720x12) | ~3.49 ms | **2.14 ms** | ~1.6x |

Object-frame validation is no longer dominated by parseability; numeric validation remains on its fast path but is now the dominant measurable target inside `validate_returns_dataframe`.

### Baselines re-measured at handoff refresh (2026-11-13T03:00:20Z, medians of 7 runs)

| target | median | min |
|---|---:|---:|
| `validate_returns_dataframe` numeric 720x12 | 1.14 ms | 1.06 ms |
| `validate_returns_dataframe` numeric 2000x100 | 8.64 ms | 8.48 ms |
| `_drop_all_nan_columns` 2000x100 | 0.58 ms | 0.56 ms |
| `_run_data_quality_campaign` 2000x100 | 4.28 ms | 4.26 ms |
| `_normalize_columns` 2000x100 | 0.29 ms | 0.28 ms |
| `_max_consecutive_equal_finite` invoked per-column over 2000x100 | 2.44 ms | 2.43 ms |

**cProfile of `_run_data_quality_campaign` (2000x100, 20 runs, this tree) — 0.132 s total, breakdown:**
- `_run_data_quality_campaign` itself — 0.132 s cumtime.
- `_max_consecutive_equal_finite` — **0.056 s cumtime across 2000 calls** (100 cols × 20 runs). Inside it: `np.unique` 0.031 s + `_unique1d` 0.029 s + `np.sort` 0.007 s. **This is the single biggest lever: it is invoked once per column, and each call re-sorts the whole column.**
- `all(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns)` genexpr — 0.039 s cumtime (80 calls). Replaceable with whole-frame `pd.api.types.is_numeric_dtype(df)`.
- Pandas column access inside the loop — `frame.__getitem__` 0.028 s, `_get_item` 0.021 s, `_ixs` 0.019 s, `iget` 0.009 s. Prefer `to_numpy()` once over the whole frame.

**Step 3e target (highest leverage, evidence-backed):** batch the stale/frozen detection across the whole numeric frame in one pass instead of per-column `_max_consecutive_equal_finite`, and replace the per-column `is_numeric_dtype` genexpr with a whole-frame check. Semantics (threshold `max(stale_run_threshold, 50)`, per-column raise with the exact message) must be preserved exactly.

## NEXT FOCUS CAMPAIGN — Step 3e: optimize numeric-frame `validate_returns_dataframe` hot path (BINDING, HEAVY WORK)

**Initial task for the next agentic session.** Do not defer, do not substitute probe/coverage churn, do not reopen closed campaigns without a new reproducible defect. Execute end-to-end. This is the remaining measured leverage in the BAB data pipeline; the future agent must not avoid it.

### Entry criteria (mandatory before writing code)
1. Re-confirm full gate green on this tree: `python3 -m pytest -q -p no:cacheprovider` → RC=0.
2. Re-measure isolated baselines (record medians): `validate_returns_dataframe` on numeric 720x12 and 2000x100, plus cProfile breakdown confirming `_run_data_quality_campaign`, `_drop_all_nan_columns`, `_normalize_columns`, `_max_consecutive_equal_finite` as current top contributors.

### Execution plan (measured; choose by evidence, no guessing)
1. **Pick one highest-leverage target by measurement** (start with whichever dominates after re-profile on this tree; likely `_run_data_quality_campaign` per-column stale/finite checks and/or batching `_max_consecutive_equal_finite` over numeric frames, or reducing redundant column copies/coercions between helpers). Treat pandas per-column access as the cost driver; prefer whole-frame/numpy operations where semantics are identical.
2. **Implement a focused optimization preserving exact semantics:**
   - `_normalize_columns`: preserve canonical header mapping, asset-name normalization (`_normalize_asset_name`), duplicate-after-normalization detection/error, unnamed-empty-column drop behavior, and idempotence.
   - `_drop_all_nan_columns`: preserve "all NaN => `BABDataError(\"All columns are entirely NaN; no usable return data remains.\")`", keep columns with any finite value, keep object columns carrying non-null data when no finite numerics, defensive fallbacks.
   - `_run_data_quality_campaign`: preserve index normalization/tz handling/sort, duplicate timestamp behavior (`allow_duplicate_timestamps`), implausible-return/gap guards, `min_finite_fraction`, stale/frozen detection semantics (`_max_consecutive_equal_finite`, thresholds), and every observable error message.
   - No silent behavior changes; broad `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
3. **Prove correctness & improvement:** add/extend oracle-equivalence and regression tests (prefer `tests/test_validation_performance.py` or the most specific existing loader test module) covering representative and edge cases for the touched helper(s): mixed dtypes, all-NaN, inf, stale runs at/above threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, and malformed/non-numeric preservation. Record before/after medians and cProfile deltas.
4. **If no meaningful win after a serious, measured attempt:** stop speculative churn, record concrete evidence (what was tried, numbers), and pivot to the next measured hotspot in the same gate-clean session (document which one).
5. **Full honest gate:** `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.

### Before exit (mandatory)
1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + isolated/cProfile numbers for the optimized target (or "no measurable win" with evidence and next measured target).
3. Refresh timestamp/HEAD, shipped/uncommitted changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

## Locks / prohibitions (unchanged)
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. Do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except` — it pins the defensive fallback added in Step 3c.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path (`_drop_all_nan_columns` + `_run_data_quality_campaign`) shipped, gate-confirmed at **5127 passed / RC=0** (`c40dd50`). **Step 3d:** `_series_is_parseable` object-frame hot path vectorized with oracle-equivalence tests, gate-confirmed at **5130 passed / 35 skipped / RC=0** (committed `43a2313`). **Step 4:** `docs/COVERAGE_NOTES.md`.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
