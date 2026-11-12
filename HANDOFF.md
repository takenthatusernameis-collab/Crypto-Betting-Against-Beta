# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T08:52:34Z
**HEAD:** `c14cdc09e516b2225e2b3f7390dded0ce78b8ead` on `main`
**Working tree (tracked):** clean at refresh. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts may exist and must not be committed.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is a pointer only. No duplicate/stale task blocks.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old head SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven runtime blocker reproduced:** core BAB module imports `quality, signals, portfolio, config, backtest, data_sources, attribution, metrics, cli, costs, regime, shorting, sizing` cleanly (`PYTHONPATH=$PWD`).

## Gate floors (last fresh verification, HEAD `0ef833a`, 2026-11-12T07:47Z — carry-forward; re-verify on current HEAD before new work)
All GREEN with durable logs (prior HEAD):
- **Gate 1:** `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → **898 passed, 5 skipped** (rc=0). Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate1_20261112T074740Z.log`
- **Gate 2:** `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → **2234 passed, 5 skipped** (rc=0). Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate2_20261112T074748Z.log`
- **Gate 3:** `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*` → **164 passed** (rc=0). Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate3_20261112T074750Z.log`
Env: Python 3.12.3, repo root, `PYTHONPATH=$PWD`. **Step 1 of C43: re-run all three gates on `c14cdc0` and tee fresh durable logs under `/home/runner/work/_temp/kilo-tmp/c43_gate_{gate}_{ts}.log`; record rc/duration/counts here if they change.**

## Completed campaign (do not reopen without new reproducible failure + durable evidence)
- **C42 ROTATION:** CLOSED — 38/38 adversarial probes PASS, 0 FAIL, no proven gaps. Full matrix/summary in prior durable logs: `/home/runner/work/_temp/kilo-tmp/c42_probe_summary_20261112T082656Z.json` and `c42_probe_*` logs.
- C6–C41 CLOSED per prior evidence. No churn.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (read this first)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` is pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics; do not treat as current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; no planning-only turn.
- **Start now:** re-verify gates on current HEAD, run ≥20 NEW C43 adversarial probes with durable logs, fix only smallest proven gaps with regressions, refresh this file before exit. If C43 is clean, immediately define and start C44 with ≥20 new probes and leave it binding.

## BINDING INITIAL TASK — C43 ROTATION (heavy, mandatory, start immediately)

**Objective:** execute a deep adversarial robustness campaign (C43). This is execution work, not planning. Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs. Absence of a pre-known bug is not permission to stop; exhaust the required probe matrix and cross-interactions.

### 1) Re-verify gate floors first (capture fresh durable logs for current HEAD)
Run Gate 1/2/3 to completion with `PYTHONPATH=$PWD` and tee logs under `/home/runner/work/_temp/kilo-tmp/c43_gate_{gate}_{ts}.log`. Record rc/duration/counts in this file if anything changes or before exit.

### 2) Execute ≥20 NEW adversarial probes (C43 shapes only)
- **Do not reuse** C40/C41/C42 scripts or shapes. Every probe must emit a durable log with probe id, target, shape, rc, duration, PASS/FAIL, and repro path under `/home/runner/work/_temp/kilo-tmp/`.
- **Required surfaces:**
  - `beta.py`: `calculate_beta` with constant/NaN/inf returns, single observation, misaligned index, benchmark mismatch/absence, window edge cases.
  - `data_loader.py`: `load_returns` / `normalize_schema` / `detect_and_normalize_exchange_format` with malformed headers, mixed freq, tz edge cases, extreme/streaming-like shapes.
  - `strategy.py`: `run_strategy` / `generate_signals` under config permutations and regime/shorting/cost interactions.
  - `costs.py`: `TransactionCostModel` / `compute_transaction_costs` with zero/negative ADV, extreme spreads, NaN prices, per-asset models.
  - `regime.py`: `regime_scale_factors` / `regime_scale_scalar` with trend/combined methods, hysteresis edges, constant vol, NaN returns.
  - `shorting.py`: `apply_shorting_constraints` with borrowable dict, per-asset borrow costs, strict-mode violations, cascading caps.
  - `sizing.py`: `apply_position_sizing` with Kelly/RiskParity/EqualWeight, lookback < data, max_leverage binding, unreachable target_vol.
- **Required cross-interactions (deeper):** `beta`+`regime` (beta stability across vol regimes), `strategy`+`costs`+`shorting` (full pipeline with borrow+transaction costs), `regime`+`shorting` (regime scaling on borrow-constrained weights), `attribution`+`regime` (attribution by regime state), `metrics`+`regime` (metrics per regime bucket).
- Maintain a probe matrix (id, target, shape, result, log path). Minimum 20 probes.

### 3) On proven regression/gap
Apply the **smallest** fix in an allowed editable area only → add a minimal regression test → re-run affected tests and all three gate floors → capture durable evidence (before/after if applicable).

### 4) On no proven gaps
Record **"C43 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths (never a claim without logs).

### 5) Before exit (mandatory)
Refresh this same `HANDOFF.md` with: timestamp/HEAD, gate results+log paths, full C43 probe matrix outcomes, fixes/tests added (if any), working-tree notes, and the **next concrete heavy task**. If C43 closes cleanly, **immediately define and start C44** (≥20 new probes, new shapes, durable logs) on remaining unexhausted surfaces/cross-interactions and leave that as binding. Keep this file the single durable handoff.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.

(End of file)
