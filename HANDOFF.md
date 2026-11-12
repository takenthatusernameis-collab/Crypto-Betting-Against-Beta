# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T03:33:41Z
**HEAD:** `617cbf8` on `main`
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C38 Gate 2 closure + probe continuation)

**C38 is active. Execute heavy, evidence-producing work immediately. "No proven gaps" is valid only after full Step 1 (all gates with durable evidence) + Step 2 execution.**

### Step 0 — Controller/workflow sync (not a blocker now)
- `.github/workflows/main.yml` `stage_safe_changes` includes `*/.github/workflows/*` and matches controller `EXCLUDE_PATTERNS` intent.
- Prior verified evidence (C38): `PYTHONPATH=. python3 -m pytest -q tests/test_controller_progress_accounting.py` → **68 passed, rc=0** (2026-11-12T03:26Z, per prior log). **Do not reopen** unless you reproduce a new sync failure with durable evidence.

### Step 1 — Gate floors (mandatory, durable logs required)
Run from repo root. Use: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest ...` (system python 3.12.3; **no `.venv/bin/python3` in this env**). Timeout/interruption without observed final failure is **INCONCLUSIVE, not green**. Every gate run must write a durable log under `/home/runner/work/_temp/kilo-tmp/` (tee/capture stdout+stderr, include start/end, final summary line, rc, duration).

1. **Data loader campaign_d + batch148/149/172** — **Floor:** ≥898 passed, 5 skipped, rc=0.
   - **Last verified (PASS):** 898 passed, 5 skipped, 53 warnings, rc=0 (4.44s). Log: `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign_d_20261112T032635Z.log`.
2. **Full BAB suite excl data_loader + controller** — **Floor:** rc=0 (baseline ~2234 passed, 5 skipped). **CURRENT BOTTLENECK / MUST COMPLETE.**
   - **Status:** INCONCLUSIVE in C38 (no durable log with final summary+rc; prior attempt progressed then exited without recorded completion).
   - **Required now:** run to completion with ample timeout/monitor, never abort early, capture final counts/rc/duration in durable log (e.g. `/home/runner/work/_temp/kilo-tmp/c38_gate_full_bab_<UTC_TS>.log`). Treat any missing final summary as inconclusive and rerun.
   - Suggested command pattern: `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
3. **CLI campaign11 + campaign14** — **Floor:** ≥164 passed, 0 failed, rc=0.
   - **Last verified (PASS):** 164 passed, rc=0 (110.65s). Log: `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign11_14_20261112T032635Z.log`.

**If any floor is red:** smallest proven fix in allowed areas only, add minimal regression, re-run affected gate(s) and then all floors as required, record evidence.

### Step 2 — C38/C39 adversarial probe campaign (mandatory after Step 1 green)
Exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Rotate/expand beyond prior probes.

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output`, invalid/NaN/Inf args, missing/dir/empty `--data`, malformed/huge headers, duplicate/whitespace/unicode universe tokens, min-rows/lookback/beta-window boundaries, output overwrite/dir targets, `bab_backtest_report.py` arg combos. **User-path contract:** nonzero + no traceback unless stricter rc evidenced by tests.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series (raw `metrics.summary` may be non-finite by contract; sanitized/report paths must remain strict-finite/no-leakage where applicable). Validate `report_to_json`/tear-sheet/report CLI behavior.
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, invariants, monotonicity/interaction checks. Use correct APIs/signatures (e.g. `compute_transaction_costs(...)`, `get_regime_state(returns: DataFrame, ...)`, `trade_attribution(backtest_df)`, `apply_position_sizing(signals, returns, sizer)`, `EqualWeightSizer`, `apply_shorting_constraints(weights)`).

**Prior probe evidence (C38, no proven BAB regressions found):**
- `/home/runner/work/_temp/kilo-tmp/c38_probe_20261112T032930Z.log` (`c38_probe.py`, rc=1): 25/27 PASS; 2 FAILs were harness API misuse (fixed in probe2).
- `/home/runner/work/_temp/kilo-tmp/c38_probe2_20261112T032959Z.log` (`c38_probe2.py`, rc=0): 9/9 PASS (regime df/basic+small+nan/inf, `EqualWeightSizer` sizing basic/zero, CLI min-rows/beta-window large/unicode token, report `--synthetic`).
- Covered: CLI invalid/boundary args, missing/dir/empty/malformed data, from-prices dry/run+JSON output+overwrite, odd universe tokens, `bab_backtest_report` help/no-args/`--synthetic`, metrics degenerate/inf/huge/empty compute paths (no unexpected exceptions), costs/attribution/shorting/regime/sizing smoke. **Still expand:** repeated-flag combos, symlink+permission edge mixes, broader report/script arg matrices, monotonicity & cross-module invariants under extremes.

Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure & handoff refresh (before exit)
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C38/C39: no proven gaps" with evidence summary/log paths.
- **Always refresh this same `HANDOFF.md`** with: timestamp/HEAD, exact gate counts+rc+durations+durable log paths, probe matrix outcomes (PASS/FAIL per area + repro paths), working-tree notes, and the next concrete heavy task. Keep single, durable, unambiguous.

## Current status (2026-11-12T03:33:41Z)
- **Working tree:** clean tracked state observed at refresh (no intentional source changes pending). Untracked probe/gate artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit).
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; no `.venv`; set `PYTHONPATH` to repo root for tests/scripts.
- **Gates:** Gate 1 PASS (898/5/rc0), Gate 3 PASS (164/rc0) with durable logs above; **Gate 2 INCONCLUSIVE — primary blocker to clear.**
- **`research_state/workflow_run_diagnostics.jsonl`:** historical captured CI/log signals, not evidence of current checkout failures.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C37 without a new statable reproducible failure + durable evidence.
