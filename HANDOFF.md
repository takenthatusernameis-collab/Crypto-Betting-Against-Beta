# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T14:52:00Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (verified 2026-11-05T14:52Z):** `main` @ `29dae1d` (working tree has BAB-only local changes from this session; not committed). **Durable handoff:** **this file only** (`./HANDOFF.md`).
**Priority (repo-name driven, non-negotiable):** **Crypto-Betting-Against-Beta → BAB only**: `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and **measured** coverage. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (re-recon, 2026-11-05T14:52Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no` → **2 failed, 66 passed** (0.22s). `main.yml` `stage_safe_changes()` missing `*/.github/workflows/*` vs `scripts/controller_progress.py`. **Operator with `workflows` scope only.** **Mandatory route-around:** `--ignore=tests/test_controller_progress_accounting.py` for BAB verification.
- **BAB targeted verification (fresh, 2026-11-05T14:52Z):**
  - `python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py` → **82 passed, 4 warnings** (6.23s), RC 0.
  - CLI-focused suite incl. new campaign: `tests/test_bab_cli.py test_bab_cli_console_adversarial.py test_bab_cli_report_hardening.py test_bab_cli_strategy_edge.py test_bab_cli_coverage_campaign.py` → **64 passed, 1 warning** (13.16s), RC 0 (coverage run).
- **Coverage — fresh completed aggregate (2026-11-05T14:52Z, programmatic `coverage.Coverage`):**
  - Scope: `tests/test_bab_data_loader_coverage_gaps.py test_bab_data_loader_robust.py test_betting_against_beta_data_loader.py test_bab_data_loader_promote.py test_bab_messy_data.py test_bab_zero_silent_error.py test_bab_cli.py test_bab_cli_console_adversarial.py test_bab_cli_report_hardening.py test_bab_cli_strategy_edge.py test_bab_cli_coverage_campaign.py` → **226 passed, 7 skipped, 11 warnings, RC 0** (18.57s).
  | Module | Stmts | Miss | Cover | Δ vs 2026-11-05T12:27Z baseline |
  |---|---:|---:|---:|---:|
  | `strategies/betting_against_beta/data_loader.py` | 1693 | 710 | **58%** | **+2pp** (738→710 miss) |
  | `strategies/betting_against_beta/cli.py` | 319 | 48 | **85%** | **+29pp** (140→48 miss; baseline 318 stmts) |
- **This session’s verified changes (local, BAB-only):**
  - `strategies/betting_against_beta/cli.py`: import `BABDataError` at module level; removed redundant shadowing imports in `main()` dry-run/run paths (correctness fix for exception handling scope; revealed by new tests). No public API/flag behavior changes intended.
  - `tests/test_bab_cli_coverage_campaign.py` (**new**): 15 tests covering `_validate_output_path` (empty/mkdir fail/unwritable), `_coerce_finite_scalar`, `_build_output_summary`/`_extract_cumulative` edge cases, `_json_default`/`_json_safe` type coverage, `main()` parse/dry-run/dir/output/strategy-error branches. **All passing.**
  - `tests/test_bab_data_loader_coverage_gaps.py` (**extended**): added adversarial/branch tests for `_normalize_index` (empty numeric, ns/us numeric, parse paths), `_promote_datetime_column`, exchange-format pivots (candle_begin_time/unix), loader paths (dir reject, pickle/parquet/jsonl behaviors, duplicate-column handling explicit). Fixed one malformed new fixture (array length). **82 passed, 1 skipped** for this file alone.
- **Remaining gaps:**
  - `cli.py` (48 misses): remaining are mostly deep defensive/unreachable-ish branches (`os.access` exception pass-through, nested `json_default`/`_json_safe` rare type branches, specific dry-run loader generic-exception prints, run-path generic `BABDataError` wrapping/strategy exceptions, cumulative/print defensive excepts, `_extract_cumulative` rare column/series fallbacks). **Campaign B target (≥85% aggregate) reached on measured slice.** Optional: push further only if low-risk and testable.
  - `data_loader.py` (710 misses): still the **primary risk**. Large uncovered clusters: `_normalize_index`/epoch+tz+coercion fallbacks, `_coerce_to_datetime_scalar` inspection/caller-specific branches, `_promote_datetime_column`, exchange detection/pivots, metadata drops, numeric QC, format loaders (hdf/parquet/json variants/pickle/IO), duplicate/NaT handling, `_run_data_quality_campaign`/validation helpers. **Integrate `tests/test_bab_data_loader_coverage_gaps.py` in every BAB loader coverage run.** Target **≥90%** with test-first adversarial campaigns; **no silent wrong success**; `BABDataError` contract preserved.
  - Core engines not freshly re-measured this session.
