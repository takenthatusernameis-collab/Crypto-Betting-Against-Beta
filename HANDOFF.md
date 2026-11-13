# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T06:06:18Z
**HEAD:** `584eba1 chore(kilo): checkpoint agent session` (working tree clean at refresh except this handoff update)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Last recorded gate (do not assume current):** `bash scripts/bab_gate.sh` → **5140 passed, 35 skipped, RC=0** (recorded 2026-11-13T06:02:00Z in prior pointer/state). Re-run as the first and final correctness check for any code changes this session.

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T06:06:18Z) — BINDING:**
> **Ship Step 3e performance code in `strategies/betting_against_beta/data_loader.py`** (optimize `validate_returns_dataframe` / `_run_data_quality_campaign` numeric path) with oracle-equivalence tests and a full green gate. **Then immediately start Step 3f** hot spots in `beta.py:331` (`calculate_rolling_beta`), `portfolio.py:43` (`construct_portfolio`), `backtest.py:9` (`run_backtest`) if Step 3e is landed or blocked by hard evidence. No measurement-only churn, no probe-count expansion, no commits unless explicitly requested.

## Priority basis (repo name first)
Repository purpose is the BAB strategy. All runs flow through `validate_returns_dataframe` (`strategies/betting_against_beta/data_loader.py`) before beta/signal/portfolio/backtest stages, so validation/pipeline overhead is the highest-leverage engineering work.

**Authoritative warm baseline (2026-11-13T04:45Z, this container, 31-run medians, 2000x100 numeric frame — do not re-measure except before/after shipped changes):**
- `validate_returns_dataframe`: **7.40 ms** (p10 7.37 / p90 7.48)
- `_max_consecutive_equal_finite_frame` helper (`data_loader.py:1328`, currently unused): **2.44 ms**
- `_normalize_columns`: 0.26 ms (leave alone)
- gap `Series.diff` check already NumPy-based: ~0.04 ms
- `is_numeric_dtype` loop/genexpr cost material (~0.045 ms / 100 calls context)
- frame `copy` / block copies material (~0.04–25 ms in profiles depending on path)

cProfile (20 calls, 2000x100): `_run_data_quality_campaign` dominates; stale-run scan, copies/coercions, and repeated numeric materialization are main costs.

## Bottlenecks removed / current blockers
- **Removed (process bottleneck):** prior sessions spent effort profiling without shipping. This handoff makes Step 3e code+tests+gate the mandatory first deliverable and forbids re-profiling churn.
- **No active reproducible in-repo blocker recorded.** `research_state/workflow_run_diagnostics.jsonl` contains historical diagnostics only; treat as non-blocking context.
- `AGENT_HANDOFF.md`/`HANDOFF.md` were stale vs HEAD — refreshed now as the single coordination point.

## Step 3e — `validate_returns_dataframe` numeric path (REQUIRED WORK)
**Current code reality (verified):** gap check uses `index.to_numpy(dtype="datetime64[ns]")`+`np.diff`; numeric fast path scans qualifying columns via `_max_consecutive_equal_finite` per-column (`~1471-1473`) and fallback paths also do per-column conversions (`~1485-1506`); `validate_returns_dataframe` hoists `arr`/`finite_arr` and passes to `_run_data_quality_campaign` (`~1665,1716-1724`) but campaign still has redundant/re-materializing paths (`arr_all`/`finite_all` handling, unconditional `df.copy()`/sort/coerce, numeric branch recomputes/allocates). `_max_consecutive_equal_finite_frame` (`1328`) is unused/dead heavy code.

1. **Whole-frame numeric dtype check:** replace `all(pd.api.types.is_numeric_dtype(dt) for dt in cleaned.dtypes)` (`~1449`) with a single dtype check (e.g. `pd.api.types.is_numeric_dtype(cleaned.dtypes)` or equivalent) preserving mixed/object behavior.
2. **Stale-run hot path:** eliminate per-column overhead while preserving exact semantics (finite-only, reset on NaN/inf/value change, same thresholds/raise ordering/messages). Prefer reusing the hoisted numeric `arr`/`arr2` in fast/fallback paths (avoid `pd.to_numeric(...).to_numpy` per column when frame is already numeric/coerced). Implement a tight NumPy/vectorized scan or a lower-allocation per-column routine; delete or replace unused `_max_consecutive_equal_finite_frame` (no dead heavy helper left behind).
3. **Remove redundant copy/coercion/sort in campaign:** `_run_data_quality_campaign` unconditionally copies and may re-normalize/sort/coerce index even when called from `validate_returns_dataframe` on an already-normalized frame. Add a safe internal fast path/flags so validate avoids duplicate work **without breaking**: returned-frame independence for callers mutating inputs, duplicate-timestamp handling, tz normalization, index sort, error types/messages/ordering where observable, benchmark/quality semantics.
4. **Single numeric view reuse:** when `arr`/`finite_mask` are provided, ensure inf/abs checks, finite masks, and stale/fraction logic operate on one consistent view without extra materializations (`~1412`, `~1450`, `~1665`, numeric branch).
5. **Do not churn `_normalize_columns`** (~0.26 ms) unless a correctness-preserving simplification is incidental.

