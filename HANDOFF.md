# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T19:43:22Z (refreshed this session)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `c75a057` (`chore(kilo): checkpoint agent session`). Working tree: **`HANDOFF.md` updated (untracked/modified relative to HEAD state) as the single durable handoff**; **`tests/test_bab_data_loader_coverage_gaps.py` exists locally (499 passed, 5 skipped in isolation) and is included in the measured aggregate — verify persistence/commit state with `git status`/`git diff` before assuming it is in HEAD.** Transient `.coverage`/cache artifacts present locally; **no production code changed**; **no `.github/workflows/*` touched**.

**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks. Do not explore unrelated files.

## Recon re-verified (2026-11-05T19:43Z)

- Env: Python 3.12.3, pytest 9.2.0.
- BAB loader/CLI aggregate (fresh, completed): `--ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py` → **608 passed, 11 skipped, 48 warnings, RC 0**.
- Inspect-sensitive regression spot-check: `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **44 passed, 5 warnings, RC 0**. **`_coerce_to_datetime_scalar` inspect/caller branches preserved.**
- `tests/test_bab_data_loader_coverage_gaps.py` alone → **499 passed, 5 skipped, RC 0** (prior verified run; aggregate includes it).

## Verified state (fresh completed measurement, 2026-11-05T19:43Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py` — `main.yml` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for all BAB verification. **No `.github/workflows/*` edits/commits/pushes.**
- **Coverage — fresh completed aggregate (2026-11-05T19:43Z, `coverage run`):** **608 passed, 11 skipped, RC 0**.

| Module | Stmts | Miss | Cover | Target |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 437 | **74%** | **≥90%** (Campaign A, mandatory) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** (loader-focused aggregate) | **≥85%** (full scope, low priority) |
| **Measured slice total** | 2012 | 499 | **75%** | **≥85%** |

- **Coverage command (bounded, completed):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' --show-missing
```
- **Not freshly re-measured this session:** full repo route-around gate; core BAB engines beyond loader/CLI slice; full BAB-only aggregate across all BAB modules/tests.
- **Transient local artifacts (ignore, not committed):** `.coverage`, `.pytest_cache/`, `.hypothesis/`.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes.**

## Environment

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -V && python3 -m pytest --version
```

## Bottlenecks (remove / route around)

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks full gate (`main.yml` missing `*/.github/workflows/*`) | **Operator with `workflows` scope** | Add pattern in workflow file only. **Agents lacking permission must not touch `.github/workflows/*`.** Route BAB verification with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` **74% (437 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate, non-optional)** | **Test-first per batch.** Target remaining uncovered clusters (reconfirm with `coverage report --show-missing`). Use `monkeypatch`/`tmp_path`; smallest correct fix only on proven contract violation. **No broad refactor; never silent wrong success; preserve `BABDataError` contract. Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`. No comments in code.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `tests/test_bab_data_loader_coverage_gaps.py` persistence unclear in git | **Next BAB agent** | Before large additions, verify with `git status`/`git diff`; if untracked/uncommitted but valuable, include it in BAB work commits only when repo policy allows and tests are green (agent may commit code/tests if appropriate; never push workflows). | File state explicit; no accidental loss of verified tests |
| 4 | `cli.py` — **81%** in loader aggregate | **Next BAB agent (low priority)** | Add safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |
| 5 | Core engines under-covered / not freshly re-measured | **Next BAB agent (after A gains each batch)** | Close high-value branches with invariant assertions across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 6 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. | Completed coverage table recorded |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T19:43Z, `main@c75a057`.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff. Read it, run Step 0, then execute Campaign A immediately. Do not idle, do not explore unrelated files, do not stop after one small patch.**

