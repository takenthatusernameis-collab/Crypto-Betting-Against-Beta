# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T18:15:42Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T18:15:42Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

**STEP 0 (GATE - BLOCKING):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). If RED, fix gate FIRST.
2. Verify with coverage snapshot before any changes.

**STEP 1 (PRIMARY CAMPAIGN D - RELENTLESS):**
Drive `strategies/betting_against_beta/data_loader.py` from **74%** to **>=90%** with:
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
- **Git:** HEAD at 630d74e, clean on main, up to date with origin/main
- **Gate:** GREEN (2207 passed, 18 skipped). Fixed workflow pattern sync in `.github/workflows/main.yml` - added `*/.github/workflows/*` to stage_safe_changes exclusion list.
- **Coverage:** 85% total; `strategies/betting_against_beta/data_loader.py` **74% (431+ missing)** → TARGET **>=90%**
- **Working tree:** clean (only workflow fix committed in effect; test environment ready)

## BOTTLENECKS ELIMINATED
- **Workflow sync (FIXED):** `tests/test_controller_progress_accounting.py` pattern sync failures resolved. Gate now GREEN.
- **Pattern parity:** Python EXCLUDE_PATTERNS and workflow bash case list in sync.

## CAMPAIGN D ATTACK PLAN (data_loader.py → >=90%)
**Recon:**
```bash
pip install -r requirements.txt
PYTHONPATH=$PWD python3 -m coverage run -m pytest -q tests/test_*data_loader*.py tests/test_bab_data_loader*.py
PYTHONPATH=$PWD python3 -m coverage report -m strategies/betting_against_beta/data_loader.py
```

**Priority targets (by coverage gain):**
1. `_normalize_index` - numeric epoch magnitude branches, empty numeric index, mixed types, coercer fallbacks (lines ~36-310)
2. `_coerce_to_datetime_scalar` - all epoch magnitudes (ns/us/ms/s), tz-aware handling, string parsing, NaT/None/NaN/inf (lines ~310-490)
3. `_promote_datetime_column` / `_detect_and_normalize_exchange_format` - all candidate names, unnamed columns, exchange formats (CoinGecko/Binance/Coinbase) (lines ~490-970)
4. `_normalize_columns`, `_coerce_numeric`, `_strip_units_and_parse`, `_drop_all_nan_columns`, `_series_is_parseable` - units/currency/commas/percent/European decimals/K/M/B/T (lines ~970-1540)
5. Loaders: `load_returns*` all formats (CSV/JSON/JSONL/Parquet/HDF5/Pickle/DataFrame), `load_prices`, `detect_price_or_returns`, `validate_returns_dataframe` all error paths, `load_returns_from_json` all orients (split/index/records/columns), `load_returns_from_pickle` dict/list variants
6. Helpers: `_drop_metadata_columns`, edge cases raising `BABDataError`

**Execution rules:**
1. Recon first - identify exact missing lines
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
