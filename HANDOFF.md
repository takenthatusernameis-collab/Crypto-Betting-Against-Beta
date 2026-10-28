# HANDOFF - 2026-10-28T01:09:29Z

## Timestamp
2026-10-28T01:09:29Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **one intentional uncommitted change** (see below). Tests: **210 passed, 0 failed**.
- Bottleneck removed this session:
  1. `.github/workflows/main.yml` `stage_safe_changes` case list now includes `*/.github/workflows/*` (was missing; caused `test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` and `::test_nested_workflow_pattern_is_present_in_workflow` to fail, blocking checkpoint staging of vendored workflow files). Tests now 210/0 (was 208/2 at session start).
- BAB real-data wiring is **complete and verified end-to-end**:
  - `BABStrategy.run(returns_df=df)` accepts an in-memory DataFrame (validated via `data_loader.validate_returns_dataframe`).
  - `BABConfig(data_source="path.csv|json")` loads real files; `BABStrategy.run()` dispatches on extension.
  - `scripts/bab_backtest_report.py` supports `--data-source`, `--returns-csv` (alias), and `--json`.
  - Smoke test against a 300-row synthetic-real CSV: DataFrame path and CSV path both produce cumulative 2.0263; CLI exits 0 with all 8 metric keys.
- Real-data robustness partially done:
  - `tests/fixtures/messy_returns.csv` (missing dates/NaNs/delisted column/duplicates) + `tests/test_bab_messy_data.py` (3 tests, all passing).
  - `data_loader._normalize_index` drops duplicate timestamps (keeps first).
  - `signals.generate_bab_signals` handles Series rows safely.
  - `portfolio.construct_portfolio` handles pandas Series/DataFrame safely without truth-value ambiguity errors.
  - Missing benchmark still raises as expected.

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: Zero-Silent-Error Real-Data Pipeline (HEAVY — do all of it, do not skip)
The pipeline runs end-to-end on clean synthetic data and survives the existing messy fixture. Now make it **provably safe on arbitrary real crypto data**: no NaN/inf weights, no swallowed exceptions, deterministic cleaning or a loud `BABDataError` — on every code path. This campaign is mandatory; each item below has a testable acceptance criterion.

Recon (fast, do first): `python3 -m pytest -q`, `git status`, `git diff --stat`.

1) **Expand defect fixtures + regression tests** (add to `tests/fixtures/`, each with a test asserting deterministic cleaning **or** a clear `BABDataError` — never NaN/inf weights, never an uncaught traceback):
   - (a) `all_nan_column.csv` — an asset column all-NaN across the window → excluded from ranking / zero weight, never a NaN weight, never a crash.
   - (b) `benchmark_nan_window.csv` — benchmark (BTC) goes NaN mid-window → rolling beta degrades gracefully (NaN beta rows → flat period), never raises mid-pipeline.
   - (c) `non_monotonic_dates.csv` — out-of-order dates + gaps → loader sorts; strategy does not crash.
   - (d) `junk_columns.csv` — CSV with extra non-numeric/junk columns → `_coerce_numeric` raises `BABDataError` OR loader drops them deterministically; tested either way.
   - (e) `returns.json` — JSON returns format → `load_returns_from_json` path works end-to-end via `BABStrategy.run(data_source="...json")`.

2) **Harden `strategies/betting_against_beta/beta.py`**:
   - `calculate_beta`/`calculate_rolling_beta` must not leak exceptions; degenerate cases return NaN cleanly; insufficient history → NaN (not crash); benchmark column missing → `BABDataError` raised before estimation.

3) **Harden `signals.py` / `portfolio.py`** — remove silent `except: continue` swallowing:
   - All-NaN beta rows → zero-weight row (not crash, not NaN weight).
   - Zero-sum / single-asset cases handled.
   - Guarantee **weights contain no NaN/inf**: add an explicit finiteness guard in the pipeline (`BABStrategy.run`) and a test asserting `np.isfinite(weights.values).all()`.

4) **Enforce `min_rows` end-to-end** — add a strategy-level test: a DataFrame with fewer than `BABConfig.min_rows` rows raises `BABDataError` before beta estimation.

5) **Report/CLI finiteness** — verify `scripts/bab_backtest_report.py --json` emits only finite metrics on messy input (no `NaN` serialized).

6) **Verify + handoff**: `python3 -m pytest -q` all pass; update this handoff with a new timestamp.

## ACCEPTANCE CRITERIA
- [ ] New defect fixtures (a–e) + regression tests added, all passing
- [ ] No code path emits NaN/inf weights on messy input (tested, not just asserted)
- [ ] No broad `except: continue` swallowing hides errors in signals/portfolio/beta
- [ ] `min_rows` enforced end-to-end (tested)
- [ ] JSON report metrics finite on messy input
- [ ] `python3 -m pytest -q` all pass
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD (write the failing test first), offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test; untested code does not count as done.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to the `stage_safe_changes` case list (1 line).
