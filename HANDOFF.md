# HANDOFF - 2026-10-28T03:22:00Z

## Timestamp
2026-10-28T03:22:00Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see below).
- Environment unblocked: `pytest`, `pandas`, `numpy` installed via `pip install -r requirements.txt`; `python3 -m pytest -q` runs locally.
- Suite: **258 passed, 0 failed** (was 249; +9 campaign tests added this session).

## CAMPAIGN COMPLETE: BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability
All 7 campaign items completed this session. Every new behavior has a test.

1) **Real-data end-to-end smoke**: `TestReportRealDataSmoke` in `tests/test_bab_backtest_report.py` asserts the `--json` report on `tests/fixtures/real_data_defects.csv` is valid, finite, carries expected config keys (universe, benchmark, beta_window, long/quantile, short_quantile, transaction_costs, data_source), and has a non-empty universe.
2) **Transaction costs end-to-end**: `TestTransactionCostsPath` asserts `metrics.turnover > 0` with `--transaction-costs 0.001` and that cumulative-with-costs <= cumulative-without-costs on the same fixture.
3) **Non-BTC benchmark**: `TestNonBtcBenchmark` runs `--benchmark ETH` on the messy fixture, asserts finite strategy_beta and finite metrics.
4) **min_rows enforcement**: `TestMinRowsEnforcement` in `tests/test_betting_against_beta.py` asserts `BABStrategy.run()` raises `BABDataError` on short real data (DataFrame and CSV paths) and that the synthetic default path is unaffected.
5) **Report determinism/idempotency**: `TestReportDeterminism` asserts two `--json` runs on the same source produce byte-identical metrics, config, and rebalances.
6) **CI/Infra sync guardrail**: `EXCLUDE_PATTERNS` in `scripts/controller_progress.py` and the `stage_safe_changes` list in `.github/workflows/main.yml` are in lock-step; the 4 pattern-sync tests pass on every run.
7) **Verify + handoff**: `python3 -m pytest -q` all pass (258); handoff updated with new timestamp.

## ACCEPTANCE CRITERIA
- [x] `python3 -m pytest -q` all pass (258)
- [x] Real-data smoke test passes on `tests/fixtures/real_data_defects.csv` via `--json` (finite metrics)
- [x] Transaction-cost path test passes (turnover > 0; costs reduce cumulative vs zero-cost)
- [x] Non-BTC benchmark test passes (ETH benchmark, finite weights)
- [x] min_rows enforcement test passes (BABDataError on insufficient rows)
- [x] Report determinism test passes (identical JSON metrics across runs)
- [x] CI pattern-sync tests pass (4/4)
- [x] Every new behavior has a test
- [x] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to the `stage_safe_changes()` case list to restore lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS (bottleneck removal; 2 previously-failing pattern-sync tests now pass; suite 258 passed, 0 failed).
- `tests/test_bab_backtest_report.py` — added `TestReportRealDataSmoke`, `TestTransactionCostsPath`, `TestNonBtcBenchmark`, `TestReportDeterminism` (4 new test classes, 9 new tests).
- `tests/test_betting_against_beta.py` — added `TestMinRowsEnforcement` (3 new tests) and imported `BABStrategy`.