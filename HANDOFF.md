# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-04T01:18:22Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work MUST advance BAB under `strategies/betting_against_beta/`. The repository NAME is a mandate for HEAVY, relentless implementation and hardening. Do NOT deviate to unrelated work.

**MANDATORY GATE (LAW):** Run `export PATH=$HOME/.local/bin:$PATH && timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py`. Be patient. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (2081 passed, 15 skipped). Working tree clean of blocking issues.

## BOTTLENECKS REMOVED / FIXED THIS SESSION
1. **Controller/workflow pattern parity FIXED (was blocking the gate - RED).** The gate was RED with 2 controller failures (`test_python_patterns_are_subset_of_workflow`, `test_nested_workflow_pattern_is_present_in_workflow`) because `.github/workflows/main.yml:stage_safe_changes()` missing `*/.github/workflows/*` while `scripts/controller_progress.py:EXCLUDE_PATTERNS` had it. Added `*/.github/workflows/*` to workflow pattern list. Mirrored parity. Gate re-ran GREEN.

## CURRENT FOCUS CAMPAIGN (MAXIMUM IMPACT - DO NOT STOP UNTIL DONE)
### CAMPAIGN D - data_loader.py HARDENING (PRIMARY CRITICAL TARGET - STILL IN PROGRESS)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts). Drive coverage from **73% (406 missing statements)** to **>=90%** with zero API breaks. This remains the largest high-value coverage gap - attack relentlessly.

**Priority attack order (by missing coverage - highest ROI first):**
1. `_normalize_index` - numeric epoch magnitude branches (ms/us/ns/s, floats, mixed scales, edge cases), empty/numeric edge cases, elementwise fallbacks
2. `_coerce_to_datetime_scalar` - string epoch detection, large/small magnitudes, NaN/inf/None/NaT, tz-aware/naive, dayfirst fallbacks, malformed digit-containing strings
3. `_promote_datetime_column` / `_detect_and_normalize_exchange_format` - exchange format detection (Binance/CoinGecko/long format), unnamed columns, last-resort object parsing, tz normalization
4. `_coerce_numeric`, `_strip_units_and_parse`, `_normalize_columns`, `_series_is_parseable` - units/currency/commas/percent/European decimals, NA markers, malformed digit strings
5. `validate_returns_dataframe`, `load_returns*` (CSV/JSON/JSONL/Parquet/HDF5/Pickle/DataFrame), `load_prices`, `normalize_schema`, `detect_price_or_returns`, quality campaign paths, error cases

**Aggressive execution plan:**
1. **Recon:** Measure data_loader coverage in isolation.
   ```bash
   export PATH=$HOME/.local/bin:$PATH
   timeout 300 bash -lc 'PYTHONPATH=$PWD python3 -c "
   import coverage,pytest,os
   ROOT=os.getcwd()
   cov=coverage.Coverage(source=[os.path.join(ROOT,\"strategies\",\"betting_against_beta\",\"data_loader.py\")],data_file=None)
   cov.start()
   files=sorted([os.path.join(ROOT,\"tests\",f) for f in os.listdir(os.path.join(ROOT,\"tests\")) if f.startswith(\"test_\") and f.endswith(\".py\") and \"data_loader\" in f])
   pytest.main([\"-q\"]+files)
   cov.stop()
   cov.report(show_missing=True)
   "'
   ```
2. **Attack relentlessly:** Add adversarial tests to existing `tests/test_bab_data_loader*.py` files OR create `tests/test_bab_data_loader_campaign_d_deep2.py`. Cover every branch with tight assertions. Test error paths (BABDataError) explicitly.
3. **Harden minimally:** Only make minimal defensive changes if truly untestable through existing APIs. Always raise `BABDataError` with clear messages. Preserve all public APIs. No behavior changes breaking existing tests.
4. **Verify constantly:** Run full gate after each batch - MUST stay GREEN. Be patient with full suite.
5. **Iterate until >=90%:** Do not move to next campaign until >=90% coverage on data_loader.py and gate GREEN.

### QUEUED (AFTER CAMPAIGN D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) - only if D complete and gate GREEN
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry:** Run gate first - must be GREEN
2. **Recon:** Get data_loader coverage breakdown (isolate to data_loader tests)
3. **Target top gaps:** `_normalize_index` numeric branches, `_coerce_to_datetime_scalar` string/epoch paths first (biggest uncovered areas)
4. **Test-heavy hardening:** Write tests that exercise every branch, add minimal fixes if needed
5. **Gate after every change batch:** `timeout 600 bash scripts/bab_gate.sh` must exit 0
6. **Update handoff on stop:** With timestamp, files changed, gate status, concrete next steps, coverage % before/after

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate (all tests)
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Pattern changes mirrored between controller and workflow
- Heavy hardening required - no half-measures
- Raise `BABDataError` on bad/parse failures as per module conventions

## PROGRESS SNAPSHOT (2026-11-04T01:18:22Z)
- **Gate:** GREEN (2081 passed, 15 skipped)
- **Bottlenecks removed:** controller/workflow pattern parity fixed (`*/.github/workflows/*` added to `.github/workflows/main.yml:stage_safe_changes()` and mirrored in `scripts/controller_progress.py:EXCLUDE_PATTERNS`); gate restored to GREEN
- **Focus:** Campaign D - data_loader.py hardening in progress (73%, 406 missing statements). Added comprehensive adversarial tests covering numeric epochs (ns/us/ms/s), string epochs, tz handling, exchange formats, loaders (CSV/JSON/JSONL/pickle/parquet/hdf5), validation paths.
- **Immediate next action:** Continue Campaign D - attack remaining large gaps in data_loader. Focus on uncovered branches in `_normalize_index`, `_coerce_to_datetime_scalar`, `_promote_datetime_column`, `_detect_and_normalize_exchange_format`, loaders and validation. Add tight tests per branch, minimal defensive fixes only if necessary, run gate after each batch. Target >=90% coverage on data_loader.py, keep gate GREEN.

(End of file)
