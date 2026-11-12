# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T02:14:44Z
**HEAD:** `48b39b4915b87536f7b31ee7f592bee0cdabb6d1` on `main` (working tree clean at handoff refresh)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

---

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C38, execute immediately)

**C38 is the active campaign (gate floors + rotated/expanded adversarial probe matrix on allowed surfaces). Do heavy, evidence-producing work now. "No proven gaps" is allowed only after full Step 1 + Step 2 execution with durable evidence — never a reason to skip. C38 has NOT been executed at this HEAD yet — start with Step 1 now.**

### Step 1 — Gate floors (mandatory, first)
Run to completion with ample timeout and durable logs under `/home/runner/work/_temp/kilo-tmp/c38_gate_<name>_<ts>.log`. Use `.venv/bin/python -m pytest ...` (system `python3` may lack pytest). Timeout/interruption without observed failure is **inconclusive, not green**.

1. `.venv/bin/python -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - **Floor:** ≥898 passed, 5 skipped, rc=0 (C37 baseline: 898 passed, 5 skipped).
2. `.venv/bin/python -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - **Floor:** rc=0 (C37 baseline: 2234 passed, 5 skipped). Slow; timeout ≥900s or monitor, never abort early.
3. `.venv/bin/python -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`
   - **Floor:** ≥164 passed, 0 failed, rc=0.

Record exact counts+rc+durations+durable log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

### Step 2 — C38 adversarial probe campaign (mandatory after Step 1 green)
Systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Execute all areas and **rotate/expand beyond C36/C37** (never skip heavy verification):

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty/permission-denied `--data`, benchmark missing/overlap/duplicate, empty/whitespace/duplicate universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths, `bab_backtest_report.py` arg combos. **C38 rotation/expansion:** malformed/huge CSV headers, Unicode/locale-ish tokens, `--min-rows`/`--lookback` boundary interactions with real files, output path permission/overwrite behaviors, multiple repeated flags, symlink+dir edge mixes, `--universe` token normalization/idempotence under odd spacing/commas.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series, serialization safety (raw `metrics.summary` may be non-finite by contract; CLI/report sanitized paths must remain strict-finite/no-leakage). **C38 rotation/expansion:** empty/zero-variance benchmarks, mixed-frequency/index dtype oddities, extreme drawdown/turnover cases, report/CLI invariants over strategy outputs containing non-finite raw metrics.
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths. Use correct APIs/signatures (regime expects DataFrames; `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd)`; `trade_attribution(weights)` 1-arg per signature; `sizing.apply_position_sizing(signals, returns, sizer)`). **C38 rotation/expansion:** per-asset/heterogeneous cost params, borrow limit edge mixes, sizer behavior on empty/all-zero/singular inputs, regime scaling interaction with sizing/shorting constraints, attribution on no-trade/partial-trade paths.

For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C38: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and set next task to "C39: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)".
- Do not exit after Step 1 alone. Do not invent failures.

**Rules:** Do not reopen C28–C37 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without evidenced attempt and durable logs. This file is the sole durable coordination artifact.

---

## C38 status (2026-11-12T02:14:44Z, HEAD `48b39b4`) — NOT STARTED / PENDING EXECUTION
- **Step 1 gates:** not run at this HEAD in this session (handoff refresh only). Next agent must execute immediately and capture durable logs (`/home/runner/work/_temp/kilo-tmp/c38_gate_*`).
- **Step 2 probes:** not run. Rotate/expand beyond C36/C37 per matrix above.
- **Next concrete action:** run C38 Step 1 gate floors now; on green proceed to full Step 2 probe campaign; on red fix minimally with regression in allowed areas and re-gate; then close with evidence. No commit/push unless explicitly requested.

---

## Bottlenecks / environment (resolved guidance — do not re-litigate)
- **`tests/test_controller_progress_accounting.py` excluded, NOT a BAB blocker** (fails on `.github/workflows/*` pattern sync; infra only). Do not edit `.github/workflows/*`; do not weaken/delete it.
- **Use `.venv/bin/python -m pytest`** (system Python may lack pytest). Full suites are slow; use ample timeout/monitor and durable logs. Timeout without observed failure is inconclusive.
- **Probe harness:** run from repo root or `sys.path.insert(0, repo_root)` in untracked `/home/runner/work/_temp/kilo-tmp/` scripts. Use correct APIs/signatures; treat CLI user-error contract as "nonzero + no traceback" unless stricter rc evidenced by tests. Probe "FAIL" labels are not bugs without contract/API-aligned evidence.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit.
- **Historical only:** `research_state/workflow_run_diagnostics.jsonl` are prior captured log signals, not current source/test failures.

---

## C37 session results (2026-11-12T01:24–01:33Z refresh window, HEAD `55d5ff7`) — COMPLETE, no proven BAB gaps

### Step 1 gates (all PASS, durable evidence present)
- campaign_d+batch148/149/172: **898 passed, 5 skipped, rc=0** (3.16s) — `/home/runner/work/_temp/kilo-tmp/c37_gate_campaign_d_20261112T011330Z.log`
- full BAB excl data_loader/controller: **2234 passed, 5 skipped, rc=0** (262.45s) — `/home/runner/work/_temp/kilo-tmp/c37_gate_full_bab_20261112T012004Z.log` (latest full-gate evidence)
- campaign11+14: **164 passed, 0 failed, rc=0** (98.35s) — `/home/runner/work/_temp/kilo-tmp/c37_gate_campaign11_14_20261112T011821Z.log`

All floors satisfied (≥898/5, rc=0 full BAB excl data_loader/controller, ≥164 campaign11+14).

### Step 2 probe campaign (executed, durable logs)
- Probe rerun/log: `/home/runner/work/_temp/kilo-tmp/c37_probe_rerun_20261112T012432Z.log`
- Coverage: CLI/API/reporting parity & edge contracts; metrics/reporting robustness; costs/regime/attribution/shorting/sizing boundaries; scripts help surfaces.
- Result: **6 FAILs, all analyzed as non-product (probe contract-expectation issues), consistent with C36:**
  1. `METRICS::degenerate_series_all_inf`, `degenerate_series_neg_inf`, `degenerate_series_extreme`, `degenerate_series_mixed_nan_inf` — raw `metrics.summary` allowed non-finite by contract; CLI/report sanitized paths strict-finite (`CLI::json_report_strict_finite` PASS, `METRICS::strategy_run_sanitized` PASS).
  2. `COSTS::cost_model_adv_0`, `COSTS::zero_weight_change` — functions completed without exception, finite return, no traceback/corruption; probe assumption not evidenced as required contract.

No reproducible BAB-relevant failure with durable contract-aligned evidence was identified; therefore **no fixes/regressions were required**.

### Closure
- **C37: no proven gaps** after full Step 1 + Step 2 execution with durable evidence. Gates green, probe matrix executed and analyzed, no proven BAB-relevant defects.

---

## C28–C36 status (closed) — do not reopen without new evidence
- **C28–C33:** CLOSED per prior evidence (`c28_*`–`c33_*` logs under `/home/runner/work/_temp/kilo-tmp/`).
- **C34:** COMPLETE, no proven gaps.
- **C35:** COMPLETE, no proven gaps.
- **C36:** COMPLETE, no proven gaps.
- **C37:** COMPLETE, no proven gaps (this session).

---

## Locks / prohibitions
- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

---

## Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durations+durable log paths, C38 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
