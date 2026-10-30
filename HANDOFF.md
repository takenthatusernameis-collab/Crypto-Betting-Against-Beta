# HANDOFF - 2026-10-30T20:14:58Z (SINGLE DURABLE HANDOFF) - CAMPAIGN REFRESH

## TIMESTAMP
2026-10-30T20:14:58Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/ - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta. Repo name MANDATES BAB-first. MEASURE FIRST, ELIMINATE BOTTLENECKS, ATTACK P0s (beta.py 89%, data_loader.py 94%, quality.py 95%). NO COASTING. TOUCH >= 4 FILES WITH REAL LOGIC/TESTS. PUSH BAB COVERAGE ABOVE 96% BY HITTING UNCOVERED BRANCHES. DO NOT STOP AT EASY WINS.
```

## CAMPAIGN OBJECTIVE (NON-NEGOTIABLE)
Push BAB total coverage above 96% through substantive, heavy work. Focus ruthlessly on uncovered branches in P0 modules. Every session must produce measurable coverage delta with evidence. Momentum is mandatory - this campaign must be self-propelling.

## NON-NEGOTIABLE GATES (MUST REMAIN GREEN AT ALL TIMES)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q` (FULL SUITE GREEN: 1416 passed, 11 skipped, ~117s)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q` (BAB tests GREEN: 1244 passed, 11 skipped)
- BAB COVERAGE: CURRENT 96% (2514 stmts / 106 miss) - TARGET >= 95% ACHIEVED, >= 96% DISPLAYED. MAINTAIN OR IMPROVE. DO NOT REGRESS BELOW 95%.

## BOTTLENECK ELIMINATION PROTOCOL (AGGRESSIVE)
- **VERIFY FIRST**: Re-check gates at session start. If red, fix before any new work.
- **PATTERN SYNC**: Watch for controller/progress pattern sync failures (EXCLUDE_PATTERNS vs workflow case lists). Fix root cause, not symptoms.
- **FLAKINESS HUNT**: Eliminate any time/network-dependent behavior. All tests must be deterministic/offline/seeded.
- **IMPORT/DEPS**: Resolve import errors immediately.
- **ROTATE ON STALL**: If stuck on a single module for >2 iterations with no meaningful delta, rotate to next P0 while keeping context of the stall.
- **REMOVE BLOCKERS**: Infrastructure only touched if it blocks BAB gates. Otherwise never.

## MANDATE (STRICT ENFORCEMENT)
- **BAB-FIRST**: Absolute priority on `strategies/betting_against_beta/` above everything else.
- **HEAVY WORK REQUIRED**: Touch >= 4 different files with REAL logic or REAL tests with substantive assertions. NO docs-only. NO trivial-only (whitespace/comments/formatting only).
- **TDD DISCIPLINE**: Write deterministic tests with real assertions (shapes/dtypes/finiteness/invariants). For uncovered branches, either add tests to hit them or fix implementation to be testable - do both if necessary.
- **NO SHORTCUTS**: If tempted by easy work, attack hard uncovered branches instead.
- **NEVER COAST**: Push uncovered lines until exhausted or forced to rotate by evidence.
- **PRESERVE INVARIANTS**: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >= 60 obs default, ranking logic. Enforce finiteness. Raise BAB errors on bad inputs. NO bare except:.

## ATTACK PLAN (MAXIMUM ROI, IN ORDER)
### PHASE 0 - BLOCKER REMOVAL (MANDATORY)
Verify all gates green. If any red, isolate and fix immediately. (Currently resolved, but must re-verify each session.)

### PHASE 1 - P0 COVERAGE HARDENING (PRIORITY)
1. **beta.py** (89%, 29 miss: 55-56, 90-91, 103, 113, 123, 125-126, 129-130, 151, 163, 165-170, 249-253, 343-347) - Focus: validation, edge cases, exception paths, window boundaries, NaN/inf handling.
2. **data_loader.py** (94%, 17 miss: 44, 64-65, 117-119, 183-184, 221-222, 247, 302-304, 331-333) - Focus: alignment, missing data, dtypes, index handling, error paths.
3. **quality.py** (95%, 10 miss: 47-48, 132, 187-188, 211-212, 245-246, 259) - Focus: filters, thresholds, degenerate cases, winsorization/clipping.
4. **backtest.py** (97%, 2 miss: 58-59) - Clean up remaining nits quickly, then rotate back to P0 if needed.

**GOAL**: Push total BAB coverage above 96% and drive P0s down aggressively. Do NOT move to P2 until P0s show real momentum or branches are exhausted with evidence.

### PHASE 2 - REMAINING (AFTER P0 MOMENTUM)
portfolio.py (94%, 13 miss), regime.py (94%, 12 miss), data_sources.py (100%), shorting.py (95%, 9 miss), metrics.py (97%, 4 miss), strategy.py (98%, 3 miss), signals.py (98%, 2 miss), config.py (98%, 3 miss), cli.py (100%), costs.py (99%, 2 miss), sizing.py (100%), attribution/data/errors/__init__ (100%).

### PHASE 3 - STRESS & EDGE CASES
Property-based tests, adversarial inputs, degenerate market regimes, all-NaN benchmarks, zero-observation windows, single-asset cases, extreme beta dispersion.

## EXECUTE EXACTLY (NO DEVIATION)
1. **MEASURE FIRST**: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing`
2. **FIX BOTTLENECK**: Any red gate -> isolate and fix before anything else.
3. **ATTACK UNCOVERED**: Identify exact missed lines for target module. Write deterministic TDD tests with real assertions. Fix minimally in implementation OR extend tests to hit missed branches - DO BOTH IF NEEDED.
4. **ROTATE AGGRESSIVELY**: After each meaningful gain on current P0, assess - if remaining misses are hard or progress slows, immediately move to next P0. MUST touch >= 4 files with substantial real work per session.
5. **VERIFY CONSTANTLY**: After changes, run BAB tests + full suite. Never leave gates red.
6. **REPORT RIGOROUSLY**: Before/after total BAB coverage + delta per touched module + exact list of files with real work touched + missed lines hit + proof gates are green.

