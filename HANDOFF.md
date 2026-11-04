# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T19:25:00Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T19:25:00Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

**STEP 0 (GATE - BLOCKING):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). If RED, fix gate FIRST.
2. Verify with coverage snapshot before any changes.

**STEP 1 (PRIMARY CAMPAIGN D - RELENTLESS, DO NOT STOP):**
Drive `strategies/betting_against_beta/data_loader.py` from **~73%** to **>=90%** with:
- Zero API breaks
- Zero test regressions
- Gate GREEN after EVERY batch
- Do not stop until >=90% AND gate GREEN

## MANDATORY GATE (LAW)
1. IMMEDIATELY run: `bash scripts/bab_gate.sh`
2. MUST exit 0. If RED → stop feature work and fix.
3. Full suite via gate (all tests). ~2-3 min.
4. NEVER checkpoint with RED.

## CURRENT STATE
- **Git:** HEAD at 63b872b, clean on main, up to date with origin/main
- **Gate:** GREEN (2207 passed, 18 skipped) after fixing workflow pattern sync (`*/.github/workflows/*` added to exclusion in both `.github/workflows/main.yml` and `scripts/controller_progress.py`)
- **Coverage:** 85% total; `strategies/betting_against_beta/data_loader.py` **~73%** → TARGET **>=90%**
- **Working tree:** clean

## BOTTLENECKS ELIMINATED
- **Workflow sync (FIXED):** Pattern parity restored between Python EXCLUDE_PATTERNS and workflow bash case list. Gate restored to GREEN.
- **Pattern parity:** All workflow exclusion patterns synchronized.

## CAMPAIGN D ATTACK PLAN (data_loader.py → >=90%)
**Recon:**
```bash
pip install -r requirements.txt
PYTHONPATH=$PWD python3 -m coverage run -m pytest -q tests/test_*data_loader*.py tests/test_bab_data_loader*.py
PYTHONPATH=$PWD python3 -m coverage report -m strategies/betting_against_beta/data_loader.py
```

**Priority targets (by coverage gain):**
1. **_normalize_index** (lines ~102-310) - numeric epoch magnitude branches (ns/us/ms/s), empty numeric index, mixed types, tz handling, coercer fallbacks, NaT dropping, duplicate handling
2. **_coerce_to_datetime_scalar** (lines ~310-490) - all epoch magnitudes, tz-aware handling, string parsing with dayfirst, date/datetime objects, NaT/None/NaN/inf, campaign-specific paths
3. **_promote_datetime_column / _detect_and_normalize_exchange_format** (lines ~490-970) - all candidate names, unnamed columns, exchange formats (CoinGecko/Binance/Coinbase), multiple datetime columns
4. **_normalize_columns, _coerce_numeric, _strip_units_and_parse, _drop_all_nan_columns, _series_is_parseable** (lines ~970-1540) - units/currency/commas/percent/European decimals/K/M/B/T, mixed formats
5. **Loaders** (lines ~1540-2245): `load_returns_from_csv`, `load_returns_from_json` all orients (split/index/records/columns/table), `load_returns_from_pickle` dict/list variants including list of dicts, `load_returns_from_hdf5`, `load_prices`, `detect_price_or_returns`, `load_returns` dispatcher for all extensions, `validate_returns_dataframe` all error paths
6. **Helpers**: `_drop_metadata_columns`, `_coerce_series_to_datetime_index`, edge cases raising `BABDataError`

**Execution rules:**
1. Recon first - identify exact missing lines with coverage
2. Add comprehensive adversarial tests hitting every uncovered branch
3. Only modify implementation if branch is truly untestable via public APIs; preserve all public APIs, raise `BABDataError` on failures
4. `bash scripts/bab_gate.sh` MUST exit 0 after EVERY batch (be patient ~2-3 min)
5. Do NOT move to other campaigns until data_loader.py >=90% AND gate GREEN

## QUEUED AFTER D>=90%
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if gaps
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- Gate GREEN before checkpoint/end
- Full suite via gate
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Heavy hardening - no shortcuts
- Raise `BABDataError` on parse/validation failures

**ACTION:** Run gate first to confirm GREEN. Start Campaign D immediately - drive data_loader.py to >=90%. No exploratory sidetracks. Heavy relentless work required.
