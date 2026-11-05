# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T05:19:XXZ
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T05:19:00Z
**DIRECTIVE:** Repository name IS the directive. You are here to harden and extend the Betting Against Beta strategy. There is NO sidetrack mission until BAB gate is satisfied. Build, test, and verify relentlessly. The gate is source of truth. Do not deviate. Focus ALL compute/edits on BAB modules.

## STATE SNAPSHOT (CURRENT)

- **Full BAB-related test suite:** 2220 passed (0 failures) in tests matching `test_bab*`.
- **All tests under `tests/`:** Running full suite takes time; gate script covers everything under `tests/` with coverage.
- **Gate script:** `scripts/bab_gate.sh` runs all tests under `tests/` with coverage of `strategies/betting_against_beta/`.
- **Recent fixes:** data_loader error wrapping to `BABDataError` (parquet/hdf5), added coverage tests.

## BOTTLENECKS REMOVED (THIS SESSION)

- Dependencies present (pytest, coverage, numpy, pandas, scipy, sklearn, pyarrow, openpyxl, tables, hypothesis)
- Gate pattern correct - scans all `tests/test_*.py`
- Clean state, HEAD intact, no history rewrites

## CURRENT FOCUS

**Gate must remain GREEN at all times.** Before doing any work, run recon:
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
bash scripts/bab_gate.sh 2>&1 | tail -15
```
If RED → STOP and fix immediately. Do not checkpoint/commit with RED. Priority is `strategies/betting_against_beta/`. Remove bottlenecks if any emerge.

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

**ACTION:** Run gate now to confirm GREEN. Then pick highest-value uncovered branches in BAB modules (start with data_loader, then strategy/backtest/beta/signals/portfolio, then CLI/metrics/attribution/regime/costs/quality/config) and relentlessly harden with adversarial tests until comprehensive coverage with zero regressions. Do not stop until gate is GREEN and hardening is thorough. Build the next focus campaign as you go - leave no obvious gap unaddressed. Remove any bottlenecks blocking significant progress. Prioritize based on repo name (BAB) - no sidetracks.
