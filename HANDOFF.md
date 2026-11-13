# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T06:30:30Z
**HEAD:** `1ace2b50f6fe5087a98cc4dec182bbefa8095bd6` (working tree clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Gate (verified this session, NOT assumed):** `bash scripts/bab_gate.sh` → **5140 passed, 35 skipped, RC=0** (306.65s, 2026-11-13T06:30Z, at HEAD `1ace2b5`, container python 3.12.3).

> **INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T06:30:30Z) — BINDING, HEAVY WORK REQUIRED:**
> **Ship the Step 3e performance code in `strategies/betting_against_beta/data_loader.py` (stale-run scan) with oracle-equivalence tests and a full green gate.** The profiling below (done this session) shows the dominant cost is a per-column **Python** loop, not copies. Do not re-profile the recorded baselines except before/after your own change. Measurement-only or handoff-only churn is forbidden. No commits unless explicitly requested.

## Why this is the highest-leverage work (repo-name priority)

Repository purpose is the BAB strategy. **Every** run — synthetic, CSV, prices, CLI — funnels through `validate_returns_dataframe` before beta/signal/portfolio/backtest. It is the shared hot path, so its overhead dominates end-to-end latency.

## Verified evidence (measured in this container, 2026-11-13T06:24–06:30Z)

Warm medians, 2000×100 numeric frame + BTC col, after `validate_returns_dataframe` warm-up:

| Measurement | Value |
|---|---|
| `validate_returns_dataframe` (full call) | **6.54 ms** (p10 6.47 / p90 6.66) |
| 1× `_max_consecutive_equal_finite` over all 100 cols | **3.29 ms** (≈50% of full call) |
| 1× `arr2[:, j]` slicing only (100 cols) | 0.013 ms (negligible) |

cProfile (20 calls, same frame) top self-time:
- `_max_consecutive_equal_finite` (`data_loader.py:1300`) — **2020 calls, 0.021s tottime / 0.038s cumtime** ← #1 target
- pandas `_merge_blocks` — 40 calls, 0.021s (frame copies in `_coerce_numeric`/campaign)
- `numpy.copy` — 420 calls, 0.014s
- `_run_data_quality_campaign` (`data_loader.py:1362`) — 20 calls, 0.014s tottime / 0.073s cumtime
- `_normalize_asset_name` (`:928`) — 2020 calls, 0.010s; `_normalize_columns` (`:990`) 0.007s tottime / 0.038s cumtime

**Key correction to prior handoff:** copies/coercion are *not* the dominant cost. The **per-column Python stale-run scan is** (`_max_consecutive_equal_finite` called once per column at `:1493` for every column with `finite_count >= threshold` — i.e. essentially every column in clean data). The dead `_max_consecutive_equal_finite_frame` (`:1328`) is the already-written vectorized replacement.

## Step 3e — REQUIRED WORK (exact anchors)

**Target:** `strategies/betting_against_beta/data_loader.py`, stale-run check in `_run_data_quality_campaign`.

1. **Primary win — vectorize the stale scan.** Replace the per-column Python loop at `:1483-1498`:
   ```python
   if stale_run_threshold is not None and int(stale_run_threshold) > 0:
       max_allowed_stale = max(int(stale_run_threshold), 50)
       stale = np.flatnonzero(finite_counts >= int(stale_run_threshold))
       if stale.size:
           for j in stale:
               j = int(j)
               max_run = _max_consecutive_equal_finite(arr2[:, j])
               if max_run >= max_allowed_stale:
                   col = cleaned.columns[j]
                   raise BABDataError(f"Stale/frozen data detected in column '{col}': {max_run} consecutive equal values")
   ```
   Use the existing `_max_consecutive_equal_finite_frame(arr2)` (`:1328`, currently dead) to compute **all** columns in one vectorized pass, then check `max_run >= max_allowed_stale` on the resulting int64 array. **Raise-ordering must match the loop exactly:** the loop raises on the *first* column (lowest column index) meeting the threshold, so the vectorized version must raise on `np.flatnonzero(max_runs >= max_allowed_stale)[0]` — lowest column index first. Preserve exact message text (`Column '<name>'` / `Stale/frozen data detected in column '<name>': <run> consecutive equal values`). `_max_consecutive_equal_finite_frame` already implements the same semantics as the 1-D helper (boundary on value-change or non-finite; finite-only tally); verify equivalence with a differential test against `_max_consecutive_equal_finite` before relying on it.
   - **Equivalence already proven this session:** `_max_consecutive_equal_finite_frame` was differential-tested against `_max_consecutive_equal_finite` over 300 randomized frames (NaNs/inf/-inf, constant runs, all-NaN columns, varying n/m) → **0 mismatches**. It is safe to rely on. Scratch: `/home/runner/work/_temp/kilo-tmp/equiv.py`.
