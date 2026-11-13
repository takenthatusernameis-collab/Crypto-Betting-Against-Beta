# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T02:54:50Z
**HEAD:** `fe8119b chore(kilo): checkpoint agent session` (working tree clean; last work `43a2313` Step 3d committed)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).
**Prioritization:** The repo name is the strategy itself. The gatekeeper hot path is `validate_returns_dataframe` (data_loader.py:1471) — every backtest run must pass validation before any BAB signal/portfolio work. Step 3d (object-frame `_series_is_parseable`) is shipped; the remaining measured leverage is the **numeric-frame** validation hot path = Step 3e.

## CURRENT STATE (verified this session, 2026-11-13T02:54:50Z)

- **Full gate — GREEN:** `python3 -m pytest -q -p no:cacheprovider` → **5130 passed / 35 skipped / RC=0** in 287.64s (single command, no `--ignore`). Warnings are pre-existing (RuntimeWarning, PytestRemovedIn10Warning on class-scoped fixtures).
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

### Bottlenecks removed / next measured hotspots (evidence for Step 3e)

cProfile of `validate_returns_dataframe` (numeric 720x12, 200 runs, this tree): **0.501 s** total. Dominant contributors inside validate:
- `_run_data_quality_campaign` (`data_loader.py:1322`) — 0.186 s cumtime (stale-run / finite-fraction column work, heavy pandas column access).
- `_drop_all_nan_columns` (`data_loader.py:1058`) — 0.064 s cumtime.
- `_normalize_columns` (`data_loader.py:986`) — 0.052 s cumtime (Python per-column normalization/string handling).
- `_max_consecutive_equal_finite` (`data_loader.py:1296`) — 0.061 s cumtime across calls (vectorized but invoked per-column in quality campaign; opportunity to batch on numeric frames).
- Pandas column access/indexing overhead (`frame.__getitem__/_ixs/_get_item`) — ~0.1+ s aggregate inside these helpers.

cProfile of `BABStrategy.run` (30 runs, synthetic 720x12): ~0.133 s total, dominated by `backtest.run_backtest`/`calculate_rolling_beta` and pandas overhead; validate is now a smaller share of end-to-end run.

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
