# HANDOFF - 2026-10-30T10:16:57Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T10:16:57Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY: strategies/betting_against_beta/ > EVERYTHING ELSE.
REPO_IDENTITY: Crypto-Betting-Against-Beta (Frazzini–Pedersen Betting Against Beta for crypto: long low-beta, short high-beta vs BTC benchmark, dollar-neutral portfolio).

GATE: python3 -m pytest -q MUST stay GREEN.
- Full suite: 1012+ passed (currently 1012 passed, 11 skipped) — DO NOT regress.
- BAB suite: python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q MUST stay GREEN.
- BAB coverage NOW: 65% total (857 missed of 2454 stmts). TARGET: >= 95% BAB coverage. NO EXCUSES.

BOTTLENECKS: NONE. Gates green. Blockers removed. Proceed with HEAVY WORK.

CAMPAIGN: DRIVE BAB TOTAL COVERAGE TO >= 95%. Touch >= 4 FILES WITH REAL LOGIC OR REAL TESTS. Do NOT do docs-only work. No network calls. Deterministic/seeded/offline only.

FOCUS ORDER (biggest uncovered surface, highest ROI):
1) quality.py (7%)    - Nearly untested. Add/extend deterministic tests covering ALL public functions + edge cases (NaN/inf/empty/degenerate/non-datetime/duplicates). Make every branch hit.
2) beta.py (59%)      - Expand tests for calculate_beta, calculate_rolling_beta, _calc_rolling_beta_series, calculate_beta_fast, estimate_betas. Cover truncation/alignment, insufficient history (<60 obs), degenerate variances, NaN/inf, ties, NaN propagation.
3) data_loader.py (70%)- Cover CSV/JSON loaders, tz/naive handling, coercion, empty/single-asset, malformed dates (enforce BABDataError), NA/inf, bad indices, column mapping, edge cases.
4) backtest.py (73%)  - Costs, slippage, one-day lag enforcement (critical invariant), cumulative paths, transaction costs on turnover, edge cases with NaN/inf/flat periods.
5) signals.py (45%), strategy.py (53%), portfolio.py (54%), regime.py (63%) - Fill remaining branches as you go.

EXECUTE:
1. MEASURE: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. PICK TOP UNCOVERED LINES IN P0 MODULE. Write DETERMINISTIC tests with REAL ASSERTIONS (shapes, dtypes, finiteness, invariants). TDD: failing test -> minimal correct fix -> green.
3. REPEAT until BAB total >= 95% AND you have touched >= 4 files with real logic/tests. Keep gates green the whole time.
4. VERIFY: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q && PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q
5. Report: coverage delta per touched module + BAB total before/after.

STRICT RULES:
- BAB-FIRST ALWAYS. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >=60 obs default, ranking logic.
- TDD discipline. Real assertions. >=4 files touched with real work.
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED)
- Full Suite: 1109 passed, 11 skipped (GREEN)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (285 passed, 6 skipped in BAB-specific set; combined all BAB tests passing)
- BAB coverage (all BAB tests): 65% total (2454 stmts / 857 miss). TARGET >= 95%
- Bottlenecks: NONE - gates green, ready for heavy campaign
- Handoff: Single durable handoff enforced. Only this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| quality.py | 163 | 152 | 7% | P0 (BIGGEST GAP) |
| attribution.py | 37 | 32 | 14% | P4 |
| data_sources.py | 67 | 39 | 42% | P4 |
| signals.py | 113 | 62 | 45% | P3 |
| strategy.py | 198 | 93 | 53% | P3 |
| portfolio.py | 223 | 103 | 54% | P3 |
| beta.py | 235 | 96 | 59% | P1 |
| regime.py | 186 | 69 | 63% | P3 |
| data_loader.py | 287 | 85 | 70% | P1 |
| backtest.py | 74 | 20 | 73% | P2 |
| config.py | 199 | 52 | 74% | P4 |
| shorting.py | 172 | 9 | 95% | OK |
| sizing.py | 163 | 4 | 98% | OK |
| costs.py | 150 | 2 | 99% | OK |
| metrics.py | 132 | 5 | 96% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors.py | 2 | 0 | 100% | OK |
| __init__.py | 4 | 0 | 100% | OK |
| cli.py | 34 | 34 | 0% | LOW (only after >=95%) |

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work required: >=4 files with real logic/tests when working on strategy modules.
- Quality over speed. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md if state materially changes. No commits unless explicitly asked.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded only. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >=95% total for BAB strategy modules.
