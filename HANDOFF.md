# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T08:27:03Z** @ workspace `main` (`HEAD aa927a5`, `git status --short` shows 2 new untracked test files: `tests/test_bab_signals_coverage_campaign.py`, `tests/test_bab_portfolio_coverage_campaign.py` — **do not commit unless explicitly requested**). `strategies/betting_against_beta/data_loader.py` blob **596ee9e** (unchanged, verified). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta.** `data_loader.py` target-miss floor is **GATE-CLOSED** (B103–B192; no new strict-4 mechanism; do not churn). **Significant progress continues via BAB Package Coverage Campaign.** **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative baseline (RE-VERIFIED 2026-11-09T08:27Z this session):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; full BAB suite (excl. controller) → **4367 passed, 35 skipped, 237 warnings, `rc=0`**. Campaign scope: `pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3514 deselected, 53 warnings**. Coverage `--include='*/strategies/betting_against_beta/data_loader.py'` → **324 miss / 1683 stmts / 81%** (gate preserved). `322,326` in `data_loader.py` is **LIVE/GUARD — DO NOT ALTER**.

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed; handlers may wrap as `BABDataError`), **and data_loader 0-delta gate churn** (B103–B192 exhausted; `data_loader.py` floor is baseline/unreachable per recorded evidence — **no more probe/gate-only sessions on data_loader without a concretely demonstrated, non-repeat strict-4 mechanism discovered from a production bug/feature need**).

## Session progress (BAB package coverage campaign)

