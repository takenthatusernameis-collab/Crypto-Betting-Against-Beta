# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T11:31:38Z
**Repo:** `takenthatusernameis-collab/Crypto-Betting-Against-Beta`
**Branch/SHA (local):** `main` @ `682d8c7` (HEAD == `origin/main` at check; working tree clean except this handoff update in progress)
**Non-negotiable focus:** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and measured coverage. Repo name is the priority filter: every action must advance BAB quality. No infra/controller refactors, no workflow commits/pushes, no sidetracks.

## Verified state (this session)

- **Tree:** no duplicate durable handoff files found (only `./HANDOFF.md`). Prior commits are checkpoint-only.
- **Infra blocker (not BAB logic; agent cannot clear):** `pytest -q tests/test_controller_progress_accounting.py` → **2 failed, 66 passed** (0.23s).
  - Failures: `TestStageSafeChangesPatternSync::test_python_patterns_are_subset_of_workflow` and `test_nested_workflow_pattern_is_present_in_workflow` — `.github/workflows/main.yml` `stage_safe_changes()` is missing `*/.github/workflows/*` while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes it.
  - **Operator with `workflows` scope only:** add `*/.github/workflows/*|` adjacent to `.github/workflows/*|` in `main.yml` `stage_safe_changes()`; keep restore/clean/workflow-managed behavior consistent. **Agents without workflow permission must not edit/commit/push `.github/workflows/*`.**
- **BAB subsets (measured, recon 2026-11-05T11:30:47Z):**
  - `pytest -q tests/test_bab_data_loader*.py tests/test_bab_loader*.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_cli*.py tests/test_betting_against_beta_data_loader*.py` → **1445 passed, 15 skipped, 105 warnings** (61.45s).
  - `pytest -q tests/test_bab_backtest*.py tests/test_bab_beta*.py tests/test_bab_signals*.py tests/test_bab_portfolio*.py tests/test_bab_sizing*.py tests/test_bab_strategy*.py tests/test_betting_against_beta.py tests/test_betting_against_beta_costs.py tests/test_betting_against_beta_metrics*.py tests/test_betting_against_beta_quality.py tests/test_betting_against_beta_regime.py tests/test_betting_against_beta_shorting.py tests/test_betting_against_beta_sizing.py` → **709 passed, 14 warnings** (44–46s).
  - These subsets are green; warnings exist (runtime/numpy/runpy) — do not hide regressions behind warning noise.
- **Targeted coverage (measured, `--source=strategies.betting_against_beta`, loader+CLI subset):** `data_loader.py` **1693 stmts, 345 miss, 80%**; `cli.py` **318 stmts, 124 miss, 61%**. Missing-line report is the live gap map (`coverage report -m`).
- **Full BAB-only suite with coverage:** **not yet completed to verified truth in this session**. Prior attempts timed out or produced no aggregate data in interrupted cross-process runs. **Do not claim GREEN/full BAB coverage without a fresh completed run and recorded tail + coverage table.**

## Sacred invariants (never regress)

- **No lookahead:** weights lagged 1 day / lag semantics preserved.
- **Robust parsing:** NaN/inf/NaT/non-numeric/ambiguous datetime handled explicitly; invalid parse/validation → `BABDataError` per contract (no silent wrong success).
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
| 1 | Workflow/controller exclude-pattern sync blocks full gate (`main.yml` missing `*/.github/workflows/*` in `stage_safe_changes`) | **Operator with `workflows` scope** | One-line-equivalent fix in workflow file; agents lacking workflow permission **must not touch it**. Route BAB work via `--ignore=tests/test_controller_progress_accounting.py`. | `pytest -q tests/test_controller_progress_accounting.py` passes; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` 80% targeted (345 miss, 1693 stmts) — largest BAB risk surface | **Next BAB agent (heavy, immediate)** | Test-first adversarial campaigns via public APIs; smallest correct fixes only when contract is violated. Do not refactor broadly. | Measured coverage **≥90%** for `data_loader.py` with zero regressions and `BABDataError` contract preserved |
| 3 | `cli.py` 61% targeted (124 miss, 318 stmts) | **Next BAB agent** | Arg combos/conflicts, dry-run no-side-effects, file I/O/errors, `--version`, exit codes, rendered errors. | Measured coverage **≥85%** |
| 4 | Full BAB-only aggregate coverage truth unknown (long-running suite) | **Next BAB agent** | Run BAB-only coverage in bounded batches or one completed run; persist exact numbers in this handoff. | Completed coverage table recorded here (no timeout/incomplete claims) |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, BAB-ONLY)

**You are on BAB hardening duty.** Repo name = `Crypto-Betting-Against-Beta`; prioritize BAB correctness/robustness/coverage above everything else. Do not explore unrelated files. Do not stop after one small patch. Do not edit/commit/push `.github/workflows/*` or other infra. Work in verified batches and record real output in this handoff.

### 0) Recon — establish truth (run to completion; record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD
python3 -m pytest -q tests/test_controller_progress_accounting.py 2>&1 | tail -10  # expected 2 fails until operator fixes workflow
python3 -m coverage erase
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q tests/test_bab_data_loader*.py tests/test_bab_loader*.py tests/test_bab_messy_data.py tests/test_bab_zero_silent_error.py tests/test_bab_cli*.py tests/test_betting_against_beta_data_loader*.py 2>&1 | tail -12
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py' -m 2>&1 | tail -120
```
Baseline recorded 2026-11-05T11:30:47Z: loader/CLI subset **1445 passed, 15 skipped**; `data_loader.py` **80% (345 miss / 1693 stmts)**; `cli.py` **61% (124 miss / 318 stmts)**.
If time permits in the same session, get full BAB aggregate truth with bounded scope: `python3 -m coverage run --append --source=strategies.betting_against_beta -m pytest -q -x --tb=no tests/test_bab*.py tests/test_betting_against_beta*.py 2>&1 | tail -20` then full `coverage report --include='strategies/betting_against_beta/*.py' -m`. If it exceeds budget, split into module batches and record partial-but-verified numbers.

### 1) Campaign A — `data_loader.py` (PRIMARY, heavy)
Target current misses (345 lines / 80% targeted). **Test-first per batch:** add adversarial/branch tests → run targeted loader/CLI suites → apply smallest correct fix only if behavior violates contract → rerun coverage delta.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty scalars, promotion/fallback paths, metadata-column drops.
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution/errors, extension routing, `DataFrame`/path dispatch.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; expect `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files, duplicate timestamps. **Never silent wrong success.**

### 2) Campaign B — `cli.py`
Cover 124 misses: argparse combinations, `--dry-run` (must not run backtest / produce side effects beyond contract), `--from-prices`/`--synthetic`/`--data`/`--universe` validation & conflicts, output paths, `--version`, exit codes, error rendering. Use `capsys`, `tmp_path`, `monkeypatch`.

### 3) Campaign C — core engines (after A/B progress each batch)
`backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`: close high-value branches; add invariant checks (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression subsets above. **No GREEN claim without actual test output.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commits/SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and uncompromising about unfinished work.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
