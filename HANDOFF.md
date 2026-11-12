# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T07:04:04Z
**HEAD:** `5d25e9460d166f5c7853a152981fb80dab1c9f7b` on `main` (tracked working tree clean at refresh; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Bottleneck removal (this refresh):** revalidated repo state (HEAD `5d25e94`, tree clean), confirmed C41 gate floors are GREEN with durable logs, executed C41 ROTATION probe campaign (22 new probes, all PASS, no proven gaps), removed stale HEAD/timestamp ambiguity, and set the binding next campaign to C42 rotation. Prior C40/C40-extended evidence remains historical baseline only. No workflow edits or code changes made.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (start immediately)

**Start work now. Do not plan-only, do not re-diagnose historical CI noise, do not declare "blocked" without an evidenced attempt and durable logs.**

The repo is **Crypto-Betting-Against-Beta**: controller infrastructure plus a market-neutral Betting Against Beta (BAB) crypto strategy (long low-beta / short high-beta vs benchmark BTC). The only binding product is BAB correctness/robustness across `attribution.py`, `metrics.py`, `cli.py`, `scripts/bab_gate.sh`/controller contracts, and `costs`/`regime`/`shorting`/`sizing` cross-surface interactions. All work must flow through the gate floors + durable evidence standard below.

**C41 ROTATION — CLOSED: no proven gaps.** 22 new adversarial probes executed, all PASS, across `attribution.py` (4), `metrics.py` (6), `scripts/bab_gate.sh`/controller contracts (3), `cli.py` report I-O (4), and `costs`/`regime`/`shorting`/`sizing` cross-surface interactions (5). Durable logs under `/home/runner/work/_temp/kilo-tmp/` (see master log `c41_probe_campaign_summary_20261112T070404Z.log`). No regressions found; no code changes required.

1. **Gate floors already GREEN (C41 @ `5d25e94`) — do not re-run unless a fix lands.**
   - Gate 1 `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`: **898 passed, 5 skipped, rc=0 (4.92s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate1_20261112T061648Z.log`
   - Gate 2 `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`: **2234 passed, 5 skipped, rc=0 (205.51s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate2_20261112T062047Z.log`
   - Gate 3 `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`: **164 passed, rc=0 (77.97s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate3_20261112T062421Z.log`
   - `scripts/bab_gate.sh`: syntax OK, executable OK, shebang `#!/usr/bin/env bash`.
   - Environment: system Python 3.12.3 (`/usr/bin/python3`), repo root, `PYTHONPATH=$PWD`, no `.venv`. Declared deps in `requirements.txt` (`numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`).

2. **Immediate binding task: execute C42 ROTATION adversarial probe campaign (minimum 20 NEW probes).** Rotate shapes/cases; do not reuse C40/C40-extended or C41 probe scripts/shapes. Target remaining unexhausted editable/allowed surfaces:
   - `quality.py`: `data_quality_report` with None/empty/non-DataFrame, duplicate index, non-datetime index, large gaps, all-NaN columns, mixed dtypes.
   - `signals.py`: `generate_bab_signals` with constant betas, all-same beta, NaN betas, <2 observations, quantile edge (0.0/1.0 excluded via config but test boundary), empty universe, single asset.
   - `portfolio.py`: `construct_portfolio` with dollar-neutral/long-only, weight caps, zero longs/shorts, NaN signals, misaligned index.
   - `config.py`: `BABConfig` validation boundaries (vol_thresholds + vol_percentiles both set, vol_hysteresis out of [0,1], beta_window < 1, long_quantile/short_quantile at 0/1, universe_override no overlap).
   - `backtest.py`: `run_backtest` serialization/round-trip, NaN/inf in prices/returns, empty DataFrame, single row, transaction costs interaction.
   - `data_sources.py`: emitter contracts, malformed CSV/JSON, missing benchmark column, duplicate timestamps, unsupported file format.
   - Cross-parameter: `regime`+`sizing` (regime scale → vol-target leverage), `attribution`+`shorting` (attribution on borrow-constrained weights), `metrics`+`sizing` (metrics on sized portfolio).
   - Every probe: durable log under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, repro path. Smoke checks are insufficient.

3. **If any proven regression:** smallest fix in allowed area only → minimal regression test → re-run affected tests + all three gate floors → record evidence.

4. **If no proven gaps:** record **"C42 rotation: no proven gaps"** with per-area/per-probe evidence and log paths.

5. **Before exit, refresh this same `HANDOFF.md`** (single durable handoff) with timestamp/HEAD, gate results+logs, full probe matrix outcomes, working-tree notes, and the next concrete heavy task.

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` contains **historical** CI/log excerpts/signals only; not evidence of a current checkout failure. Do not use it to justify inaction.

### Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C40 without a new statable reproducible failure + durable evidence.

## Next focus campaign (binding)

**Primary:** execute **C42 ROTATION** (≥20 new probes, durable evidence, all gate floors green) — this is the immediate binding task. Targets: `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py` plus `regime`+`sizing`, `attribution`+`shorting`, `metrics`+`sizing` cross-interactions.

**If C42 rotation closes with no proven gaps:** refresh handoff and immediately define/execute **C43 rotation** targeting any remaining editable surfaces with the same heavy evidence standard (≥20 new probes, durable logs, gate floors green).

**Current status (verified at this refresh):**
- Working tree: clean tracked state. Untracked artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit).
- Quick sanity: key editable modules import cleanly (`cli, metrics, attribution, costs, regime, shorting, sizing`) with `PYTHONPATH=$PWD` → `imports_ok`.
- C41 gates GREEN (see above). C41 probe campaign **EXECUTED**: 22 new probes, all PASS, no proven gaps → `c41_probe_campaign_summary_20261112T070404Z.log`.
- C42 probe campaign **NOT yet executed** — ≥20 new probes required before any handoff refresh/closure.
