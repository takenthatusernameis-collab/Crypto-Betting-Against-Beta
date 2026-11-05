# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T19:05:21Z (refreshed this session)
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified):** `main` @ `192f0c7` (`chore(kilo): checkpoint agent session`). Working tree has **local uncommitted test additions** in `tests/test_bab_data_loader_coverage_gaps.py` (Batch 8+9, this session) plus transient `.coverage`/cache artifacts; **no production code changed**; **no `.github/workflows/*` touched**. **Durable handoff:** **this file only** (`./HANDOFF.md`).
**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Recon re-verified (2026-11-05T19:05Z)

- Env: Python 3.12.3, pytest 9.2.0.
- BAB loader/CLI aggregate (fresh, completed): `--ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py` → **596 passed, 11 skipped, 46 warnings**, RC 0.
- Regression spot-check (inspect-sensitive campaign_d): `tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py` → **51 passed, 7 warnings**, RC 0. **`_coerce_to_datetime_scalar` inspect/caller branches preserved.**

## Verified state (fresh completed measurement, 2026-11-05T19:05Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py` — `main.yml` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for all BAB verification. **No `.github/workflows/*` edits/commits/pushes.**
- **Coverage — fresh completed aggregate (2026-11-05T19:05Z, `coverage run`):** **596 passed, 11 skipped, RC 0**.

| Module | Stmts | Miss | Cover | Δ vs 18:58Z baseline (526 miss / 69%) | Target |
|---|---:|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 439 | **74%** | **+5pp, -87 miss** (526→439) | **≥90%** |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** (loader-focused aggregate) | stable | **≥85%** (full scope) |
| **Measured slice total** | 2012 | 501 | **75%** | **+4pp** | **≥85%** |

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

## This session’s verified progress (BAB-only)

- **Batch 8 + 9 complete** → `tests/test_bab_data_loader_coverage_gaps.py` (487 passed, 5 skipped in that file alone; 596/11 in aggregate): `_not_null`/`_series_has_any_finite`, `_coerce_series_to_datetime_index` (tz/list/error paths), `_normalize_index` (numeric epoch ms/us/ns/s, float epochs, empty numeric index, mixed tz strings, all-NaT/unparseable), `_coerce_to_datetime_scalar` (epoch strings, ISO/Z/offset, tz Timestamp, NaN/inf/bad strings), `_promote_datetime_column` (multi-column/unparseable/unnamed/last-resort/object-scan/tz), `_detect_and_normalize_exchange_format` (OHLCV single-asset, long pivot, epoch date), `load_prices` (CSV/JSON/DataFrame/pickle/JSONL/parquet-skip/unsupported), `load_returns`/JSON/JSONL dispatch (split/records, bad payloads, range-index defaults), metadata/`detect_price_or_returns`, `standardize_columns`/`clean_data`/`validate_prices` contracts, QC/validation edges.
- **Production code:** **unchanged**. Invariants preserved: no lookahead/lag semantics untouched; `BABDataError` contract preserved; dollar-neutral/costs/slippage/public APIs untouched. **Did not break inspect-based caller branches in `_coerce_to_datetime_scalar`.**
- **Campaign A status:** **`data_loader.py` 74% (439 miss / 1693 stmts). Not done** — target remains **≥90%** in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.

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
| 2 | `data_loader.py` **74% (439 miss / 1693 stmts)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Test-first per batch.** Target remaining uncovered clusters (reconfirm with `coverage report --show-missing`). Current biggest remaining gaps include: **227-247** (21L, `_coerce_series_to_datetime_index` tail tz/index/drop exception branches), **819-837** (19L, `_promote_datetime_column` parse/coerce/set_index fallbacks), **558-567/571/573-574/577-586/594-595** and **620/623-626/630/632-633/639-642/664/676-684/690-691/694-695** (exchange format tz/epoch/pivot/OHLCV branches), **708-714/729-734/738-739/755-758/766-767/770-771/789-792** (exchange/promote date-detection/conservative coercion branches), **320-322/324-328/334-335/338-342/351-352/368-372/374-377/381-382/388-389/395-396/400-404/425-429/431-434/438-439/449-453/455-458/462-463/467-468/471-472/479-483** (`_coerce_to_datetime_scalar` fallback/inspect-adjacent branches — **do not break campaign_d inspect behavior**), **110-111/128-130/134/141-143/147-149/153-155/161/171-176/180/188/194/196/200-201/208-209/213-214** (`_normalize_index` numeric/elementwise fallback tails), **1232+ subsets** (QC/validation/junk/coercion), **1562+ subsets** (CSV/parquet/hdf5/pickle loader tails), **1711+ subsets** (JSON/split/table/edge), **1926-1929/1937-1938/1942/1990/1992-1993** (`load_prices`/detect tails), **2213/2238-2239/2241/2247-2248** (wrappers). Use `monkeypatch`/`tmp_path`; smallest correct fix only on contract violation. **No broad refactor; never silent wrong success; preserve `BABDataError` contract. Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`. No comments in code.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` — **81%** in loader aggregate | **Next BAB agent (low priority)** | Add safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn. | Stable/no-regression; ≥85% in full scope |
| 4 | Core engines under-covered / not freshly re-measured | **Next BAB agent (after A gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes) across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. | Completed coverage table recorded |

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T19:05Z, `main@192f0c7` (+ local uncommitted `tests/test_bab_data_loader_coverage_gaps.py` Batch 8+9).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff.** Do **not** explore unrelated files. Do **not** stop after one small patch — deliver multiple verified batches per session. Do **not** edit/commit/push `.github/workflows/*` or other infra. Route around controller blocker with `--ignore=tests/test_controller_progress_accounting.py`. **Production code is currently unchanged; keep it that way unless a tested contract violation requires the smallest correct fix.**

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

