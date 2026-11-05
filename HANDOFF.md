# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T10:16:43Z
**Repo:** `Crypto-Betting-Against-Beta` — **BAB-only focus (non-negotiable).** Every action must increase `strategies/betting_against_beta/` correctness, robustness, adversarial handling, or coverage. No sidetracks. Prioritize by repo name.
**Git:** `HEAD` = `origin/main` = `038cb1d7ebc2889f086a280bb0dc7c55e709072f` (`git status --short` clean). **No local-ahead commits. No uncommitted workflow diff detected this session.**

## Verified state (this session)

- **Recon:** Clean tree at `038cb1d`; `origin/main` in sync. Smoke BAB tests passed with deps: `pytest -q tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_cli.py tests/test_bab_beta_campaign.py tests/test_betting_against_beta.py` → **118 passed** (env below).
- **Controller sync tests (BLOCKER for full gate):** `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` → **2 failed, 66 passed** (68 total). Failures: Python `EXCLUDE_PATTERNS` includes `*/.github/workflows/*` (`scripts/controller_progress.py`) but the **committed** `.github/workflows/main.yml` `stage_safe_changes` bash list (line ~1163) is missing `*/.github/workflows/*`. This is a **workflow/Python pattern-sync misalignment in committed state**. `scripts/bab_gate.sh` runs **all** `test_*.py`, so full gate is **not GREEN** until an operator with `workflows` permission adds `*/.github/workflows/*` to the workflow's `stage_safe_changes` exclude list (and commits/pushes it) **or** an authorized non-workflow fix aligns behavior/tests without weakening safety. **Do not commit/push `.github/workflows/*` with the current token.** BAB strategy work is independent; proceed on BAB modules while tracking this blocker explicitly.
- **Full BAB gate not end-to-end re-verified this session** (dependency/env + runtime constraints in this shell). Prior handoff baseline reported `bash scripts/bab_gate.sh` → 2858 passed, 0 failed, 87% before this blocker surfaced; **next agent must re-run gate with correct env and report actual result.**
- **Coverage (last verified baseline, re-measure):** `data_loader.py` **79% (~352 missing, PRIMARY)**, `cli.py` **61% (~124 missing, SECONDARY)**, `backtest.py` 80%, `strategy.py` 89%, `beta.py` 92%, `signals.py` 91%, `portfolio.py` 93%, `sizing.py` 98%.

## Environment (required for tests/gate in this runner)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
# deps installed this session via: pip install --user -r requirements.txt (landed in kilo-home)
```

## Bottlenecks (remove to unblock significant progress)

1. **Full gate blocked by controller/workflow exclude-pattern sync.** Committed `main.yml` missing `*/.github/workflows/*` in `stage_safe_changes` while Python requires it → 2 controller sync failures; `bab_gate.sh` includes them. **Operator action (workflows permission) required to fix workflow**; do not commit workflow files with current token. Track as infra blocker; do not let it stop BAB module hardening.
2. **Coverage gaps:** `data_loader.py` (PRIMARY, ~352 missing) and `cli.py` (SECONDARY, ~124 missing). Highest-value BAB progress is closing these via test-first campaigns using public APIs.

## Invariants (sacred)

- Weights **lagged by 1 day** (no lookahead). NaN/inf/NaT handled explicitly. Raise `BABDataError` on parse/validation failures per contract.
- Dollar-neutral by default; liquidity/transaction-cost/slippage semantics enforced. Keep public APIs stable.
- Never claim remote persistence until remote SHA matches. No force-push/history rewrite.
- **Never commit `.github/workflows/*` with the current token.**

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (MANDATORY, HEAVY WORK)

**BAB-only heavy campaign. Do recon first, run tests with the env above, report the true gate state (including controller sync blocker), then execute multi-batch BAB hardening on `strategies/betting_against_beta/`. Do not explore unrelated code. Do not stop at partial progress. Never commit workflow files.**

### 0) Recon + true status
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git log --oneline -3 && git rev-parse HEAD origin/main
python3 -m pytest -q tests/test_controller_progress_accounting.py 2>&1 | tail -12
# Full gate (includes controller tests; expect 2 sync failures until workflow fixed by operator):
bash scripts/bab_gate.sh 2>&1 | tail -20
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py,strategies/betting_against_beta/backtest.py,strategies/betting_against_beta/strategy.py,strategies/betting_against_beta/beta.py' -m 2>&1 | tail -60
```
Record actual numbers. If only controller-sync workflow failures remain, proceed with BAB campaigns and keep BAB-targeted suites GREEN.

### 1) Campaign A — `data_loader.py` → target >= 90% (close highest-value missing branches)
Inspect missing lines (`coverage report -m`), hit via **public APIs** (`load_returns`, `load_prices`, loaders for csv/json/jsonl/excel/parquet/pickle/hdf, validation/coercion as exposed): datetime scalar coercion (tz/naive, epochs ns/us/ms/s, strings/floats, NaT/None/inf/nan, dayfirst, ISO/Z/offsets, ambiguous/invalid), index normalization/promotion, metadata drops, exchange/long/wide detection + pivots/duplicates, dispatch/extension routing and parser errors → `BABDataError`, `validate_returns_dataframe` (benchmark, all-NaN/all-NaT, non-numeric coercion, insufficient cols/rows). Use `tmp_path`/`monkeypatch`; **test-first**; smallest impl change only if demonstrably correct and unreachable otherwise. Batch loop: add tests → targeted data_loader tests → BAB-focused regression → commit BAB-only gate-green chunks when authorized.

```bash
python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q tests/test_bab_data_loader*.py tests/test_betting_against_beta_data_loader*.py
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py' -m | tail -120
```

### 2) Campaign B — `cli.py` → target >= 85%
Argparse flags/combos, `--dry-run` no side effects/backtest, `--from-prices`/`--synthetic`/`--data` validation, `--universe`, outputs, exit codes/errors, `--version`.

### 3) Campaign C — core engines
High-value branches in `backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`. Add invariant/property tests: 1-day lag/no-lookahead, dollar neutrality, NaN/inf propagation, costs/slippage, benchmark edge cases.

## Binding rules
1. Recon first; never edit blind. 2. Keep BAB suites/gate intent GREEN; never commit RED; report controller/workflow blocker truthfully. 3. BAB-only. 4. Test-first; minimal correct impl changes only when necessary. 5. Zero regressions; preserve invariants/public APIs. 6. No force-push/history rewrite. 7. **Never commit `.github/workflows/*`** with current token. 8. **Update this HANDOFF** (UTC timestamp, true gate/coverage numbers, commits, next concrete bottleneck/command). Single durable source of truth.

**Start now:** run recon with the env above, report actual gate status, then execute Campaign A on `data_loader.py` in heavy, verifiable batches.
