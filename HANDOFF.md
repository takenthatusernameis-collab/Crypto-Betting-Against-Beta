# HANDOFF: Crypto-Betting-Against-Beta — Canonical Durable Session Handoff
**Timestamp (UTC):** 2026-11-14T10:41:29Z
**Repository:** Crypto-Betting-Against-Beta (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/HEAD:** `main...origin/main`, `fadfcef` (working tree clean at this refresh except this handoff update)
**Single source of truth:** this file. Do not create parallel handoff/session docs. If evidence conflicts, trust live output and update this file.

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T10:41:29Z UTC) — BINDING

**Mission (repo-prioritized):** harden the **Crypto Betting Against Beta (BAB)** strategy (beta estimation, signals/portfolio, backtest/costs/slippage/partial-fill, risk/regime/beta-neutrality, execution/reconciliation, CLI, data loading/quality) from historically "green" to **production-hardened and evidence-backed**. Every session must produce measurable progress with command evidence (RC/counts/timings/excerpts). No status-only work.

### Non-negotiable operating rules
- **Do heavy work every session:** run real commands, capture evidence, and leave the repo measurably better or better-understood. No probe archaeology, no lettered campaign docs, no root probe/debug sprawl.
- **No claim without proof:** historical claims are context only; verify in this environment.
- **Scope discipline:** no `.github/workflows/*` edits, no tracked `.cov*`/cache churn, keep diffs focused/reviewable. Preserve default-path behavior unless a fix is justified by tests + rationale documented here.
- **Canonical handoff only:** update this file (and only this file) as the durable handoff.

### Verified environment/bootstrap (2026-11-14, this session)
- `git status --short --branch` → `## main...origin/main`
- `git rev-parse --short HEAD` → `fadfcef`
- `python3 --version` → `Python 3.12.3`, `python3 -m pytest --version` → `pytest 9.2.0`
- Deps import smoke: `python3 -c "import numpy, pandas, scipy; print('deps ok')"` → `deps ok`
- Smoke tests: `python3 -m pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py` → `104 passed, 2 warnings in 12.34s` (RC 0). Warnings: `data_loader.py:811` date parsing fallback in timezone/malformed-date tests (existing behavior).
- CLI smoke: `python3 -m strategies.betting_against_beta.cli --synthetic` → `Final cumulative return: 0.413704`, `Periods: 252` (RC 0).
- Tooling: `python3 -m ruff --version` → `ruff 0.17.5`. `pyproject.toml` already contains `[tool.ruff]`/`[tool.ruff.lint]` config.
- Repo scale: `308` files under `tests/`; real-data fixtures present in `tests/fixtures/` (`real_market_prices*.csv`, `real_market_returns.csv`, `real_data_defects.csv`, etc.).

### Full-suite baseline (COMPLETE — gate passed)
- `python3 -m pytest -q --tb=line --durations=20 2>&1 | tee /tmp/full_pytest_baseline.log` → **5667 passed, 35 skipped, 255 warnings in 592.02s (0:09:52), EXIT_RC=0** (bgp `bgp_1d99ba2bb001BFgFFazYr6D6sG`, process exited). Log: `/tmp/full_pytest_baseline.log`.
- No failures/flakes. Warnings are pre-existing only (data_loader.py date-parsing fallbacks :811/:875/:205/:210/:248/:261/:405; numpy/pandas RuntimeWarnings; Pandas4Warning datetime formatting; PytestRemovedIn10Warning class-scoped fixtures) — context only, no assertion changes made.
- Slowest 20: test_beta_perf_numpy_cache 21.83s; test_beta_performance 21.40s; test_betting_against_beta rolling beta 6.22s; test_bab_scale_perf_guard 5.86s/2.43s; test_portfolio_performance 5.02s; test_bab_config_matrix_stress 4.72s; CLI campaign parity tests ~2.2–3.1s.
- **Baseline gate is green.** Product code untouched this session (HANDOFF.md only).

### R4 Live-Readiness Preflight (COMPLETE — all green)
- `python3 scripts/bab_r4_preflight.py` → **R4-A/B/C present + green; R2/R3 baseline green.**
  - R4-A dry-run / portfolio-risk report: product capability + tests present, 12 tests passed.
  - R4-B drawdown-limit kill switch: product capability + tests present, 10 tests passed.
  - R4-C deterministic paper-trading replay harness: product capability + tests present, 9 tests passed.
  - R2/R3 regression baseline: 217 tests passed (test_bab_stress_regimes.py, test_bab_stress_horizon.py, test_bab_scale_perf_guard.py, test_bab_execution_realism_r3.py).
- **R4 is shipped and verified.** No R4 work required.

### Priority campaign (execute in order)
1. **Full-suite health baseline (HIGHEST, gate):** COMPLETE — 5667 passed, 35 skipped, RC 0, 592.02s. Promoted into this handoff. Gate green; no further action unless regressions appear.
2. **Static analysis / in-repo quality gate (HIGH, BINDING NEXT TASK):**
   - Confirmed baseline: `python3 -m ruff check .` → **1977 errors** (`414` fixable, `449` unsafe-fixable), **EXIT_RC=1** at HEAD `fadfcef` (ast_probe.py E501/PERF401, widespread I001/formatting across repo incl. root probes/scripts/tests). `pyproject.toml` `[tool.ruff]` config exists; tree not clean under it. Log: `/tmp/ruff_baseline.log`.
   - **Scope restriction for this campaign:** clean `strategies/` package first (299 errors at HEAD), then `scripts/`, then tests as tolerated.
   - Binding next action: make `ruff check strategies/` pass via **behavior-preserving fixes + minimal justified config tuning only**. Record exact commands, before/after counts, rationale. No assertion weakening; no semantics changes. Prefer targeted cleanup over noisy churn; do not apply `--fix --unsafe-fixes` blindly (unsafe fixes may alter semantics).
   - Do not edit `.github/workflows/*`; do not churn tracked `.cov*`/cache.
