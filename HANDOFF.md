# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T07:45:29Z
**HEAD:** `0de0bbb451c4ed976ec35f8d094820f77ccf6542` on `main` (tracked working tree clean at refresh; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Staleness/bottlenecks cleared at refresh:** prior handoff cited HEAD `9919fc0`; HEAD has advanced via checkpoint commits to `0de0bbb` (clean tracked state). Corrected here. `research_state/workflow_run_diagnostics.jsonl` is **historical CI/log excerpts only** (Oct/Nov captured runs, prior-head signals) — not evidence of a current-checkout failure and must not justify inaction. No dirty tracked files, no workflow-sync regression evidenced, no runtime blocker reproduced. **C42 is NOT started and is the only required next work.**

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (start immediately)

**Start work now. Do not plan-only. Do not re-diagnose historical CI noise. Do not declare "blocked" without an evidenced attempt and durable logs.**

Repo is **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark). Binding product work is BAB correctness/robustness across `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py`, `attribution.py`, `metrics.py`, `cli.py`/reporting, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, and controller/gate contracts — driven by proven evidence only.

### 1) Reconfirm gate baseline with durable logs before claiming progress (and after any fix)
- Gate 1: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
- Gate 2: `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
- Gate 3: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`
- Optional full gate: `scripts/bab_gate.sh` (may exceed short timeouts; run with adequate wall time).
- Env: Python 3.12.3, repo root, `PYTHONPATH=$PWD`. Deps: `numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`.
- Prior durable reference (C41): Gate 1 898 passed/5 skipped rc=0, Gate 2 2234 passed/5 skipped rc=0, Gate 3 164 passed rc=0 (`/home/runner/work/_temp/kilo-tmp/c41_gate_*`). Gate 1 re-verified GREEN at prior refresh (898/5/0); Gates 2/3 **must be re-verified now** (prior run timed out at 5 min) and any regression treated as blocking evidence.

### 2) Immediate binding task: execute C42 ROTATION adversarial probe campaign (≥20 NEW probes)
- **Do not reuse** C40/C40-extended/C41 probe scripts or shapes. Every probe must have durable log(s) under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, and repro path. Smoke checks are insufficient.
- **Required coverage (all):**
  - `quality.py`: `data_quality_report` with None/empty/non-DataFrame, duplicate index, non-datetime index, large gaps, all-NaN columns, mixed dtypes.
  - `signals.py`: `generate_bab_signals` with constant/all-same/NaN betas, <2 observations, empty universe, single asset, quantile boundary behavior.
  - `portfolio.py`: `construct_portfolio` with dollar-neutral/long-only, weight caps, zero longs/shorts, NaN signals, misaligned index.
  - `config.py`: `BABConfig` validation boundaries (vol_thresholds+vol_percentiles conflict, vol_hysteresis out of [0,1], beta_window < 1, long/short quantiles at 0/1, universe_override no overlap).
  - `backtest.py`: `run_backtest` serialization/round-trip, NaN/inf in prices/returns, empty/single-row DataFrame, transaction-costs interaction.
  - `data_sources.py`: emitter contracts, malformed CSV/JSON, missing benchmark column, duplicate timestamps, unsupported format.
  - **Cross-interactions:** `regime`+`sizing` (regime scale → vol-target leverage), `attribution`+`shorting` (attribution on borrow-constrained weights), `metrics`+`sizing` (metrics on sized portfolio).
- Record a probe matrix (id, target, shape, result, log path).

### 3) On proven regression
Apply smallest fix in allowed editable area only → add minimal regression test → re-run affected tests + all three gate floors → capture durable evidence.

### 4) If no proven gaps
Record **"C42 rotation: no proven gaps"** with per-area/per-probe evidence and log paths.

