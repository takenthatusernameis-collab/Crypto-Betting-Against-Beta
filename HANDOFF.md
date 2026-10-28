# HANDOFF - 2026-10-28T08:20:00Z

## Timestamp
2026-10-28T08:20:00Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**FOCUS CAMPAIGN: CLOSE BAB GUARD & COST TEST COVERAGE (TDD)**

Bottleneck removed: CI pattern sync. `.github/workflows/main.yml` `stage_safe_changes` case list was missing the nested `*/.github/workflows/*` pattern that Python `EXCLUDE_PATTERNS` requires. Pattern added. Suite was red at 266 passed / 2 failed; now **268 passed, 0 failed**. Do not re-open the pattern-sync issue; it is closed.

Verified ground truth (do not re-verify unless something changes): the guard/cost behavior the prior campaign listed already EXISTS in code — `max_position_size`, `max_turnover`/`max_total_turnover` all raise `BABDataError` on violations and no-op when None; `tc`/`slippage_cost` aliases resolve in `run_backtest`. **The bottleneck is not implementation, it is zero test coverage.** The next agent's heavy work is writing the missing tests (TDD: failing test first → implement if needed → green suite). Do not re-implement what works.

### Campaign items (gated: failing test first → implement → green suite — do not skip)
1. **Liquidity/Participation Guards — TEST COVERAGE (IMMEDIATE)**: No test references `max_position_size`, `max_turnover`, or `max_total_turnover`. Add tests in `tests/test_betting_against_beta.py` (new class `TestLiquidityGuards`): violation raises `BABDataError` (not generic), no-op when absent/None, `max_total_turnover` alias routes to `max_turnover`, negative/zero limit raises `BABDataError`. Behavior is in `strategies/betting_against_beta/portfolio.py:94-137` and wired in `strategy.py:173-174`.
2. **Turnover/Cost Correctness — TEST COVERAGE**: Add tests for `run_backtest` (`strategies/betting_against_beta/backtest.py:7-77`): zero turnover day produces no cost, negative turnover handled, NaN/inf weights coerced, `tc` and `slippage_cost` aliases produce identical results to `transaction_costs`/`slippage`.
3. **Cost Monotonicity — TEST COVERAGE**: No test proves higher `transaction_costs` -> strictly worse cumulative. Add: `costly.cumulative.iloc[-1] < free.cumulative.iloc[-1]` for increasing cost levels on a rebalancing weight path (slippage monotonicity already exists at `test_betting_against_beta.py:511` — extend the same idea to `transaction_costs`).
4. **Data Integrity — Timezone Handling**: `data_loader.py` tests cover string-index normalization but not tz-aware vs tz-naive `DatetimeIndex`. Add tests: tz-aware index is accepted/normalized consistently, tz-naive accepted, malformed dates still raise `BABDataError`, benchmark with no finite values raises.
5. **Pipeline Safety Regression**: Add a test asserting `BABStrategy.run()` output weights/signals/betas contain no NaN/inf on the synthetic default path and on the expanded real fixture (`tests/fixtures/real_market_prices_expanded.csv`).

### Execution Rules
1. **START HERE** - Read `strategies/betting_against_beta/{backtest,portfolio,strategy,config,data_loader,beta,signals,metrics}.py` before changes.
2. **TDD MANDATORY** - Failing test → implement → pass. No new behavior without a test.
3. **BAB FIRST** - Product focus over infra. No drift into controller/infra refactors unless they block BAB.
4. **NO COMMIT** unless explicitly asked.
5. **HANDOFF DISCIPLINE** - Update this file when significant progress is made or blocked.
6. **RECON FIRST** - `python3 -m pytest -q` (expect 268 passed), `git status`, `git diff --stat`, `git log --oneline -5`.

**GOAL**: Close the BAB guard/cost/tz test-coverage gap with TDD so the suite proves robustness, not just runs.

## Current State
- Branch: main @ HEAD (up to date with origin/main)
- Tests: **268 passed, 0 failed** (all green)
- CI pattern sync fixed in `.github/workflows/main.yml` (added `*/.github/workflows/*` to `stage_safe_changes` case list)

## Bottlenecks Removed
- Workflow/Python exclude pattern drift (added `*/.github/workflows/*` to workflow `stage_safe_changes` case list; suite was red at 266 passed / 2 failed, now 268 passed / 0 failed)

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- Every new behavior needs a test
- No NaN/inf in weights/signals/metrics on tested inputs
- Consistent `BABDataError` for data issues
- No fabricated market data

## UNCOMMITTED WORKING CHANGES
- `.github/workflows/main.yml` - pattern sync fix (added `*/.github/workflows/*` to stage_safe_changes case list)