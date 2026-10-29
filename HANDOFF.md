# HANDOFF - 2026-10-29T01:05:27Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-29T01:05:27Z

## PROJECT IDENTITY (NON-NEGOTIABLE - DRIVES ALL PRIORITIZATION)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default), Frazzini–Pedersen style
- **PRIORITY:** **BAB STRATEGY CODE IN `strategies/betting_against_beta/` > EVERYTHING ELSE**

## IMMEDIATE FIRST TASK (DO THIS NOW - NO EXCUSES, NO DISTRACTIONS)

**SESSION START CHECKLIST (MUST EXECUTE IN ORDER):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
# 1) Baseline MUST be green before any edits
python3 -m pytest -q
# Expected: 411 passed, 0 failed, 6 skipped
```

**IF BASELINE IS GREEN → START HEAVY WORK IMMEDIATELY (MANDATORY):**

### PRIMARY HEAVY TASK: Regime Detection (TDD, multi-file, production-grade)
Create and integrate regime detection for the BAB strategy. Do **NOT** do docs-only, comment-only, rename-only, or trivial refactors. This must touch multiple files with real logic and tests.

#### Required deliverables
1) **`strategies/betting_against_beta/regime.py`** (new)
   - `calculate_realized_vol(returns: pd.Series, window: int, method: str = "std"|"ewma", ...) -> pd.Series` with NaN-safe handling
   - `classify_vol_regime(vol: pd.Series, thresholds: tuple|dict|percentiles: tuple, hysteresis: float = 0.0, ...) -> pd.Series` returning regime labels (e.g., `low|medium|high`) aligned to index, with min-history NaN
   - `classify_trend_regime(prices_or_returns: pd.Series, ma_window: int, z_window: int|None = None, ...) -> pd.Series` (MA cross/z-score/price-vs-MA) with NaN-safe
   - `compute_regime_state(...) -> pd.DataFrame` with columns for regime labels/states aligned to `returns_df.index`, handling insufficient history as flat/NaN-permitted per design
   - `apply_regime_scaling(signals_or_weights: pd.DataFrame, regime: pd.DataFrame, config: ...) -> pd.DataFrame` returning no-lookahead, index-aligned weights/signals (deterministic)

2) **`strategies/betting_against_beta/config.py`** (extend)
   - Add regime fields with sensible defaults and validation: `regime_filter: bool = False`, `regime_method: str = "vol"|"trend"|"combined"`, `vol_window: int`, `vol_use_ewma: bool`, `vol_thresholds: tuple|None`, `vol_percentiles: tuple|None` (e.g., (0.33,0.66)), `vol_hysteresis: float`, `trend_ma_window: int`, `trend_z_window: int|None`, `regime_scale_high: float`, `regime_scale_low: float` (and any needed for combined)
   - Extend `_validate_ranges()` to enforce positive windows, valid ranges, hysteresis in [0,1], scale factors reasonable, and prevent invalid combinations
   - Preserve frozen-config safety

3) **Integration**
   - `strategies/betting_against_beta/strategy.py`: integrate regime logic in `BABStrategy.run()` after generating signals/before or during portfolio construction with **no lookahead**. Must be toggleable via `BABConfig.regime_filter`.
   - `strategies/betting_against_beta/portfolio.py`: support regime scaling cleanly if needed (or keep in strategy) without changing public API contract in a breaking way; ensure dollar-neutral/weight constraints remain intact

4) **Tests (TDD)**
   - Create `tests/test_betting_against_beta_regime.py` **FIRST** with failing tests covering:
     - Volatility regimes: std/EWMA, thresholds and percentiles, hysteresis prevents whipsaw, alignment to index
     - Trend/mean-revert: MA cross, z-score, price-vs-MA, NaN/insufficient history
     - `compute_regime_state` alignment and NaN handling
     - Config integration + validation (bad values rejected)
     - Strategy integration with `regime_filter=True` producing deterministic, index-aligned results; no lookahead (weights shifted appropriately / applied after signal generation as designed)
     - Edge cases: constant series, all-NaN window, single asset, benchmark behavior
   - Implement until **ALL** new regime tests pass and **full suite remains green**.

**ACCEPTANCE CRITERIA (MUST MEET):**
- `python3 -m pytest -q` → >=411 passed, 0 failed (regressions forbidden)
- New regime tests all pass
- Multi-file changes (>=3 files: regime.py, config.py, strategy.py, tests/…) with substantive logic
- No network calls, deterministic (no unseeded randomness), robust NaN/inf/zero handling
- No lookahead in regime application
- Follows existing code style/patterns

**NEXT AFTER REGIME (IMMEDIATE FOLLOW-ON, DO NOT SKIP):**
Once regime detection is solid and fully tested, move to **Beta-neutral enforcement**: strengthen beta targeting (tracking error monitoring, drift detection/correction), add tests, integrate into portfolio/strategy without lookahead. Keep heavy multi-file work going.

## CURRENT VERIFIED STATE
- **Branch:** main @ `573fe2f`
- **Working tree:** `.github/workflows/main.yml` modified (pattern-sync fix applied). `__pycache__/` untracked.
- **Tests:** **411 passed, 0 failed, 6 skipped** (green)
- **Bottlenecks:** NONE (pattern-sync resolved; single durable handoff enforced)

## BARRIERS REMOVED
- CI/workflow pattern-sync drift resolved (added `*/.github/workflows/*` to both Python and workflow)
- Handoffs consolidated to **single durable `HANDOFF.md`** (symlink `HANDOFF_NEXT_SESSION.md -> HANDOFF.md` present). **ONLY THIS FILE MATTERS. IGNORE ALL OLDER HANDOFF_*.md FILES.**

## FOCUS CAMPAIGN (HEAVY WORK - MANDATORY SEQUENCE - CANNOT AVOID)

### Priority 1: Data Infrastructure Hardening
- [x] Multi-format loaders
- [ ] Expand `quality.py` test coverage (data quality checks)
- [ ] Corporate actions: document splits/dividends/airdrops assumptions explicitly + tests
- [x] Pluggable data sources exported
- [x] Efficient caching (`DataCache`)

### Priority 2: Strategy & Risk Management (IN PROGRESS - START NOW)
- [x] Transaction costs
- [x] Portfolio risk controls
- [x] Dynamic position sizing
- [x] Shorting constraints
- [ ] **Regime detection** - `regime.py` (vol regimes, trend/mean-revert, regime states, integration, hooks) **← MANDATORY FIRST**
- [ ] **Beta-neutral enforcement** - strengthen beta targeting, tracking error, drift monitoring **← NEXT IMMEDIATELY AFTER**

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
- **HEAVY WORK REQUIRED:** Multi-file features with tests. If change is < 3 files and no substantive logic, it's not heavy enough - go deeper.
- **TDD:** Failing test → understand → minimal implementation → green → refactor
- **ROBUSTNESS:** No bare `except:`; handle NaN/inf/zeros/gaps/timezones/delistings; validate inputs
- **DETERMINISTIC:** No randomness without explicit seeds
- **OFFLINE:** No network calls in tests/core
- **ALWAYS GREEN:** Run full suite often; never regress (maintain >=411 passed, 0 failed)
- **SINGLE HANDOFF:** Update **THIS FILE** (`HANDOFF.md`) after significant progress with new timestamp + concrete completed work + next concrete heavy task
- **NO COMMITS UNLESS ASKED:** Leave uncommitted changes for review

## EXECUTION LOOP (REPEAT UNTIL EXPLICITLY STOPPED)
1. Verify baseline green (must pass)
2. Do **P2 Regime detection** first (TDD, multi-file). No exploration detours.
3. Implement production-grade solution across multiple files → make all tests pass → refactor
4. Validate full suite, check for regressions
5. Update handoff with timestamp, completed work, blockers removed, next concrete heavy task (beta-neutral enforcement)
6. Continue heavy work - never stop at partial, never do busywork

**IGNORE ALL OLDER HANDOFF_*.md FILES. ONLY `HANDOFF.md` MATTERS.**
