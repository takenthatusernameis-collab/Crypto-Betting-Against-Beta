# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T15:57:57Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `3bc2586` (local main == `origin/main`, working tree clean at session start; this handoff refresh is the intended edit). Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `3bc2586`, deps installed via `python3 -m pip install --user numpy pandas scipy pytest hypothesis coverage`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical campaign_d run):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3691 deselected, 53 warnings, rc=0 in 5.59s** (baseline preserved).
- Full `python3 -m pytest -q -k "not data_loader and not controller"` was started but **not completed within this session's tool-harness window** (prior verified baseline @ 9550376 was **1776 passed, 5 skipped, rc=0 in 149.67s**; no BAB production/strategy code changed in this session). **Next agent must run it to completion and record exact count/rc before non-script BAB changes.**

**campaign9 — COMPLETED (script/tooling hardening):** Added/committed green regression coverage for target scripts (CLI/script contract, deterministic outputs/fixtures, error paths). **No production code changes were required/found** in the four target scripts during this verification pass; no edits to `.github/workflows/*`, gate-closed modules, `data_loader` 322/326, or tracked `probe*`/`debug*`/`ast_probe.py`.
- `tests/test_scripts_campaign9.py` is tracked (committed in `c5d0c3c`; present in HEAD ancestry). **24 passed, rc=0 in 16.88s**.
- Target script suite (campaign9 + existing report/console hardening): `python3 -m pytest tests/test_bab_backtest_report.py tests/test_bab_report_strict_json.py tests/test_bab_cli_console_adversarial.py tests/test_bab_report_cli_edge_cases.py tests/test_bab_cli_report_hardening.py tests/test_scripts_campaign9.py -q` → **84 passed, rc=0 in 29.25s**.
- Broader script-related sanity: `python3 -m pytest tests/test_scripts_campaign9.py tests/test_bab_backtest_report.py tests/test_bab_report_strict_json.py tests/test_bab_cli_console_adversarial.py tests/test_bab_report_cli_edge_cases.py tests/test_bab_cli_report_hardening.py tests/test_bab_zero_silent_error.py -q` → **91 passed, rc=0 in 29.87s**.
- BAB regression sanity samples (green): `tests/test_bab_strategy_edge.py tests/test_bab_backtest_*.py tests/test_bab_portfolio_*.py` → **125 passed, 1 warning, rc=0 in 10.05s**. Core module-name glob check revealed some legacy test filenames assumed in prose do not exist as written (`test_bab_backtest.py`, `test_bab_strategy.py` etc.); use actual file globs when verifying.

**MISSION (repo priority):** Execute **campaign10 — post-script BAB hardening / verification closure**. campaign7/8/9 are closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (49%, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign10 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Verification closure (required first):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` — record exact count/rc and compare to **1776/5**. Fix any regression before new work.
2. **Next highest-value BAB slice (choose one, execute, measure):** (a) strengthen `scripts/run_per_file.py` / `scripts/bab_gate.sh` contract tests + deterministic behavior where testable without workflow edits; OR (b) add green regression tests for `strategies/betting_against_beta` CLI/reporting integration edges still under-tested (`cli.py`/`data_loader` adapter boundaries) **without touching data_loader gate-closed internals/322,326 and without probe churn**; OR (c) real-data evaluation/reporting reproducibility tests using committed fixtures (no new external data). Pick the slice with measurable, non-gate-churning value; record before/after evidence.
3. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
4. Gates that must stay green: `campaign_d` 883/5; full BAB excl data_loader/controller ≥1776/5 (or updated verified count with explanation); all BAB strategy/script tests touched; per-file BAB sets green as applicable.
5. **No** `.github/workflows/*` edits, no gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326), no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits, no weakening `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order):**
0. Step 0 gates: deps import; `campaign_d` 883/5; full excl 1776/5 (complete it this session). Fix regressions before new work.
1. Execute campaign10 slice with concrete tests/assertions; record exact counts/rc.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — documented closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 49% gate closed. BAB package slice: **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** full BAB excl data_loader/controller is ~2.5 min in prior verified runs — run to completion (not a blocker). `rm -f .coverage .coverage.*` before canonical runs. campaign7 residual misses remain closed-without-edit.

**ACTIVE:** campaign10 — verification closure + next highest-value BAB hardening slice (no gate-churn). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T15:57:57Z @ `3bc2586`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
