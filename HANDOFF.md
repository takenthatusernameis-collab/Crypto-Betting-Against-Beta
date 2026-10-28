# HANDOFF - 2026-10-28T07:20:43Z

## Timestamp
2026-10-28T07:20:43Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**FOCUS CAMPAIGN: HARDEN BAB FOR TRADEABLE REALISM**

All tests green (268 passed, 0 failed). Bottleneck removed (CI pattern sync: `*/.github/workflows/*` added to `.github/workflows/main.yml` stage_safe_changes). Next agent MUST advance BAB robustness without breaking behavior.

### Campaign items (gated: failing test first → implement → green suite — do not skip)
1. **Fees/Slippage & Turnover Correctness (IMMEDIATE)**: Verify `run_backtest` computes turnover once symmetrically; ensure `tc`/`slippage_cost` aliases work and are applied correctly. Add tests for zero/negative turnover, NaN/inf weights.
2. **Edge cases**: Handle zero turnover days, constant weights, extreme moves. Ensure no division by zero, no NaN/inf leakage.
3. **Cost monotonicity**: Add tests proving higher costs/slippage -> lower/strictly worse returns.
4. **Liquidity/Participation Guards**: `max_position_size`, `max_turnover`/`max_total_turnover` exist; ensure they raise `BABDataError` on violations (not generic errors), no-ops when absent/None. Add tests for guard violations.
5. **Data Integrity**: Harden `load_prices()`/`load_returns()` for timezone-aware/naive, duplicates, all-NaN columns, malformed dates -> `BABDataError`. Benchmark with no finite values must raise.
6. **Pipeline safety**: Ensure betas/signals/weights never contain NaN/inf on valid inputs; coerce safely or raise consistently.

### Execution Rules
1. **START HERE** - Read `strategies/betting_against_beta/{backtest,portfolio,strategy,config,data_loader,beta,signals,metrics}.py` before changes.
2. **TDD MANDATORY** - Failing test → implement → pass. No new behavior without a test.
3. **BAB FIRST** - Product focus over infra.
4. **NO COMMIT** unless explicitly asked.
5. **HANDOFF DISCIPLINE** - Update this file when significant progress is made or blocked.

**GOAL**: Take BAB from functional to tradeable-realism hardened with tests proving robustness.

## Current State
- Branch: main @ HEAD
- Tests: **268 passed, 0 failed** (all green)
- CI pattern sync fixed in `.github/workflows/main.yml` (added `*/.github/workflows/*`)

## Bottlenecks Removed
- Workflow/Python exclude pattern drift (added `*/.github/workflows/*` to workflow stage_safe_changes list; suite was red at 266 passed / 2 failed, now 268 passed / 0 failed)

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- Every new behavior needs a test
- No NaN/inf in weights/signals/metrics on tested inputs
- Consistent `BABDataError` for data issues
- No fabricated market data

## UNCOMMITTED WORKING CHANGES
- `.github/workflows/main.yml` - pattern sync fix (`*/.github/workflows/*`)
