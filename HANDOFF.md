# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T04:25:00Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T04:25:00Z
**DIRECTIVE:** Repository name IS the directive. You are here to harden and extend the Betting Against Beta strategy. There is NO sidetrack mission until BAB gate is satisfied. Build, test, and verify relentlessly. The gate is source of truth.

## STATE SNAPSHOT (CURRENT)

- **Full BAB test suite:** 2583 passed (0 failures) - all tests in `tests/test_bab*.py` and `tests/test_betting_against_beta*.py` passing.
- **Gate script:** `scripts/bab_gate.sh` runs all tests under `tests/` with coverage. With all deps installed (`pytest`, `coverage`, `numpy`, `pandas`, `scipy`, `scikit-learn`, `pyarrow`, `openpyxl`, `tables`, `hypothesis`), the gate should exit 0.
- **Fixed in this session:**
  - Made `load_returns_from_parquet`/`load_returns_from_hdf5` properly wrap non-BAB errors from `validate_returns_dataframe` into `BABDataError` (matching expected behavior).
  - Added focused coverage tests for data_loader edge cases.

## BOTTLENECKS REMOVED (THIS SESSION)

- Dependencies installed globally for the environment (including hypothesis for property tests)
- Gate is runnable
- Workflow pattern intact

## CURRENT FOCUS

**Gate must remain GREEN at all times.** Before doing any work, run recon:
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -5
```
If RED → STOP and fix immediately. Do not checkpoint/commit with RED.

## HEAVY WORK CAMPAIGN (CONTINUE HARDENING)

Prioritize based on risk/coverage gaps in BAB strategy modules. Work in this order:

### CAMPAIGN A: Data Loader (MAINTAIN >=90% coverage, prefer higher)
- File: `strategies/betting_against_beta/data_loader.py` (currently well-tested; add adversarial tests for any newly discovered uncovered branches)
- Focus: `_coerce_to_datetime_scalar`, `_normalize_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, loaders (csv/json/jsonl/parquet/hdf5/pickle), `validate_returns_dataframe`, `load_prices`/`load_returns` paths, error wrapping to `BABDataError`

### CAMPAIGN B: Core Strategy/Backtest/Beta
- `strategies/betting_against_beta/strategy.py`, `backtest.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py` - harden edge cases (NaN/inf/NaT, lookahead safety, weights lagged by 1 day, rebalancing, transaction costs)

### CAMPAIGN C: CLI/Reporting/Quality/Metrics
- `strategies/betting_against_beta/cli.py`, `scripts/bab_backtest_report.py`, `quality.py`, `metrics.py`, `attribution.py`, `regime.py`, `shorting.py`, `costs.py`, `config.py`

**RULES (BINDING):**
1. Recon first, fix gate immediately if red
2. Add targeted tests first when coverage gaps exist; only change implementation if branch truly untestable via public APIs. Preserve public APIs. Always raise `BABDataError` on parse/validation failures.
3. Gate after EVERY batch of changes
4. No sidetracks - stay in `strategies/betting_against_beta/` until all critical gaps closed and gate green
5. Zero regressions - all existing tests must pass
6. No history rewriting (no reset/rebase/force-push). HEAD intact.
7. Invariants: weights lagged by 1 day (no lookahead), handle NaN/inf/NaT explicitly, no breaking API changes

**ACTION:** Run gate now to confirm GREEN. Then pick highest-value uncovered branches in BAB modules and relentlessly harden with adversarial tests until comprehensive coverage with zero regressions. Do not stop until gate is GREEN and hardening is thorough.
