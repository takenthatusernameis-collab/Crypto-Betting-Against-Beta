# HANDOFF - 2026-10-28T07:12:32Z

## Timestamp
2026-10-28T07:12:32Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**FOCUS CAMPAIGN: ADVANCE BAB REALISM TO TRADEABLE READINESS**

The codebase is in clean, test-green state (268 passed, 0 failed). Bottlenecks removed. Next: push BAB toward tradeable realism with stricter guards/tests where missing, without breaking behavior.

### Priority 1: Execution Realism (hard constraints)
- **Fees/slippage robustness**: Ensure turnover-based slippage/TC applied symmetrically across `run_backtest` (and any other entry points). Consider allowing alternative param names (`tc`, `slippage_cost`) and verify composition. Add tests for edge cases (zero/negative turnover, NaN/inf weights).
- **Liquidity/participation constraints**: Add lightweight guards for ADV/volume if present (or enforce `max_turnover`/`max_position_size`/`max_total_turnover`) that fail safely with `BABDataError`. When data absent, guards must be no-ops. Do NOT fabricate data.
- **Rebalance timing**: Confirm daily/weekly/monthly rebalance with calendar alignment, partial periods, no lookahead. Weights held between rebalance dates; turnover only changes on rebalance dates.

### Priority 2: Data Integrity & Robustness
- **Real data ingestion**: Harden `load_prices()`/`load_returns()` for timezone-naive/aware dates, duplicate timestamps, missing assets, all-NaN columns, malformed dates -> consistent `BABDataError`. Benchmark with no finite values must raise.
- **Benchmark/neutrality**: Enforce dollar-neutrality and gross/net exposure; use portfolio risk checks. Ensure no NaN/inf leak into weights/signals/metrics.
- **Survivorship/delist**: Leverage existing DELISTED/all-NaN dropping; consider explicit logging/metrics but keep offline/testable.

### Priority 3: Evaluation & Validation
- **Walk-forward / OOS**: If walk-forward paths exist or added, ensure beta estimated on train only, no leakage, calendar consistent. Add tests if gaps.
- **Metrics**: Verify CAGR/Sharpe/turnover/slippage-aware PnL correct/finite on fixtures.
- **Regression safety**: Keep all tests passing. Any new behavior requires tests first (TDD).

### Execution Rules
1. **Start immediately** with Priority 1. Read relevant files (`strategies/betting_against_beta/backtest.py`, `strategy.py`, `portfolio.py`, `data_loader.py`, `config.py`) before changing anything.
2. **TDD**: Write failing test → implement → pass. Do not guess.
3. **Product-first**: BAB > infra. Only touch infra if blocking BAB.
4. **No commit** unless explicitly asked. Working tree may have intentional changes.
5. **Handoff discipline**: When significant progress made or blocked, update `HANDOFF.md` (timestamped) as single durable handoff.

**GOAL**: Move BAB from "feature-complete" to "robust against realistic frictions" with tests proving it.

## Current State
- Branch main @ HEAD.
- Environment: `pytest`, `pandas`, `numpy` installed.
- Suite: **268 passed, 0 failed** (all green).
- Added lightweight liquidity/participation guards to `portfolio`/`strategy`/`config` (max_position_size, max_turnover/max_total_turnover) — no-ops if absent, raise `BABDataError` on violations. Hardened `run_backtest` for turnover calculation and alternative param names (`tc`, `slippage_cost`).
- CI/workflow pattern sync fixed in `.github/workflows/main.yml` (`*/.github/workflows/*` added).

## Bottlenecks Removed
- CI/pattern-sync: Workflow and Python exclude lists now in lock-step.
- Backtest robustness: more defensive alignment/cleanup, turnover computed once symmetrically.

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- No commit unless explicitly asked.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.
- No fabricated market data; use existing fixtures or add minimal fixtures only if necessary and justified.

## UNCOMMITTED WORKING CHANGES
- `.github/workflows/main.yml` — pattern sync fix
- `strategies/betting_against_beta/backtest.py` — robustness/hardening
- `strategies/betting_against_beta/config.py` — added liquidity guard fields
- `strategies/betting_against_beta/portfolio.py` — added liquidity/position/turnover guards
- `strategies/betting_against_beta/strategy.py` — plumbed guard params
