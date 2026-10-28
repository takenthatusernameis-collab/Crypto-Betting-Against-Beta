# HANDOFF - 2026-10-28T02:11:00Z

## Timestamp
2026-10-28T02:11:00Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see below). Tests: **231 passed, 0 failed** (was 217; +14 new tests this session).
- Bottlenecks removed this session:
  1. `.github/workflows/main.yml` `stage_safe_changes` pattern list was missing `*/.github/workflows/*` (Python had it, bash did not). Restored lock-step; `TestStageSafeChangesPatternSync` now passes.
  2. `tests/fixtures/real_data_defects.csv` (30 rows) was orphaned — no test referenced it. Added a `TestRealDataDefects` class in `tests/test_bab_messy_data.py` and a `TestReportOnMessyData` class in `tests/test_bab_backtest_report.py` so the fixture is exercised end-to-end (strategy + CLI JSON).
  3. **Delisted-asset handling**: `_drop_all_nan_columns()` added to `data_loader.py`. All-NaN columns (delistings, stale feeds) are now dropped deterministically before the inf check, so they cannot propagate NaNs into betas/signals/weights even when their name matches the configured universe. Raises `BABDataError` if *every* column is all-NaN.
  4. `resolved_universe` behavior clarified and tested: benchmark is part of the universe; empty intersection falls back to all available columns (not just non-benchmark).

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: BAB Strategy Robustness & Production Readiness (HEAVY - do all of it)
All previous defects are fixed. Now harden for production-like crypto data and expand coverage/observability without breaking tests.

Recon (fast): `python3 -m pytest -q`, `git status`, `git diff --stat`.

1) **Data loader hardening**: Ensure coerce/validation handle mixed dtypes robustly; if junk/non-numeric columns exist, drop deterministically or raise BABDataError with clear message. Add tests.
2) **Beta robustness**: calculate_rolling_beta must handle all-NaN columns, constant series, benchmark NaNs without raising; ensure benchmark missing raises BABDataError consistently. Add tests.
3) **Signals/Portfolio**: Eliminate remaining silent broad excepts where possible; add tests for all-zero signals, single-asset cases; guarantee finite weights.
4) **Strategy/config**: Enforce min_rows in strategy path; verify resolved_universe behavior when intersection empty.
5) **Backtest/Report**: Ensure bab_backtest_report never emits NaN/inf in JSON.
6) **CI/Infra sync**: Keep EXCLUDE_PATTERNS in scripts/controller_progress.py and .github/workflows/main.yml in lock-step; run sync tests.
7) **Verify + handoff**: `python3 -m pytest -q` all pass; update handoff with new timestamp.

## ACCEPTANCE CRITERIA
- [ ] All new edge case tests added and passing
- [ ] No NaN/inf weights/signals on any tested messy input
- [ ] Consistent BABDataError for data issues
- [ ] CI pattern sync tests pass
- [ ] `python3 -m pytest -q` all pass (231+)
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — re-added `*/.github/workflows/*` to the `stage_safe_changes` case list (1 token).
- `strategies/betting_against_beta/data_loader.py` — added `_drop_all_nan_columns()`; called after `_coerce_numeric()` in `validate_returns_dataframe`.
- `tests/test_bab_messy_data.py` — added `TestRealDataDefects` (2 tests) for `tests/fixtures/real_data_defects.csv`.
- `tests/test_bab_backtest_report.py` — added `TestReportOnMessyData` (2 tests) asserting finite JSON metrics on the messy fixture.
- `tests/test_betting_against_beta.py` — added `TestResolvedUniverse` (4 tests) and `TestCalculateRollingBeta` edge cases (all-NaN asset, constant series, missing benchmark).
- `tests/test_betting_against_beta_data_loader.py` — added `TestAllNanColumnDropping` (3 tests).
- `tests/fixtures/real_data_defects.csv` — now referenced by tests (was orphaned).

(End of file - total 54 lines)