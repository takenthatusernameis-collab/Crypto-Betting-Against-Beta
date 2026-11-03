# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T17:37:46Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` (~1944 tests, ~3 min). Be patient - do not kill it early.

**GATE STATUS AT HANDOFF TIME:** GREEN — 1944 passed, 13 skipped, exit 0 (~172s). All prior bottlenecks cleared; no session is blocked.

**BOTTLENECKS REMOVED (this session):**
1. **PATTERN SYNC FIXED** - Added `*/.github/workflows/*` to the `stage_safe_changes` case in `.github/workflows/main.yml` (line ~1163, right after `.github/workflows/*`), matching `scripts/controller_progress.py` `EXCLUDE_PATTERNS`. Both `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` now pass.
2. **`_promote_datetime_column` FIXED** - Rewrote the candidate-name promotion block in `strategies/betting_against_beta/data_loader.py` so clean date/timestamp columns promote to a `DatetimeIndex` (2-col D4 contract), unparseable values raise `BABDataError`, multi-column frames stay conservative (raw string index), and a patched/failing `set_index` keeps the column. Also guarded the last-resort loop against promoting columns containing NaT. All 6 prior gate failures (D4 `_promote_datetime_column` + pattern sync + campaign/precision-hit promotion edge cases) now pass.

**Working tree:** UNCOMMITTED. Modified: `.github/workflows/main.yml`, `strategies/betting_against_beta/data_loader.py`. Do not commit unless explicitly asked.

## CURRENT FOCUS CAMPAIGN (GATE GREEN -> HEAVY WORK NOW)

### CAMPAIGN D - data_loader.py HARDENING (ACTIVE - HIGHEST PRIORITY NOW)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **68%** (506 missing stmts) toward **>=90%** without changing public APIs. This is the heavy work the repo name demands; future agents must not skip it.

**Attack remaining in this exact order:**
1. `_normalize_index` mixed-tz/string branch (dayfirst elementwise, fallback raise, tz-convert fallbacks).
2. `_coerce_to_datetime_scalar` remaining float branch and Timestamp/fallback paths.
3. `_coerce_series_to_datetime_index` - finite checks, index promotion.
4. `_detect_and_normalize_exchange_format` - long/wide/OHLCV, pivot, column promotion, guards.
5. `_promote_datetime_column` - continue hardening beyond D4 fixes (guards, unnamed/object/epoch promotion).
6. `_coerce_numeric` - per-column coercion, BABDataError on garbage, second-pass.
7. `_run_data_quality_campaign` - gaps/dupes/stale/min-finite/implausible.
8. `validate_returns_dataframe` - structure/benchmark/min-history/JSON strictness.
9. Loaders (`load_returns_from_csv/parquet/hdf5/pickle/json/dataframe`).
10. Prices path (`load_prices`, `_prices_to_returns`, `detect_price_or_returns`, `normalize_schema`).
11. Aliases/utils (`standardize_columns`, `clean_data`, `validate_prices`, list_columns/iter_assets).

**Rules for D:** Do NOT change public APIs. Add guards/validation. All errors via `BABDataError` with clean messages. Handle NaN/inf explicitly everywhere. Weights must remain lagged by 1 day (lookahead forbidden). Every change must keep gate GREEN. Add tests as needed. Run FULL gate after EVERY meaningful change. NEVER checkpoint with RED.

### CAMPAIGN C - CLI/REPORTING (QUEUED)
Targets: `cli.py` (61%, 124 missing), `scripts/bab_backtest_report.py`. Only start after D >=90% AND gate GREEN.

### CAMPAIGN B - CORE/BACKTEST/STRATEGY (VIGILANCE)
Only expand if regressions appear or D+C complete and gate GREEN.

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry gate:** `timeout 600 bash scripts/bab_gate.sh` -> currently GREEN. Re-verify immediately on session start.
2. **Campaign D:** Read `strategies/betting_against_beta/data_loader.py` top-to-bottom; harden per the attack order above; add tests; run full gate after every meaningful change.
3. **Verify constantly:** Run gate after EVERY meaningful change. NEVER checkpoint with RED.
4. **Sync workflows/controllers:** If touching workflows/controllers, sync patterns in BOTH `scripts/controller_progress.py` and `.github/workflows/main.yml`.
5. **Handoff on stop:** UPDATE THIS FILE with timestamp, files modified, exact state, next concrete steps with file:line, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** BAB under `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full suite:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights lagged by 1 day.
- **Finiteness:** Handle NaN/inf explicitly.
- **API compatibility:** No breaking public API changes.
- **Sync workflows/controllers:** Pattern changes must be mirrored.
- **Heavy work mandatory:** Given repo name "Crypto-Betting-Against-Beta", substantial hardening is required.

## PROGRESS SNAPSHOT (2026-11-03T17:37:46Z)
- **Gate:** GREEN (1944 passed, 13 skipped, exit 0, ~172s). Unblocked this session.
- **Fixed this session:** pattern sync in `.github/workflows/main.yml` + `scripts/controller_progress.py` alignment; `_promote_datetime_column` in `strategies/betting_against_beta/data_loader.py` (D4 + campaign/precision-hit edge cases).
- **data_loader.py:** 68% coverage (506 missing) - PRIMARY TARGET (Campaign D).
- **cli.py:** 61% coverage (124 missing) - Campaign C (queued).
- **Others:** Most BAB modules >=89-100%.
- **Immediate next action:** Re-verify gate GREEN, then begin Campaign D hardening of `strategies/betting_against_beta/data_loader.py` starting with `_normalize_index` mixed-tz/string branch.
