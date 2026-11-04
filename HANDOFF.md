# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T22:25:26Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T22:25:26Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

**STEP 0 (GATE - BLOCKING):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). Confirm coverage snapshot.
2. If RED, fix gate FIRST - no feature work until GREEN.

**STEP 1 (PRIMARY CAMPAIGN D - RELENTLESS, DO NOT STOP):**
Drive `strategies/betting_against_beta/data_loader.py` from **78%** to **>=90%** with:
- Zero API breaks
- Zero test regressions
- Gate GREEN after EVERY batch
- Do not stop until >=90% AND gate GREEN

## MANDATORY GATE (LAW)
1. IMMEDIATELY run: `bash scripts/bab_gate.sh` (full suite via gate, ~2-3 min)
2. MUST exit 0. If RED → stop feature work and fix.
3. NEVER checkpoint with RED.
4. Gate is source of truth.

## CURRENT STATE
- **Git:** HEAD at 218326f, clean on main, up to date with origin/main
- **Gate:** GREEN (2484 passed, 18 skipped, 0 failed). Workflow pattern-sync bottleneck REMOVED - added `*/.github/workflows/*` to `.github/workflows/main.yml` `stage_safe_changes` case list (lines 1163, 1240) to match Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py:28`. All controller_progress tests pass.
- **Coverage (from last gate):** 86% total; `strategies/betting_against_beta/data_loader.py` **78%** (372 missing statements out of 1669) → TARGET **>=90%** (need ~160 more statements covered)
- **Working tree:** clean (workflow fix committed? NO - verify before checkpoint)
- **Test files added this session:** `tests/test_bab_data_loader_campaign_d_push.py`, `tests/test_bab_data_loader_campaign_d_push2.py`, `tests/test_bab_data_loader_campaign_d_push3.py`, `tests/test_bab_data_loader_campaign_d_push4.py` (~1000 adversarial tests)

## BOTTLENECKS ELIMINATED
- **Workflow sync (FIXED):** Pattern parity restored between Python `EXCLUDE_PATTERNS` and workflow bash case list. `*/.github/workflows/*` added to `.github/workflows/main.yml` case list (lines 1163 and 1240). Gate restored from RED (2 controller_progress failures) to GREEN (2484 passed).

## CAMPAIGN D ATTACK PLAN (data_loader.py 78% → >=90%)

**Recon (run FIRST every session):**
```bash
bash scripts/bab_gate.sh 2>&1 | tail -5
PYTHONPATH=$PWD python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_*data_loader*.py 2>&1 | tail -3
PYTHONPATH=$PWD python3 -m coverage report -m --include="strategies/betting_against_beta/data_loader.py"
```

**Missing line blocks by priority (coverage report shows exactly which lines are uncovered):**

**PRIORITY 1 - Largest uncovered blocks (hit these first):**
1. **Lines 120-193** `_normalize_index` numeric epoch magnitude branches (ns/us/ms/s), empty numeric index, mixed types, tz handling, coercer fallbacks, NaT dropping, duplicate handling
2. **Lines 295-390** `_coerce_to_datetime_scalar` string epoch magnitude branches, ISO/dayfirst parsing, NA markers
3. **Lines 411-479** `_coerce_to_datetime_scalar` int/float/Timestamp branches, final fallback, garbage raising
4. **Lines 525-700** `_detect_and_normalize_exchange_format` long-format pivot, OHLCV wide, date-column promotion, empty/early-return
5. **Lines 715-906** `_promote_datetime_column` candidate column parsing, unnamed columns, last-resort object column, tz normalization

**PRIORITY 2 - Medium uncovered blocks:**
6. **Lines 981-1043** `_normalize_columns` column-name variants (adj close, OHLCV, date, asset names), duplicate detection, unnamed drop, exception handler
7. **Lines 1053-1084** `_drop_all_nan_columns` all-NaN raise, mixed keep, object column keep, empty/None
8. **Lines 1095-1150** `_strip_units_and_parse` currency symbols, commas/thousand/Euro decimal, percent, NA markers, malformed-with-digits→NaN, pure-garbage→raise, None/NaN/inf
9. **Lines 1180-1213** `_coerce_numeric` direct astype, object string coercion, non-numeric raise
10. **Lines 1226-1333** `_run_data_quality_campaign` None/empty/non-DF, duplicates, implausible return, gap too large, stale run, min finite fraction, all-pass
11. **Lines 1389-1545** `validate_returns_dataframe` None/non-DF/empty, insufficient rows, missing benchmark, only benchmark, benchmark no finite, short history, inf values, valid pass, case-insensitive rename, quality=False, RangeIndex lacks datetime

**PRIORITY 3 - Loader and helper blocks:**
12. **Lines 1548-1854** All loaders: CSV not-found/empty, parquet/hdf5/pickle/json not-found, pickle flat-scalar-list, pickle unsupported type, unsupported extension, None source, directory path, CSV/JSON/pickle/DataFrame roundtrips with data, dispatch
13. **Lines 1866-1915** `_drop_metadata_columns` Unnamed drop, sequential integer artifact, non-positive min value, all zeros, all-metadata raise
14. **Lines 1981-2069** `detect_price_or_returns` returns/prices detection, empty→prices, unknown extension, CSV/JSON/parquet/hdf5/pickle source detection
15. **Lines 2096-2168** `normalize_schema` None/non-DF/empty, multi-level columns, first-row-as-headers, duplicate-header removal, junk column dropping, valid schema
16. **Lines 2183-2221** `standardize_columns`, `clean_data`, `validate_prices` None/non-DF, valid, no-positive→None

**Execution rules (NON-NEGOTIABLE):**
1. Recon first - identify exact missing lines with coverage report
2. Add comprehensive adversarial tests hitting every uncovered branch. Put tests in `tests/test_bab_data_loader_campaign_d_push*.py` or create `test_bab_data_loader_campaign_d_push5.py` if needed.
3. Only modify implementation if branch is truly untestable via public APIs; preserve all public APIs, raise `BABDataError` on failures
4. `bash scripts/bab_gate.sh` MUST exit 0 after EVERY batch (~2-3 min) - be patient
5. Do NOT move to other campaigns until data_loader.py >=90% AND gate GREEN
6. No shortcuts. Heavy relentless hardening.

## QUEUED AFTER D>=90%
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if gaps remain
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

**ACTION:** Gate confirmed GREEN. Campaign D in progress - data_loader.py at 78%, need >=90%. No exploratory sidetracks. Heavy relentless work required.
