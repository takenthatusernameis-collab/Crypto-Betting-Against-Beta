# HANDOFF: Crypto-Betting-Against-Beta — Canonical Durable Session Handoff
**Timestamp (UTC):** 2026-11-14T10:22:00Z
**Repository:** Crypto-Betting-Against-Beta (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/HEAD:** `main...origin/main`, `fadfcef` (working tree clean at this refresh except this handoff update)
**Single source of truth:** this file. Do not create parallel handoff/session docs. If evidence conflicts, trust live output and update this file.

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T10:22:00Z UTC) — BINDING

**Mission (repo-prioritized):** harden the **Crypto Betting Against Beta (BAB)** strategy (beta estimation, signals/portfolio, backtest/costs/slippage/partial-fill, risk/regime/beta-neutrality, execution/reconciliation, CLI, data loading/quality) from historically “green” to **production-hardened and evidence-backed**. Every session must produce measurable progress with command evidence (RC/counts/timings/excerpts). No status-only work.

### Non-negotiable operating rules
- **Do heavy work every session:** run real commands, capture evidence, and leave the repo measurably better or better-understood. No probe archaeology, no lettered campaign docs, no root probe/debug sprawl.
- **No claim without proof:** historical claims are context only; verify in this environment.
- **Scope discipline:** no `.github/workflows/*` edits, no tracked `.cov*`/cache churn, keep diffs focused/reviewable. Preserve default-path behavior unless a fix is justified by tests + rationale documented here.
- **Canonical handoff only:** update this file (and only this file) as the durable handoff.

### Verified environment/bootstrap (2026-11-14, this session)
- `git status --short --branch` → `## main...origin/main`
- `git rev-parse --short HEAD` → `fadfcef`
- `python3 --version` → `Python 3.12.3` (observed in env), `python3 -m pytest --version` → `pytest 9.2.0`
- Deps import smoke: `python3 -c "import numpy, pandas, scipy; print('deps ok')"` → `deps ok`
- Smoke tests: `python3 -m pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py` → `104 passed, 2 warnings in 12.34s` (RC 0). Warnings: `data_loader.py:811` date parsing fallback in timezone/malformed-date tests (existing behavior).
- CLI smoke: `python3 -m strategies.betting_against_beta.cli --synthetic` → `Final cumulative return: 0.413704`, `Periods: 252` (RC 0).
- Tooling: `python3 -m ruff --version` → `ruff 0.17.5`. `pyproject.toml` already contains `[tool.ruff]`/`[tool.ruff.lint]` config.
- Repo scale: `308` files under `tests/`; real-data fixtures present in `tests/fixtures/` (`real_market_prices*.csv`, `real_market_returns.csv`, `real_data_defects.csv`, etc.).

### Current blocker / in-progress baseline (must be resolved first)
- **Full-suite baseline was started but not completed in this session:**
  `python3 -m pytest -q --tb=line --durations=20 2>&1 | tee /tmp/full_pytest_baseline.log` (bg process `bgp_1d98863ba0015rn1jQ3tLCMc1M`) was **still running** at last check (~77% by log tail, heavy `ss/sss` skip clusters observed, no failures seen in tail). Log: `/tmp/full_pytest_baseline.log`.
- **Immediate action for next agent:** do not assume completion. Check `tail -n 60 /tmp/full_pytest_baseline.log` and process status; if still running, wait/monitor to completion and capture final summary (pass/fail/skip, time, slowest 20, any failures/flakes) with RC. If interrupted/lost, rerun the full baseline and record evidence. **Fix any real failures at root cause** (no assertion weakening), rerun impacted scope then full suite as feasible. This is the gate for further work.

