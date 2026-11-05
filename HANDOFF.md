# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T15:26:01Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified 2026-11-05T15:11Z):** `main` @ `7ea47d2` (`chore(kilo): checkpoint agent session`). Working tree clean at verification. **Durable handoff:** **this file only** (`./HANDOFF.md`).
**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (re-recon, 2026-11-05T15:11Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no` → **2 failed, 66 passed** (0.22s). `main.yml` `stage_safe_changes()` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for BAB verification.
- **BAB targeted verification (fresh, 2026-11-05T15:11Z):** `python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_bab_cli_coverage_campaign.py` → **111 passed, 1 skipped, 4 warnings** (6.31s), RC 0.
- **Coverage — fresh completed aggregate (2026-11-05T15:11Z, programmatic `coverage.Coverage`, same scope as below):** **226 passed, 7 skipped, 11 warnings, RC 0** (17.76s).

| Module | Stmts | Miss | Cover | Notes |
|---|---:|---:|---:|---|
| `strategies/betting_against_beta/data_loader.py` | 1693 | 710 | **58%** | **PRIMARY risk/gap** — largest uncovered BAB surface |
| `strategies/betting_against_beta/cli.py` | 319 | 48 | **85%** | Campaign B target met; residual misses mostly defensive |
| **BAB total (measured slice)** | 2012 | 758 | **62%** | `source=['strategies.betting_against_beta']`, measured modules above |

- **Coverage command (bounded, completed):**
```bash
python3 - <<'PY'
import coverage, sys, pytest
sys.path.insert(0,'.')
cov=coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()
rc=pytest.main(['-q','--tb=no',
  'tests/test_bab_data_loader_coverage_gaps.py','tests/test_bab_data_loader_robust.py',
  'tests/test_betting_against_beta_data_loader.py','tests/test_bab_data_loader_promote.py',
  'tests/test_bab_messy_data.py','tests/test_bab_zero_silent_error.py',
  'tests/test_bab_cli.py','tests/test_bab_cli_console_adversarial.py',
  'tests/test_bab_cli_report_hardening.py','tests/test_bab_cli_strategy_edge.py',
  'tests/test_bab_cli_coverage_campaign.py'])
cov.stop(); cov.save()
print('RC',rc)
cov.report(include=['strategies/betting_against_beta/data_loader.py','strategies/betting_against_beta/cli.py'], show_missing=True)
PY
```
- **Campaign test assets present (HEAD):** `tests/test_bab_data_loader_coverage_gaps.py` (508 lines), `tests/test_bab_cli_coverage_campaign.py` (211 lines). Keep both green and included in BAB coverage runs.
- **Not freshly re-measured this session:** core BAB engines beyond the loader/CLI aggregate slice; full BAB-only aggregate across *all* `strategies/betting_against_beta/*` modules and *all* BAB tests is unknown until measured in bounded/completed batches.
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
| 2 | `data_loader.py` **58% (710 miss / 1693 stmts, 2026-11-05T15:10Z)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Test-first per batch.** Add adversarial/branch tests via public APIs against largest uncovered clusters; smallest correct fix only when contract violated. **No broad refactor; never silent wrong success; preserve `BABDataError` contract.** Keep `tests/test_bab_data_loader_coverage_gaps.py` in every BAB loader coverage run. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` residual 48 misses — **≥85% met** | **Next BAB agent (opportunistic, low-risk only)** | Only add deterministic branch tests if they improve defensive correctness; do not weaken contracts or contort behavior for coverage. | Stable/no-regression; optional measured lift |
| 4 | Core engines under-covered / not freshly re-measured | **Next BAB agent (after material A gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes) across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. Use programmatic `coverage.Coverage` if pytest-cov CLI collection is flaky. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T15:11Z, `main@7ea47d2`, working tree clean.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff.** Do **not** explore unrelated files. Do **not** stop after one small patch — deliver multiple verified batches per session. Do **not** edit/commit/push `.github/workflows/*` or other infra. Work in **verified batches** and record real output in this handoff. Bottleneck #1 is routed around.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no 2>&1 | tail -6   # expect 2 fails (infra blocker)
python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_bab_cli_coverage_campaign.py 2>&1 | tail -4
```
Coverage baseline (bounded, **completed**) — use the exact command in “Verified state”.

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy — DO NOT DEFER)
**Baseline:** 58% (710 miss / 1693 stmts). **Test-first per batch:** add adversarial/branch tests → run targeted suites → smallest correct fix only if behavior violates contract → rerun coverage delta. **Do not declare A done until `data_loader.py` ≥90% measured in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**

Priority target clusters (from 2026-11-05T15:10Z missing ranges; confirm with fresh `show_missing`):
- **Datetime/index/epoch/tz coercion & fallbacks:** `_coerce_to_datetime_scalar` (inspect/caller/NaT/float/int/string/bool/object branches), `_normalize_index` (string/numeric epoch ns/us/ms/s inference, tz-aware/naive, parse fallbacks, trivial-index rejection contract), `_coerce_series_to_datetime_index`, `_promote_datetime_column` (exchange skip/normalize paths, tz normalization, header/first-row heuristics).
- **Exchange/shape detection & pivots:** `_detect_and_normalize_exchange_format` (long symbol+date+price pivot, OHLCV single-asset wide, date-only promotion with epoch/coercion guards, tz cleaning, price/open/high/low column selection fallbacks).
- **Normalization/cleaning:** `_normalize_asset_name`/`_normalize_columns` edge cases (multi-index/unnamed/junk/duplicate detection paths already tested — extend around misses), `_drop_metadata_columns`, `_drop_all_nan_columns`, `_strip_units_and_parse`/`_series_is_parseable`/`_coerce_numeric` (European decimals, thousand separators, percent malformed, mixed types, units/currency tokens, garbage vs malformed distinction).
- **Format loaders & dispatch:** `load_returns`/`detect_price_or_returns` (prices-vs-returns auto-detect for files/DataFrames, dir/not-found/unsupported ext), CSV/JSON/JSONL/Parquet/HDF5/Pickle loader error branches (missing optional deps, parser/IO/value errors, pickle flat-scalar/list/dict/object types, JSONL comments/blank lines, JSON orient/forms).
- **Schema/validation/quality:** `normalize_schema` (multi-level cols, header-in-row/duplicate-header heuristics, junk-column drops), `_prices_to_returns`/`load_prices`/`_is_likely_returns`, `validate_returns_dataframe` (benchmark case-insensitive/rename, junk-column pre-drop, retry-after-coerce, trivial index rejection contract, min_rows/finite history, inf handling), `_run_data_quality_campaign` (duplicates allowed/dropped, implausible returns, max gap, min finite fraction, stale/frozen runs — respect current lenient defaults and existing contracts; **do not break existing tests**), `standardize_columns`/`clean_data`/`validate_prices`.

**Rules:** mock missing deps/IO with `monkeypatch`/`tmp_path`; use deterministic synthetic data; assert `BABDataError` and messages/behavior per existing contracts; **never silent wrong success**; keep public APIs stable.

### 2) Campaign B — `cli.py` (opportunistic)
Target met at **85%**. Only pursue additional misses if safe/deterministic and they improve defensive correctness or reduce real blind spots; do not weaken contracts.

### 3) Campaign C — core engines (after A gains each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: close high-value branches; enforce invariants (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output. No coverage claim without completed measurement.**
- Keep `tests/test_bab_data_loader_coverage_gaps.py` and `tests/test_bab_cli_coverage_campaign.py` passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, local/commit SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**