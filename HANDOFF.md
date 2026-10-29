# HANDOFF - 2026-10-29T22:19:19Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T22:19:19Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED AND VERIFIED:** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes` case (line ~1163) so it stays in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`. Nested workflow files under subdirs are now excluded both in Python and in the bash list. All `TestStageSafeChangesPatternSync` tests pass.
- **Baseline restored GREEN:** `python3 -m pytest -q` → **804 passed, 0 failed, 8 skipped** (verified). No regressions.

## COVERAGE (CURRENT, measured via coverage)
**Overall across `strategies/betting_against_beta/`: ~88% (target >=95% across all modules).**
Current gaps: `data_sources.py` ~79%, `data_loader.py` ~80%, `shorting.py` ~80%, `costs.py` ~81%, `config.py` ~82%, `beta.py` ~83%, `strategy.py` ~88%, `backtest.py` ~91%, etc.

Target >=95% across all `strategies/betting_against_beta/` modules.

## COMPLETED THIS SESSION
- Removed workflow/controller pattern drift bottleneck: added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes` case (line ~1163) so it stays in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`. Nested workflow files under subdirs excluded both in Python and bash. Baseline restored GREEN: `python3 -m pytest -q` → **804 passed, 0 failed, 8 skipped**. All `TestStageSafeChangesPatternSync` tests pass. No regressions.

## IMMEDIATE HEAVY TASK (NEXT AGENT)
**Campaign: push ALL strategy modules to >=95% coverage.**

Priority order (biggest remaining gaps / highest impact):
1. `data_sources.py` (79%) - finish edge cases (LRU edge paths, HDF5 key precedence, non-DataFrame cache objects), add tests
2. `data_loader.py` (80%) - comprehensive messy/edge cases already partially tested; need remaining branches
3. `shorting.py` (80%) - feasibility/borrowing costs, caps, partial availability, NaN/inf
4. `costs.py` (81%) - slippage/fees edge cases, turnover, caps
5. `config.py` (82%) - validation/coercion paths
6. `beta.py` (83%) - rolling/covariance edge cases, min periods, NaN handling
7. `strategy.py` (88%), `backtest.py` (91%) - remaining branches
8. Bring everything >=95%

**Approach (TDD, heavy):**
- For each file: run targeted coverage to see exact missing lines; write failing tests exercising uncovered branches/edge cases (NaN/inf/zeros/mismatched shapes/dates/non-monotonic, min_obs/window edge cases).
- Add minimal production code only if needed to make behavior correct and robust (no bare except:, enforce finiteness, preserve semantics).
- Touch >=4 files with real logic/tests per session.
- Keep suite green: `python3 -m pytest -q` must stay green.

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be green (804 passed, 0 failed, 8 skipped)
```
**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE THIS FIRST)
```
PRIORITY: BAB strategy in strategies/betting_against_beta/ > everything else.
GATE: python3 -m pytest -q must be green (currently 804 passed, 0 failed, 8 skipped). If not, fix workflow/controller pattern drift (`*/.github/workflows/*` missing from `.github/workflows/main.yml` `stage_safe_changes` case line ~1163) before any other work.
CAMPAIGN: Coverage crusade to >=95% across ALL strategies/betting_against_beta/ modules.
START: TDD on data_sources.py and data_loader.py FIRST (biggest gaps). Cover edge cases, bounds, NaN/inf, shapes. Then shorting.py, costs.py, config.py, beta.py.
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
