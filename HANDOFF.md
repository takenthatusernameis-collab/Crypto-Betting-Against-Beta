# HANDOFF - 2026-10-28T08:27:52Z

## Timestamp
2026-10-28T08:27:52Z

## Purpose
**SINGLE DURABLE HANDOFF. START HERE.** Ignore all other `HANDOFF*.md` files unless you need historical context. `HANDOFF.md` (this file) is the source of truth for the next session.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the **Betting Against Beta (BAB)** crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. **BAB ALWAYS COMES FIRST. Infra only if it blocks BAB.**

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)

**FOCUS CAMPAIGN: CLOSE BAB GUARD & COST TEST COVERAGE WITH HEAVY TDD (NO SHORTCUTS)**

The suite is green. The remaining gap is behavioral test coverage of the BAB product itself. Your job is to make the suite PROVE guard/cost/tz/pipeline robustness — not to re-implement.

### Ground Truth (DO NOT RE-IMPLEMENT)
- Guards exist: `max_position_size`, `max_turnover`/`max_total_turnover` raise `BABDataError` on violations and no-op when `None` (`strategies/betting_against_beta/portfolio.py:94-137`, wired in `strategy.py:173-174`).
- Cost aliases exist: `tc`/`slippage_cost` resolve in `run_backtest` (`strategies/betting_against_beta/backtest.py:7-77`).
- CI pattern sync is **CLOSED**: `.github/workflows/main.yml` `stage_safe_changes()` now includes `*/.github/workflows/*` in lock-step with Python `EXCLUDE_PATTERNS`. Suite green (295 passed).

**BOTTLENECK REMOVED.** The recurring CI drift that dropped `*/.github/workflows/*` from the bash exclusion list on every checkpoint reset is fixed in the working tree. Do not re-litigate it unless a future checkpoint discards it again.

### Heavy Campaign (Execute in order, TDD strictly)

#### PHASE 1: LIQUIDITY/PARTICIPATION GUARDS (IMMEDIATE - HEAVY)
Create `TestLiquidityGuards` in `tests/test_betting_against_beta.py`. You MUST write failing tests first:
- [ ] `max_position_size` violation raises `BABDataError` (assert exception type, not generic Exception)
- [ ] `max_turnover` violation raises `BABDataError`
- [ ] `max_total_turnover` violation raises `BABDataError`
- [ ] Guards no-op when `None`/absent (default behavior unchanged)
- [ ] `max_total_turnover` is an alias that routes to `max_turnover` (test both paths produce identical error)
- [ ] Negative/zero limits raise `BABDataError`
- [ ] Guard interactions with equal-weight dollar-neutral construction don't break existing behavior

#### PHASE 2: TURNOVER/COST CORRECTNESS (HEAVY)
Add tests for `run_backtest` covering:
- [ ] Zero turnover day produces no transaction/slippage costs
- [ ] Negative turnover handled correctly (|turnover| or sign handling - verify actual behavior)
- [ ] NaN/inf weights coerced safely (no crashes, no NaN in outputs)
- [ ] `tc` alias == `transaction_costs` results (byte-for-byte equivalent on same inputs)
- [ ] `slippage_cost` alias == `slippage` results (byte-for-byte equivalent on same inputs)
- [ ] Both aliases work together without conflict

#### PHASE 3: COST MONOTONICITY (HEAVY)
Prove robustness with monotonicity tests:
- [ ] Higher `transaction_costs` → strictly worse final cumulative return: `costly.cumulative.iloc[-1] < free.cumulative.iloc[-1]` on rebalancing path
- [ ] Higher `slippage` → strictly worse final cumulative return (extend existing pattern from line ~511)
- [ ] Monotonicity holds across multiple cost levels (e.g., 0, 0.001, 0.005)
- [ ] Cost monotonicity doesn't introduce NaN/inf

#### PHASE 4: DATA INTEGRITY - TIMEZONE HANDLING (HEAVY)
Expand `data_loader` coverage:
- [ ] tz-aware `DatetimeIndex` accepted and normalized consistently
- [ ] tz-naive `DatetimeIndex` still accepted (existing behavior preserved)
- [ ] Mixed timezone scenarios don't crash
- [ ] Malformed dates still raise `BABDataError`
- [ ] Benchmark with no finite values raises `BABDataError`
- [ ] Index alignment with tz-aware/tz-naive doesn't break beta calculation

#### PHASE 5: PIPELINE SAFETY REGRESSION (HEAVY)
Assert end-to-end cleanliness:
- [ ] `BABStrategy.run()` on default synthetic path produces no NaN/inf in weights/signals/betas/returns
- [ ] Same assertion on `tests/fixtures/real_market_prices_expanded.csv`
- [ ] Dollar-neutral property holds (weights sum to ~0) on both paths
- [ ] Long/short counts match quantile expectations
- [ ] No lookahead: verify lagged weights behavior

### Execution Rules (NON-NEGOTIABLE)
1. **START HERE** - Read `strategies/betting_against_beta/{backtest,portfolio,strategy,config,data_loader,beta,signals,metrics}.py` before making ANY changes.
2. **TDD MANDATORY** - Write failing test → understand failure → minimal fix if implementation is broken → green. If implementation is correct (as stated), tests will just fail due to missing coverage and you need to write them to pass against existing correct behavior.
3. **BAB FIRST** - Product focus over infra. NO controller/infra refactors unless they directly block BAB tests.
4. **NO COMMIT** unless explicitly asked.
5. **HEAVY WORK REQUIRED** - Do not stop at 1-2 tests. Complete phases systematically. Each phase should add multiple tests.
6. **VERIFY CONSTANTLY** - Run `python3 -m pytest -q` after each phase. Never leave suite broken.
7. **RECON FIRST** - Before writing code: `python3 -m pytest -q` (expect 295 passed), `git status`, `git diff --stat`, `git log --oneline -5`.

**GOAL**: Close ALL gaps above. Make the suite PROVE guard/cost/tz robustness. Don't just "run tests" - write comprehensive tests that would catch regressions.

## Current State
- Branch: main @ HEAD (up to date with origin/main)
- Tests: **295 passed, 0 failed** (all green)
- CI: Pattern sync fixed in `.github/workflows/main.yml`
- Uncommitted: `.github/workflows/main.yml` (pattern sync fix) + `__pycache__/` dirs

## Bottlenecks Removed
1. **Workflow/Python exclude pattern drift** - Added `*/.github/workflows/*` to `stage_safe_changes()` bash case list at `.github/workflows/main.yml:1163`, matching Python `EXCLUDE_PATTERNS` (scripts/controller_progress.py:28). Was causing `TestStageSafeChangesPatternSync` (2 failures) and blocking green suite; now fixed and verified (295 passed).

## Remaining Bottlenecks (TO REMOVE BY TESTS)
- **Test coverage gap** - Guards, cost aliases, monotonicity, tz handling, pipeline safety all lack tests despite existing implementation.

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- Every new behavior needs a test (coverage of existing behavior counts as closing gaps)
- No NaN/inf in weights/signals/metrics on tested inputs
- Consistent `BABDataError` for data issues
- No fabricated market data
- Minimal diffs, follow existing code style

## NEXT ACTION
**IMMEDIATELY**: Run recon commands (`python3 -m pytest -q`, `git status`, `git diff --stat`, `git log --oneline -5`), read the core BAB files, start Phase 1 with failing tests in `TestLiquidityGuards`. Do NOT explore unrelated code until BAB coverage is closed.
