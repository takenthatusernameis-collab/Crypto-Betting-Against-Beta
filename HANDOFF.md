# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T22:25:15Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work MUST advance BAB under `strategies/betting_against_beta/`. The repository NAME is a mandate for HEAVY, relentless implementation and hardening. Do NOT deviate to unrelated work.

**MANDATORY GATE (LAW):** Run `export PATH=$HOME/.local/bin:$PATH && timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py`. Be patient. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (2000 passed, 13 skipped; controller tests all pass). Working tree clean as of handoff EXCEPT the bottleneck fix below, which is now applied and verified GREEN.

## BOTTLENECKS REMOVED / FIXED THIS SESSION
1. **Controller/workflow pattern parity FIXED (was blocking the gate - RED).** The gate entered this session RED: 2 controller failures (`test_python_patterns_are_subset_of_workflow`, `test_nested_workflow_pattern_is_present_in_workflow`) because `scripts/controller_progress.py:EXCLUDE_PATTERNS` contains `*/.github/workflows/*` but `.github/workflows/main.yml:1163` (`stage_safe_changes()` bash case list) did not. Added `*/.github/workflows/*` to the workflow's `stage_safe_changes()` pattern list right after `.github/workflows/*`. Pattern lists are now in lock-step. Gate re-ran GREEN (2000 passed, 13 skipped). This is the single point that was blocking all progress; it is cleared.

## CURRENT FOCUS CAMPAIGN (MAXIMUM IMPACT - DO NOT STOP UNTIL DONE)
### CAMPAIGN D - data_loader.py HARDENING (PRIMARY CRITICAL TARGET)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts). Drive coverage from **72% (425 missing statements) in full-suite gate report** to **>=90%** with zero API breaks. This is the biggest remaining coverage gap by far (next closest module is cli.py at 61% but data_loader has the largest absolute missing-statement count and is the strategy's data entry point).

**Priority attack order (by missing coverage - highest ROI first):**
1. `_normalize_index` - numeric epoch magnitude branches (ms/us/ns/s), large gaps, mixed types, unparseable -> raise BABDataError
2. `_coerce_to_datetime_scalar` - numeric-string magnitude branches, int/float paths, tz-aware/naive handling
3. `_promote_datetime_column` / `_detect_and_normalize_exchange_format` - exchange format detection edge cases, promotion logic
4. `_coerce_numeric`, `_normalize_columns`, unit stripping, parseability
5. `_run_data_quality_campaign`, validation paths, loaders (`load_returns*`, `load_prices`, `load_returns_from_*`), schema/cleaning, JSON/CSV/Excel-like edge cases, NaN/inf/NaT handling

**Aggressive execution plan:**
1. **Recon:** Measure data_loader coverage in isolation against all data_loader tests.
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
2. **Attack relentlessly:** Add tight adversarial tests to existing `tests/test_bab_data_loader*.py` files OR create `tests/test_bab_data_loader_campaign_d_deep.py`. Cover every branch: malformed/mixed types, tz-aware/naive crossovers, NaT/NaN/inf, epochs in seconds/ms/microseconds/nanoseconds, unparseable strings, bad encodings, missing cols, empty/partial frames, duplicates, index types.
3. **Harden minimally:** Only make minimal defensive changes if truly untestable through existing APIs. Always raise `BABDataError` with clear messages. Preserve all public APIs. No behavior changes breaking existing tests.
4. **Verify constantly:** Run full gate after each batch - MUST stay GREEN. Be patient.
5. **Iterate until >=90%:** Do not move to next campaign until >=90% coverage on data_loader.py and gate GREEN.

### QUEUED (AFTER CAMPAIGN D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) - only if D complete and gate GREEN
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry:** Run gate first - must be GREEN
2. **Recon:** Get data_loader coverage breakdown
3. **Target top gaps:** `_normalize_index` and `_coerce_to_datetime_scalar` first (massive uncovered area)
4. **Test-heavy hardening:** Write tests that exercise every branch, add minimal fixes if needed
5. **Gate after every change batch:** `timeout 600 bash scripts/bab_gate.sh` must exit 0
6. **Update handoff on stop:** With timestamp, files changed, gate status, concrete next steps

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate (all tests)
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Pattern changes mirrored between controller and workflow
- Heavy hardening required - no half-measures

## PROGRESS SNAPSHOT (2026-11-03T22:25:15Z)
- **Gate:** GREEN (2000 passed, 13 skipped)
- **Bottleneck removed:** controller/workflow pattern parity (`*/.github/workflows/*` added to workflow stage_safe_changes); gate was RED, now GREEN
- **Focus:** Campaign D - data_loader.py 72% (425 missing / 1522 stmts) -> >=90%
- **Immediate next action:** Run gate (GREEN confirmed), run recon coverage on data_loader.py against data_loader tests, target `_normalize_index` and `_coerce_to_datetime_scalar` uncovered branches first with adversarial tests.
