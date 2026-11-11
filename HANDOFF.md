# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T22:09:54Z
**HEAD:** `9f9d80e` (`chore: capture completed workflow run diagnostics`) on `main` — working tree clean. Since prior verified baseline (`c5f2d8c`) only a diagnostics-capture commit landed (no BAB product/test code changes); gates remain the last verified evidence but **MUST be re-run to completion this session** (Step 1).
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (execute immediately, no preamble loops)

**This session is C31 (adversarial robustness + gate-integrity). You must do heavy, evidence-producing work. "No proven gaps" is an outcome only after full execution below — never a reason to skip.**

1. **Step 1 — Gate floors (mandatory, first, run to completion with ample timeout; persist durable logs under `/home/runner/work/_temp/kilo-tmp/c31_gate_<name>_<ts>.log`):**
   - `python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → **floor ≥883 passed, 5 skipped, rc=0**.
   - `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → **rc=0** (slow; use timeout ≥900s, never abort early; timeout without observed failure is inconclusive, not green).
   - `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` → **floor ≥164 passed, 0 failed, rc=0**.
   Record exact counts+rc+durations+log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

2. **Step 2 — C31 adversarial probe campaign (mandatory after Step 1 green; heavy work):** systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Minimum required probe matrix (execute all; extend if you find a concrete hypothesis):
   - **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty `--data`, benchmark missing/overlap, empty/whitespace universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths.
   - **Metrics/reporting robustness:** degenerate/constant/NaN/short series, extreme drawdowns/vol, serialization safety (no NaN/Inf leakage in JSON).
   - **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths.
   For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

3. **Step 3 — Closure:** If no reproducible gaps after full Step 1+2, record "C31: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and leave next concrete task as "C32: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)". Do not exit after Step 1 alone; do not invent failures.

**Rules:** Do not reopen C28/C29 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without an evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## Last verified baseline (2026-11-11T21:14:49Z, HEAD `c5f2d8c`, prior session — re-verify this session)

- **campaign_d:** `898 passed, 5 skipped, rc=0` in 8.11s (≥883). Log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign_d_20261111T205319Z.log`.
- **Full BAB excl `data_loader`/controller:** `2234 passed, 5 skipped, rc=0` in 558.50s. Log: `/home/runner/work/_temp/kilo-tmp/c30_gate_full_bab_20261111T205319Z.log`.
- **campaign11+14:** `164 passed, 0 failed, rc=0` in 208.32s (≥164). Log: `/home/runner/work/_temp/kilo-tmp/c30_gate_campaign11_14_20261111T205319Z.log`.
- **HEAD advanced to `9f9d80e`** via `chore: capture completed workflow run diagnostics` only (non-BAB code). Prior logs remain valid historical evidence; current session must produce fresh c31 logs.

## Known bottlenecks / environment notes

- **Bottleneck removed this refresh — stale HEAD/timestamp in HANDOFF:** corrected to `9f9d80e` @ 2026-11-11T22:09:54Z. Future agents must verify `git rev-parse --short HEAD` before trusting recorded HEAD.
- **No proven BAB runtime/code bottlenecks.**
- **Environment:** full suites are slow and can exceed default CLI timeouts; run with ample timeout and durable logs. Timeout/interruption without observed failure is inconclusive, not a regression.
- **Historical CI diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` (and large tool-output excerpts) contain prior captured log signals, not current source/test failures. Do not use to justify inaction.
- **Known non-BAB (excluded, not a blocker):** `tests/test_controller_progress_accounting.py` may fail (infra/workflow staging). Exclude from BAB gates; **do not edit `.github/workflows/*`; do not weaken tests.**
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/`).

## C28/C29 status (closed) — do not reopen without new evidence

- **C28 items 1–5:** CLOSED (no proven gaps). Evidence: prior durable probe logs in git/HANDOFF lineage (`/home/runner/work/_temp/kilo-tmp/c28_*`).
- **C29 (12/12 combos):** COMPLETE, all PASS. Evidence: `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`, `c29_combos2_12_probe.py`, `c29_combo1_api_probe.py`.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durable log paths for any runs/probes completed, C31 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
