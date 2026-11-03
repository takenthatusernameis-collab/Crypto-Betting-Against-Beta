# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T17:08:15Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` (~1900 tests, ~3-4 min). Be patient - do not kill it early.

**GATE STATUS AT HANDOFF TIME:** RED — 1938 passed, 13 skipped, 6 FAILED, exit 1 (~170s).
**Failures (must fix first):**
- `tests/test_bab_data_loader_campaign_d4.py::test_promote_datetime_from_date_column` - `_promote_datetime_column` not promoting `date` column to `DatetimeIndex`
- `tests/test_bab_data_loader_campaign_d4.py::test_promote_datetime_unparseable_raises` - unparseable dates not raising `BABDataError`
- `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync::test_python_patterns_are_subset_of_workflow` - `*/.github/workflows/*` missing from workflow
- `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync::test_nested_workflow_pattern_is_present_in_workflow` - nested workflow pattern missing from workflow

**Working tree:** UNCOMMITTED. Do not commit unless explicitly asked.

## BOTTLENECKS IDENTIFIED & REMOVAL INSTRUCTIONS
1. **PATTERN SYNC BROKEN (CRITICAL - BLOCKING GATE)** - `scripts/controller_progress.py` has `*/.github/workflows/*` in `EXCLUDE_PATTERNS` but `.github/workflows/main.yml`'s `stage_safe_changes` case is missing it again. This was just fixed last session and is now broken again. MUST sync in BOTH places. Add `*/.github/workflows/*` to the bash case in `.github/workflows/main.yml` (near line ~1163, after `.github/workflows/*`) AND ensure `controller_progress.EXCLUDE_PATTERNS` contains it.
2. **Campaign D4 tests failing (BLOCKING GATE)** - New tests added for `_promote_datetime_column`. Implementation in `strategies/betting_against_beta/data_loader.py` is incomplete/wrong. Must make both tests pass without breaking existing behavior.
3. **Long gate runtime** - Expect 3-4 min. Use `timeout 600`. Do not interrupt.
4. **Coverage blind spots** - `data_loader.py` still at 68% (499 missing). Continue hardening after unblocking gate.

## CURRENT FOCUS CAMPAIGN (UNBLOCK FIRST, THEN HEAVY WORK)

### CAMPAIGN 0 - UNBLOCK GATE (HIGHEST PRIORITY - DO NOT START ANYTHING ELSE)
**Objective:** Get gate GREEN. Fix both bottleneck classes in parallel if possible.

**Tasks:**
1. **Fix pattern sync (5 min)**
   - Read `.github/workflows/main.yml` around `stage_safe_changes` case
   - Add `*/.github/workflows/*` to the bash pattern list (must match what controller expects)
   - Read `scripts/controller_progress.py` to confirm `EXCLUDE_PATTERNS` has it
   - Verify both match

2. **Fix `_promote_datetime_column` (15-30 min)**
   - Read `strategies/betting_against_beta/data_loader.py` `_promote_datetime_column` (around 648-865)
   - Test expects: when there's a `date` column with parseable dates like `["2023-01-01", "2023-01-02"]`, it should be promoted to `DatetimeIndex` (and likely removed as column or handled per existing API)
   - Test expects: unparseable dates like `["bad", "also-bad"]` must raise `BABDataError`
   - Study existing behavior of similar promotion functions (`_coerce_series_to_datetime_index`, `_normalize_index`) to match style
   - Add/fix logic to try parsing `date`/`datetime`/`time` columns, coerce to datetime, set as index, handle unparseable by raising `BABDataError`
   - Don't change public API

**Verification:** After each fix, run just the failing tests first: `python -m pytest tests/test_bab_data_loader_campaign_d4.py tests/test_controller_progress_accounting.py -v`. Then run full gate once both fixed.

### CAMPAIGN D - data_loader.py HARDENING (RESUME AFTER GATE GREEN)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **68%** (499 missing stmts) toward **>=90%** without changing public APIs.

