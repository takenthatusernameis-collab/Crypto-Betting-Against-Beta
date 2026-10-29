# HANDOFF - 2026-10-29T15:53:26Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T15:53:26Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## BOTTLENECKS REMOVED (VERIFIED)
- **Workflow/controller pattern sync FIXED FOR REAL:** `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*`. Added it now (parity with `scripts/controller_progress.py` EXCLUDE_PATTERNS). `tests/test_controller_progress_accounting.py` → **68 passed**. **2 controller accounting failures eliminated.**
- **Baseline restored GREEN:** `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped**. Deterministic baseline confirmed.

## COVERAGE BASELINE (MEASURED)
**Overall across `strategies/betting_against_beta/`: 66% (2424 stmts, 818 missing)**
Worst gaps (attack first):
- `metrics.py` 12% (20-27,32-44,54-72,... massive gaps - largely untested)
- `sizing.py` 50%
- `signals.py` 51%
- `portfolio.py` 59%
- `backtest.py` 59%
- `strategy.py` 62%
- `beta.py` 61%
- `costs.py` 65%
- `shorting.py` 65%
- `config.py` 73%
- `data_loader.py` 77%
- `data_sources.py` 80%
- `quality.py` 87%
- `regime.py` 90%
- `cli.py` 97%

## MANDATORY SESSION START (IN ORDER):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # MUST be >=602 passed, 0 failed, 8 skipped before edits
```

**IF GREEN → START HEAVY WORK IMMEDIATELY. NO EXPLORATION, NO DOCS-ONLY CHANGES.**

## FOCUS CAMPAIGN (UNAVOIDABLE)
### Priority 5: Testing & Robustness — IN PROGRESS (HEAVY)
- [x] Beta parity regression (multi-seed, NaN/inf)
- [x] Config-matrix stress (regime/shorting/sizing/costs), determinism + finiteness
- [x] Report CLI edge cases
- [x] Signals/portfolio edge cases, dollar neutrality
- [x] Data loader robustness (malformed/mixed types/bad dates/dupes/timezones/gaps/all-NaN)
- [x] Deterministic property-style fuzzing across signals/portfolio/data_loader/backtest (seeded, offline)
- [ ] **COVERAGE CRUSADE:** Raise coverage across `strategies/betting_against_beta/` to **>=95%**. Currently 66% overall. **metrics.py is at 12% - must be brought up substantially.** Attack signals/strategy/beta/backtest/portfolio/sizing/costs/shorting first, then remaining modules.

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## NEXT HEAVY TASK (FOCUS FOR NEXT SESSION — DO NOT DEFER)
**CRUSH COVERAGE GAPS ACROSS `strategies/betting_against_beta/` WITH SUBSTANTIVE MULTI-FILE HARDENING. Target: >=95% coverage.**

**IMMEDIATE ACTIONS (EXECUTE IN ORDER):**
1) **Measure ruthlessly:** `python3 -m coverage run -m pytest -q && python3 -m coverage report --include="strategies/betting_against_beta/*" -m` (may take time). Identify untested branches/lines.
2) **Attack gaps systematically:** Start with **metrics.py** (12% - almost entirely untested), then **signals.py** (51%), **sizing.py** (50%), **portfolio.py** (59%), **backtest.py** (59%), **beta.py** (61%), **strategy.py** (62%), **costs.py** (65%), **shorting.py** (65%). Write deterministic, offline tests that exercise real code paths (happy paths + edge cases + error paths).
3) **Harden brittle paths:** Fix uncovered brittle code where found (no bare `except:`, preserve behavior, enforce finiteness/determinism). Add guards only if they match existing conventions.
4) **Touch >=4 files** with real logic/tests. Multi-file substantive changes required.
5) **Validate:** `python3 -m pytest -q` >= 602 passed, 0 failed, 8 skipped; push coverage to **>=95%** across `strategies/betting_against_beta/`. No regressions.

**THIS IS NOT OPTIONAL. HEAVY WORK IS MANDATORY.**

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file substantive changes across >=4 files when changing strategy code. If < 4 files touched with real logic, go deeper.
- **TDD:** failing test → understand → minimal impl → green → refactor
- **ROBUSTNESS:** no bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** no randomness without explicit seeds
- **OFFLINE:** no network calls in tests/core
- **ALWAYS GREEN:** maintain >=602 passed, 0 failed, 8 skipped
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

## SESSION UPDATE - 2026-10-29T15:53:26Z (CURRENT)
- **Bottleneck removed (REAL):** `.github/workflows/main.yml` `stage_safe_changes` case list was missing `*/.github/workflows/*` (nested pattern). Added it; `tests/test_controller_progress_accounting.py` → **68 passed**. Both previously failing controller tests now pass.
- **Baseline:** `python3 -m pytest -q` → **602 passed, 0 failed, 8 skipped** (restored to green).
- **Coverage measured:** **66% overall** across `strategies/betting_against_beta/` (2424 stmts, 818 missing). Critical gaps: `metrics.py` 12%, `sizing.py` 50%, `signals.py` 51%, `portfolio.py` 59%, `backtest.py` 59%, `beta.py` 61%, `strategy.py` 62%.
- **Next heavy task (UNAVOIDABLE):** Coverage crusade to **>=95%** across `strategies/betting_against_beta/`; substantive multi-file hardening touching >=4 files; no regressions. **Start with metrics.py (12%)** - add comprehensive deterministic tests. Then attack signals/strategy/beta/backtest/portfolio/sizing/costs/shorting. Validate full suite >=602 passed, 0 failed, 8 skipped.
