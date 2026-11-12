# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T03:32:19Z
**HEAD:** `d4d88d6` on `main`
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C38 continuation)

**C38 remains active. Execute immediately (heavy, evidence-producing work). "No proven gaps" is allowed only after full Step 1 + Step 2 execution with durable evidence — never a reason to skip.**

### Step 0 — Controller sync blocker
- **FIXED (this session, verified):** `.github/workflows/main.yml` `stage_safe_changes` case synced with `scripts/controller_progress.py` `EXCLUDE_PATTERNS` by adding `*/.github/workflows/*`.
- **Evidence:** `PYTHONPATH=. python3 -m pytest -q tests/test_controller_progress_accounting.py` → **68 passed, rc=0** (2026-11-12T03:26Z). Do not re-open unless new reproducible sync evidence.

### Step 1 — Gate floors (mandatory, durable logs required)
Run from repo root with `PYTHONPATH=. python3 -m pytest ...` (system python; `.venv/bin/python3` not present in this env). Timeout/interruption without observed failure is **inconclusive, not green**.

1. Data loader campaign_d + batch148/149/172
   - **Floor:** ≥898 passed, 5 skipped, rc=0.
   - **This session (PASS):** **898 passed, 5 skipped, 53 warnings, rc=0** (4.44s). Log: `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign_d_20261112T032635Z.log` (TS=20261112T032635Z).
2. Full BAB suite excl data_loader + controller
   - **Floor:** rc=0 (baseline ~2234 passed, 5 skipped). Slow; use ample timeout/monitor, never abort early; capture final summary+rc+duration.
   - **This session: INCONCLUSIVE (must complete).** Attempted background run started 2026-11-12T03:26:35Z (`C38 Gate 2 full BAB suite ... with PYTHONPATH`, observed progressing to ~35%+ in logs snapshot) but process exited and no durable `c38_gate_full_bab_20261112T032635Z.log` with final summary/rc was located; prior `c38_gate_full_bab_*` logs also inconclusive/truncated. **Next agent must run to completion with durable log and record final counts/rc/duration.**
3. CLI campaign11 + campaign14
   - **Floor:** ≥164 passed, 0 failed, rc=0.
   - **This session (PASS):** **164 passed, rc=0** (110.65s / 0:01:50). Log: `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign11_14_20261112T032635Z.log` (TS=20261112T032635Z).

A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

### Step 2 — C38 adversarial probe campaign (mandatory after Step 1 green)
Exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Rotate/expand beyond C36/C37.

- **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output`, invalid/NaN args, missing/dir/empty `--data`, malformed/huge headers, duplicate/whitespace/unicode universe tokens, min-rows/lookback boundaries, output overwrite, `bab_backtest_report.py` arg combos. No-traceback on user paths; rc contracts as evidenced.
- **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series (raw `metrics.summary` may be non-finite by contract; sanitized/report paths must remain strict-finite/no-leakage where applicable).
- **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, invariants, correct APIs/signatures (`compute_transaction_costs(weights, weights_prev, prices, ...)`, `get_regime_state(returns: DataFrame, ...)`, `trade_attribution(backtest_df)`, `apply_position_sizing(signals, returns, sizer)`, `apply_shorting_constraints(weights)`).

**This session probes (durable):**
- `/home/runner/work/_temp/kilo-tmp/c38_probe_20261112T032930Z.log` (`c38_probe.py`, rc=1): **25/27 PASS**. 2 initial FAILs were probe-harness API misuse (fixed in probe2): `regime.get_regime_state` requires DataFrame returns; sizing exports `EqualWeightSizer` (not `EqualWeight`).
- `/home/runner/work/_temp/kilo-tmp/c38_probe2_20261112T032959Z.log` (`c38_probe2.py`, rc=0): **9/9 PASS** (regime df/basic+small windows+nan/inf, `EqualWeightSizer` sizing basic/zero, cli min-rows large/beta-window large/unicode universe token, report `--synthetic`).
- **Covered areas (no proven BAB regressions found):** CLI invalid/boundary args, missing/dir/empty/malformed data, from-prices dry/run+JSON output+overwrite, universe token normalization oddities, `bab_backtest_report` help/no-args/`--synthetic`, metrics degenerate/inf/huge/empty compute paths (no unexpected exceptions), costs zero/basic, attribution basic/nan-inf, shorting basic, regime/sizing correct-API smoke. **Remaining/expand in next session:** deeper repeated-flag combos, symlink+permission edge mixes, broader report/script arg matrices, regime/attribution/costs/shorting/sizing monotonicity & interaction invariants under extremes, and any C39 rotation gaps after Gate 2 is green.

Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

### Step 3 — Closure
- **If gaps found:** fix with minimal proven change + regression in allowed areas, re-run gates, record evidence.
- **If no proven gaps after full Step 1+2:** record "C38: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and set next task to "C39: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)".

## Current status (verified this session)
- **Working tree:** intentional infra sync in `.github/workflows/main.yml` (`*/.github/workflows/*` added to `stage_safe_changes`). Untracked probe scripts/logs under `/home/runner/work/_temp/kilo-tmp/` (not to be committed). Do not revert intentional changes; **no commit/push unless explicitly requested**.
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; **no `.venv/bin/python3`**; run tests with `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta` (or from repo root with `PYTHONPATH=.`). Running without PYTHONPATH from some contexts can yield collection/import issues.
- **Gates this session:** Gate 1 PASS (898/5/rc0, log above), Gate 3 PASS (164/rc0, log above), Gate 2 **INCONCLUSIVE** (see Step 1).
- **Probes:** corrected API probes PASS (9/9) with no proven BAB regressions; initial harness misuse documented.

## Bottlenecks / environment guidance
- Full non-data_loader suite is slow and prone to harness/timeout ambiguity; require final summary line + rc in durable log. Timeout without observed failure is inconclusive.
- Probe from repo root or set `sys.path`/`PYTHONPATH` to repo root in untracked `/home/runner/work/_temp/kilo-tmp/` scripts. Use correct APIs/signatures; CLI user-error contract: nonzero + no traceback unless stricter rc evidenced by tests.
- `research_state/workflow_run_diagnostics.jsonl` entries are historical captured signals, not current source/test failures.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except for newly proven controller/workflow sync regression with evidence (Step 0 fix already applied).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**
- Do not reopen C28–C37 without new statable reproducible failure + durable evidence.

## Handoff refresh requirement (before exit)
Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durations+durable log paths, C38 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
