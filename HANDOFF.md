# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T21:06:07Z (durable refresh)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `145b771` (`chore(kilo): checkpoint agent session`).
**Working tree:** clean (`git status --short` empty). **No `.github/workflows/*` edits/commits/pushes.**

**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Recon verified (2026-11-05T21:06Z)

- Env: Python 3.12.3, pytest 9.0.2/9.2.x available, coverage. **3540 tests collected** (full tree).
- Full suite (route around controller blocker): `3513 passed, 25 skipped, 184 warnings, 2 failed` (RC 1) — the **only 2 failures** are the known infra/controller workflow-sync tests in `tests/test_controller_progress_accounting.py` (see Bottleneck #1). **All BAB/strategy/infra-other tests pass under the ignore route.**
- Inspect-sensitive suites preserved: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. **`_coerce_to_datetime_scalar` inspect/caller branches preserved.**
- BAB handoff aggregate (last completed measurement recorded in-session at 20:54Z; re-run Step 0 before new claims): **691 passed, 11 skipped, 53 warnings, RC 0** for the bounded BAB set below.

## Verified state

- **Infra blocker (NOT BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync::{test_python_patterns_are_subset_of_workflow,test_nested_workflow_pattern_is_present_in_workflow}` fail because `.github/workflows/main.yml` `stage_safe_changes`/related exclusions are missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around for agents:** `--ignore=tests/test_controller_progress_accounting.py`. **Never edit/commit/push `.github/workflows/*`.**
- **Coverage — last completed aggregate (2026-11-05T20:54Z, `coverage run`):**

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 378 | **78%** | **≥90%** (Campaign A, mandatory, heavy) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (low priority) |
| **Measured slice total** | 2012 | 440 | **78%** | **≥85%** |

- **Coverage command (bounded):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing
```

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
| 1 | Workflow/controller exclude-pattern sync blocks un-ignored full green | **Operator with `workflows` scope** | Add `*/.github/workflows/*` pattern in workflow file only. Agents lacking permission must not touch `.github/workflows/*`. Route BAB verification with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green |
| 2 | `data_loader.py` **78% (378 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate, non-optional)** | **Test-first per batch.** Target uncovered clusters with `monkeypatch`/`tmp_path`/optional-dep skips. Smallest correct fix only on proven contract violation. No broad refactor; never silent wrong success; preserve `BABDataError` contract. Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`. No comments in code. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions |
| 3 | `cli.py` — **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T21:06Z, `main@145b771`, clean tree. Last completed bounded BAB aggregate: 691 passed/11 skipped; `data_loader.py` 78% (378 miss / 1693 stmts).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage. **Read this handoff, run Step 0, then execute Campaign A immediately. Do not idle. Do not stop after one small patch. Do not claim completion until Campaign A reaches ≥90% in a fresh completed aggregate run.**

## Non-negotiable operating rules

- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥3 verified batches** (more if stable). Each batch = tests + focused run + aggregate+coverage delta + recorded numbers.
- **No workflow/infra changes.** Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`.
- **Production code secondary.** Keep unchanged unless a **tested contract violation** requires the **smallest correct fix**. Never silent wrong success. Preserve `BABDataError` semantics and public APIs.
- **Preserve inspect-sensitive behavior.** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- **No narration-as-progress.** No GREEN/coverage claim without actual command output captured in the session.

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
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing 2>&1 | tail -16
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)

**Baseline (last completed):** **78% (378 miss / 1693 stmts)**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.** Need ~175 more covered statements.

**Target:** extend `tests/test_bab_data_loader_coverage_gaps.py` with deterministic batch classes (no comments). Use `monkeypatch`/`tmp_path`/`pytest.importorskip` as needed. After each batch: focused run, aggregate+coverage, `campaign_d*` spot-check.

**Concrete missing clusters to attack (reconfirm fresh with `--show-missing`):**

1. **320-352/368-404/479-483** (`_coerce_to_datetime_scalar`/`_normalize_index` deeper fallbacks): ns/us/ms/s boundary fallbacks in int/float branches, timestamp tz_convert/tz_localize exception paths, epoch/string parsing residuals, elementwise coercer edge cases. ~60 stmts.
2. **558-565/571/582-586/620/626/630/632-633/641-642/664/676-684/694-695/708-714/729-734/757-758/766-767/770-771/789-792** (`_detect_and_normalize_exchange_format`/exchange pivot): remaining pivot coercion, tz elementwise, OHLCV parsing, date coercion do_coerce/set_index fallbacks. ~55 stmts.
3. **804-805/821-823/832/840-841/859/861-864/867-868/878-879/882-883/890/894/901-903/908-914/917-918** (`_promote_datetime_column`): candidate parse tz/set_index fallbacks, unnamed-column parse coercion, last-resort object scan tz/set_index. ~45 stmts.
4. **1584/1588-1592/1612/1620-1627/1649/1659-1664/1686-1687/1698-1699/1757/1764-1765/1782-1783/1792-1793/1799-1806/1825-1826** (CSV/Parquet/HDF5/Pickle/JSON loader exception tails): monkeypatch missing deps/readers, parser/OSError/ValueError wrapping, empty payloads, pickle dict/list/unsupported branches. ~55 stmts.
5. **1869-1870/1895/1901-1902/1926-1929/1937-1938/1942/1990/1992-1993/2010/2022-2023/2041-2042/2051/2054-2055/2061/2068/2079-2080/2087-2092** (`load_returns` dispatch tails, `_drop_metadata_columns`, `_is_likely_returns`, `detect_price_or_returns` json/parquet/hdf5/pickle paths). ~45 stmts.
6. **2137-2138/2160-2163/2167-2168/2173-2174/2187-2189/2192-2193/2213/2238-2239/2241/2247-2248** (`normalize_schema` MultiIndex/header/exception tails, `clean_data`/`validate_prices` tails). ~20 stmts.
7. **953/982-983/1030-1034/1055-1056/1082-1090/1097-1098/1110-1126/1139/1147/1153-1154/1163/1174-1198/1202/1207/1221-1222/1226-1227/1254-1258/1293-1294/1304-1320/1345-1346/1418-1419/1443-1452/1474-1490/1530-1539** (name normalization/QC/validation/coercion/returns validation branches). ~98 stmts.

**Required cadence (non-optional):** complete **≥3 batches** this session, measuring after each. Prioritize batches 1, 3, 4, then 2/5/6/7 by fresh missing report. If a branch is genuinely unreachable without unsafe production changes, document evidence here and move on—do not fabricate coverage.

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
