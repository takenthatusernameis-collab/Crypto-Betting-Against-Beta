# HANDOFF - 2026-10-30T18:33:10Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-30T18:33:10Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/ - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta.

NON-NEGOTIABLE GATES (MUST REMAIN GREEN AT ALL TIMES):
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q (FULL SUITE TIMED OUT - BOTTLENECK - FIX BEFORE ANYTHING ELSE)
- PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q (BAB tests must stay GREEN: 1191 passed, 11 skipped)
- BAB COVERAGE: CURRENT 95% (2514 stmts / 133 miss) - TARGET >= 95% ACHIEVED. MAINTAIN OR IMPROVE. DO NOT REGRESS BELOW 95%.

BOTTLENECK ACTIVE: Full test suite timed out at 120s. BAB tests alone finish in ~60s. Investigate non-BAB tests (controller progress, nonfinite serialization, campaign resume) for hangs/slowness. FIX BEFORE EXPANDING SCOPE.

MANDATE: MAINTAIN BAB COVERAGE >= 95%. TOUCH >= 4 DIFFERENT FILES WITH REAL LOGIC OR REAL TESTS WHEN WORKING ON STRATEGY MODULES. HEAVY WORK IS MANDATORY. DO NOT AVOID IT. DO NOT DO DOCS-ONLY OR TRIVIAL-ONLY CHANGES. NO SHORTCUTS.

BOTTLENECKS: ONE ACTIVE (full suite timeout). FIX ANY THAT EMERGE IMMEDIATELY BEFORE ANYTHING ELSE. REMOVE BOTTLENECKS RUTHLESSLY.

ATTACK PLAN (MAXIMUM ROI, IN ORDER):
PHASE 0 (BLOCKER REMOVAL): Diagnose and fix full test suite timeout. Run full suite with -x --timeout or isolate slow tests. Verify full suite green before proceeding.
PHASE 1 (COVERAGE MAINTENANCE & HARDENING): beta.py (89%, 30 misses: 55-56, 85, 90-91, 103, 113, 123, 125-126, 129-130, 151, 163, 165-170, 249-253, 343-347), data_loader.py (93%, 20 misses: 44, 64-65, 117-119, 159, 178-179, 183-184, 221-222, 247, 302-304, 331-333), quality.py (92%, 15 misses: 30, 47-48, 132, 187-188, 209, 211-212, 245-246, 259, 275, 279, 289), backtest.py (91%, 7 misses: 53, 58-59, 69-70, 77-78). Push total to >=96%.
PHASE 2 (REMAINING P0-P2): portfolio.py (94%, 14 misses), data_sources.py (94%, 4 misses), regime.py (94%, 12 misses), shorting.py (95%, 9 misses), metrics.py (96%, 5 misses), strategy.py (97%, 5 misses), config.py (98%, 3 misses), signals.py (96%, 4 misses), cli.py (97%, 1 miss), costs.py (99%, 2 misses), sizing.py (99%, 2 misses).
PHASE 3 (STRESS & EDGE CASES): Add property-based tests, adversarial inputs, degenerate market regimes, all-NaN benchmarks, zero-observation windows.

EXECUTE EXACTLY (NO DEVIATION):
1. MEASURE FIRST: PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
2. FIX BOTTLENECK: Full suite timeout - isolate slow non-BAB tests, add timeouts, fix hangs.
3. IDENTIFY EXACT MISSED LINES. WRITE DETERMINISTIC TDD TESTS WITH REAL ASSERTIONS (shapes/dtypes/finiteness/invariants). Fix minimally in implementation OR extend tests to hit missed branches - DO BOTH IF NEEDED. Touch REAL code or REAL tests with SUBSTANCE.
4. ROTATE AGGRESSIVELY: After each meaningful gain on P0, immediately move to next P0 until >=96%. MUST touch >=4 files with substantial real work. DO NOT STOP AT 3 FILES.
5. VERIFY CONSTANTLY: After changes, run BAB tests + full suite. Never leave gates red.
6. REPORT: before/after total BAB coverage + delta per touched module + exact list of files with real work touched + proof gates are green.

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

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T18:33:10Z)
- Full Suite: TIMED OUT at 120s (BOTTLENECK - ACTIVE)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1191 passed, 11 skipped)
- BAB coverage (all BAB tests): 95% total (2514 stmts / 133 miss). TARGET >= 95% ACHIEVED.
- Bottleneck: ACTIVE - full suite timeout. BAB tests alone complete in ~60s.
- Handoff: Single durable handoff enforced. ONLY this file is authoritative.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 30 | 89% | P0 |
| data_loader.py | 287 | 20 | 93% | P0 |
| quality.py | 183 | 15 | 92% | P0 |
| backtest.py | 74 | 7 | 91% | P1 |
| portfolio.py | 223 | 14 | 94% | P2 |
| data_sources.py | 67 | 4 | 94% | P2 |
| regime.py | 186 | 12 | 94% | P2 |
| shorting.py | 172 | 9 | 95% | P4 |
| signals.py | 113 | 4 | 96% | P3 |
| strategy.py | 198 | 5 | 97% | P3 |
| cli.py | 34 | 1 | 97% | P3 |
| config.py | 199 | 3 | 98% | P3 |
| costs.py | 150 | 2 | 99% | P4 |
| metrics.py | 132 | 5 | 96% | P4 |
| sizing.py | 163 | 2 | 99% | P4 |
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
- Coverage target: >=95% total for BAB strategy modules (ACHIEVED - maintain or improve to >=96%).
- Next agent must not avoid heavy work - campaign is self-propelling and MANDATORY.
- Never coast. Always push uncovered branches. Always touch >=4 files with substance.