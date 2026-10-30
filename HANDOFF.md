# HANDOFF - 2026-10-30T20:17:12Z (SINGLE DURABLE HANDOFF) - BETA PY ATTACK

## TIMESTAMP
2026-10-30T20:17:12Z

## IMMEDIATE ACTION FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py - CRYPTO BETTING AGAINST BETA (FRAZZINI-PEDERSEN). REPO_IDENTITY: Crypto-Betting-Against-Beta. BAB-FIRST MANDATE. MEASURE -> ELIMINATE BOTTLENECKS -> HIT UNCOVERED BRANCHES. ATTACK beta.py (89%, 29 MISS) FIRST. TOUCH >= 4 FILES WITH REAL LOGIC/TESTS. TARGET: beta.py >= 95%, TOTAL BAB >= 97%. NO COASTING. DO HEAVY WORK. NO DOCS-ONLY.
```

## CAMPAIGN OBJECTIVE (NON-NEGOTIABLE)
Drive total BAB coverage above 96% to >=97% by crushing beta.py uncovered branches (29 lines). Every session must produce measurable coverage delta with evidence. Momentum is mandatory - this campaign must be self-propelling. Heavy work required.

## NON-NEGOTIABLE GATES (MUST REMAIN GREEN AT ALL TIMES)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q` (FULL SUITE GREEN: 1416 passed, 11 skipped)
- `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q` (BAB tests GREEN: 1244 passed, 11 skipped)
- BAB COVERAGE: CURRENT 96% (2514 stmts / 106 miss) - MAINTAIN OR IMPROVE. NEVER REGRESS BELOW 95%.

## BOTTLENECK ELIMINATION PROTOCOL (AGGRESSIVE)
- **VERIFY FIRST**: Re-check gates at session start. If red, fix before any new work.
- **PATTERN SYNC**: Watch for controller/progress pattern sync failures. Fix root cause, not symptoms.
- **FLAKINESS HUNT**: Eliminate any time/network-dependent behavior. All tests must be deterministic/offline/seeded.
- **IMPORT/DEPS**: Resolve import errors immediately.
- **ROTATE ON STALL**: If stuck on a single module for >2 iterations with no meaningful delta, rotate to next P0 while keeping context of the stall.
- **REMOVE BLOCKERS**: Infrastructure only touched if it blocks BAB gates. Otherwise never.

## MANDATE (STRICT ENFORCEMENT)
- **BAB-FIRST**: Absolute priority on `strategies/betting_against_beta/` above everything else.
- **HEAVY WORK REQUIRED**: Touch >= 4 different files with REAL logic or REAL tests with substantive assertions. NO docs-only. NO trivial-only (whitespace/comments/formatting only).
- **TDD DISCIPLINE**: Write deterministic tests with real assertions (shapes/dtypes/finiteness/invariants). For uncovered branches, either add tests to hit them or fix implementation to be testable - do both if necessary.
- **NO SHORTCUTS**: Attack hard uncovered branches in P0s first.
- **NEVER COAST**: Push uncovered lines until exhausted or forced to rotate by evidence.
- **PRESERVE INVARIANTS**: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >= 60 obs default, ranking logic. Enforce finiteness. Raise BAB errors on bad inputs. NO bare except:.

## ATTACK PLAN (MAXIMUM ROI, IN ORDER)
### PHASE 0 - BLOCKER REMOVAL (MANDATORY)
Verify all gates green. (Currently green.)

