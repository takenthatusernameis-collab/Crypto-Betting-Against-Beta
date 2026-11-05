# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

**Timestamp (UTC):** 2026-11-05T10:20:55Z
**Repo:** `takenthatusernameis-collab/Crypto-Betting-Against-Beta` — **BAB-only focus (non-negotiable).** Every action must increase `strategies/betting_against_beta/` correctness, robustness, adversarial handling, or coverage. No sidetracks. Prioritize by repo name.
**Git:** `HEAD` = `origin/main` = `038cb1d7ebc2889f086a280bb0dc7c55e709072f` (`chore: capture completed workflow run diagnostics`). Working tree clean except this HANDOFF update.

## Verified state (this session, 2026-11-05T10:20Z)

- **Recon:** Clean tree at `038cb1d`; `origin/main` in sync. Deps present in runner user site (`kilo-home/.local/lib/python3.12/site-packages`).
- **BAB smoke:** `pytest -q tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_cli.py tests/test_bab_beta_campaign.py tests/test_betting_against_beta.py` → **118 passed** (env below).
- **Full repo gate (`scripts/bab_gate.sh`) is BLOCKED by infra, not by BAB code:** `tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync` → **2 failed, 66 passed**. Root cause: Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py` includes `*/.github/workflows/*`, but committed `.github/workflows/main.yml` `stage_safe_changes` bash list (line ~1163) is missing `*/.github/workflows/*` (and the restore/clean logic also has a separate top-level workflow handling nuance — see `main.yml:1184-1185,1240`). **Operator with `workflows` permission must fix committed workflow and push** (add nested workflow exclude pattern consistently where the sync test expects). **This agent must NOT commit/push `.github/workflows/*`.**
- **BAB-only gate (authoritative for strategy work while infra blocked):** run all `tests/test_*.py` **excluding** `tests/test_controller_progress_accounting.py` (or run BAB-targeted suites + full BAB module coverage). Full-suite BAB-only run with coverage is long (>120s in this shell with instrumentation); **next agent must run it to completion and record the true number**. Do not claim GREEN without the actual tail.
- **Coverage snapshot (BAB modules, sampled this session — re-measure with full suite):**
  - `data_loader.py` **44%** (1693 stmts, ~945 missing) — **PRIMARY CAMPAIGN TARGET** (many loader/parser/validation branches unhit in sampled run; full suite baseline previously higher—measure accurately).
  - `cli.py` **56%** (~140 missing) — **SECONDARY**.
  - `backtest.py` **50%**, `strategy.py` **37%**, `beta.py` **21%** (sampled), `signals.py` **41%**, `portfolio.py` **34%**, `sizing.py` **20%** in sampled targeted run — **full-suite numbers differ; re-measure before/after each campaign**.

## Environment (required)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -V && python3 -m pytest --version
```

## Bottlenecks (remove to unblock significant progress)

1. **Infra gate blocker (workflow permission):** `main.yml` missing `*/.github/workflows/*` in `stage_safe_changes` exclude list vs `scripts/controller_progress.py` → 2 controller sync failures break `bab_gate.sh`. **Action:** human/operator with workflow scope fixes `.github/workflows/main.yml` (align with Python patterns as tests require) and pushes. **Do not edit/commit workflow files with current token.** Record when fixed; then re-run full `bash scripts/bab_gate.sh`.
2. **Coverage/robustness debt in BAB modules:** `data_loader.py` is the largest risk surface (parsing, index normalization, exchange/long/wide detection, format dispatch, validation, adversarial NaN/inf/NaT/epoch/tz/duplicates). Close gaps via **public APIs and real code paths** (test-first). `cli.py` needs flag/combo/error/exit-code coverage.
3. **Noisy test runtime:** full suite + coverage is slow; use targeted campaigns, then broader BAB regression, then full BAB-only run, then (after workflow fix) full gate.

## Invariants (sacred — never regress)

- **1-day lagged weights / no lookahead** in backtest/portfolio application.
- **NaN/inf/NaT handled explicitly**; raise `BABDataError` on parse/validation failures per contract.
- **Dollar-neutral by default**; transaction costs/slippage semantics preserved.
- **Public APIs stable** (`BABStrategy.run`, loaders, config, CLI flags/behavior) unless a bug fix is required and tested.
- Never claim remote persistence until remote SHA matches. No force-push/history rewrite.
- **Never commit `.github/workflows/*`** with current token.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (MANDATORY, HEAVY WORK)

**Execute a BAB-only hardening marathon on `strategies/betting_against_beta/`. Do recon first, establish true numbers, then deliver multiple verified batches. Do not explore unrelated code. Do not stop at partial progress. Do not commit workflow files.**

### 0) Recon + establish truth (record actual outputs)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
git status --short && git log --oneline -3 && git rev-parse HEAD origin/main
python3 -m pytest -q tests/test_controller_progress_accounting.py 2>&1 | tail -15
# BAB-only regression (may take several minutes; do not background-poll; wait for completion):
python3 -m coverage run --source=strategies/betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests 2>&1 | tail -30
python3 -m coverage report --include='strategies/betting_against_beta/data_loader.py,strategies/betting_against_beta/cli.py,strategies/betting_against_beta/backtest.py,strategies/betting_against_beta/strategy.py,strategies/betting_against_beta/beta.py,strategies/betting_against_beta/signals.py,strategies/betting_against_beta/portfolio.py,strategies/betting_against_beta/sizing.py' -m 2>&1 | tail -80
```
If workflow was fixed by operator, also run `bash scripts/bab_gate.sh` and record tail.

### 1) Campaign A — `data_loader.py` (PRIMARY) — target **≥90%** full-suite coverage
Work in **small, verified batches** (each batch: add/adjust tests → targeted data_loader suites → relevant regression → coverage delta). Inspect missing lines from coverage and hit via **public/exposed APIs** (`load_returns`, `load_prices`, format loaders, validation/coercion helpers as exported/used):
- Datetime/index: tz-aware/naive, epoch ns/us/ms/s and numeric strings/floats, ISO/Z/offsets, ambiguous/dayfirst, NaT/None/inf/nan/empty, scalar/object coercion fallbacks, index promotion from columns, metadata column drops.
- Shape detection: exchange-qualified/long/wide heuristics, pivots, duplicate handling, benchmark resolution.
- Dispatch/parsers: csv/json/jsonl/excel/parquet/pickle/hdf paths (mock optional deps with `monkeypatch`/`tmp_path` where appropriate), extension routing, malformed inputs → `BABDataError` (never silent wrong success).
- `validate_returns_dataframe`: non-numeric coercion, all-NaN/all-NaT, insufficient rows/cols, benchmark presence/derivation edge cases.
**Rules:** test-first; minimal implementation changes only for demonstrably correct behavior/contract; preserve public API; adversarial cases explicit.

### 2) Campaign B — `cli.py` (SECONDARY) — target **≥85%**
Cover argparse combinations, `--dry-run` (no side effects/backtest), `--from-prices`/`--synthetic`/`--data` validation and mutual/conflict paths, `--universe`, output paths, exit codes, error messages, `--version`, config resolution. Use `capsys`/`tmp_path`/subprocess-style invocation only if consistent with existing tests.

### 3) Campaign C — core engines (close high-value branches)
`backtest.py`, `strategy.py`, `beta.py`, `signals.py`, `portfolio.py`, `sizing.py`: target ≥90% where practical. Add invariant/property-style tests: 1-day lag/no-lookahead, dollar neutrality, NaN/inf propagation, costs/slippage, benchmark edge cases, empty/degenerate universes.

### 4) Close-out (every session)
- Run targeted suites for touched areas + BAB-only regression summary (or full gate after workflow fix). **Never claim GREEN without actual test output.**
- Update **this HANDOFF**: UTC timestamp, true pass/fail/skip counts, coverage deltas per module, commits (if any), remaining blockers (including workflow), and the **next concrete command + target file/branches**. Keep it the single durable source of truth.

## Binding rules
1. Recon first; never edit blind. 2. Report truth (infra blocker vs BAB failures). 3. BAB-only; no sidetracks. 4. Test-first; smallest correct change. 5. Zero regressions; preserve invariants/APIs. 6. No force-push/history rewrite. 7. **Never commit `.github/workflows/*`.** 8. Update this HANDOFF at session end.

**Start now:** complete Step 0 with real numbers, then execute Campaign A batches on `data_loader.py` until measurable coverage/risk reduction is achieved.
