# HANDOFF: Crypto-Betting-Against-Beta — Canonical Durable Session Handoff
**Timestamp (UTC):** 2026-11-14T10:46:19Z
**Repository:** Crypto-Betting-Against-Beta (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/HEAD:** `main...origin/main`, `a4ce212` (working tree clean)
**Single source of truth:** this file. Do not create parallel handoff/session docs. If evidence conflicts, trust live output and update this file.

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T10:46:19Z UTC) — BINDING

**Mission (repo-prioritized):** harden the **Crypto Betting Against Beta (BAB)** strategy — beta estimation, signals/portfolio construction, backtest/costs/slippage/partial-fill, risk/regime/beta-neutrality, execution/reconciliation, CLI, and data loading/quality — from historically "green" to **production-hardened and evidence-backed**. Every session must produce measurable progress backed by command evidence (RC, counts, timings, excerpts). No status-only work.

### Non-negotiable operating rules
- **Do heavy work every session:** run real commands, capture evidence, leave the repo measurably better or better-understood. No probe archaeology, no lettered campaign docs, no root probe/debug sprawl.
- **No claim without proof:** historical claims are context only; verify in this environment.
- **Scope discipline:** no `.github/workflows/*` edits, no tracked `.cov*`/cache churn, keep diffs focused/reviewable. Preserve default-path behavior unless a fix is justified by tests + rationale documented here.
- **Canonical handoff only:** update this file (and only this file) as the durable handoff.

### Verified environment/bootstrap (2026-11-14, this session)
- `git rev-parse --short HEAD` → `a4ce212`; `git status --short --branch` → `## main...origin/main` (clean).
- `python3 --version` → `Python 3.12.3`; `python3 -m pytest --version` → `pytest 9.2.0`; `ruff 0.17.5`.
- Deps import smoke: `python3 -c "import numpy, pandas, scipy; print('deps ok')"` → `deps ok`.
- Module import smoke: `python3 -c "import strategies.betting_against_beta.strategy"` → imports cleanly (no runtime error).
- Repo scale: `308` files under `tests/`; real-data fixtures in `tests/fixtures/` (`real_market_prices*.csv`, `real_market_returns.csv`, `real_data_defects.csv`, etc.).

### Verified quality/lint baseline (this session, HEAD `a4ce212`)
- `python3 -m ruff check strategies/` → **299 errors** (117 unsafe-fixable), RC 1.
- `python3 -m ruff check .` → **1977 errors** (414 fixable, 449 unsafe-fixable), RC 1.
- `strategies/` breakdown (`--statistics`): `E501` line-too-long 164; `UP045` non-pep604-optional 61; `SIM105` suppressible-exception 22; `SIM108` if-else→if-exp 10; `F841` unused-variable 10; `SIM102` collapsible-if 6; `PERF203` try-except-in-loop 6; `UP006` non-pep585-annotation 5; `UP007` non-pep604-union 5; `UP035` deprecated-import 2; `F821` undefined-name 2; `RUF059` unused-unpacked-variable 2; `RUF013` implicit-optional 1; `PERF102` incorrect-dict-iterator 1; `SIM103` needless-bool 1; `SIM201` negate-equal-op 1.
- **F821 triage (resolved understanding):** both F821 (`strategy.py:66` `_rebalance_mask(...) -> pd.Series`, `strategy.py:192` `_load_returns(...) -> pd.DataFrame`) are **annotation-only** and safe at runtime because the module has `from __future__ import annotations` (annotations are lazy strings) and `pandas` is imported function-locally where used. Confirmed: `strategy.py` imports cleanly. Fix = add a `TYPE_CHECKING` guard import of `pandas` (behavior-preserving), not a runtime change.

### Prior verified baselines (context — re-verify only if regressions suspected)
- **Full-suite baseline GREEN** (prior session): `python3 -m pytest -q --tb=line --durations=20` → **5667 passed, 35 skipped, 255 warnings in 592.02s, RC 0**. Slowest: `test_beta_perf_numpy_cache` 21.83s; `test_beta_performance` 21.40s; rolling-beta 6.22s; `test_bab_scale_perf_guard` 5.86s; `test_portfolio_performance` 5.02s; `test_bab_config_matrix_stress` 4.72s. Warnings pre-existing (data_loader date-parsing fallbacks, numpy/pandas RuntimeWarnings, Pandas4Warning, PytestRemovedIn10Warning).
- **R4 Live-Readiness Preflight GREEN** (prior session): `python3 scripts/bab_r4_preflight.py` → R4-A/B/C present + green (31 tests), R2/R3 baseline green (217 tests). **R4 shipped; no R4 work required.**

