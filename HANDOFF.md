# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T18:51:48Z
**HEAD:** `bc0af86` (`chore(kilo): checkpoint agent session`) on `main`
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (execute first, no preamble loops)

**Start by re-confirming all three gate floors (Step 1 below) before doing anything else. Do not invent work, do not churn locked areas, do not run open-ended probes without a concrete, reproducible failure hypothesis.**

- **C28 items 1–5:** CLOSED — no proven gaps. **Do not reopen without a new, statable, reproducible failure + durable probe evidence.**
- **C29 (all 12 mandatory combos):** COMPLETE — 12/12 PASS, no proven gaps. **No regressions added.**
- **Current bottlenecks:** None proven in BAB product code. Historical workflow diagnostics are CI-log excerpts from past runs, not current source/test failures. Full-suite floors are slow in this environment; an incomplete/timed-out re-run without observed failure is inconclusive (not a regression). Re-run to completion with durable logs before claiming green/red.

**If a new failure is discovered (must be specific, reproducible, BAB-relevant):**
1. Capture minimal repro + durable probe log under `/home/runner/work/_temp/kilo-tmp/<unique>.log`.
2. Apply the smallest proven fix in allowed areas only (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) unless new evidence disproves a lock.
3. Add a minimal regression test only for the proven gap.
4. Re-run affected gates and all three floors below; refresh this HANDOFF with timestamp/HEAD, counts/rc, evidence paths, and next concrete task.

**If no new failure is found:** state "no proven gaps", keep gates/floors unchanged (or record completed re-runs), refresh timestamp/HEAD/evidence summary, and exit without code churn. Do not declare "blocked" without an evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## Current baseline (2026-11-11T18:51:48Z, HEAD `bc0af86`, clean tree; NO BAB product/test code edited)

- **campaign_d gate floor (re-confirmed this session):** `898 passed, 5 skipped, rc=0` in 8.44s (≥883 floor). Durable log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign_d_20261111T1852Z.log`. Command: `python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
- **Full BAB excl `data_loader`/controller floor:** **Re-ran to completion this session:** `2234 passed, 5 skipped, rc=0` in 561.86s (matches last recorded green at `bc98cf4`). Durable log: `/home/runner/work/_temp/kilo-tmp/c30_gate_full_bab_20261111T1852Z.log`. Command: `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
- **campaign11+14 closure bundle floor:** **Re-ran to completion this session:** `164 passed, 0 failed, rc=0` in 207.05s (≥164 floor). Durable log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign11_14_20261111T1852Z.log`. Command: `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`
- **Known non-BAB (excluded from BAB gates, not a blocker):** `tests/test_controller_progress_accounting.py` has controller/infra failures (workflow `stage_safe_changes` excludes nested `*/.github/workflows/*` in `scripts/controller_progress.py`). **Do not edit `.github/workflows/*`; do not weaken tests.**
- **This session:** all three gate floors re-confirmed green to completion with durable logs, repo/README/HANDOFF/git/diagnostics inspected, working tree clean, no BAB product/test edits made, no new reproducible BAB failure found. `research_state/workflow_run_diagnostics.jsonl` remains historical CI-log excerpts only.

**Gate floors (must stay green):** campaign_d ≥883 passed/5 skipped/rc=0; full BAB excl data_loader/controller rc=0; campaign11+14 ≥164 passed/0 failed/rc=0. Re-run affected gates after any product/test edit.

## Known bottlenecks / environment notes

- **No proven BAB runtime/code bottlenecks.**
- **Environment:** full gate-floor suites are slow in this checkout and can exceed default CLI timeouts; run with ample timeout and persist output to durable `/home/runner/work/_temp/kilo-tmp/<unique>.log` when needed. A timeout/interruption without observed failure is inconclusive, not a regression.
- **Historical CI diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior captured log excerpts/signals, not evidence of current source/test failure. Do not use to justify inaction.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).

## C28/C29 status (closed) — do not reopen without new evidence

- **C28 items 1–5:** CLOSED (no proven gaps). Evidence preserved in prior durable probe logs cited in git history/HANDOFF lineage (`/home/runner/work/_temp/kilo-tmp/c28_*`).
- **C29 (12/12 combos):** COMPLETE, all PASS, no proven gaps. Evidence: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`, `c29_combos2_12_probe.py`, `c29_combo1_api_probe.py`.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Closed/locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Next concrete focus campaign — C30 (gate-integrity & regression-prevention, binding)

**No proven gaps. No active BAB bottlenecks.** Steady-state maintenance only until new evidence appears.

**Step 1 (mandatory, every session, first):** Re-confirm all three gate floors to completion (capture durable logs under `/home/runner/work/_temp/kilo-tmp/c30_gate_<name>_<ts>.log`):
- campaign_d: `python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → **GREEN this session: 898 passed / 5 skipped / rc=0** (log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign_d_20261111T1852Z.log`)
- Full BAB excl `data_loader`/controller: `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → **GREEN this session: 2234 passed / 5 skipped / rc=0** (log: `/home/runner/work/_temp/kilo-tmp/c30_gate_full_bab_20261111T1852Z.log`)
- campaign11+14 closure bundle: `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` → **GREEN this session: 164 passed / 0 failed / rc=0** (log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign11_14_20261111T1852Z.log`)
Record counts + rc + log paths here. A red floor is a proven blocker — fix before any other work. All three floors are currently green.

**Step 2:** Only if Step 1 is fully green AND you have a concrete, statable, reproducible BAB-relevant failure hypothesis, execute the "If a new failure is discovered" procedure (durable probe log → smallest proven fix in allowed areas only → minimal regression test only for the proven gap → re-run floors → refresh HANDOFF).

**Step 3 (never avoid heavy work, never invent work):** If no concrete failure hypothesis exists, record "no proven gaps", keep evidence current, and exit without code churn. **No new BAB-relevant failure hypothesis exists this session.** Heavy work in C30 = rigorous gate verification and regression protection (completed above) — not feature work. Exit steady-state.

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durable log paths for any runs completed, and the next concrete task (or "none; steady-state C30"). Keep it single, durable, unambiguous.