### Step 3e correctness gates (must hold)
- Preserve contracts: `BABDataError` behavior where observable, duplicate handling, tz normalization, index sort, benchmark checks, NaN/inf rejection, finite-fraction/stale-run thresholds, lenient `allow_duplicate_timestamps`, numeric-vs-fallback parity.
- Add/extend oracle coverage in `tests/test_validation_performance.py` (or focused tests): all-NaN cols, mixed dtypes, inf/-inf, stale runs at/above/below threshold, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation, empty/single-row frames, and **mutation-independence** of returned frames.
- Keep existing stale-run/oracle tests green (adapt only if helper API changes but semantics remain equivalent).
- Run targeted tests for touched areas, then **full gate**: `bash scripts/bab_gate.sh` → **RC=0** (or `python3 -m pytest -q -p no:cacheprovider`).
- Record before/after warm medians + delta (or "no measurable win" with hard evidence) in this file and proceed to Step 3f.

## Step 3f — end-to-end `BABStrategy.run()` hot spots (start after 3e)
Re-measure before changing; prior anchors: `calculate_rolling_beta` ~12.1 ms (`beta.py:331`), `construct_portfolio` ~6.4 ms (`portfolio.py:43`), `run_backtest` ~2.1 ms (`backtest.py:9`).

1. **`beta.py:331` `calculate_rolling_beta`:** replace per-column/to_numpy fan-out and temporaries with a block `to_numpy`/broadcast path where semantics identical. Preserve per-window degeneracy/min_obs behavior and float outputs (tol 1e-12).
2. **`portfolio.py:43` `construct_portfolio`:** reduce avoidable `copy()`/`to_numpy`/`np.trunc`/`_write_book` fan-out allocations. Preserve dollar-neutrality, turnover/position/gross limits, `BABPortfolioError` behavior/messages.
3. **`backtest.py:9` `run_backtest`:** evaluate `weights.shift(1)`/`fillna` allocation vs NumPy/in-place/concat equivalent preserving gross/cost/slippage and clipping semantics.
4. For each changed stage: oracle-equivalence tests + generous perf ceiling checks (pattern `tests/test_beta_performance.py`), full gate.

## Anti-churn / execution rules (binding)
- **Do not** re-profile/re-measure recorded baselines except before/after code you ship now.
- **Do not** reopen probe-count campaigns, rotate C-numbers, or add "no reduction identified" logs/tests that do not pin real behavior/perf-oracle needs.
- **Do not** treat historical `research_state/workflow_run_diagnostics.jsonl` entries as current failures.
- If Step 3e yields no measurable win after a genuine implementation attempt, document evidence and move immediately to Step 3f item 1 (never idle).

## Completed / locked context (do not reopen without new reproducible failure + evidence)
- C42–C54 history closed per prior campaigns: full-suite gate discipline, broad-silent audit, `beta.py` perf (`8c2830a`), `construct_portfolio` DN vectorization (`83ff28e`), `validate_returns_dataframe` numeric fast path (`c40dd50`), `_series_is_parseable` vectorized (`43a2313`), `docs/COVERAGE_NOTES.md` recorded.
- **Step 3e baseline measured 2026-11-13T04:45Z but optimization not yet shipped** — this is the open binding task.

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Before exit (mandatory)
1. Run targeted tests for changed code, then `bash scripts/bab_gate.sh` (or `python3 -m pytest -q -p no:cacheprovider`) → RC=0.
2. Record before/after warm medians + delta (or evidenced "no measurable win") and next target.
3. Refresh this file: timestamp/HEAD, gate result, shipped/uncommitted changes, residual debt with exact anchors.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
