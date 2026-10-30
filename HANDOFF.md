# HANDOFF - 2026-10-30T06:36:56Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T06:36:56Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto).

GATE: python3 -m pytest -q MUST stay GREEN.
- BAB: 285 passed, 6 skipped (tests/test_betting_against_beta*.py)
- Full: 1012 passed, 11 skipped

CURRENT BOTTLENECKS: NONE VISIBLE (gates green). If any infra/test harness blocks BAB, REMOVE IT FIRST (verify gates green) before changing BAB scope.

MANDATORY CAMPAIGN (HEAVY WORK): DRIVE BAB TO >=95% TOTAL COVERAGE. THIS SESSION MUST TOUCH >=4 FILES WITH REAL LOGIC/TESTS.

FOCUS ORDER (by coverage gap + risk):
1) cli.py (0%) - implement minimal testable CLI surface or add targeted tests if logic exists; avoid expanding scope beyond BAB.
2) quality.py (7%) - data quality gates, NA/inf, coercion, tz/dates, shape checks.
3) attribution.py (14%) - factor/return attribution paths, edge cases (zeros/nans).
4) data_sources.py (42%) - source selection, fallbacks, errors (deterministic/offline).
5) signals.py (45%) - ranking/quantiles/deciles, tie handling, insufficient history.
6) strategy.py (53%) / portfolio.py (54%) - integration edges (one-day lag, dollar-neutral, rebalancing).
7) beta.py (59%) - rolling OLS edge cases (window/min obs, NaN/inf, collinearity), fast paths.
8) regime.py (63%) / data_loader.py (70%) / backtest.py (73%) / config.py (74%) - remaining gaps.

TASKS (DO IN ORDER):
1. MEASURE: Run targeted coverage on BAB modules to get exact missing lines/branches. (e.g. pytest with coverage on strategies.betting_against_beta)
2. HEAVY TDD: Pick >=2 modules from top of gap list. For each gap, write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS covering NaN/inf/zeros/mismatched shapes, tz/dates, coercion/NA, rolling stats edge cases, deciles/quantiles, ties, one-day lag, dollar-neutral, rank/decile logic, beta window constraints. Fix minimal implementation if needed to handle edge cases correctly.
3. VERIFY: python3 -m pytest tests/test_betting_against_beta*.py -q stays green AND python3 -m pytest -q stays green. Report coverage delta per touched module + total BAB.
4. HANDOFF DISCIPLINE: ONLY update THIS HANDOFF.md at end if state materially changes. NO COMMITS unless explicitly asked.

STRICT RULES:
- Deterministic/offline/seeded only. No network calls.
- NO bare except:. Enforce finiteness (no NaN/inf).
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window constraints, rank logic.
- TDD: failing test -> minimal impl/fix -> green.
- Focus BAB. Only touch infra/workflows if they break BAB gate.
- Add real tests with assertions; no docs-only changes. Heavy work required (>=4 files).
- If blocked, remove blocker before moving scope.

START NOW: Identify lowest-coverage BAB modules (cli/quality/attribution first) and begin heavy coverage work. Leave no low-hanging untested critical path behind.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (Frazzini–Pedersen methodology)
- Core Modules: strategies/betting_against_beta/ (all modules)
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB Tests: 285 passed, 6 skipped (GREEN)
- BAB Total Coverage: 65% (target >=95%)
- Top gaps: cli.py 0%, quality.py 7%, attribution.py 14%, data_sources.py 42%, signals.py 45%, strategy.py 53%, portfolio.py 54%, beta.py 59%, regime.py 63%, data_loader.py 70%, backtest.py 73%, config.py 74%, costs.py 99%, metrics.py 96%, sizing.py 98%, shorting.py 95%, data.py 100%, errors.py 100%, __init__.py 100%
- Bottlenecks: NONE VISIBLE. Gates green.
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >= 4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they block BAB progress, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
