# HANDOFF - 2026-10-30T09:10:08Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T09:10:08Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark).

GATE: python3 -m pytest -q MUST stay GREEN. Last verified: 1012 passed, 11 skipped (GREEN). BAB tests (tests/test_betting_against_beta*.py) must pass.
BOTTLECKS: NONE. Controller/workflow drift already fixed (*/.github/workflows/* synced). No blockers.

CURRENT COVERAGE (BAB modules, term-missing):
- TOTAL BAB: 94% (2454 stmts / 140 miss) -> TARGET >=95%
- beta.py          88%  (27,52-53,71,73,75,77,80,82,85-86,98,105-106,108,118,120-121,124-125,142,154,156-159,301,309)  [START HERE]
- data_loader.py   89%  (37-41,44,64-65,72-73,107,117-119,159,178-179,183-184,221-222,247,302-304,321,331-333,357-358)
- backtest.py      91%  (53,58-59,69-70,77-78)
- quality.py       92%  (30,47-48,116,132,187-188,209,211-212,245-246,259)
- portfolio.py     94%  (29,39-40,87-88,155-160,200-201,275)
- regime.py        94%  (111,139-140,175-177,181-182,185,188,190,217)
- data_sources.py  94%  (20,47,94-95)
- signals 96%, strategy 97%, cli 97%, config 98%, costs 99%, sizing 99%, metrics 96%, shorting 95%, attribution/data/errors/__init__ 100%

MANDATORY CAMPAIGN (HEAVY WORK): Drive BAB total >=95%. Touch >=4 files with REAL LOGIC/TESTS. Do not do docs-only.

FOCUS ORDER:
1) beta.py (88%) - rolling OLS/min_obs/window, degenerate/collinear, NaN/inf handling
2) data_loader.py (89%) - coercion/tz/dates/empty/single-asset, NA/inf
3) backtest.py (91%) - costs, cumulative, one-day lag edges
4) quality.py (92%) - finiteness checks/strict raise paths

EXECUTE IN ORDER:
1. MEASURE: python3 -m pytest -q --cov=strategies.betting_against_beta --cov-report=term-missing to get exact current gaps/branches.
2. TDD PER GAP: For each uncovered line/branch in beta.py first, write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS (NaN/inf/zeros/mismatched shapes, ties, deciles/quantiles, one-day lag, dollar-neutral). Make them fail, fix minimal impl to be correct, go green.
3. REPEAT for data_loader.py, backtest.py, quality.py as needed to reach >=95% total BAB without regressing >=95% modules.
4. VERIFY: python3 -m pytest tests/test_betting_against_beta*.py -q && python3 -m pytest -q stay green. Report coverage delta per touched module + BAB total.
5. HANDOFF: ONLY update THIS HANDOFF.md at end if state materially changes. NO COMMITS unless explicitly asked.

STRICT RULES:
- Deterministic/offline/seeded only. No network.
- NO bare except:. Enforce finiteness (no NaN/inf).
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window constraints, rank logic.
- TDD: failing test -> minimal impl/fix -> green.
- BAB-first. Only touch infra/workflows if they break BAB gate.
- Real tests with assertions; >=4 files touched.
- Remove blockers before expanding scope.

START: open beta.py around missing lines and add failing tests covering each uncovered branch. Leave nothing critical untested.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core Modules: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB coverage TOTAL: 94% (target >=95%)
- Biggest gaps: beta.py 88%, data_loader.py 89%, backtest.py 91%, quality.py 92%
- Bottlenecks: NONE (workflow/controller drift resolved)
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >=4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