**Attack remaining in this exact order:**
1. `_normalize_index` mixed-tz/string branch (lines ~182-261) - dayfirst elementwise (207-227), fallback raise (228-238), tz-convert fallbacks (250-257).
2. `_coerce_to_datetime_scalar` remaining float branch (lines ~428-465) and Timestamp/fallback paths (467-488).
3. `_coerce_series_to_datetime_index` (lines ~64-99) - finite checks, index promotion.
4. `_detect_and_normalize_exchange_format` (lines ~443-645) - long/wide/OHLCV, pivot, column promotion, guards.
5. `_promote_datetime_column` (lines ~648-865) - continue hardening beyond D4 fixes (guards, unnamed/object/epoch promotion).
6. `_coerce_numeric` (lines ~1130-1165) - per-column coercion, BABDataError on garbage, second-pass.
7. `_run_data_quality_campaign` (lines ~1170-1285) - gaps/dupes/stale/min-finite/implausible.
8. `validate_returns_dataframe` (lines ~1289-1464) - structure/benchmark/min-history/JSON strictness.
9. Loaders (`load_returns_from_csv/parquet/hdf5/pickle/json/dataframe`) (lines ~1467-1689).
10. Prices path (`load_prices`, `_prices_to_returns`, `detect_price_or_returns`, `normalize_schema`) (lines ~1745-2056).
11. Aliases/utils (`standardize_columns`, `clean_data`, `validate_prices`, list_columns/iter_assets) (lines ~2065-2109).

**Rules for D:** Do NOT change public APIs. Add guards/validation. All errors via `BABDataError` with clean messages. Handle NaN/inf explicitly everywhere. Weights must remain lagged by 1 day (lookahead forbidden). Every change must keep gate GREEN. Add tests as needed. Run FULL gate after every meaningful change.

### CAMPAIGN C - CLI/REPORTING (QUEUED)
Targets: `cli.py` (61%, 124 missing), `scripts/bab_backtest_report.py`. Only start after D >=90% AND gate GREEN.

### CAMPAIGN B - CORE/BACKTEST/STRATEGY (VIGILANCE)
Only expand if regressions appear or D+C complete and gate GREEN.

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry gate:** `timeout 600 bash scripts/bab_gate.sh` -> currently RED. Fix first.
2. **Unblock immediately:** Fix pattern sync in both places, fix `_promote_datetime_column` for D4 tests. Run focused tests, then full gate until GREEN.
3. **Recon D:** Once GREEN, read `strategies/betting_against_beta/data_loader.py` top-to-bottom focusing on D sections. Continue hammering D.
4. **Verify constantly:** Run gate after EVERY meaningful change. NEVER checkpoint with RED.
5. **Sync on workflow changes:** If touching workflows/controllers, sync patterns in BOTH `scripts/controller_progress.py` and `.github/workflows/main.yml`.
6. **Handoff on stop:** UPDATE THIS FILE with timestamp, files modified, exact state, next concrete steps with file:line, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** BAB under `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full suite:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights lagged by 1 day.
- **Finiteness:** Handle NaN/inf explicitly.
- **API compatibility:** No breaking public API changes.
- **Sync workflows/controllers:** Pattern changes must be mirrored.
- **Heavy work mandatory:** Given repo name "Crypto-Betting-Against-Beta", substantial hardening is required.

## PROGRESS SNAPSHOT (2026-11-03T13:09:57Z)
- **Gate:** RED (1938 passed, 13 skipped, 6 failed, ~170s). Must unblock before Campaign D.
- **New failures:** D4 tests for `_promote_datetime_column` + pattern sync regression.
- **data_loader.py:** 68% coverage (499 missing) - PRIMARY TARGET after unblocking.
- **cli.py:** 61% coverage (124 missing) - Campaign C (queued).
- **Others:** Most BAB modules >=89-100%.
- **Immediate next action:** Fix pattern sync in `.github/workflows/main.yml` + `scripts/controller_progress.py`, fix `_promote_datetime_column` in `strategies/betting_against_beta/data_loader.py`, verify focused tests then full gate GREEN.
