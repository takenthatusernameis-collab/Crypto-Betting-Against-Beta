# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T10:27:36Z
**Repo:** `takenthatusernameis-collab/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `3d082bf` (local == `origin/main`; clean working tree verified this session)
**Non-negotiable focus:** **BAB only** — `strategies/betting_against_beta/` correctness, robustness, adversarial handling, and measured coverage. No infra/controller refactors, no workflow edits, no sidetracks. Prioritize by repo name.

## Verified state (this session)

- **Tree:** `git status --short` empty; no duplicate handoff files found (`./HANDOFF.md` only).
- **Infra blocker (not BAB logic):** `pytest -q tests/test_controller_progress_accounting.py` → **2 failed, 66 passed**.
  - Fails because `.github/workflows/main.yml` `stage_safe_changes()` case list excludes `.github/workflows/*` but is missing `*/.github/workflows/*`, while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes both.
  - **Operator with `workflows` scope only:** in `main.yml` `stage_safe_changes()`, add `*/.github/workflows/*|` adjacent to `.github/workflows/*|` (mirror nested-pattern handling). Keep restore/clean/workflow-managed behavior consistent. **Do not commit/push `.github/workflows/*` from agent sessions lacking workflow permission.**
- **BAB tests (measured):** `pytest -q tests/test_bab_data_loader*.py tests/test_bab_cli*.py tests/test_betting_against_beta.py` → **1408 passed, 9 skipped, 95 warnings** (72.92s). BAB loader/CLI/core smoke is green in this subset.
- **Targeted coverage (measured, same subset, `--source=strategies.betting_against_beta`):**
  - `strategies/betting_against_beta/data_loader.py`: **1693 stmts, 348 miss, 79%** (major gap surface; see `coverage report -m` missing lines).
  - `strategies/betting_against_beta/cli.py`: **318 stmts, 124 miss, 61%**.
  - *Not yet measured truth:* full BAB-only suite `pytest -q --ignore=tests/test_controller_progress_accounting.py tests` with coverage — **must be run to completion and recorded** (prior long run timed out in earlier context; do not claim GREEN/full coverage without fresh output).

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

## Bottlenecks

| # | Bottleneck | Owner | Action | Exit criteria |
|---|------------|-------|--------|---------------|
| 1 | Workflow/controller exclude-pattern sync blocks full gate | Operator (`workflows` scope) | Fix `main.yml` `stage_safe_changes` to include `*/.github/workflows/*` | `pytest -q tests/test_controller_progress_accounting.py` passes; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` 79% targeted / unknown full-suite truth | **Next agent (heavy)** | Test-first adversarial campaigns via public APIs; smallest correct fixes only | Measured full-suite BAB coverage **≥90%** for `data_loader.py` (or justified exceptions documented) + zero regressions |
| 3 | `cli.py` 61% targeted | **Next agent** | Arg combos, dry-run side effects, `--from-prices`/`--synthetic`/`--data` conflicts, output/version/errors, exit codes | Measured coverage **≥85%** |
| 4 | Core engine branch/invariant gaps | **Next agent** | `backtest/strategy/beta/signals/portfolio/sizing` edge branches + invariants | High-value gaps closed; invariants preserved |

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY)

**You are on BAB hardening duty.** Do not explore unrelated files. Do not stop after one small patch. Do not edit/commit `.github/workflows/*`. Work in verified batches and record real output.

### 0) Recon — establish truth (run to completion; paste/record key numbers)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git rev-parse --short HEAD origin/main
python3 -m pytest -q tests/test_controller_progress_accounting.py 2>&1 | tail -10
python3 -m coverage erase
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests 2>&1 | tail -60
python3 -m coverage report --include='strategies/betting_against_beta/*.py' -m 2>&1 | tail -140
```
If infra blocker #1 is fixed during your session, also run `bash scripts/bab_gate.sh 2>&1 | tail -80`.

### 1) Campaign A — `data_loader.py` (PRIMARY)
Target the 348+ missing statements (per targeted run) and any new misses from full-suite run. **Test-first per batch:** add adversarial/branch tests → run targeted loader/CLI/core suites → smallest correct fix only if behavior violates contract → rerun coverage delta.
- **Datetime/index coercion:** tz-aware/naive, epoch ns/us/ms/s, numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty scalars, promotion/fallback paths, metadata-column drops.
- **Shape/dispatch/benchmark:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution/errors, extension routing.
- **Formats/optional deps:** csv/json/jsonl/excel/parquet/pickle/hdf — mock missing deps and IO edge cases via `monkeypatch`/`tmp_path`; ensure `BABDataError` on contract violations.
- **Adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, malformed files. **Never** silent wrong success.

### 2) Campaign B — `cli.py`
Cover missing lines/branches: argparse combinations, `--dry-run` (no backtest side effects), `--from-prices`/`--synthetic`/`--data`/`--universe` validation & conflicts, output paths, `--version`, exit codes, error rendering. Use `capsys`, `tmp_path`, `monkeypatch`.

### 3) Campaign C — core engines
`backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`: close high-value branches; add invariant checks (1-day lag/no lookahead, dollar neutrality, NaN/inf stability, costs/slippage, empty/degenerate universes).

### 4) Close-out (required)
- Run targeted suites after each batch + final BAB regression (`--ignore=tests/test_controller_progress_accounting.py` until #1 fixed). **No GREEN claim without actual test output.**
- Update **this single HANDOFF** in place: new UTC timestamp, measured pass/fail/skip, coverage deltas per module, commits/SHAs (if any), remaining blockers, and the next **concrete command + target files/lines/tests**. Keep it actionable and brutal about unfinished work.

**Start at Step 0 now. Produce verified BAB progress, not narration.**
