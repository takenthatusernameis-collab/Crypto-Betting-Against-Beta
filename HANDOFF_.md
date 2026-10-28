# HANDOFF: Crypto-Betting-Against-Beta — Initial Task for Next Agentic Work Session

- Timestamp (UTC): 2026-10-28T03:22:00Z
- Repo: /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
- Branch: main
- Pointer file: HANDOFF_NEXT_SESSION.md -> this file

## Objective
Resume work on the "Betting Against Beta" (BAB) crypto strategy. Scaffolding supports building it. BAB comes first, infra second.

## Status: CAMPAIGN COMPLETE
The "BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability" campaign is DONE. All 7 items completed, 9 new tests added, suite 258 passed, 0 failed.

## Clear Initial Task Message (for the next agent)
**TASK:** No heavy campaign is pending. The next focus is to review the uncommitted working changes below, decide whether to commit them, and then either (a) extend BAB production readiness (e.g. slippage model, multi-day rebalance, real price CSV ingestion with date parsing, universe override via config, portfolio-level risk checks, live-data fixture expansion), or (b) pick up a new product-first BAB item from the backlog. Recon: `python3 -m pytest -q`, `git status`, `git diff --stat`. Do not commit unless explicitly asked.

## Constraints
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- No NaN/inf weights/signals/metrics on any tested input; consistent BABDataError for data issues.
- Working changes intentionally uncommitted for review.

## Bottlenecks Removed
- `.github/workflows/main.yml` `stage_safe_changes()` now includes `*/.github/workflows/*`, restoring lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS; 4 pattern-sync tests pass.
- All 7 campaign items completed: real-data smoke, transaction costs path, non-BTC benchmark, min_rows enforcement, report determinism, CI pattern sync, verify + handoff.

## Uncommitted Working Changes (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to stage_safe_changes case list.
- `tests/test_bab_backtest_report.py` — added TestReportRealDataSmoke, TestTransactionCostsPath, TestNonBtcBenchmark, TestReportDeterminism.
- `tests/test_betting_against_beta.py` — added TestMinRowsEnforcement (3 tests) + BABStrategy import.