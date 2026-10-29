# HANDOFF - 2026-10-28T23:59:18Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-28T23:59:18Z

## IMMEDIATE FIRST TASK (DO THIS NOW)

**0. Confirm baseline green (do first):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # Must show 400 passed, 0 failed, 6 skipped
```
**Bottleneck removed:** `.github/workflows/main.yml` `stage_safe_changes()` now includes `*/.github/workflows/*`, matching `scripts/controller_progress.py:28`. Pattern-sync tests pass. Suite is green (400 passed, 0 failed, 6 skipped). Uncommitted change to `main.yml` remains for review (do NOT commit unless asked).

**1. Execute the next concrete task (TDD, heavy work, multi-file):**
   - **Item: Regime detection** (Priority 2, Strategy & Risk Management) — NEXT CONCRETE TASK (start here now)
   - Add `strategies/betting_against_beta/regime.py` with:
     - volatility regime classification (realized vol thresholds / percentile regimes),
     - trend/mean-revert filters,
     - regime state per period (and regime-conditional signals/position sizing).
   - Integrate into strategy/config (e.g. `BABConfig.regime_filter` / regime model) so regimes can filter or scale exposures.
   - Tests: new `tests/test_betting_against_beta_regime.py`; failing test first → implement → green suite → refactor.
   - **Then continue: `beta-neutral enforcement` (strengthen tracking error / drift monitoring).**

**RULE: You MUST make substantial progress on the BAB strategy (`strategies/betting_against_beta/`). No busywork.**

## Project Identity (NON-NEGOTIABLE)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default)
- **Priority:** **BAB STRATEGY CODE > EVERYTHING ELSE**. Fix infra only if it blocks BAB. Otherwise ignore.

## Current Verified State
- **Branch:** main @ `41b5311`
- **Working tree:** `main.yml` modified (pattern-sync bottleneck fix, uncommitted for review); `__pycache__/` dirs untracked (do NOT commit unless asked)
- **Tests:** **400 passed, 0 failed, 6 skipped** (verified green)
- **Status:** Bottleneck removed. All tests green. Ready for regime detection.

## Bottlenecks Removed (this session)
- **CI/workflow pattern-sync drift:** Added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes()` case list to match `scripts/controller_progress.py` EXCLUDE_PATTERNS. All 4 controller pattern-sync tests pass. Suite now 400 passed, 0 failed, 6 skipped.
- **Handoff clutter:** Removed ~300 stale `HANDOFF_*.md` files. Single durable handoff is `HANDOFF.md` (pointer `HANDOFF_NEXT_SESSION.md -> HANDOFF.md`).

## NEXT FOCUS CAMPAIGN: PRODUCTION-GRADE BAB STRATEGY (HEAVY WORK — MANDATORY)

### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders (tests)
- [ ] Data quality checks tests for `quality.py`
- [ ] Corporate actions: document splits/dividends/airdrops assumptions explicitly in code + tests
- [x] Pluggable data sources implemented; add tests + ensure exported (done in __init__)
- [x] Efficient caching (`DataCache`) implemented; add tests

### Priority 2: Strategy & Risk Management (IN PROGRESS — START HERE)
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [ ] **Regime detection**: `regime.py` - volatility regimes, trend/mean-revert filters (**NEXT — start now**)
- [ ] Beta-neutral enforcement: strengthen beta targeting with tracking error, drift monitoring

### Priority 3: Performance & Scalability
- [ ] Vectorize beta, Numba acceleration, memory efficiency, parallelization, benchmarks

### Priority 4: Analytics & Reporting
- [ ] Extended metrics, attribution, tear sheets, rolling analytics, trade analytics

### Priority 5: Testing & Robustness
- [ ] Property-based, stress, integration, regression, fuzz, coverage >95%

### Priority 6: Developer Experience
- [ ] CLI, config YAML/JSON, API polish, examples, types, docs

## MANDATORY RULES
- **PRODUCT-FIRST:** `strategies/betting_against_beta/` absolute priority
- **HEAVY WORK:** Substantial features/fixes across multiple files with tests. No trivial tweaks.
- **TDD:** Failing test first → implement → pass → refactor
- **NO SILENT FAILURES:** No bare `except:` or `except Exception:` without specific handling + logging/re-raise
- **CRYPTO-ROBUST:** Handle NaN/inf/zeros/gaps/delistings/extremes/timezones
- **DETERMINISTIC:** No randomness without explicit seeds
- **OFFLINE:** No network in tests/core
- **ALL TESTS GREEN:** Run full suite frequently. Never regress.
- **SINGLE HANDOFF:** Update THIS file (`HANDOFF.md`) after significant progress with new timestamp + concrete next steps
- **NO COMMITS UNLESS ASKED:** Uncommitted for review

## EXECUTION LOOP
1. Verify baseline (tests green)
2. Pick highest-impact unblocked item from Priority 1-6
3. Design → TDD tests → implement → test → refactor
4. Validate full suite, check coverage/regressions
5. Update this handoff with timestamp, what done, blockers removed, next concrete task
6. Repeat - build momentum with heavy work

**DO NOT STOP UNTIL SIGNIFICANT, SUBSTANTIAL PROGRESS IS MADE ON THE BAB STRATEGY. IGNORE OLDER HANDOFF_*.md FILES.**
