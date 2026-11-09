# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T13:58:40Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `148bfbc640c5a4e0766a87947a13ac0f73e9c2b1` (local main; working tree clean). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed4c14de098562aede46c93c0f242b248` (VERIFIED — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob unchanged/closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** Continue the **BAB Package Coverage Campaign**. campaign7 (remaining micro-gaps) is **COMPLETE** — all six target modules at 100% or documented closed-without-edit. No remaining reachable coverage work on `signals.py`, `portfolio.py`, `metrics.py`, `config.py`, `costs.py`, `sizing.py`. `beta.py` (94%) and `data_loader.py` (49%) remain **GATE CLOSED** (no churn — `beta.py` dead-code per `docs/unreachable_proofs.md`; `data_loader` only if a concretely demonstrated production need arises). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T13:58:40Z @ `148bfbc`, deps ok):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, rc=0** (baseline preserved).
- Full BAB suite excl data_loader/controller → **1778 passed, 5 skipped, rc=0** in 146s (target 1759/5 met/exceeded).
- `strategy.py`: 100% — CLOSED. `quality.py` (campaign5): 100% — CLOSED. `cli.py` (campaign6): 100% — CLOSED.

**Coverage (full BAB suite, `-k "not data_loader and not controller"`, `.coverage*` cleared before runs):**
- `strategy.py` 100%, `quality.py` 100%, `cli.py` 100%, `attribution.py` 100%, `backtest.py` 100%, `regime.py` 100%, `shorting.py` 100%, `data_sources.py` 100%, `data.py` 100%, `errors.py` 100%. ALL CLOSED.
- `portfolio.py`: **100%** (244 stmts, 0 miss) — campaign7 DONE (was 94%).
- `sizing.py`: **100%** (176 stmts, 0 miss) — campaign7 DONE (was 98%).
- `signals.py`: **98%** (128 stmts, **2 miss**: `37, 75`) — both documented closed-without-edit in `tests/test_bab_coverage_campaign7_microgaps.py` (control-flow proof: `n==0` unreachable; object-astype branch unreachable via public API).
- `metrics.py`: **99%** (134 stmts, **1 miss**: `97`) — documented closed-without-edit (turnover mean-NaN unreachable via public API).
- `config.py`: **99%** (199 stmts, **2 miss**: `101-102`) — documented closed-without-edit (freeze except unreachable on CPython).
- `costs.py`: **98%** (130 stmts, **2 miss**: `59-60`) — documented closed-without-edit (freeze except unreachable on CPython).
- `beta.py`: 94% — GATE CLOSED (dead/unreachable). `data_loader.py`: 49% — GATE CLOSED.

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Then full BAB suite excl data_loader/controller → expect **1778/5 rc=0** (or updated count). Fix regressions before new work.

2. **campaign8 — NEXT FOCUS CAMPAIGN (mandatory, not avoidable): Full-suite global-green verification + campaign7 floor lock.**
   - Split the complete suite by module file under `tests/`; run each file to green locally (removes the full-suite-timeout sandbox excuse — do NOT claim global green from this sandbox alone).
   - Run the **complete** suite (every `test_*.py` under `tests/`) in a capable environment (CI or larger box) and record exact count/rc.
   - Re-confirm campaign7 six modules at 100% or documented closed-without-edit using full-suite coverage evidence (`coverage run --source=strategies/betting_against_beta -m pytest -k "not data_loader and not controller"` + `coverage report -m`).
   - Gates that must stay green: `campaign_d` 883/5; full BAB excl data_loader/controller 1778/5; all strategy tests.
   - No production code changes unless a real bug is found with evidence + regression test.
   - Exit criteria: complete suite green in CI/larger box recorded with exact count/rc; campaign7 floor documented; refreshed HANDOFF naming the slice after campaign8.

3. **Non-regression gates (all required):** `campaign_d` 883/5 green; all strategy tests green; full BAB suite (excl data_loader/controller) 1778/5 green. Fix real bugs minimally with evidence + regression tests.

4. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:**
- **Full-suite timeout in this sandbox IS A REMOVED BOTTLENECK EXCUSE, NOT A BLOCKER:** do not claim global green from this sandbox alone. Split the suite by module file and run each to green locally, then run the complete suite in a capable environment (CI or larger box) and record exact count/rc. `campaign_d` (883/5) and full BAB excl data_loader/controller (1778/5) already pass here — use them as the local gate.
- deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`.
- `quality.py` (campaign5) and `cli.py` (campaign6) are **DONE** — do not re-target.
- campaign7 is **DONE** — do not re-target; its residual misses are all documented closed-without-edit.
- Next campaign after campaign8: consider `data_loader` only if a concrete production need arises; otherwise the BAB package is at coverage floor.

**ACTIVE:** campaign8 — full-suite global-green verification + campaign7 floor lock (six modules at 100% or documented closed-without-edit; `beta.py`/`data_loader` gates CLOSED — no churn). `strategy/quality/cli/attribution/backtest/regime/shorting/data_sources/data/errors/portfolio/sizing: 100% CLOSED. signals/metrics/config/costs: 98-99% with all residual misses documented closed-without-edit.`

**Measurable outcome (required next session):** complete suite green in CI/larger box with exact count/rc recorded; campaign7 six modules confirmed at 100% or documented closed-without-edit via full-suite evidence; all gates green; refreshed HANDOFF naming the slice after campaign8.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T13:58:40Z @ `148bfbc`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
