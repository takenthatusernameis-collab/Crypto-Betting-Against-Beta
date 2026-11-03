# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T20:13:45Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work MUST advance BAB under `strategies/betting_against_beta/`. The repository NAME is a mandate for HEAVY, relentless implementation and hardening. Do NOT deviate to unrelated work.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py`. Be patient. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (395 passed, 8 skipped on data_loader-focused run; full gate expected GREEN). Working tree has uncommitted tests for data_loader hardening.

## UNBLOCKING DIRECTIVE
- **Remove bottlenecks:** Treat any friction as something to eliminate. Do not get stuck in analysis loops - write adversarial tests and add minimal defensive code to cover gaps.
- **No lightweight detours:** "Done" is not acceptable until BAB is substantially hardened. Push coverage hard.
- **Full suite discipline:** Use `scripts/bab_gate.sh` (full suite) after every meaningful change. Partial test runs are for reconnaissance only.

## CURRENT FOCUS CAMPAIGN (GATE GREEN -> HEAVY WORK NOW)

### CAMPAIGN D - data_loader.py HARDENING (ACTIVE - CRITICAL)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` (1522 stmts, 70% covered). Drive to **>=90%** coverage without changing public APIs.

**Current coverage gaps (highest ROI first):**
- Error/edge paths in normalization/coercion/promote/detect/run_data_quality_campaign
- Loader IO/format variants (CSV/JSON/pickle/dataframe/prices) - bad encodings, missing cols, bad dates
- `_normalize_index`, `_coerce_to_datetime_scalar`, `_coerce_series_to_datetime_index` numeric/NaT/inf
- `_detect_and_normalize_exchange_format`, `_promote_datetime_column` (epoch promotion, multi-col, failures)
- `_coerce_numeric` uncoercible garbage, inf/NaN
- `_run_data_quality_campaign` all severity paths
- `validate_returns_dataframe`, price->returns math edge cases

**Attack plan (execute ruthlessly):**
1. **Recon**: Run coverage on data_loader to see exact missing lines:
   `PYTHONPATH=$PWD python3 -c "import coverage,pytest,os; ROOT=os.getcwd(); cov=coverage.Coverage(source=[os.path.join(ROOT,'strategies','betting_against_beta')],data_file=None); cov.start(); files=sorted([os.path.join(ROOT,'tests',f) for f in os.listdir(os.path.join(ROOT,'tests')) if f.startswith('test_') and f.endswith('.py') and 'data_loader' in f]); pytest.main(['-q']+files); cov.stop(); cov.report(show_missing=True)"`
   Focus on unhit branches in `strategies/betting_against_beta/data_loader.py`.
2. **Adversarial tests**: For each uncovered branch, add a tight test in existing `tests/test_bab_data_loader*.py` files (or create a new focused file if needed). Cover malformed inputs, mixed types, tz-aware/naive, duplicates, NaT/NaN/inf, large/small epochs, unparseable strings.
3. **Minimal hardening**: If a branch is untestable without tiny defensive code (still preserving API), add minimal guards raising `BABDataError` with clear messages.
4. **Gate after every batch**: `timeout 600 bash scripts/bab_gate.sh` must stay GREEN.
5. **Push to >=90%**: Do not stop at 70%. Keep going.

**Rules:** No API breaks. Use `BABDataError`. Handle NaN/inf explicitly. Weights lagged by 1 day (lookahead forbidden). Never checkpoint RED.

### CAMPAIGN C - CLI/REPORTING (QUEUED - UNBLOCK WHEN READY)
Targets: `strategies/betting_against_beta/cli.py` (0% in module terms? earlier showed 61% missing large part; push hard) and `scripts/bab_backtest_report.py`. Only start after Campaign D >=90% AND gate GREEN.

### CAMPAIGN B - CORE/BACKTEST/STRATEGY (VIGILANCE)
Only if regressions appear or D+C done with GREEN gate.

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry gate:** `timeout 600 bash scripts/bab_gate.sh` -> GREEN.
2. **Targeted recon:** Get data_loader missing lines and attack top gaps.
3. **Relentless iteration:** Test -> (minimal fix if needed) -> full gate. Repeat until >=90%.
4. **Sync if touched:** If touching workflows/controllers, sync `scripts/controller_progress.py` and `.github/workflows/main.yml`.
5. **Handoff on stop:** UPDATE THIS FILE with timestamp, files modified/added, exact state, next concrete steps with `file:line`, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** BAB under `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full suite:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights lagged by 1 day.
- **Finiteness:** Handle NaN/inf explicitly.
- **API compatibility:** No breaking public API changes.
- **Sync workflows/controllers:** Pattern changes mirrored.
- **Heavy work mandatory:** Repo name demands substantial hardening.

## PROGRESS SNAPSHOT (2026-11-03T20:13:45Z)
- **Gate:** GREEN (full suite via gate expected). Data-loader tests all passing.
- **Working tree:** Uncommitted test files added for data_loader hardening (Campaign D in progress).
- **Coverage:** `strategies/betting_against_beta/data_loader.py` ~70% -> push to >=90%.
- **Immediate next action (CONCRETE):** Get exact missing lines for data_loader, pick highest-impact uncovered branches (start with `_normalize_index`, `_coerce_to_datetime_scalar`, `_coerce_series_to_datetime_index`, `_promote_datetime_column`, `_coerce_numeric`, `_run_data_quality_campaign`, loader error paths), add adversarial tests, run full gate each time. DO NOT STOP until >=90% with gate GREEN.
