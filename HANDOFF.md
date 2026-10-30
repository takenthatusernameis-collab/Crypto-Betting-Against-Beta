# HANDOFF - 2026-10-30T20:19:32Z (SINGLE DURABLE HANDOFF) - BETA.PY BOTTLENECK CRUSH

## TIMESTAMP
2026-10-30T20:19:32Z

## INITIAL TASK MESSAGE FOR NEXT AGENT (COPY/PASTE AS FIRST MESSAGE)
```
PRIORITY #1: strategies/betting_against_beta/beta.py | REPO: Crypto-Betting-Against-Beta | BAB-FIRST MANDATE
ATTACK beta.py (89%, 29 MISS) NOW. MEASURE -> ELIMINATE BOTTLENECKS -> HIT UNCOVERED BRANCHES -> PROVE DELTA.
TOUCH >= 4 FILES WITH REAL LOGIC/TESTS. NO DOCS-ONLY. NO TRIVIAL-ONLY.
TARGETS: beta.py >= 95% | TOTAL BAB >= 97%.
FULL SUITE MUST STAY GREEN. BAB SUITE MUST STAY GREEN.
DO HEAVY WORK. DO NOT COAST. CRUSH HARDEST BRANCHES FIRST.
```

## CAMPAIGN OBJECTIVE (NON-NEGOTIABLE)
Push BAB coverage from 96% (2514 stmts / 106 miss) to >=97% by crushing beta.py uncovered branches. Momentum mandatory - self-propelling campaign requiring heavy, substantive work every session.

## CURRENT STATE (VERIFIED)
- Full Suite: GREEN (1416 passed, 11 skipped)
- BAB tests (test_betting_against_beta*.py + test_bab_*.py): GREEN (1244 passed, 11 skipped)
- BAB coverage (all BAB tests): 96% (2514 stmts / 106 miss)
- **PRIMARY BOTTLENECK**: beta.py at 89% (29 misses) - HIGHEST ROI

## NON-NEGOTIABLE GATES (MUST STAY GREEN)
```bash
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest -q
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q
```

## BOTTLENECK ELIMINATION PROTOCOL
- **VERIFY FIRST**: Check gates at session start. Fix red before new work.
- **FOCUS RUTHLESSLY**: BAB > everything else. Only touch infra if it blocks BAB gates.
- **FLAKINESS HUNT**: Eliminate time/network-dependent behavior. Deterministic/offline/seeded only.
- **IMPORTS/DEPS**: Fix immediately.
- **ROTATE ON STALL**: If stuck >2 iterations with no meaningful delta, rotate to next P0 while keeping context.
- **REMOVE BLOCKERS**: No other work until gates green.

## EXACT EXECUTION PLAN
### STEP 1: MEASURE
```bash
PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest tests/test_betting_against_beta*.py tests/test_bab_*.py -q --cov=strategies.betting_against_beta --cov-report=term-missing
```

### STEP 2: ATTACK beta.py (P0-CRITICAL) - 29 MISSES
**File**: `strategies/betting_against_beta/beta.py` (89%, 29 miss: 55-56, 90-91, 103, 113, 123, 125-126, 129-130, 151, 163, 165-170, 249-253, 343-347)

Focus areas:
- **estimate_betas/rolling_beta** (lines ~44-56): Hit both-None fallthrough paths, forcing len() failures, edge cases where both inputs fail conversion
- **calculate_beta** (lines ~90-130): Length mismatch with Series alignment paths, empty aligned df, min_obs after masking, BABDataError re-raise paths
- **calculate_beta_fast** (lines ~151,163,165-170): all_finite mask branches, constant/degenerate benchmark std < 1e-18 → 0.0, non-finite beta → 0.0, LinAlgError paths
- **calculate_rolling_beta** (lines ~249-253,343-347): bad_cols fallback path, benchmark conversion failures in outer try, _finalize_betas masks, vectorized path edge cases
- **_calc_rolling_beta_series** (lines ~103,113,123,125-126,129-130): Degenerate denom cases, insufficient obs, NaN propagation

**Strategy**: Write deterministic TDD tests with real assertions (shapes/dtypes/finiteness/invariants). Add tests or fix implementation to hit branches - do BOTH if needed. Use synthetic/offline data only.

### STEP 3: ROTATE IF NEEDED
If beta.py progress stalls or remaining branches are very hard, move to next P0s: data_loader.py (94%, 17 miss), quality.py (95%, 10 miss). Keep context of stall.

### STEP 4: VERIFY & REPORT
After changes: run BAB tests + full suite. Report before/after coverage per touched module, delta, files touched with real work, missed lines hit, proof gates green.

## MANDATES (STRICT)
- **BAB-FIRST**: Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK**: Touch >= 4 different files with REAL logic or REAL tests with substantive assertions. NO docs-only. NO trivial-only.
- **TDD DISCIPLINE**: Real assertions (shapes/dtypes/finiteness/invariants). Deterministic/offline/seeded.
- **PRESERVE INVARIANTS**: one-day lag, dollar-neutral where applicable, quantile/decile logic, beta window >= 60 obs default, ranking logic. Enforce finiteness. Raise BAB errors on bad inputs. NO bare except:.
- **NEVER COAST**: Push uncovered lines. Do hard branches first.
- **GATES ALWAYS GREEN**: Never leave gates red.
- **NO COMMITS** unless explicitly asked. Only update THIS HANDOFF.md if state materially changes.
- **MOMENTUM**: Campaign must self-propel. Heavy work required.

## COVERAGE SNAPSHOT
| Module | Stmts | Miss | Cover | Priority |
|---|---|---|---|---|
| beta.py | 275 | 29 | 89% | P0-CRITICAL |
| data_loader.py | 287 | 17 | 94% | P0 |
| quality.py | 183 | 10 | 95% | P0 |
| portfolio.py | 223 | 13 | 94% | P2 |
| regime.py | 186 | 12 | 94% | P2 |
| backtest.py | 74 | 2 | 97% | P1 |
| shorting.py | 172 | 9 | 95% | P4 |
| signals.py | 113 | 2 | 98% | P3 |
| strategy.py | 198 | 3 | 98% | P3 |
| config.py | 199 | 3 | 98% | P3 |
| costs.py | 150 | 2 | 99% | P4 |
| metrics.py | 132 | 4 | 97% | P4 |
| cli.py | 34 | 0 | 100% | P3 |
| sizing.py | 163 | 0 | 100% | P4 |
| data_sources.py | 67 | 0 | 100% | P2 |
| attribution.py | 37 | 0 | 100% | OK |
| data.py | 15 | 0 | 100% | OK |
| errors.py | 2 | 0 | 100% | OK |
| __init__.py | 4 | 0 | 100% | OK |

**PROJECT IDENTITY**: Crypto-Betting-Against-Beta | BAB (Frazzini-Pedersen) for crypto - long low-beta, short high-beta vs benchmark (default BTC) | Core: strategies/betting_against_beta/
