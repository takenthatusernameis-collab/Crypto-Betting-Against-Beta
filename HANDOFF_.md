# HANDOFF: Crypto-Betting-Against-Beta — Initial Task for Next Agentic Work Session

- Timestamp (UTC): 2026-10-28T03-18-05Z
- Repo: /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
- Branch: main
- Pointer file: HANDOFF_NEXT_SESSION.md -> this file

## Objective
Resume work on the "Betting Against Beta" (BAB) crypto strategy. Scaffolding supports building it. BAB comes first, infra second.

## Clear Initial Task Message (for the next agent)
**TASK:** Focus Campaign: BAB Production Readiness — Real-Data Path, Transaction Costs & Report Observability (HEAVY - do all of it). Recon: `python3 -m pytest -q`, `git status`, `git diff --stat`. Then: (1) real-data end-to-end smoke on tests/fixtures/real_data_defects.csv via --json with TestReportRealDataSmoke; (2) transaction costs end-to-end TestTransactionCostsPath; (3) non-BTC benchmark TestNonBtcBenchmark (ETH); (4) min_rows enforcement TestMinRowsEnforcement; (5) report determinism TestReportDeterminism; (6) CI/infra pattern sync guardrail 4/4; (7) verify + handoff. Every new behavior needs a test. Do not commit unless explicitly asked.

## Constraints
- Product-first (BAB), TDD, offline/testable, handoff discipline.
- No NaN/inf weights/signals/metrics on any tested input; consistent BABDataError for data issues.
- Working changes intentionally uncommitted for review.

## Bottlenecks Removed
- .github/workflows/main.yml stage_safe_changes restored lock-step with scripts/controller_progress.py EXCLUDE_PATTERNS (*/.github/workflows/*); suite 249 passed, 0 failed.