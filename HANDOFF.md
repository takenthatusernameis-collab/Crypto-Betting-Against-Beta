# HANDOFF - 2026-10-29T17:47:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T17:47:00Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED FOR REAL:** `.github/workflows/main.yml` `stage_safe_changes` case list now includes `*/.github/workflows/*` (matches `scripts/controller_progress.py` EXCLUDE_PATTERNS). `tests/test_controller_progress_accounting.py` → **68 passed**. Controller accounting failures eliminated.
- **Baseline restored GREEN:** `python3 -m pytest -q` → **664 passed, 0 failed, 8 skipped** (verified after fix).

## COVERAGE BASELINE (CURRENT)
**Overall across `strategies/betting_against_beta/`: 73% (2426 stmts, 650 missing)** (measured with focused runs; need to drive >=95%).

Attack order (priority):
1. `strategy.py` 62% (75 missing) — PRIMARY TARGET
2. `beta.py` 71% (63 missing)
3. `data_loader.py` 77% (66 missing)
4. `config.py` 74% (51 missing)
5. `shorting.py` 65% (61 missing)
6. `sizing.py` 50% (81 missing)
7. `costs.py` 65% (52 missing)
8. `metrics.py` 12% (116 missing)
9. `data_sources.py` 80% (13 missing)
10. `quality.py` 87% (22 missing)
11. `regime.py` 90% (18 missing)
12. `portfolio.py` 94% (14 missing)
13. `backtest.py` 85% (11 missing)
14. `signals.py` 96% (4 missing)
15. `attribution.py` 100%, `data.py` 100%, `errors.py` 100%, `cli.py` 97%, `sizing` heavy gaps

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be green: 664 passed, 0 failed, 8 skipped
```
**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE THIS FIRST)
```
PRIORITY: BAB strategy in strategies/betting_against_beta/ > everything else.
GATE: python3 -m pytest -q must be 664 passed, 0 failed, 8 skipped. If not, fix workflow/controller pattern drift (ensure .github/workflows/* case covers */.github/workflows/*) before any other work.
CAMPAIGN: Coverage crusade to >=95% across strategies/betting_against_beta/ (currently ~73%, 650 missing).
START: TDD attack on strategy.py (62%, 75 missing) and beta.py (71%, 63 missing) FIRST. Write failing tests for uncovered paths/branches (happy+edge+error), add minimal production code if needed to make behavior correct without changing semantics, refactor. Cover rebalance paths, kwargs/aliases, data_source/CSV, risk/sizing/shorting/regime/beta-neutral branches, finiteness guards, report/tear_sheet/json, error cases.
REQUIREMENTS: touch >=4 files with real logic/tests per session; no bare except:; deterministic/offline/seeded; enforce finiteness; preserve behavior.
VALIDATE: coverage report for strategies/betting_against_beta/*, full suite green (664/0/8), no regressions. Update THIS HANDOFF.md with timestamp/completed/bottlenecks/next heavy task. ONLY HANDOFF.md MATTERS. HEAVY WORK MANDATORY.
```

## IMMEDIATE ACTIONS (EXECUTE IN ORDER)
1) **Baseline gate:** `python3 -m pytest -q` → must be 664 passed, 0 failed, 8 skipped.
2) **Measure ruthlessly:** `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` → drive missing down aggressively.
3) **Attack gaps systematically:** TDD on `strategy.py`, `beta.py`, `data_loader.py`, `config.py`, `sizing.py`, `shorting.py` first (largest gaps). Failing test → understand → minimal impl → green → refactor.
4) **Harden brittle paths:** fix uncovered brittle code where found (no bare `except:`, preserve behavior, enforce finiteness/determinism). Look for NaN/inf/zeros/gaps/timezones/delistings.
5) **Touch >=4 files** with real logic/tests per session.
6) **Validate:** `python3 -m pytest -q` >= 664 passed, 0 failed, 8 skipped; coverage >=95%; no regressions.
7) **Update THIS FILE (`HANDOFF.md`)** with timestamp, completed work, bottlenecks removed, next concrete heavy task. ONLY `HANDOFF.md` MATTERS.

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files when changing strategy code. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=664 passed, 0 failed, 8 skipped
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