- **Transient local artifacts (not committed):** `.coverage`, `.pytest_cache/`, `.hypothesis/`, untracked `tests/test_bab_cli_coverage_campaign.py`, modified files above.

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (**no silent wrong success**).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable:** `BABStrategy.run`, loaders, config, CLI behavior/flags unless a tested bug fix requires change.
- No force-push/history rewrite. No fake persistence/remote claims without matching SHA.

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
| 2 | `data_loader.py` **58% (710 miss / 1693 stmts, 2026-11-05T14:52Z aggregate)** — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | **Keep integrating `tests/test_bab_data_loader_coverage_gaps.py` in all BAB coverage runs.** Add test-first adversarial campaigns via public APIs against remaining misses (datetime/index coercion fallbacks + tz/epoch ns/us/ms/s boundaries, `_coerce_to_datetime_scalar` contract-safe paths, `_promote_datetime_column`, exchange pivots/detection, format loaders csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps/IO, metadata drops, duplicate/NaT, numeric QC, validation/quality helpers). Smallest correct fixes only when contract violated. **No broad refactor; never silent wrong success.** | Measured `data_loader.py` **≥90%** in a **fresh completed aggregate** BAB-loader run with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` residual 48 misses (mostly defensive) — **≥85% target met** | **Next BAB agent (opportunistic, low-risk only)** | Only add deterministic branch tests if they don’t weaken contracts; avoid contorting behavior for coverage. | Stable/no-regression; optional measured lift |
| 4 | Core engines under-covered (not freshly re-measured) | **Next BAB agent (after each material A gain)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes) across `beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`. | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown across all BAB modules/tests | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers + command here. Use programmatic `coverage.Coverage` if pytest-cov CLI collection is flaky. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**Verified 2026-11-05T14:52Z, `main@29dae1d` + local BAB changes (see above).** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. **This is the only durable handoff.** Do **not** explore unrelated files. Do **not** stop after one small patch — deliver multiple verified batches. Do **not** edit/commit/push `.github/workflows/*` or other infra. Work in **verified batches** and record real output in this handoff. Bottleneck #1 is routed around.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no 2>&1 | tail -6  # expect 2 fails
python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_cli.py tests/test_bab_cli_coverage_campaign.py 2>&1 | tail -4
```
Coverage baseline (bounded, **completed**):
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

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy — DO NOT DEFER)
Baseline: **58% (710 miss / 1693 stmts, 2026-11-05T14:52Z)**. **Test-first per batch:** add adversarial/branch tests → run targeted suites → smallest correct fix only if behavior violates contract → rerun coverage delta. **Do not declare A done until `data_loader.py` ≥90% measured in a fresh completed aggregate run with zero regressions and `BABDataError` contract preserved.**
- Prioritize largest uncovered clusters in `data_loader.py` missing ranges (see coverage output); focus on deterministic public-API paths.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s boundaries, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst where supported, NaT/None/inf/nan/empty scalars, `_coerce_to_datetime_scalar`/`_normalize_index` fallbacks (respect existing `BABDataError` contracts).
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection/pivots, duplicate rows/cols, benchmark resolution/errors, extension routing, `DataFrame`/path dispatch, metadata drops.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; expect `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files, duplicate timestamps. **Never silent wrong success.**
- Keep/extend `tests/test_bab_data_loader_coverage_gaps.py` and existing loader contracts aligned.

### 2) Campaign B — `cli.py` (opportunistic)
Target met at **85%**. Only pursue additional misses if safe/deterministic and they improve defensive correctness or reduce real blind spots; do not weaken contracts.

### 3) Campaign C — core engines (after A gains each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`, `metrics.py`, `costs.py`, `sizing.py`, `regime.py`, `shorting.py`, `quality.py`, `attribution.py`, `data_sources.py`: close high-value branches; enforce invariants (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets (ignore controller blocker).
- **No GREEN claim without actual test output.** No coverage claim without completed measurement.
- Keep `tests/test_bab_data_loader_coverage_gaps.py` and `tests/test_bab_cli_coverage_campaign.py` passing.
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, local/commit SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising.

**Start at Step 0 now. Produce verified BAB progress, not narration. Every session must leave measured deltas or a precise, evidence-backed blocker.**
