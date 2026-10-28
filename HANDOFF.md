# HANDOFF - 2026-10-28T03:14:03Z

## Timestamp
2026-10-28T03:14:03Z

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## Project Name Priority
Repository: **Crypto-Betting-Against-Beta**. Product is the "Betting Against Beta" (BAB) crypto strategy — market-neutral, long low-beta / short high-beta crypto assets vs a benchmark (default BTC), dollar-neutral equal weights, rolling OLS beta, one-day-lagged backtest. Scaffolding (agent loop, accounting, diagnostics) supports building it. Everything below is ranked by that product name: BAB comes first, infra second.

## Current State
- Branch main @ HEAD. Working tree: **intentional uncommitted changes** (see below). Tests: **249 passed, 0 failed** (was 247; +2 after unblocking).
- Environment unblocked this session: `pytest`, `pandas`, `numpy` were not installed, so `python3 -m pytest -q` was a hard blocker. Installed via `pip install -r requirements.txt`. The test suite now runs locally.
- Bottleneck removed this session:
  - `.github/workflows/main.yml` `stage_safe_changes()` case list was missing the nested variant `*/.github/workflows/*` that `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS` requires. Drift meant a vendored workflow file under a subdirectory could be staged as meaningful progress, silently corrupting controller progress accounting. Restored lock-step; `TestStageSafeChangesPatternSync` (4/4) now passes and `python3 -m pytest -q` is green (249 passed, 0 failed).
- Prior HANDOFF claims (lock-step restored, messy-data tests, delisted-asset dropping, beta robustness, report sanitizer) are reflected in the tree and now verified green.

## INITIAL TASK FOR NEXT SESSION (Do This First)

### Focus Campaign: BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability (HEAVY - do all of it)
The core BAB pipeline (synthetic data, beta, signals, portfolio, backtest, metrics) is implemented and tested. Now harden for production-like crypto data and make the end-to-end report/CLI path observable and trustworthy without breaking tests.

Recon (fast): `python3 -m pytest -q`, `git status`, `git diff --stat`.

1) **Real-data end-to-end smoke**: Run `python3 scripts/bab_backtest_report.py --data-source tests/fixtures/real_data_defects.csv --json` and assert the emitted JSON is valid, finite, and carries expected config keys (universe, benchmark, beta_window, long/short quantile, transaction_costs, data_source). Add a test (`TestReportRealDataSmoke`) asserting no NaN/inf metrics and non-empty universe on the messy fixture.
2) **Transaction costs end-to-end**: Run the report with `--transaction-costs 0.001` (10 bps) and assert `metrics.turnover` > 0 and the cost path is reflected (cumulative with costs <= cumulative without costs on the same data). Add a test (`TestTransactionCostsPath`) comparing `--transaction-costs 0.0` vs `0.001`.
3) **Non-BTC benchmark**: Run the report with `--benchmark ETH` on a fixture containing ETH and assert the strategy runs, beta vs ETH is estimated, and weights are finite. Add a test (`TestNonBtcBenchmark`).
4) **min_rows enforcement**: `BABStrategy.run()` must raise `BABDataError` when real data has fewer than `config.min_rows` rows; synthetic default path unaffected. Add tests (`TestMinRowsEnforcement`).
5) **Report determinism/idempotency**: Running `bab_backtest_report.py --json` twice on the same source must produce byte-identical metrics (except `captured_at`-free report payload). Add a test (`TestReportDeterminism`).
6) **CI/Infra sync guardrail**: Keep `EXCLUDE_PATTERNS` in `scripts/controller_progress.py` and the `stage_safe_changes` list in `.github/workflows/main.yml` in lock-step; the 4 pattern-sync tests must pass on every run.
7) **Verify + handoff**: `python3 -m pytest -q` all pass (249+); update this handoff with a new timestamp and record completed campaign items in UNCOMMITTED WORKING CHANGES.

## ACCEPTANCE CRITERIA
- [ ] `python3 -m pytest -q` all pass (249+)
- [ ] Real-data smoke test passes on `tests/fixtures/real_data_defects.csv` via `--json` (finite metrics)
- [ ] Transaction-cost path test passes (turnover > 0; costs reduce cumulative vs zero-cost)
- [ ] Non-BTC benchmark test passes (ETH benchmark, finite weights)
- [ ] min_rows enforcement test passes (BABDataError on insufficient rows)
- [ ] Report determinism test passes (identical JSON metrics across runs)
- [ ] CI pattern-sync tests pass (4/4)
- [ ] Every new behavior has a test
- [ ] Handoff updated with new timestamp

## CONSTRAINTS
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- Do not commit unless explicitly asked; working changes intentionally uncommitted for review.
- Every new behavior must have a test.
- No NaN/inf weights/signals/metrics on any tested input; consistent `BABDataError` for data issues.

## UNCOMMITTED WORKING CHANGES (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to the `stage_safe_changes()` case list to restore lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS (bottleneck removal; 2 previously-failing pattern-sync tests now pass).
