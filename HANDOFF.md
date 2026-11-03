# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T17:53:02Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` (~1944 tests, ~3 min). Be patient - do not kill it early.

**GATE STATUS AT HANDOFF TIME:** GREEN — 1944 passed, 13 skipped, exit 0 (~172s). All prior bottlenecks cleared; no session is blocked.

**BOTTLENECKS REMOVED (previous session):**
1. **PATTERN SYNC FIXED** - Added `*/.github/workflows/*` to the `stage_safe_changes` case in `.github/workflows/main.yml` (line ~1163, right after `.github/workflows/*`), matching `scripts/controller_progress.py` `EXCLUDE_PATTERNS`. Both `test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` now pass.
2. **`_promote_datetime_column` FIXED** - Rewrote the candidate-name promotion block in `strategies/betting_against_beta/data_loader.py` so clean date/timestamp columns promote to a `DatetimeIndex` (2-col D4 contract), unparseable values raise `BABDataError`, multi-column frames stay conservative (raw string index), and a patched/failing `set_index` keeps the column. Also guarded the last-resort loop against promoting columns containing NaT. All 6 prior gate failures (D4 `_promote_datetime_column` + pattern sync + campaign/precision-hit promotion edge cases) now pass.

**Working tree:** UNCOMMITTED. Modified: `.github/workflows/main.yml`, `strategies/betting_against_beta/data_loader.py`. Do not commit unless explicitly asked.

**HEAVY WORK MANDATE:** This repo is named "Crypto-Betting-Against-Beta". There is NO reason to do lightweight work. Campaign D must be driven to completion with ruthless coverage focus. If you find yourself "done" before hitting >=90% on `data_loader.py` with green gate, you have not looked hard enough.

## CURRENT FOCUS CAMPAIGN (GATE GREEN -> HEAVY WORK NOW)

### CAMPAIGN D - data_loader.py HARDENING (ACTIVE - HIGHEST PRIORITY NOW)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **68%** (506 missing stmts) toward **>=90%** without changing public APIs. This is the heavy work the repo name demands; future agents must not skip it.

**Coverage-driven attack order (execute in this exact sequence):**
1. `_normalize_index` - mixed-tz/string branches, dayfirst elementwise coercion, tz-convert fallbacks, fallback raise paths. Hunt untested exception branches.
2. `_coerce_to_datetime_scalar` - float/epoch branches, Timestamp passthrough, string parse fallbacks, BABDataError paths.
3. `_coerce_series_to_datetime_index` - NaT/inf/finite checks, index promotion, empty/degenerate series.
4. `_detect_and_normalize_exchange_format` - long/wide/OHLCV detection, pivot logic, column promotion, index handling, guards against malformed frames.
5. `_promote_datetime_column` - continue hardening (unnamed/object/epoch promotion, multi-col guards, NaT containing columns, set_index failure paths).
6. `_coerce_numeric` - per-column coercion, BABDataError on uncoercible garbage, second-pass logic, inf/NaN behavior.
7. `_run_data_quality_campaign` - gaps/dupes/stale/min-finite/implausible values, severity handling, campaign integration.
8. `validate_returns_dataframe` - structure validation, benchmark presence, min-history, JSON strictness, index/column edge cases.
9. Loaders (`load_returns_from_csv`, `load_returns_from_parquet`, `load_returns_from_hdf5`, `load_returns_from_pickle`, `load_returns_from_json`, `load_returns_from_dataframe`) - IO errors, encoding, dtypes, empty files, bad paths.
10. Prices path (`load_prices`, `_prices_to_returns`, `detect_price_or_returns`, `normalize_schema`) - price->returns math, alignment, dropna behavior, edge cases.
11. Aliases/utils (`standardize_columns`, `clean_data`, `validate_prices`, `list_columns`, `iter_assets`, helpers) - any remaining uncovered branches.

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
2. **Reconnaissance:** Read `strategies/betting_against_beta/data_loader.py` top-to-bottom. Identify the largest untested branches by mental coverage map. Start at `_normalize_index` as specified.
3. **Relentless hardening:** Attack in order. For each function, write mental adversarial cases, add guards if missing, add tests if coverage gaps are obvious.
4. **Gate discipline:** Run `timeout 600 bash scripts/bab_gate.sh` after EVERY meaningful change. If RED -> fix immediately before moving on.
5. **Sync workflows/controllers:** If touching workflows/controllers, sync patterns in BOTH `scripts/controller_progress.py` and `.github/workflows/main.yml`.
6. **Coverage tracking:** After significant chunks, check coverage mentally - push until >=90%. Do not stop early.
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

## PROGRESS SNAPSHOT (2026-11-03T17:53:02Z)
- **Gate:** GREEN (1944 passed, 13 skipped, exit 0, ~172s). Unblocked.
- **Working tree:** Modified (uncommitted): `.github/workflows/main.yml`, `strategies/betting_against_beta/data_loader.py`
- **Fixed previously:** pattern sync in `.github/workflows/main.yml` + alignment with `scripts/controller_progress.py`; `_promote_datetime_column` in `strategies/betting_against_beta/data_loader.py` (D4 + campaign/precision-hit edge cases).
- **data_loader.py:** 68% coverage (506 missing) - PRIMARY TARGET (Campaign D). **MUST push to >=90%**.
- **cli.py:** 61% coverage (124 missing) - Campaign C (queued).
- **Others:** Most BAB modules >=89-100%.
- **Immediate next action:** Re-verify gate GREEN, then begin Campaign D hardening starting with `_normalize_index` mixed-tz/string branch in `strategies/betting_against_beta/data_loader.py`.