### Priority campaign (execute in order) — HEAVY WORK REQUIRED
1. **Ruff quality gate on `strategies/` (BINDING NEXT TASK):**
   - Re-confirm: `python3 -m ruff check strategies/` (expect 299 errors, RC 1).
   - Apply **behavior-preserving fixes only** until `ruff check strategies/` exits RC 0: safe `--fix` first (E501 is not auto-fixable — reformat manually; I001/UP/SIM mostly safe), targeted manual edits for the remainder. **Do NOT** apply `--fix --unsafe-fixes` blindly (unsafe fixes can alter semantics; F841 unused-variable and SIM105 need individual review, not blanket removal).
   - Fix the 2 F821 via a `TYPE_CHECKING` guard import of `pandas` (preserves lazy annotations).
   - Record exact commands, before/after error counts, and rationale per change class. No assertion weakening; no semantics changes.
2. **Extend quality gate to `scripts/`, then tests (as tolerated):** same method, scope by directory, record counts. Then re-run full `ruff check .` to confirm net reduction.
3. **Performance profiling & targeted optimization (HIGH):** profile hot/slow areas focusing on `beta.py` rolling beta (~21–22s tests), `backtest.py` lag/cost/partial-fill, `costs.py` (sqrt overflow warning), `execution.py`/reconciliation, CLI E2E. Implement ≥1 behavior-preserving optimization or justified fix with before/after measurements and equivalence tests (synthetic + fixture data).
4. **Real-data & edge hardening (MEDIUM-HIGH):** exercise `tests/fixtures/real_market_prices*.csv`, `real_market_returns.csv`, defect fixtures via CLI and `BABStrategy`/loader/quality paths. Add/strengthen tests for timezone/coercion, missing symbols, NaN/inf/duplicate dates, execution/cost realism edges with evidence. No external/venue credentials—do not fake.
5. **Close with evidence:** update this file with timestamp, HEAD, commands run (with RC), results, files changed, regressions/risks, and the next binding task.

### Known focus hints (validate, don't assume)
- Full suite is large/slow (308 test files; multi-minute runtime; slow execution/replay/CLI tests) — expect long wall time.
- Root contains many `probe_*`/`debug_*`/`ast_probe.py` artifacts contributing to ruff noise; treat carefully (avoid churny archaeology; clean only if needed for a passing quality gate and keep behavior intact).
- `research_state/workflow_run_diagnostics.jsonl` holds historical CI/agent diagnostics (`kilo_edit_tool_invalid_arguments` seen historically) — non-blocking unless reproduced live.
- `AGENT_HANDOFF.md` is pointer-only; `AGENT_TASK_2026-11-14.md` is superseded.

### Escalation/blockers
- If environment prevents completing a baseline, capture exact errors, remediate minimally, document, and proceed with the highest-value unblocked heavy work (e.g. ruff cleanup/fixes) while preserving the evidence trail.

## Session log
- **2026-11-14T09:35:56Z (prior, handoff consolidation):** Established canonical handoff, superseded parallel task doc, no product/test evidence collected.
- **2026-11-14T10:22:00Z (prior, evidence-gathering):** Audited repo/config/docs/tests/fixtures; confirmed HEAD `fadfcef`, clean baseline, pytest 9.2.0, ruff 0.17.5, 308 test files. Smoke: `pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py` → **104 passed, 2 warnings, 12.34s, RC 0**. `python3 -m strategies.betting_against_beta.cli --synthetic` → **Final cumulative return 0.413704, Periods 252, RC 0**. `ruff check .` → **1977 errors**. Started full-suite baseline (not completed by session end).
- **2026-11-14T10:30:00Z (prior, baseline complete):** Reran full-suite baseline. **5667 passed, 35 skipped, RC 0, 592.02s, no failures.** Warnings pre-existing only. Baseline gate green. Files changed: `HANDOFF.md` only.
- **2026-11-14T10:41:29Z (prior, R4 preflight + lint refresh):** `python3 scripts/bab_r4_preflight.py` → R4-A/B/C green (31 tests, 14.74s); R2/R3 baseline green (217 tests, 52.56s). `ruff check .` → 1977 errors; `ruff check strategies/` → 299 errors. Files changed: `HANDOFF.md` only.
- **2026-11-14T10:46:19Z (this session, handoff refresh + F821 triage):**
  - Confirmed HEAD `a4ce212`, clean tree. Re-verified: `ruff check strategies/` → 299 errors (RC 1); `ruff check .` → 1977 errors (RC 1); `--statistics` breakdown captured.
  - Triaged the 2 `F821` (`strategy.py:66`, `:192`): annotation-only, safe under `from __future__ import annotations` + function-local `import pandas as pd`. Confirmed `import strategies.betting_against_beta.strategy` succeeds. Fix path = `TYPE_CHECKING` guard import (behavior-preserving), not a runtime bug.
  - **Bottlenecks removed:** campaign unblocked; #1 open item (ruff `strategies/` gate) has a clear, safe method and the F821 ambiguity is resolved. No product/test code changed; only this handoff refreshed.
  - **Next binding task:** execute campaign #1 — drive `ruff check strategies/` to RC 0 via behavior-preserving fixes (safe `--fix` + manual E501/F841/SIM105 + TYPE_CHECKING F821), record before/after counts and rationale, then proceed to #2 (scripts/tests) and #3 (performance).