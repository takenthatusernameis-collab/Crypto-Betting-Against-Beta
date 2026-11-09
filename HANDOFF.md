# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T15:13:28Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `a66851f5474c835158c79bd6ed275f9c558a976a` (local main; working tree clean before this handoff update). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed4c14de098562aede46c93c0f242b248` (VERIFIED — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob unchanged/closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** Continue the **BAB Package Coverage Campaign**. campaign8 (full-suite global-green verification + campaign7 floor lock) is **COMPLETE/VERIFIED**. campaign7 micro-gaps remain **COMPLETE** — all six target modules at 100% or documented closed-without-edit. No remaining reachable coverage work on `signals.py`, `portfolio.py`, `metrics.py`, `config.py`, `costs.py`, `sizing.py`. `beta.py` (92% on targeted BAB slice; gate-closed dead/unreachable) and `data_loader.py` (49%, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T15:13:28Z @ `a66851f`, deps ok, PYTHONPATH=$PWD, `.coverage*` cleared before canonical runs):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3667 deselected, 53 warnings, rc=0 in 6.32s** (baseline preserved).
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1776 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 146.94s (0:02:26)** (full BAB excl data_loader/controller). **Target 1776/5 MET.**
- Per-file global verification (removes any residual full-suite-timeout excuse): `python3 scripts/run_per_file.py --root . --filter test_betting_against_beta --timeout 300` → **files: 10, green: 10, red: 0**. `python3 scripts/run_per_file.py --root . --filter test_bab_ --timeout 300` → **files: 227, green: 227, red: 0**. Total BAB-focused per-file set (237 files) all GREEN.

**Coverage evidence (targeted BAB slice: `coverage run --source=strategies.betting_against_beta -m pytest -q tests/test_bab_coverage_campaign7_microgaps.py tests/test_betting_against_beta*.py tests/test_bab_*.py -k "not data_loader and not controller"` → 1615 passed, 5 skipped, 2772 deselected, 35 warnings, rc=0 in 131.87s):**
- Campaign7 six-module floor (CONFIRMED):
  - `portfolio.py`: **100%** (244 stmts, 0 miss) — CLOSED.
  - `sizing.py`: **100%** (176 stmts, 0 miss) — CLOSED.
  - `signals.py`: **98%** (128 stmts, **2 miss**: `37, 75`) — documented closed-without-edit in `tests/test_bab_coverage_campaign7_microgaps.py` (control-flow proof: `n==0` unreachable; object-astype branch unreachable via public API).
  - `metrics.py`: **99%** (134 stmts, **1 miss**: `97`) — documented closed-without-edit (turnover mean-NaN unreachable via public API).
  - `config.py`: **99%** (199 stmts, **2 miss**: `101-102`) — documented closed-without-edit (freeze except unreachable on CPython).
  - `costs.py`: **98%** (130 stmts, **2 miss**: `59-60`) — documented closed-without-edit (freeze except unreachable on CPython).
- Other BAB modules (slice): `__init__/attribution/backtest/cli/data/data_sources/errors/portfolio/quality/regime/shorting/sizing/strategy` 100% CLOSED; `beta.py` 92% (gate closed, dead/unreachable); `data_loader.py` 49% (gate closed). BAB package total (slice): **4407 stmts, 898 miss, 80%**.

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Then `python3 -m pytest -q -k "not data_loader and not controller"` → expect **1776/5 rc=0** (or updated count). Fix regressions before new work.

2. **campaign9 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable): BAB package value-add hardening with measurable output.** Campaign7/8 are closed/verified; residual misses are documented closed-without-edit or gate-closed. The next highest-value BAB slice is to **strengthen production-path robustness/tests around real-data & reporting workflows** without touching gate-closed modules/probe churn:
   - Add/extend tests for `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py`, `scripts/generate_real_market_fixture.py`, and `scripts/perf_bench.py` (CLI/script contract, deterministic outputs/fixtures, error paths) — target measurable coverage or at minimum green regression tests with clear assertions. **No edits to `.github/workflows/*`.**
   - If a real bug is found in these scripts, fix minimally with evidence + regression test (production code change allowed only with evidence).
   - Re-confirm campaign7 floor and all BAB gates remain green after changes.
   - Gates that must stay green: `campaign_d` 883/5; full BAB excl data_loader/controller 1776/5; all BAB strategy tests; per-file BAB sets green.
   - Exit criteria: new script-focused tests added and green (record exact new/total counts), campaign7 floor unchanged, refreshed HANDOFF naming the slice after campaign9 with commands/counts/rc.

3. **Non-regression gates (all required):** `campaign_d` 883/5 green; all strategy/BAB tests green; full BAB suite (excl data_loader/controller) 1776/5 green. Fix real bugs minimally with evidence + regression tests.

4. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage/test deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:**
- **Full-suite timeout in this sandbox IS A REMOVED BOTTLENECK, NOT A BLOCKER:** full BAB excl data_loader/controller = 1776/5 rc=0 (146.94s). Per-file BAB verification green (237 files). Do not claim sandbox timeout as a reason to skip verification.
- deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`.
- `quality.py` (campaign5), `cli.py` (campaign6), campaign7, campaign8 are **DONE** — do not re-target. campaign7 residual misses are all documented closed-without-edit.
- Next campaign after campaign9: if script hardening is saturated, consider real-data integration/evaluation docs or `data_loader` only if a concrete production need arises; otherwise the BAB package is at coverage floor.

**ACTIVE:** campaign9 — BAB script/tooling hardening (tests for `bab_backtest_report.py`, `load_real_bab_example.py`, `generate_real_market_fixture.py`, `perf_bench.py`; bug fixes only with evidence). campaign7 floor LOCKED (portfolio/sizing 100%; signals 98% m37,75; metrics 99% m97; config 99% m101-102; costs 98% m59-60 — all closed-without-edit). `beta.py`/`data_loader` gates CLOSED — no churn.

**Measurable outcome (required next session):** campaign9 script-focused tests added and green with exact counts/rc; `campaign_d` 883/5; full BAB excl data_loader/controller ≥1776/5 green; campaign7 floor unchanged; refreshed HANDOFF naming the slice after campaign9.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T15:13:28Z @ `a66851f`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
