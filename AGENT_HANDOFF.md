# Agent Handoff — Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-12T01:28:05Z
**Session ID:** Initial handoff for next agentic work session

---

## Project Overview

**Repository:** `Crypto-Betting-Against-Beta`
**Core Strategy:** Betting Against Beta (BAB) — Frazzini-Pedersen market-neutral crypto strategy
**Approach:** Long low-beta assets, short high-beta assets vs benchmark (default BTC)
**Stack:** Python 3.9+, numpy, pandas, scipy, pytest, hypothesis

---

## Current State Summary

### ✅ Working
- Core BAB pipeline: `BABStrategy.run()` end-to-end (synthetic data by default)
- All modules in `strategies/betting_against_beta/` compile without errors
- Main test suite: `test_betting_against_beta.py` — **86 passed**
- Beta parity regression: **3 passed**
- CLI campaign tests: **15 passed**
- Data loader comprehensive: **16 passed**
- Beta campaign heavy: **10 passed**
- Beta adversarial hardening: **3 passed**

### ❌ Known Failures (2 tests)
**File:** `tests/test_controller_progress_accounting.py`
- `TestStageSafeChangesPatternSync.test_python_patterns_are_subset_of_workflow`
- `TestStageSafeChangesPatternSync.test_nested_workflow_pattern_is_present_in_workflow`

**Root cause:** Python `EXCLUDE_PATTERNS` includes `'*/.github/workflows/*'` but the GitHub Actions workflow's `stage_safe_changes` list does not. This is a configuration sync issue between Python controller code and the CI workflow YAML.

---

## Repository Structure (Key Paths)

```
strategies/betting_against_beta/
├── config.py          # BABConfig dataclass (universe, benchmark, windows, quantiles)
├── data.py            # Synthetic return generator
├── beta.py            # calculate_rolling_beta (OLS, rolling window)
├── signals.py         # generate_bab_signals (rank -> long/short quantiles)
├── portfolio.py       # construct_portfolio (equal-weight, dollar-neutral)
├── backtest.py        # run_backtest (lagged weights, costs, cumulative)
├── strategy.py        # BABStrategy: end-to-end entrypoint (run pipeline)
├── cli.py             # CLI with --data, --benchmark, --universe, --dry-run, --output
├── data_loader.py     # load_returns / load_prices (CSV/JSON/Parquet/HDF5/Pickle)
├── metrics.py         # summary metrics (Sharpe, vol, drawdown, turnover, beta)
├── quality.py         # data quality checks
├── costs.py           # transaction cost models
├── sizing.py          # Kelly, VolTarget, RiskParity, EqualWeight sizers
├── shorting.py        # ShortingConstraints application
├── data_sources.py    # External data source adapters
├── attribution.py     # Trade attribution (gross/cost/slippage/net)
├── regime.py          # Regime detection & position scaling
├── errors.py          # BABDataError
└── __init__.py        # Public exports

tests/
├── test_betting_against_beta.py              # Core strategy tests (86 pass)
├── test_bab_beta_parity_regression.py        # Beta calculation parity (3 pass)
├── test_bab_cli_campaign11ab_cli_surfaces.py # CLI surface tests (15 pass)
├── test_bab_data_loader_comprehensive.py     # Data loader (16 pass)
├── test_bab_beta_campaign_heavy.py           # Beta heavy tests (10 pass)
├── test_beta_adversarial_hardening.py        # Adversarial beta (3 pass)
├── test_controller_progress_accounting.py    # Controller sync (2 FAIL)
└── ... 100+ campaign test files (campaign_d, campaign11, campaign14, etc.)
```

---

## Immediate Next Actions (Priority Order)

### 1. Fix Controller Test Failures (High Priority)
**File:** `tests/test_controller_progress_accounting.py`
**Action:** Sync `EXCLUDE_PATTERNS` in Python controller with `stage_safe_changes` in `.github/workflows/*.yml`
- Add `'*/.github/workflows/*'` to workflow `stage_safe_changes` list
- OR remove it from Python `EXCLUDE_PATTERNS` if intentional
- Verify both tests pass after fix

### 2. Run Full Test Suite & Identify Blockers
**Command:** `python3 -m pytest -q --tb=short 2>&1 | tail -50`
**Goal:** Complete test run to catalog all failures, not just the known 2
- Many campaign test files exist — some may have hidden failures
- Timeout risk: full suite >120s; run in batches if needed

### 3. Validate CLI End-to-End with Real Data Path
**Test:** `python -m strategies.betting_against_beta.cli --data <sample.csv> --from-prices --benchmark BTC --dry-run`
**Goal:** Ensure `--from-prices` path works (load_prices → returns conversion)

### 4. Harden Data Loader Edge Cases
**Files:** `strategies/betting_against_beta/data_loader.py`, `tests/test_bab_data_loader_*.py`
**Focus:** Timezone handling, malformed dates, missing benchmark column, empty DataFrames
- Campaign D tests suggest ongoing data loader hardening

### 5. Add Type Checking / Lint Gate
**Action:** Install `mypy`, add `pyproject.toml` `[tool.mypy]` config, run `mypy strategies/`
- Currently no static analysis in CI
- Strategy code has type hints but some `noqa: ANN401` suppressions

---

## Campaign Test Landscape (Context)

The repo contains **100+ test files** named with campaign patterns:
- `campaign_d_*` — Data loader deep hardening (batch, coverage, push, ultra, heavy)
- `campaign11*` — CLI contract/regression (universe, dry-run, numeric reporting)
- `campaign14*` — CLI reporting extensions
- `campaign9*` — Scripts validation
- `beta_*`, `quality_*`, `backtest_*`, `portfolio_*` — Module-specific campaigns

**Implication:** Heavy test-driven development in progress. Next agent should:
1. Not assume tests are "done" — campaigns indicate active gap-filling
2. Run campaign-specific suites before modifying corresponding modules
3. Treat `test_bab_data_loader_campaign_d_*.py` as the data loader spec

---

## Commands Cheatsheet

```bash
# Install deps
pip install -r requirements.txt

# Core strategy tests (fast, reliable)
python3 -m pytest tests/test_betting_against_beta.py -q

# CLI contract tests
python3 -m pytest tests/test_bab_cli_campaign11ab_cli_surfaces.py -q

# Data loader campaigns
python3 -m pytest tests/test_bab_data_loader_campaign_d*.py -q

# Controller sync (currently 2 failures)
python3 -m pytest tests/test_controller_progress_accounting.py -q

# CLI smoke test (synthetic)
python -m strategies.betting_against_beta.cli --synthetic

# CLI dry-run with data file
python -m strategies.betting_against_beta.cli --data prices.csv --from-prices --benchmark BTC --dry-run
```

---

## Handoff Note for Next Agent

> **Do not skip the controller test fix.** The 2 failures in `test_controller_progress_accounting.py` are a config drift between Python and YAML — trivial to fix but blocks CI green.
> **Run campaign tests before touching modules.** The `campaign_d_*` and `campaign11*` files are living specifications for data loader and CLI respectively.
> **Heavy work expected.** This repo is in active campaign-mode test expansion. Next session should allocate time for full test suite triage, not just the 2 known failures.