## Non-negotiable operating rules
- **BAB-only scope.** Work only in `strategies/betting_against_beta/*`, BAB tests, and this handoff.
- **Heavy session required.** Deliver **≥2 verified batches** (more if stable). Each batch = new/updated tests + targeted run + aggregate/coverage delta + recorded numbers.
- **No workflow/infra changes.** Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`.
- **Production code secondary.** Keep unchanged unless a **tested contract violation** requires the **smallest correct fix**. Never silent wrong success. Preserve `BABDataError` semantics and public APIs.
- **Preserve inspect-sensitive behavior.** `_coerce_to_datetime_scalar` caller/inspect branches must keep `campaign_d`/`campaign_d2`/`campaign_d3` (and related) suites passing.
- **No false claims.** No GREEN/coverage claims without actual completed output.

## Step 0 — Recon (run to completion; record truth)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -4
python3 -m pytest -q --tb=no tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py 2>&1 | tail -2
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -2
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing 2>&1 | tail -10
```

## Campaign A — `data_loader.py` (PRIMARY, HEAVY — DO NOT DEFER)
**Baseline (fresh, 2026-11-05T19:43Z):** **74% (437 miss / 1693 stmts)**; aggregate **608 passed, 11 skipped**. **Campaign A is NOT done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Target:** extend `tests/test_bab_data_loader_coverage_gaps.py` with deterministic batch classes (no comments in code). Use `monkeypatch`/`tmp_path`. After each batch: run focused file, run aggregate + coverage, run inspect-sensitive `campaign_d*` spot-check.

**Concrete batch targets (reconfirm fresh with `--show-missing`; current measured missing clusters):**
1. **227-247**: `_coerce_series_to_datetime_index` tail — tz normalize loop exceptions, `Timestamp` tz convert/localize fallbacks, index assignment/drop failures.
2. **819-837, 840-841, 859, 861-864, 867-868, 878-879, 882-883, 890, 894, 901-903, 908-914, 917-918**: `_promote_datetime_column` candidate parse/coerce/set_index fallbacks, unnamed-column parse coercion, last-resort object scan tz/DatetimeIndex set_index branches.
3. **558-567, 571, 573-574, 577-586, 594-595, 620, 623-626, 630, 632-633, 639-642, 664, 676-684, 690-691, 694-695, 708-714, 729-734, 738-739, 755-758, 766-767, 770-771, 789-792**: `_detect_and_normalize_exchange_format` epoch/date coercion, OHLCV/pivot tz normalization, conservative coercion vs preserve, exception fallbacks.
4. **320-483**: `_coerce_to_datetime_scalar` fallback chains (ns/us/ms/s boundaries, bad epoch parse fallbacks, Timestamp/datetime conversion, pandas parse fallbacks). **Do not break inspect-sensitive caller behavior.**
5. **110-214, 258-297**: `_normalize_index` numeric dtype magnitude branches, elementwise coercer fallbacks, mixed string tz/coerce/dayfirst tails.
6. **1562-1699, 1711-1806, 1825-1826**: CSV/Parquet/HDF5/Pickle loader tails; JSON/JSONL/split/table/records/default orient/error paths (monkeypatch missing optional deps/readers).
7. **1926-1942, 1990-1993, 2010-2092, 2137-2193, 2213, 2238-2248**: `load_prices`/`_drop_metadata_columns`/`_prices_to_returns`/`detect_price_or_returns`/metadata/dispatch/`clean_data`/`validate_prices` tails.
8. **1232-1554 subsets**: QC/validation/coercion remaining branches.

**Required cadence:** complete **≥2 batches** this session, measuring after each. If a branch is genuinely unreachable without unsafe production changes, document it with evidence here and move to the next highest-value cluster.

## Campaign B — `cli.py` (low priority)
Safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn.

## Campaign C — core engines (after A gains each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: assert **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes.

## Close-out (required before ending session)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker). Keep `campaign_d*` inspect-sensitive suites passing.
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commit/file-state notes (no false SHA claims), remaining blockers, and the next **concrete command + target files/lines/tests**.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**
