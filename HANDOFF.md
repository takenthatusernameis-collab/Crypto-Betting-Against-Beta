# HANDOFF - 2026-10-28T20:25:22Z (SINGLE DURABLE HANDOFF)

## TIMESTAMP
2026-10-28T20:25:22Z

## IMMEDIATE FIRST TASK (DO THIS NOW)
**Priority: P0 - Start heavy work immediately on BAB strategy**

1. **Verify baseline** (30 seconds):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pytest -q  # Must show 349 passed, 0 failed
```

2. **Pick ONE high-impact item from Priority 1 below and execute it fully** - write tests first, implement, test, refactor. Don't do trivial fixes.

**RULE: You MUST make substantial progress on the BAB strategy (strategies/betting_against_beta/). No busywork.**

## Project Identity (NON-NEGOTIABLE)
- **Repository:** `Crypto-Betting-Against-Beta`
- **Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default)
- **Priority:** **BAB STRATEGY CODE > EVERYTHING ELSE**. Fix infra only if it blocks BAB. Otherwise ignore.

## Current Verified State
- **Branch:** main @ `e1618b2`
- **Working tree:** clean
- **Tests:** **349 passed, 0 failed** (verified)
- **Status:** Silent-error eradication complete. Workflow pattern sync fixed (`*/.github/workflows/*` added to stage_safe_changes). All tests green.

## Bottlenecks Removed
- CI/workflow pattern sync drift fixed (controller pattern-sync tests pass)
- Silent failures eliminated across BAB pipeline
- Config immutability enforced
- Pattern sync bottleneck fixed: added `*/.github/workflows/*` to `.github/workflows/main.yml` stage_safe_changes bash case; 2 failing controller tests now pass (349/349 green)

## NEXT FOCUS CAMPAIGN: PRODUCTION-GRADE BAB STRATEGY (HEAVY WORK)

### Priority 1: Data Infrastructure Hardening (CRITICAL) - START HERE IF UNSURE
- [ ] **Multi-format loaders**: Extend `data_loader.py` to support Parquet, HDF5, pandas pickle with schema validation
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
- **SINGLE HANDOFF:** Update THIS file (`HANDOFF_NEXT_SESSION.md`) after significant progress with new timestamp + concrete next steps
- **NO COMMITS UNLESS ASKED:** Uncommitted for review

## EXECUTION LOOP
1. Verify baseline (tests green)
2. Pick highest-impact unblocked item from Priority 1-6
3. Design → TDD tests → implement → test → refactor
4. Validate full suite, check coverage/regressions
5. Update this handoff with timestamp, what done, blockers removed, next concrete task
6. Repeat - build momentum with heavy work

**DO NOT STOP UNTIL SIGNIFICANT, SUBSTANTIAL PROGRESS IS MADE ON THE BAB STRATEGY. IGNORE OLDER HANDOFF_*.md FILES.**