**Baseline (fresh, 2026-11-05T19:05Z):** **74% (439 miss / 1693 stmts)**; measured aggregate **596 passed, 11 skipped**. **Do not declare A done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Concrete next command (after adding Batch 10 tests to `tests/test_bab_data_loader_coverage_gaps.py`):**
```bash
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no \
  --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py \
  tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py \
  tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' --show-missing
```

**Batch 10+ highest-value uncovered targets (reconfirm fresh; current measured missing):**
- **227-247**: `_coerce_series_to_datetime_index` tail branches (tz normalize loop exceptions, `Timestamp` tz convert/localize fallbacks, index assignment/drop failures) — monkeypatch `DataFrame.copy`/index setter/drop as needed.
- **819-837, 840-841, 859, 861-864, 867-868, 878-879, 882-883, 890, 894, 901-903, 908-914, 917-918**: `_promote_datetime_column` candidate parse/coerce/set_index fallbacks, unnamed-column parse coercion, last-resort object scan tz/DatetimeIndex set_index branches.
- **558-595, 620-695, 708-792**: `_detect_and_normalize_exchange_format` epoch/date coercion, OHLCV/pivot tz normalization, conservative “do not coerce” vs coercion paths, exception fallbacks.
- **320-483**: `_coerce_to_datetime_scalar` fallback chains (ns/us/ms/s boundaries, bad epoch parse fallbacks, Timestamp/datetime conversion, pandas parse fallbacks). **CRITICAL:** preserve inspect-based caller behavior for `campaign_d`/`campaign_d_core` tests (NaT/bad-value expectations) — do **not** modify production code unless unavoidable and verified.
- **110-214, 258-297**: `_normalize_index` numeric dtype magnitude branches, elementwise coercer fallbacks, mixed string tz/coerce/dayfirst tails.
- **1562-1699, 1711-1806, 1825-1826**: CSV/Parquet/HDF5/Pickle loader tails; JSON/JSONL/split/table/records/default orient/error paths.
- **1926-1942, 1990-1993, 2010-2092, 2137-2193**: `load_prices`/`_drop_metadata_columns`/`_prices_to_returns`/`detect_price_or_returns`/metadata/dispatch tails.
- **2213, 2238-2248**: `clean_data`/`validate_prices` exception/non-positive/finite-check tails.
- **1232-1554 subsets**: QC/validation/coercion remaining branches (`_run_data_quality_campaign`, `validate_returns_dataframe`, numeric coercion/junk/drop helpers).

**Rules:** mock missing deps/IO with `monkeypatch`/`tmp_path`; deterministic synthetic data; assert `BABDataError`/behavior per existing contracts; **never silent wrong success**; keep public APIs stable. **Preserve inspect-based caller branches in `_coerce_to_datetime_scalar`.** **No comments in code.** Smallest correct production fix only on proven contract violation.

## 2) Campaign B — `cli.py` (81% in this aggregate; low priority)

Add safe deterministic tests only if touching CLI behavior; prefer correctness over coverage churn.

## 3) Campaign C — core engines (after A gains each batch)

`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: invariants — **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes.

## 4) Close-out (required)

- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Keep `tests/test_bab_data_loader_coverage_gaps.py` and `tests/test_bab_cli_coverage_campaign.py` passing. Keep inspect-sensitive `campaign_d` suites passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, local/commit SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**
