# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T18:58:13Z (refreshed this session)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `cd6c483` (`chore(kilo): checkpoint agent session`). Working tree has transient `.coverage`/`.pytest_cache`/`.hypothesis` only; **no `.github/workflows/*` touched**. **Durable handoff:** **this file only** (`./HANDOFF.md`).
**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Recon re-verified (2026-11-05T18:58Z)
- Env: Python 3.12.3, pytest 9.2.0.
- BAB loader/CLI aggregate (fresh, completed): `--ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py` → **515 passed, 10 skipped, 35 warnings**, RC 0.

## Verified state (fresh completed measurement, 2026-11-05T18:58Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py` — `main.yml` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for all BAB verification. **No `.github/workflows/*` edits/commits/pushes.**
- **Coverage — fresh completed aggregate (2026-11-05T18:58Z, `coverage run`):** **515 passed, 10 skipped, RC 0**.

| Module | Stmts | Miss | Cover | Δ vs 18:49Z baseline | Target |
|---|---:|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 526 | **69%** | **+1pp** (541→526 miss) | **≥90%** |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** (loader-focused aggregate) / **85%** (full CLI scope confirmed prior) | stable | **≥85%** (full scope) |
| **Measured slice total** | 2012 | 588 | **71%** | **+1pp** | **≥85%** |

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
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py'
```
- **Not freshly re-measured this session:** full repo route-around gate; core BAB engines beyond loader/CLI slice; full BAB-only aggregate across all BAB modules/tests.
- **Transient local artifacts (ignore, not committed):** `.coverage`, `.pytest_cache/`, `.hypothesis/`.

## This session’s verified progress (BAB-only)

- **Added Batch 7 tests** to `tests/test_bab_data_loader_coverage_gaps.py` (406 passed, 4 skipped in that file alone): `_normalize_index` numeric/object fallback/elementwise/dayfirst/duplicate/tz/numeric-magnitude branches; `_coerce_to_datetime_scalar` epoch/string/ISO/offset/dayfirst/numpy/datetime/date/zero/magnitude variants (preserving inspect-based caller-branch behavior — **no production changes**); `_detect_and_normalize_exchange_format` long symbol variants, OHLCV/adj-close/close-price/time heuristic, conservative string-date, epoch-ms promotion; `_promote_datetime_column` tz-aware index, 2-col date promotion, unparseable candidate `BABDataError`, unnamed/last-resort scan, epoch/snapped_at candidates; format loaders CSV empty/read-error, JSON split/index/table/jsonl/bad-line/missing, `load_returns` jsonl/dir/None dispatch, pickle dict/empty, parquet/hdf5 read/validate exception wrapping; `validate_returns_dataframe` type/None/empty/no-dt-index/min-rows/junk/inf/benchmark/no-finite/only-benchmark/insufficient-history/quality-off/case-insensitive; `_run_data_quality_campaign` bad-index/dups/allow-dups/implausible/gap/stale/min-finite-fraction/tz/clean; `normalize_schema` MultiIndex flatten, duplicate-header handling, junk-column drop, non-df/empty errors.
- **Production code:** **unchanged**. Invariants preserved: no lookahead/lag semantics untouched; `BABDataError` contract preserved (no silent wrong success introduced); dollar-neutral/costs/slippage/public APIs untouched. **Did not break inspect-based caller branches in `_coerce_to_datetime_scalar`.**

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
| 2 | `data_loader.py` **69% (526 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Test-first per batch.** Target largest uncovered clusters (reconfirm with `coverage report --show-missing`). Current biggest contiguous gaps: **66-99** (34L, module-level helpers), **227-247** (21L, `_coerce_series_to_datetime_index` tail/tz/index-assign branches), **819-837** (19L, `_promote_datetime_column` candidate parse/set_index fallbacks), **1923-1938** (16L, `load_prices` path), **2234-2249** (16L, `standardize_columns`/`clean_data`/`validate_prices` tails + `__all__` context), **1797-1807** (11L, JSON loader tail/orients), **1989-1999** (11L, `detect_price_or_returns`/returns coercion), plus `_normalize_index`/`_coerce_to_datetime_scalar` fallback chains and remaining format-loader/quality/validation branches. Use `monkeypatch`/`tmp_path`; smallest correct fix only on contract violation. **No broad refactor; never silent wrong success; preserve `BABDataError` contract. Do not break inspect-based caller branches in `_coerce_to_datetime_scalar`.** **No comments in code.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` — full-scope **85% confirmed** (prior); 81% in loader aggregate | **Next BAB agent (low priority)** | Only add safe deterministic tests if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% holds |
| 4 | Core engines under-covered / not freshly re-measured | **Next BAB agent (after A gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes) across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. | Completed coverage table recorded |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T18:58Z, `main@cd6c483`.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff.** Do **not** explore unrelated files. Do **not** stop after one small patch — deliver multiple verified batches per session. Do **not** edit/commit/push `.github/workflows/*` or other infra. Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`.

## 0) Recon — establish truth (run to completion; record key numbers)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py 2>&1 | tail -3
```