### PHASE 1 - CRUSH BETA.PY (BIGGEST BOTTLENECK - DO THIS FIRST)
**beta.py** (89%, 29 miss: 55-56, 90-91, 103, 113, 123, 125-126, 129-130, 151, 163, 165-170, 249-253, 343-347)
- **estimate_betas/rolling_beta**: Hit lines around min_obs/min_periods, both-None fallthrough to empty array construction (44-56). Force both inputs to fail __len__ conversion paths.
- **calculate_beta**: Hit alignment branches where lengths differ AND inputs become Series/arrays causing alignment, empty aligned df after dropna, min_obs after masking all finite values. Cover the BABDataError re-raise path.
- **calculate_beta_fast**: Cover all_finite mask branch, constant/degenerate benchmark std < 1e-18 returning 0.0, non-finite beta returning 0.0, LinAlgError paths.
- **calculate_rolling_beta**: Hit the bad_cols fallback path, benchmark conversion failures in outer try, and edge cases in vectorized path. Also cover _finalize_betas masks.
- **_calc_rolling_beta_series**: Degenerate denom cases, insufficient obs, NaN propagation.

**Goal**: Get beta.py to >=95% (ideally higher). Do NOT leave until meaningful progress or hard branches blocked - then rotate to data_loader.py.

### PHASE 2 - NEXT P0s AFTER BETA MOMENTUM
1. **data_loader.py** (94%, 17 miss) - alignment, missing data, dtypes, index handling, error paths
2. **quality.py** (95%, 10 miss) - filters, thresholds, degenerate cases
3. **backtest.py** (97%, 2 miss) - quick cleanup if blocking

### PHASE 3 - REMAINING
portfolio.py, regime.py, shorting.py, metrics.py, strategy.py, signals.py, config.py, costs.py etc. Push to >=97% total BAB coverage.

## EXECUTE EXACTLY (NO DEVIATION)
1. **MEASURE FIRST**: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing`
2. **FIX BOTTLENECK**: Any red gate -> isolate and fix before anything else.
3. **ATTACK UNCOVERED**: Identify exact missed lines for beta.py. Write deterministic TDD tests with real assertions. Fix minimally in implementation OR extend tests to hit missed branches - DO BOTH IF NEEDED.
4. **ROTATE AGGRESSIVELY**: After each meaningful gain on beta.py, assess - if remaining misses are hard or progress slows, move to data_loader.py. MUST touch >= 4 files with substantial real work per session.
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
- HEAVY WORK MANDATED - NEVER AVOID IT.
- If tempted to do easy work, DO THE HARD UNCOVERED BRANCHES INSTEAD.

## PROJECT IDENTITY (DRIVES PRIORITIZATION)
- Repository: Crypto-Betting-Against-Beta
- Strategy: Betting Against Beta (BAB) for crypto - long low-beta, short high-beta vs benchmark (default BTC), Frazzini–Pedersen methodology
- Core: strategies/betting_against_beta/
- ABSOLUTE PRIORITY: strategies/betting_against_beta/ above everything else

## CURRENT STATE (MEASURED 2026-10-30T20:17:12Z)
- Full Suite: GREEN (1416 passed, 11 skipped)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1244 passed, 11 skipped)
- BAB coverage (all BAB tests): 96% (2514 stmts / 106 miss). TARGET: push to >=97%.
- **PRIMARY BOTTLENECK**: beta.py at 89% (29 misses) - HIGHEST ROI TARGET
- Bottleneck elimination required: attack beta.py aggressively with heavy work touching >=4 files.

## COVERAGE SNAPSHOT (BAB modules)
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 29 | 89% | P0-CRITICAL |
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
- Heavy work required: >= 4 files with real logic/tests.
- Quality over speed. TDD discipline required.
- Handoff discipline: ONLY update THIS HANDOFF.md if state materially changes. No commits unless explicitly asked.
- No scope creep: only touch infra if breaks BAB gate.
- Deterministic/offline/seeded only. No network calls.
- Blocker removal: fix gate/infrastructure blockers first.
- Coverage target: push from 96% to >=97%. Crush beta.py first.
- Next agent must not avoid heavy work - campaign is self-propelling and MANDATORY.
- Never coast. Always push uncovered branches. Always touch >= 4 files with substance.
- Momentum rule: measure after each block, rotate if stalled, never declare done while P0 uncovered branches remain.
