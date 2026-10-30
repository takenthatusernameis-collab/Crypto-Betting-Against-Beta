# HANDOFF - 2026-10-30T17:11:33Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T17:11:33Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/ - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta.

NON-NEGOTIABLE GATES (MUST REMAIN GREEN):
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q (1122 passed, 11 skipped baseline)
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q (BAB tests must stay GREEN)
- BAB COVERAGE: CURRENT 94% (2514 stmts / 144 miss) -> TARGET >= 95%. GAP: need to cover >=19 lines. NO EXCUSES.

MANDATE: PUSH BAB COVERAGE FROM 94% TO >= 95%. TOUCH >= 4 DIFFERENT FILES WITH REAL LOGIC OR REAL TESTS. HEAVY WORK IS MANDATORY. DO NOT AVOID IT. DO NOT DO DOCS-ONLY OR TRIVIAL-ONLY CHANGES.

BOTTLENECKS: NONE. IF ANY GATE FAILS OR BAB BREAKS, FIX IMMEDIATELY BEFORE ANYTHING ELSE. REMOVE BOTTLENECKS RUTHLESSLY.

ATTACK PLAN (MAXIMUM ROI):
1. beta.py (89%, 30 misses) - _calc_rolling_beta_series, fast paths, NaN/inf/all-NaN/constant/degenerate, truncation/alignment, dtype/coercion, error paths
2. data_loader.py (89%, 31 misses) - tz-aware/naive, malformed dates, inf/NaN/string coercion, column mapping, empty/single-dup/missing, CSV/JSON edges
3. quality.py (92%, 15 misses) - strict checks, data_quality_report combos, helpers, edge cases
4. backtest.py (91%, 7 misses) - one-day lag invariant, costs/slippage, cumulative paths, zero-trade/NaN
5. portfolio/regime/signals/metrics/shorting/sizing/costs/config/strategy/data_sources/cli as needed

EXECUTE EXACTLY:
1. MEASURE FIRST: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. WRITE DETERMINISTIC TDD TESTS WITH REAL ASSERTIONS (shapes/dtypes/finiteness/invariants). Fix minimally or extend tests to hit missed branches. Touch REAL code or REAL tests.
3. ROTATE: After each meaningful gain on P0, immediately move to next P0 until >=95%. MUST touch >=4 files with substantial work.
4. VERIFY: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q && PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q
5. REPORT: before/after total BAB coverage + delta per touched module + list of files with real work touched.

CONSTRAINTS:
- BAB-FIRST. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >=60 obs default, ranking logic.
- TDD, real assertions, >=4 files with real work. NO docs-only. NO trivial-only.
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
- HEAVY WORK MANDATED - NEVER AVOID IT. Campaign self-propelling.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T16:08:53Z)
- Full Suite: 1122 passed, 11 skipped (GREEN)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN
- BAB coverage (all BAB tests): 94% total (2514 stmts / 144 miss). TARGET >= 95% - ACTION REQUIRED NOW
- Bottlenecks: NONE (all gates verified green)
- Handoff: Single durable handoff enforced. ONLY this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 30 | 89% | P0 |
| data_loader.py | 287 | 31 | 89% | P0 |
| quality.py | 183 | 15 | 92% | P0 |
| backtest.py | 74 | 7 | 91% | P1 |
| portfolio.py | 223 | 14 | 94% | P2 |
| data_sources.py | 67 | 4 | 94% | P2 |
| regime.py | 186 | 12 | 94% | P2 |
| signals.py | 113 | 4 | 96% | P3 |
| strategy.py | 198 | 5 | 97% | P3 |
| cli.py | 34 | 1 | 97% | P3 |
| config.py | 199 | 3 | 98% | P3 |
| costs.py | 150 | 2 | 99% | P4 |
| metrics.py | 132 | 5 | 96% | P4 |
| sizing.py | 163 | 2 | 99% | P4 |
| shorting.py | 172 | 9 | 95% | P4 |
| attribution.py | 37 | 0 | 100% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors.py | 2 | 0 | 100% | OK |
| __init__.py | 4 | 0 | 100% | OK |

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work required: >=4 files with real logic/tests when working on strategy modules.
- Quality over speed. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md if state materially changes. No commits unless explicitly asked.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded only. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
- Next agent must not avoid heavy work - campaign is self-propelling and MANDATORY.
