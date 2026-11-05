# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

**Timestamp:** 2026-11-05T04:11:00Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**PRIORITY (NON-NEGOTIABLE):** `strategies/betting_against_beta/` - ALL effort MUST go here

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE THIS FIRST)

**Time:** 2026-11-05T04:11:00Z
**DIRECTIVE:** The repository name IS the directive. You are here to harden and extend the Betting Against Beta strategy. There is NO sidetrack mission until the below is satisfied. Build, test, and verify relentlessly.

## BOTTLENECKS REMOVED (THIS SESSION)

- **Dependencies installed:** `pytest`, `coverage`, `numpy`, `pandas`, `scipy`, `scikit-learn`, `pyarrow`, `openpyxl`, `tables` (installed to user site-packages; add to `PATH` if needed)
- **Gate runnable:** `scripts/bab_gate.sh` is now executable in this environment with deps present
- **Workflow pattern:** `.github/workflows/main.yml` already includes `*/.github/workflows/*` in `stage_safe_changes` (required by `scripts/controller_progress.py`)

## CURRENT GATE STATUS (BLOCKING)

- `bash scripts/bab_gate.sh` MUST exit 0 at ALL times.
- **Gate = source of truth.** If RED: STOP everything and fix the gate. Do NOT checkpoint, commit, or move on with RED.
- Run from repo root. The gate is self-contained and scans all `tests/test_*.py`.

## FOCUS CAMPAIGN D - RELENTLESS DATA_LOADER COVERAGE HARDENING (DO NOT STOP)

**TARGET:** `strategies/betting_against_beta/data_loader.py`
**REQUIRED:** >= 90% coverage (missing lines <= ~167 based on historical size)
**STATUS:** IN PROGRESS - THIS IS THE ONLY MISSION UNTIL COMPLETE AND GATE IS GREEN

### RECON (MANDATORY AT START OF EVERY SESSION)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD

# Gate first
bash scripts/bab_gate.sh 2>&1 | tail -2

# Focused coverage on data_loader tests
PYTHONPATH=$PWD python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_bab_data_loader*.py tests/test_betting_against_beta_data_loader*.py 2>&1 | tail -3
PYTHONPATH=$PWD python3 -m coverage report -m --include="strategies/betting_against_beta/data_loader.py"
```

### ATTACK PLAN (HIT EVERY UNCOVERED BRANCH)

Systematically cover in order of effort/branch density:

1. **Early helpers** - `_not_null`, `_series_has_any_finite`, `_coerce_series_to_datetime_index`
2. **Index normalization** - `_normalize_index` numeric epoch branches (different magnitudes, fallbacks, exception paths)
3. **Scalar coercion** - `_coerce_to_datetime_scalar` (epoch magnitudes, strings, NA/NaT/inf, tz-aware/naive)
4. **Exchange format detection** - `_detect_and_normalize_exchange_format` (long-format pivot edges, OHLCV wide, date promotion, symbol columns)
5. **Datetime promotion** - `_promote_datetime_column` (unnamed/object, tz normalization, fallbacks)
6. **Column ops** - `_normalize_columns`, `_drop_all_nan_columns`
7. **Parsing/coercion** - `_strip_units_and_parse`, `_coerce_numeric`, `_series_is_parseable`
8. **Quality/validation** - `_run_data_quality_campaign`, `validate_returns_dataframe`, `validate_prices`
9. **Loaders** - CSV/JSON/JSONL/Parquet/HDF5/Pickle + all error/edge paths (bad encodings, empty, mixed dtypes)
10. **Schema/cleaning** - `drop_metadata_columns`, `detect_format`, `normalize_schema`, `standardize_data`, `clean_data`, remaining helpers

### EXECUTION RULES (BINDING)

1. **Recon first** - Get exact missing lines before writing anything.
2. **Adversarial testing** - Extend `tests/test_bab_data_loader_campaign_d*.py` (or add tightly scoped tests) to hit EVERY uncovered branch. Prefer edge cases (NaN/inf/NaT, mixed types, bad epochs, tz-aware/naive, malformed inputs).
3. **Impl only if untestable** - Only change implementation if a branch cannot be reached via public APIs. Preserve ALL public APIs. Always raise `BABDataError` on parse/validation failures.
4. **Gate after EVERY batch** - After adding tests AND after any impl change, run `bash scripts/bab_gate.sh`. MUST be GREEN.
5. **No sidetracks** - Do NOT touch other campaigns until `data_loader.py` >= 90% AND gate is GREEN.
6. **Zero regressions** - Every existing test must still pass.
7. **No history rewriting** - Do NOT reset/rebase/force-push. HEAD must remain intact.

## QUEUED (ONLY AFTER D>=90% + GREEN)

- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) if coverage gaps remain
- **CAMPAIGN B:** Core/backtest/strategy only if regressions appear

## INVARIANTS (NEVER VIOLATE)

- BAB under `strategies/betting_against_beta/` FIRST
- Gate GREEN before any checkpoint/end of session
- Full suite via gate only
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf/NaT explicitly
- No breaking API changes
- Heavy hardening - no shortcuts
- Raise `BABDataError` on parse/validation failures

**ACTION:** Execute recon. Drive `strategies/betting_against_beta/data_loader.py` from current coverage to >= 90% with zero regressions. Do not stop until target met and `bash scripts/bab_gate.sh` exits 0.