2. **Secondary — whole-frame numeric dtype check.** Replace `all(pd.api.types.is_numeric_dtype(dt) for dt in cleaned.dtypes)` at `:1468` (and `:1080`) with a single whole-frame check (e.g. `pd.api.types.is_numeric_dtype(cleaned.dtypes)`), preserving exact mixed/object → fallback behavior. Minor win; do it only if it does not change behavior.
3. **Only if profile still shows it after (1):** reduce redundant copy/coercion/sort when `_run_data_quality_campaign` is called from `validate_returns_dataframe` on an already-normalized frame (`:1738`). Do **not** do this speculatively — it is not the bottleneck. Any change must preserve returned-frame independence (callers may mutate inputs), duplicate-timestamp handling, tz normalization, index sort, and error type/message/ordering.

### Correctness gates (must all hold)
- Preserve contracts: `BABDataError` types/messages/raise-ordering, duplicate-timestamp handling (incl. `allow_duplicate_timestamps`), tz normalization, index sort, benchmark checks, NaN/inf rejection, finite-fraction & stale-run thresholds, numeric-vs-fallback parity.
- Add/extend **oracle** tests in `tests/test_validation_performance.py` (pattern: existing oracle tests there): all-NaN cols, mixed dtypes, inf/-inf, stale runs at/above/below threshold, **stale run in multiple columns where the lowest-index column must win**, sparse finite fractions, duplicate timestamps, tz-aware indexes, canonical/duplicate column normalization, malformed/non-numeric preservation, empty/single-row frames, mutation-independence of returned frames.
- Keep all existing stale-run/oracle tests green (adapt only if the helper API changes but semantics are identical).
- Targeted tests for touched areas → then **full gate** `bash scripts/bab_gate.sh` → **RC=0**.
- Record before/after warm medians + delta in this file.

## Step 3f — end-to-end `BABStrategy.run()` hot spots (start after 3e lands)
Re-measure before changing; prior anchors: `calculate_rolling_beta` ~12.1 ms (`beta.py:331`), `construct_portfolio` ~6.4 ms (`portfolio.py:43`), `run_backtest` ~2.1 ms (`backtest.py:9`).
1. `beta.py:331` `calculate_rolling_beta`: block `to_numpy`/broadcast path; preserve per-window degeneracy/min_obs, float tol 1e-12.
2. `portfolio.py:43` `construct_portfolio`: reduce avoidable `copy()`/`to_numpy`/`np.trunc`/`_write_book` allocations; preserve dollar-neutrality, turnover/position/gross limits, `BABPortfolioError`.
3. `backtest.py:9` `run_backtest`: `weights.shift(1)`/`fillna` vs NumPy/in-place equivalent; preserve gross/cost/slippage/clipping.
4. Per stage: oracle-equivalence + generous perf-ceiling tests (pattern `tests/test_beta_performance.py`), full gate.

## Environment / bottlenecks removed this session
- **REMOVED (real blocker):** container shipped with **no Python deps** (no `numpy`/`pandas`/`scipy`/`pytest`/`hypothesis`). Prior sessions could not have run the gate here. Fixed: `pip install -r requirements.txt` (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis). `coverage` still not installed → gate runs without coverage report (by design). If gate reporting needs coverage: `pip install coverage` (no config edits).
- **REMOVED (process bottleneck):** prior handoff spent sessions profiling without shipping. This handoff makes Step 3e code+tests+gate the mandatory first deliverable, with a *measured* target and the vectorized replacement already identified.
- **REMOVED (staleness):** both handoff files refreshed to HEAD `1ace2b5` at 2026-11-13T06:30:30Z; gate result verified, not assumed.
- `research_state/workflow_run_diagnostics.jsonl` is historical CI/log diagnostics only (prior runs, tool-arg noise, transient env issues). **Non-blocking context, not justification for inaction.**

## Anti-churn / execution rules (binding)
- **Do not** re-profile/re-measure recorded baselines except before/after code you ship now.
- **Do not** reopen probe-count campaigns, rotate C-numbers, or add "no reduction identified" logs/tests that do not pin real behavior/perf-oracle needs.
- **Do not** treat historical `research_state/workflow_run_diagnostics.jsonl` entries as current failures.
- If Step 3e yields no measurable win after a genuine implementation, document the evidence here and move immediately to Step 3f item 1 (never idle).

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed / locked context (do not reopen without new reproducible failure + evidence)
- C42–C54 closed: full-suite gate discipline, broad-silent audit, `beta.py` perf (`8c2830a`), `construct_portfolio` DN vectorization (`83ff28e`), `validate_returns_dataframe` numeric fast path (`c40dd50`), `_series_is_parseable` vectorized (`43a2313`), `docs/COVERAGE_NOTES.md`.
- **Step 3e code still unshipped at HEAD `1ace2b5`** — the open binding task above (code reality verified: `_max_consecutive_equal_finite_frame` present but unused at `:1328`; per-column loop at `:1483-1498`; `all(...)` dtype check at `:1468`).

## Before exit (mandatory)
1. Targeted tests for changed code, then `bash scripts/bab_gate.sh` → RC=0.
2. Record before/after warm medians + delta (or evidenced "no measurable win") and next target.
3. Refresh this file: timestamp/HEAD, gate result, shipped/uncommitted changes, residual debt with exact anchors.
4. Keep `AGENT_HANDOFF.md` pointer-only and in sync.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**