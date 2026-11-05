# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T10:21:42Z
**Repo:** `takenthatusernameis-collab/Crypto-Betting-Against-Beta`
**Non-negotiable focus:** **BAB only**. Every action must increase `strategies/betting_against_beta/` correctness, robustness, adversarial handling, or coverage. No sidetracks. Prioritize by repo name.
**Git:** clean tree at `038cb1d7ebc2889f086a280bb0dc7c55e709072f` (`origin/main` in sync). `git status --short` empty before this HANDOFF update.

## Verified state (this session)

- **BAB smoke:** `pytest -q tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_cli.py tests/test_bab_beta_campaign.py tests/test_betting_against_beta.py` → **118 passed**.
- **Full gate blocked by infra (not BAB):** `tests/test_controller_progress_accounting.py` → **2 failed, 66 passed**.
  - **Cause:** `.github/workflows/main.yml` `stage_safe_changes()` excludes `.github/workflows/*` but is missing nested `*/.github/workflows/*` in the `case` pattern list, while `scripts/controller_progress.py` `EXCLUDE_PATTERNS` includes both. Sync tests require parity.
  - **Exact fix (operator with `workflows` scope only):** in `main.yml` `stage_safe_changes()` case pattern, prepend `*/.github/workflows/*|` after `.github/workflows/*|` (same pattern family as nested `.venv`/`__pycache__` entries). Keep restore/clean/workflow-managed behavior consistent. **This agent/token must not commit or push `.github/workflows/*`.**
- **BAB-only quality truth not yet fully re-measured this session** (full `--ignore=tests/test_controller_progress_accounting.py` coverage run is long). **Next agent must run to completion and record real pass/fail/skip + coverage.** Do not claim GREEN without actual output.
- **Known risk focus:** `data_loader.py` is the largest BAB robustness/coverage surface (parsing, index/datetime coercion, shape dispatch, exchange/long/wide detection, validation, optional formats, adversarial NaN/inf/NaT/epoch/tz/duplicates). `cli.py` needs flag/error/exit-code/`--dry-run`/`--from-prices` path coverage.

## Environment

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -V && python3 -m pytest --version
```

## Bottlenecks (remove in order)

| # | Bottleneck | Owner | Action | Done when |
|---|------------|-------|--------|-----------|
| 1 | Workflow/controller exclude-pattern sync | **Operator (workflow perm)** | Fix `main.yml` `stage_safe_changes` to include `*/.github/workflows/*`; push | `pytest -q tests/test_controller_progress_accounting.py` all pass; `bash scripts/bab_gate.sh` unblocked |
| 2 | `data_loader.py` coverage/robustness debt | **Next agent** | Test-first campaigns via public APIs; adversarial inputs → `BABDataError` where contract requires | Measured full-suite BAB coverage ≥90% for `data_loader.py` (or documented justified exceptions) with zero regressions |
| 3 | `cli.py` coverage | **Next agent** | Arg combos, dry-run, prices/returns, conflicts, output/version/errors | ≥85% full-suite coverage |
| 4 | Core engine branch gaps | **Next agent** | `backtest/strategy/beta/signals/portfolio/sizing` invariants + edge branches | High-value gaps closed; no lookahead/dollar-neutral/cost semantics preserved |

## Sacred invariants

- **1-day lagged weights / no lookahead**.
- **NaN/inf/NaT handled explicitly**; invalid parse/validation → `BABDataError` per contract (never silent wrong success).
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable** (`BABStrategy.run`, loaders, config, CLI) unless a tested bug fix is required.
- No force-push/history rewrite. **Never commit `.github/workflows/*`.** Never claim remote persistence without matching remote SHA.

---

## INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY)

**Mission:** Run a **BAB-only hardening marathon** in `strategies/betting_against_beta/`. Establish true test/coverage numbers first, then deliver **multiple verified batches** closing `data_loader.py` and `cli.py` gaps. Do not explore unrelated code. Do not stop after one small fix. Do not edit/commit workflow files.

### Step 0 — Recon (capture real output)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git log --oneline -3 && git rev-parse HEAD origin/main
python3 -m pytest -q tests/test_controller_progress_accounting.py 2>&1 | tail -12
python3 -m coverage erase
python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests 2>&1 | tail -40
python3 -m coverage report --include='strategies/betting_against_beta/*.py' -m 2>&1 | tail -120
```
After operator fixes workflow: also `bash scripts/bab_gate.sh 2>&1 | tail -60`.

### Step 1 — Campaign A: `data_loader.py` (PRIMARY, test-first)
For each batch: write failing/adversarial tests → implement smallest correct fix (if needed) → run targeted `test_bab*data_loader*`/related suites → record coverage delta. Hit missing branches via **public APIs**: `load_returns`, `load_prices`, format loaders, exported validation/coercion.
- **Datetime/index:** tz-aware/naive, epoch ns/us/ms/s + numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty, scalar coercion fallbacks, index promotion, metadata column drops.
- **Shape/dispatch:** exchange-qualified/long/wide detection, pivots, duplicate rows/cols, benchmark resolution, extension routing, csv/json/jsonl/excel/parquet/pickle/hdf paths (mock optional deps via `monkeypatch`/`tmp_path`).
- **Validation/adversarial:** non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, benchmark presence. Malformed inputs must raise `BABDataError` (never silent wrong success).

### Step 2 — Campaign B: `cli.py`
Cover argparse combinations, `--dry-run` (no backtest/side effects), `--from-prices`/`--synthetic`/`--data` validation/conflicts, `--universe`, output paths, exit codes, errors, `--version`. Use `capsys`/`tmp_path`.

### Step 3 — Campaign C: core engines
Close high-value branches in `backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`. Add invariant/property-style checks: no lookahead/1-day lag, dollar neutrality, NaN/inf behavior, costs/slippage, empty/degenerate universes.

### Step 4 — Close-out
- Run targeted + BAB-only regression (or full gate after workflow fix). **Never claim GREEN without test output.**
- Update **this HANDOFF** (UTC timestamp, true counts, coverage deltas, commits/SHAs if any, remaining blockers, next concrete command+targets). Keep this file the single durable source of truth.

**Start at Step 0 now. Do heavy, verified BAB work.**
