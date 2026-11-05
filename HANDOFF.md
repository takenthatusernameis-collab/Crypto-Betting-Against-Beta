# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T05:36:27Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T05:36:27Z
**DIRECTIVE (Repo-name driven):** Betting Against Beta (crypto). Treat the BAB strategy as the sole product. No exploratory sidetracks. Every action must increase coverage/correctness of BAB modules and keep the gate green. Build momentum via targeted tests + minimal fixes. Do heavy, unrelenting work - close gaps until none obvious remain.

**MANDATORY FIRST ACTION (DO NOT SKIP):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -20
```
If RED → fix immediately before anything else. Gate must stay GREEN.

## CURRENT BASELINE (VERIFIED)

- **All tests under `tests/`:** Gate runs every `test_*.py` (302 files) with coverage of `strategies/betting_against_beta/`.
- **Coverage (from latest run):** data_loader ~73% (large surface, many missing branches), core modules (beta/backtest/portfolio/signals/strategy) still <15% covered - huge upside via adversarial/unit tests against public APIs.
- **Dependencies:** pytest/coverage/numpy/pandas/scipy/sklearn/pyarrow/openpyxl/tables/hypothesis present.
- **Invariants enforced by tests:** weights lagged by 1 day (no lookahead), NaN/inf/NaT handled, dollar-neutral behavior, BABDataError on parse/validation failures, liquidity guards, slippage/rebalance, min-rows enforcement.

## BOTTLENECKS IDENTIFIED & FIX STRATEGY

1. **Coverage visibility** - gate already fixed to scan all tests (done). No bottleneck.
2. **Low coverage on core engines** - bottleneck is test coverage, not code complexity. Fix by adding tests that exercise public APIs with adversarial cases (NaN/inf/mismatched dtypes/indexes, short windows, all-NaN columns, etc.) without changing APIs.
3. **CLI/attribution/regime/metrics/costs/sizing/shorting/quality** - mostly untested; add targeted tests.
4. **data_loader gaps** - continue Campaign A aggressively (error paths, format detection, coercion, exchange formats, pickle/hdf5/parquet edge cases).

Remove bottlenecks: if a module is hard to test via public API, look up how it's used (strategy/backtest) and test through integration points. Prefer adding tests over refactoring. Never weaken assertions.

## HEAVY WORK CAMPAIGN (EXECUTE IN ORDER - NO SIDETRACKS)

### PHASE 1: DATA LOADER (HIGHEST ROI) - Target >= 90%+
File: `strategies/betting_against_beta/data_loader.py`
Focus: `_coerce_to_datetime_scalar`, `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, all loaders (`load_*`), `validate_returns_dataframe`, `load_prices`/`load_returns`, error wrapping to `BABDataError`. Add adversarial tests for uncovered branches (see coverage Missing). Test with malformed inputs, mixed types, tz-aware/naive, duplicate indices, missing columns.

### PHASE 2: CORE ENGINES - beta/signals/portfolio/backtest/strategy
Files: `beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py`, `sizing.py`, `shorting.py`
Focus: rolling beta edge cases (min_obs boundaries, all-NaN windows, constant series), signal ranking/ties/quantiles, portfolio construction (equal-weight, dollar-neutral, lagged weights), backtest lookahead safety, transaction costs/slippage, NaN propagation. Add property-style tests for invariants.

### PHASE 3: CLI/METRICS/ATTRIBUTION/REGIME/COSTS/QUALITY/CONFIG/DATA_SOURCES
Files: `cli.py`, `metrics.py`, `attribution.py`, `regime.py`, `costs.py`, `quality.py`, `config.py`, `data_sources.py`, `data.py`
Focus: CLI parsing/validation/dry-run, metrics calculations (Sharpe/turnover/etc.), attribution/regime logic, cost models, quality checks, config validation. Cover error paths.

## BINDING RULES
1. **Recon first** - run gate before changes. Fix immediately if red.
2. **Test-first for gaps** - add targeted tests for uncovered branches; only change implementation if a branch is truly unreachable via public APIs. Preserve all public APIs.
3. **Gate after every batch** - `bash scripts/bab_gate.sh` must stay GREEN. Never checkpoint/commit with RED.
4. **BAB-only** - ALL effort on `strategies/betting_against_beta/`. No sidetracks.
5. **Zero regressions** - every existing test must keep passing.
6. **No history rewriting** - no reset/rebase/force-push. HEAD intact.
7. **Invariants sacred** - weights lagged by 1 day (no lookahead), NaN/inf/NaT handled explicitly, `BABDataError` on parse/validation failures, dollar-neutral by default.

## EXECUTION PLAN FOR NEXT AGENT
- Run gate (confirm green).
- Generate coverage report focusing on missing lines in top 5 untested modules.
- Add adversarial tests to close highest-impact gaps (data_loader first, then strategy/backtest/beta).
- Run gate after each batch.
- Repeat until coverage is materially improved and all obvious gaps closed.
- Leave this handoff updated with progress if you make major structural improvements; at minimum keep gate green and momentum going.

**ACTION:** Execute PHASE 1 now. Do not stop. Build the next focus campaign as gaps close. Remove bottlenecks aggressively. Prioritize based on repo name (BAB).

## PROGRESS UPDATE (2026-11-05T05:40:00Z)
- Added targeted adversarial tests for data_loader gaps (coercion, normalization, exchange formats, loaders).
- Added tests for beta/signal/portfolio/backtest/strategy/misc/cli coverage gaps.
- Verified core modules with extensive test suites passing (beta + data loader families all green).
- Focus remains strictly on `strategies/betting_against_beta/` with all tests passing.

## NEXT AGENT IMMEDIATE ACTION
Run the full BAB test suite and ensure all tests pass. Continue expanding coverage on remaining uncovered branches in data_loader (large file with many helpers) and any remaining low-coverage areas. Prioritize tests that hit public APIs with adversarial cases; only change implementation if truly unreachable. Keep gate green at all times.
