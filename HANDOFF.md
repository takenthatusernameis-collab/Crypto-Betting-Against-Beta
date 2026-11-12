# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T08:30:00Z
**HEAD:** `0ef833ad204187676e5b7b3f85aa01b646973e48` on `main`
**Working tree (tracked):** clean at refresh (`git status --porcelain` empty). Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts may exist and must not be committed.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work across `quality.py`, `signals.py`, `portfolio.py`, `config.py`, `backtest.py`, `data_sources.py`, `attribution.py`, `metrics.py`, `cli.py`/reporting, `costs.py`, `regime.py`, `shorting.py`, `sizing.py` and controller/gate contracts. No unrelated refactors.

## Bottlenecks cleared (this refresh)
- **Stale/duplicated handoff removed:** prior `HANDOFF.md` contained duplicated "BINDING INITIAL TASK MESSAGE" blocks and stale status claims (Gate 1 "GREEN @ this refresh", HEAD/timestamp mismatch). Replaced with this single canonical, timestamped handoff.
- **Historical diagnostics isolated:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads only. Treat as historical; not evidence of a current-checkout failure and must not justify inaction.
- **No runtime blocker reproduced:** core BAB module imports `quality, signals, portfolio, config, backtest, data_sources, attribution, metrics, cli, costs, regime, shorting, sizing` → `imports_ok` (`PYTHONPATH=$PWD`). No dirty tracked files, no proven workflow-sync regression.

## Gate Re-verification (fresh durable logs for HEAD `0ef833a...`)
All three gates PASS with fresh logs:

