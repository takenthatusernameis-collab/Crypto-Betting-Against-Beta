# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T05:54:40Z
**Repo:** `Crypto-Betting-Against-Beta`
**Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA at handoff:** `main` @ `1c441d3` (verify: `git rev-parse --short HEAD`). Working tree clean. **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

## Priority (repo-name-driven, non-negotiable)
Repo name is **Crypto-Betting-Against-Beta** → **BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. Until Campaign A is complete, every session must produce **measured `data_loader.py` miss-count reduction** (or documented unreachable-branch proof while still moving).

## Verified state (2026-11-06T05:53Z)
- **Env:** Python 3.12.3, pytest 9.2.0, coverage 7.17.2.
  - `export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`
  - `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`
- **`campaign_d*` guards (inspect-sensitive):** `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**.
- **Fresh Step 0 aggregate (completed 2026-11-06T05:54Z, 1127 passed / 16 skipped / 84 warnings):**
  - `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 243 miss, 86%** (gap to ≥90%: **74 stmts**, target **≤169 miss**).
  - `strategies/betting_against_beta/cli.py` — **319 stmts, 62 miss, 81%** (defer until Campaign A sustains measured deltas).
  - Source of truth: rerun Step 0 fresh before coding and after **every** batch; use `coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing`.
- **Test layout:** BAB tests under `tests/test_bab_*` and `tests/test_betting_against_beta_*`; coverage-gaps suite ends at `TestBatch27NormalizeParseCoerceDropResiduals` (`tests/test_bab_data_loader_coverage_gaps.py:7077`). Next new batch is **`TestBatch28`**.

## Bottlenecks (and route-around)
| # | Bottleneck | Owner | Route-around / action | Exit |
|---|------------|-------|-----------------------|------|
| 1 | **Controller workflow-sync test fails (not agent-clearable):** `pytest -q tests/test_controller_progress_accounting.py` → `TestStageSafeChangesPatternSync::test_nested_workflow_pattern_is_present_in_workflow` fails because `.github/workflows/main.yml` omits `*/.github/workflows/*` while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes it. **Agent cannot modify workflows.** | **Operator with `workflows` scope only** | **Never edit/commit/push `.github/workflows/*`.** Always run BAB gates with `--ignore=tests/test_controller_progress_accounting.py`. Do not spend BAB time on this. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green. |
| 2 | **`data_loader.py` 86% (243 miss) — Campaign A mandatory, heavy, cannot be deferred.** | **Next BAB agent (immediate)** | Test-first batches in `tests/test_bab_data_loader_coverage_gaps.py` (`TestBatch28+`). A batch counts **only** with **fresh aggregate measured miss-count delta** (or documented unreachable-branch proof). Smallest correct fix only for proven contract violations. Preserve `BABDataError` contract and inspect-sensitive branches (`_coerce_to_datetime_scalar` / campaign_d semantics). **No comments in code.** **Deliver ≥3 verified batches with measured delta this session** unless blocked by proven unreachable branches (document file/line evidence and keep moving). **Do not end early.** Heavy work is the session; there is no lighter track. | Fresh completed aggregate shows `data_loader.py` **≥90% (≤169 miss)**, zero regressions, `campaign_d*` green. |
| 3 | `cli.py` 81% | Later BAB agent | Safe deterministic tests only if touching CLI; no CLI work before sustained Campaign A measured-delta batching. | Stable/no-regression; ≥85%. |

## Current `data_loader.py` missing clusters (Step 0, 2026-11-06T05:52Z — recheck fresh)
`43-44, 84, 92-93, 128-130, 134, 147-149, 194, 196, 213-214, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 400, 403-404, 482-483, 561, 620, 641-642, 676-684, 694-695, 708-714, 733-734, 757-758, 766-767, 770-771, 789-792, 804-805, 840-841, 859, 861-864, 867-868, 890, 894, 901-903, 908-914, 953, 982-983, 1033-1034, 1084-1085, 1097-1098, 1112, 1115, 1174-1175, 1186, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248`.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (execute immediately)
**Mission (single focus): Campaign A — drive `data_loader.py` to ≥90% (≤169 miss) with measured, verified batches. Heavy work required; no deferral. This is the only track.**

1. **Step 0 (mandatory, fresh):** run the aggregate coverage command, record `data_loader.py` miss/stmts/% and `cli.py`, and recheck missing clusters with `--show-missing`. Do not reuse stale numbers.
2. **Batch 28:** add `TestBatch28*` in `tests/test_bab_data_loader_coverage_gaps.py` targeting reachable lines from the **rechecked** missing list (prior candidates: loader/dispatch/validation tails around `1254-1258,1293-1294,1304-1305,1312-1313,1319-1320,1345-1346,1418-1419,1443-1444,1451-1452,1474-1475,1487-1488,1490,1530-1531,1533-1536,1588-1592,1620-1623,1626-1627,1649,1659-1660,1663-1664,1686-1687,1698-1699` — confirm still missing). Use `tmp_path`, malformed/ext/encoding/dispatch cases; `pytest.importorskip` only for optional deps. Exercise public/API and reachable internal paths; preserve behavior and `BABDataError` semantics.
3. **After each batch:** focused batch run → `campaign_d*` guard run → **full Step 0 aggregate** → record miss-count delta. **No delta = batch does not count.**
4. **Continue without stopping:** Batch 29, 30, … (returns/clean/pct-change/missing-fill/outlier/normalize/index/scalar/monkeypatch/inspect-sensitive residuals while preserving `campaign_d*`). Deliver **≥3 verified batches with measured delta** this session unless a cluster is proven unreachable (document file/line evidence and keep moving). There is no off-ramp other than ≥90% or documented unreachable proof.
5. **End condition:** Campaign A reaches `data_loader.py` ≥90% in a fresh completed aggregate with zero regressions and `campaign_d*` green, **or** reachable clusters exhausted with documented proof. **Do not declare done early.** Do not pivot to cli.py or any other module until Campaign A end condition is met.

## Verification commands
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages

# Step 0 aggregate (fresh baseline / after each batch)
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing

# campaign_d* guard (after every batch)
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

## Sacred invariants (never regress)
- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) passing.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**
