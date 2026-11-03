# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T12:19:21Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` (coverage on `strategies/betting_against_beta/` ~1900 tests, ~3-4 min). Be patient - do not kill it early.

**GATE STATUS AT HANDOFF TIME:** GREEN (exit 0) — 1898 passed, 13 skipped, 210.62s. Verified with `timeout 600 bash scripts/bab_gate.sh`.

**BOTTLENECK REMOVED THIS SESSION:** Workflow pattern drift was the RED blocker. `*/.github/workflows/*` was missing from the bash `stage_safe_changes` case in `.github/workflows/main.yml` (line 1163), failing `test_python_patterns_are_subset_of_workflow` + `test_nested_workflow_pattern_is_present_in_workflow`. Added `*/.github/workflows/*` right after `.github/workflows/*` at `main.yml:1163`. Pattern-sync tests now 4/4 pass. Gate re-ran GREEN.
NOTE: workflow fix APPLIED this session (`*/.github/workflows/*` now present at main.yml:1163). Working tree uncommitted — do not commit unless explicitly asked. Confirm present before trusting gate.

## BOTTLENECKS IDENTIFIED & REMOVAL INSTRUCTIONS
1. **Long gate runtime** - Expect 3-4 min. Use `timeout 600`. Do not interrupt. Treat completion as required verification.
2. **Workflow pattern drift** - `scripts/controller_progress.py` and `.github/workflows/main.yml` must stay in lockstep on exclusion patterns. If adding workflow files or changing scanner logic, sync both.
3. **Coverage blind spots** - `data_loader.py` is the largest unhardened surface (68%). Attack it systematically with concrete missing branches.
4. **Environment assumptions** - Deps (pandas, numpy, scipy, pytest, coverage) appear present. If import/syntax appears, fix immediately.

## CURRENT FOCUS CAMPAIGN (MAXIMUM AGGRESSION - HEAVY WORK REQUIRED)

### CAMPAIGN D - data_loader.py HARDENING (HIGHEST PRIORITY - DO NOT SKIP)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **66%** (540 missing stmts) toward **>=90%** without changing public APIs.

**Status this session:** Added `tests/test_bab_data_loader_campaign_d.py` (25 tests) covering `_normalize_index` numeric-epoch index branches (empty, ns/us/ms/s/small/negative) and `_coerce_to_datetime_scalar` (None, float nan/inf, pd.NaT, empty/nan/null strings, numeric-string epochs of every magnitude, int epochs, tz-aware Timestamp, ISO `...Z`). All 25 pass. These clusters are now exercised.

**Attack remaining in this exact order (heavy implementation expected):**
1. `_normalize_index` mixed-tz/string branch (lines ~182-261) - dayfirst elementwise (207-227), fallback raise (228-238), tz-convert fallbacks (250-257).
2. `_coerce_to_datetime_scalar` remaining float branch (lines ~428-465) and Timestamp/fallback paths (467-488).
3. `_coerce_series_to_datetime_index` (lines ~64-99) - finite checks, index promotion. Cover: 36, 39-41, 43-44, 54, 57-61, 66-99
4. `_detect_and_normalize_exchange_format` (lines ~443-645) - long/wide/OHLCV, pivot, column promotion, guards.
5. `_promote_datetime_column` (lines ~648-865) - guards, unnamed/object/epoch promotion.
6. `_coerce_numeric` (lines ~1130-1165) - per-column coercion, BABDataError on garbage, second-pass.
7. `_run_data_quality_campaign` (lines ~1170-1285) - gaps/dupes/stale/min-finite/implausible.
8. `validate_returns_dataframe` (lines ~1289-1464) - structure/benchmark/min-history/JSON strictness.
9. Loaders (`load_returns_from_csv/parquet/hdf5/pickle/json/dataframe`) (lines ~1467-1689).
10. Prices path (`load_prices`, `_prices_to_returns`, `detect_price_or_returns`, `normalize_schema`) (lines ~1745-2056).
11. Aliases/utils (`standardize_columns`, `clean_data`, `validate_prices`, list_columns/iter_assets) (lines ~2065-2109).

**Rules for D:** Do NOT change public APIs. Add guards/validation. All errors via `BABDataError` with clean messages. Handle NaN/inf explicitly everywhere. Weights must remain lagged by 1 day (lookahead forbidden). Every change must keep gate GREEN. Add one test file per cluster; run the FULL gate after every meaningful change.

### CAMPAIGN C - CLI/REPORTING (QUEUED - DO NOT START UNTIL D >=90% AND GATE GREEN)
Targets: `cli.py` (61%, 124 missing), `scripts/bab_backtest_report.py`. Harden adversarial args, `--dry-run`, `--output` path safety, JSON strictness, NaN/inf, error paths.

### CAMPAIGN B - CORE/BACKTEST/STRATEGY (MAINTAIN VIGILANCE)
Targets: lookahead safety, finiteness, numerical stability. Watch `backtest.py`, `beta.py`, `strategy.py`, `signals.py`. Only expand if regressions appear or D+C complete and gate GREEN.

## EXECUTION PLAN (NON-NEGOTIABLE)
1. **Entry gate:** `timeout 600 bash scripts/bab_gate.sh` -> GREEN.
2. **Recon:** Read `strategies/betting_against_beta/data_loader.py` top-to-bottom with focus on sections above. Run focused tests for data_loader if helpful, but gate is required.
3. **Hammer D:** Attack missing branches one cluster at a time. Add minimal, correct guards/tests via implementation hardening. Keep APIs identical.
4. **Verify constantly:** Run gate after EVERY meaningful change. NEVER checkpoint with RED. If slow, wait for completion.
5. **Escalate only if blocked:** If a fix requires touching workflows/controllers, sync patterns in both places or explain in handoff update.
6. **Handoff on stop:** If you must stop, UPDATE THIS FILE with timestamp, files modified, exact failing cases (if any), next concrete steps with file:line, and current gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** BAB under `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full suite:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights lagged by 1 day.
- **Finiteness:** Handle NaN/inf explicitly.
- **API compatibility:** No breaking public API changes.
- **No unnecessary workflow changes:** Only if required to fix blocking gate issue.
- **Heavy work mandatory:** Given repo name "Crypto-Betting-Against-Beta", substantial hardening is required.

## PROGRESS SNAPSHOT (2026-11-03T12:19:21Z)
- Gate GREEN: 1898 passed, 13 skipped, exit 0 (210.62s). Bottleneck (workflow `*/.github/workflows/*` pattern) REMOVED at `main.yml:1163` — now actually applied (was claimed but missing). Working tree only, NOT committed.
- `data_loader.py`: 66% coverage (540 missing) - PRIMARY TARGET (Campaign D). `_normalize_index` numeric epochs + `_coerce_to_datetime_scalar` clusters now covered via new `tests/test_bab_data_loader_campaign_d.py` (25 tests, all pass).
- `cli.py`: 61% coverage (124 missing) - Campaign C (queued, do not start until D >=90% and gate GREEN).
- Other BAB modules >=89%; `quality.py`, `data_sources.py`, `errors.py`, `data.py`, `shorting.py`, `attribution.py` at 100%.
- Bottlenecks: gate runtime long (~3.5 min, use timeout 600); data_loader is largest unhardened surface.
- Next action: run full gate to confirm GREEN, then continue Campaign D at `_normalize_index` mixed-tz/string branch (`data_loader.py:182-261`) and `_coerce_to_datetime_scalar` float/Timestamp fallbacks (`data_loader.py:428-488`).