### Priority campaign (execute in order)
1. **Full-suite health baseline (HIGHEST, gate):** complete/recover the run above with full evidence. Promote final counts/timing/slowest-tests into this handoff.
2. **Static analysis / in-repo quality gate (HIGH, actionable now):**
   - `python3 -m ruff check .` currently reports `1977 errors` (`414` fixable, `449` unsafe-fixable) at HEAD (sample: `ast_probe.py` E501/PERF401, widespread I001/formatting and other issues across repo including root probes/scripts/tests). `pyproject.toml` config exists but the tree is **not clean** under it.
   - Deliverable: make `ruff check` pass for a clearly defined, high-signal scope (or whole repo if feasible) with behavior-preserving fixes and minimal config tuning if justified; record exact commands, before/after counts, and rationale. Prefer targeted/scoped cleanup over noisy churn; do not break semantics.
3. **Performance profiling & targeted optimization (HIGH):** profile hot/slow areas with evidence (`--durations`, `time`, `cProfile`/targeted benchmarks) focusing on `beta.py` rolling beta, `backtest.py` lag/cost/partial-fill, `costs.py`, `execution.py`/reconciliation, CLI end-to-end. Implement ≥1 behavior-preserving optimization or justified fix with before/after measurements and tests proving equivalence (synthetic + fixture data).
4. **Real-data & edge hardening (MEDIUM-HIGH):** exercise `tests/fixtures/real_market_prices*.csv`, `real_market_returns.csv`, defect fixtures via CLI and `BABStrategy`/loader/quality paths. Add/strengthen tests for timezone/coercion, missing symbols, NaN/inf/duplicate dates, and execution/cost realism edges with evidence. No external/venue credentials—do not fake.
5. **Close with evidence:** update this file with timestamp, HEAD, commands run (with RC), results, files changed, regressions/risks, and the next binding task.

### Known focus hints (validate, don’t assume)
- Full suite is large/slow (308 test files; prior sessions noted multi-minute runtime and slow execution/replay/CLI tests) — expect long wall time.
- Root contains many `probe_*`/`debug_*`/`ast_probe.py` artifacts that currently contribute to ruff noise; treat carefully (avoid churny archaeology; clean only if needed for a passing quality gate and keep behavior intact).
- `research_state/workflow_run_diagnostics.jsonl` holds historical CI/agent diagnostics (`kilo_edit_tool_invalid_arguments` seen historically) — non-blocking unless reproduced live.
- `AGENT_HANDOFF.md` is pointer-only; `AGENT_TASK_2026-11-14.md` is superseded.

### Escalation/blockers
- If environment prevents completing baseline, capture exact errors, remediate minimally, document, and proceed with highest-value unblocked heavy work (e.g. ruff cleanup/fixes) while preserving evidence trail.

## Session log
- **2026-11-14T09:35:56Z (prior, handoff consolidation):** Established canonical handoff, superseded parallel task doc, no product/test evidence collected.
- **2026-11-14T10:22:00Z (this session, evidence-gathering):**
  - Audited repo/config/docs/tests/fixtures (`ls`, `find`, `README.md`, `pyproject.toml`, `tests/fixtures/*`), confirmed HEAD `fadfcef`, clean baseline, pytest 9.2.0, ruff 0.17.5, 308 test files.
  - Ran smoke: `pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py` → **104 passed, 2 warnings, 12.34s, RC 0**. Ran `python3 -m strategies.betting_against_beta.cli --synthetic` → **Final cumulative return 0.413704, Periods 252, RC 0**.
  - Assessed lint: `ruff check .` → **1977 errors** (414 fixable, 449 unsafe) despite ruff config present.
  - Started full-suite baseline `pytest -q --tb=line --durations=20` to `/tmp/full_pytest_baseline.log` (bgp `bgp_1d98863ba0015rn1jQ3tLCMc1M`); **not completed by session end** (last observed ~77%, skips present, no failures seen in tail). **No full-suite summary available yet.**
  - Files changed this session: `HANDOFF.md` only (durable handoff refresh). No product code/tests modified.
  - **Next binding task:** complete/recover full-suite baseline with definitive evidence, then drive ruff gate cleanup (high-signal/behavior-preserving) and proceed down priority list.
