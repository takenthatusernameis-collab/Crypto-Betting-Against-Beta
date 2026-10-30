# HANDOFF - 2026-10-30T09:40:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T09:40:00Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > everything else.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark).

GATE: python3 -m pytest -q MUST stay GREEN. Last verified: 1012 passed, 11 skipped (GREEN). BAB tests (tests/test_betting_against_beta*.py) must pass (last run: 285 passed, 6 skipped).

BOTTLECKS: NONE. No infrastructure/workflow blockers detected.

CAMPAIGN: DRIVE BAB TOTAL COVERAGE >= 95%. Touch >= 4 FILES WITH REAL LOGIC/TESTS. No docs-only work.

FOCUS ORDER (by impact + uncovered surface):
1) quality.py (7%)   - Entire module untested. Add deterministic unit tests for all public functions + edge cases (NaN/inf/empty/degenerate). This is the biggest gap.
2) beta.py (59%)     - Expand tests for calculate_beta, calculate_rolling_beta, _calc_rolling_beta_series, calculate_beta_fast, estimate_betas. Cover truncation/alignment, insufficient history, degenerate variances, NaN/inf, ties.
3) data_loader.py (70%) - Cover CSV/JSON loaders, tz/naive handling, coercion, empty/single-asset, malformed dates (enforce BABDataError), NA/inf, bad indices.
4) backtest.py (73%) - Costs, one-day lag enforcement, cumulative paths, transaction costs, edge cases with NaN/inf/flat periods.

EXECUTE IN ORDER:
1. MEASURE: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. TDD PER GAP: For each uncovered line/branch, write DETERMINISTIC/OFFLINE/SEEDED tests with REAL ASSERTIONS (shapes, finiteness, invariants). Make them fail, fix minimal impl to be correct, go green.
3. REPEAT until BAB total >= 95% without regressing >=95% modules. Touch >=4 files.
4. VERIFY: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py -q && PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q stay green. Report coverage delta per touched module + BAB total.
5. HANDOFF: ONLY update THIS HANDOFF.md at end if state materially changes. NO COMMITS unless explicitly asked.

STRICT RULES:
- Deterministic/offline/seeded only. No network.
- NO bare except:. Enforce finiteness (no NaN/inf). Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window constraints (>=60 obs default), rank logic.
- TDD: failing test -> minimal impl/fix -> green.
- BAB-first. Only touch infra/workflows if they break BAB gate.
- Real tests with assertions; >=4 files touched.
- Remove blockers before expanding scope.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core Modules: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: `strategies/betting_against_beta/` above everything else

## CURRENT STATE (MEASURED)
- Full Suite: 1012 passed, 11 skipped (GREEN)
- BAB tests: 285 passed, 6 skipped (GREEN)
- BAB coverage (tests/test_betting_against_beta*.py): 65% total (2454 stmts / 857 miss). TARGET: >= 95%
- Bottlenecks: NONE
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| quality.py | 163 | 152 | 7% | P0 |
| attribution.py | 37 | 32 | 14% | P4 |
| data_sources.py | 67 | 39 | 42% | P4 |
| portfolio.py | 223 | 103 | 54% | P3 |
| beta.py | 235 | 96 | 59% | P1 |
| regime.py | 186 | 69 | 63% | P3 |
| data_loader.py | 287 | 85 | 70% | P1 |
| backtest.py | 74 | 20 | 73% | P2 |
| config.py | 199 | 52 | 74% | P4 |
| signals.py | 113 | 62 | 45% | P3 |
| strategy.py | 198 | 93 | 53% | P3 |
| shorting.py | 172 | 9 | 95% | OK |
| sizing.py | 163 | 4 | 98% | OK |
| costs.py | 150 | 2 | 99% | OK |
| metrics.py | 132 | 5 | 96% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors/__init__ | 2 | 0 | 100% | OK |
| __init__ | 4 | 0 | 100% | OK |
| cli.py | 34 | 34 | 0% | LOW (only if time after >=95%) |

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work: >=4 files with real logic/tests per session when working on strategy modules.
- Quality over speed: correctness always wins. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
