# Crypto-Betting-Against-Beta - Next Session Task Handoff

**Repository:** `Crypto-Betting-Against-Beta`
**Date:** 2026-11-14
**Priority:** HIGH - Core strategy implementation complete; test coverage gaps remain

---

## Project Overview

This is a **Betting Against Beta (BAB) strategy for cryptocurrency markets**. The core pipeline:
1. **Load returns** (synthetic by default, or CSV/JSON/Parquet/HDF5/Pickle via `--data`)
2. **Calculate rolling betas** (OLS per window, vectorized, NaN-safe, shared benchmark rolling sums)
3. **Generate signals** (long bottom beta quantile, short top beta quantile, dollar-neutral)
4. **Construct portfolio** (with position sizing, shorting constraints, regime filters, beta-neutral enforcement)
5. **Backtest** (lagged weights, transaction costs, slippage, R3-A partial-fill realism, R4-B drawdown kill switch, R5-A execution adapters)

---

## Current Status

| Component | Status |
|-----------|--------|
| Config (`config.py`) | ✅ Complete with full validation |
| Beta calc (`beta.py`) | ✅ Complete, vectorized, fast |
| Strategy (`strategy.py`) | ✅ Complete pipeline + dry-run |
| Backtest (`backtest.py`) | ✅ Complete with R3/R4/R5 hooks |
| CLI (`cli.py`) | ✅ Complete with adapters, reconciliation |
| Tests | ⚠️ **100+ tests** but **critical gaps** |

---

## Critical Test Gaps Blocking Progress

The test suite has **deep coverage campaigns** (evidenced by test names: `test_bab_beta_deep_final.py`, `test_bab_beta_campaign_heavy.py`, `test_bab_backtest_coverage_campaign2.py`, `test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py`, etc.) but **these key areas remain uncovered**:

### 1. BETA CALCULATION EDGE CASES (HIGHEST PRIORITY)
- **File:** `test_bab_beta_deep_final.py`, `test_bab_beta_campaign_heavy.py`
- **Missing:** Tests for benchmark with NaN values → beta poisoning (entire series NaN), constant benchmark → beta=NaN not 0, min_obs enforcement per-window, negative beta values in quantile ranking, beta calculation with min_obs > window (should clamp)

### 2. BACKTEST EXECUTION REALISM (HIGH PRIORITY)
- **File:** `test_bab_backtest_coverage_campaign2.py`, `test_bab_execution_integration_r5.py`
- **Missing:** Tests for partial_fill enabled with/without ADV data, max_participation boundary (0,1], slippage drag scaling verification, cost_model dict→object coercion, prices_df loading from path, R4-B kill_switch triggered/not-triggered with drawdown limit, execution adapter intent/fill reconciliation

### 3. SIGNAL GENERATION QUANTILES (HIGH PRIORITY)
- **File:** `test_bab_signals_coverage.py`, `test_bab_signals_coverage_campaign3.py`
- **Missing:** Tests for all-beta-NaN returns → all-zero signals, long_quantile + short_quantile > 1 (should error), rebalance_freq monthly/weekly with non-datetime index, quantile boundary assets (exact quantile value), signal generation with beta_neutral enforcement

### 4. PORTFOLIO CONSTRUCTION & RISK CONSTRAINTS (HIGH PRIORITY)
- **File:** `test_bab_portfolio_coverage_campaign.py`, `test_bab_sizing_heavy.py`
- **Missing:** Tests for max_position_size binding, max_turnover enforcement (turnover calc), enforce_risk_checks with gross/net exposure limits, KellySizer/VolatilityTargetSizer/RiskParitySizer with various configs, ShortingConstraints (borrow cost, availability, caps), beta_neutral_correction vs adjustment modes

### 5. CLI REGRESSIONS (MEDIUM-HIGH PRIORITY)
- **File:** `test_bab_cli_campaign11*.py` (multiple files)
- **Missing:** Tests for --output path validation (directory, unwritable, parent creation), --data as directory not file, --from_prices without --data, --fills with wrong adapter, --adapter mock without --fills, dry-run with invalid config/data, synthetic flag vs data priority, JSON output strict-NaN safety

### 6. DATA LOADER REAL-WORLD EDGE CASES (MEDIUM PRIORITY)
- **File:** `test_bab_data_loader_campaign_*.py` (many files)
- **Missing:** Tests for CSV with duplicate timestamps, CSV with missing benchmark column, Parquet/HDF5/Pickle loading, min_rows validation (2 default), benchmark not in universe_override → error, synthetic data generation with custom seed/n_days

---

## Recommended Next Actions (In Order)

