# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T16:14:00Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `58349c4` (local main == `origin/main`, working tree clean; production code unchanged since `3bc2586`, only HANDOFF.md touched by session checkpoint commit). Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `58349c4`, deps installed via `python3 -m pip install --user numpy pandas scipy pytest hypothesis coverage`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3691 deselected, 53 warnings, rc=0 in 5.17s** (baseline preserved).
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1800 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 122.32s** (FULL RUN COMPLETED this session; prior verified baseline 1776/5 at `9550376`; count rose to 1800 due to added script/session test coverage — record this as the new verified floor, no regression).
- BAB regression sanity samples green: `tests/test_bab_strategy_edge.py tests/test_bab_backtest_*.py tests/test_bab_portfolio_*.py` → **125 passed, 1 warning, rc=0** (use actual file globs; legacy names like `test_bab_backtest.py` do not exist as written).

**campaign9 — COMPLETED (script/tooling hardening):** `tests/test_scripts_campaign9.py` tracked (committed `c5d0c3c`). Script suite: `tests/test_bab_backtest_report.py tests/test_bab_report_strict_json.py tests/test_bab_cli_console_adversarial.py tests/test_bab_report_cli_edge_cases.py tests/test_bab_cli_report_hardening.py tests/test_scripts_campaign9.py` → **84 passed, rc=0**. Broader sanity incl. `test_bab_zero_silent_error.py` → **91 passed, rc=0**. No production code changes required/found in target scripts; no edits to `.github/workflows/*`, gate-closed modules, `data_loader` 322/326, or tracked `probe*`/`debug*`/`ast_probe.py`.

**MISSION (repo priority):** Execute **campaign10 — post-script BAB hardening / verification closure**. campaign7/8/9 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (40 miss / 98%, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign10 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Verification closure — COMPLETE this session:** full excl data_loader/controller baseline recorded as **1800/5 rc=0** (was 1776/5). No regression. Do not re-run unless making non-script BAB changes.
2. **Next highest-value BAB slice (choose exactly one, execute, measure):** (a) strengthen `scripts/run_per_file.py` / `scripts/bab_gate.sh` contract tests + deterministic behavior where testable without workflow edits; OR (b) add green regression tests for `strategies/betting_against_beta` CLI/reporting integration edges still under-tested (`cli.py`/`data_loader` adapter boundaries) **without touching data_loader gate-closed internals/322,326 and without probe churn**; OR (c) real-data evaluation/reporting reproducibility tests using committed fixtures (`tests/fixtures/returns.json`) (no new external data). Pick the slice with measurable, non-gate-churning value; record before/after evidence (counts+rc).
3. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
4. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl data_loader/controller ≥1800/5 (or updated verified count with explanation); all BAB strategy/script tests touched; per-file BAB sets green as applicable.
5. **No** `.github/workflows/*` edits, no gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326), no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits, no weakening `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order):**
0. Step 0 gates: deps import ✓; `campaign_d` 883/5 ✓ rc=0; full excl **1800/5 ✓ rc=0** (complete — recorded as new floor). Fix regressions before new work.
1. Execute campaign10 slice with concrete tests/assertions; record exact counts/rc.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — documented closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 1693 stmts / 98% gate closed (remaining miss `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` — all mechanism-closed per `docs/unreachable_proofs.md`; structural-dead/inspect-gated, **DO NOT ALTER**). BAB package slice: **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** full BAB excl data_loader/controller is ~2 min — now completed (was the open incomplete run); not a blocker going forward. `rm -f .coverage .coverage.*` before canonical runs. campaign7 residual misses remain closed-without-edit.

**ACTIVE:** campaign10 — verification closure complete (1800/5 floor recorded) + next highest-value BAB hardening slice (no gate-churn). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T16:14:00Z @ `58349c4`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
