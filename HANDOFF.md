# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-05T01:27:22Z
**Repo:** Crypto-Betting-Against-Beta (BAB)
**Priority:** strategies/betting_against_beta/ - HEAVY, relentless implementation and hardening

## INITIAL TASK MESSAGE (for next agentic session - EXECUTE FIRST)
**Time:** 2026-11-05T01:27:22Z
**MANDATE:** Repository name is directive. ALL work MUST advance BAB under `strategies/betting_against_beta/`. Do NOT deviate. Build a focus campaign future agents cannot dodge - heavy work only.

## SAME-RUN RECOVERY (BLOCKING CONTEXT)
- **Run context:** NEW worker session inside the SAME active GitHub Actions run (previous session ended due to bounded remote checkpoint persistence failure).
- **HEAD state:** Local HEAD `85905b3111a199136cb8e9837766b9e728cd298b` (ahead of origin/main by 4). Last known remote-tracking `1a585a3d7cf12009aa55c723d6cfc725c697e959`.
- **Preserve:** ALL existing local commits and work. Do NOT reset/discard. No history rewrite unless confirmed root cause requires AND after preserving recovery bundle + rollback plan.
- **Recovery artifacts:** Check `/home/runner/work/_temp/` for `kilo-recovery-*.bundle` and `kilo-recovery-status-*.txt` if present. Session logs showed push blocked by GitHub App missing `workflows` permission on workflow changes; controller will retry persistence of all local-ahead commits after this session - DO NOT claim persistence until remote SHA matches.
- **Note:** Branch is `main...origin/main [ahead 4]` with clean tree.

**REMEDY (safe, material):**
1. **Verify gate first** - `bash scripts/bab_gate.sh` must exit 0.
2. **Do NOT force-push or rewrite history.** Blocker is permission-scoped (workflows). Controller will retry; keep working productively without blocking on remote.
3. **If push/auth issues surface again,** document exact error, ensure no new workflow files staged unexpectedly, and continue local work. Do not modify auth/push mechanics.
4. **Confirm clean state** - `git status --short --branch` should show ahead commits with clean tree (or intentional uncommitted work only if necessary).

## STEP 0 (GATE - BLOCKING)
1. `bash scripts/bab_gate.sh` MUST exit 0 (GREEN).
2. Bottleneck REMOVED previously: added `*/.github/workflows/*` to workflow `stage_safe_changes` pattern-sync.
3. If RED in this session, fix gate FIRST - no feature work until GREEN. Never checkpoint with RED.

## STEP 1 (PRIMARY CAMPAIGN D - RELENTLESS, DO NOT STOP)
Drive `strategies/betting_against_beta/data_loader.py` from **78%** to **>=90%** with:
- Zero API breaks
- Zero test regressions
- Gate GREEN after EVERY batch
- Do not stop until >=90% AND gate GREEN

**Current:** data_loader.py **78%** (1669 stmts, ~375 missing). Need to cover ~205+ more statements.

## MANDATORY GATE (LAW)
1. IMMEDIATELY run: `bash scripts/bab_gate.sh` (full suite via gate)
2. MUST exit 0. If RED → stop feature work and fix.
3. NEVER checkpoint with RED.
4. Gate is source of truth.

## CURRENT STATE (2026-11-05T01:27:22Z)
- **Git:** Clean working tree on main, 4 commits ahead of origin/main (85905b3, ce40122, 42b7caf, 6cf5b1c). Remote push pending due to app permissions (controller will retry).
- **Gate:** Run immediately if not confirmed; previously GREEN.
- **Coverage:** data_loader.py **78%** → TARGET **>=90%** (966 passed, 13 skipped in data_loader tests)
- **Focus:** Campaign D is the ONLY mission until data_loader.py >=90% AND gate GREEN

## ATTACK STRATEGY - HIT EVERY UNCOVERED BRANCH
Recon first every session:
```bash
bash scripts/bab_gate.sh 2>&1 | tail -3
PYTHONPATH=$PWD python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_*data_loader*.py 2>&1 | tail -2
PYTHONPATH=$PWD python3 -m coverage report -m --include="strategies/betting_against_beta/data_loader.py"
```

Focus areas (from current coverage gaps):
1. **_normalize_index numeric epoch branches** (~120-193)
2. **_coerce_to_datetime_scalar** (~295-479): epoch magnitudes, string parsing, NA/nat/inf, tz
3. **_detect_and_normalize_exchange_format** (~525-700): long-format pivot, OHLCV wide, date promotion
4. **_promote_datetime_column** (~715-904): unnamed/object columns, tz normalization, fallbacks
5. **_normalize_columns/_drop_all_nan_columns** (~981-1084)
6. **_strip_units_and_parse/_coerce_numeric** (~1085-1213): currency/commas/percent, malformed
7. **_run_data_quality_campaign** (~1226-1333)
8. **validate_returns_dataframe** (~1389-1545)
9. **All loaders** (~1548-1854): CSV/JSON/JSONL/Parquet/HDF5/Pickle, errors
10. **Remaining helpers** (~1866-2221): drop metadata, detect, normalize_schema, standardize, clean_data, validate_prices

## EXECUTION RULES (NON-NEGOTIABLE)
1. **Recon first** - identify exact missing lines every session
2. **Adversarial tests** - Add comprehensive tests hitting EVERY uncovered branch in `tests/test_bab_data_loader_campaign_d_push*.py` (extend existing campaign files or create new focused ones)
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

**ACTION:** Gate is source of truth. Same-run recovery noted (push pending due to permissions; controller will retry). Campaign D is the ONLY mission. Drive data_loader.py from 78% to >=90% with zero regressions. Be relentless - do not stop until target met and gate GREEN.
