# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T12:19:51Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `3234b17` (local main; working tree clean). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed4c14de098562aede46c93c0f242b248` (VERIFIED — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob unchanged/closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** continue the **BAB Package Coverage Campaign** — reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing `data_loader`/`campaign_d` baselines. `data_loader`/`beta` dead-code remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T12:19:51Z @ `3234b17`, deps ok):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883 passed, 5 skipped, rc=0** (baseline preserved; re-verify before new work).
- Full BAB suite excl controller: **timed out at 120s in this runtime** (runtime bottleneck). Collection excl controller: **4530 tests collected**. Targeted `strategy*.py` suite: **70 passed, rc=0**. **Next session MUST run full suite to green in a capable environment before claiming global green; record exact count/rc.** Prior canonical baseline (362f1f2 history): **4445 passed, 35 skipped, rc=0**.

**campaign4 delivered (tests-only; no production code changed):**
- `tests/test_bab_strategy_coverage_campaign4.py` — **3 passed**. Targets `strategy.py` defensive finiteness guard second pass + fallbacks (lines `379-385`).
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, **0 miss**) — CAMPAIGN4 TARGET CLOSED.

**Coverage (`coverage run -m pytest <targets>` + `coverage report -m --include=...`; `.coverage*` cleared before runs):**
- `strategies/betting_against_beta/strategy.py`: **100%** (297 stmts, 0 miss). CLOSED.
- `strategies/betting_against_beta/signals.py`: **97%** (128 stmts, 4 miss). Residual: `37, 75, 139-140` (narrow defensive).
- `strategies/betting_against_beta/portfolio.py`: **94%** (244 stmts, 14 miss). Residual: `39-40, 95-96, 118-119, 131-132, 152-157` (defensive).
- `strategies/betting_against_beta/beta.py`: **33%** (320 stmts, 214 miss) — **CLOSED; dead/unreachable** per `docs/unreachable_proofs.md`.
- `strategies/betting_against_beta/data_loader.py`: **29%** — **GATE CLOSED**.
- `strategies/betting_against_beta/quality.py`: **83%** (183 stmts, **32 miss**: `30, 47-48, 116, 132, 187-188, 209, 211-212, 245-246, 259, 264-290`). **NEXT HEAVY SINGLE SLICE.**
- `strategies/betting_against_beta/cli.py`: **0%** — after quality.py.
- `strategies/betting_against_beta/attribution.py`: **97%** (1 miss line 62). `backtest.py` **51%** (52 miss). `config.py` **71%** (57). `costs.py` **18%** (107). `data_sources.py` **42%** (39). `metrics.py` **69%** (42). `regime.py` **62%** (75). `shorting.py` **64%** (59). `sizing.py` **48%** (92).

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Run full BAB suite excl controller to completion in a capable env; record exact count/rc. Fix regressions before new work.

2. **campaign5 — `quality.py` coverage (NEXT HEAVY SINGLE SLICE):** Baseline **83%** (32 miss: `30,47-48,116,132,187-188,209,211-212,245-246,259,264-290`). Snapshot before/after with `coverage run -m pytest -o addopts='' tests/test_bab_quality*.py`. Create `tests/test_bab_quality_coverage_campaign5.py`. Production-realistic scenarios: data quality checks, missing/non-finite handling, threshold/edge validation, date/index alignment, error paths, return structure/types. Use scoped monkeypatches only for truly defensive branches; if a miss is provably unreachable, document closed-without-edit with evidence. Target materially higher coverage (aim ≥95% or justify residual). No production code changes unless a real bug is found with evidence + regression test.

3. **Non-regression gates (all required):** `campaign_d` 883/5 green; all strategy tests green; full BAB suite green in capable env. Fix real bugs minimally with evidence + regression tests.

4. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`; full-suite 120s timeout in this runtime is a bottleneck — do not claim global green until a capable env runs it to completion.

**ACTIVE:** `quality.py` coverage campaign5 (next heavy slice — 32 misses). **strategy.py 100% CLOSED. beta.py/data_loader gates CLOSED — no churn.**

**Measurable outcome (required next session):** materially improved coverage/tests on `quality.py` (before/after evidence; target ≥95% or documented closed-without-edit) and all gates green, plus refreshed HANDOFF naming the following slice (`cli.py` coverage campaign, currently 0%).

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T12:19:51Z @ `3234b17`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