## 1) Campaign A — `data_loader.py` (PRIMARY, heavy — DO NOT DEFER)

**Baseline (fresh, 2026-11-05T18:58Z):** **69% (526 miss / 1693 stmts)**; measured aggregate **515 passed, 10 skipped**. **Do not declare A done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Concrete next command (after adding Batch 8 tests to `tests/test_bab_data_loader_coverage_gaps.py`):**
```bash
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing
```

**Batch 8+ highest-value uncovered targets (reconfirm fresh):**
- **66-99**: `_not_null` / `_series_has_any_finite` / small module-level helpers — exercise None/NaT/pd.NA/Series/list/tuple/scalar/exception paths.
- **227-247**: `_coerce_series_to_datetime_index` tail branches (tz normalization loop, `Timestamp` tz convert/localize fallbacks, index assignment, drop column, exception handling).
- **819-837, 856-864, 867-868, 874-883, 890-918**: `_promote_datetime_column` candidate parse/coerce fallbacks, 2-col vs multi-col behavior, unnamed-column coercion, last-resort object scan tz/set_index branches.
- **1923-1938, 1895, 1901-1902, 1917-1918, 1942, 1954**: `load_prices`/`detect_price_or_returns` dispatch branches.
- **2234-2249, 2211-2213, 2221-2224**: `standardize_columns`/`clean_data`/`validate_prices` convenience wrappers.
- **1797-1807, 1821-1826**: JSON loader tail (`index` orient path nuances) / `load_returns` dispatch fallbacks.
- **558-695 subsets** and **708-771 subsets**: remaining `_detect_and_normalize_exchange_format` and `_promote_datetime_column` error/tz/parse branches.
- **320-493 subsets** and **110-306 subsets**: remaining `_coerce_to_datetime_scalar` / `_normalize_index` fallback chains — **preserve inspect/caller test-name branches** (do not break `campaign_d*`).
- **1232-1554 subsets**: quality/validation remaining branches (`_run_data_quality_campaign`, `validate_returns_dataframe`, coercion/junk/drop helpers).

**Rules:** mock missing deps/IO with `monkeypatch`/`tmp_path`; deterministic synthetic data; assert `BABDataError`/behavior per existing contracts; **never silent wrong success**; keep public APIs stable. **Do not break inspect-based caller branches in `_coerce_to_datetime_scalar`.** **Do not add comments to code.**

## 2) Campaign B — `cli.py` (full-scope 85% confirmed; low priority)

Maintain ≥85% in full scope. Add safe deterministic tests only if touching CLI behavior.

## 3) Campaign C — core engines (after A gains each batch)

`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: invariants — **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes.

## 4) Close-out (required)

- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Keep `tests/test_bab_data_loader_coverage_gaps.py` and `tests/test_bab_cli_coverage_campaign.py` passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, local/commit SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**
