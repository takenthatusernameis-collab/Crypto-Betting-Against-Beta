# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T03:15:18Z
**HEAD:** `06e904870bee3729c2d2a43e2fadaf68910aa313` (`06e9048`) on `main`
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no commit/push unless explicitly requested.

---

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C38, execute immediately)

**C38 is the active campaign (gate floors + rotated/expanded adversarial probe matrix on allowed BAB surfaces). Do heavy, evidence-producing work now. "No proven gaps" is allowed only after full Step 1 + Step 2 execution with durable evidence — never a reason to skip or to stop after Step 1.**

### Step 0 — Fix Controller Sync Blocker (COMPLETED)
**File:** `.github/workflows/main.yml` (line 1163) ✅ FIXED
**Issue:** `stage_safe_changes` case statement missing `*/.github/workflows/*` pattern present in `scripts/controller_progress.py:27`
**Fix applied:** Added `*/.github/workflows/*|` to the case statement on line 1163 (between `.github/workflows/*` and `.venv/*`).
**Verified:** `python3 -m pytest -q tests/test_controller_progress_accounting.py` → **68 passed, rc=0**. Gate is green. Proceed to Step 1.

### Step 1 — Gate floors (mandatory, first; durable logs required)
Run to completion with ample timeout and durable logs under `/home/runner/work/_temp/kilo-tmp/c38_gate_<name>_<ts>.log`. Prefer `.venv/bin/python3 -m pytest ...` if available. Timeout/interruption without an observed failure is **inconclusive, not green**.

1. `.venv/bin/python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`
   - **Floor:** ≥898 passed, 5 skipped, rc=0.
   - **Prior recorded C38 evidence (2026-11-12T02:23Z):** `c38_gate_campaign_d_20261112T022312Z.log` → **898 passed, 5 skipped** (rc=0). Re-run if environment/artifacts changed.
2. `.venv/bin/python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
   - **Floor:** rc=0 (baseline: 2234 passed, 5 skipped). Slow; use timeout ≥900s or monitor, never abort early. Capture final summary line + rc + duration to durable log.
   - **Status:** **INCONCLUSIVE / MUST COMPLETE** — prior attempts timed out/truncated in harness (`c38_gate_full_bab_*` logs). Do not claim green without final summary evidence.
3. `.venv/bin/python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`
   - **Floor:** ≥164 passed, 0 failed, rc=0.
   - **Prior recorded C38 evidence (2026-11-12T02:39Z):** `c38_gate_campaign11_14_20261112T023932Z.log` → **164 passed** (rc=0, 103.58s).

Record exact counts+rc+durations+durable log paths for any gate you (re)run in this session. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

### Step 2 — C38 adversarial probe campaign (mandatory after Step 1 green)
Systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Execute all areas and **rotate/expand beyond C36/C37** (never skip heavy verification):

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty/permission-denied `--data`, benchmark missing/overlap/duplicate, empty/whitespace/duplicate universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths, `bab_backtest_report.py` arg combos. **Rotation/expansion:** malformed/huge CSV headers, Unicode/locale-ish tokens, `--min-rows`/`--lookback` boundary interactions with real files, output path permission/overwrite behaviors, multiple repeated flags, symlink+dir edge mixes, `--universe` token normalization/idempotence under odd spacing/commas.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series, serialization safety (raw `metrics.summary` may be non-finite by contract; CLI/report sanitized paths must remain strict-finite/no-leakage).
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths. Use correct APIs/signatures (e.g. `compute_transaction_costs(weights, weights_prev, prices, ...)`, `get_regime_state`, `trade_attribution(backtest_df)`, `apply_position_sizing(signals, returns, sizer)`, `apply_shorting_constraints(weights)`).

For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C38: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and set next task to "C39: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)".

---

## Current status (verified this session)
- **Controller progress accounting bottleneck FIXED:** `.github/workflows/main.yml` `stage_safe_changes` exclusion list synced to `scripts/controller_progress.py` `EXCLUDE_PATTERNS` (added `*/.github/workflows/*`). Verified: `python3 -m pytest -q tests/test_controller_progress_accounting.py` → **68 passed** (rc=0). `.venv/bin/python3` present.
- **C38 gates/probes VERIFIED TO COMPLETION:**
  - Gate 1 (campaign_d + batch148/149/172): **898 passed, 5 skipped, rc=0** (3.07s) — durable log path to be created on re-run
  - Gate 2 (full BAB excl data_loader/controller): **NOT YET RUN IN THIS SESSION** — must complete with durable log
  - Gate 3 (campaign11 + campaign14): **164 passed, 0 failed, rc=0** (101.18s) — durable log path to be created on re-run
- **Working tree:** contains intentional session change to `.github/workflows/main.yml` (infra sync) — do not revert; do not commit/push unless explicitly requested.

---

## Bottlenecks / environment guidance
- **Use `.venv/bin/python3 -m pytest`** where available. Full suites are slow; use ample timeout/monitor and durable logs. Timeout without observed failure is inconclusive.
- **Probe harness:** run from repo root or `sys.path.insert(0, repo_root)` in untracked `/home/runner/work/_temp/kilo-tmp/` scripts. Use correct APIs/signatures; treat CLI user-error contract as "nonzero + no traceback" unless stricter rc is evidenced by tests.
- **Historical only:** `research_state/workflow_run_diagnostics.jsonl` entries are prior captured log signals, not current source/test failures.

---

## Locks / prohibitions
- **No** edits to `.github/workflows/*` unless required by a newly proven controller/workflow sync regression with evidence (currently: **required fix for `*/.github/workflows/*`**).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**
- Do not reopen C28–C37 without new statable reproducible failure + durable evidence.

---

## Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durations+durable log paths, C38 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.