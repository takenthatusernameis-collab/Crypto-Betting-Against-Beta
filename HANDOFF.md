# HANDOFF - 2026-10-28T00:11:19Z

## Timestamp
2026-10-28T00:11:19Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD (uncommitted working changes below). Tests: **210 passed, 0 failed** (was 207/0 after infra fixes; added 3 messy-data tests all passing).
- Bottlenecks removed:
  1. `.github/workflows/main.yml` `stage_safe_changes` now includes both `.github/workflows/*` and `*/.github/workflows/*` (fixed pattern sync).
  2. `tests/test_bab_backtest_report.py::_run()` now passes full env to subprocess (imports resolve).
- BAB real-data wiring is **complete and verified end-to-end**.
- Real-data robustness hardened:
  - Added `tests/fixtures/messy_returns.csv` with missing dates/NaNs/delisted column/duplicates; regression test `tests/test_bab_messy_data.py` passes.
  - `data_loader._normalize_index` now drops duplicate timestamps (keeps first).
  - `signals.generate_bab_signals` handles Series rows safely.
  - `portfolio.construct_portfolio` handles pandas Series/DataFrame safely without truth-value ambiguity errors.
  - Missing benchmark still raises as expected.

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: Real-Data Robustness + Validation Hardening (Continue)
The pipeline now survives the added messy fixture. Next heavy lift is broader real-world defects and production-hardening without silent errors.

1) Recon (fast, do first): `python3 -m pytest -q`, `git status`, `git diff --stat`.
2) Expand defect coverage: add fixtures for (a) all-NaN asset column across window, (b) benchmark becomes NaN in window causing beta issues, (c) non-monotonic dates with gaps, (d) CSV with extra junk columns, (e) JSON returns format. For each, assert either deterministic cleaning or clear `BABDataError`.
3) Harden `strategies/betting_against_beta/beta.py`:
   - `calculate_beta` should return NaN cleanly on degenerate cases (already does) but ensure no exceptions leak.
   - `calculate_rolling_beta`: when benchmark missing/NaN issues arise, raise `BABDataError` early (or let loader enforce). Ensure insufficient history produces NaN but downstream doesn't crash.
4) Harden `signals.py`/`portfolio.py` against all-NaN beta rows, zero-sum cases, and ensure weights never contain NaN/inf (add guards + tests).
5) Verify `BABConfig.min_rows` enforced end-to-end via test (loader already enforces; add explicit strategy-level test).
6) All tests pass; update this handoff.

## ACCEPTANCE CRITERIA
- [ ] New defect fixtures + tests committed/passing
- [ ] Beta/signal/portfolio paths cannot emit NaN/inf weights on messy input
- [ ] All tests pass (`python3 -m pytest -q`)
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to `stage_safe_changes`.
- `tests/test_bab_backtest_report.py` — `_run()` uses full env.
- `strategies/betting_against_beta/data_loader.py` — drop duplicate timestamps on normalized index.
- `strategies/betting_against_beta/signals.py` — handle Series row safely.
- `strategies/betting_against_beta/portfolio.py` — robust assignment avoiding pandas truth-value ambiguity.
- `tests/fixtures/messy_returns.csv` (new), `tests/test_bab_messy_data.py` (new).
