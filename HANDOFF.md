# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T04:52:52Z (verified by fresh recon)
**Repo:** `Crypto-Betting-Against-Beta` — `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `3ad0021` (verified). **Tree state now:** **clean** (Batches 25–27 committed in checkpoint `3ad0021`). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

**Non-negotiable priority (repo-name driven):** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks.

## Recon verified (2026-11-06T04:52:32Z, executed)

- Env: Python 3.12.3, pytest 9.2.0, coverage 7.17.2. `PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`, `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`.
- **Controller blocker (NOT BAB; agent cannot clear):** `tests/test_controller_progress_accounting.py` workflow-sync fails because `.github/workflows/main.yml` is missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around on every run:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- Inspect-sensitive suites preserved: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0** (verified after every batch).

## Coverage — Step 0 aggregate (2026-11-06T04:52:52Z, fresh completed aggregate)

Command (aggregate): `coverage erase && coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py`

**Result:** **1127 passed, 16 skipped, 84 warnings, RC 0**.

| Module | Stmts | Miss (before) | Miss (after) | Cover | Delta |
|---|---:|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 276 (84%) | **243** | **86%** | **-33 miss** |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | 62 | **81%** | 0 |

**Campaign A status:** **IN PROGRESS, NOT reached.** **~74 statements** still needed (243 miss vs ≤169 for ≥90%). Source of truth: fresh `coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing`.

## This session — verified batches (measured deltas)

All batches added to `tests/test_bab_data_loader_coverage_gaps.py` (dirty/uncommitted). Each batch: focused tests passed, `campaign_d*` guard passed, full Step 0 aggregate green, coverage measured.

| Batch | Focus | Focused tests | Aggregate (after batch 27 final) | Measured miss delta (aggregate context) |
|---|---|---:|---|---|
| 25 `TestBatch25ExchangeDetectPivotOhlcvTails` | `_detect_and_normalize_exchange_format` long/pivot tz-cleanup + parse-failure tails (targets incl. 561, 564-565, 571, 582-586, 620, 623-624, 630, 641-642, 676-684, 694-695, 708-714) | 8 passed | — | contributed to total -33 |
| 26 `TestBatch26PromoteExchangeAndOhlcvResiduals` | exchange/pivot/OHLCV/promote datetime residuals (targets incl. 733-734, 757-758, 766-771, 789-792, 804-805, 821-823, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 982-983) | 14 passed | — | contributed; aggregate reached 85%/262 miss after batch 26 |
| 27 `TestBatch27NormalizeParseCoerceDropResiduals` | `_normalize_columns`/`_drop_all_nan_columns`/`_strip_units_and_parse`/`_series_is_parseable`/`_coerce_numeric` residuals (1030-1034, 1055-1056, 1082-1090, 1097-1098, 1112-1122, 1139, 1147, 1163, 1174-1178, 1186, 1221-1222, 1226-1227) | 14 passed | **1127 passed, 16 skipped** | **262 → 243 miss (-19 in batch 27 step; -33 total vs session start)** |

**Verified guards:** `campaign_d/d2/d3` = **44 passed, 5 warnings, RC 0** after each batch and at close. **No production code changed.** `BABDataError` semantics/public APIs preserved.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**

## Bottlenecks — route around / remove

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks un-ignored full green | **Operator with `workflows` scope** | Add `*/.github/workflows/*` in workflow file only. Route BAB runs with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green |
| 2 | `data_loader.py` **86% (243 miss / 1693 stmts)** — Campaign A still mandatory | **Next BAB agent (immediate, non-optional, heavy)** | **Test-first per batch, measured.** Target uncovered clusters from fresh `--show-missing`. A batch counts **only if fresh aggregate shows reduced miss count** (or proven unreachable evidence). Smallest correct fix only on proven contract violation. Preserve `BABDataError` contract and inspect-sensitive branches. **No comments in code.** Execute continuously: **≥3 verified batches with measured delta per session** unless blocked by proven unreachable branches (document evidence). | Measured `data_loader.py` **≥90%** (≤169 miss) in a **fresh completed aggregate** BAB run with zero regressions |
| 3 | `cli.py` **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior. **Do not start until Campaign A has sustained measured-delta batching.** | Stable/no-regression; ≥85% |

## Current missing clusters (fresh `--show-missing`, 2026-11-06T04:52:32Z)

`data_loader.py` missing: `43-44, 84, 92-93, 128-130, 134, 147-149, 194, 196, 213-214, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 482-483, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 821-823, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 982-983, 1082-1085, 1088-1090, 1112, 1115, 1119-1122, 1139, 1147, 1163, 1174-1175, 1177-1178, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.

**Priority next (Campaign A, heavy):**
1. **Batch 28 — load/dispatch/schema/clean tails:** target `1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699` (recheck Step 0). Use `tmp_path`, malformed/ext/encoding/loader dispatch, `pytest.importorskip` only for optional deps.
2. **Batch 29 — returns/clean/pct_change/missing-fill/outlier tails:** `1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.
3. **Batch 30+ — early/scalar/normalize residuals:** `43-44, 84, 92-93, 128-130, 134, 147-149, 194, 196, 213-214, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 482-483, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 821-823, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 982-983` (inspect-sensitive/monkeypatch-heavy; preserve `campaign_d*`).

## Immediate next action (concrete)

**Start at Step 0 now.** Then implement **Batch 28** in `tests/test_bab_data_loader_coverage_gaps.py` (class `TestBatch28LoadDispatchSchemaCleanTails`) targeting the Batch 28 line cluster above (recheck fresh `--show-missing` first). After Batch 28: focused run, `campaign_d*` guard, full Step 0 aggregate, record miss-count delta. Continue immediately to Batch 29/30 with measured deltas. **≥3 verified batches with measured delta required unless proven unreachable (document evidence).**

Verify pattern:
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m pytest -q --tb=short tests/test_bab_data_loader_coverage_gaps.py::TestBatch28LoadDispatchSchemaCleanTails
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing
```

**Campaign A remains mandatory/heavy until `data_loader.py` ≥90% (≤169 miss) in a fresh completed aggregate with zero regressions. Do not end early.**
