# HANDOFF - 2026-10-28T07:14:30Z

## Timestamp
2026-10-28T07:14:30Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**FOCUS CAMPAIGN: HARDEN BAB FOR TRADEABLE REALISM**

All tests green (268 passed, 0 failed). Bottlenecks removed (CI pattern sync fixed). Next agent MUST advance BAB robustness without breaking behavior.

### Priority 1: Fees/Slippage & Turnover Correctness (IMMEDIATE)
- **Symmetric turnover**: Verify `run_backtest` computes turnover once symmetrically; ensure `tc`/`slippage_cost` aliases work and are applied correctly. Add tests for zero/negative turnover, NaN/inf weights.
- **Edge cases**: Handle zero turnover days, constant weights, extreme moves. Ensure no division by zero, no NaN/inf leakage.
- **Cost monotonicity**: Maintain/add tests proving higher costs/slippage -> lower/strictly worse returns as expected.

### Priority 2: Liquidity/Participation Guards (ENFORCE STRICTLY)
- **Guards in place**: `max_position_size`, `max_turnover`/`max_total_turnover` exist in config/portfolio/strategy. Ensure they raise `BABDataError` on violations (not generic errors). Make no-ops when absent/None.
- **Tighten behavior**: Add tests for guard violations with clear errors. Consider per-row enforcement and alignment with previous weights.
- **No fabrication**: Never invent ADV/liquidity data - only enforce if provided.

### Priority 3: Data Integrity (HARDEN)
- **Robust loading**: Harden `load_prices()`/`load_returns()` for timezone-aware/naive, duplicates, all-NaN columns, malformed dates -> `BABDataError`. Benchmark with no finite values must raise.
- **Pipeline safety**: Ensure betas/signals/weights never contain NaN/inf on valid inputs; coerce safely or raise consistently.
- **Delisting/survivorship**: Existing behavior drops all-NaN columns; add logging/guards as needed without breaking tests.

### Priority 4: Evaluation Rigor
- **Walk-forward/OOS**: If adding walk-forward, beta on train only (no leakage). Calendar-aligned.
- **Metrics**: Verify finite values on fixtures; regression tests for key metrics.
- **TDD**: Write failing test first for any new behavior.

### Execution Rules
1. **START HERE** - Read `strategies/betting_against_beta/{backtest,portfolio,strategy,config,data_loader,beta,signals,metrics}.py` before changes.
2. **TDD MANDATORY** - Failing test → implement → pass.
3. **BAB FIRST** - Product focus over infra.
4. **NO COMMIT** unless explicitly asked.
5. **HANDOFF DISCIPLINE** - Update this file when significant progress made or blocked.

**GOAL**: Take BAB from functional to tradeable-realism hardened with tests proving robustness.

## Current State
- Branch: main @ HEAD
- Tests: **268 passed, 0 failed** (all green)
- Fixed CI pattern sync in `.github/workflows/main.yml` (added `*/.github/workflows/*`)
- Liquidity/participation guards added to config/portfolio/strategy (no-ops if absent)
- Backtest hardened for turnover and `tc`/`slippage_cost` aliases

## Bottlenecks Removed
- Workflow/Python exclude pattern drift (now in sync)
- Backtest robustness around turnover calculation

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable
- No commit unless explicitly asked
- Every new behavior needs a test
- No NaN/inf in weights/signals/metrics on tested inputs
- Consistent `BABDataError` for data issues
- No fabricated market data

## UNCOMMITTED WORKING CHANGES
- `.github/workflows/main.yml` - pattern sync fix
- `strategies/betting_against_beta/backtest.py` - robustness
- `strategies/betting_against_beta/config.py` - guard fields
- `strategies/betting_against_beta/portfolio.py` - guards
- `strategies/betting_against_beta/strategy.py` - guard plumbing
