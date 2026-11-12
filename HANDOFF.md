# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T08:05:10Z
**HEAD:** `349a58f3c5d8b2e390769195b0ec5d706bc991d2` on `main`
**Working tree (tracked):** clean at refresh (`git status --porcelain` empty). Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts may exist and must not be committed.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work across `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py`, `attribution.py`, `metrics.py`, `cli.py`/reporting, `costs.py`, `regime.py`, `shorting.py`, `sizing.py` and controller/gate contracts. No unrelated refactors.

## Bottlenecks cleared (this refresh)
- **Stale/duplicated handoff removed:** prior `HANDOFF.md` contained duplicated "BINDING INITIAL TASK MESSAGE" blocks and stale status claims (Gate 1 "GREEN @ this refresh", HEAD/timestamp mismatch). Replaced with this single canonical, timestamped handoff.
- **Historical diagnostics isolated:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads only. Treat as historical; not evidence of a current-checkout failure and must not justify inaction.
- **No runtime blocker reproduced:** core BAB module imports `quality, signals, portfolio, config, backtest, data_sources, attribution, metrics, cli, costs, regime, shorting, sizing` → `imports_ok` (`PYTHONPATH=$PWD`). No dirty tracked files, no proven workflow-sync regression.

## BINDING INITIAL TASK — NEXT AGENT (start immediately, heavy execution required)

**Start work now. Do not plan-only. Do not re-diagnose historical CI noise. Do not declare "blocked" without an evidenced attempt and durable logs. C42 is NOT started and is the only required next work.**

### 1) Reconfirm gate baseline with durable logs (before claiming progress and after any fix)
- Gate 1: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
- Gate 2: `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
- Gate 3: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`
- Optional full gate: `scripts/bab_gate.sh` (may exceed short timeouts; run with adequate wall time).
- Env: Python 3.12.3, repo root, `PYTHONPATH=$PWD`. Deps: `numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`.
- Prior durable reference (C41, historical): Gate 1 898 passed/5 skipped rc=0, Gate 2 2234 passed/5 skipped rc=0, Gate 3 164 passed rc=0 (logs under `/home/runner/work/_temp/kilo-tmp/c41_gate_*`). **Gates 1/2/3 must be re-verified now with fresh durable logs for this HEAD**; any regression is blocking evidence.

### 2) Execute C42 ROTATION adversarial probe campaign (≥20 NEW probes, mandatory)
- **Do not reuse** C40/C40-extended/C41 probe scripts or shapes. Every probe must have durable log(s) under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, and repro path. Smoke checks are insufficient.
- **Required coverage (all):**
  - `quality.py`: `data_quality_report` with None/empty/non-DataFrame, duplicate index, non-datetime index, large gaps, all-NaN columns, mixed dtypes.
  - `signals.py`: `generate_bab_signals` with constant/all-same/NaN betas, <2 observations, empty universe, single asset, quantile boundary behavior.
  - `portfolio.py`: `construct_portfolio` with dollar-neutral/long-only, weight caps, zero longs/shorts, NaN signals, misaligned index.
  - `config.py`: `BABConfig` validation boundaries (vol_thresholds+vol_percentiles conflict, vol_hysteresis out of [0,1], beta_window < 1, long/short quantiles at 0/1, universe_override no overlap).
  - `backtest.py`: `run_backtest` serialization/round-trip, NaN/inf in prices/returns, empty/single-row DataFrame, transaction-costs interaction.
  - `data_sources.py`: emitter contracts, malformed CSV/JSON, missing benchmark column, duplicate timestamps, unsupported format.
  - **Cross-interactions:** `regime`+`sizing` (regime scale → vol-target leverage), `attribution`+`shorting` (attribution on borrow-constrained weights), `metrics`+`sizing` (metrics on sized portfolio).
- Maintain a probe matrix (id, target, shape, result, log path). Minimum 20 probes total.

### 3) On proven regression
Apply the **smallest** fix in an allowed editable area only → add a minimal regression test → re-run affected tests + all three gate floors → capture durable evidence.

### 4) If no proven gaps
Record **"C42 rotation: no proven gaps"** with per-area/per-probe evidence and log paths (not a claim without logs).

### 5) Before exit (mandatory)
Refresh this same `HANDOFF.md` with: timestamp/HEAD, fresh gate results+log paths, full C42 probe matrix outcomes, working-tree notes, and the next concrete heavy task.
If C42 closes cleanly, **immediately define and start C43** (≥20 new probes, new shapes, durable logs) on remaining unexhausted surfaces/cross-interactions and leave that as the binding next task. Keep this file the single durable handoff.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C41 without a new statable reproducible failure + durable evidence.

## Status snapshot (this refresh)
- C41: CLOSED, no proven gaps (prior durable evidence; historical).
- **C42: NOT started — binding primary task now.**
- Gate floors: **not re-verified at this refresh** (must be re-run with fresh durable logs for HEAD `349a58f...`).
- Next campaign (binding): **C42 ROTATION** (≥20 new adversarial probes, all required surfaces/cross-interactions). On clean close, define and start **C43** immediately with ≥20 new probes and durable evidence.
