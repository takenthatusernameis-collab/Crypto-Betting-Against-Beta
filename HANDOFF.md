# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-05T03:35:00Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-05T03:23:46Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

## SAME-RUN RECOVERY (BLOCKING CONTEXT)
- **Run context:** NEW worker session inside the SAME active GitHub Actions run (previous session ended due to bounded remote checkpoint persistence failure).
- **HEAD state:** Local HEAD `29d0d3cf1740dee4605e4358e3f29aa5261c0868` (ahead of origin/main by 9 commits). Last known remote-tracking `6b89023` (push succeeded after dropping workflow-touching commit).
- **Preserve:** ALL existing local commits and work. Do NOT reset/discard. No history rewrite unless confirmed root cause requires AND after preserving recovery bundle + rollback plan.
- **Push:** Remote push pending due to GitHub App missing `workflows` permission on workflow changes in previous context; controller will retry persistence of all local-ahead commits after this session - DO NOT claim persistence until remote SHA matches.
- **Status:** `git status --short --branch` shows clean tree, ahead commits preserved.

**REMEDY (safe, material):**
1. **Verify gate first** - `bash scripts/bab_gate.sh` must exit 0.
2. **Do NOT force-push or rewrite history.** Blocker is permission-scoped (workflows). Controller will retry; keep working productively without blocking on remote.
3. **If push/auth issues surface again,** document exact error, ensure no new workflow files staged unexpectedly, and continue local work. Do not modify auth/push mechanics.
4. **Confirm clean state** - `git status --short --branch` should show ahead commits with clean tree.

## STEP 0 (GATE - BLOCKING)
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN). **CURRENT: GREEN** (2779 passed, 18 skipped).
2. If RED in this session, fix gate FIRST - no feature work until GREEN. Never checkpoint with RED.
3. Gate is source of truth.

## STEP 1 (PRIMARY CAMPAIGN D - RELENTLESS, DO NOT STOP)
Drive `strategies/betting_against_beta/data_loader.py` from **78%** to **>=90%** with:
- Zero API breaks
- Zero test regressions  
- Gate GREEN after EVERY batch
- Do not stop until >=90% AND gate GREEN

**Current (gate):** data_loader.py **78%** (1679 stmts, 364 missed). Need to cover ~185+ more statements to reach >=90%.

**Added in this session:** Added `tests/test_bab_data_loader_campaign_d_final_push.py` with 65+ tests covering early helpers, normalize_index paths, exchange format, promotion/coercion, loaders/validate paths etc. Full gate remains GREEN. Coverage of data_loader did not reach >=90% yet - need more targeted tests for specific uncovered branches.

## MANDATORY GATE (LAW)
1. IMMEDIATELY run: `bash scripts/bab_gate.sh` (full suite via gate)
2. MUST exit 0. If RED → stop feature work and fix.
3. NEVER checkpoint with RED.
4. Gate is source of truth.

## CURRENT STATE (2026-11-05T02:43:30Z)
- **Git:** Clean working tree on main, 8 commits ahead of origin/main (local commits preserved). Remote push pending due to app permissions (controller will retry).
- **Gate:** GREEN (2779 passed, 18 skipped). All tests pass.
- **Coverage:** data_loader.py **78%** → TARGET **>=90%** (need +12pp, ~196 stmts). Other modules have good coverage.
- **Focus:** Campaign D is the ONLY mission until data_loader.py >=90% AND gate GREEN
- **New tests:** Added comprehensive campaign D tests in `tests/test_bab_data_loader_campaign_d_final_push.py`

## ATTACK STRATEGY - HIT EVERY UNCOVERED BRANCH
Recon first every session:
```bash
bash scripts/bab_gate.sh 2>&1 | tail -3
PYTHONPATH=$PWD python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_*data_loader*.py 2>&1 | tail -2
PYTHONPATH=$PWD python3 -m coverage report -m --include="strategies/betting_against_beta/data_loader.py"
```

Focus areas (from current coverage gaps in gate):
1. **Early helpers** (_not_null, _series_has_any_finite, _coerce_series_to_datetime_index) - some branches missed
2. **_normalize_index numeric epoch branches** (~120-290): different magnitudes, fallbacks, exception paths
3. **_coerce_to_datetime_scalar** (~309-495): epoch magnitudes, string parsing, NA/nat/inf, tz
4. **_detect_and_normalize_exchange_format** (~495-700): long-format pivot edge cases, OHLCV wide, date promotion
5. **_promote_datetime_column** (~700-924): unnamed/object columns, tz normalization, fallbacks
6. **_normalize_columns/_drop_all_nan_columns** (~986-1104)
7. **_strip_units_and_parse/_coerce_numeric/_series_is_parseable** (~1104-1232)
8. **_run_data_quality_campaign** (~1232-1351)
9. **validate_returns_dataframe** (~1351-1562)
10. **All loaders** (~1562-1871): CSV/JSON/JSONL/Parquet/HDF5/Pickle, errors
11. **Remaining helpers** (~1871-2259): drop metadata, detect, normalize_schema, standardize, clean_data, validate_prices

## EXECUTION RULES (NON-NEGOTIABLE)
1. **Recon first** - identify exact missing lines every session via coverage
2. **Adversarial tests** - Add comprehensive tests hitting EVERY uncovered branch in `tests/test_bab_data_loader_campaign_d*.py` (extend existing or create new focused ones)
3. **Implementation only if necessary** - Only modify impl if branch truly untestable via public APIs; preserve all public APIs, raise `BABDataError` on failures
4. **Gate after EVERY batch** - `bash scripts/bab_gate.sh` MUST exit 0 after EVERY batch
5. **No sidetracks** - Do NOT move to other campaigns until data_loader.py >=90% AND gate GREEN
6. **No shortcuts** - Heavy relentless hardening. Every missing branch must be covered or proven untestable
7. **Zero regressions** - All existing tests must pass
8. **Preserve commits/work** - Same-run recovery context applies; no resets/discards/rebases without documented rollback plan after recovery bundle

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

**ACTION:** Gate is GREEN (2779 passed, 18 skipped). Campaign D is the ONLY mission. Drive data_loader.py from 79% to >=90% with zero regressions. Be relentless - do not stop until target met and gate GREEN. Same-run recovery noted (push pending due to permissions; controller will retry). All local commits preserved.
