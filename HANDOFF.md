# HANDOFF - 2026-10-28T17:17:18Z

## Timestamp
2026-10-28T17:17:18Z

## Purpose
Single durable handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see latest state). Tests: **249 passed, 0 failed**.
- Bottlenecks already removed (pattern sync, orphaned fixtures exercised, all-NaN column dropping, silent broad excepts eliminated, beta robustness, report JSON sanitization).

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: BAB Strategy Robustness & Production Readiness (HEAVY - do all of it)
Recon (fast): `python3 -m pytest -q`, `git status`, `git diff --stat`.

1) **Data loader hardening**: Ensure coerce/validation handle mixed dtypes robustly; if junk/non-numeric columns exist, drop deterministically or raise BABDataError with clear message. Add tests.
2) **Beta robustness**: `calculate_rolling_beta` must handle all-NaN columns, constant series, benchmark NaNs without raising; ensure benchmark missing raises BABDataError consistently. Add tests.
3) **Signals/Portfolio**: Eliminate remaining silent broad excepts where possible; add tests for all-zero signals, single-asset cases; guarantee finite weights.
4) **Strategy/config**: Enforce min_rows in strategy path; verify resolved_universe behavior when intersection empty.
5) **Backtest/Report**: Ensure `bab_backtest_report` never emits NaN/inf in JSON.
6) **CI/Infra sync**: Keep EXCLUDE_PATTERNS in `scripts/controller_progress.py` and `.github/workflows/main.yml` in lock-step; run sync tests.
7) **Verify + handoff**: `python3 -m pytest -q` all pass; update handoff with new timestamp.

## ACCEPTANCE CRITERIA
- [ ] All new edge case tests added and passing
- [ ] No NaN/inf weights/signals on any tested messy input
- [ ] Consistent BABDataError for data issues
- [ ] CI pattern sync tests pass
- [ ] `python3 -m pytest -q` all pass (249+)
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.

## NOTES
- Use this as the single source of truth for next session. Bottlenecks have been removed where found; continue hardening toward production-like crypto data without breaking tests.