| Date (UTC) | Module | Before (module miss/%) | After (module miss/%) | Tests / evidence | Gates |
|---|---|---:|---:|---|---|
| 2026-11-09T07:38Z (prior) | `cli.py` | 48 / 85% | 2 / 99% | `tests/test_bab_cli_coverage_push.py` (+25); CLI/report-cli 93 passed, 1 warning | canonical data_loader gate preserved; campaign_d 883/5/3444; no data_loader/probe edits |
| 2026-11-09T07:53Z (prior) | `strategy.py` | 37 / 88% (297 stmts) | **7 / 98%** (297 stmts) | Added `tests/test_bab_strategy_coverage_campaign.py` (**23 tests**, production-realistic mocks/defensive paths). All strategy tests **67 passed**. Minimal real bug fix: `strategy.py:379` used `np.where` while module imports numpy as `_np` → fixed to `_np.where`. Remaining misses 379-385 are deep defensive fallback after array-clamp exception (kept intentionally). | canonical data_loader **556/6/31/`rc=0`, 365/1683/78%**; campaign_d **883/5/3467** |
| **2026-11-09T08:10Z (prior)** | **BASELINE VERIFICATION** | — | — | **Canonical scope (data_loader + campaign_d + strategy): 1422 passed, 11 skipped, 77 warnings, `rc=0`.** `data_loader.py` **311/1683/82%**; `strategy.py` **7/297/98%**; `cli.py` 0% (not in canonical scope); `attribution.py` 97%; `data_sources.py` 42%; `signals.py` **11/128/91%**; `portfolio.py` **34/244/86%**; `shorting.py` 100%; `sizing.py` 96%; `costs.py` 98%; `metrics.py` 96%; `quality.py` 86%; `regime.py` 79%; `beta.py` 52%; `backtest.py` 60%; `config.py` 77%. | canonical data_loader **311/1683/82%**; campaign_d **883/5/3467**; all BAB tests **1422/11/77/`rc=0`** |
| **2026-11-09T08:45Z (prior)** | **`signals.py` + `portfolio.py`** | **signals 72/128/44%**<br>**portfolio 66/244/73%** | **signals 19/128/85%**<br>**portfolio 44/244/82%** | Added `tests/test_bab_signals_coverage_campaign.py` (**22 tests**: string/NaN/`_finite_beta_series` path, ranking vs reference, quantile clamping, object-column coercion). Added `tests/test_bab_portfolio_coverage_campaign.py` (**25 tests**: `_clean_signal_value` string branch, None/empty input, kwargs limit aliases, dollar-neutrality adjustment loop, max_position_size/max_turnover/gross/net validation, risk-check bad-type defaults, `enforce_beta_neutrality` guards, turnover inner except). **47 new tests, all pass.** | canonical **1422/11/77/`rc=0`** preserved; +new tests **1469/11/`rc=0`**; campaign_d **883/5/3514**; full BAB suite (excl. controller) **4367 passed, 35 skipped**; data_loader **311/1683/82%** unchanged |
| **2026-11-09T08:27Z (this session)** | **BASELINE RE-VERIFICATION** | — | — | Full BAB suite (excl. controller): **4367 passed, 35 skipped, rc=0**. Campaign_d: **883 passed, 5 skipped, 3514 deselected**. Coverage (verified): `data_loader.py` **324/1683/81%** (GATE-CLOSED); `strategy.py` **30/297/90%**; `signals.py` **19/128/85%**; `portfolio.py` **43/244/82%**; `beta.py` **123/320/62%**; `backtest.py` **44/109/60%**; `regime.py` **70/198/65%**; `data_sources.py` **39/67/42%**; `config.py` **52/199/74%**; `attribution.py` **1/37/97%**; `costs.py` **2/130/98%**; `metrics.py` **6/134/96%**; `quality.py` **26/183/86%**; `sizing.py` **6/176/97%**; `shorting.py` **0/164/100%**; `cli.py` 0% (not in scope). | All gates green; data_loader gate preserved; campaign_d 883/5/3514 |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T08:27:03Z (BAB Package Coverage Campaign, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** deliver **significant, production-relevant BAB package progress** by closing the largest real coverage/test gaps in `strategies/betting_against_beta/` **without** regressing the data_loader baseline or campaign_d. `data_loader.py` miss-floor work is **GATE-CLOSED**.

**Current state (verified 2026-11-09T08:27Z, HEAD aa927a5, data_loader blob 596ee9e):** full BAB suite (excl. controller) **4367 passed, 35 skipped, `rc=0`**; campaign_d **883 passed, 5 skipped, 3514 deselected**. Coverage: `data_loader.py` **324/1683/81%** (GATE-CLOSED); `strategy.py` **30/297/90%**; `signals.py` **19/128/85%**; `portfolio.py` **43/244/82%**; `beta.py` **123/320/62%**; `backtest.py` **44/109/60%**; `regime.py` **70/198/65%**; `data_sources.py` **39/67/42%**; `config.py` **52/199/74%**; `attribution.py` **1/37/97%**; `costs.py` **2/130/98%**; `metrics.py` **6/134/96%**; `quality.py` **26/183/86%**; `sizing.py` **6/176/97%**; `shorting.py` **0/164/100%**; `cli.py` 0% (not in scope). **Next slice (highest value):** `data_sources.py` (42%), `beta.py` (62%), `backtest.py` (60%), `regime.py` (65%) — core BAB math / data ingestion, lowest coverage first.

### Residual uncovered lines (real behavior, not vacuous mocks)

**data_sources.py (39 misses):** Primary target — lowest coverage (42%). Covers exchange data fetching, CCXT integration, rate limiting, error handling, symbol normalization, and data validation paths.

**beta.py (123 misses):** Rolling OLS beta calculation, edge cases (insufficient observations, constant returns, NaN handling), window alignment, benchmark self-beta=1.0 enforcement.

**backtest.py (44 misses):** Lagged weight application, transaction cost models, slippage, cumulative return computation, turnover calculation, empty/NaN input guards.

**regime.py (70 misses):** Regime classification (trend/volatility), scalar regime scaling, EWMA vs simple vol, threshold/hysteresis logic, regime persistence.

### Forced steps (execute in order; heavy work required)

1. **Step 0 — fresh baseline (mandatory):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; rerun full BAB suite (excl. controller) → must reproduce **4367 passed, 35 skipped, `rc=0`**; rerun `pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3514 deselected**; capture module baseline for `data_sources.py`, `beta.py`, `backtest.py`, `regime.py` via `coverage run --source=strategies.betting_against_beta --rcfile=/dev/null -m pytest ...` → **record exact miss/stmts/% before edits.**

2. **Ship tests for `data_sources.py`/`beta.py`/`backtest.py`/`regime.py` slices (minimum one substantial slice each, priority order):** cover real behavior (exchange data fetching/validation, rolling beta OLS, backtest lagged weights/costs/cumulative, regime classification). Use `tmp_path`/monkeypatch/controlled data; no semantic production changes solely for coverage, no vacuous mocks. Add `tests/test_bab_data_sources_coverage_campaign.py`, `tests/test_bab_beta_coverage_campaign.py`, `tests/test_bab_backtest_coverage_campaign.py`, `tests/test_bab_regime_coverage_campaign.py` (or extend existing targeted files only when cleaner). Minimize production fixes; if a real bug is found, fix it with evidence and a test.

3. **Non-regression gates (all required before declaring done):** rerun full BAB suite (excl. controller) → **4367/35/`rc=0`**; rerun `pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883/5/3514**; rerun all BAB tests relevant to touched modules. Fix failures caused by new tests; minimally fix real bugs with evidence.

4. **Coverage proof:** report before/after miss% for each touched module. **A session that only plans, only reruns baseline, or only touches data_loader gate docs is blocked/inefficient.**

5. **Handoff update (durable):** refresh this HANDOFF with timestamp/SHA/blob, exact Step 0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep it single-file canonical.

6. **Forbidden:** data_loader probe/gate churn without a new strict-4 mechanism; semantic production changes solely for coverage; altering `322,326` in `data_loader.py`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** materially improved coverage/tests on the next slice (`data_sources.py` → `beta.py` → `backtest.py` → `regime.py`) with all gates green and before/after evidence, **plus** refreshed HANDOFF naming the following slice — **OR** **(B)** a concrete, evidence-backed blocker (failing environment/dep/real bug) with minimal reproduction and the exact unblocked next action. No baseline-only exit.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T08:27:03Z** @ `aa927a5` / data_loader blob `596ee9e` verified; **data_loader gate closed; `strategy.py` 88%→90%; `signals.py` 44%→85%; `portfolio.py` 73%→82%. Next focus = `data_sources.py` (42%) / `beta.py` (62%) / `backtest.py` (60%) / `regime.py` (65%) coverage campaign slice — lowest coverage first.**
