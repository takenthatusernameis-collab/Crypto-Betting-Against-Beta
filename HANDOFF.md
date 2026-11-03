# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T21:35:19Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work MUST advance BAB under `strategies/betting_against_beta/`. The repository NAME is a mandate for HEAVY, relentless implementation and hardening. Do NOT deviate to unrelated work.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py`. Be patient. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (all tests passing). Working tree state as-is; review uncommitted changes and commit only after confirming GREEN.

## BOTTLENECKS REMOVED / FIXED THIS SESSION
1. **Gate pattern-sync drift (controller/workflow) FIXED.** Added `*/.github/workflows/*` to both `stage_safe_changes` case list and mirrored in `stage_and_checkpoint` in `.github/workflows/main.yml` to match `scripts/controller_progress.py:EXCLUDE_PATTERNS`. Tests `tests/test_controller_progress_accounting.py` all pass.
2. **data_loader robustness fix.** `strategies/betting_against_beta/data_loader.py:493` reordered to check `isinstance(df, pd.DataFrame)` before `df.empty` in `_detect_and_normalize_exchange_format`.

## CURRENT FOCUS CAMPAIGN (MAXIMUM IMPACT)
### CAMPAIGN D - data_loader.py HARDENING (CRITICAL - PRIMARY TARGET)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts). Drive coverage from **72%** to **>=90%** with zero API breaks. This is the biggest remaining gap.

**Priority attack order (by missing coverage - highest ROI first):**
1. `_normalize_index` - numeric epoch magnitude branches (ms/us/ns/s), large gaps, mixed types, unparseable -> raise BABDataError
2. `_coerce_to_datetime_scalar` - numeric-string magnitude branches, int/float paths, tz-aware/naive handling
3. `_promote_datetime_column` / `_detect_and_normalize_exchange_format` - exchange format detection edge cases, promotion logic
4. `_coerce_numeric`, `_normalize_columns`, unit stripping, parseability
5. `_run_data_quality_campaign`, validation paths, loaders (`load_returns*`, `load_prices`), schema/cleaning, JSON/CSV edge cases

**Execution plan:**
1. **Recon:** Run coverage on data_loader tests to see exact uncovered lines.
   ```bash
   timeout 300 bash -lc 'PYTHONPATH=$PWD python3 -c "
   import coverage,pytest,os
   ROOT=os.getcwd()
   cov=coverage.Coverage(source=[os.path.join(ROOT,\"strategies\",\"betting_against_beta\")],data_file=None)
   cov.start()
   files=sorted([os.path.join(ROOT,\"tests\",f) for f in os.listdir(os.path.join(ROOT,\"tests\")) if f.startswith(\"test_\") and f.endswith(\".py\") and \"data_loader\" in f])
   pytest.main([\"-q\"]+files)
   cov.stop()
   cov.report(show_missing=True)
   "'
   ```
2. **Attack:** Add tight adversarial tests to `tests/test_bab_data_loader*.py` (or create `tests/test_bab_data_loader_campaign_d_hardening.py`). Cover malformed/mixed types, tz-aware/naive, NaT/NaN/inf, epochs (seconds/ms/microseconds/nanoseconds), unparseable strings, bad encodings, missing cols, empty/partial frames.
3. **Harden:** Only make minimal defensive changes if untestable otherwise. Always raise `BABDataError` with clear messages. Preserve all public APIs. No behavior changes that break existing tests.
4. **Verify:** Run full gate `timeout 600 bash scripts/bab_gate.sh` after each batch - MUST stay GREEN. Be patient.
5. **Iterate:** Relentlessly push to >=90%. Do not move to next campaign until >=90% and gate GREEN.

### QUEUED (AFTER D >=90% GREEN)
- **CAMPAIGN C:** CLI/reporting (`cli.py`, `scripts/bab_backtest_report.py`) - only if D complete and gate GREEN
- **CAMPAIGN B:** Core/backtest/strategy only on regressions

## EXECUTION PLAN (NON-NEGOTIABLE)
1. Entry gate GREEN (run it first)
2. Recon data_loader gaps, attack highest-impact first (_normalize_index, _coerce_to_datetime_scalar)
3. Test -> minimal fix if needed -> full gate, repeat until >=90%
4. If touching workflows/controllers, sync `scripts/controller_progress.py` and `.github/workflows/main.yml` (pattern parity required)
5. Update this handoff on stop with timestamp, files changed, gate status, concrete next steps

## INVARIANTS
- BAB under `strategies/betting_against_beta/` FIRST
- `bash scripts/bab_gate.sh` must exit 0 before ending/checkpoint
- Full suite via gate
- Weights lagged by 1 day (no lookahead)
- Handle NaN/inf explicitly
- No breaking API changes
- Pattern changes mirrored between controller and workflow
- Heavy hardening required

## PROGRESS SNAPSHOT (2026-11-03T21:35:19Z)
- **Gate:** GREEN (full suite passing)
- **Focus:** Campaign D - data_loader to >=90% coverage (currently 72%)
- **Key fixes:** workflow/controller pattern sync; data_loader isinstance-before-empty
- **Immediate next action:** Run recon coverage on data_loader tests, target top uncovered branches in `_normalize_index` and `_coerce_to_datetime_scalar` with adversarial tests, iterate to >=90% with GREEN gate.
