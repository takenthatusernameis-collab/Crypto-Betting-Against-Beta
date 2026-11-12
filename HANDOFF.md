# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T08:57:30Z
**HEAD:** `b7df039846bd790de468b0d8c9bc9a5b5ee88a7a` (`chore(kilo): checkpoint agent session`) on `main`
**Working tree (tracked):** clean. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts may exist and must not be committed.
**Env:** Python 3.12.3, Linux, repo root, `PYTHONPATH=$PWD`.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No duplicate/stale task blocks.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old head SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven runtime blocker reproduced:** core BAB modules import cleanly on current HEAD.
- **Gate invocation note (current env):** pytest glob-expansion for `tests/test_bab_data_loader_campaign_d*.py` is brittle in this shell; Gate 1 was executed with explicit campaign_d file list. Gate 2/3 must run from repo root with `PYTHONPATH=$PWD` (running from wrong cwd produced `ModuleNotFoundError: strategies` collection failures in early attempt; corrected reruns launched).

## Gate floors (current HEAD `b7df039`, 2026-11-12T08:57Z session)

| Gate | Command (cwd=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta, PYTHONPATH=$PWD) | Result | Log |
|---|---|---|---|
| 1 | `python3 -m pytest -q` over explicit `tests/test_bab_data_loader_campaign_d{,2,3,5,_coerce_more,_core,_core2,_core3,_core4,_core5,_core_final,_deep,_deep3,_final_coverage,_final_push,_final_push2,_gaps,_gaps2,_heavy,_heavy2,_heavy3,_heavy_push2,_more2,_more4,_more5,_push,_push2,_push3,_push4,_push_final,_push_heavy,_ultra}.py` + `batch148/149/172` | **898 passed, 5 skipped, 53 warnings, rc=0** (4.85s) | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate1_20261112T085359Z.log` |
| 2 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | **IN PROGRESS at handoff write** (background rerun after timeout-prone foreground runs); partial logs show ~19% complete earlier | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate2_20261112T085359Z_bg.log` (also earlier: `_rerun.log`, base log) |
| 3 | `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` | **IN PROGRESS at handoff write** (background rerun); partial logs show ~43% complete earlier | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate3_20261112T085359Z_bg.log` (also earlier: `_rerun.log`, base log) |

**Carry-forward prior GREEN (HEAD `0ef833a`):** Gate 2 → 2234 passed,5 skipped; Gate 3 → 164 passed (see `c42_gate_*` logs). **Next session MUST confirm/record final rc+counts for Gates 2/3 on `b7df039` from the `*_bg.log` tails before starting C43 probe execution; if either fails, treat as top-priority proven regression and fix smallest-first.**

## Completed campaign (do not reopen without new reproducible failure + durable evidence)
- **C42 ROTATION:** CLOSED — 38/38 adversarial probes PASS, 0 FAIL, no proven gaps. Evidence: `/home/runner/work/_temp/kilo-tmp/c42_probe_summary_20261112T082656Z.json` and `c42_probe_*`.
- C6–C41 CLOSED per prior evidence. No churn.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (read this first)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; no planning-only turn.
- **Immediate actions (in order):**
  1. Check Gate 2/3 background outcomes on `b7df039`: `tail -40 /home/runner/work/_temp/kilo-tmp/c43_gate_gate2_20261112T085359Z_bg.log` and `...gate3..._bg.log`; record final rc/pass/skip/fail counts and durations here. If still running, wait/monitor to completion (no polling loops without progress; use `background_process status/logs`). If any failure, stop and fix smallest proven gap with regression + re-run affected gates.
  2. Execute **≥20 NEW C43 adversarial probes** (new shapes/scripts, no C40–C42 reuse) with durable logs under `/home/runner/work/_temp/kilo-tmp/c43_probe_*.{log,json}` including id, target, shape, rc, duration, PASS/FAIL, repro.
  3. On any proven gap: smallest fix in allowed editable area only → minimal regression → re-run affected tests + all three gates → capture evidence.
  4. Refresh this file with full C43 matrix/evidence and next concrete task before exit. If C43 clean, **immediately define and start C44** (≥20 new probes, new shapes, binding).

## BINDING INITIAL TASK — C43 ROTATION (heavy, mandatory)

**Objective:** deep adversarial robustness campaign (C43). Execution, not planning. Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs.

### 1) Finalize gate floors (current HEAD)
Confirm Gate 2/3 completion from bg logs and record definitive results in this file (Gate 1 already GREEN). If failures appear, they become the first proven work item.

### 2) Execute ≥20 NEW adversarial probes (C43 shapes only)
- **No reuse** of C40/C41/C42 scripts/shapes. Durable per-probe logs under `/home/runner/work/_temp/kilo-tmp/`.
- **Surfaces:** `beta.py` (`calculate_beta`: constant/NaN/inf, single obs, misaligned index, benchmark mismatch/absence, window edges), `data_loader.py` (`load_returns`/`normalize_schema`/`detect_and_normalize_exchange_format`: malformed headers, mixed freq, tz edges, extreme/streaming-like), `strategy.py` (`run_strategy`/`generate_signals`: config permutations, regime/shorting/cost interactions), `costs.py` (`TransactionCostModel`/`compute_transaction_costs`: zero/negative ADV, extreme spreads, NaN prices, per-asset), `regime.py` (`regime_scale_factors`/`regime_scale_scalar`: trend/combined, hysteresis edges, constant vol, NaN returns), `shorting.py` (`apply_shorting_constraints`: borrowable dict, per-asset borrow costs, strict violations, cascading caps), `sizing.py` (`apply_position_sizing`: Kelly/RiskParity/EqualWeight, lookback < data, max_leverage binding, unreachable target_vol).
- **Required cross-interactions:** `beta`+`regime`, `strategy`+`costs`+`shorting`, `regime`+`shorting`, `attribution`+`regime`, `metrics`+`regime`.
- Maintain probe matrix (id, target, shape, result, log path). Minimum 20 probes.

### 3) On proven regression/gap
Smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence.

### 4) On no proven gaps
Record **"C43 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths.

### 5) Before exit (mandatory)
Refresh this file with: timestamp/HEAD, gate results+log paths (including finalized Gate 2/3), full C43 probe matrix, fixes/tests added (if any), working-tree notes, and **next concrete heavy task**. If C43 closes cleanly, **immediately define and start C44** (≥20 new probes, new shapes, durable logs) and leave it binding.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.

(End of file)
