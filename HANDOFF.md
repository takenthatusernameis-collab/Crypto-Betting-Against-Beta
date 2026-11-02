# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-02T04:57:26Z
**Priority from repo name:** Crypto Betting Against Beta (BAB) - market-neutral (long low-beta, short high-beta vs benchmark). ALL WORK MUST ADVANCE BAB.
**Session Mode:** Repo-prioritized, bottleneck-removal enforced. Heavy campaign required.
**Status:** GATE 6 GREEN — 1828 passed, 13 skipped, 0 failures. Campaigns 1-6 complete. Pattern-sync bottleneck fixed. Baseline verified and stable.

## BOTTOM LINE - DO THIS FIRST (NO EXCEPTIONS)

Gate 0 (already green):
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest -q  # 1828 passed, 13 skipped
python3 -c "
from strategies.betting_against_beta import BABStrategy
s = BABStrategy()
r = s.run()
print(float(r.backtest['cumulative'].iloc[-1]))
"  # 0.31664543005633267
```

If red, fix immediately. Never proceed without green baseline.

## IMMEDIATE TASK FOR NEXT SESSION (START HERE - HEAVY WORK REQUIRED)

**CAMPAIGN 7: PRODUCTION HARDENING & REAL-WORLD VALIDATION**

The repo is at a clean checkpoint with full CLI/data-loader/packaging support. Next focus: make BAB robust for production use with real crypto data, add rigorous validation, and extend functionality without breaking existing behavior.

### Priority 1: Real Data Integration & Validation (CRITICAL)
1. **Real data pipeline hardening** - Test with actual crypto market data patterns. Validate data_loader handles exchange-specific formats (CoinGecko, Binance, Coinbase CSVs). Add support for common formats if gaps exist.
2. **Data quality validation** - Add comprehensive checks for survivorship bias, missing data handling, outlier detection. Ensure defensive behavior on messy real data.
3. **Time series integrity** - Validate no lookahead, proper alignment, timezone handling across datasets.

### Priority 2: Performance & Scalability (HIGH)
4. **Optimize rolling calculations** - Profile `calculate_rolling_beta` on large datasets. Vectorize where possible while maintaining correctness.
5. **Memory efficiency** - Test with multi-year data (1000+ assets, 2000+ days). Ensure reasonable memory usage.
6. **Benchmarking expansion** - Extend `scripts/perf_bench.py` with larger dataset scenarios.

### Priority 3: Strategy Enhancements (HIGH)
7. **Transaction cost modeling** - Make costs more realistic (market impact, slippage models). Current implementation exists but needs real-world calibration.
8. **Risk management** - Add position limits, leverage controls, drawdown monitoring. Integrate with sizing/shorting modules.
9. **Attribution & reporting** - Expand attribution analysis, add risk metrics (Sharpe, Sortino, max drawdown, turnover). Leverage existing `metrics.py`, `attribution.py`.

### Priority 4: Testing & Robustness (HIGH)
10. **Property-based testing** - Add hypothesis tests for edge cases (dollar neutrality, weight constraints, no lookahead).
11. **Stress testing** - More extreme scenarios (correlation breakdowns, regime changes).
12. **Integration tests** - End-to-end with real-style data, CLI edge cases.

## EXECUTION STRATEGY
- **Run Gate 0 first** - Confirm baseline is green before making changes.
- **Work iteratively** - Make small, tested changes. Run tests after each modification.
- **Maintain green** - Never let tests go red. Add tests for new functionality.
- **BAB-first mindset** - Every change must advance the Betting Against Beta strategy.
- **Heavy work required** - Trivial changes won't cut it. Tackle the priorities above systematically.
- **Preserve contracts** - Keep synthetic defaults, public APIs stable unless absolutely necessary with full test coverage.

## CURRENT STATE
- **Tests:** 1828 passed, 13 skipped, 0 failures
- **CLI:** `bab-example` works, `--dry-run`, `--version`, `--from-prices` all functional
- **Packaging:** pyproject.toml with console entry point, package discovery configured
- **Data loading:** Robust loader with stress-tested edge cases
- **Real data E2E:** Tested with fixtures
- **Performance:** Benchmarked (beta calc ~1.55ms, full run ~10.71ms)
- **Bottlenecks:** All removed

## FILES OF INTEREST
- `strategies/betting_against_beta/` - Core BAB implementation
- `strategies/betting_against_beta/data_loader.py` - Data loading (needs hardening)
- `strategies/betting_against_beta/cli.py` - CLI interface
- `scripts/load_real_bab_example.py` - Example loader
- `tests/test_bab_*` - BAB-specific tests
- `pyproject.toml` - Packaging config

## NON-NEGOTIABLE RULES
- **BASELINE FIRST:** Gate 0 mandatory. Never skip.
- **MAINTAIN GREEN:** 1828 passed, 13 skipped must remain; only add tests, never weaken.
- **BAB FIRST:** Crypto Betting Against Beta above everything else.
- **NO UNNECESSARY WORKFLOW CHANGES:** Only touch `.github/workflows/*` if absolutely required AND pattern-sync tests still pass.
- **PRESERVE CONTRACTS:** Keep synthetic defaults. Preserve public APIs.
- **EVIDENCE MANDATORY:** For each significant change, record what changed and test results.
- **NO LOOKAHEAD:** Weights must be lagged by 1 day.
- **DEFENSIVE BY DEFAULT:** Validate, coerce safely, fail clearly.
- **HEAVY WORK REQUIRED:** Trivial one-liners insufficient.

**START NOW:** Run Gate 0. This is a clean, production-ready checkpoint. Campaign 7 awaits - focus on real-world robustness and production hardening.
