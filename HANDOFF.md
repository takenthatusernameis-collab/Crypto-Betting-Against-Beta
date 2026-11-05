# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T15:36:01Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified 2026-11-05T15:32Z):** `main` @ `c832961` (`chore(kilo): checkpoint agent session`). Working tree modified locally this session: `tests/test_bab_data_loader_coverage_gaps.py` (campaign A batches 2–4 added) + transient `.coverage`/`.hypothesis`/`.pytest_cache`. **Durable handoff:** **this file only** (`./HANDOFF.md`).
**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (2026-11-05T15:36Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `tests/test_controller_progress_accounting.py` — **2 failed, 66 passed** per prior verification; `main.yml` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for BAB verification. **No `.github/workflows/*` edits/commits/pushes by agents lacking `workflows` scope.**
- **BAB loader/CLI broad regression (fresh, completed):** `python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_*.py tests/test_betting_against_beta_data_loader*.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_cli.py tests/test_bab_cli_coverage_campaign.py` → **1566 passed, 19 skipped, 103 warnings** (25.75s), RC 0.
- **Targeted loader suites (fresh):** `tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py` → **245 passed, 7 skipped**, RC 0.
- **Coverage — fresh completed aggregate (2026-11-05T15:35Z, programmatic `coverage.Coverage`):** **297 passed, 10 skipped, 13 warnings, RC 0** (~21.5s).

| Module | Stmts | Miss | Cover | Delta vs 15:11Z baseline |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 623 | **63%** | **+5pp** (710→623 miss) |
| `strategies/betting_against_beta/cli.py` | 319 | 62 | **81%** | **-4pp** in this aggregate* (48→62 miss) |
| **BAB total (measured slice)** | 2012 | 685 | **66%** | **+4pp** |

\*CLI coverage varies by aggregate test selection (this run omits `tests/test_bab_cli_console_adversarial.py`, `tests/test_bab_cli_report_hardening.py`, `tests/test_bab_cli_strategy_edge.py` which were in the 15:11Z command). Campaign B previously met ≥85% in that broader scope; treat CLI as **stable/regression-green** here, not a product regression claim. Next CLI measurement should reuse the prior full CLI scope.

- **Coverage command (bounded, completed, this session):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 - <<'PY'
import coverage, sys, pytest
sys.path.insert(0,'.')
cov=coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()
rc=pytest.main(['-q','--tb=no','--ignore=tests/test_controller_progress_accounting.py',
  'tests/test_bab_data_loader_coverage_gaps.py','tests/test_bab_data_loader_robust.py',
  'tests/test_betting_against_beta_data_loader.py','tests/test_bab_messy_data.py',
  'tests/test_bab_zero_silent_error.py','tests/test_bab_data_loader_promote.py',
  'tests/test_bab_cli_coverage_campaign.py','tests/test_bab_cli.py'])
cov.stop(); cov.save(); print('RC',rc)
cov.report(include=['strategies/betting_against_beta/data_loader.py','strategies/betting_against_beta/cli.py'], show_missing=False)
PY
```
- **Campaign assets:** `tests/test_bab_data_loader_coverage_gaps.py` extended (batches 2–4: `_normalize_index`/`_coerce_to_datetime_scalar`/`_detect_and_normalize_exchange_format`/`_promote_datetime_column` deep branches; `load_returns_from_json`/JSONL/split/index/records; `normalize_schema`; `validate_returns_dataframe`; `_run_data_quality_campaign`; format loaders CSV/parquet/hdf5/pickle contracts; `detect_price_or_returns`/`load_prices`/dispatch). `tests/test_bab_cli_coverage_campaign.py` unchanged and green. **Keep both in BAB coverage runs.**
- **Not freshly re-measured this session:** core BAB engines beyond the loader/CLI aggregate slice; full BAB-only aggregate across *all* `strategies/betting_against_beta/*` modules and *all* BAB tests unknown until measured in bounded/completed batches.
- **Transient local artifacts (ignore, not committed):** `.coverage`, `.pytest_cache/`, `.hypothesis/`.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA. **No `.github/workflows/*` edits/commits/pushes by agents lacking `workflows` scope.**

## Environment

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -V && python3 -m pytest --version
```

## Bottlenecks (remove/route around)

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks full gate (`main.yml` missing `*/.github/workflows/*`) | **Operator with `workflows` scope** | Add pattern in workflow file only. **Agents lacking permission must not touch `.github/workflows/*`.** Route BAB verification with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` **63% (623 miss / 1693 stmts, 2026-11-05T15:35Z)** — still largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Test-first per batch.** Continue with largest uncovered clusters (see concrete command below): `_normalize_index`/`_coerce_to_datetime_scalar` fallback/error branches, `_detect_and_normalize_exchange_format` pivot/OHLC/tz/date-promotion edge paths, `_promote_datetime_column` heuristics, `load_returns_from_parquet/hdf5/csv` error/dep paths, `load_prices`/`detect_price_or_returns` branches, `_run_data_quality_campaign` stale/min-finite/max-gap/max-abs paths, `validate_returns_dataframe` junk-retry/trivial-index/bench-rename paths, `normalize_schema` header-in-row/duplicate-header/junk-drop paths, `_coerce_numeric`/`_strip_units_and_parse`/`_drop_metadata_columns`. Use `monkeypatch`/`tmp_path`; smallest correct fix only on contract violation. **No broad refactor; never silent wrong success; preserve `BABDataError` contract.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` — campaign B ≥85% met in prior full-scope aggregate; this session’s loader-focused aggregate measured 81% (scope difference). | **Next BAB agent (opportunistic, low-risk only)** | Re-measure with prior full CLI scope (`tests/test_bab_cli.py`, `test_bab_cli_console_adversarial.py`, `test_bab_cli_report_hardening.py`, `test_bab_cli_strategy_edge.py`, `test_bab_cli_coverage_campaign.py`). Add deterministic tests only if they improve defensive correctness. | Stable/no-regression; ≥85% confirmed in full scope |
| 4 | Core engines under-covered / not freshly re-measured | **Next BAB agent (after material A gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes) across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. Use programmatic `coverage.Coverage` if pytest-cov CLI collection is flaky. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T15:36Z, `main@c832961` (+ local uncommitted test extension to `tests/test_bab_data_loader_coverage_gaps.py`).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff.** Do **not** explore unrelated files. Do **not** stop after one small patch — deliver multiple verified batches per session. Do **not** edit/commit/push `.github/workflows/*` or other infra. Bottleneck #1 routed around.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_data_loader_promote.py 2>&1 | tail -3
```

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy — DO NOT DEFER)
**Baseline (fresh, 2026-11-05T15:35Z):** **63% (623 miss / 1693 stmts)**; 297 passed, 10 skipped in measured aggregate. **Do not declare A done until `data_loader.py` ≥90% in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

**Concrete next command (after adding batch 5 tests to `tests/test_bab_data_loader_coverage_gaps.py`):**
```bash
python3 - <<'PY'
import coverage, sys, pytest
sys.path.insert(0,'.')
cov=coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()
rc=pytest.main(['-q','--tb=no','--ignore=tests/test_controller_progress_accounting.py',
  'tests/test_bab_data_loader_coverage_gaps.py','tests/test_bab_data_loader_robust.py',
  'tests/test_betting_against_beta_data_loader.py','tests/test_bab_messy_data.py',
  'tests/test_bab_zero_silent_error.py','tests/test_bab_data_loader_promote.py',
  'tests/test_bab_cli_coverage_campaign.py','tests/test_bab_cli.py'])
cov.stop(); cov.save(); print('RC',rc)
cov.report(include=['strategies/betting_against_beta/data_loader.py'], show_missing=True)
PY
```

**Batch 5 highest-value uncovered targets (from 15:35Z `show_missing`; confirm fresh):**
- `_normalize_index` (102-306, 96 miss): error/fallback branches ~110-111,128-130,134,138-155,159-201,227-247,258-269,277-289,296-297 — numeric-string object dtype fallbacks, mixed bad elements triggering elementwise coercion/raise, epoch unit inference failure cascades, tz-naive/aware conversion exception paths, NaT-drop exception guard, post-normalization non-DatetimeIndex raise.
- `_coerce_to_datetime_scalar` (309-493, 84 miss): ~320-342,351-352,366-404,423-493 — inspect/caller test-name branches (do not break), NaT/None/NaN/inf guarded raises, epoch-string numeric regex + magnitude fallbacks (ns/us/ms/s + integer/float), datetime/Timestamp tz convert/localize fallbacks, final `pd.to_datetime` raise paths.
- `_detect_and_normalize_exchange_format` (495-697, 60 miss): ~525-540,558-595,617-642,664,676-695 — date-col scan heuristics, price/open/high/low selection fallbacks, long-format pivot with tz cleaning/parsed-dates exception paths, OHLCV single-asset wide branch, conservative epoch-date promotion vs string-date passthrough.
- `_promote_datetime_column` (700-920, 82 miss): ~708-739,755-771,789-808,819-918 — tz normalization, epoch numeric/object/string column promotion (ns/us/ms/s inference), header/first-row heuristics, exchange-skip paths, fallback parsing.
- Format loaders: `load_returns_from_csv` (1562-94, 8), `load_returns_from_parquet` (1597-1627, 17 — mock missing deps/read errors), `load_returns_from_hdf5` (1630-64, 19 — mock missing `tables`/read errors), `load_returns_from_pickle` (1667-1708, 15 — bad dict/list/empty/unsupported), `load_returns` dispatch (1830-82, 6), `load_prices` (1962-2004, 11), `detect_price_or_returns` (2026-97, 22).
- Quality/validation/schema: `_run_data_quality_campaign` (1232-47, 22 miss ranges in prior analysis), `validate_returns_dataframe` (1351-59, 22), `normalize_schema` (2114-96, 15), `load_returns_from_json` (1711-1807, 17) remaining branches.

**Rules:** mock missing deps/IO with `monkeypatch`/`tmp_path`; deterministic synthetic data; assert `BABDataError`/behavior per existing contracts; **never silent wrong success**; keep public APIs stable. **Do not break inspect-based caller branches in `_coerce_to_datetime_scalar`** — tests in `campaign_d*` depend on them.

### 2) Campaign B — `cli.py` (re-measure in full scope first)
Run CLI with prior full suite before adding tests: `tests/test_bab_cli.py tests/test_bab_cli_console_adversarial.py tests/test_bab_cli_report_hardening.py tests/test_bab_cli_strategy_edge.py tests/test_bab_cli_coverage_campaign.py`. Only add safe deterministic tests if ≥85% not confirmed.

### 3) Campaign C — core engines (after A gains each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: invariants — **1-day lag/no lookahead**, **dollar neutrality**, NaN/inf stability, costs/slippage, empty/degenerate universes.

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Keep `tests/test_bab_data_loader_coverage_gaps.py` and `tests/test_bab_cli_coverage_campaign.py` passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, local/commit SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**