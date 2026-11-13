# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T02:34:09Z
**HEAD:** `c40dd50 chore(kilo): checkpoint agent session`
**Working tree:** clean (Step 3c committed; nothing staged/dirty). **Commit nothing unless the user explicitly asks.**
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).

## CURRENT STATE (verified this session, 2026-11-13)

- **Full gate — GREEN:** `python3 -m pytest -q -p no:cacheprovider` → **5127 passed / 35 skipped / RC=0** in 289s (single command, no `--ignore`).
- **Data-loader regression subset still green:** `test_bab_data_loader_batch62.py test_bab_data_loader_numeric_qc.py test_bab_data_loader_bottleneck_branches.py test_bab_data_loader_edge_cases.py test_betting_against_beta_data_loader.py test_bab_zero_silent_error.py`.
- **Portfolio/perf subset still green** (`test_portfolio_performance.py`, `test_beta_performance.py`, `test_beta_perf_numpy_cache.py`).

### Step 3c — validation-hotspot optimization (shipped, committed `c40dd50`, gate-confirmed)

**Target:** `validate_returns_dataframe` was the #1 hotspot; `_drop_all_nan_columns` + `_run_data_quality_campaign` vectorized numeric fast path added to `data_loader.py` with oracle-equivalence tests in `tests/test_validation_performance.py`.

**Measured (median, 2026-11-13):**

| stage | before | after | speedup |
|---|---|---|---|
| `_drop_all_nan_columns` (720x12) | 0.295 ms | 0.072 ms | ~4.1x |
| `_run_data_quality_campaign` (720x12) | 0.606 ms | 0.421 ms | ~1.4x |
| `validate_returns_dataframe` (720x12) | 1.502 ms | 1.013 ms | ~1.5x |
| `validate_returns_dataframe` (2000x100) | 10.924 ms | 6.799 ms | ~1.6x |
| full `BABStrategy.run` (720x12) | 4.05 ms | 3.49 ms | ~1.16x |
| cProfile validate (20 runs, 720x12) | 0.078 s / 47% | 0.056 s / 38% | — |

(`calculate_rolling_beta` 0.70 ms and tracemalloc peak 0.73 MB unchanged; allocation-neutral.)

### Bottleneck removed / confirmed for Step 3d

Measured baselines on the current tree (2000x100 frames, `datetime` index):

| metric | median |
|---|---|
| `_series_is_parseable` across all object columns | **236 ms** |
| `validate_returns_dataframe` on all-parseable object frame | **485 ms** |
| `_series_is_parseable` on numeric frame (skipped at call sites via `is_numeric_dtype`) | ~0 ms |

`_series_is_parseable` (`data_loader.py:1196`) loops **per cell** in Python and calls `_strip_units_and_parse` (regex per cell). It is called from `validate_returns_dataframe` at `data_loader.py:1554` (pre-coerce junk drop) and `:1571` (`_coerce_numeric` failure fallback). Numeric-dtype columns are short-circuited at both call sites (`continue` on `is_numeric_dtype`); object/string frames reach the per-cell loop. This is the measured next #1 hotspot (~94% of object-frame validate).

## NEXT FOCUS CAMPAIGN — Step 3d: kill the `_series_is_parseable` object-frame bottleneck (BINDING, HEAVY WORK)

This is the **initial task** for the next agentic work session. Do not defer, do not substitute probe/coverage churn. Execute end-to-end below.

### Entry criteria (mandatory before writing code)
1. Full gate green on current tree: `python3 -m pytest -q -p no:cacheprovider` → RC=0 (confirmed above; re-confirm at session start).
2. Baseline recorded above (`_series_is_parseable` 236 ms / validate 485 ms on object 2000x100). Re-measure in isolation to confirm medians before optimizing.

### Execution plan (measured; no probe/coverage churn)

1. **Reproduce the cost precisely:** confirm the two call sites (`data_loader.py:1554`, `:1571`) and that object/string frames reach them while numeric frames do not. Record per-cell `_strip_units_and_parse` cost vs vectorized `pd.to_numeric(errors='coerce')` on the same columns.
2. **Implement one focused optimization** that preserves exact semantics: a column is parseable iff `parseable >= max(1, int(total_non_na * 0.5))` where `None`/NaN count as parseable and a cell is parseable iff `_strip_units_and_parse` does not raise. Candidates (choose by measurement, **do not guess**):
   - Vectorize the cheap majority case: try `pd.to_numeric(series, errors='coerce')` first; only fall back to per-cell `_strip_units_and_parse` for columns that fail or need unit/`%`/comma/European-decimal handling.
   - Short-circuit: numeric-dtype columns are parseable by definition (already done at call sites; keep).
   - If a per-cell pass is unavoidable, reduce Python overhead (hoist regex/lookups, operate on numpy arrays) while keeping the 50% threshold and NaN/None rules identical.
   **Preserve exactly:** threshold, `None`/NaN-as-parseable rule, `_strip_units_and_parse` return/raise behavior, every observable error message, and the defensive `try/except: return False` wrapper.
3. **Prove correctness & improvement:** extend `tests/test_validation_performance.py` with an oracle equivalence test for `_series_is_parseable` (per-cell `_strip_units_and_parse` oracle) across: numeric, numeric-strings, units (`$`/`%`/commas/European decimals), NA markers, malformed numerics (`1.2.3`), pure garbage (`abc`), and the 50%-boundary. Record before/after medians. If no meaningful win after a serious attempt, record concrete evidence and stop — no speculative churn.
4. **Full honest gate:** `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.

### Before exit (mandatory)
1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + isolated numbers for `_series_is_parseable` (or state "no measurable win" with evidence).
3. Refresh timestamp/HEAD, shipped changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

## Locks / prohibitions (unchanged)

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`. Do not weaken `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except` — it pins the defensive fallback added in Step 3c.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped (`83ff28e`). **Step 3c:** `validate_returns_dataframe` numeric fast path (`_drop_all_nan_columns` + `_run_data_quality_campaign`) shipped, gate-confirmed at **5127 passed / RC=0**. **Step 4:** `docs/COVERAGE_NOTES.md`.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
