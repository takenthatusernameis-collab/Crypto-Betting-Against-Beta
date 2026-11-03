# SINGLE DURABLE HANDOFF - Crypto-Betting-Against-Beta

## INITIAL TASK MESSAGE (for next agentic session - MUST EXECUTE FIRST)
**Time:** 2026-11-03T11:09:00Z
**Repo priority:** Crypto Betting Against Beta (BAB). ALL work must advance BAB under `strategies/betting_against_beta/`. Nothing else takes precedence. Repo name DEMANDS heavy implementation/hardening work on BAB - do not deviate.

**MANDATORY GATE (LAW):** Run `timeout 600 bash scripts/bab_gate.sh` IMMEDIATELY on session start. It MUST exit 0 (GREEN). If gate ever goes RED at any point, STOP ALL FEATURE WORK AND FIX IT BEFORE DOING ANYTHING ELSE. Gate runs ALL `tests/test_*.py` with coverage on `strategies/betting_against_beta/` (~1900 tests, ~3-4 min). Be patient - do not kill it early.

**GATE STATUS AT HANDOFF TIME:** PREVIOUSLY VERIFIED GREEN (1898 passed, 13 skipped). Re-verify on entry.

## BOTTLENECKS IDENTIFIED & REMOVAL INSTRUCTIONS
1. **Long gate runtime** - Expect 3-4 min. Use `timeout 600`. Do not interrupt. Treat completion as required verification.
2. **Workflow pattern drift** - `scripts/controller_progress.py` and `.github/workflows/main.yml` must stay in lockstep on exclusion patterns. If adding workflow files or changing scanner logic, sync both.
3. **Coverage blind spots** - `data_loader.py` is the largest unhardened surface (68%). Attack it systematically with concrete missing branches.
4. **Environment assumptions** - Deps (pandas, numpy, scipy, pytest, coverage) appear present. If import/syntax appears, fix immediately.

## CURRENT FOCUS CAMPAIGN (MAXIMUM AGGRESSION - HEAVY WORK REQUIRED)

### CAMPAIGN D - data_loader.py HARDENING (HIGHEST PRIORITY - DO NOT SKIP)
**Objective:** Bulletproof `strategies/betting_against_beta/data_loader.py` against adversarial inputs. Raise coverage from **68%** (499 missing stmts) toward **>=90%** without changing public APIs.

**Attack in this exact order (heavy implementation expected):**
1. `_normalize_index` (lines ~102-261) - numeric epochs (s/ms/us/ns), mixed tz, NaT, duplicates, elementwise coercion, fallbacks. Cover: 111, 119-123, 127-129, 133-135, 139-141, 145-150, 153-167, 174-175, 179-180, 193-213, 244-245, 255-256
2. `_coerce_to_datetime_scalar` (lines ~262-440) - all epoch magnitudes, strings, floats, NaN/inf, bad formats, naive/aware. Cover: 266, 272-274, 278, 289-290, 295-298, 300-303, 309-311, 316-326, 334-349, 352-353, 373-376, 378-381, 422-428, 446
3. `_coerce_series_to_datetime_index` (lines ~64-99) - finite checks, index promotion. Cover: 36, 39-41, 43-44, 54, 57-61, 66-99
4. `_detect_and_normalize_exchange_format` (lines ~443-645) - long/wide/OHLCV, pivot, column promotion, guards. Cover: 487-488, 506-515, 519, 521-522, 525-534, 542-543, 554, 568, 571-574, 578, 580-581, 587-590, 602, 612, 624-632, 638-639, 642-643
5. `_promote_datetime_column` (lines ~648-865) - guards, unnamed/object/epoch promotion. Cover: 656-662, 679-684, 689-690, 703-704, 722, 724-727, 730-731, 741-742, 745-746, 753, 764-802, 820-828, 831-832, 838-839, 850-864, 897
6. `_coerce_numeric` (lines ~1130-1165) - per-column coercion, BABDataError on garbage, second-pass. Cover: 908, 912, 916, 918, 920, 922, 926-927, 940, 952-953, 974-978, 999-1000, 1028-1029, 1041-1042, 1054, 1056, 1101, 1112-1113, 1124, 1126-1127, 1164-1165
7. `_run_data_quality_campaign` (lines ~1170-1285) - gaps/dupes/stale/min-finite/implausible. Cover: 1179, 1181, 1185-1188, 1191-1196, 1200-1205, 1226-1232, 1242-1243, 1245-1251, 1257-1258, 1263-1265, 1283-1284
8. `validate_returns_dataframe` (lines ~1289-1464) - structure/benchmark/min-history/JSON strictness. Cover: 1379-1380, 1392-1393, 1395, 1426, 1432-1436, 1438-1441, 1458-1459
9. Loaders (`load_returns_from_csv/parquet/hdf5/pickle/json/dataframe`) (lines ~1467-1689) - errors/orients/encodings/dtypes/empty/malformed. Cover: 1489, 1493-1497, 1523-1525, 1553-1555, 1577-1578
10. Prices path (`load_prices`, `_prices_to_returns`, `detect_price_or_returns`, `normalize_schema`) (lines ~1745-2056) - conversion/schema/multi-level. Cover: 1753, 1761-1762, 1777-1788, 1792-1798, 1802, 1852-1853, 1882-1883, 1911, 1914-1915, 1921, 1928-1930, 1985, 1987, 1989, 1996-1998, 2004-2010, 2020-2023, 2027-2028, 2033-2034, 2045-2049, 2051-2053
11. Aliases/utils (`standardize_columns`, `clean_data`, `validate_prices`, list_columns/iter_assets) (lines ~2065-2109). Cover: 2072, 2082, 2095, 2098-2099, 2101, 2107-2109

**Rules for D:** Do NOT change public APIs. Add guards/validation. All errors via `BABDataError` with clean messages. Handle NaN/inf explicitly everywhere. Weights must remain lagged by 1 day (lookahead forbidden). Every change must keep gate GREEN.

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

## PROGRESS SNAPSHOT (2026-11-03T11:09:00Z)
- Gate previously GREEN (1898 passed, 13 skipped). Must re-verify on entry.
- `data_loader.py`: 68% coverage (499 missing) - PRIMARY TARGET (Campaign D)
- `cli.py`: 61% coverage (124 missing) - Campaign C (queued)
- Other BAB modules >=89%; `quality.py`, `data_sources.py`, `errors.py`, `data.py`, `shorting.py`, `attribution.py` at 100%
- Bottlenecks: gate runtime long (use timeout 600), need aggressive hardening of data_loader
- Next action: verify gate GREEN, then attack `_normalize_index` and `_coerce_to_datetime_scalar` first.
