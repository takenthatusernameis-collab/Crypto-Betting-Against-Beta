# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T08:10:22Z** @ workspace `main` (`HEAD 26a94ff`, `git status --short` clean). `strategies/betting_against_beta/data_loader.py` blob **596ee9e** (unchanged, verified). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta.** `data_loader.py` target-miss floor is **GATE-CLOSED** (B103–B192; no new strict-4 mechanism; do not churn). **Significant progress continues via BAB Package Coverage Campaign.** **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative data_loader baseline (RE-VERIFIED 2026-11-09T08:10Z this session):** `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical file list `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{45,47,48,50,52,55,56,59,63,66,68,72,73,75,76,83,84,85,86,89,96,148,172}.py` (23 files) + `tests/test_bab_data_loader_campaign_d*.py` (10 files) + `tests/test_bab_strategy*.py` (7 files) = **1422 passed, 11 skipped, 77 warnings, `PYTEST_RC 0`**. Coverage `--include='*/strategies/betting_against_beta/data_loader.py'` → **311 miss / 1683 stmts / 82%** (canonical + campaign_d + strategy scope). `pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3467 deselected, 53 warnings**. `326` is **LIVE/GUARD — DO NOT ALTER**.

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed; handlers may wrap as `BABDataError`), **and data_loader 0-delta gate churn** (B103–B192 exhausted; `data_loader.py` floor is baseline/unreachable per recorded evidence — **no more probe/gate-only sessions on data_loader without a concretely demonstrated, non-repeat strict-4 mechanism discovered from a production bug/feature need**).

## Session progress (BAB package campaign)

