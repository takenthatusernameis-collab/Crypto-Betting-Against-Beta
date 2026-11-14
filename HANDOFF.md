# HANDOFF: Crypto-Betting-Against-Beta — Canonical Durable Session Handoff
**Timestamp (UTC):** 2026-11-14T09:35:56Z
**Repository:** Crypto-Betting-Against-Beta (`/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`)
**Branch/HEAD:** `main...origin/main`, `fadfcef` (working tree clean at handoff write)
**Single source of truth:** this file. Do not create parallel handoff/session docs; if evidence conflicts, trust live output and update this file.

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T09:35:56Z UTC) — BINDING

**Mission (repo-prioritized):** advance the **Crypto Betting Against Beta (BAB)** strategy from “feature-complete, tests-green historically” to **production-hardened and evidence-backed**. This repo is a quantitative crypto strategy codebase (beta estimation, BAB signals/portfolio, backtest, costs/slippage/partial-fill, risk/regime/beta-neutrality, execution/reconciliation, CLI, data loading/quality). Future work must materially improve correctness confidence, performance, real-data robustness, or developer/ops quality gates — **not** docs/probe archaeology.

### Non-negotiable operating rules
- **Do heavy work every session:** run real commands, capture evidence (RC, counts, timings, key excerpts), and leave the repo in a measurably better or better-understood state. No “status-only” sessions.
- **No claim without proof:** verify in this environment before asserting pass/fail/perf. Historical claims below are context, not proof.
- **No scope theater:** no new lettered campaign docs, no root probe/debug script sprawl, no `.github/workflows/*` edits, no tracked `.cov*`/cache churn. Keep diffs focused and reviewable.
- **Preserve behavior unless a fix is justified:** default-path invariance matters; if you change semantics, add/adjust tests and document rationale here with evidence.
- **Canonical handoff only:** update this file (and only this file) as the durable handoff.

### Bootstrap & fast verification (use absolute/inline paths; do not rely on unset shell vars)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status --short --branch
git rev-parse --short HEAD
python3 --version
python3 -m pytest --version
python3 -c "import numpy, pandas, scipy; print('deps ok')"
python3 -m pytest -q tests/test_betting_against_beta.py tests/test_bab_cli.py
python3 -m strategies.betting_against_beta.cli --synthetic
```
Record actual outputs/RCs in your session notes and reflect any material finding in this handoff.

### Priority campaign (execute in order; complete what you start or leave crisp evidence)
1. **Full-suite health baseline (HIGHEST, mandatory first real task):**
   - Run: `python3 -m pytest -q --tb=line --durations=20` (full `tests/`, ~300+ files; expect multi-minute runtime). Capture pass/fail/skip counts, total time, slowest tests, and any flakes.
   - If anything fails, **fix root cause** (not by weakening assertions) and re-run impacted scope then full suite as feasible. This is the gate for all other work.
2. **Performance profiling & targeted optimization (HIGH):**
   - Profile known hot/slow areas with evidence: `beta.py` rolling beta, `backtest.py` lag/cost/partial-fill paths, `costs.py` transaction cost computation, `execution.py`/reconciliation paths, CLI end-to-end. Use `--durations`, `time`, and `cProfile`/`python -X importtime` or targeted benchmarks as appropriate.
   - Implement at least one **behavior-preserving** optimization or a clearly-justified fix with before/after measurements and tests proving equivalence on representative cases (synthetic + fixture data).
3. **Static analysis / quality gate in-repo (HIGH, no workflow edits):**
   - Add minimal, sane `[tool.ruff]` and/or `[tool.mypy]` (or equivalent) config in `pyproject.toml` and make the codebase pass a defined command set (e.g. `ruff check` on scoped paths, targeted mypy). Prefer incremental, high-signal rules; fix real issues found. Document exact commands and results here.
4. **Real-data & edge hardening (MEDIUM-HIGH):**
   - Exercise `tests/fixtures/real_market_prices*.csv`, `real_market_returns.csv` and defect fixtures via CLI and `BABStrategy`/loader/quality paths. Add or strengthen tests for timezone/coercion, missing symbols, NaN/inf/duplicate dates, and execution/cost realism edge cases (e.g. participation/negative-sqrt or bound issues in modeled costs) **with evidence**.
5. **Close with evidence:** update this file with timestamp, HEAD, commands run, results, files changed, regressions/risks, and the next binding task.

### Known focus hints (validate, don’t assume)
- Prior handoffs flagged slow tests (execution integration/replay/CLI campaigns) and absent lint/type gates; `pyproject.toml` currently has no `[tool.ruff]/[tool.mypy]`.
- `research_state/workflow_run_diagnostics.jsonl` contains historical CI/agent diagnostics (including prior `kilo_edit_tool_invalid_arguments` log signals); treat as historical/non-blocking context unless reproduced live.
- Real-data fixtures exist in `tests/fixtures/`; use them instead of inventing external data sources. No real-venue credentials available — do not fake.

### Escalation/blockers
- If full suite or key tests cannot run due to environment issues, capture exact errors, remediate minimally, and document. If a true external dependency blocks progress, record it explicitly with evidence and proceed with the highest-value unblocked heavy work.
- CI workflow pattern-sync issues (historical) must be handled atomically in controller/workflow if ever touched — but **prefer not touching `.github/workflows/*`** in this campaign.

## Historical context (unverified snapshot from prior sessions; re-verify live)
- Strategy/modules reported complete through R1–R5 (core BAB, data/CLI/quality, execution costs, risk/replay, execution adapters) plus sizing/shorting/regime/beta-neutrality/attribution features under `strategies/betting_against_beta/`.
- Prior notes claimed large green test suites (300+ files / 1000+ tests). Treat as stale until reproduced by current full-suite baseline.
- `AGENT_HANDOFF.md` is a pointer; `AGENT_TASK_2026-11-14.md` is legacy/superseded by this canonical handoff.

## Session log
- **2026-11-14T09:35:56Z (handoff consolidation):** Audited repo state (HEAD `fadfcef`, clean tree), read README/pyproject/workflow head, existing handoffs, research_state, and fixtures. Established this file as the single durable, timestamped, binding task message and removed parallel-handoff ambiguity by superseding stale task-doc guidance. No product code/tests changed; **no test/build evidence collected this step** — next agent must execute Priority 1 immediately.
