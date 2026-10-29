# HANDOFF - 2026-10-29T00:07:38Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T00:07:38Z

## IMMEDIATE FIRST TASK (DO THIS NOW - NO EXCUSES)

**0) Verify baseline is green (must pass before any changes):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q
# Expected: 400 passed, 0 failed, 6 skipped
```

**1) START HEAVY WORK - Regime Detection (TDD, multi-file, production-grade):**
This is the highest ROI unblocked item. Do NOT do trivial refactors or docs-only changes.

- Create `strategies/betting_against_beta/regime.py` implementing:
  - Volatility regime classification (realized vol thresholds and percentile-based regimes). Support configurable windows/thresholds/percentiles.
  - Trend/mean-revert filters (e.g. moving averages, z-scores) to classify regimes/states.
  - Per-period regime state output (DataFrame aligned to returns index) with clear API.
  - Regime-conditional logic hooks (signals/position sizing/scaling) that can be consumed by strategy/portfolio.
- Extend `BABConfig` with regime-related fields (e.g. `regime_filter`/`regime_model`/regime params) with validation.
- Integrate regime filtering/scaling into `BABStrategy.run()` (and ensure deterministic behavior, no lookahead).
- Write `tests/test_betting_against_beta_regime.py` FIRST with failing tests covering volatility regimes, trend/mean-revert, state alignment, config integration, and strategy integration. Implement until green.
- After regime detection is solid, move to **Beta-neutral enforcement** (strengthen beta targeting with tracking error / drift monitoring).

**RULE:** You MUST make substantial progress on `strategies/betting_against_beta/`. Infra only if it blocks BAB. No busywork.

## PROJECT IDENTITY (NON-NEGOTIABLE)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE > EVERYTHING ELSE**

## CURRENT VERIFIED STATE
- **Branch:** main @ `573fe2f`
- **Working tree:** `.github/workflows/main.yml` modified (pattern-sync fix, uncommitted for review). `__pycache__/` untracked.
- **Tests:** **400 passed, 0 failed, 6 skipped** (green)
- **Bottlenecks:** Pattern-sync between workflow `stage_safe_changes()` and `scripts/controller_progress.py` EXCLUDE_PATTERNS fixed.

## BARRIERS REMOVED
- CI/workflow pattern-sync drift resolved (added `*/.github/workflows/*`).
- Handoff consolidated to single durable `HANDOFF.md` (symlink `HANDOFF_NEXT_SESSION.md -> HANDOFF.md`).

## FOCUS CAMPAIGN (HEAVY WORK - MANDATORY SEQUENCE)

### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders
- [ ] Data quality checks tests for `quality.py` (expand coverage)
- [ ] Corporate actions: document splits/dividends/airdrops assumptions explicitly + tests
- [x] Pluggable data sources exported
- [x] Efficient caching (`DataCache`)

### Priority 2: Strategy & Risk Management (IN PROGRESS - START NOW)
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [ ] **Regime detection** - `regime.py` (vol regimes, trend/mean-revert, regime states, integration) **← START HERE**
- [ ] **Beta-neutral enforcement** - strengthen beta targeting, tracking error, drift monitoring

### Priority 3: Performance & Scalability
- [ ] Vectorize beta calculations, Numba paths, memory efficiency, parallelization, benchmarks

### Priority 4: Analytics & Reporting
- [ ] Extended metrics, attribution, tear sheets, rolling analytics, trade analytics

### Priority 5: Testing & Robustness
- [ ] Property-based tests, stress tests, integration, regression, fuzzing, coverage >95%

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/`
- **HEAVY WORK REQUIRED:** Multi-file features with tests. No trivial-only changes.
- **TDD:** Failing test → understand → minimal implementation → green → refactor
- **ROBUSTNESS:** No bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** No randomness without explicit seeds
- **OFFLINE:** No network calls in tests/core
- **ALWAYS GREEN:** Run full suite often; never regress (target >=400 passed, 0 failed)
- **SINGLE HANDOFF:** Update THIS file (`HANDOFF.md`) after significant progress with new timestamp + concrete next steps
- **NO COMMITS UNLESS ASKED:** Leave uncommitted changes for review

## EXECUTION LOOP (REPEAT)
1. Verify baseline green
2. Pick highest-impact unblocked item from P1-6 (currently P2 regime detection)
3. TDD: write failing tests → implement → pass → refactor
4. Validate full suite, check for regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete task
6. Continue with heavy work - never stop at partial

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
