# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T12:06:30Z
**Repo:** `Crypto-Betting-Against-Beta` (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/SHA (local, verified):** `main` @ `f71ab58` (`git status --short` clean at handoff write; local `origin/main` tracking)
**Durable handoff:** this file only (`./HANDOFF.md`). No duplicates.
**Non-negotiable focus:** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and measured coverage. Repo name is the priority filter. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (fresh recon, 2026-11-05T12:06Z)

- **Infra blocker (not BAB logic; agent cannot clear):** `pytest -q tests/test_controller_progress_accounting.py --tb=no` → **2 failed, 66 passed** (0.22s).
  - `TestStageSafeChangesPatternSync::{test_python_patterns_are_subset_of_workflow,test_nested_workflow_pattern_is_present_in_workflow}`: `.github/workflows/main.yml` `stage_safe_changes()` missing `*/.github/workflows/*` while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes it.
  - **Operator with `workflows` scope only:** add `*/.github/workflows/*|` adjacent to `.github/workflows/*|` in `main.yml` `stage_safe_changes()`; keep restore/clean/workflow-managed behavior consistent. **Agents without workflow permission must not edit/commit/push `.github/workflows/*`.**
- **BAB targeted verification (fresh):** `pytest -q tests/test_bab_cli.py -x --tb=no` → **27 passed** (14.66s).
- **Coverage (from existing `.coverage` DB, `--source=strategies.betting_against_beta`; not a fresh full BAB aggregate claim):**
  - `strategies/betting_against_beta/data_loader.py` — **80%** (345 miss / 1693 stmts).
  - `strategies/betting_against_beta/cli.py` — **61%** (124 miss / 318 stmts).
  - Prior recorded targeted core snapshot (2026-11-05T11:38Z context): `backtest.py` 50%, `beta.py` 33%, `signals.py` 41%, `portfolio.py` 34%, `strategy.py` 38%; module-set TOTAL ~63% (3109 stmts, 1157 miss). **Full BAB-only aggregate coverage across all `strategies/betting_against_beta/*.py` remains unrecorded as final truth — do not claim full GREEN/coverage without a fresh completed run and recorded tail + table.**

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
| 2 | `data_loader.py` 80% targeted (345 miss, 1693 stmts) — largest BAB risk/coverage surface | **Next BAB agent (heavy, immediate)** | Test-first adversarial campaigns via public APIs; smallest correct fixes only when contract is violated. No broad refactor. | Measured `data_loader.py` **≥90%** with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` 61% targeted (124 miss, 318 stmts) | **Next BAB agent** | Cover missing lines (arg combos/conflicts, dry-run no side effects, file I/O/errors, `--version`/exit codes/rendered errors) using `capsys`, `tmp_path`, `monkeypatch`. | Measured `cli.py` **≥85%** |
| 4 | Core engines under-covered (`beta` 33%, `portfolio` 34%, `strategy` 38%, `signals` 41%, `backtest` 50% — prior snapshot) | **Next BAB agent (after A/B gains each batch)** | Close high-value branches with invariant assertions (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, degenerate universes). | Material measured lift per module; no regressions |
| 5 | Full BAB-only aggregate coverage truth unknown | **Next BAB agent** | Run BAB-only coverage in bounded/completed batches; persist exact numbers here. | Completed coverage table recorded (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**You are on BAB hardening duty.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. Do not explore unrelated files. Do not stop after one small patch. Do not edit/commit/push `.github/workflows/*` or other infra. Work in **verified batches** and record real output in this handoff.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py --tb=no 2>&1 | tail -6  # expect 2 fails until operator fixes workflow
python3 -m coverage erase
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q tests/test_bab_data_loader*.py tests/test_bab_loader*.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_cli*.py tests/test_betting_against_beta_data_loader*.py 2>&1 | tail -12
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' -m 2>&1 | tail -120
```
If budget allows, append core and report targeted modules (or run full BAB-only batches) and **persist exact numbers**.

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy)
Target current misses (345 lines in latest recon). **Test-first per batch:** add adversarial/branch tests → run targeted suites → apply smallest correct fix only if behavior violates contract → rerun coverage delta.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty scalars, promotion/fallback paths, metadata-column drops.
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution/errors, extension routing, `DataFrame`/path dispatch.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; expect `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files, duplicate timestamps. **Never silent wrong success.**

### 2) Campaign B — `cli.py`
Cover 124 misses: argparse combinations/conflicts, `--dry-run` must not run backtest/produce side effects beyond contract, `--from-prices`/`--synthetic`/`--data`/`--universe` validation, output paths, `--version`, exit codes, rendered errors.

### 3) Campaign C — core engines (after A/B progress each batch)
`beta.py`, `portfolio.py`, `strategy.py`, `signals.py`, `backtest.py`: close high-value branches; enforce invariants (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets. **No GREEN claim without actual test output.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commits/SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising about unfinished work.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
