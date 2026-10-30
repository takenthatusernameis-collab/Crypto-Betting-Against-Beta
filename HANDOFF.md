# HANDOFF - 2026-10-30T17:15:53Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T17:15:53Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/ - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta.

NON-NEGOTIABLE GATES (MUST REMAIN GREEN AT ALL TIMES):
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q (1122 passed, 11 skipped baseline - DO NOT REGRESS)
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q (BAB tests must stay GREEN)
- BAB COVERAGE: CURRENT 94% (2514 stmts / 144 miss) -> TARGET >= 95%. GAP: need to cover >=19 lines. THIS IS MANDATORY.

MANDATE: PUSH BAB COVERAGE FROM 94% TO >= 95%. TOUCH >= 4 DIFFERENT FILES WITH REAL LOGIC OR REAL TESTS. HEAVY WORK IS MANDATORY. DO NOT AVOID IT. DO NOT DO DOCS-ONLY OR TRIVIAL-ONLY CHANGES. NO SHORTCUTS.

BOTTLENECKS: NONE DETECTED. IF ANY GATE FAILS OR BAB BREAKS, FIX IMMEDIATELY BEFORE ANYTHING ELSE. REMOVE BOTTLENECKS RUTHLESSLY AND WITHOUT HESITATION.

ATTACK PLAN (MAXIMUM ROI, IN ORDER):
1. beta.py (89%, 30 misses) - _calc_rolling_beta_series degenerate/non-finite/insufficient paths, calculate_beta/calculate_beta_fast edge cases (all-NaN masks, alignment truncation, lstsq failures), rolling_beta fallbacks, estimate_betas parameter coercion. HIT EVERY BRANCH.
2. data_loader.py (89%, 31 misses) - _normalize_index tz/naive/duplicates/unparseable, _promote_datetime_column all candidate paths/unnamed/last-resort, _drop_all_nan_columns all-NaN case raising, _coerce_numeric percent/commas/NA markers/object paths/astype fallback, validate_returns_dataframe benchmark-all-NaN/only-benchmark/inf cases, load_* error paths (parquet/hdf5/pickle/json records/orient), edge coercions.
3. quality.py (92%, 15 misses) - data_quality_report combinations (with/without report dicts), strict checks, helper paths, NaN/inf/duplicates/outliers/constant/empty cases. Cover all missed lines.
4. backtest.py (91%, 7 misses) - one-day lag invariant enforcement, costs/slippage paths, cumulative paths, zero-trade/NaN cases.
5. portfolio.py/regime/signals/metrics/shorting/sizing/costs/config/strategy/data_sources as needed to reach >=95% and to satisfy ">=4 files touched".

EXECUTE EXACTLY (NO DEVIATION):
1. MEASURE FIRST: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. IDENTIFY EXACT MISSED LINES. WRITE DETERMINISTIC TDD TESTS WITH REAL ASSERTIONS (shapes/dtypes/finiteness/invariants). Fix minimally in implementation OR extend tests to hit missed branches - DO BOTH IF NEEDED. Touch REAL code or REAL tests with SUBSTANCE.
3. ROTATE AGGRESSIVELY: After each meaningful gain on P0, immediately move to next P0 until >=95%. MUST touch >=4 files with substantial real work. DO NOT STOP AT 3 FILES.
4. VERIFY CONSTANTLY: After changes, run BAB tests + full suite. Never leave gates red.
5. REPORT: before/after total BAB coverage + delta per touched module + exact list of files with real work touched + proof gates are green.

CONSTRAINTS (STRICT):
- BAB-FIRST. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network. NO time-based flakiness.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >=60 obs default, ranking logic.
- TDD, real assertions, >=4 files with real work. NO docs-only. NO trivial-only (whitespace/comments only).
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
- HEAVY WORK MANDATED - NEVER AVOID IT. Campaign self-propelling. Build momentum and DO NOT COAST.
- If you feel tempted to do easy work, DO THE HARD UNCOVERED BRANCHES INSTEAD.
```

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T17:15:53Z)
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
- Never coast. Always push uncovered branches. Always touch >=4 files with substance.
