# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T00:02:28Z (handoff reviewed this session; no new verification run)
**Repo:** `Crypto-Betting-Against-Beta` — `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `9696941` (HEAD verified). **Working tree:** clean at verification (`git status --short` empty). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

**Non-negotiable priority (repo-name driven):** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks.

## Recon verified (2026-11-05T23:21Z)

- Env: Python 3.12.3, pytest 9.2.0, coverage. `PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`, `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`.
- **Controller blocker (NOT BAB; agent cannot clear):** `tests/test_controller_progress_accounting.py` workflow-sync fails because `.github/workflows/main.yml` is missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- Inspect-sensitive suites preserved: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. `_coerce_to_datetime_scalar` inspect/caller branches preserved.
- Non-controller full gate (route-around): **3694 passed, 27 skipped, 192 warnings, 2 failed (controller-only), RC 1** when run without ignore; with `--ignore=tests/test_controller_progress_accounting.py` the BAB-relevant scope is green (matches prior verified state: 3628+ passed, 27 skipped, RC 0 on non-controller set).
- **Fresh BAB aggregate (completed 2026-11-05T23:20Z):** `coverage erase && coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py` → **918 passed, 15 skipped, 66 warnings, RC 0** (31.42s).

## Coverage — fresh completed aggregate (2026-11-05T23:20Z)

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 353 | **79%** | **≥90%** (Campaign A, **mandatory, heavy**) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (Campaign B, low priority) |

**Campaign A status:** **NOT reached.** **~184 statements** still needed (79%→90% over 1693). Source of truth: `coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing` from the fresh aggregate.

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
| 2 | `data_loader.py` **79% (353 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (immediate, non-optional, heavy)** | **Test-first per batch.** Target uncovered clusters from fresh `--show-missing`. Smallest correct fix only on proven contract violation. No broad refactor; never silent wrong success; preserve `BABDataError` contract and inspect-sensitive branches. **No comments in code.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB run with zero regressions |
| 3 | `cli.py` **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T23:21Z, `main@9696941`, clean tree. BAB aggregate: 918 passed/15 skipped/66 warnings, RC 0. `data_loader.py` 79% (353 miss / 1693 stmts), `cli.py` 81% (62 miss). Inspect-sensitive `campaign_d*` (44 tests) green.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage. **Read this handoff, run Step 0, then execute Campaign A immediately. Do not idle. Do not stop after one small patch. Do not claim completion until Campaign A reaches ≥90% in a fresh completed aggregate run.**

## Non-negotiable operating rules

- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥3 verified batches** (more if stable). Each batch = tests added + focused run + `campaign_d*` guard + aggregate+coverage delta + recorded numbers. **Stopping after 1 batch is failure to follow handoff unless blocked by a proven unreachable branch (document evidence).**
- **No workflow/infra changes.** Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- **Production code secondary.** Keep unchanged unless a **tested contract violation** requires the **smallest correct fix**. Never silent wrong success. Preserve `BABDataError` semantics and public APIs.
- **Preserve inspect-sensitive behavior.** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- **No narration-as-progress.** No GREEN/coverage claim without actual command output captured.

## Step 0 — Recon (run to completion; record truth)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py 2>&1 | tail -2
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_data_loader_miss_fill.py \
  tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -2
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)

**Baseline (fresh):** **79% (353 miss / 1693 stmts)**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Method:** extend `tests/test_bab_data_loader_coverage_gaps.py` (or add focused deterministic BAB test files only when necessary) with batch classes; **no comments in code**. Use `monkeypatch`/`tmp_path`/`pytest.importorskip`. After each batch: focused run, `campaign_d*` guard, aggregate+coverage, record numbers.

**Concrete next targets (start here, recheck Step 0 `--show-missing`):**
1. **Coerce/epoch/inspect-adjacent fallbacks (careful — preserve campaign_d):** 40-44, 60-61, 84, 86-89, 92-93, 110-111, 128-130, 134, 147-149, 153-155, 161, 171-176, 180, 188, 194, 196, 200-201, 208-209, 213-214, 227-247, 258, 260, 268-269, 285-286, 289, 296-297.
2. **Index/normalize/datetime promotion:** 320-322, 326-328, 334-335, 338-342, 351-352, 368-372, 374-377, 381-382, 388-389, 395-396, 400-404, 479-483, 561, 564-565, 571, 582-586, 620, 623-626, 630, 632-633, 641-642.
3. **Exchange detect/normalize/pivot/OHLCV tails:** 664, 676-684, 694-695, 708-714, 729-734, 757-758, 766-767, 770-771, 789-792, 804-805, 821-823, 832, 840-841, 859, 861-864, 867-868, 878-879, 882-883, 890, 894, 901-903, 908-914, 917-918, 953, 982-983.
4. **Loaders (CSV/JSON/JSONL/Parquet/HDF5/Pickle) + detect/dispatch/wrappers:** 1030-1034, 1055-1056, 1082-1085, 1088-1090, 1097-1098, 1112, 1115, 1119-1122, 1139, 1147, 1163, 1174-1175, 1177-1178, 1186, 1188-1189, 1198, 1202, 1207, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1612, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942.
5. **Schema/clean/validate/standardize/utility tails:** 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248.

**Required cadence (non-optional):** complete **≥3 batches** next session, measuring after each. If a branch is genuinely unreachable without unsafe production changes, document evidence here and move on—do not fabricate coverage.

## Campaign B — `cli.py` (low priority)

Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. **Do not start until Campaign A has delivered ≥3 measured batches.**

## Campaign C — core engines (after A gains each batch)

`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: assert **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes. Do not displace Campaign A.

## Close-out (required before ending session)

- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker). Keep `campaign_d*` inspect-sensitive suites passing.
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commit/file-state notes (no false SHA claims), remaining blockers, and the next **concrete command + target files/lines/tests**.
- If changes are made, ensure working tree state is accurately described; do not claim remote push/persistence.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
