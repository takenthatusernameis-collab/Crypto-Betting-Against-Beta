# HANDOFF - 2026-10-29T22:22:25Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T22:22:25Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED AND VERIFIED:** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes` case (line ~1160). Nested workflow files under subdirs now excluded both in Python (`scripts/controller_progress.py` has `*/.github/workflows/*`) and in bash workflow. All `TestStageSafeChangesPatternSync` tests pass.
- **Baseline restored GREEN:** `python3 -m pytest -q` → **804 passed, 8 skipped, 0 failed** (verified). No regressions.

## COVERAGE (CURRENT - all BAB tests + existing coverage tests)
**Overall across `strategies/betting_against_beta/`: ~57% with current test set** (many modules partially tested). Target >=95% across ALL modules.

Current gaps (priority order):
1. `costs.py` (17%) - massive gap, core functionality
2. `attribution.py` (17%), `metrics.py` (12%), `quality.py` (7%), `regime.py` (0%), `cli.py` (0%), `sizing.py` (20%) - very low coverage
3. `data_sources.py` (42%), `data_loader.py` (48%), `signals.py` (45%), `strategy.py` (50%), `portfolio.py` (54%), `shorting.py` (61%), `backtest.py` (66%), `config.py` (73%), `beta.py` (83%) - need to push to >=95%

## COMPLETED THIS SESSION
- Fixed workflow/controller pattern drift: added `*/.github/workflows/*` to `.github/workflows/main.yml` stage_safe_changes case. Verified all pattern sync tests pass.
- Restored full suite to green (804 passed, 8 skipped).

## IMMEDIATE HEAVY TASK (NEXT AGENT)
**Campaign: push ALL strategy modules to >=95% coverage. Start from highest-impact/core modules.**

Priority order (biggest gaps / highest impact):
1. `costs.py` (17%) - transaction costs, slippage models, turnover costs - critical for backtesting
2. `shorting.py` (61%) - shorting constraints, feasibility, borrowing costs
3. `data_sources.py` (42%), `data_loader.py` (48%) - data ingestion/normalization edge cases
4. `config.py` (73%) - validation/coercion paths
5. `beta.py` (83%) - rolling/covariance edge cases, min periods, NaN handling
6. `signals.py` (45%), `portfolio.py` (54%), `strategy.py` (50%) - core logic
7. `backtest.py` (66%) - remaining branches
8. Fill all other modules (`attribution`, `metrics`, `quality`, `regime`, `sizing`, `cli`) to >=95%

**Approach (TDD, heavy):**
- For each file: run targeted coverage to see exact missing lines; write failing tests exercising uncovered branches/edge cases (NaN/inf/zeros/mismatched shapes/dates/non-monotonic, min_obs/window edge cases).
- Add minimal production code only if needed to make behavior correct and robust (no bare except:, enforce finiteness, preserve semantics).
- Touch >=4 files with real logic/tests per session.
- Keep suite green: `python3 -m pytest -q` must stay green.

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be green (804 passed, 8 skipped)
```
**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE THIS FIRST)
```
PRIORITY: BAB strategy in strategies/betting_against_beta/ > everything else.
GATE: python3 -m pytest -q must be green (currently 804 passed, 8 skipped). If not, fix workflow/controller pattern drift (`*/.github/workflows/*` missing from `.github/workflows/main.yml` `stage_safe_changes` case) before any other work.
CAMPAIGN: Coverage crusade to >=95% across ALL strategies/betting_against_beta/ modules.
START: TDD on costs.py (17%) FIRST - this is the biggest gap. Then shorting.py, data_sources.py, data_loader.py. Cover edge cases, bounds, NaN/inf, shapes.
REQUIREMENTS: touch >=4 files with real logic/tests per session; no bare except:; deterministic/offline/seeded; enforce finiteness; preserve behavior.
VALIDATE: coverage report for strategies/betting_against_beta/*, full suite green, no regressions. Update THIS HANDOFF.md with timestamp/completed/bottlenecks/next heavy task. ONLY HANDOFF.md MATTERS. HEAVY WORK MANDATORY.
```

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files when changing strategy code. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain full suite green
- **SINGLE HANDOFF:** Update THIS FILE after significant progress. ONLY `HANDOFF.md` MATTERS.
- **NO COMMITS UNLESS ASKED**

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Do PRIMARY HEAVY TASK first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → all tests pass → refactor
4. Validate full suite, check regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue heavy work — never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
