# HANDOFF - 2026-10-29T00:13:35Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T00:13:35Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## IMMEDIATE FIRST TASK (DO THIS NOW - NO EXCUSES, NO DISTRACTIONS)

**0) Verify baseline is green (MUST pass before any changes):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q
# Expected: 400 passed, 0 failed, 6 skipped
```

**1) START HEAVY WORK NOW - Regime Detection (TDD, multi-file, production-grade):**
This is the highest ROI unblocked item directly advancing the BAB strategy. Do NOT do trivial refactors, docs-only changes, or infra tweaks unless they are strictly required to implement regime detection.

- Create `strategies/betting_against_beta/regime.py` implementing:
  - **Volatility regimes**: realized volatility calculation over configurable windows; classify into regimes (e.g., low/medium/high) using thresholds or percentiles with hysteresis to avoid whipsaw. Support rolling windows, EWMA volatility.
  - **Trend/mean-revert filters**: moving averages, z-scores, price vs MA, momentum signals to classify market regimes/states.
  - **Per-period regime state**: return a DataFrame aligned to returns index with regime labels/states (and optional probabilities). Handle NaN/insufficient history gracefully.
  - **Regime-conditional hooks**: API to scale signals/positions based on regime (e.g., de-lever in high vol, adjust quantiles). Must be consumable by strategy/portfolio without lookahead.
- Extend `BABConfig` with regime-related fields (e.g., `regime_filter: bool = False`, `regime_method`, `vol_window`, `vol_thresholds`/percentiles, `trend_window`, etc.) with full validation in `_validate_ranges()` and frozen-config safety.
- Integrate regime filtering/scaling into `BABStrategy.run()` - apply regime logic after signals/before or during portfolio construction in a deterministic, no-lookahead manner.
- **Write `tests/test_betting_against_beta_regime.py` FIRST** with failing tests covering: volatility regimes, trend/mean-revert classification, state alignment to index, config integration/validation, strategy integration with regime scaling, NaN/edge cases. Implement until ALL tests green.
- After regime detection is solid and tested, immediately move to **Beta-neutral enforcement** (strengthen beta targeting with tracking error / drift monitoring) as the next heavy task.

**RULE:** You MUST make substantial multi-file progress on `strategies/betting_against_beta/`. If nothing blocks you, do heavy implementation work - not exploration, not busywork.

## CURRENT VERIFIED STATE
- **Branch:** main @ `573fe2f`
- **Working tree:** `.github/workflows/main.yml` modified (pattern-sync fix applied). `__pycache__/` untracked.
- **Tests:** **400 passed, 0 failed, 6 skipped** (green) - bottlenecks removed
- **Bottlenecks:** NONE. Pattern-sync between Python and workflow fixed.

## BARRIERS REMOVED
- CI/workflow pattern-sync drift resolved (added `*/.github/workflows/*` to both Python and workflow).
- Handoff consolidated to single durable `HANDOFF.md` (symlink `HANDOFF_NEXT_SESSION.md -> HANDOFF.md`).

## FOCUS CAMPAIGN (HEAVY WORK - MANDATORY SEQUENCE - CANNOT AVOID)

### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders
- [ ] Expand `quality.py` test coverage (data quality checks)
- [ ] Corporate actions: document splits/dividends/airdrops assumptions explicitly + tests
- [x] Pluggable data sources exported
- [x] Efficient caching (`DataCache`)

### Priority 2: Strategy & Risk Management (IN PROGRESS - START NOW, HEAVY)
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [ ] **Regime detection** - `regime.py` (vol regimes, trend/mean-revert, regime states, integration, hooks) **← START HERE - MANDATORY**
- [ ] **Beta-neutral enforcement** - strengthen beta targeting, tracking error, drift monitoring

### Priority 3: Performance & Scalability
- [ ] Vectorize beta calculations, optimize rolling windows, memory efficiency, parallelization where safe, benchmarks

### Priority 4: Analytics & Reporting
- [ ] Extended metrics (Sharpe/Sortino/Calmar/maxDD, rolling), attribution, tear sheets, rolling analytics, trade analytics

### Priority 5: Testing & Robustness
- [ ] Property-based tests (hypothesis), stress tests, integration, regression, fuzzing, coverage >95%

### Priority 6: Developer Experience
- [ ] CLI polish, YAML/JSON config, API polish, examples, typing, docs

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** Absolute priority on `strategies/betting_against_beta/` - this is a BAB crypto strategy repo
- **HEAVY WORK REQUIRED:** Multi-file features with tests. No trivial-only changes. If task is < 3 files changed with real logic, it's probably not heavy enough - push deeper.
- **TDD:** Failing test → understand → minimal implementation → green → refactor
- **ROBUSTNESS:** No bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** No randomness without explicit seeds
- **OFFLINE:** No network calls in tests/core
- **ALWAYS GREEN:** Run full suite often; never regress (target >=400 passed, 0 failed)
- **SINGLE HANDOFF:** Update THIS file (`HANDOFF.md`) after significant progress with new timestamp + concrete completed work + next concrete heavy task
- **NO COMMITS UNLESS ASKED:** Leave uncommitted changes for review

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green
2. Pick highest-impact unblocked item from P2+ (currently P2 regime detection - MUST DO)
3. TDD: write comprehensive failing tests first → implement production-grade solution across multiple files → make tests pass → refactor
4. Validate full suite, check for regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task
6. Continue with heavy work - never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
