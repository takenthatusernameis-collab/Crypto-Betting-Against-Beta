# HANDOFF - 2026-10-28T01:15:00Z

## Timestamp
2026-10-28T01:15:00Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see below). Tests: **217 passed, 0 failed**.
- Bottlenecks addressed this session:
  1. Zero-silent-error campaign for real-data pipeline completed: added defect fixtures and regression tests; hardened beta/signals/portfolio/strategy with NaN/inf guards; enforced min_rows end-to-end; report paths remain finite.
  2. .github/workflows/main.yml stage_safe_changes pattern list updated to include */.github/workflows/* and kept in sync with scripts/controller_progress.py.

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: BAB Strategy Robustness & Production Readiness (HEAVY - do all of it)
All previous defects are fixed. Now harden for production-like crypto data and expand coverage/observability without breaking tests.

Recon (fast): `python3 -m pytest -q`, `git status`, `git diff --stat`.

1) **Data loader hardening**: Ensure coerce/validation handle mixed dtypes robustly; if junk/non-numeric columns exist, drop deterministically or raise BABDataError with clear message. Add tests.
2) **Beta robustness**: calculate_rolling_beta must handle all-NaN columns, constant series, benchmark NaNs without raising; ensure benchmark missing raises BABDataError consistently.
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
- [ ] `python3 -m pytest -q` all pass (217+)
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.

## UNCOMMITTED WORKING CHANGES (review before committing)
- strategies/betting_against_beta/beta.py - hardened
- strategies/betting_against_beta/signals.py - hardened
- strategies/betting_against_beta/portfolio.py - hardened
- strategies/betting_against_beta/strategy.py - weights finiteness guard
- strategies/betting_against_beta/errors.py - added
- tests/test_bab_zero_silent_error.py - added
- tests/fixtures/all_nan_column.csv, benchmark_nan_window.csv, non_monotonic_dates.csv, junk_columns.csv, returns.json - added
- .github/workflows/main.yml - pattern sync