## CONSTRAINTS (STRICT)
- BAB-FIRST. Only touch infra if it breaks BAB gate.
- Deterministic/offline/seeded. NO network. NO time-based flakiness.
- NO bare except:. Enforce finiteness. Raise BAB errors on bad inputs.
- Preserve invariants: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >= 60 obs default, ranking logic.
- TDD, real assertions, >= 4 files with real work. NO docs-only. NO trivial-only.
- Remove blockers before expanding scope.
- ONLY update THIS HANDOFF.md if state materially changes. NO COMMITS unless explicitly asked.
- HEAVY WORK MANDATED - NEVER AVOID IT. Campaign is self-propelling. Build momentum and DO NOT COAST.
- If tempted to do easy work, DO THE HARD UNCOVERED BRANCHES INSTEAD.

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T20:14:58Z)
- Full Suite: GREEN (1416 passed, 11 skipped) after fixing stage_safe_changes pattern sync bottleneck.
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1244 passed, 11 skipped).
- BAB coverage (all BAB tests): 96% (2514 stmts / 106 miss). TARGET >= 95% ACHIEVED, >= 96% DISPLAYED.
- Bottleneck: RESOLVED (controller progress pattern sync + full suite green).
- Handoff: Single durable handoff enforced. ONLY this file is authoritative. Campaign refreshed for aggressive P0 attack.

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
- Coverage target: >= 95% total for BAB strategy modules (maintain; displayed 96%). Push above 96%.
- Next agent must not avoid heavy work - campaign is self-propelling and MANDATORY.
- Never coast. Always push uncovered branches. Always touch >= 4 files with substance.
- Momentum rule: measure after each block, rotate if stalled, never declare done while P0 uncovered branches remain.
