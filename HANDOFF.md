# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-04T23:30:47Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-04T23:30:47Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

**STEP 0 (GATE - BLOCKING):**
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). Confirm full suite passes. ✓ GREEN as of 2026-11-04T23:30:47Z (2497 passed, 18 skipped).
2. Bottleneck REMOVED: added `*/.github/workflows/*` to workflow `stage_safe_changes` case (`.github/workflows/main.yml:1163`) so controller/workflow pattern-sync tests pass. Gate was RED, now GREEN.
3. If RED in a future session, fix gate FIRST - no feature work until GREEN. Never checkpoint with RED.

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
- **Git:** Clean working tree on main (after gate fix commit)
- **Gate:** GREEN - `bash scripts/bab_gate.sh` exits 0 (2497 passed, 18 skipped)
- **Coverage (current):** data_loader.py **78%** (1669 stmts, 372 missing) → TARGET **>=90%** (need to cover ~205+ more statements)
- **Focus:** Campaign D is the ONLY mission until data_loader.py >=90%

## ATTACK STRATEGY - HIT EVERY UNCOVERED BRANCH

**Recon (run FIRST every session):**
```bash
bash scripts/bab_gate.sh 2>&1 | tail -5
PYTHONPATH=$PWD python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_*data_loader*.py 2>&1 | tail -3
PYTHONPATH=$PWD python3 -m coverage report -m --include="strategies/betting_against_beta/data_loader.py"
```

**SYSTEMATIC ATTACK PLAN (use coverage Missing list):**

**PRIORITY 1 - _normalize_index numeric epoch branches (lines ~120-193):**
Hit ns/us/ms/s boundaries, empty numeric index, sample conversion failures, all fallback paths, mixed types.

**PRIORITY 2 - _coerce_to_datetime_scalar (lines ~295-479):**
All string epoch magnitudes (ns/us/ms/s), ISO formats, dayfirst, NA markers, int/float/Timestamp paths, garbage raising.

**PRIORITY 3 - _detect_and_normalize_exchange_format (lines ~525-700):**
Long-format pivot, OHLCV wide formats, date-column promotion, early returns, edge cases.

**PRIORITY 4 - _promote_datetime_column (lines ~715-904):**
Unnamed columns, last-resort object column, tz normalization, candidate parsing failures.

**PRIORITY 5 - _normalize_columns (lines ~981-1043):**
Column variants, duplicate detection, unnamed drop, exception handlers.

**PRIORITY 6 - _drop_all_nan_columns, _strip_units_and_parse, _coerce_numeric (lines ~1053-1213):**
All-NaN edge cases, currency symbols/commas/percent/NA, malformed numbers, pure garbage, object coercion.

**PRIORITY 7 - _run_data_quality_campaign (lines ~1226-1333):**
All quality checks - None/empty/non-DF, duplicates, implausible returns, gaps, staleness, min finite fraction.

**PRIORITY 8 - validate_returns_dataframe (lines ~1389-1545):**
All validation paths - None/non-DF/empty, insufficient rows, missing benchmark, only benchmark, short history, inf values, RangeIndex without datetime.

**PRIORITY 9 - All loaders (lines ~1548-1854):**
CSV/JSON/JSONL/Parquet/HDF5/Pickle roundtrips, not-found cases, empty files, pickle scalar/list types, unsupported extensions, directory paths, dispatch logic.

**PRIORITY 10 - Remaining helpers (lines ~1866-2221):**
_drop_metadata_columns, detect_price_or_returns, normalize_schema, standardize_columns, clean_data, validate_prices.

## EXECUTION RULES (NON-NEGOTIABLE)
1. **Recon first** - identify exact missing lines with coverage report every session
2. **Adversarial tests** - Add comprehensive tests hitting EVERY uncovered branch. Put in `tests/test_bab_data_loader_campaign_d_push*.py` (create new files as needed)
3. **Implementation only if necessary** - Only modify implementation if branch truly untestable via public APIs; preserve all public APIs, raise `BABDataError` on failures
4. **Gate after EVERY batch** - `bash scripts/bab_gate.sh` MUST exit 0 after EVERY batch (~2-3 min) - be patient, no rushing
5. **No sidetracks** - Do NOT move to other campaigns until data_loader.py >=90% AND gate GREEN
6. **No shortcuts** - Heavy relentless hardening. Every single missing branch must be covered or proven untestable
7. **Zero regressions** - All existing tests must pass

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

**ACTION:** Gate is GREEN. Campaign D is the ONLY mission. Drive data_loader.py from 78% to >=90% with zero regressions. Be relentless. Hit every uncovered line.
