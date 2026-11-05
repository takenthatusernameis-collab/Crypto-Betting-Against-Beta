# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T21:30:00Z (durable refresh)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `ba888c8` (local HEAD; clean before this session's test-file edits may be uncommitted — verify with `git status`).
**Working tree (this session):** modified `tests/test_bab_data_loader_coverage_gaps.py` (appended Campaign A batch tests); no production code changes. **No `.github/workflows/*` edits/commits/pushes.**

**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Recon verified (2026-11-05T21:30Z)

- Env: Python 3.12.3, pytest 9.2.2, coverage.
- Full suite quick signal (earlier run, `--maxfail=1`): only known failure is `tests/test_controller_progress_accounting.py` workflow-sync (`*/.github/workflows/*` missing in workflow). **Not BAB logic. Route with `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`.**
- Inspect-sensitive suites preserved (fresh): `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. **`_coerce_to_datetime_scalar` inspect/caller branches preserved.**
- Fresh bounded BAB aggregate (completed this session): **794 passed, 11 skipped, 57 warnings, RC 0** for the bounded set in Step 0/coverage command below.

## Verified state

- **Infra blocker (NOT BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync::{test_python_patterns_are_subset_of_workflow,test_nested_workflow_pattern_is_present_in_workflow}` fail because `.github/workflows/main.yml` excludes are missing `*/.github/workflows/*` (must stay in lock-step with `scripts/controller_progress.py` `EXCLUDE_PATTERNS`). **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py`.
- **Coverage — fresh completed aggregate (2026-11-05T21:30Z, `coverage run`, bounded BAB set):**

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 364 | **78%** | **≥90%** (Campaign A, mandatory, heavy) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **≥85%** (low priority) |

- **Session progress (verified, no GREEN/coverage claim without output):** 3 measured test batches added to `tests/test_bab_data_loader_coverage_gaps.py` (coerce/normalize/promote deep fallbacks, loader exception tails, exchange/detect/dispatch, schema/utility tails). Focused new tests + `campaign_d*` spot-checks passed. Aggregate moved **691 → 794 passed** (11 skipped). `data_loader.py` moved **378 miss (78%) → 364 miss (78%)** in bounded aggregate — **net -14 missed statements this session; Campaign A ≥90% NOT reached (need ~195 more covered statements / ~89%+ delta on remaining misses).**

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
| 1 | Workflow/controller exclude-pattern sync blocks un-ignored full green | **Operator with `workflows` scope** | Add `*/.github/workflows/*` pattern in workflow file only. Agents lacking permission must not touch `.github/workflows/*`. Route with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; un-ignored full gate green |
| 2 | `data_loader.py` **78% (364 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate, non-optional)** | **Test-first per batch.** Target uncovered clusters with `monkeypatch`/`tmp_path`/optional-dep skips. Smallest correct fix only on proven contract violation. No broad refactor; never silent wrong success; preserve `BABDataError` contract. Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`. No comments in code. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions |
| 3 | `cli.py` — **81%** | **Next BAB agent (low priority)** | Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T21:30Z, `main@ba888c8` (local). Last completed bounded BAB aggregate: 794 passed/11 skipped; `data_loader.py` 78% (364 miss / 1693 stmts).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage. **Read this handoff, run Step 0, then execute Campaign A immediately. Do not idle. Do not stop after one small patch. Do not claim completion until Campaign A reaches ≥90% in a fresh completed aggregate run.**

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
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing 2>&1 | tail -18
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)

**Baseline (fresh completed):** **78% (364 miss / 1693 stmts)**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.** Need ~195 more covered statements.

**Target:** extend `tests/test_bab_data_loader_coverage_gaps.py` with deterministic batch classes (no comments). Use `monkeypatch`/`tmp_path`/`pytest.importorskip` as needed. After each batch: focused run, aggregate+coverage, `campaign_d*` spot-check.

**Concrete next attack surface (reconfirm fresh with `--show-missing` before coding):** prioritize branches in `_coerce_to_datetime_scalar` ns/us/ms/s/epoch fallback exceptions and inspect-stack edge paths that do not break `campaign_d*`; `_normalize_index` tz_convert/tz_localize/elementwise coercion error paths; `_promote_datetime_column` parse/set_index/tz/last-resort scan fallbacks; `_detect_and_normalize_exchange_format` pivot/OHLCV/date-coercion tails; CSV/Parquet/HDF5/Pickle/JSON loader read/validate wrapping (`load_returns_from_*`, `detect_price_or_returns` for json/parquet/hdf5/pickle/csv/unknown paths); `load_returns`/`load_prices` dispatch auto-detect and key/extension tails; `_drop_metadata_columns`/`_is_likely_returns`; `normalize_schema` MultiIndex/header/junk-column coercion tails; `clean_data`/`validate_prices`/`standardize_columns` exception contracts. Use missing-report ranges from Step 0 as source of truth.

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