| Date (UTC) | Module | Before (module miss/%) | After (module miss/%) | Tests / evidence | Gates |
|---|---|---:|---:|---|---|
| 2026-11-09T07:38Z (prior) | `cli.py` | 48 / 85% | 2 / 99% | `tests/test_bab_cli_coverage_push.py` (+25); CLI/report-cli 93 passed, 1 warning | canonical data_loader gate preserved; campaign_d 883/5/3444; no data_loader/probe edits |
| 2026-11-09T07:53Z (prior) | `strategy.py` | 37 / 88% (297 stmts) | **7 / 98%** (297 stmts) | Added `tests/test_bab_strategy_coverage_campaign.py` (**23 tests**, production-realistic mocks/defensive paths). All strategy tests **67 passed**. Minimal real bug fix: `strategy.py:379` used `np.where` while module imports numpy as `_np` → fixed to `_np.where`. Remaining misses 379-385 are deep defensive fallback after array-clamp exception (kept intentionally). | canonical data_loader **556/6/31/`rc=0`, 365/1683/78%**; campaign_d **883/5/3467** |
| **2026-11-09T08:10Z (this session)** | **BASELINE VERIFICATION** | — | — | **Canonical scope (data_loader + campaign_d + strategy): 1422 passed, 11 skipped, 77 warnings, `rc=0`.** `data_loader.py` **311/1683/82%**; `strategy.py` **7/297/98%**; `cli.py` 0% (not in canonical scope); `attribution.py` 97%; `data_sources.py` 42%; `signals.py` **11/128/91%**; `portfolio.py` **34/244/86%**; `shorting.py` 100%; `sizing.py` 96%; `costs.py` 98%; `metrics.py` 96%; `quality.py` 86%; `regime.py` 79%; `beta.py` 52%; `backtest.py` 60%; `config.py` 77%. **Next slice:** `signals.py` (11 misses) and `portfolio.py` (34 misses) — core BAB construction logic. | canonical data_loader **311/1683/82%**; campaign_d **883/5/3467**; all BAB tests **1422/11/77/`rc=0`** |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T08:10:22Z (BAB Package Coverage Campaign, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** deliver **significant, production-relevant BAB package progress** by closing the largest real coverage/test gaps in `strategies/betting_against_beta/` **without** regressing the data_loader baseline or campaign_d. `data_loader.py` miss-floor work is **GATE-CLOSED**.

**Current state (verified 2026-11-09T08:10Z, HEAD 26a94ff, data_loader blob 596ee9e):** canonical scope **1422 passed, 11 skipped, 77 warnings, `rc=0`**. `data_loader.py` **311/1683/82%**; `strategy.py` **7/297/98%**; `cli.py` 0% (not in canonical scope); `attribution.py` 97%; `data_sources.py` 42%; **`signals.py` 11/128/91%**; **`portfolio.py` 34/244/86%**; `shorting.py` 100%; `sizing.py` 96%; `costs.py` 98%; `metrics.py` 96%; `quality.py` 86%; `regime.py` 79%; `beta.py` 52%; `backtest.py` 60%; `config.py` 77%. **Next slice:** `signals.py` and `portfolio.py` (core BAB construction logic; highest value after strategy/cli).

### Uncovered lines requiring real behavior tests (not vacuous mocks):

**signals.py (11 misses):**
- Line 37: `_finite_beta_series` — string-detection path (`str_mask` branch, original string entries zeroed to NaN)
- Line 75: `_reference_generate_bab_signals` — `if n == 0: continue` after single-asset check
- Lines 136-142: `generate_bab_signals` — fallback exception handling when primary numeric coercion fails
- Lines 159-161: `generate_bab_signals` — fallback rank computation when `argsort` fails (exception path)

**portfolio.py (34 misses):**
- Line 29: `_clean_signal_value` — string parsing branch (`isinstance(val, str)`)
- Lines 39-40: `_clean_signal_value` — outer defensive `except` (documented unreachable; fuzz-proven total)
- Line 57: `construct_portfolio` — `None` input early return
- Line 59: `construct_portfolio` — non-DataFrame/empty early return
- Lines 66-67: `construct_portfolio` — `max_turnover` kwargs alias resolution
- Lines 95-96: `construct_portfolio` — signal cleaning exception fallback (returns zero frame)
- Lines 118-119: `construct_portfolio` — long weight assignment exception swallow
- Lines 131-132: `construct_portfolio` — short weight assignment exception swallow
- Lines 152-157: `construct_portfolio` — dollar-neutrality per-row adjustment loop (both sides exist)
- Lines 159-160: `construct_portfolio` — outer exception fallback return
- Line 170: `construct_portfolio` — `max_position_size` positive validation raise
- Line 184: `construct_portfolio` — `max_turnover` positive validation raise
- Lines 193-194: `construct_portfolio` — turnover limit check raise
- Line 196: `construct_portfolio` — turnover `BABDataError` re-raise
- Line 200: `construct_portfolio` — turnover inner `except` (non-numeric `weights_df_prev`)
- Lines 207-208: `construct_portfolio` — risk-checks parameter parsing (bad types → defaults)
- Line 214: `construct_portfolio` — single asset weight limit raise
- Line 217: `construct_portfolio` — gross exposure limit raise
- Line 220: `construct_portfolio` — net exposure (dollar-neutral) limit raise
- Line 259: `enforce_beta_neutrality` — `None`/empty weights or betas early return
- Line 314: `enforce_beta_neutrality` — tolerance check skip when `abs(port_beta - target) <= tol`

### Forced steps (execute in order; heavy work required)

1. **Step 0 — fresh baseline (mandatory):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; rerun canonical scope coverage (API method: `coverage.Coverage(source=['strategies.betting_against_beta'], config_file='/dev/null')` driving `pytest -q --ignore=tests/test_controller_progress_accounting.py` over canonical 23 batch files + 10 campaign_d files + 7 strategy files) → must reproduce **1422/11/77/`rc=0`, data_loader 311/1683/82%**, campaign_d **883/5/3467**. Capture module baseline for `signals.py` and `portfolio.py`. **Record exact numbers before edits.**

2. **Ship tests for `signals.py` and `portfolio.py` slices (minimum one substantial slice each):** cover real behavior (signal ranking/quantiles/NaN handling/string coercion, portfolio dollar-neutral/weight constraints/turnover/risk-checks/beta-neutrality). Use `tmp_path`/monkeypatch/controlled data; no semantic production changes solely for coverage, no vacuous mocks. Add `tests/test_bab_signals_coverage_campaign.py` and `tests/test_bab_portfolio_coverage_campaign.py` (or extend existing targeted files only when cleaner). Minimize production fixes; if a real bug is found, fix it with evidence and a test.

3. **Non-regression gates (all required before declaring done):** rerun canonical scope → **1422/11/77/`rc=0`, data_loader 311/1683/82%**; rerun `pytest -q -k campaign_d` → **883/5/3467**; rerun all BAB tests relevant to touched modules plus full `pytest -q` **excluding** `tests/test_controller_progress_accounting.py` (report counts). Fix failures caused by new tests; minimally fix real bugs with evidence.

4. **Coverage proof:** report before/after miss% for `signals.py` and `portfolio.py`. **A session that only plans, only reruns baseline, or only touches data_loader gate docs is blocked/inefficient.**

5. **Handoff update (durable):** refresh this HANDOFF with timestamp/SHA/blob, exact Step 0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice (e.g., `beta.py`/`backtest.py`/`regime.py`/`data_sources.py` as value dictates). Keep it single-file canonical.

6. **Forbidden:** data_loader probe/gate churn without a new strict-4 mechanism; semantic production changes solely for coverage; altering `322,326` in `data_loader.py`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** materially improved coverage/tests on `signals.py` and/or `portfolio.py` with all gates green and before/after evidence, **plus** refreshed HANDOFF naming the next slice — **OR** **(B)** a concrete, evidence-backed blocker (failing environment/dep/real bug) with minimal reproduction and the exact unblocked next action. No baseline-only exit.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T08:10:22Z** @ `26a94ff` / data_loader blob `596ee9e` verified; **data_loader gate closed; `strategy.py` pushed 88%→98% (+23 tests, 1 defensive `_np.where` fix). Next focus = `signals.py` (11 misses) / `portfolio.py` (34 misses) coverage campaign slice.**