# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T05:37:40Z
**HEAD:** `74447c4 chore(kilo): checkpoint agent session` (working tree: handoff docs refreshed this session; last substantive code commit `43a2313` Step 3d)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (last verified at prior handoff, 2026-11-13T04:46:06Z):** `bash scripts/bab_gate.sh` → **5140 passed, 35 skipped, RC=0**. Not re-run this session (docs-only refresh); re-run as the first correctness check before/after any Step 3e/3f code change.

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T05:37:40Z):**
> **Ship Step 3e performance code in `strategies/betting_against_beta/data_loader.py`** and land it with oracle-equivalence coverage + a full green gate — no measurement-only churn. Then immediately begin Step 3f (end-to-end pipeline hot spots). Commit nothing unless explicitly requested. This is the binding focus campaign: validation/pipeline overhead is the top leverage for a BAB repo; do not spend the session on probe-count expansion or re-profiling work already recorded below.

## Priority basis (repo name first)

The repository name *is* the strategy: `crypto-betting-against-beta`. Every pipeline run passes through `validate_returns_dataframe` (`strategies/betting_against_beta/data_loader.py:1515`) before beta/signal/portfolio/backtest work can start. Validation/pipeline hot-path performance is the top remaining engineering leverage.

**Authoritative warm baseline (this container, 2026-11-13T04:45Z, 31-run medians on 2000x100 numeric frame; from prior verified handoff):**

| target | warm median |
|---|---:|
| `validate_returns_dataframe` | **7.40 ms** (p10 7.37 / p90 7.48) |
| `_max_consecutive_equal_finite_frame` helper (`data_loader.py:1328`, unused) | **2.44 ms** |
| `_normalize_columns` | 0.26 ms |
| gap `Series.diff` check | 0.04 ms |
| `is_numeric_dtype` genexpr (100 calls) | 0.045 ms |
| frame `copy` | 0.04 ms |

cProfile (20 calls, 2000x100): `_run_data_quality_campaign` 97 ms cumulative; `_max_consecutive_equal_finite_frame` 46 ms (cumsum 23 ms); `_normalize_columns` 36 ms; dtype `is_numeric_dtype` ≈13 ms; `Series.diff` gap ≈2 ms; `DataFrame.copy` ≈25 ms (pandas block copies). **Do not re-run to "confirm"; measure only before/after changes you ship.**

## Current state / blockers removed this refresh
- Single durable handoff is refreshed, timestamped, and points at one concrete heavy-work campaign (Step 3e code → Step 3f). No active blocker in-repo; main prior bottleneck was measurement-only churn (profiled but not shipped) — anti-churn rules below are binding.
- `research_state/workflow_run_diagnostics.jsonl` shows historical successful scheduled runs with captured log-signal excerpts (old heads/tool-arg noise); **treat as historical diagnostics, not current failures**. No current reproducible gate failure recorded in-tree.
- Working tree had only this handoff refresh at write time; keep it clean except intentional Step 3e/3f changes.

## Step 3e — optimize `validate_returns_dataframe` numeric path (BINDING, ship code)

**Code reality on this tree (verified):** gap check already uses `index.to_numpy(dtype="datetime64[ns]")` + `np.diff` (`data_loader.py:1429-1434`); numeric fast path already does per-column stale scans over qualifying columns via `_max_consecutive_equal_finite` (`1463-1478`, `_max_consecutive_equal_finite_frame` at `1328` is currently unused); `validate_returns_dataframe` already hoists `arr = cleaned.to_numpy(dtype=float, copy=False)` (`1665`) and passes it into `_run_data_quality_campaign` (`1716-1724`), which reuses it for abs checks (`1412`). Remaining work is to exploit this layout and remove residual overhead/allocation while preserving semantics.

### Required work (implement, test, gate, record — in one pass)
1. **Whole-frame numeric dtype check (micro, easy win):** replace `all(pd.api.types.is_numeric_dtype(dt) for dt in cleaned.dtypes)` at `data_loader.py:1449` with `pd.api.types.is_numeric_dtype(cleaned.dtypes)` or an equivalent single check over the dtype object/index. Preserve behavior for mixed/object frames.
2. **Stale-run path (PRIMARY hot spot by profile):** `_max_consecutive_equal_finite` is called per qualifying column in the numeric fast path (`1471-1473`) and per-column fallback (`1485-1506`). Reduce overhead without changing results: avoid per-column pandas conversions in fallback (`pd.to_numeric(...).to_numpy`/`cleaned[col].to_numpy` at `1485-1492`) by slicing/reusing the already-available numeric `arr`/`arr2` where the frame is numeric/coerced; consider a tighter vectorized/NumPy per-column run scan that avoids Python-level object churn but keeps exact max-run semantics (finite-only, reset on NaN/inf or value change). `_max_consecutive_equal_finite_frame` (`1328-1359`) is unused — either delete it or replace with a lower-allocation implementation used by the fast path; do not keep dead heavy code.
3. **Reduce redundant frame copies/conversions:** `_run_data_quality_campaign` unconditionally copies `df` (`1376`) and may coerce/sort again even when called from `validate_returns_dataframe` after normalization/coercion; add a safe internal fast path/flags or restructure so validate does not pay duplicate copy/sort/to_datetime work on an already-clean numeric frame. Any shortcut must preserve: returned-frame independence for callers that mutate input, duplicate-timestamp handling, tz normalization, index sort, error messages/types, and benchmark/quality semantics.
4. **Redundant `to_numpy` in campaign:** when `arr` is provided, avoid `arr_all = arr if arr is not None else cleaned.to_numpy(dtype=float)` producing a second materialization path that defeats reuse; ensure inf/abs checks and finite masks operate on one view consistently (`1412`, `1450`, `1665`).
5. **Do NOT churn `_normalize_columns`:** warm cost ~0.26 ms; leave unless a correctness-preserving simplification falls out naturally.

