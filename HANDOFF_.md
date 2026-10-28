# HANDOFF: Crypto-Betting-Against-Beta — Initial Task for Next Agentic Work Session

- Timestamp (UTC): 2026-10-28T03:24:06Z
- Repo: /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
- Branch: main @ HEAD (f0ff50b chore(kilo): checkpoint agent session)
- Pointer file: HANDOFF_NEXT_SESSION.md -> HANDOFF.md (this durable handoff)

## Objective
Resume work on the "Betting Against Beta" (BAB) crypto strategy. Scaffolding supports building it. BAB comes first, infra second.

## Status: PRIOR CAMPAIGN COMPLETE; BOTTLECK REMOVED
The "BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability" campaign is DONE (7 items, suite green). One blocker remained: the prior handoff claimed the CI pattern-sync fix was applied, but `*/.github/workflows/*` was missing from `.github/workflows/main.yml`, leaving the suite red (256 passed, 2 failed). That bottleneck is now removed — suite is 258 passed, 0 failed — with an intentional uncommitted change to `.github/workflows/main.yml` awaiting review/commit.

## Clear Initial Task Message (for the next agent)
**TASK:** Begin the inferred next focus campaign **BAB Execution Realism & Real-Market Backtesting**, product-first and TDD:

1. Slippage model priced on turnover in `backtest.py` (test first: slippage reduces cumulative vs zero-slippage, scales with turnover).
2. Multi-day rebalance honoring `config.rebalance_freq` (daily/weekly/monthly) (test first: weekly < daily rebalance events, weights constant in window).
3. Real price ingestion (price CSV/JSON with date column → returns, DatetimeIndex, gap handling; bad dates raise `BABDataError`).
4. Portfolio-level risk checks in `portfolio.py` (gross/net exposure, max single weight; raise on violation).
5. Expanded real-market fixture (8 crypto + BTC, ~400 rows, delisted all-NaN column, date gap) reused by 1–4.
6. Verify: `python3 -m pytest -q` all pass; re-timestamp HANDOFF.md and this file.

Do not skip items; each is gated by a failing test written first, then implementation, then green suite. Do not commit unless explicitly asked.

## Recon commands (run first)
`python3 -m pytest -q` (expect 258 passed), `git status`, `git diff --stat`, `git log --oneline -5`.

## Constraints
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- No NaN/inf weights/signals/metrics on any tested input; consistent BABDataError for data issues.
- Working changes intentionally uncommitted for review.

## Bottlenecks Removed
- `.github/workflows/main.yml` `stage_safe_changes()` now includes `*/.github/workflows/*`, restoring lock-step with `scripts/controller_progress.py` EXCLUDE_PATTERNS; all 4 pattern-sync tests pass; suite 258 passed, 0 failed.

## Uncommitted Working Changes (review before committing)
- `.github/workflows/main.yml` — added `*/.github/workflows/*` to stage_safe_changes case list.
