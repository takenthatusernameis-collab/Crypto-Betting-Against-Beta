# HANDOFF - 2026-10-28T19:40:00Z (updated 2026-10-28T19:40:00Z)

## Timestamp
2026-10-28T19:40:00Z

## Purpose
**SINGLE DURABLE HANDOFF.** Start here. Ignore all older HANDOFF_*.md files unless you need historical context for a specific bug.

## Project Name Priority (NON-NEGOTIABLE)
**Repository:** `Crypto-Betting-Against-Beta`
**Product:** Betting Against Beta (BAB) crypto strategy — long low-beta, short high-beta vs benchmark (BTC default).
**Hierarchy:** **BAB STRATEGY CODE > EVERYTHING ELSE.** Infrastructure/agent scaffolding exists only to support building the BAB strategy. If infra blocks BAB, fix it first. Otherwise ignore it.

## Current State (Verified)
- **Branch:** main @ `e1618b2`
- **Working tree:** clean (no uncommitted changes)
- **Tests:** **349 passed, 0 failed** (verified 2026-10-28T19:39:xx)
- **Status:** Silent-error eradication campaign COMPLETE. All broad `except Exception:` paths narrowed, tz-aware handling added, config frozen, pattern sync fixed.

## Bottlenecks Identified & Removed
1. **CI/workflow pattern sync drift** - Fixed `.github/workflows/main.yml` to include `*/.github/workflows/*` pattern matching Python `EXCLUDE_PATTERNS`. Controller pattern-sync tests now pass.
2. **Silent failures in BAB pipeline** - All exception handlers narrowed to specific types with loud errors. Config immutability enforced.

## NEXT FOCUS CAMPAIGN: PRODUCTION-GRADE BAB STRATEGY (HEAVY WORK)

**Objective:** Transform the BAB strategy from solid implementation to production-grade, battle-tested trading system. Do heavy, substantive work - add features, harden edge cases, optimize performance, expand test coverage.

### Priority 1: Data Infrastructure Hardening (CRITICAL)
- [ ] **Multi-format loaders**: Extend `data_loader.py` to support Parquet, HDF5, and pandas pickle with validation
- [ ] **Data quality checks**: Add comprehensive data quality report (gaps, outliers, stale data, volume anomalies)
- [ ] **Corporate actions**: Handle splits, dividends, airdrops in price data (or document assumptions)
- [ ] **Time alignment**: Robust handling of different timezones, missing bars, non-trading days
- [ ] **Real data connectors**: Add pluggable data source interface (abstract base) for future API integration
- [ ] **Data caching**: Add efficient caching layer for expensive computations

### Priority 2: Strategy & Risk Management (HIGH)
- [ ] **Advanced risk controls**: Enhance `portfolio.py` with sector/sector-exposure limits, correlation limits, VaR/CVaR checks
- [ ] **Dynamic position sizing**: Kelly criterion, volatility targeting, risk parity alternatives
- [ ] **Transaction cost models**: Add realistic models (market impact, bid-ask spread by liquidity, time-varying costs)
- [ ] **Shorting constraints**: Handle borrow costs, availability constraints, leverage limits
- [ ] **Regime detection**: Add market regime filters (volatility regimes, trending vs mean-reverting)
- [ ] **Hedging**: Add options for beta-neutrality enforcement, factor exposure tracking

### Priority 3: Performance & Scalability (HIGH)
- [ ] **Vectorization**: Optimize `beta.py` rolling calculations for very large universes (1000+ assets)
- [ ] **Numba/JIT**: Consider acceleration for hot paths while keeping pure Python fallback
- [ ] **Memory efficiency**: Chunked processing for large datasets
- [ ] **Parallelization**: Multi-core support where safe (with proper random seeds)
- [ ] **Benchmarking**: Add performance regression tests and profiling hooks

### Priority 4: Analytics & Reporting (HIGH)
- [ ] **Comprehensive metrics**: Extend `metrics.py` with alpha/beta decomposition, Information Ratio, Sortino, Calmar, Omega ratio, win rate, etc.
- [ ] **Attribution analysis**: Factor attribution (market, size, momentum) if possible
- [ ] **Tear sheet generation**: Auto-generate HTML/PDF reports with charts
- [ ] **Rolling performance**: Time-varying Sharpe, rolling drawdowns
- [ ] **Trade analytics**: Turnover analysis, holding periods, win/loss by regime

### Priority 5: Testing & Robustness (CRITICAL)
- [ ] **Property-based tests**: Use hypothesis for edge cases (random inputs)
- [ ] **Stress tests**: Black swan scenarios, extreme volatility, correlation breakdowns
- [ ] **Integration tests**: End-to-end tests with realistic crypto market conditions
- [ ] **Regression suite**: Golden file tests for known scenarios
- [ ] **Fuzzing**: Malformed data, extreme parameters
- [ ] **Coverage**: Aim for >95% coverage on core strategy modules

### Priority 6: Developer Experience (MEDIUM-HIGH)
- [ ] **CLI tool**: Add `bab` CLI (click/argparse) for running backtests from command line
- [ ] **Configuration files**: YAML/JSON config file support
- [ ] **API design**: Clean, documented API for programmatic use
- [ ] **Examples**: Jupyter notebooks with tutorials, real-world examples
- [ ] **Type hints**: Complete type coverage
- [ ] **Documentation**: Comprehensive docstrings, architecture diagrams

## MANDATORY EXECUTION RULES
- **PRODUCT-FIRST:** BAB strategy code in `strategies/betting_against_beta/` has ABSOLUTE priority
- **HEAVY WORK:** Do NOT do trivial changes. Build substantial features/fixes. Multiple files, comprehensive tests.
- **TDD:** Write failing tests first, implement to pass, refactor. All new code must be tested.
- **NO SILENT FAILURES:** Never use bare `except:` or `except Exception:` without specific handling + logging/re-raise
- **CRYPTO-ROBUST:** Handle NaN, inf, zeros, gaps, delistings, extreme values, timezone issues
- **DETERMINISTIC:** No randomness without explicit seeds
- **OFFLINE:** No network calls in tests/core logic
- **ALL TESTS MUST PASS:** Run `python3 -m pytest -q` frequently. Never break existing tests.
- **SINGLE HANDOFF:** Update this `HANDOFF.md` with timestamp after significant progress
- **NO COMMITS UNLESS ASKED:** Leave changes uncommitted for review

## STARTING INSTRUCTIONS
1. **Verify baseline**: `cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta && python3 -m pytest -q` (must be green)
2. **Pick highest-impact item** from Priority 1-6 that enables future heavy work
3. **Design & implement** with tests
4. **Validate** - run full test suite, check for regressions
5. **Update handoff** with progress, next steps, blockers
6. **REPEAT** - keep pushing hard, build momentum

**DO NOT STOP UNTIL YOU HAVE MADE SIGNIFICANT, SUBSTANTIAL PROGRESS ON THE BAB STRATEGY. THIS IS A HEAVY WORK SESSION.**
