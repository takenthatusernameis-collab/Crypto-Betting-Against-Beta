# HANDOFF - 2026-10-30T06:16:18Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T06:16:18Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto).

GATE: python3 -m pytest -q MUST stay GREEN.
- BAB: 285 passed, 6 skipped (tests/test_betting_against_beta*.py)
- Full: 1012 passed, 11 skipped (2 controller tests fixed by workflow pattern-sync)
BOTTLENECKS REMOVED: Added `*/.github/workflows/*` to stage_safe_changes in `.github/workflows/main.yml`. Controller suite 68/68 green.

CAMPAIGN: DRIVE BAB TO >=95% TOTAL COVERAGE WITH HEAVY WORK (>=4 FILES WITH REAL LOGIC/TESTS THIS SESSION). NO DOCS-ONLY CHANGES.

CURRENT FOCUS: Push uncovered paths in core BAB modules (data_loader, beta, backtest/portfolio/quality/regime/shorting/signals/metrics/costs/config). Add deterministic, offline, seeded tests with real assertions for branches (NaN/inf/zeros/mismatched shapes, tz/dates, coercion/NA markers, edge cases in rolling stats, deciles/quantiles, one-day lag, dollar-neutral). Enforce finiteness; no bare except:.

KEEP PASSING:
- tests/test_bab_data_loader_campaign.py
- tests/test_bab_beta_campaign.py
- tests/test_bab_strategy_campaign.py
- tests/test_bab_data_sources_campaign.py
- tests/test_bab_data_loader_campaign_heavy.py
- tests/test_bab_data_loader_deep.py
- tests/test_bab_data_loader_heavy_extra.py
- tests/test_bab_beta_heavy_extra.py
- tests/test_bab_backtest_portfolio_heavy_extra.py

MANDATORY RULES:
- TDD: failing test -> minimal impl/fix -> green. Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf). Handle NaN/inf/zeros/mismatched shapes/dates/non-monotonic cases.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile logic, beta window constraints, rank/decile logic.
- Validate: `python3 -m pytest tests/test_betting_against_beta*.py -q` stays green AND `python3 -m pytest -q` stays green.
- ONLY update THIS HANDOFF.md. NO COMMITS unless explicitly asked.
- Focus BAB strategy. Do not touch infra/workflows unless they break the BAB gate.
- Add real tests with assertions for uncovered logic. Heavy work required (>=4 files).
- If blocked, remove the blocker before moving scope. Coverage target >=95% total.

IMMEDIATE NEXT TASK (do first):
1. Run full BAB suite + quick coverage scan (or just run targeted tests) to identify lowest-coverage files among strategies/betting_against_beta/*.py. Pick >=2 highest-value uncovered modules and add >=4 new test functions/files worth of real coverage (or extend existing campaign tests).
2. Prioritize data_loader and beta (common sources of uncovered branches).
3. Keep all gates green, report coverage delta, and update ONLY this HANDOFF.md at end if state materially changes.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- Core Modules: strategies/betting_against_beta/ (all modules)
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB Tests: 285 passed, 6 skipped (GREEN)
- Bottlenecks: Removed - pattern-sync fixed in `.github/workflows/main.yml` (added `*/.github/workflows/*`). Controller tests all pass (68/68).
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >= 4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they block BAB progress, verify gates green, resume campaign.
