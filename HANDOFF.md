# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T07:37:51Z
**HEAD:** `1a3143a153dfed9ff6399d84c09b354bec3c21e3` on `main` (tracked working tree clean; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Handoff staleness fixed at this refresh:** prior handoff cited HEAD `479d7aa` and closed C41; actual HEAD advanced to `1a3143a` with clean tree. Quick sanity: editable/core modules import cleanly with `PYTHONPATH=$PWD` (`imports_ok`). `research_state/workflow_run_diagnostics.jsonl` remains **historical** Oct-2026 CI/log excerpts only — not evidence of current checkout failure and must not justify inaction.

**Bottleneck status:** no active blockers, no dirty tracked state, no workflow sync issue reproduced. C41 rotation is CLOSED (22/22 probes PASS, no proven gaps/regressions per prior durable logs under `/home/runner/work/_temp/kilo-tmp/`). Prior gate floors reported GREEN @ C41 and were not re-run at this refresh because no fix landed; re-verify with durable logs before/alongside any code change.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (start immediately)

**Start work now. Do not plan-only. Do not re-diagnose historical CI noise. Do not declare "blocked" without an evidenced attempt and durable logs.**

The repo is **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark). Binding product work is BAB correctness/robustness across `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py`, `attribution.py`, `metrics.py`, `cli.py`/reporting, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, and controller/gate contracts — driven by proven evidence only.

1. **Establish/reconfirm gate baseline with durable logs before claiming progress (re-run if any fix lands or if baseline is in doubt).**
   - Gate 1: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - Gate 2: `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - Gate 3: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`
   - Optional full gate: `scripts/bab_gate.sh` (self-contained; coverage optional).
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
- Imports sanity: `quality, signals, portfolio, config, backtest, data_sources, attribution, metrics, cli, costs, regime, shorting, sizing` → `imports_ok` (PYTHONPATH=$PWD).
- C41: CLOSED, no proven gaps (prior evidence).
- C42: **NOT started** — required before closure of this session’s handoff.
