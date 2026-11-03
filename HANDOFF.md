# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T10:40:13Z | **Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation work on BAB - do not deviate.

**MANDATORY GATE:** Run `bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED, FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/`. Full suite is large (~1900 tests, ~3.5 min) - be patient.

## GATE STATUS AT HANDOFF TIME: GREEN (VERIFIED)
**Bottleneck cleared:** `*/.github/workflows/*` nested-variant pattern added to `.github/workflows/main.yml` case list (line 1163), in lock-step with `scripts/controller_progress.py:28` `EXCLUDE_PATTERNS`. Gate re-verified: `bash scripts/bab_gate.sh` → 1898 passed, 13 skipped, exit 0 (GREEN). No controller/infra failures remain.

## IMMEDIATE BOTTLENECKS TO CLEAR (if any block progress)
1. **Gate RED** - none currently (gate GREEN). If it turns RED, diagnose and fix before any feature work (see `main.yml:1163` pattern-sync rule).
2. **Test/runtime environment** - Deps confirmed available (pandas, numpy, scipy, pytest, coverage). No install needed.
3. **Any RED BAB tests** - None currently. Fix BAB failures first if they appear; do not add features until GREEN.
4. **Import/syntax errors** - Fix immediately.

## CURRENT FOCUS CAMPAIGN (MAXIMUM AGGRESSION - HEAVY WORK REQUIRED)

### Campaign D - Data loader & quality (HIGHEST PRIORITY - BIGGEST UNHARDENED SURFACE)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against every adversarial case.
**Coverage baseline:** `data_loader.py` = 1544 stmts, 499 missing, **68%** coverage (largest unhardened surface in the package). `quality.py` = 100%.
**Target:** Raise `data_loader.py` coverage toward 90%+ without changing public APIs.

**Hardening targets (attack systematically, each with concrete line ranges from the coverage missing report):**
1. `_normalize_index` - numeric epochs (s/ms/us/ns), mixed tz, NaT, duplicates, elementwise coercion, all fallbacks (lines ~102-261). Untested branches: 111, 119-123, 127-129, 133-135, 139-141, 145-150, 153-167, 174-175, 179-180, 193-213, 244-245, 255-256.
2. `_coerce_to_datetime_scalar` - all epoch magnitudes, strings, floats, NaN/inf, bad formats, timezone naive/aware (lines 262-440). Untested: 266, 272-274, 278, 289-290, 295-298, 300-303, 309-311, 316-326, 334-349, 352-353, 373-376, 378-381, 422-428, 446.
3. `_detect_and_normalize_exchange_format` - long/wide/OHLCV, date column detection, pivot paths, column promotion, guard logic (lines 443-645). Untested: 487-488, 506-515, 519, 521-522, 525-534, 542-543, 554, 568, 571-574, 578, 580-581, 587-590, 602, 612, 624-632, 638-639, 642-643.
4. `_promote_datetime_column` - column promotion guards, unnamed columns, last-resort object/epoch promotion (lines 648-865). Untested: 656-662, 679-684, 689-690, 703-704, 722, 724-727, 730-731, 741-742, 745-746, 753, 764-802, 820-828, 831-832, 838-839, 850-864, 897.
5. `_coerce_series_to_datetime_index` - finite-check fallbacks, index promotion (lines 64-99). Untested: 36, 39-41, 43-44, 54, 57-61, 66-99.
6. `_coerce_numeric` - per-column coercion, BABDataError on garbage, second-pass path (lines 1130-1165). Untested: 908, 912, 916, 918, 920, 922, 926-927, 940, 952-953, 974-978, 999-1000, 1028-1029, 1041-1042, 1054, 1056, 1101, 1112-1113, 1124, 1126-1127, 1164-1165.
7. `_run_data_quality_campaign` - gaps, duplicates, stale runs, min-finite-fraction, implausible returns (lines 1170-1285). Untested: 1179, 1181, 1185-1188, 1191-1196, 1200-1205, 1226-1232, 1242-1243, 1245-1251, 1257-1258, 1263-1265, 1283-1284.
8. `validate_returns_dataframe` - structural validation, benchmark coverage, min-history, JSON strictness (lines 1289-1464). Untested: 1379-1380, 1392-1393, 1395, 1426, 1432-1436, 1438-1441, 1458-1459.
9. Loaders `load_returns_from_csv/parquet/hdf5/pickle/json/dataframe` - file-not-found, empty/malformed, all orients, encodings, dtypes (lines 1467-1689). Untested: 1489, 1493-1497, 1523-1525, 1553-1555, 1577-1578.
10. `load_prices` / `_prices_to_returns` / `detect_price_or_returns` / `normalize_schema` - price→return conversion, schema heuristics, multi-level columns (lines 1745-2056). Untested: 1753, 1761-1762, 1777-1788, 1792-1798, 1802, 1852-1853, 1882-1883, 1911, 1914-1915, 1921, 1928-1930, 1985, 1987, 1989, 1996-1998, 2004-2010, 2020-2023, 2027-2028, 2033-2034, 2045-2049, 2051-2053.
11. `standardize_columns`, `clean_data`, `validate_prices`, list_columns/iter_assets aliases (lines 2065-2109). Untested: 2072, 2082, 2095, 2098-2099, 2101, 2107-2109.