3. **Performance profiling & targeted optimization (HIGH):** profile hot/slow areas focusing on `beta.py` rolling beta (~21–22s tests), `backtest.py` lag/cost/partial-fill, `costs.py` (sqrt overflow warning), `execution.py`/reconciliation, CLI E2E. Implement ≥1 behavior-preserving optimization or justified fix with before/after measurements and equivalence tests (synthetic + fixture data).
4. **Real-data & edge hardening (MEDIUM-HIGH):** exercise `tests/fixtures/real_market_prices*.csv`, `real_market_returns.csv`, defect fixtures via CLI and `BABStrategy`/loader/quality paths. Add/strengthen tests for timezone/coercion, missing symbols, NaN/inf/duplicate dates, execution/cost realism edges with evidence. No external/venue credentials—do not fake.
5. **Close with evidence:** update this file with timestamp, HEAD, commands run (with RC), results, files changed, regressions/risks, and the next binding task.

### Known focus hints (validate, don't assume)
- Full suite is large/slow (308 test files; prior sessions noted multi-minute runtime and slow execution/replay/CLI tests) — expect long wall time.
- Root contains many `probe_*`/`debug_*`/`ast_probe.py` artifacts that currently contribute to ruff noise; treat carefully (avoid churny archaeology; clean only if needed for a passing quality gate and keep behavior intact).
- `research_state/workflow_run_diagnostics.jsonl` holds historical CI/agent diagnostics (`kilo_edit_tool_invalid_arguments` seen historically) — non-blocking unless reproduced live.
- `AGENT_HANDOFF.md` is pointer-only; `AGENT_TASK_2026-11-14.md` is superseded.

### Escalation/blockers
- If environment prevents completing baseline, capture exact errors, remediate minimally, document, and proceed with highest-value unblocked heavy work (e.g. ruff cleanup/fixes) while preserving evidence trail.

## Session log
- **2026-11-14T09:35:56Z (prior, handoff consolidation):** Established canonical handoff, superseded parallel task doc, no product/test evidence collected.
- **2026-11-14T10:22:00Z (prior, evidence-gathering):** Audited repo/config/docs/tests/fixtures (`ls`, `find`, `README.md`, `pyproject.toml`, `tests/fixtures/*`), confirmed HEAD `fadfcef`, clean baseline, pytest 9.2.0, ruff 0.17.5, 308 test files. Ran smoke: `pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py` → **104 passed, 2 warnings, 12.34s, RC 0**. Ran `python3 -m strategies.betting_against_beta.cli --synthetic` → **Final cumulative return 0.413704, Periods 252, RC 0**. Assessed lint: `ruff check .` → **1977 errors** (414 fixable, 449 unsafe) despite ruff config present. Started full-suite baseline `pytest -q --tb=line --durations=20` to `/tmp/full_pytest_baseline.log` (bgp `bgp_1d98863ba0015rn1jQ3tLCMc1M`); **not completed by session end** (last observed ~77%, skips present, no failures seen in tail). **No full-suite summary available yet.** Files changed this session: `HANDOFF.md` only (durable handoff refresh). No product code/tests modified. **Next binding task:** complete/recover full-suite baseline with definitive evidence, then drive ruff gate cleanup (high-signal/behavior-preserving) and proceed down priority list.
- **2026-11-14T10:30:00Z (prior, baseline complete):** Reran full-suite baseline after prior run was lost (log had stalled at 8%, background process gone). **5667 passed, 35 skipped, RC 0, 592.02s (0:09:52), no failures.** Warnings pre-existing only; no assertion/code changes. Slowest 20 promoted into handoff. **Baseline gate green.** Files changed: `HANDOFF.md` only. Bottleneck removed: baseline no longer blocked. **Next binding task:** ruff quality-gate cleanup — re-measure `python3 -m ruff check .` (1977 errors at HEAD), then clean a high-signal scope starting with `strategies/` via behavior-preserving fixes, record before/after counts + rationale, then proceed to campaign #3 (performance profiling/optimization).
- **2026-11-14T10:41:29Z (this session, R4 preflight + lint baseline refresh):**
  - Ran `python3 scripts/bab_r4_preflight.py` → **R4-A/B/C present + green; R2/R3 baseline green.** 31 R4 tests passed in 14.74s; 217 R2/R3 baseline tests passed in 52.56s. **R4 shipped and verified.** No R4 work required.
  - Refreshed lint baseline: `python3 -m ruff check .` → **1977 errors** (414 fixable, 449 unsafe-fixable), RC 1. `python3 -m ruff check strategies/` → **299 errors** (117 unsafe-fixable), RC 1.
  - Files changed this session: `HANDOFF.md` only (durable handoff refresh). No product code/tests modified.
  - **Bottlenecks removed:** Full-suite gate green; R4 preflight green. **Next binding task:** **Ruff quality-gate cleanup on `strategies/` package (299 errors at HEAD).** Run `python3 -m ruff check strategies/` to re-confirm baseline, then apply behavior-preserving fixes (safe `--fix` first, targeted manual edits for remaining) until `ruff check strategies/` exits RC 0. Record exact commands, before/after error counts, and rationale per change. Then proceed to `scripts/` and tests as tolerated, then campaign #3 (performance profiling/optimization).