# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T12:25:15Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (local, verified):** `main` @ `938ee68` (`git status --short` clean at recon)
**Durable handoff:** this file only (`./HANDOFF.md`). No duplicates.
**Priority filter (non-negotiable):** repo name = **Crypto-Betting-Against-Beta** → focus **BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (fresh recon, 2026-11-05T12:25Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `pytest -q tests/test_controller_progress_accounting.py --tb=no` → **2 failed, 66 passed** (0.24s).
  - `TestStageSafeChangesPatternSync::{test_python_patterns_are_subset_of_workflow,test_nested_workflow_pattern_is_present_in_workflow}`: `.github/workflows/main.yml` `stage_safe_changes()` missing `*/.github/workflows/*` while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes it.
  - **Operator with `workflows` scope only:** add `*/.github/workflows/*|` adjacent to `.github/workflows/*|` in `main.yml` `stage_safe_changes()`; keep restore/clean/workflow-managed behavior consistent. **Agents without workflow permission must not edit/commit/push `.github/workflows/*`.**
  - **Route around (mandatory):** run BAB verification ignoring `tests/test_controller_progress_accounting.py`; this blocker must never stall BAB work.
- **BAB verification (fresh):**
  - `tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py` → **82 passed, 4 warnings** (6.18s), RC 0.
  - `tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_betting_against_beta_data_loader.py tests/test_bab_data_loader_robust.py` → **146 passed, 6 skipped** (prior run, 9.20s).
  - Expanded slice (programmatic coverage run): `tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_data_loader_promote.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_cli.py` → **162 passed, 6 skipped, 10 warnings, RC 0** (10.45s).
- **Coverage (measured, `coverage.Coverage` programmatic, source=`strategies.betting_against_beta`, expanded slice above):**
  | Module | Stmts | Miss | Cover |
  |---|---:|---:|---:|
  | `data_loader.py` | 1693 | 738 | **56%** |
  | `cli.py` | 318 | 140 | **56%** |
  | `beta.py` | 320 | 214 | **33%** |
  | `portfolio.py` | 244 | 161 | **34%** |
  | `strategy.py` | 297 | 186 | **37%** |
  | `signals.py` | 128 | 76 | **41%** |
  | `backtest.py` | 109 | 54 | **50%** |
  | **TOTAL (slice)** | 3109 | 1569 | **50%** |
- **CLI missing sample (140 misses, expanded slice):** includes `42,46,52,53,61-65,76,78,82,84,86-87,104-105,112,115-118,134-136,139-140,142-143,145-146,148-149,151-167,169,205-207,215,226-228,235-236,...` (helpers + dry-run/output/error/parse branches). **`tests/test_bab_cli.py` has only 14 tests and does not directly exercise `_validate_output_path`, `_coerce_finite_scalar`, `_build_output_summary`, `_json_default`, `_extract_cumulative`, or many arg/error/`--output`/`--universe` edge paths.**
- **Data-loader largest uncovered clusters (line ranges, by size):** `(179-201,23) (81-99,19) (2234-2249,16) (1732-1745,14) (1923-1934,12) (237-247,11) (394-404,11) (2046-2056,11) ...` — target via public APIs/adversarial fixtures.
- **Full BAB-only aggregate coverage across *all* `strategies/betting_against_beta/*.py` with *all* BAB-relevant tests remains unrecorded as final truth — do not claim full GREEN/coverage without a fresh completed run and recorded tail + table.**

## Progress this session (BAB-only)

- Fresh recon completed: SHA `938ee68`, controller blocker reproduced (2 fails; routed around), BAB targeted suites green, expanded coverage slice measured.
- Confirmed `tests/test_bab_data_loader_coverage_gaps.py` (68 tests) present and passing in targeted/expanded runs. **No production BAB code changed. No workflow/infra files touched.**
- Durable handoff refreshed in place with current numbers and a heavy, explicit next-session campaign.

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
| 2 | `data_loader.py` 56% (738 miss / 1693 stmts) — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Integrate `tests/test_bab_data_loader_coverage_gaps.py` into all BAB coverage runs.** Add more test-first adversarial campaigns via public APIs against remaining misses (exchange pivots, datetime epoch-ms/ns branches, `_promote_datetime_column` coercion fallbacks, format loaders, metadata drops, duplicate/NaT handling, format-specific missing deps/IO). Smallest correct fixes only when contract is violated. No broad refactor. | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` 56% (140 miss / 318 stmts); helper/error/arg branches largely untested | **Next BAB agent (parallel batch after A starts)** | Cover missing lines with `capsys`, `tmp_path`, `monkeypatch`: `_validate_output_path` (empty/dir/unwritable/mkdir fail), `_coerce_finite_scalar`, `_build_output_summary` (malformed/Series/list backtest, bad universe), `_json_default`/`_json_safe`, `_extract_cumulative`, arg combos/conflicts, `--dry-run` no side effects, `--output` validation/writability, `--from-prices`/`--synthetic`/`--data`/`--universe` validation, `--version`/exit codes/rendered errors, parse failures. | Measured `cli.py` **≥85%** in fresh aggregate run |
| 4 | Core engines under-covered (`beta` 33%, `portfolio` 34%, `strategy` 37%, `signals` 41%, `backtest` 50% in slice) | **Next BAB agent (after A/B gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes). | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. Use programmatic `coverage.Coverage` if pytest-cov CLI collection is flaky. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**You are on BAB hardening duty.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. Do **not** explore unrelated files. Do **not** stop after one small patch. Do **not** edit/commit/push `.github/workflows/*` or other infra. Work in **verified batches** and record real output in this handoff. Bottleneck #1 is routed around — it must not stop BAB work.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no 2>&1 | tail -6  # expect 2 fails until operator fixes workflow
python3 -m pytest -q tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py 2>&1 | tail -4
```
Coverage (bounded, **completed**; expand only if it finishes):
```bash
python3 - <<'PY'
import coverage, sys, pytest
sys.path.insert(0,'.')
cov=coverage.Coverage(source=['strategies.betting_against_beta'])
cov.start()
rc=pytest.main(['-q','tests/test_bab_data_loader_coverage_gaps.py','tests/test_bab_data_loader_robust.py','tests/test_betting_against_beta_data_loader.py','tests/test_bab_data_loader_promote.py','tests/test_bab_messy_data.py','tests/test_bab_zero_silent_error.py','tests/test_bab_cli.py'])
cov.stop(); cov.save()
print('RC',rc)
cov.report(include=['strategies/betting_against_beta/data_loader.py','strategies/betting_against_beta/cli.py'], show_missing=True)
PY
```
**Persist exact numbers** (pass/fail/skip, stmts/miss/cover, RC). Never claim GREEN without actual output.

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy)
Baseline: **56% (738 miss / 1693 stmts)** in expanded slice. **Test-first per batch:** add adversarial/branch tests → run targeted suites → apply smallest correct fix only if behavior violates contract → rerun coverage delta.
- Prioritize largest uncovered clusters: `(179-201),(81-99),(2234-2249),(1732-1745),(1923-1934),...` and format/datetime/pivot paths.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s boundaries, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty scalars, promotion/fallback paths, metadata-column drops.
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution/errors, extension routing, `DataFrame`/path dispatch.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; expect `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files, duplicate timestamps. **Never silent wrong success.**
- Add/extend `tests/test_bab_data_loader_coverage_gaps.py` or focused `tests/test_bab_data_loader_*_campaign.py`; keep contracts aligned with existing loader tests.

### 2) Campaign B — `cli.py` (immediate high-value; helpers are uncovered)
Baseline: **56% (140 miss / 318 stmts)**; only 14 CLI tests exist. Cover missing branches:
- Direct/helper tests (import-safe): `_validate_output_path`, `_coerce_finite_scalar`, `_build_output_summary`, `_json_default`/`_json_safe`, `_extract_cumulative`.
- `main(argv)`: argparse combos/conflicts, `--dry-run` must not run backtest or write output, `--output` dir/unwritable/parent-mkdir errors, `--from-prices`/`--synthetic`/`--data`/`--universe` validation, `--version`, parse/config/strategy/data errors, exit codes, rendered messages, non-finite/NaN cumulative handling.
- Use `capsys`, `tmp_path`, `monkeypatch`; mock `BABStrategy.run`/loaders where needed for deterministic branch coverage.

### 3) Campaign C — core engines (after A/B progress each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`: close high-value branches; enforce invariants (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output.** No coverage claim without completed measurement.
- Keep `tests/test_bab_data_loader_coverage_gaps.py` passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commits/SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising about unfinished work.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