### Correctness gates (must hold)
- Preserve existing behavior/error contracts: `BABDataError` messages/types/raise ordering where observable, duplicate handling, tz normalization, index sort, benchmark checks, NaN/inf rejection, finite-fraction/stale-run thresholds, lenient `allow_duplicate_timestamps`, and numeric-vs-fallback parity.
- Extend `tests/test_validation_performance.py` (or add focused oracle tests) for: all-NaN columns, mixed dtypes, inf/-inf, stale runs at/above/below threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation, empty/single-row frames, and mutation-independence of returned frames.
- Keep `TestMaxConsecutiveEqualFiniteFrameOracle`/stale-run oracle coverage green (adjust only if helper API intentionally changes but semantics remain equivalent).
- Run targeted validation/perf-oracle tests, then full gate: `bash scripts/bab_gate.sh` → **RC=0**, single command, no ignores (or `python3 -m pytest -q -p no:cacheprovider`).
- Record before/after warm medians + cProfile/isolation delta in this file (or "no measurable win" with hard evidence, then proceed immediately to Step 3f).

## Step 3f — end-to-end `BABStrategy.run()` overhead (follow-on, start after 3e)

Pipeline stage anchors (re-measure before changing): `construct_portfolio` ~6.4 ms (`portfolio.py:43`), `calculate_rolling_beta` ~12.1 ms (`beta.py:331`), `run_backtest` ~2.1 ms (`backtest.py:9`). `_apply_rebalance` matters mainly for non-daily configs.

1. **`calculate_rolling_beta` (`beta.py:331`):** evaluate replacing per-column/to_numpy fan-out and temporaries (e.g. `y_df.mul(bench_arr[:, None], axis=0)`) with one block `returns_df[finite_cols].to_numpy()` multiply/broadcast path where semantics are identical. Preserve per-window degeneracy/min_obs behavior and float outputs (tolerance 1e-12).
2. **`construct_portfolio` (`portfolio.py:43`):** inspect `signals_df.copy()`, `to_numpy`, `np.trunc`, and `_write_book` fan-out for avoidable allocations/copies. Preserve dollar-neutrality, turnover/position/gross limits, and `BABPortfolioError` behavior/messages.
3. **`run_backtest` (`backtest.py:9`):** evaluate `weights.shift(1)`/`fillna` allocation vs NumPy/concat/in-place equivalent. Preserve gross/cost/slippage columns and clipping semantics.
4. For any changed stage: add oracle-equivalence tests + generous-ceiling perf/timing checks (pattern: `tests/test_beta_performance.py`); run full gate.

## Anti-churn / execution rules (binding)
- **Do not** spend this session re-measuring/re-profiling the baseline above except to record before/after for code you actually change now.
- **Do not** reopen probe-count campaigns, rotate C-numbers, or add "no reduction identified" logs. Do not append tests unless they pin a real behavior/perf-oracle need for shipped changes.
- **Do** treat historical entries in `research_state/workflow_run_diagnostics.jsonl` as non-blocking context only.
- If Step 3e yields no measurable win after a genuine attempt, document evidence and move immediately to Step 3f item 1; never idle.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path shipped, gate-confirmed at **5127 passed** (`c40dd50`). **Step 3d:** `_series_is_parseable` object-frame hot path vectorized, gate-confirmed at **5137 passed / 35 skipped** (committed `43a2313`). **Step 4:** `docs/COVERAGE_NOTES.md`.
- **Step 3e (measured, not shipped):** baseline/profile recorded above at 2026-11-13T04:45Z; implementation remains open (this handoff's binding task).

## Locks / prohibitions (unchanged)
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. Do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Before exit (mandatory for next session)
1. Run targeted tests for changed code, then full gate `bash scripts/bab_gate.sh` (or `python3 -m pytest -q -p no:cacheprovider`) → RC=0, single command, no ignores.
2. Record before/after warm medians + delta for optimized target(s), or "no measurable win" with evidence and the next measured target.
3. Refresh this file: timestamp/HEAD, gate result, shipped/uncommitted changes, residual debt with numbers and exact file anchors.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**