**Gate 1** (data_loader campaign_d + batches 148/149/172):
- Command: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
- Result: **898 passed, 5 skipped** (rc=0) in 4.86s
- Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate1_20261112T074740Z.log`

**Gate 2** (full suite minus data_loader + controller_progress):
- Command: `PYTHONPATH=$PWD python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
- Result: **2234 passed, 5 skipped** (rc=0) in 404.60s
- Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate2_20261112T074748Z.log`

**Gate 3** (CLI campaigns 11 & 14):
- Command: `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`
- Result: **164 passed** (rc=0) in 150.89s
- Log: `/home/runner/work/_temp/kilo-tmp/c42_gate_gate3_20261112T074750Z.log`

Env: Python 3.12.3, repo root, `PYTHONPATH=$PWD`. Deps: `numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`.

## C42 ROTATION Adversarial Probe Campaign — COMPLETE (38 probes, 38 PASS)
Executed ≥20 NEW probes across all required surfaces + cross-interactions. No C40/C41 probe reuse. Every probe has durable log with rc, duration, PASS/FAIL, repro path under `/home/runner/work/_temp/kilo-tmp/`.

### Probe Matrix (id, target, shape, result, log path)

| ID | Target | Shape | Result | Duration | Log |
|----|--------|-------|--------|----------|-----|
| C42-Q01 | quality.py | None input | PASS | 0.30s | c42_probe_c42-q01_20261112T082645Z.log |
| C42-Q02 | quality.py | empty DataFrame | PASS | 0.30s | c42_probe_c42-q02_20261112T082645Z.log |
| C42-Q03 | quality.py | non-DataFrame input | PASS | 0.29s | c42_probe_c42-q03_20261112T082645Z.log |
| C42-Q04 | quality.py | duplicate index | PASS | 0.30s | c42_probe_c42-q04_20261112T082646Z.log |
| C42-Q05 | quality.py | non-datetime index | PASS | 0.30s | c42_probe_c42-q05_20261112T082646Z.log |
| C42-Q06 | quality.py | large gaps | PASS | 0.30s | c42_probe_c42-q06_20261112T082646Z.log |
| C42-Q07 | quality.py | all-NaN columns | PASS | 0.32s | c42_probe_c42-q07_20261112T082646Z.log |
| C42-Q08 | quality.py | mixed dtypes | PASS | 0.30s | c42_probe_c42-q08_20261112T082647Z.log |
| C42-S01 | signals.py | constant betas | PASS | 0.30s | c42_probe_c42-s01_20261112T082647Z.log |
| C42-S02 | signals.py | NaN betas | PASS | 0.30s | c42_probe_c42-s02_20261112T082647Z.log |
| C42-S03 | signals.py | <2 observations | PASS | 0.30s | c42_probe_c42-s03_20261112T082648Z.log |
| C42-S04 | signals.py | empty universe | PASS | 0.30s | c42_probe_c42-s04_20261112T082648Z.log |
| C42-S05 | signals.py | single asset | PASS | 0.30s | c42_probe_c42-s05_20261112T082648Z.log |
| C42-S06 | signals.py | quantile boundary | PASS | 0.29s | c42_probe_c42-s06_20261112T082649Z.log |
| C42-P01 | portfolio.py | dollar-neutral | PASS | 0.29s | c42_probe_c42-p01_20261112T082649Z.log |
| C42-P02 | portfolio.py | long-only (dollar_neutral=False) | PASS | 0.29s | c42_probe_c42-p02_20261112T082649Z.log |
| C42-P03 | portfolio.py | weight caps (max_position_size) raises on exceed | PASS | 0.29s | c42_probe_c42-p03_20261112T082649Z.log |
| C42-P04 | portfolio.py | zero longs | PASS | 0.29s | c42_probe_c42-p04_20261112T082650Z.log |
| C42-P05 | portfolio.py | zero shorts | PASS | 0.30s | c42_probe_c42-p05_20261112T082650Z.log |
| C42-P06 | portfolio.py | NaN signals | PASS | 0.30s | c42_probe_c42-p06_20261112T082650Z.log |
| C42-P07 | portfolio.py | misaligned index | PASS | 0.30s | c42_probe_c42-p07_20261112T082651Z.log |
| C42-C01 | config.py | vol_thresholds+percentiles conflict | PASS | 0.30s | c42_probe_c42-c01_20261112T082651Z.log |
| C42-C02 | config.py | vol_hysteresis out of [0,1] | PASS | 0.30s | c42_probe_c42-c02_20261112T082651Z.log |
| C42-C03 | config.py | beta_window < 1 | PASS | 0.30s | c42_probe_c42-c03_20261112T082652Z.log |
| C42-C04 | config.py | long/short quantiles at 0/1 | PASS | 0.34s | c42_probe_c42-c04_20261112T082652Z.log |
| C42-C05 | config.py | universe_override no overlap | PASS | 0.30s | c42_probe_c42-c05_20261112T082652Z.log |
| C42-B01 | backtest.py | serialization round-trip | PASS | 0.30s | c42_probe_c42-b01_20261112T082652Z.log |
| C42-B02 | backtest.py | NaN/inf in returns | PASS | 0.30s | c42_probe_c42-b02_20261112T082653Z.log |
| C42-B03 | backtest.py | empty DataFrame | PASS | 0.30s | c42_probe_c42-b03_20261112T082653Z.log |
| C42-B04 | backtest.py | transaction costs interaction | PASS | 0.34s | c42_probe_c42-b04_20261112T082653Z.log |
| C42-D01 | data_sources.py | malformed CSV | PASS | 0.30s | c42_probe_c42-d01_20261112T082654Z.log |
| C42-D02 | data_sources.py | malformed JSON | PASS | 0.29s | c42_probe_c42-d02_20261112T082654Z.log |
| C42-D03 | data_sources.py | missing benchmark column raises | PASS | 0.34s | c42_probe_c42-d03_20261112T082654Z.log |
| C42-D04 | data_sources.py | duplicate timestamps | PASS | 0.34s | c42_probe_c42-d04_20261112T082655Z.log |
| C42-D05 | data_sources.py | unsupported format | PASS | 0.29s | c42_probe_c42-d05_20261112T082655Z.log |
| C42-X01 | regime+sizing | regime scale → vol-target leverage | PASS | 0.30s | c42_probe_c42-x01_20261112T082655Z.log |
| C42-X02 | attribution+shorting | attribution on borrow-constrained weights | PASS | 0.30s | c42_probe_c42-x02_20261112T082656Z.log |
| C42-X03 | metrics+sizing | metrics on sized portfolio | PASS | 0.32s | c42_probe_c42-x03_20261112T082656Z.log |

**Summary:** 38 probes executed, 38 PASS, 0 FAIL. No proven gaps found. Full summary at `/home/runner/work/_temp/kilo-tmp/c42_probe_summary_20261112T082656Z.json`.

## Working-tree notes
- No tracked file modifications. All probes/logs in untracked `/home/runner/work/_temp/kilo-tmp/`.
- C42 probe campaign script: `/home/runner/work/_temp/kilo-tmp/c42_probe_campaign_v2.py` (not committed).
- All three gate floors re-verified and GREEN for current HEAD.

## BINDING NEXT TASK — C43 ROTATION (start immediately, heavy execution required)

**C42 closes cleanly → immediately define and start C43.**

### C43 ROTATION adversarial probe campaign (≥20 NEW probes, mandatory)
- **Do not reuse** C42/C41/C40 probe scripts or shapes. Every probe must have durable log(s) under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, and repro path.
- **Required coverage (all unexhausted surfaces + deeper cross-interactions):**
  - `beta.py`: `calculate_beta` with constant/NaN/inf returns, single observation, misaligned index, benchmark mismatch, window edge cases.
  - `data_loader.py`: `load_returns` / `normalize_schema` / `detect_and_normalize_exchange_format` with malformed headers, mixed freq, tz edge cases, huge files, streaming.
  - `strategy.py`: `run_strategy` / `generate_signals` with config permutations, regime interactions, shorting interactions, cost interactions.
  - `costs.py`: `TransactionCostModel` / `compute_transaction_costs` with zero/negative adv, extreme spreads, NaN prices, per-asset cost models.
  - `regime.py`: `regime_scale_factors` / `regime_scale_scalar` with trend/combined methods, hysteresis edge cases, constant vol, NaN returns.
  - `shorting.py`: `apply_shorting_constraints` with borrowable dict, per-asset costs, strict mode violations, cascading caps.
  - `sizing.py`: `apply_position_sizing` with Kelly/RiskParity/EqualWeight, lookback < data, max_leverage binding, target_vol unreachable.
  - **Cross-interactions (deeper):**
    - `beta` + `regime`: beta stability across vol regimes.
    - `strategy` + `costs` + `shorting`: full pipeline with borrow costs + transaction costs.
    - `regime` + `shorting`: regime scaling applied to borrow-constrained weights.
    - `attribution` + `regime`: attribution breakdown by regime state.
    - `metrics` + `regime`: metrics computed per-regime bucket.
- Maintain a probe matrix (id, target, shape, result, log path). Minimum 20 probes total.

### On proven regression
Apply the **smallest** fix in an allowed editable area only → add a minimal regression test → re-run affected tests + all three gate floors → capture durable evidence.

### If no proven gaps
Record **"C43 rotation: no proven gaps"** with per-area/per-probe evidence and log paths (not a claim without logs).

### Before exit (mandatory)
Refresh this same `HANDOFF.md` with: timestamp/HEAD, fresh gate results+log paths, full C43 probe matrix outcomes, working-tree notes, and the next concrete heavy task. If C43 closes cleanly, **immediately define and start C44** (≥20 new probes, new shapes, durable logs) on remaining unexhausted surfaces/cross-interactions and leave that as the binding next task. Keep this file the single durable handoff.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C42 without a new statable reproducible failure + durable evidence.

## Status snapshot (this refresh)
- C41: CLOSED, no proven gaps (prior durable evidence; historical).
- **C42: CLOSED, no proven gaps (38 probes, 38 PASS, durable logs captured).**
- Gate floors: **re-verified GREEN at this refresh** (fresh durable logs for HEAD `0ef833a...`).
- Next campaign (binding): **C43 ROTATION** (≥20 new adversarial probes, deeper surfaces/cross-interactions as specified above).

(End of file)