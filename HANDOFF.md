# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-04T03:33:12Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work MUST advance BAB under `strategies/betting_against_beta/`. The repository NAME is a mandate for HEAVY, relentless implementation and hardening. Do NOT deviate to unrelated work.

**MANDATORY GATE (LAW):** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`. Be patient - full suite takes time. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (2135 passed, 17 skipped). Working tree clean. Coverage: 85% total, data_loader.py at 73% (406 missing).

## BOTTLENECKS REMOVED / FIXED THIS SESSION
1. **Gate verified clean.** Confirmed GREEN with full suite passing (2135 passed, 17 skipped). No blocking issues.
2. **Controller progress accounting bottleneck removed.** The workflow's bash `stage_safe_changes` exclusion list (`.github/workflows/main.yml:1163`) was missing the nested variant `*/.github/workflows/*` that Python `EXCLUDE_PATTERNS` (`scripts/controller_progress.py:28`) requires. Added it, restoring lock-step between the two lists. `tests/test_controller_progress_accounting.py` (95 tests) now passes; gate GREEN.
3. **Handoff updated with concrete next steps.** Clear attack plan for largest coverage gap.

## CURRENT FOCUS CAMPAIGN (MAXIMUM IMPACT - DO NOT STOP UNTIL DONE)
### CAMPAIGN D - data_loader.py HARDENING (CRITICAL - HIGHEST ROI)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts). Drive coverage from **73% (406 missing)** to **>=90%** with zero API breaks. Largest untapped gap.

**Attack order (by density/impact):**
1. **`_normalize_index`** - numeric epoch magnitude branches (ms/us/ns/s), floats/strings/ints, mixed scales, empty/numeric/object fallbacks
2. **`_coerce_to_datetime_scalar`** - string epoch detection, large/small magnitudes, NaN/inf/None/NaT, tz-aware/naive, dayfirst, malformed digit strings
3. **`_promote_datetime_column` / `_detect_and_normalize_exchange_format`** - Binance/CoinGecko/long/wide/ohlcv, unnamed columns, object parsing, tz normalization
4. **`_coerce_numeric`, `_strip_units_and_parse`, `_normalize_columns`, `_series_is_parseable`** - units/currency/commas/percent/European decimals, NA markers
5. **Loaders/validation** - `load_returns*` (CSV/JSON/JSONL/Parquet/HDF5/Pickle/DataFrame), `load_prices`, `detect_price_or_returns`, `validate_returns_dataframe`, all error paths raising `BABDataError`

**Execution (NON-NEGOTIABLE):**
1. **Recon:** `PYTHONPATH=$PWD coverage run -m pytest -q tests/test_*data_loader*.py && coverage report -m strategies/betting_against_beta/data_loader.py`
2. **Write adversarial tests** in existing `tests/test_bab_data_loader*.py` or new `tests/test_bab_data_loader_campaign_d_hardcore.py`. Hit EVERY branch with assertions. Test all `BABDataError` paths.
3. **Harden minimally** only if truly untestable via public APIs. Preserve APIs/behavior. Raise `BABDataError` with clear messages.
4. **Gate after EVERY batch:** `bash scripts/bab_gate.sh` MUST exit 0. Be patient.
5. **Converge:** Do NOT move to other campaigns until data_loader.py >= 90% AND gate GREEN.

## QUEUED (AFTER CAMPAIGN D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if gaps emerge
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Heavy hardening required - no shortcuts
- Raise `BABDataError` on bad/parse failures

## PROGRESS SNAPSHOT (2026-11-04T03:33:12Z)
- **Gate:** GREEN (2135 passed, 17 skipped)
- **Coverage:** 85% total; data_loader.py 73% (406 missing) - PRIMARY TARGET
- **State:** Clean working tree. Controller progress accounting workflow sync fixed. Campaign D in progress - focus on data_loader hardening to >=90%.
