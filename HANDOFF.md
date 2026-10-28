# HANDOFF - 2026-10-28T23-14-58Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-28T23:14:58Z

## IMMEDIATE FIRST TASK (DO THIS NOW)

**0. Confirm baseline green (do first):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # Must show 400 passed, 0 failed, 6 skipped
```
Bottleneck removed earlier; all tests green. **Shorting constraints** module added and wired.

**1. Execute the next concrete task (TDD, heavy work, multi-file):**
   - **Item: Regime detection** (Priority 2, Strategy & Risk Management) — NEXT CONCRETE TASK (start here now)
   - Add `strategies/betting_against_beta/regime.py` with:
     - volatility regime classification (e.g. realized vol thresholds / percentile regimes),
     - trend/mean-revert filters,
     - regime state per period (and possibly regime-conditional signals/position sizing).
   - Integrate into strategy/config (e.g. `BABConfig.regime_filter` / regime model) so regimes can filter or scale exposures.
   - Tests: new `tests/test_betting_against_beta_regime.py`; failing test first → implement → green suite → refactor.
   - **Then continue: `beta-neutral enforcement` (strengthen tracking error / drift monitoring).**

**RULE: You MUST make substantial progress on the BAB strategy (`strategies/betting_against_beta/`). No busywork.**

## Project Identity (NON-NEGOTIABLE)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default)
- **Priority:** **BAB STRATEGY CODE > EVERYTHING ELSE**. Fix infra only if it blocks BAB. Otherwise ignore.

## Current Verified State
- **Branch:** main @ `01cc47d`
- **Working tree:** clean except untracked `__pycache__/` dirs (do NOT commit unless asked)
- **Tests:** **400 passed, 0 failed, 6 skipped** (verified green after adding shorting constraints)
- **Status:** Bottleneck removed. All tests green.

## Bottlenecks Removed
- **CI/workflow pattern-sync drift:** Fixed `.github/workflows/main.yml` `stage_safe_changes()` to include `*/.github/workflows/*` matching `scripts/controller_progress.py:28`. All controller pattern-sync tests pass.
- **Shorting constraints (delivered):** Added `strategies/betting_against_beta/shorting.py` (borrow costs per asset, availability flags, hard caps on short exposure/notional per asset, strict/non-strict modes, signal->weights conversion). Wired into `BABConfig` (normalize dict) and `BABStrategy.run()` to apply constraints after portfolio construction. Exported in `__init__.py`. Added `tests/test_betting_against_beta_shorting.py` (13 tests, all pass).

## Progress So Far (this campaign)
- **Multi-format loaders**: tested (parquet/hdf5 skip without engine, pickle). **DONE.**
- **Data quality checks**: `quality.py` implemented; tests still to add (P1 gap).
- **Pluggable data sources + caching**: `data_sources.py` implemented + exported; add tests.
- **Transaction cost model**: `costs.py` wired into `backtest.py` with 22 tests. **DONE.**
- **Portfolio risk controls**: gross/net/max-single-weight checks raise `BABDataError`. **DONE.**
- **Dynamic position sizing**: Kelly/vol targeting/risk parity wired via config, 9 tests. **DONE.**
- **Shorting constraints**: borrow costs, availability, hard caps + wiring + tests. **DONE.**
- Remaining P1: **Corporate actions** (document splits/dividends/airdrops assumptions + tests). **Data quality tests**. **Data sources tests**.

## NEXT FOCUS CAMPAIGN: PRODUCTION-GRADE BAB STRATEGY (HEAVY WORK — MANDATORY)

### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders (tests)
- [ ] Data quality checks tests for `quality.py`
- [ ] Corporate actions: document assumptions explicitly in code + tests
- [x] Pluggable data sources implemented; add tests + ensure exported (done in __init__)
- [x] Efficient caching (`DataCache`) implemented; add tests

### Priority 2: Strategy & Risk Management (IN PROGRESS)
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [ ] **Regime detection**: `regime.py` - volatility regimes, trend/mean-revert filters (NEXT)
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
