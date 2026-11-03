# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T19:25:00Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` (~1944+ tests). Be patient - do not kill it early. NEVER checkpoint with RED.

**GATE STATUS AT HANDOFF TIME:** GREEN (re-verified after adding data_loader tests). Working tree has uncommitted test files added for hardening. Continue Campaign D.

**HEAVY WORK MANDATE:** This repo is named "Crypto-Betting-Against-Beta". There is NO reason to do lightweight work. Campaign D must be driven to completion with ruthless coverage focus. If you find yourself "done" before hitting >=90% on `data_loader.py` with green gate, you have not looked hard enough.

## CURRENT FOCUS CAMPAIGN (GATE GREEN -> HEAVY WORK NOW)

### CAMPAIGN D - data_loader.py HARDENING (ACTIVE - HIGHEST PRIORITY NOW)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **70%** toward **>=90%** without changing public APIs.

**Progress this session:**
- Added comprehensive tests for `_normalize_index` (numeric epoch magnitudes ns/us/ms/s, floats, mixed tz strings, elementwise coercion, duplicates/NaT, unparseable cases)
- Added tests for `_coerce_to_datetime_scalar` (all magnitudes, NaN/inf/None/NaT, tz-aware, strings with Z/offset)
- Added tests for `_coerce_series_to_datetime_index`, `_detect_and_normalize_exchange_format`, `_promote_datetime_column`, `_coerce_numeric`, `_run_data_quality_campaign`
- Added tests for loaders (`load_returns_from_csv/json/pickle`, `load_returns_from_dataframe`, `load_prices` paths)
- Gate remains GREEN. Total missing decreased (691->681). Continue pushing coverage upward.

**Coverage-driven attack order (execute in this exact sequence):**
1. `_normalize_index` - continue hardening remaining branches (numeric fallbacks, elementwise paths)
2. `_coerce_to_datetime_scalar` - cover float/int edge cases more
3. `_coerce_series_to_datetime_index` - NaT/inf/finite checks, index promotion edge cases
4. `_detect_and_normalize_exchange_format` - long/wide/OHLCV detection edge cases
5. `_promote_datetime_column` - epoch promotion, multi-col guards, NaT containing columns, set_index failures
6. `_coerce_numeric` - uncoercible garbage paths, inf/NaN behavior
7. `_run_data_quality_campaign` - all severity paths
8. `validate_returns_dataframe` - structure validation edge cases
9. Loaders - IO errors, encoding, bad paths
10. Prices path - price->returns math edge cases
11. Remaining uncovered branches in data_loader.py

**Rules for D:**
- Do NOT change public APIs. Add guards/validation only where necessary to harden.
- All errors via `BABDataError` with clean, informative messages.
- Handle NaN/inf explicitly everywhere. Never propagate silently.
- Weights must remain lagged by 1 day (lookahead forbidden).
- Every change must keep gate GREEN. Run FULL gate after EVERY meaningful change.
- NEVER checkpoint with RED.
- If you need to add a test to cover a branch, add it in an appropriate `tests/test_bab_*` file (prefer extending existing relevant test files).
- Be adversarial - think of malformed inputs, mixed types, tz-aware/naive mixes, duplicate indices, partial data, etc.

### CAMPAIGN C - CLI/REPORTING (QUEUED)
Targets: `strategies/betting_against_beta/cli.py` (61%, 124 missing), `scripts/bab_backtest_report.py`. Only start after D >=90% AND gate GREEN.

### CAMPAIGN B - CORE/BACKTEST/STRATEGY (VIGILANCE)
Only expand if regressions appear or D+C complete and gate GREEN.

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry gate:** `timeout 600 bash scripts/bab_gate.sh` -> verify GREEN immediately on session start.
2. **Reconnaissance:** Read `strategies/betting_against_beta/data_loader.py` focusing on uncovered lines from coverage. Continue attacking in order.
3. **Relentless hardening:** Attack uncovered branches with tests; add minimal defensive code only if needed without changing APIs.
4. **Gate discipline:** Run `timeout 600 bash scripts/bab_gate.sh` after EVERY meaningful change. If RED -> fix immediately before moving on.
5. **Sync workflows/controllers:** If touching workflows/controllers, sync patterns in BOTH `scripts/controller_progress.py` and `.github/workflows/main.yml`.
6. **Coverage tracking:** Push until >=90%. Do not stop early.
7. **Handoff on stop:** UPDATE THIS FILE with timestamp, files modified, exact state, next concrete steps with `file:line`, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** BAB under `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full suite:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights lagged by 1 day.
- **Finiteness:** Handle NaN/inf explicitly.
- **API compatibility:** No breaking public API changes.
- **Sync workflows/controllers:** Pattern changes must be mirrored.
- **Heavy work mandatory:** Given repo name "Crypto-Betting-Against-Beta", substantial hardening is required.

## PROGRESS SNAPSHOT (2026-11-03T19:25:00Z)
- **Gate:** GREEN (1944+ tests passing, exit 0). Verified after test additions.
- **Working tree:** Modified/added test files for data_loader hardening (uncommitted). No source code changes to data_loader API/behavior.
- **Files added:** `tests/test_bab_data_loader_campaign_d2.py`, `tests/test_bab_data_loader_campaign_d3.py`, `tests/test_bab_data_loader_campaign_d4.py`, `tests/test_bab_data_loader_coerce_series.py`, `tests/test_bab_data_loader_exchange.py`, `tests/test_bab_data_loader_promote.py`, `tests/test_bab_data_loader_numeric_qc.py`, `tests/test_bab_data_loader_loaders.py`, `tests/test_bab_data_loader_more_loaders.py`
- **data_loader.py:** ~70% coverage, actively being pushed higher via targeted tests. Continue Campaign D.
- **cli.py:** 61% coverage - Campaign C (queued after D>=90%).
- **Immediate next action:** Continue Campaign D - examine remaining uncovered branches in `strategies/betting_against_beta/data_loader.py` (focus on `_promote_datetime_column`, `_coerce_numeric`, loader error paths, `_run_data_quality_campaign` branches) and add adversarial tests. Run full gate frequently.
