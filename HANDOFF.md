# HANDOFF - 2026-10-30T08:54:33Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T08:54:33Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark).

GATE: python3 -m pytest -q MUST stay GREEN. Last verified: 1012 passed, 11 skipped (GREEN). BAB tests (tests/test_betting_against_beta*.py) must pass.
BOTTLENECK REMOVED (this session): .github/workflows/main.yml stage_safe_changes case list was missing `*/.github/workflows/*` which Python EXCLUDE_PATTERNS (scripts/controller_progress.py:28) requires. Synced the two lists → controller tests now green (68 passed), full suite green. Do not re-introduce drift between the two lists.

CURRENT COVERAGE (BAB modules, measured against BAB test files): TOTAL 94% (2454 stmts / 140 miss). TARGET: >=95% total.
Per-module missing lines (term-missing output):
- beta.py          88%  27, 52-53, 71, 73, 75, 77, 80, 82, 85-86, 98, 105-106, 108, 118, 120-121, 124-125, 142, 154, 156-159, 301, 309   <-- HIGHEST GAP, start here
- data_loader.py   89%  37-41, 44, 64-65, 72-73, 107, 117-119, 159, 178-179, 183-184, 221-222, 247, 302-304, 321, 331-333, 357-358
- backtest.py      91%  53, 58-59, 69-70, 77-78
- quality.py       92%  30, 47-48, 116, 132, 187-188, 209, 211-212, 245-246, 259
- portfolio.py     94%  29, 39-40, 87-88, 155-160, 200-201, 275
- regime.py        94%  111, 139-140, 175-177, 181-182, 185, 188, 190, 217
- data_sources.py  94%  20, 47, 94-95
- maintained >=95%+: signals 96%, strategy 97%, cli 97%, config 98%, costs 99%, sizing 99%, metrics 96%, shorting 95%, attribution/data/errors/__init__ 100%

MANDATORY CAMPAIGN (HEAVY WORK): DRIVE BAB TOTAL COVERAGE TO >=95%. THIS SESSION MUST TOUCH >=4 FILES WITH REAL LOGIC/TESTS.

FOCUS ORDER (by coverage gap + risk):
1) beta.py (88%) - rolling OLS edge cases (window/min obs, NaN/inf, collinearity/degenerate), calculate_beta alignment/min_obs. Missing lines listed above.
2) data_loader.py (89%) - price/return loading, coercion, tz/dates, empty/single-asset rows.
3) backtest.py (91%) - transaction costs, cumulative returns, one-day lag edges.
4) quality.py (92%) - NaN/inf counting, strict raise, missing/inf triggers.
Then preserve >=95% on signals/strategy/cli/config/costs/sizing/metrics/shorting/attribution.

TASKS (DO IN ORDER):
1. MEASURE: python3 -m pytest -q --cov=strategies.betting_against_beta.beta --cov-report=term-missing (repeat per module) to confirm exact missing lines/branches.
2. HEAVY TDD: Pick >=2 top-gap modules (beta/data_loader first). For each gap write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS covering NaN/inf/zeros/mismatched shapes, tz/dates, coercion/NA, rolling stats edge cases, deciles/quantiles, ties, one-day lag, dollar-neutral, rank/decile logic, beta window constraints. Fix minimal implementation if needed to handle edge cases correctly.
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

START NOW: Open beta.py missing lines and write failing tests for each uncovered branch. Leave no low-hanging untested critical path behind.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta assets, short high-beta assets vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core Modules: strategies/betting_against_beta/ (all modules)
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB coverage TOTAL: 94% (target >=95%)
- Biggest gaps: beta.py 88%, data_loader.py 89%, backtest.py 91%, quality.py 92%
- Bottlenecks: NONE. Controller test drift fixed (added */.github/workflows/* to stage_safe_changes case list); gates green (1012 passed, 11 skipped).
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