### 5) Before exit
Refresh this same `HANDOFF.md` with timestamp/HEAD, gate results+logs, full C42 probe matrix outcomes, working-tree notes, and the next concrete heavy task. If C42 closes cleanly, **immediately define and start C43** (≥20 new probes, new shapes, durable logs) on remaining unexhausted surfaces; continue the evidence-driven hardening loop. Keep this file the single durable handoff.

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged. **Do not edit** unless a newly proven controller/workflow sync regression is reproduced with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` historical only.

### Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C41 without a new statable reproducible failure + durable evidence.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (start immediately)

**Start work now. Do not plan-only. Do not re-diagnose historical CI noise. Do not declare "blocked" without an evidenced attempt and durable logs.**

The repo is **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark). Binding product work is BAB correctness/robustness across `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py`, `attribution.py`, `metrics.py`, `cli.py`/reporting, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, and controller/gate contracts — driven by proven evidence only.

1. **Establish/reconfirm gate baseline with durable logs before claiming progress (re-run if any fix lands or if baseline is in doubt).**
    - Gate 1: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`  (GREEN @ this refresh: 898 passed/5 skipped rc=0)
    - Gate 2: `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
    - Gate 3: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`
    - Optional full gate: `scripts/bab_gate.sh` (self-contained; coverage optional). NOTE: full suite may exceed short timeouts; run with adequate wall time.
    - Environment: system Python 3.12.3, repo root, `PYTHONPATH=$PWD`. Declared deps: `numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`.
    - Prior C41 GREEN reference: Gate 1 898 passed/5 skipped rc=0, Gate 2 2234 passed/5 skipped rc=0, Gate 3 164 passed rc=0 (logs in `/home/runner/work/_temp/kilo-tmp/c41_gate_*`).

2. **Immediate binding task: execute C42 ROTATION adversarial probe campaign (minimum 20 NEW probes).**
    - **Do not reuse** C40/C40-extended/C41 probe scripts or shapes. Every probe must have durable log(s) under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, and repro path. Smoke checks are insufficient.
    - **Required target surfaces/shapes (cover all):**
      - `quality.py`: `data_quality_report` with None/empty/non-DataFrame, duplicate index, non-datetime index, large gaps, all-NaN columns, mixed dtypes.
      - `signals.py`: `generate_bab_signals` with constant/all-same/NaN betas, <2 observations, empty universe, single asset, quantile boundary behavior.
      - `portfolio.py`: `construct_portfolio` with dollar-neutral/long-only, weight caps, zero longs/shorts, NaN signals, misaligned index.
      - `config.py`: `BABConfig` validation boundaries (vol_thresholds+vol_percentiles conflict, vol_hysteresis out of [0,1], beta_window < 1, long/short quantiles at 0/1, universe_override no overlap).
      - `backtest.py`: `run_backtest` serialization/round-trip, NaN/inf in prices/returns, empty/single-row DataFrame, transaction-costs interaction.
      - `data_sources.py`: emitter contracts, malformed CSV/JSON, missing benchmark column, duplicate timestamps, unsupported format.
      - **Cross-parameter interactions:** `regime`+`sizing` (regime scale → vol-target leverage), `attribution`+`shorting` (attribution on borrow-constrained weights), `metrics`+`sizing` (metrics on sized portfolio).
    - Record a probe matrix (probe id, target, shape, result, log path).

3. **On proven regression:** apply smallest fix in allowed editable area only → add minimal regression test → re-run affected tests + all three gate floors → capture durable evidence.
4. **If no proven gaps:** record **"C42 rotation: no proven gaps"** with per-area/per-probe evidence and log paths.
5. **Before exit, refresh this same `HANDOFF.md`** (single durable handoff) with timestamp/HEAD, gate results+logs, full C42 probe matrix outcomes, working-tree notes, and the next concrete heavy task (if C42 closes cleanly, define and start C43 rotation with ≥20 new probes on remaining unexhausted surfaces).

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` is historical only; not current-checkout evidence.

### Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C41 without a new statable reproducible failure + durable evidence.

## Next focus campaign (binding)

**Primary (now):** **C42 ROTATION** — ≥20 new adversarial probes with durable evidence across all required surfaces above; keep gate floors green. This is mandatory heavy work, not optional planning.

**If C42 closes with no proven gaps:** refresh handoff and immediately define/execute **C43 rotation** (≥20 new probes, new shapes, durable logs) on any remaining unexhausted editable surfaces/cross-interactions; continue the evidence-driven hardening loop.

**Current status (verified at this refresh):**
- Working tree: clean tracked state. Untracked artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit).
- Imports sanity: `quality, signals, portfolio, config, backtest, data_sources, attribution, metrics, cli, costs, regime, shorting, sizing` → `imports_ok` (PYTHONPATH=$PWD, package path `strategies.betting_against_beta.*`).
- C41: CLOSED, no proven gaps (prior evidence).
- C42: **NOT started** — required before closure of this session’s handoff.
- Gate 1 baseline: GREEN (898 passed/5 skipped rc=0) @ this refresh. Gates 2/3 pending re-verification.
