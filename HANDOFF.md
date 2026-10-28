# HANDOFF - 2026-10-28T21:13:17Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-28T21:13:17Z

## IMMEDIATE FIRST TASK (DO THIS NOW)
**Priority: P0 - Start heavy work immediately on the BAB strategy**

1. **Verify baseline** (30 seconds):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # Must show 349 passed, 0 failed
```

2. **Execute the clear initial task below (TDD, heavy work, multi-file):**
   - **Item: Multi-format loaders** (Priority 1, Data Infrastructure Hardening)
   - `data_loader.py` already implements `load_returns_from_parquet`, `load_returns_from_hdf5`, `load_returns_from_pickle` plus `load_returns` dispatch — but `tests/test_betting_against_beta_data_loader.py` has **zero** parquet/hdf5/pickle tests.
   - Write failing tests first in `tests/test_betting_against_beta_data_loader.py` covering all three loaders (happy path, missing file, bad schema -> BABDataError, validation passthrough), then implement/extend, then green suite, then refactor.
   - `pyarrow`/`tables`/`fastparquet` are NOT installed: parquet/hdf5 tests must `pytest.mark.skipif` on missing engine (do not hard-fail the suite); pickle is directly testable.
   - Do not stop until this item is fully done across loader + tests + validation.

**RULE: You MUST make substantial progress on the BAB strategy (strategies/betting_against_beta/). No busywork.**

## Project Identity (NON-NEGOTIABLE)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default)
- **Priority:** **BAB STRATEGY CODE > EVERYTHING ELSE**. Fix infra only if it blocks BAB. Otherwise ignore.

## Current Verified State
- **Branch:** main @ `0b5d132`
- **Working tree:** dirty (uncommitted bottleneck fix — `.github/workflows/main.yml:1163`; do NOT commit unless asked)
- **Tests:** **349 passed, 0 failed** (verified)
- **Status:** Bottleneck removed. All tests green.

## Bottlenecks Removed
- **CI/workflow pattern-sync drift (recurring blocker across multiple sessions):** `.github/workflows/main.yml` `stage_safe_changes()` bash case list was missing the nested pattern `*/.github/workflows/*` that Python `EXCLUDE_PATTERNS` (`scripts/controller_progress.py:28`) already had. This caused `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` to fail on every session (347 passed, 2 failed). **Fixed:** added `*/.github/workflows/*` immediately after `.github/workflows/*` at `.github/workflows/main.yml:1163`. Verified: full suite 349 passed, 0 failed.
- Earlier removals (still valid): silent-error eradication across BAB pipeline; config immutability enforced; 2 previously failing controller tests eliminated.

## NEXT FOCUS CAMPAIGN: PRODUCTION-GRADE BAB STRATEGY (HEAVY WORK — MANDATORY)

Agents must work down this campaign in order. No item may be skipped or deferred without a documented blocker in this handoff. Each item requires TDD: failing test → implement → pass → refactor, across multiple files.

### Priority 1: Data Infrastructure Hardening (CRITICAL) - START HERE
- [ ] **Multi-format loaders**: Parquet/HDF5/pickle exist in `data_loader.py` but lack tests in `test_betting_against_beta_data_loader.py`  <-- NEXT CONCRETE TASK (start here now)
- [ ] **Data quality checks**: Expand `quality.py` - gaps, outliers (z-score/IQR), stale data, volume anomalies, duplicate timestamps
- [ ] **Corporate actions**: Handle splits/dividends/airdrops or document assumptions explicitly in code + tests
- [ ] **Time alignment**: Robust tz-aware handling, missing bars, non-trading days, DST
- [ ] **Pluggable data sources**: Abstract base class `DataSource` in new `data_sources.py` for future API connectors
- [ ] **Efficient caching**: Add `DataCache` with TTL/size limits for expensive computations

### Priority 2: Strategy & Risk Management (HIGH)
- [ ] **Advanced risk controls**: Enhance `portfolio.py` - sector/group limits, correlation caps, VaR/CVaR (historical/parametric), leverage limits
- [ ] **Dynamic position sizing**: Kelly, volatility targeting (e.g., target vol scaling), risk parity
- [ ] **Transaction costs**: Realistic models in `costs.py` (market impact sqrt, bid-ask by ADV/liquidity, borrow costs for shorts)
- [ ] **Shorting constraints**: Borrow costs, availability flags, hard caps
- [ ] **Regime detection**: Add `regime.py` - volatility regimes, trend/mean-revert filters
- [ ] **Beta-neutral enforcement**: Strengthen beta targeting with tracking error, drift monitoring

### Priority 3: Performance & Scalability (HIGH)
- [ ] **Vectorize beta**: Optimize `beta.py` rolling OLS/covariance for 1000+ assets
- [ ] **Numba acceleration**: Add optional JIT for hot paths with pure-Python fallback
- [ ] **Memory efficiency**: Chunked processing, dtypes, downcasting
- [ ] **Parallelization**: Safe multiprocessing where applicable with seeds
- [ ] **Benchmarks**: Add `benchmarks/` with timing regression guards

### Priority 4: Analytics & Reporting (HIGH)
- [ ] **Extended metrics**: Add IR, Sortino, Calmar, Omega, Ulcer Index, tail ratios to `metrics.py`
- [ ] **Attribution**: Market/size/momentum attribution if feasible
- [ ] **Tear sheets**: HTML report generator with plots
- [ ] **Rolling analytics**: Rolling Sharpe/drawdowns/exposures
- [ ] **Trade analytics**: Turnover, hold periods, by-regime breakdowns

### Priority 5: Testing & Robustness (CRITICAL)
- [ ] **Property-based tests**: hypothesis for invariants (weights sum to target, beta neutrality bounds)
- [ ] **Stress tests**: Black swans, vol spikes, correlation breakdown
- [ ] **Integration**: End-to-end realistic crypto scenarios
- [ ] **Regression**: Golden files for canonical cases
- [ ] **Fuzz/malformed data**: NaN/inf/dupes/tz issues
- [ ] **Coverage**: Push core modules toward >95%

### Priority 6: Developer Experience (MEDIUM-HIGH)
- [ ] **CLI**: Enhance `cli.py` (run/backtest/optimize/report)
- [ ] **Config**: YAML/JSON config loading/validation
- [ ] **API polish**: Clean public API, `__init__` exports
- [ ] **Examples**: Notebooks/tutorials
- [ ] **Types**: Complete annotations
- [ ] **Docs**: Docstrings + architecture notes

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
