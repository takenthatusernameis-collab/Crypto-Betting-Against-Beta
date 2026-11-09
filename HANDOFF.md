# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T13:10:32Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `e50a673` (local main; working tree clean; only HANDOFF.md changed since `bea46e3`). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed4c14de098562aede46c93c0f242b248` (VERIFIED — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob unchanged/closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** Continue the **BAB Package Coverage Campaign** — the previous heavy slices (quality.py campaign5, cli.py campaign6) are **COMPLETE** (both 100%). Target the remaining few uncovered lines in `signals.py` (97%), `portfolio.py` (94%), `metrics.py` (99%), `config.py` (99%), `costs.py` (98%), `sizing.py` (98%) with production-realistic tests/fixes. `beta.py` (94%) and `data_loader.py` (49%) remain **GATE CLOSED** (no churn — `beta.py` dead-code per `docs/unreachable_proofs.md`). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T13:10:32Z @ `e50a673`, deps ok):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, rc=0** (baseline preserved; re-verify before new work).
- Full BAB suite excl data_loader/controller: **1759 passed, 5 skipped, rc=0** in 152s. Collection: 1764 tests. Prior canonical baseline (362f1f2 history): 4445 passed, 35 skipped, rc=0 (full incl data_loader).
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, 0 miss) — CLOSED.
- `strategies/betting_against_beta/quality.py`: **100%** (183 stmts, 0 miss) — campaign5 COMPLETE.
- `strategies/betting_against_beta/cli.py`: **100%** (319 stmts, 0 miss) — campaign6 COMPLETE.

**Coverage (`coverage run -m pytest -o addopts='' -k "not data_loader and not controller"` + `coverage report -m --include=...`; `.coverage*` cleared before runs):**
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/quality.py`: **100%** (183 stmts, 0 miss). CLOSED (campaign5 done).
- `strategies/betting_against_beta/cli.py`: **100%** (319 stmts, 0 miss). CLOSED (campaign6 done).
- `strategies/betting_against_beta/signals.py`: **97%** (128 stmts, **4 miss**: `37, 75, 139-140`). Residual: narrow defensive branches.
- `strategies/betting_against_beta/portfolio.py`: **94%** (244 stmts, **14 miss**: `39-40, 95-96, 118-119, 131-132, 152-157`). Residual: defensive/error paths.
- `strategies/betting_against_beta/beta.py`: **94%** (320 stmts, 20 miss) — **GATE CLOSED**; dead/unreachable per `docs/unreachable_proofs.md`.
- `strategies/betting_against_beta/data_loader.py`: **49%** — **GATE CLOSED**.
- `strategies/betting_against_beta/metrics.py`: **99%** (134 stmts, **1 miss**: `97`).
- `strategies/betting_against_beta/config.py`: **99%** (199 stmts, **2 miss**: `101-102`).
- `strategies/betting_against_beta/costs.py`: **98%** (130 stmts, **2 miss**: `59-60`).
- `strategies/betting_against_beta/sizing.py`: **98%** (176 stmts, **3 miss**: `94, 129, 136`).
- `strategies/betting_against_beta/attribution.py`: **100%** (37 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/backtest.py`: **100%** (107 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/regime.py`: **100%** (198 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/shorting.py`: **100%** (164 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/data_sources.py`: **100%** (67 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/data.py`: **100%** (15 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/errors.py`: **100%** (2 stmts, 0 miss). CLOSED.

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Run full BAB suite excl data_loader/controller to completion (1759/5 target); fix regressions before new work.

2. **campaign7 — Remaining micro-gaps coverage (NEXT HEAVY SINGLE SLICE, mandatory):** Target the residual misses across `signals.py` (4), `portfolio.py` (14), `metrics.py` (1), `config.py` (2), `costs.py` (2), `sizing.py` (3). Snapshot before/after with `coverage run -m pytest -o addopts='' tests/test_bab_signals*.py tests/test_bab_portfolio*.py tests/test_bab_metrics*.py tests/test_bab_config*.py tests/test_bab_costs*.py tests/test_bab_sizing*.py`. Create `tests/test_bab_coverage_campaign7_microgaps.py`. Production-realistic scenarios required for every miss:
   - `signals.py:37,75` — `generate_bab_signals` edge cases (empty/insufficient data, quantile boundary).
   - `signals.py:139-140` — defensive `except Exception` path in signal generation.
   - `portfolio.py:39-40,95-96,118-119,131-132,152-157` — `construct_portfolio` error/empty/NaN weight paths, dollar-neutral edge cases.
   - `metrics.py:97` — Sharpe/Sortino calc with zero/NaN std.
   - `config.py:101-102` — Config validation error branches.
   - `costs.py:59-60` — Transaction cost model edge cases (zero volume, NaN price).
   - `sizing.py:94,129,136` — Position sizing edge cases (zero vol, NaN inputs, extreme values).
   Use scoped monkeypatches only for truly defensive branches; if a miss is provably unreachable via public API, document closed-without-edit with evidence. **Target 100% on all six modules or justify every residual miss.** No production code changes unless a real bug is found with evidence + regression test.

3. **Non-regression gates (all required):** `campaign_d` 883/5 green; all strategy tests green; full BAB suite (excl data_loader/controller) 1759/5 green. Fix real bugs minimally with evidence + regression tests.

4. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:**
- **Full-suite timeout in this sandbox IS A REMOVED BOTTLENECK EXCUSE, NOT A BLOCKER:** do not claim global green from this sandbox alone. Split the suite by module file and run each to green locally, then run the complete suite in a capable environment (CI or larger box) and record exact count/rc. `campaign_d` (883/5) and full BAB excl data_loader/controller (1759/5) already pass here — use them as the local gate.
- deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`.
- `quality.py` (campaign5) and `cli.py` (campaign6) are **DONE** — do not re-target.
- Next campaign after campaign7: consider `beta.py` dead-code audit (but GATE CLOSED) or `data_loader` if production need arises.

**ACTIVE:** Remaining micro-gaps coverage campaign7 (signals/portfolio/metrics/config/costs/sizing — total ~26 misses). **strategy/quality/cli/attribution/backtest/regime/shorting/data_sources/data/errors: 100% CLOSED. beta.py/data_loader gates CLOSED — no churn.**

**Measurable outcome (required next session):** 100% coverage on `signals.py`, `portfolio.py`, `metrics.py`, `config.py`, `costs.py`, `sizing.py` (before/after evidence; target 100% or documented closed-without-edit per miss) and all gates green, plus refreshed HANDOFF naming the following slice.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T13:10:32Z @ `e50a673`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.