**Hardening rule:** Do NOT change public APIs. Add guards, validation, edge case handling. Raise coverage toward 90%+. All errors via `BABDataError` with clean messages. Handle NaN/inf explicitly everywhere. Lookahead forbidden (weights lagged by 1 day).

### Campaign C - CLI/reporting (SECOND PRIORITY - QUEUED)
**Objective:** Make CLI and reporting bulletproof.
**Targets:** `cli.py` (61% coverage - 124 missing stmts), `scripts/bab_backtest_report.py` - adversarial args, `--dry-run`, `--output` path safety, JSON strictness, NaN/inf handling, error paths. Do NOT start until Campaign D is 90%+ and gate GREEN.

### Campaign B - Strategy/backtest/core (THIRD - MAINTAIN VIGILANCE)
**Objective:** Lookahead safety, finiteness, numerical stability. Audit divisions/log/sqrt/extreme values. `backtest.py` 80%, `beta.py` 92%, `strategy.py` 89%, `signals.py` 91%. Do NOT start until Campaigns D+C done and gate GREEN.

## EXECUTION PLAN (NON-NEGOTIABLE ORDER)
1. **Gate first:** `bash scripts/bab_gate.sh` → must be GREEN. If not, diagnose and fix before proceeding.
2. **Attack Campaign D aggressively:** Read `data_loader.py` thoroughly (esp. lines 102-865). Run data loader tests, find untested branches from the missing-line list above. Harden without changing public APIs.
3. **Gate after EVERY meaningful change:** Run gate frequently. NEVER checkpoint with RED gate.
4. **Heavy implementation:** Add guards, validation, edge case handling. This repo demands substantial hardening work.
5. **Update handoff if stopping:** If you must stop, update THIS file with exact progress, files modified, failing cases, next concrete steps (file:line), gate status.

## INVARIANTS (NEVER VIOLATE)
- **Repo priority:** Crypto Betting Against Beta. `strategies/betting_against_beta/` + tests FIRST.
- **Gate is law:** `bash scripts/bab_gate.sh` must exit 0 before ending session/checkpoint.
- **Full coverage:** Gate runs ALL `test_*.py` under `tests/`.
- **Lookahead forbidden:** Weights must be lagged by 1 day.
- **Finiteness required:** Handle NaN/inf explicitly.
- **No workflow changes** unless absolutely necessary to fix blocking gate issue.
- **Preserve API compatibility.**
- **Heavy work mandatory** given repo name.

## PROGRESS SNAPSHOT (2026-11-03T10:40:13Z)
- Gate bottleneck cleared: added `*/.github/workflows/*` to `.github/workflows/main.yml` case list (line 1163). Gate re-verified GREEN (1898 passed, 13 skipped, exit 0).
- `data_loader.py` coverage 68% (499 missing stmts) - Campaign D primary target. Concrete missing-line targets listed above.
- `cli.py` coverage 61% (124 missing stmts) - Campaign C, queued.
- All other BAB modules at 89%+ coverage; `quality.py`, `data_sources.py`, `errors.py`, `data.py`, `shorting.py`, `attribution.py` at 100%.
- Next session: confirm gate GREEN, then hammer Campaign D starting with `_normalize_index` (lines 102-261) and `_coerce_to_datetime_scalar` (lines 262-440).
