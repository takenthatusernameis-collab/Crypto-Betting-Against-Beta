# HANDOFF - 2026-10-28T06:12:38Z

## Timestamp
2026-10-28T06:12:38Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**NO NEW HEAVY CAMPAIGN REQUIRED** — All items from the previous campaign are already implemented and passing.

The codebase is in a clean state with all tests passing. The bottlenecks have been removed and the full BAB execution realism & real-market backtesting campaign is complete:
- Slippage model implemented in backtest.py with tests passing
- Multi-day rebalance (daily/weekly/monthly) implemented in strategy.py with tests passing
- Real price ingestion via `load_prices()` in data_loader.py with tests passing
- Portfolio-level risk checks implemented in portfolio.py with tests passing
- Expanded real-market fixture (real_market_prices_expanded.csv) with BTC + 8 crypto + DELISTED column exists and is used

**If you need to extend the strategy:** Follow TDD - write failing tests first, implement, ensure all tests pass. Keep focus on BAB product as priority. Do not commit unless explicitly asked.

## Current State
- Branch main @ HEAD (5963f23 chore(kilo): checkpoint agent session). Working tree: **intentional uncommitted change** — `.github/workflows/main.yml` bottleneck fix (added `*/.github/workflows/*` to `stage_safe_changes()` case list; restores lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS).
- Environment: `pytest`, `pandas`, `numpy` installed via `requirements.txt`; `python3 -m pytest -q` runs locally.
- Suite: **268 passed, 0 failed** (all tests green).
- All BAB execution realism features implemented and tested.

## BOTTLENECKS REMOVED
- **CI/pattern-sync**: `.github/workflows/main.yml` `stage_safe_changes()` case list was missing `*/.github/workflows/*` (present in `scripts/controller_progress.py` EXCLUDE_PATTERNS). This failed `test_nested_workflow_pattern_is_present_in_workflow` and `test_python_patterns_are_subset_of_workflow`. Added `*/.github/workflows/*` to the case list. Suite now green (268 passed, 0 failed). Change is intentionally uncommitted.

## COMPLETED CAMPAIGN (BAB Execution Realism & Real-Market Backtesting)
All items completed with tests passing:

### 1) Slippage model — DONE
- **Files:** `strategies/betting_against_beta/backtest.py` — slippage applied on turnover alongside transaction costs
- **Tests:** `test_slippage_reduces_cumulative_vs_zero_slippage`, `test_slippage_scales_monotonically_with_turnover` passing

### 2) Multi-day rebalance — DONE
- **Files:** `strategies/betting_against_beta/strategy.py`, `strategies/betting_against_beta/config.py`
- **Implementation:** `_rebalance_mask()` and `_apply_rebalance()` in strategy.py honor `rebalance_freq` (daily/weekly/monthly), hold weights between rebalance dates
- **Tests:** `test_weekly_rebalance_fewer_events_than_daily`, `test_weights_constant_within_rebalance_window_weekly` passing

### 3) Real price ingestion — DONE
- **File:** `strategies/betting_against_beta/data_loader.py`
- **Implementation:** `load_prices()` converts prices to returns via `pct_change()`, handles date parsing, gaps, drops all-NaN columns (delisted assets)
- **Tests:** `test_price_fixture_with_dates_and_gaps_produces_finite_returns`, `test_malformed_dates_raise_bab_data_error` passing

### 4) Portfolio-level risk checks — DONE
- **File:** `strategies/betting_against_beta/portfolio.py`
- **Implementation:** `construct_portfolio()` enforces gross exposure, net exposure (dollar-neutral), max single-asset weight when `enforce_risk_checks=True` or limits provided
- **Tests:** All portfolio risk check tests passing

### 5) Expanded real-market fixture — DONE
- **File:** `tests/fixtures/real_market_prices_expanded.csv` exists with BTC + 8 crypto assets (ETH,SOL,BNB,XRP,ADA,AVAX,DOT) + DELISTED column, 400 rows, used by tests

### 6) Verification — DONE
- All tests pass: **268 passed, 0 failed**

## ACCEPTANCE CRITERIA (all checked)
- [x] `python3 -m pytest -q` all pass
- [x] Slippage model test passes (cost reduces cumulative; scales with turnover) — test written first
- [x] Multi-day rebalance test passes (weekly < daily rebalance events; constant weights in window) — test written first
- [x] Real price ingestion test passes (dates parsed, gaps handled, `BABDataError` on bad dates) — test written first
- [x] Portfolio risk checks pass (gross/net/max-weight enforcement with errors) — test written first
- [x] Expanded real-market fixture added/confirmed and used by the above tests
- [x] Every new behavior has a test (no test = no merge)
- [x] Handoff re-timestamped to completion time

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.
- Do not get distracted by infra/docs unless directly blocking BAB campaign items.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to `stage_safe_changes()` case list (bottleneck removal; restores lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS; suite now 268 passed, 0 failed).
