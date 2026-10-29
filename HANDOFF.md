# HANDOFF - 2026-10-29T18:34:00Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T18:34:00Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED AND VERIFIED:** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes` case (line ~1163) so it matches `scripts/controller_progress.py` EXCLUDE_PATTERNS. `tests/test_controller_progress_accounting.py` → **68 passed**.
- **Baseline restored GREEN:** `python3 -m pytest -q` → **664 passed, 0 failed, 8 skipped** (verified).

## COVERAGE (CURRENT, measured)
**Overall across `strategies/betting_against_beta/`: 63% (2410 stmts, 881 missing)** — improved via added tests.
Focused:
- `strategy.py` 88% (23 missing)
- `beta.py` 83% (41 missing)
- `portfolio.py` 76% (53 missing)
- `config.py` 73% (53 missing)
- `metrics.py` 64% (47 missing)
- `shorting.py` 65% (61 missing)
- `regime.py` 61% (72 missing)
- `backtest.py` 66% (25 missing)
- `data_loader.py` 59% (119 missing)
- `signals.py` 45% (62 missing)
- `costs.py` 55% (68 missing)
- `sizing.py` 33% (109 missing)
- `quality.py` 34% (107 missing)
- `data_sources.py` 44% (36 missing)
- Others higher; **Target >=95% across all `strategies/betting_against_beta/` modules**.

## COMPLETED THIS SESSION
- Fixed workflow pattern sync for nested `*/.github/workflows/*` to restore green baseline.
- Added deep tests for `strategy.py` (kwargs/aliases, data sources, rebalance weekly/monthly/non-datetime, shorting/sizing/regime/beta-neutral paths, finiteness guard, report/tear_sheet/JSON).
- Hardened `beta.py` (robust calculate_beta alignment/truncation, rolling_beta fallbacks, estimate_betas aliases).
- Added tests for `beta`, `data_loader`, and cross-module gaps; touched multiple files with real logic/tests.

## IMMEDIATE HEAVY TASK (NEXT AGENT)
**Campaign: push ALL strategy modules to >=95% coverage.**

Priority order (biggest remaining gaps):
1. `data_loader.py` (59%, 119 missing) — load_paths, CSV/JSON/price->returns, validation, min_rows, benchmark/column handling, error paths
2. `costs.py` (55%, 68 missing), `regime.py` (61%, 72 missing)
3. `portfolio.py` (76% but some complex branches), `config.py` (73%)
4. `sizing.py` (33%, 109 missing), `shorting.py` (65%, 61 missing), `quality.py` (34%, 107 missing)
5. `signals.py` (45%, 62 missing), `data_sources.py` (44%, 36 missing)

**Approach (TDD, heavy):**
- For each file: run coverage-focused tests to see exact lines; write failing tests exercising uncovered branches/edge cases (NaN/inf/zeros/mismatched shapes/dates/non-monotonic, min_obs/window edge cases).
- Add minimal production code only if needed to make behavior correct and robust (no bare except:, enforce finiteness, preserve semantics).
- Touch >=4 files with real logic/tests per session.
- Keep suite green: `python3 -m pytest -q` must stay **664 passed, 0 failed, 8 skipped**.

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be green: 664 passed, 0 failed, 8 skipped
```
**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## CLEAR INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (COPY/PASTE THIS FIRST)
```
PRIORITY: BAB strategy in strategies/betting_against_beta/ > everything else.
GATE: python3 -m pytest -q must be 664 passed, 0 failed, 8 skipped. If not, fix workflow/controller pattern drift (ensure .github/workflows/* and */.github/workflows/* covered) before any other work.
CAMPAIGN: Coverage crusade to >=95% across ALL strategies/betting_against_beta/ modules. Current overall ~63%.
START: TDD on data_loader.py (59%, 119 missing) FIRST - cover CSV/JSON/price ingestion paths, validation, errors, sorting/alignment, finiteness. Then costs.py, regime.py, sizing.py, shorting.py.
REQUIREMENTS: touch >=4 files with real logic/tests per session; no bare except:; deterministic/offline/seeded; enforce finiteness; preserve behavior.
VALIDATE: coverage report for strategies/betting_against_beta/*, full suite green (664/0/8), no regressions. Update THIS HANDOFF.md with timestamp/completed/bottlenecks/next heavy task. ONLY HANDOFF.md MATTERS. HEAVY WORK MANDATORY.
```

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
