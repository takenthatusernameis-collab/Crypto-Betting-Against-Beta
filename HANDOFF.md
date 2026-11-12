# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T00:42:54Z
**HEAD:** `18bcc5c` on `main`
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C36, execute immediately)

**C36 is the active campaign (gate-integrity maintenance + expanded adversarial probe matrix). Do heavy, evidence-producing work now. "No proven gaps" is allowed only after full Step 1 + Step 2 execution with durable evidence — never a reason to skip.**

### Step 1 — Gate floors (mandatory, first)
Run to completion with ample timeout and durable logs under `/home/runner/work/_temp/kilo-tmp/c36_gate_<name>_<ts>.log`. Use `.venv/bin/python -m pytest ...` (system `python3` may lack pytest). Timeout/interruption without observed failure is **inconclusive, not green**.

1. `.venv/bin/python -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - **Floor:** ≥898 passed, 5 skipped, rc=0 (C35 baseline: 898 passed, 5 skipped).
2. `.venv/bin/python -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - **Floor:** rc=0 (C35 baseline: 2234 passed, 5 skipped). Slow; timeout ≥900s or monitor, never abort early.
3. `.venv/bin/python -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`
   - **Floor:** ≥164 passed, 0 failed, rc=0.

Record exact counts+rc+durations+durable log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

### Step 2 — C36 adversarial probe campaign (mandatory after Step 1 green)
Systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Execute all areas below and rotate/expand beyond C35 (never skip heavy verification):

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty/permission-denied `--data`, benchmark missing/overlap/duplicate, empty/whitespace/duplicate universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths, `bab_backtest_report.py` arg combos. **C36 expansion:** test `--min-rows` edge cases, `--lookback` edge cases, `--output` directory traversal, multiple `--universe` flag interactions, `--data` with symlinks.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series, serialization safety (raw `metrics.summary` may be non-finite by contract; CLI/report sanitized paths must remain strict-finite/no-leakage). **C36 expansion:** test `metrics.compute_metrics` with multi-column benchmark, `metrics.summary` with timezone-aware indices, cross-sectional metrics edge cases.
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths. Use correct APIs/signatures (regime expects DataFrames; `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd)`; `trade_attribution(weights)` 1-arg per signature; `sizing.apply_position_sizing(signals, returns, sizer)`). **C36 expansion:** test `ShortingConstraints` with per-asset borrow_bps dict, `BorrowConstraints` with wildcard borrowable, `VolatilityTargetSizer` with zero target_vol, `RiskParitySizer` with singular covariance, sizer string shorthand with invalid names, `apply_position_sizing` with duplicate column names.

For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C36: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and set next task to "C37: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)".
- Do not exit after Step 1 alone. Do not invent failures.

**Rules:** Do not reopen C28–C35 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## Bottlenecks / environment (resolved guidance — do not re-litigate)
- **`tests/test_controller_progress_accounting.py` excluded, NOT a BAB blocker** (fails on `.github/workflows/*` pattern sync; infra only). Do not edit `.github/workflows/*`; do not weaken/delete it.
- **Use `.venv/bin/python -m pytest`** (system Python may lack pytest). Full suites are slow; use ample timeout/monitor and durable logs. Timeout without observed failure is inconclusive.
- **Probe harness:** run from repo root or `sys.path.insert(0, repo_root)` in untracked `/home/runner/work/_temp/kilo-tmp/` scripts. Use correct APIs/signatures; treat CLI user-error contract as "nonzero + no traceback" unless stricter rc evidenced by tests.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit.
- **Historical only:** `research_state/workflow_run_diagnostics.jsonl` are prior captured log signals, not current source/test failures.

## C36 session results (2026-11-12T00:42:54Z, HEAD `18bcc5c`) — Step 1 COMPLETE

### Step 1 gates (all PASS):
- campaign_d+batch148/149/172: `898 passed, 5 skipped, rc=0` (3.23s) — `/home/runner/work/_temp/kilo-tmp/c36_gate_campaign_d_20261112T004254Z.log`
- full BAB excl data_loader/controller: `2234 passed, 5 skipped, rc=0` (272.65s) — `/home/runner/work/_temp/kilo-tmp/c36_gate_full_bab_20261112T004254Z.log`
- campaign11+14: `164 passed, rc=0` (100.22s) — `/home/runner/work/_temp/kilo-tmp/c36_gate_campaign11_14_20261112T004254Z.log`

### Step 2 probes: IN PROGRESS

---

## C28–C35 status (closed) — do not reopen without new evidence
- **C28–C33:** CLOSED per prior evidence (`c28_*`–`c33_*` logs under `/home/runner/work/_temp/kilo-tmp/`).
- **C34:** COMPLETE, no proven gaps (see logs above).
- **C35:** COMPLETE, no proven gaps (see logs above).

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durations+durable log paths, C36 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.