```
1. RUN EXISTING TESTS TO ESTABLISH BASELINE
   → pytest tests/ -v --tb=short 2>&1 | head -100
   → Identify FAILED/ERROR tests (not just coverage gaps)

2. ADD TESTS FOR BETA.CALCULATE_ROLLING_BETA EDGE CASES
   → test_bab_beta_deep_final.py: benchmark NaN poisoning
   → test_bab_beta_campaign_heavy.py: constant benchmark, min_obs per-window

3. ADD TESTS FOR BACKTEST PARTIAL_FILL & KILL_SWITCH
   → test_bab_backtest_coverage_campaign2.py: slippage drag scaling
   → test_bab_execution_integration_r5.py: kill_switch triggered/not-triggered

4. ADD TESTS FOR SIGNAL GENERATION QUANTILE BOUNDARIES
   → test_bab_signals_coverage.py: all-NaN betas, quantile > 1, rebalance non-datetime

5. ADD TESTS FOR PORTFOLIO RISK CONSTRAINTS
   → test_bab_sizing_heavy.py: Kelly/VolTarget/RiskParity with synthetic data
   → test_bab_portfolio_coverage_campaign.py: max_position_size, max_turnover binding

6. ADD TESTS FOR CLI VALIDATION PATHS
   → test_bab_cli_campaign11p_*.py: --output, --data, --from_prices, --fills, --adapter

7. VERIFY COVERAGE IMPROVEMENT
   → pytest tests/ --cov=strategies.betting_against_beta --cov-report=term-missing
   → Target: 95%+ line coverage on beta.py, backtest.py, signals.py, portfolio.py, cli.py
```

---

## Key Files to Modify (in order of impact)

| File | Lines | Purpose |
|------|-------|----------|
| `tests/test_bab_beta_deep_final.py` | ~200 | Beta edge cases: NaN benchmark, constant benchmark, min_obs, negative beta |
| `tests/test_bab_backtest_coverage_campaign2.py* | ~300 | Backtest: partial_fill, kill_switch, cost_model, execution adapter |
| `tests/test_bab_signals_coverage*.py` | ~250 | Signal quantile boundaries, rebalance, all-NaN handling |
| `tests/test_bab_sizing_heavy.py` | ~200 | Dynamic sizers, shorting constraints, beta-neutral |
| `tests/test_bab_cli_campaign11p_*.py` | ~300 | CLI validation, output artifacts, adapter integration |

*New test files may need to be created following the naming convention.

---

## Environment & Commands

```bash
# Project root
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta

# Install deps
pip install -r requirements.txt

# Run all tests (baseline)
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=strategies.betting_against_beta --cov-report=html

# Run specific test file
pytest tests/test_bab_beta_deep_final.py -v --tb=long

# Run CLI
python -m strategies.betting_against_beta.cli --synthetic
python -m strategies.betting_against_beta.cli --synthetic --dry-run
python -m strategies.betting_against_beta.cli --data tests/fixture.csv --beta-window 60 --long-quantile 0.25 --short-quantile 0.25 --output result.json

# Run strategy programmatically
python -c "
from strategies.betting_against_beta import BABStrategy, BABConfig
s = BABStrategy(BABConfig(beta_window=90, long_quantile=0.3, short_quantile=0.3))
r = s.run()
print(s.tear_sheet())
print('Sharpe:', s.report()['metrics']['sharpe_ratio'])
"
```

---

## Non-Negotiable Quality Gates

**DO NOT proceed past test additions without:**

1. ✅ All new tests PASS (no flaky tests)
2. ✅ Coverage INCREASES on the targeted module (beta.py, backtest.py, signals.py, portfolio.py, cli.py)
3. ✅ No new `BABConfigError`/`BABDataError` silently caught (verify error messages)
4. ✅ JSON output from CLI `--output` is strict-JSON-safe (no NaN/inf)
5. ✅ Dry-run validates ALL config/data paths before actual run

---

## Context for Future Agents

The project name **Crypto-Betting-Against-Beta** implies the CORE is **beta calculation** and **betting against it** (long low-beta, short high-beta). Every test campaign (`_campaign_`, `_deep_`, `_heavy`, `_coverage_extra`) exists because previous sessions identified gaps but **did not fully close them**. The test files are already created with descriptive names - they just need **implementation**.

**If you're blocked:** The error messages in `config.py`, `beta.py`, `data_loader.py`, `errors.py` are explicit. Match test expectations to the ACTUAL implementation behavior (don't weaken implementation to match broken tests).

**Time estimate:** 2-3 focused sessions to close all gaps and hit 95%+ coverage on core modules.

---

**END OF HANDOFF** - Begin with Step 1: Run existing tests to establish baseline.