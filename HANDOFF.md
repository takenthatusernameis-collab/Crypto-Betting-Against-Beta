# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T02:50:52Z
**HEAD:** `79c4985a3b8a8330b7c8ca2034488a6643629afe` on `main` (working tree clean at handoff refresh)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits (infra sync already done), no commit/push unless explicitly requested.

---

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C38, execute immediately)

**C38 is the active campaign (gate floors + rotated/expanded adversarial probe matrix on allowed surfaces). Do heavy, evidence-producing work now. "No proven gaps" is allowed only after full Step 1 + Step 2 execution with durable evidence — never a reason to skip.**

### Step 1 — Gate floors (mandatory, first)
Run to completion with ample timeout and durable logs under `/home/runner/work/_temp/kilo-tmp/c38_gate_<name>_<ts>.log`. Use `.venv/bin/python3 -m pytest ...` if available; system `python3` may lack deps. Timeout/interruption without observed failure is **inconclusive, not green**.

1. `.venv/bin/python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - **Floor:** ≥898 passed, 5 skipped, rc=0 (baseline: 898 passed, 5 skipped).
   - **C38 evidence:** `c38_gate_campaign_d_20261112T022312Z.log` → **898 passed, 5 skipped** (rc=0).
2. `.venv/bin/python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - **Floor:** rc=0 (baseline: 2234 passed, 5 skipped). Slow; timeout ≥900s or monitor, never abort early.
   - **C38 evidence:** Gate attempted multiple times (logs under `c38_gate_full_bab_*`); if truncated/empty due to timeout in harness, run with explicit long timeout and capture final summary line to durable log. Do **not** skip — record exact counts+rc+durations.
3. `.venv/bin/python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`
   - **Floor:** ≥164 passed, 0 failed, rc=0.
   - **C38 evidence:** `c38_gate_campaign11_14_20261112T023932Z.log` → **164 passed** (rc=0, 103.58s).

Record exact counts+rc+durations+durable log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

### Step 2 — C38 adversarial probe campaign (mandatory after Step 1 green)
Systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Execute all areas and **rotate/expand beyond C36/C37** (never skip heavy verification):

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty/permission-denied `--data`, benchmark missing/overlap/duplicate, empty/whitespace/duplicate universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths, `bab_backtest_report.py` arg combos. **C38 rotation/expansion:** malformed/huge CSV headers, Unicode/locale-ish tokens, `--min-rows`/`--lookback` boundary interactions with real files, output path permission/overwrite behaviors, multiple repeated flags, symlink+dir edge mixes, `--universe` token normalization/idempotence under odd spacing/commas.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series, serialization safety (raw `metrics.summary` may be non-finite by contract; CLI/report sanitized paths must remain strict-finite/no-leakage). **C38 probes:** `metrics.summary` accepts degenerate series (all-inf/-inf/NaN) without uncaught exception (see `c38_probe_metrics2_*`).
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths. Use correct APIs/signatures (`compute_transaction_costs(weights, weights_prev, prices, ...)` 3-arg baseline OK; regime via `get_regime_state`; `trade_attribution(backtest_df)` 1-arg; `apply_position_sizing(signals, returns, sizer)`; `apply_shorting_constraints(weights)`). **C38 probes:** basic APIs exercised OK (`c38_probe_apis_*`, `c38_probe_sizing_shorting_*`).

For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C38: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and set next task to "C39: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)".
- Do not exit after Step 1 alone. Do not invent failures.

**Rules:** Do not reopen C28–C37 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without evidenced attempt and durable logs. This file is the sole durable coordination artifact.

---

## C38 status (2026-11-12T02:50:52Z, HEAD `79c4985`) — IN PROGRESS
- **Infra fix applied:** Synced `.github/workflows/main.yml` `stage_safe_changes` to include `*/.github/workflows/*` (controller tests: 68 passed).
- **Step 1 gates:**
  - campaign_d+batch148/149/172: **898 passed, 5 skipped, rc=0** — `c38_gate_campaign_d_20261112T022312Z.log`
  - full BAB excl data_loader/controller: **ATTEMPTED** (timeouts in harness; see `c38_gate_full_bab_*` logs) — must run to completion with ample timeout and record exact final summary.
  - campaign11+14: **164 passed, 0 failed, rc=0** (103.58s) — `c38_gate_campaign11_14_20261112T023932Z.log`
- **Step 2 probes (started):** CLI/API/synthetic OK; metrics summary handles degenerate inputs without exception; costs/regime/attribution/sizing/shorting APIs exercised with correct signatures — logs under `c38_probe_*_20261112T*.log`. Continue expanding to full matrix (reporting/CLI edge combos, scripts, more regime/attribution/costs boundaries).
- **Next concrete action:** Complete full BAB gate (excl data_loader/controller) to durable log with timeout≥900s; finish C38 probe matrix per Step 2; if any reproducible BAB-relevant failure found fix minimally + regression + re-gate; else record C38 no-proven-gaps with evidence and set C39 task.

---

## Bottlenecks / environment (resolved guidance — do not re-litigate)
- **`tests/test_controller_progress_accounting.py`** — synced; passing (68/68).
- **Use `.venv/bin/python3 -m pytest`** where available. Full suites are slow; use ample timeout/monitor and durable logs. Timeout without observed failure is inconclusive.
- **Probe harness:** run from repo root or `sys.path.insert(0, repo_root)` in untracked `/home/runner/work/_temp/kilo-tmp/` scripts. Use correct APIs/signatures; treat CLI user-error contract as "nonzero + no traceback" unless stricter rc evidenced by tests.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit.
- **Historical only:** `research_state/workflow_run_diagnostics.jsonl` are prior captured log signals, not current source/test failures.

---

## Locks / prohibitions
- **No** edits to `.github/workflows/*` (sync done).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.

---

## Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durations+durable log paths, C38 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
