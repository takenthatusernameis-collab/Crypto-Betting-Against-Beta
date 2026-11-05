# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T12:19:00Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (local, verified):** `main` @ `aae0eef` (`git status --short` shows only `?? tests/test_bab_data_loader_coverage_gaps.py` — new uncommitted test file from this session)
**Durable handoff:** this file only (`./HANDOFF.md`). No duplicates.
**Non-negotiable focus:** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and measured coverage. Repo name is the priority filter. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (fresh recon, 2026-11-05T12:19Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `pytest -q tests/test_controller_progress_accounting.py --tb=no` → **2 failed, 66 passed** (0.21s).
  - `TestStageSafeChangesPatternSync::{test_python_patterns_are_subset_of_workflow,test_nested_workflow_pattern_is_present_in_workflow}`: `.github/workflows/main.yml` `stage_safe_changes()` missing `*/.github/workflows/*` while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes it.
  - **Operator with `workflows` scope only:** add `*/.github/workflows/*|` adjacent to `.github/workflows/*|` in `main.yml` `stage_safe_changes()`; keep restore/clean/workflow-managed behavior consistent. **Agents without workflow permission must not edit/commit/push `.github/workflows/*`.**
  - **Route around:** run BAB verification ignoring `tests/test_controller_progress_accounting.py` so the blocker cannot stall BAB work.
- **BAB verification (fresh, this session):**
  - `tests/test_bab_data_loader_coverage_gaps.py` (new) → **68 passed** (1.58s).
  - `tests/test_bab_cli.py` → **14 passed** (5.12s / 8.41s when instrumented).
  - Combined: `tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_betting_against_beta_data_loader.py tests/test_bab_data_loader_robust.py` → **146 passed, 6 skipped** (9.35s).
  - Prior recon (inherited, 2026-11-05T12:07Z context): data-loader/loader/messy/zero/CLI subset → **1445 passed, 15 skipped** (60.57s); not re-run end-to-end this session.
- **Coverage (measured, programmatic `coverage.Coverage` in-process, source=`strategies.betting_against_beta`; **not** a fresh full-BAB aggregate across all BAB suites):**
  - Focused slice (`test_bab_data_loader_coverage_gaps.py + test_betting_against_beta_data_loader.py + test_bab_data_loader_robust.py`): `strategies/betting_against_beta/data_loader.py` — **56%** (748 miss / 1693 stmts).
  - Focused CLI slice (`test_bab_cli.py`): `strategies/betting_against_beta/cli.py` — **56%** (140 miss / 318 stmts).
  - Existing `.coverage` DB report (historical aggregate context, may reflect broader prior runs): `data_loader.py` showed **80%** (345 miss) via `coverage report` earlier in session; **treat 80% as prior context, not this session's fresh aggregate claim**.
  - **Full BAB-only aggregate coverage across all `strategies/betting_against_beta/*.py` remains unrecorded as final truth — do not claim full GREEN/coverage without a fresh completed run and recorded tail + table.**

## Progress this session (BAB-only)

- Added `tests/test_bab_data_loader_coverage_gaps.py` (68 tests) targeting uncovered/public-helper branches in `data_loader.py` and loader/CLI-adjacent behavior: `_coerce_to_datetime_scalar` (NaT/None/NaN/inf/empty/null strings, epoch s/ms/us, ISO, numpy/tz Timestamp), `_normalize_asset_name` mappings/suffixes, `_normalize_columns`, `_normalize_index` (epoch scales, tz-aware, duplicates/NaT/all-NaT/ambiguous/unparseable/sorted), `_promote_datetime_column` (tz index, epoch/date/timestamp/time/unix promotion paths), `_detect_and_normalize_exchange_format` (long/wide, ticker/asset/coinbase/coingecko/binance-style shapes), `load_returns` (DataFrame, missing benchmark, nonexistent/unsupported path, CSV/JSON paths, long-format attempt). Tests are contract-safe (accept `BABDataError` where formats are intentionally rejected).
- No production BAB code changed. No workflow/infra files touched.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- No force-push/history rewrite. No fake persistence claims; never claim remote state without matching SHA.

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
| 1 | Workflow/controller exclude-pattern sync blocks full gate (`main.yml` missing `*/.github/workflows/*`) | **Operator with `workflows` scope** | Add pattern in workflow file only; agents lacking permission **must not touch** `.github/workflows/*`. Route BAB verification with `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` still large/uncovered (1693 stmts; 345 misses in prior aggregate context; focused slice 56%) — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Integrate `tests/test_bab_data_loader_coverage_gaps.py` into full BAB coverage runs.** Add more test-first adversarial campaigns via public APIs against remaining misses (exchange pivots, datetime epoch-ms/ns branches, `_promote_datetime_column` coercion fallbacks, format loaders, metadata drops, duplicate/NaT handling). Smallest correct fixes only when contract is violated. No broad refactor. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` 56% focused (140 miss / 318 stmts); needs aggregate confirmation | **Next BAB agent** | Cover missing lines (arg combos/conflicts, dry-run no side effects, file I/O/errors, `--from-prices`/`--synthetic`/`--data`/`--universe` validation, `--output` writability, `--version`/exit codes/rendered errors, NaN/inf scalar coercion paths) using `capsys`, `tmp_path`, `monkeypatch`. | Measured `cli.py` **≥85%** in fresh aggregate run |
| 4 | Core engines under-covered (prior snapshot: `beta` 33%, `portfolio` 34%, `strategy` 38%, `signals` 41%, `backtest` 50%) | **Next BAB agent (after A/B gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes). | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. Avoid `--cov` CLI flag issues seen earlier by using `python -m coverage run --source=strategies.betting_against_beta -m pytest ...` in-process/programmatic if needed. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**You are on BAB hardening duty.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. Do not explore unrelated files. Do not stop after one small patch. Do not edit/commit/push `.github/workflows/*` or other infra. Work in **verified batches** and record real output in this handoff. The blocker in row 1 is routed around — it must not stop BAB work.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no 2>&1 | tail -6  # expect 2 fails until operator fixes workflow
python3 -m pytest -q tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_betting_against_beta_data_loader.py tests/test_bab_data_loader_robust.py 2>&1 | tail -8
```
For coverage, use a **completed** run (prefer bounded suites; programmatic coverage if CLI data collection is flaky):
```bash
python3 - <<'PY'
import coverage, sys, pytest
sys.path.insert(0,'.')
cov=coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()
rc=pytest.main(['-q','tests/test_bab_data_loader_coverage_gaps.py','tests/test_bab_data_loader_robust.py','tests/test_betting_against_beta_data_loader.py','tests/test_bab_data_loader_promote.py','tests/test_bab_messy_data.py','tests/test_bab_zero_silent_error.py','tests/test_bab_cli.py'])
cov.stop(); cov.save()
print('RC',rc)
cov.report(include=['strategies/betting_against_beta/data_loader.py','strategies/betting_against_beta/cli.py'])
PY
```
**Persist exact numbers** (pass/fail/skip, stmts/miss/cover, RC). Expand suite list only if it completes.

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy)
Target remaining misses (prior aggregate context: 345; confirm fresh). **Test-first per batch:** add adversarial/branch tests → run targeted suites → apply smallest correct fix only if behavior violates contract → rerun coverage delta.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s boundaries, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty scalars, promotion/fallback paths, metadata-column drops.
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution/errors, extension routing, `DataFrame`/path dispatch.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; expect `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files, duplicate timestamps. **Never silent wrong success.**

### 2) Campaign B — `cli.py`
Cover missing lines: argparse combinations/conflicts, `--dry-run` must not run backtest/produce side effects beyond contract, `--from-prices`/`--synthetic`/`--data`/`--universe` validation, `--output` path/writability, `--version`, exit codes, rendered errors, scalar coercion edge cases.

### 3) Campaign C — core engines (after A/B progress each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`: close high-value branches; enforce invariants (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets. **No GREEN claim without actual test output.**
- Keep `tests/test_bab_data_loader_coverage_gaps.py` passing; expand it or add focused `tests/test_bab_*coverage*.py` files as needed.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commits/SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising about unfinished work.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
