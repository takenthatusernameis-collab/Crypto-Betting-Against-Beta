# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T21:22:00Z (durable refresh, recon verified this session)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `aa67706` (local HEAD; clean working tree at recon time).
**Working tree (this session):** no production code changes; `HANDOFF.md` updated only. **No `.github/workflows/*` edits/commits/pushes.**

**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Recon verified (2026-11-05T21:22Z)

- Env: Python 3.12.3, pytest 9.2.2, coverage. PATH/PYTHONPATH set to include `$PWD` and `/home/runner/work/_temp/kilo-home/.local/...`.
- **Controller blocker (NOT BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py` workflow-sync fails because `.github/workflows/main.yml` excludes are missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around for BAB work:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- Inspect-sensitive suites preserved (fresh): `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. `_coerce_to_datetime_scalar` inspect/caller branches preserved.
- Fresh bounded BAB aggregate (completed): **794 passed, 11 skipped, 57 warnings, RC 0** (command in Step 0 below).

## Coverage — fresh completed aggregate (2026-11-05T21:22Z, bounded BAB set)

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 364 | **78%** | **≥90%** (Campaign A, mandatory, heavy) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (low priority) |

**Campaign A status:** NOT reached. Need ~**195** more covered statements on remaining misses (source of truth: `coverage report --show-missing` from Step 0).

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- **Inspect-sensitive behavior preserved:** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**

## Bottlenecks (remove / route around)

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks un-ignored full green | **Operator with `workflows` scope** | Add `*/.github/workflows/*` pattern in workflow file only. Route BAB runs with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green |
| 2 | `data_loader.py` **78% (364 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate, non-optional)** | **Test-first per batch.** Target uncovered clusters from fresh `--show-missing`. Smallest correct fix only on proven contract violation. No broad refactor; never silent wrong success; preserve `BABDataError` contract and inspect-sensitive branches. No comments in code. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB run with zero regressions |
| 3 | `cli.py` — **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T21:22Z, `main@aa67706`. Bounded aggregate: 794 passed/11 skipped. `data_loader.py` 78% (364 miss / 1693 stmts).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage. **Read this handoff, run Step 0, then execute Campaign A immediately. Do not idle. Do not stop after one small patch. Do not claim completion until Campaign A reaches ≥90% in a fresh completed aggregate run.**

## Non-negotiable operating rules

- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥3 verified batches** (more if stable). Each batch = tests added + focused run + aggregate+coverage delta + recorded numbers.
- **No workflow/infra changes.** Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`.
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
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -2
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)

**Baseline (fresh):** **78% (364 miss / 1693 stmts)**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Method:** extend `tests/test_bab_data_loader_coverage_gaps.py` (or add focused deterministic BAB test files only when necessary) with batch classes; no comments. Use `monkeypatch`/`tmp_path`/`pytest.importorskip`. After each batch: focused run, aggregate+coverage, `campaign_d*` spot-check.

**Concrete missing-line clusters to attack (verified 2026-11-05T21:22Z; recheck Step 0 before coding):**
- **Coerce/epoch/inspect-adjacent fallbacks (careful — preserve campaign_d):** 40-44, 60-61, 84, 86-89, 92-93, 110-111, 128-130, 134, 141-155, 161, 171-176, 180, 188, 194, 196, 200-214, 227-247, 258, 260, 268-269, 285-289, 296-297.
- **Index/normalize/datetime promotion:** 320-342, 351-352, 368-404, 479-483, 561, 564-565, 571, 582-586, 620, 623-633, 641-642.
- **Exchange detect/normalize/pivot/OHLCV tails:** 664, 676-695, 708-714, 729-734, 757-771, 789-792, 804-805, 821-823, 832, 840-841, 859-868, 878-883, 890, 894, 901-918, 953, 982-983.
- **Loaders (CSV/JSON/JSONL/Parquet/HDF5/Pickle) + detect/dispatch/wrappers:** 1030-1034, 1055-1056, 1082-1090, 1097-1098, 1110-1126, 1139, 1147, 1153-1154, 1163, 1174-1178, 1186-1189, 1198, 1202, 1207, 1221-1227, 1254-1258, 1293-1294, 1304-1320, 1345-1346, 1418-1419, 1443-1444, 1451-1452, 1474-1475, 1487-1490, 1530-1539, 1588-1592, 1612, 1620-1627, 1649, 1659-1664, 1686-1687, 1698-1699, 1757, 1764-1765, 1782-1783, 1792-1806, 1825-1826, 1869-1870, 1895, 1926-1929, 1937-1942.
- **Schema/clean/validate/standardize/utility tails:** 1990-1993, 2010, 2022-2023, 2054-2055, 2061, 2068, 2087-2092, 2137-2138, 2160-2174, 2187-2193, 2238-2241, 2247-2248.

**Required cadence (non-optional):** complete **≥3 batches** next session, measuring after each. If a branch is genuinely unreachable without unsafe production changes, document evidence here and move on—do not fabricate coverage.

## Campaign B — `cli.py` (low priority)

Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. Do not start until Campaign A has delivered ≥3 measured batches.

## Campaign C — core engines (after A gains each batch)

`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: assert **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes. Do not displace Campaign A.

## Close-out (required before ending session)

- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker). Keep `campaign_d*` inspect-sensitive suites passing.
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commit/file-state notes (no false SHA claims), remaining blockers, and the next **concrete command + target files/lines/tests**.
- If changes are made, ensure working tree state is accurately described; do not claim remote push/persistence.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
