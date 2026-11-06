# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-06T03:04:12Z
**Repo:** `Crypto-Betting-Against-Beta` — `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `fdef573` (HEAD verified this session). **`git status --short`: clean** (Batches 14–19 in `tests/test_bab_data_loader_coverage_gaps.py` committed in `fdef573`/`47c9e2a` checkpoints). **No `.github/workflows/*` edits/commits/pushes. No remote push performed.**

**Non-negotiable priority (repo-name driven):** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors. No sidetracks. The repo name is the mission: every next session must do heavy BAB engineering, not coordination theater.

## Recon verified (2026-11-06T02:48:29Z, executed; recheck in Step 0)

- Env: Python 3.12.3, pytest 9.2.0, coverage 7.17.2. `PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`, `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`.
- **Controller blocker (NOT BAB; agent cannot clear):** `tests/test_controller_progress_accounting.py` workflow-sync fails because `.github/workflows/main.yml` is missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around on every run:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- Inspect-sensitive suites preserved: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. `_coerce_to_datetime_scalar` inspect/caller branches preserved.
- **Last completed BAB aggregate (2026-11-06T02:48:29Z):** `coverage erase && coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py` → **1000 passed, 16 skipped, 80 warnings, RC 0**. **+29 passed vs prior 971, zero regressions.**

## Coverage — last completed aggregate (2026-11-06T02:48:29Z)

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | **319** | **81%** | **≥90%** (Campaign A, **mandatory, heavy, immediate**) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (Campaign B, low priority; only after A has sustained measured-delta batching) |

**Campaign A status:** **IN PROGRESS, NOT reached.** **~229 statements** still needed (81%→90% over 1693). **Last net delta: 335→319 miss (-16, +1pp)** via Batches 17 (-5), 18 (-5), 19 (-6). Batches 14–16 had 0 miss reduction (keep, harmless). Source of truth: fresh `coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing` from Step 0.

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
| 1 | Workflow/controller exclude-pattern sync blocks un-ignored full green | **Operator with `workflows` scope** | Add `*/.github/workflows/*` in workflow file only. BAB agent cannot do this and must not stop for it. Route BAB runs with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green |
| 2 | `data_loader.py` **81% (319 miss / 1693 stmts)** — largest BAB risk/coverage surface; **real bottleneck** | **Next BAB agent (immediate, non-optional, heavy)** | **Test-first per batch, measured.** Target uncovered clusters from fresh `--show-missing`. A batch counts **only if fresh aggregate shows reduced miss count** (or proven unreachable evidence). Smallest correct fix only on proven contract violation. No broad refactor; never silent wrong success; preserve `BABDataError` contract and inspect-sensitive branches. **No comments in code.** Execute continuously: **≥3 verified batches with measured delta per session** unless blocked by proven unreachable branches (document evidence). | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB run with zero regressions |
| 3 | `cli.py` **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior. **Do not start until Campaign A has sustained measured-delta batching.** | Stable/no-regression; ≥85% |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-06T03:04:12Z, `main@fdef573`, tree clean. Last recon/aggregate (2026-11-06T02:48:29Z): inspect-sensitive `campaign_d*` = 44 passed/RC 0; BAB aggregate = 1000 passed/16 skipped/80 warnings/RC 0; `data_loader.py` = 81% (319 miss / 1693 stmts), `cli.py` = 81% (62 miss). Repo name = `Crypto-Betting-Against-Beta`; the only valid focus is BAB correctness, robustness, adversarial handling, and measured coverage. Read this handoff, run Step 0, then execute Campaign A immediately. No idling. No side quests. No infra/controller work. Stopping after <3 measured-delta batches is failure to follow handoff unless blocked by proven unreachable branches (document evidence). Do not claim completion until `data_loader.py` reaches ≥90% in a fresh completed aggregate BAB run with zero regressions and `BABDataError`/inspect-sensitive behavior preserved.**

## Non-negotiable operating rules

- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥3 verified batches with measured coverage delta** (more if stable). Each batch = tests added + focused run + `campaign_d*` guard + aggregate+coverage delta + recorded numbers. **A batch without a measured miss-count reduction is not progress.**
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

**Baseline (last fresh):** **81% (319 miss / 1693 stmts)**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Method:** extend `tests/test_bab_data_loader_coverage_gaps.py` (or add focused deterministic BAB test files only when necessary) with batch classes; **no comments in code**. Use `monkeypatch`/`tmp_path`/`pytest.importorskip`. Before writing a batch, identify **exact missing line numbers** to hit and verify after aggregate. After each batch: focused run, `campaign_d*` guard, aggregate+coverage, record numbers and **miss-count delta**.

**Concrete next targets (recheck Step 0 `--show-missing`; prioritize reachable clusters):**
1. **`_normalize_index` / early coercion branches (large):** 43-44, 84, 88-89, 92-93, 128-130, 134, 147-149, 153-155, 161, 171-176, 180, 188, 194, 196, 200-201, 213-214, 227-247, 258, 260, 268-269, 285-286, 289.
2. **`_coerce_to_datetime_scalar` deep paths:** 320-322, 326-328, 334-335, 338-342, 351-352, 368-372, 374-377, 381-382, 388-389, 395-396, 400-404, 479-483, 561, 564-565, 571, 582-586, 620, 623-624 (and nearby tail per fresh report).
3. **Exchange detect/normalize/pivot/OHLCV tails:** 664, 694-695, 708-714, 729-734, 757-758, 766-767, 770-771, 789-792, 804-805, 821-823, 832, 840-841, 859, 861-864, 867-868, 878-879, 882-883, 890, 894, 901-903, 908-914, 917-918, 953, 982-983 (re-verify).
4. **Promote/unnamed/last-resort remaining:** re-verify against fresh report.
5. **Loaders (CSV/JSON/JSONL/Parquet/HDF5/Pickle) + detect/dispatch/wrappers + schema/clean tails:** 1030-1034, 1055-1056, 1082-1090, 1097-1098, 1112, 1115, 1119-1122, 1139, 1147, 1163, 1174-1178, 1186, 1221-1222, 1226-1227, 1254-1258, 1293-1294, 1304-1305, 1312-1313, 1319-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1488, 1490, 1530-1531, 1533-1536, 1588-1592, 1620-1623, 1626-1627, 1649, 1659-1660, 1663-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1793, 1799-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1938, 1942, 1990, 1992-1993, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2163, 2167-2168, 2173-2174, 2187-2189, 2192-2193, 2238-2239, 2241, 2247-2248.

**Required cadence (non-optional):** complete **≥3 batches with measured miss-count reduction** next session (or document proven-unreachable evidence per blocked batch). Use targeted per-batch coverage to confirm lines hit before full aggregate. If a branch is genuinely unreachable without unsafe production changes, document evidence here and move on—do not fabricate coverage.

## Campaign B — `cli.py` (low priority)

Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. **Do not start until Campaign A has sustained measured-delta batching.**

## Campaign C — core engines (after A gains each batch)

`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: assert **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes. Do not displace Campaign A.

## Close-out (required before ending session)

- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker). Keep `campaign_d*` inspect-sensitive suites passing.
- **No GREEN claim without actual test output. No coverage claim without completed measurement and miss-count delta.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module (including miss-count before/after), commit/file-state notes (no false SHA claims), remaining blockers, and the next **concrete command + target files/lines/tests**.
- Ensure working tree state is accurately described; do not claim remote push/persistence.
- **Do not end the session early.** If coverage is still <90% and branches remain reachable, continue batching with measured deltas.

## Session state (this session)

- **Action taken:** Refreshed `HANDOFF.md` as the single durable handoff (git state aligned to `main@fdef573`, clean tree). No code/test changes. No `.github/workflows/*` changes. No remote push.
- **Verified now:** `main@fdef573`, `git status --short` clean (UTC 2026-11-06T02:49:30Z). Last measured coverage preserved from 2026-11-06T02:48:29Z.
- **Immediate next action (Batch 20, concrete):** In `tests/test_bab_data_loader_coverage_gaps.py`, add `TestBatch20NormalizeIndexEarlyBranches` targeting `data_loader.py` lines **43-44, 84, 88-89, 92-93, 128-130, 134, 147-149, 153-155, 161** (recheck Step 0 `--show-missing`). Force exception/fallback paths via unusual index types, `monkeypatch` on `pd.to_datetime`/index ops, tz-aware `DatetimeIndex` with failing `tz_convert`/`tz_localize`, empty/ambiguous inputs as appropriate to contract. Verify target lines hit: `python3 -m coverage run --source=strategies.betting_against_beta.data_loader -m pytest tests/test_bab_data_loader_coverage_gaps.py::TestBatch20NormalizeIndexEarlyBranches`. Run `campaign_d*` guard, then full aggregate from Step 0; **record miss-count delta**. Continue immediately to Batch 21/22 with measured deltas.
- **Campaign A remains mandatory/heavy until ≥90%.**

**Start at Step 0 now. Produce verified BAB progress (measured miss reduction), not narration.**
