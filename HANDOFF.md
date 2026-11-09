# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T15:30:26Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `9550376` (local main; working tree clean before this handoff update). Do not commit/push unless explicitly requested.
**Baseline (verified this session @ `9550376`, deps ok, PYTHONPATH=$PWD, `.coverage*` cleared before canonical runs):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, rc=0 in 6.25s** (baseline preserved).
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1776 passed, 5 skipped, rc=0 in 149.67s (0:02:29)** (full BAB excl data_loader/controller). **Target 1776/5 MET.**

**MISSION (repo priority):** Execute **campaign9 — BAB script/tooling hardening**. campaign7/8 are closed/verified; residual misses are documented closed-without-edit or gate-closed. No remaining reachable coverage work on `signals.py`, `portfolio.py`, `metrics.py`, `config.py`, `costs.py`, `sizing.py`. `beta.py` (92% on targeted BAB slice; gate-closed dead/unreachable) and `data_loader.py` (49%, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign9 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable, not skippable):** Strengthen production-path robustness/tests around real-data & reporting workflows without touching gate-closed modules or probe churn:
1. Add/extend green regression tests for `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py`, `scripts/generate_real_market_fixture.py`, and `scripts/perf_bench.py` (CLI/script contract, deterministic outputs/fixtures, error paths) — target measurable coverage or at minimum green regression tests with clear assertions. **No edits to `.github/workflows/*`.**
2. If a real bug is found in these scripts, fix minimally with evidence + regression test (production code change allowed only with evidence).
3. Re-confirm campaign7 floor and all BAB gates remain green after changes.
4. Gates that must stay green: `campaign_d` 883/5; full BAB excl data_loader/controller 1776/5; all BAB strategy tests; per-file BAB sets green.
5. Exit criteria (hard, must be met before this session ends): new script-focused tests added and green (record exact new/total counts + rc), campaign7 floor unchanged, HANDOFF refreshed naming the slice after campaign9 with commands/counts/rc.

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

0. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Then `python3 -m pytest -q -k "not data_loader and not controller"` → expect **1776/5 rc=0** (or updated count). Fix regressions before new work.

1. **campaign9:** Add/extend script-focused tests (see above). Record exact new/total test counts + rc. Do not touch gate-closed modules, `data_loader` lines `322,326`, `.github/workflows/*`, or tracked `probe*`/`debug*`/`ast_probe.py`.

2. **Non-regression gates (all required):** `campaign_d` 883/5 green; full BAB excl data_loader/controller ≥1776/5 green; all BAB strategy tests; per-file BAB sets green. Fix real bugs minimally with evidence + regression tests.

3. **Handoff refresh (durable, single file):** timestamp/SHA, exact commands+counts+rc, modules touched, before/after coverage/test deltas, and the next concrete highest-value slice. Keep this section binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged from prior verified session):**
- `portfolio.py`: **100%** (244 stmts, 0 miss) — CLOSED.
- `sizing.py`: **100%** (176 stmts, 0 miss) — CLOSED.
- `signals.py`: **98%** (128 stmts, **2 miss**: `37, 75`) — documented closed-without-edit.
- `metrics.py`: **99%** (134 stmts, **1 miss**: `97`) — documented closed-without-edit.
- `config.py`: **99%** (199 stmts, **2 miss**: `101-102`) — documented closed-without-edit.
- `costs.py`: **98%** (130 stmts, **2 miss**: `59-60`) — documented closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% (gate closed); `data_loader.py` 49% (gate closed). BAB package total (slice): **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:**
- **Full-suite timeout in this sandbox IS A REMOVED BOTTLENECK, NOT A BLOCKER:** full BAB excl data_loader/controller = 1776/5 rc=0 (149.67s). Per-file BAB verification green (237 files). Do not claim sandbox timeout as a reason to skip verification.
- deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` (optionally `-o addopts=''` to bypass repo addopts quirks) over `pytest-cov`.
- `quality.py` (campaign5), `cli.py` (campaign6), campaign7, campaign8 are **DONE** — do not re-target. campaign7 residual misses are all documented closed-without-edit.
- Next campaign after campaign9: if script hardening is saturated, consider real-data integration/evaluation docs or `data_loader` only if a concrete production need arises; otherwise the BAB package is at coverage floor.

**ACTIVE:** campaign9 — BAB script/tooling hardening (tests for `bab_backtest_report.py`, `load_real_bab_example.py`, `generate_real_market_fixture.py`, `perf_bench.py`; bug fixes only with evidence). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED — no churn.

**Measurable outcome (required next session):** campaign9 script-focused tests added and green with exact counts/rc; `campaign_d` 883/5; full BAB excl data_loader/controller ≥1776/5 green; campaign7 floor unchanged; refreshed HANDOFF naming the slice after campaign9.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T15:30:26Z @ `9550376`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
