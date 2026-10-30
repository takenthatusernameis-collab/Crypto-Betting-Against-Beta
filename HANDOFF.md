# HANDOFF - 2026-10-30T20:02:04Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T20:02:04Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/ - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta. Repo name drives prioritization: the BAB strategy module is absolute priority above everything else.
```

## NON-NEGOTIABLE GATES (MUST REMAIN GREEN AT ALL TIMES)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q` (FULL SUITE GREEN: 1416 passed, 11 skipped, ~117s)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q` (BAB tests GREEN: 1244 passed, 11 skipped)
- BAB COVERAGE: CURRENT 96% (2514 stmts / 106 miss) - TARGET >= 95% ACHIEVED, >= 96% DISPLAYED. MAINTAIN OR IMPROVE. DO NOT REGRESS BELOW 95%.

## BOTTLENECK STATUS
- RESOLVED. Full suite was RED (2 failures in `tests/test_controller_progress_accounting.py` because `scripts/controller_progress.py` `EXCLUDE_PATTERNS` had `*/.github/workflows/*` but `.github/workflows/main.yml` `stage_safe_changes` case list lacked it). FIXED: added `*/.github/workflows/*` to the workflow case list (`.github/workflows/main.yml:1163`). Pattern sync tests now green (4/4). Full suite now green in ~117s (1416 passed, 11 skipped). BAB coverage held at 96% (2514 stmts / 106 miss).
- REMOVE BOTTLENECKS RUTHLESSLY BEFORE EXPANDING SCOPE. If any gate is red, fix it first.

## MANDATE: MAINTAIN BAB COVERAGE >= 95% (DISPLAYED 96%). TOUCH >= 4 DIFFERENT FILES WITH REAL LOGIC OR REAL TESTS WHEN WORKING ON STRATEGY MODULES. HEAVY WORK IS MANDATORY. DO NOT AVOID IT. DO NOT DO DOCS-ONLY OR TRIVIAL-ONLY CHANGES. NO SHORTCUTS.

## ATTACK PLAN (MAXIMUM ROI, IN ORDER)
PHASE 0 (BLOCKER REMOVAL): Verify all gates green before any new work. If red, fix immediately. (DONE - gates green.)
PHASE 1 (COVERAGE HARDENING - P0): beta.py (89%, 29 miss: 55-56, 90-91, 103, 113, 123, 125-126, 129-130, 151, 163, 165-170, 249-253, 343-347), data_loader.py (94%, 17 miss: 44, 64-65, 117-119, 183-184, 221-222, 247, 302-304, 331-333), quality.py (95%, 10 miss: 47-48, 132, 187-188, 211-212, 245-246, 259), backtest.py (97%, 2 miss: 58-59). Push total above 96%.
PHASE 2 (REMAINING): portfolio.py (94%, 13 miss), regime.py (94%, 12 miss), data_sources.py (100% now), shorting.py (95%, 9 miss), metrics.py (97%, 4 miss: 71, 97, 187-188), strategy.py (98%, 3 miss: 181, 188-189), signals.py (98%, 2 miss: 37, 75), config.py (98%, 3 miss: 95-96, 113), cli.py (100% now), costs.py (99%, 2 miss: 59-60), sizing.py (100% now).
PHASE 3 (STRESS & EDGE CASES): property-based tests, adversarial inputs, degenerate market regimes, all-NaN benchmarks, zero-observation windows.

## EXECUTE EXACTLY (NO DEVIATION)
1. MEASURE FIRST: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing`
2. FIX BOTTLENECK: any red gate, isolate and fix before anything else.
3. IDENTIFY EXACT MISSED LINES. WRITE DETERMINISTIC TDD TESTS WITH REAL ASSERTIONS (shapes/dtypes/finiteness/invariants). Fix minimally in implementation OR extend tests to hit missed branches - DO BOTH IF NEEDED. Touch REAL code or REAL tests with SUBSTANCE.
4. ROTATE AGGRESSIVELY: After each meaningful gain on P0, immediately move to next P0 until above 96%. MUST touch >= 4 files with substantial real work. DO NOT STOP AT 3 FILES.
5. VERIFY CONSTANTLY: After changes, run BAB tests + full suite. Never leave gates red.
6. REPORT: before/after total BAB coverage + delta per touched module + exact list of files with real work touched + proof gates are green.

## CONSTRAINTS (STRICT)
- BAB-FIRST. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network. NO time-based flakiness.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >= 60 obs default, ranking logic.
- TDD, real assertions, >= 4 files with real work. NO docs-only. NO trivial-only (whitespace/comments only).
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
- HEAVY WORK MANDATED - NEVER AVOID IT. Campaign self-propelling. Build momentum and DO NOT COAST.
- If tempted to do easy work, DO THE HARD UNCOVERED BRANCHES INSTEAD.

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T20:02:04Z)
- Full Suite: GREEN (1416 passed, 11 skipped) after fixing stage_safe_changes pattern sync bottleneck.
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1244 passed, 11 skipped).
- BAB coverage (all BAB tests): 96% (2514 stmts / 106 miss). TARGET >= 95% ACHIEVED, >= 96% DISPLAYED.
- Bottleneck: RESOLVED (controller progress pattern sync + full suite green).
- Handoff: Single durable handoff enforced. ONLY this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 29 | 89% | P0 |
| data_loader.py | 287 | 17 | 94% | P0 |
| quality.py | 183 | 10 | 95% | P0 |
| backtest.py | 74 | 2 | 97% | P1 |
| portfolio.py | 223 | 13 | 94% | P2 |
| regime.py | 186 | 12 | 94% | P2 |
| shorting.py | 172 | 9 | 95% | P4 |
| signals.py | 113 | 2 | 98% | P3 |
| strategy.py | 198 | 3 | 98% | P3 |
| cli.py | 34 | 0 | 100% | P3 |
| config.py | 199 | 3 | 98% | P3 |
| costs.py | 150 | 2 | 99% | P4 |
| metrics.py | 132 | 4 | 97% | P4 |
| sizing.py | 163 | 0 | 100% | P4 |
| data_sources.py | 67 | 0 | 100% | P2 |
| attribution.py | 37 | 0 | 100% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors.py | 2 | 0 | 100% | OK |
| __init__.py | 4 | 0 | 100% | OK |

## EXECUTION DIRECTIVES
- Product-first: BAB never deprioritized.
- Heavy work required: >= 4 files with real logic/tests when working on strategy modules.
- Quality over speed. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md if state materially changes. No commits unless explicitly asked.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded only. No network calls.
- Blocker removal: fix gate/infrastructure blockers first if they appear, verify gates green, resume campaign.
- Coverage target: >= 95% total for BAB strategy modules (maintain; displayed 96%).
- Next agent must not avoid heavy work - campaign is self-propelling and MANDATORY.
- Never coast. Always push uncovered branches. Always touch >= 4 files with substance.
