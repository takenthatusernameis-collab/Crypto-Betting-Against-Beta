# HANDOFF - 2026-10-28T06:17:57Z

## Timestamp
2026-10-28T06:17:57Z

## Purpose
Durable single handoff. Start here. Ignore older HANDOFF_*.md files unless explicitly needed for context. HANDOFF_NEXT_SESSION.md is a symlink to this file.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MUST START HERE)
**FOCUS CAMPAIGN: ADVANCE BAB REALISM TO TRADEABLE READINESS**

The codebase is in clean, test-green state (268 passed, 0 failed). All previously planned execution realism items are complete. Bottlenecks removed (CI/workflow pattern sync fixed). Next campaign: harden the BAB implementation for realistic execution & robustness without breaking existing behavior.

### Priority 1: Execution Realism (hard constraints)
- **Fees/slippage robustness**: Verify slippage/TC composition is consistent across backtest entry points (`run_backtest`, walk-forward paths). Ensure turnover-based slippage is applied symmetrically and documented. Add/strengthen tests if any edge case remains.
- **Liquidity/participation constraints**: If ADV/volume not present, add lightweight guards (configurable max turnover/position limits) that fail safely with `BABDataError` or are no-ops when data absent. Do NOT fabricate data.
- **Rebalance timing**: Confirm multi-day rebalance (daily/weekly/monthly) works with calendar alignment and partial periods; ensure no lookahead, weights held correctly.

### Priority 2: Data Integrity & Robustness
- **Real data ingestion**: Harden `load_prices()` for timezone-naive/aware dates, duplicate timestamps, missing assets, all-NaN columns (already handled), and ensure `BABDataError` on malformed dates consistently.
- **Benchmark/neutrality**: Verify dollar-neutrality and gross/net exposure enforcement across rebalances; portfolio risk checks should be comprehensive and tested.
- **Survivorship/delist**: Leverage existing DELISTED handling; consider logging/metrics but keep offline/testable.

### Priority 3: Evaluation & Validation
- **Walk-forward / OOS**: Ensure walk-forward logic doesn't leak (beta estimated on train only), rebalance calendar consistent. Add tests if gaps exist.
- **Metrics**: Confirm CAGR/Sharpe/turnover/slippage-aware PnL are correct and finite on expanded fixture.
- **Regression safety**: Keep all 268 tests passing. Any new behavior requires tests first (TDD).

### Execution Rules
1. **Start immediately** with Priority 1. Read relevant files (`strategies/betting_against_beta/backtest.py`, `strategy.py`, `portfolio.py`, `data_loader.py`, `config.py`) before changing anything.
2. **TDD**: Write failing test → implement → pass. Do not guess.
3. **Product-first**: BAB > infra. Only touch infra if blocking BAB.
4. **No commit** unless explicitly asked. Working tree may have intentional changes.
5. **Handoff discipline**: When significant progress made or blocked, update `HANDOFF.md` (timestamped) as single durable handoff.

**GOAL**: Move BAB from "feature-complete per previous campaign" to "robust against realistic frictions" with tests proving it.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted change** — `.github/workflows/main.yml` fixed for pattern sync (`*/.github/workflows/*` added) to match `scripts/controller_progress.py` EXCLUDE_PATTERNS.
- Environment: `pytest`, `pandas`, `numpy` installed.
- Suite: **268 passed, 0 failed** (all green).
- Previous campaign complete: slippage, multi-day rebalance, real price ingestion, portfolio risk checks, expanded fixture all done.

## Bottlenecks Removed
- CI/pattern-sync: Workflow and Python exclude lists now in lock-step; `test_python_patterns_are_subset_of_workflow`, `test_nested_workflow_pattern_is_present_in_workflow`, `test_workflow_patterns_are_subset_of_python`, `test_nested_kilo_progress_log_pattern_is_present_in_workflow` all pass.

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.
- No fabricated market data; use existing fixtures or add minimal fixtures only if necessary and justified.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to `stage_safe_changes()` case list (pattern sync fix).
