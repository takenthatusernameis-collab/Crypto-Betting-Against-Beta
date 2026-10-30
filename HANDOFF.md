# HANDOFF - 2026-10-30T11:35:15Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T11:35:15Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > EVERYTHING ELSE.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark, dollar-neutral portfolio).

GATE: python3 -m pytest -q MUST stay GREEN.
- Full suite: 1109 passed, 11 skipped (GREEN - bottlenecks REMOVED).
- BAB suite: python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q MUST stay GREEN.
- BAB coverage NOW: 94% total (2474 stmts / 141 miss). TARGET: >= 95%. NO EXCUSES.

BLOCKERS: NONE. Gates restored to green.

CAMPAIGN: DRIVE BAB TOTAL COVERAGE FROM 94% TO >= 95%. Touch >= 3 FILES WITH REAL LOGIC OR REAL TESTS. Do NOT do docs-only work. No network calls. Deterministic/seeded/offline only.

FOCUS ORDER (smallest gaps remaining, highest ROI to cross >=95%):
1) beta.py (89%)       - 26 misses. Cover remaining branches: _calc_rolling_beta_series edge cases, calculate_beta_fast, NaN/inf handling, insufficient history paths, truncation/alignment, degenerate variances.
2) data_loader.py (89%) - 31 misses. Cover tz/naive, coercion, malformed dates/errors, NA/inf, bad indices, column mapping, empty/single-asset, CSV/JSON edge cases.
3) quality.py (91%)     - 16 misses. Cover remaining branches in check_data_quality/data_quality_report and helpers (strict paths, inf/nan combos).
4) backtest.py (91%)    - 7 misses. Enforce one-day lag invariant, costs/slippage edge cases, cumulative paths.
5) others (portfolio/regime/signals/metrics/shorting/sizing/costs/config/strategy/data_sources) - fill remaining as needed.

EXECUTE:
1. MEASURE: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. PICK TOP UNCOVERED LINES IN P0. Write DETERMINISTIC tests with REAL ASSERTIONS (shapes, dtypes, finiteness, invariants). TDD: failing test -> minimal correct fix -> green.
3. REPEAT until BAB total >= 95% AND you have touched >= 3 files with real logic/tests. Keep gates green the whole time.
4. VERIFY: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q && PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q
5. Report: coverage delta per touched module + BAB total before/after.

STRICT RULES:
- BAB-FIRST ALWAYS. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >=60 obs default, ranking logic.
- TDD discipline. Real assertions. >=3 files touched with real work.
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
- HEAVY WORK: Do not stop at trivial edits. Build the next focus campaign by attacking uncovered branches aggressively.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED)
- Full Suite: 1109 passed, 11 skipped (GREEN)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): 937 passed, 11 skipped (GREEN)
- BAB coverage (all BAB tests): 94% total (2474 stmts / 141 miss). TARGET >= 95%
- Bottlenecks: NONE (gates verified green)
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 235 | 26 | 89% | P0 |
| data_loader.py | 287 | 31 | 89% | P0 |
| quality.py | 183 | 16 | 91% | P0 |
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
- Heavy work required: >=3 files with real logic/tests when working on strategy modules.
- Quality over speed. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md if state materially changes. No commits unless explicitly asked.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded only. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
- Next agent must not avoid heavy work - campaign is self-propelling.