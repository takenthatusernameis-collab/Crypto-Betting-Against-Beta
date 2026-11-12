# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T05:32:54Z
**HEAD:** `6b68357` on `main` (tracked working tree clean at refresh; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Bottlenecks removed this refresh:** stale handoff HEAD (`551755a`) corrected to live HEAD (`6b68357`); baseline verified green — all `strategies/betting_against_beta/{costs,regime,shorting,sizing,cli,metrics,attribution}.py` import cleanly under system Python 3.12.3 with `PYTHONPATH=$PWD` (no `.venv`), and gate-1 data-loader subset (`batch148/149/172` + `campaign_d_core_final`) passes 25/25 rc=0. Next session starts from a green, importable baseline; no re-diagnosis of historical CI noise needed.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C40 EXTENDED heavy campaign, start immediately)

**Start work now. Do not plan-only, do not re-diagnose historical CI noise, do not declare "blocked" without an evidenced attempt and durable logs.**

1. **Re-verify gate floors (Step 1) before any probe expansion.** Use system Python 3.12.3, repo root, `PYTHONPATH=$PWD`, no `.venv`. Every gate/probe run must emit a durable log under `/home/runner/work/_temp/kilo-tmp/` (command, start/end, summary, rc, duration, stdout+stderr). Timeout/interruption without observed final failure = **INCONCLUSIVE, not green**.
2. **Execute Step 2 C40 EXTENDED adversarial probe campaign (minimum 20 NEW probes).** Rotate shapes/cases; do not reuse prior probe scripts/shapes. Target only editable/allowed surfaces: `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `cli.py`, `scripts/bab_backtest_report.py` (report CLI). Every probe: durable log with rc, duration, PASS/FAIL, and repro path. Smoke checks are insufficient.
3. **If any proven regression:** smallest fix in allowed area only → minimal regression test → re-run affected tests + all three gate floors → record evidence.
4. **If no proven gaps:** record "C40 extended: no proven gaps" with per-area/per-probe evidence and log paths.
5. **Before exit, refresh this same `HANDOFF.md`** (single durable handoff) with timestamp/HEAD, gate results+logs, full probe matrix outcomes, working-tree notes, and the next concrete heavy task.

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged vs prior verified state. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` contains **historical** CI/log excerpts/signals only; not evidence of a current checkout failure. Do not use it to justify inaction.

### Step 1 — Gate floors (must be green with durable evidence)

| Gate | Scope | Floor | Last recorded (prior session, verify now) | Prior log |
|---|---|---:|---|---|
| 1 | `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | ≥898 passed, 5 skipped, rc=0 | **898p/5s/rc=0 (4.55s)** | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate1_20261112T040157Z.log` |
| 2 | `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | rc=0 (~2234 passed, 5 skipped) | 2234p/5s/rc=0 (392.36s) | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate2_20261112T040446Z.log` |
| 3 | `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*` | ≥164 passed, 0 failed, rc=0 | 164p/rc=0 (150.03s) | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate3_20261112T040202Z.log` |

**If any floor red:** smallest proven fix in allowed areas only → minimal regression test → re-run affected + all floors → record evidence in refreshed handoff.

### Step 2 — C40 EXTENDED adversarial probe campaign (mandatory, ≥20 new probes)

**Unexhausted surfaces to probe with NEW shapes/edge cases/parameter combinations (rotate; prior shapes alone = incomplete):**

| Area | Required probe focus (non-exhaustive) |
|---|---|
| **`costs.py`** | `compute_transaction_costs`: market-impact participation cap boundary (`adv_usd`→0/NaN), borrow pro-rata with partial fills, multi-period ADV DataFrame alignment (index/column mismatch), extreme/unknown `model` strings, `weights_prev` NaN/Inf, prices with zero/negative values, `adv_usd` as Series vs DataFrame vs scalar |
| **`regime.py`** | `get_regime_state`: hysteresis band transitions (cross up/down at boundary), z-window trend with NaN leading rows, percentile quantile edges (0.0,1.0,outside), `window` < 2 / > len(returns), constant benchmark returns, multi-column regime scaling |
| **`shorting.py`** | `apply_shorting_constraints`: total short exposure cap scaling with leverage > 1, multi-asset borrow dict with missing keys, `borrow_cost_bps` as DataFrame vs scalar, unborrowable assets with `strict=False` (weight→0), `max_short_weight` per-asset dict, interaction with long/short sum constraints |
| **`sizing.py`** | `EqualWeightSizer`, `VolTargetSizer`, `KellySizer`, `RiskParitySizer`: lookback < 2 boundary, `target_vol` infeasible (zero/NaN vol), `max_leverage` clamp at boundary, `min_weight`/`max_weight` per-asset dicts, all-NaN/Inf signal rows, `VolTargetSizer` with misaligned returns index |
| **`cli.py`** | `--data`: huge-header CSV, duplicate columns, symlink valid/invalid targets, empty file, malformed CSV (unterminated quotes), output overwrite behavior, `--from-prices` misaligned timestamps, `--universe` duplicate/whitespace/unicode tokens, `--benchmark` not in data columns |
| **Report CLI** (`scripts/bab_backtest_report.py`) | `--data-source` malformed JSON, `--returns-csv` non-finite metrics, `--json` output must remain strict-finite, missing required columns, empty data source, `--benchmark` not found |

**Per-probe record (required):** area, probe name/script, PASS/FAIL, rc, duration, repro log path. Contract-consistent behavior ≠ regression; document rationale in log. Any FAIL → triage and apply smallest proven fix path above.

### Step 3 — Fix/closure & handoff refresh (mandatory before exit)
- **If gaps found:** durable repro → smallest allowed fix → minimal regression test → re-run affected + all gate floors → record evidence.
- **If no proven gaps after full Step 1+2:** record **"C40 extended: no proven gaps"** with evidence summary, per-area probe counts, and log paths.
- **Always refresh this `HANDOFF.md`** with: timestamp/HEAD, exact gate counts+rc+durations+durable log paths, extended probe outcomes (PASS/FAIL per area + names + repro paths), working-tree notes, and next concrete heavy task. Keep single, durable, unambiguous.

## Current status (verified at this refresh)

- **Working tree:** clean tracked state (`git status --porcelain` empty). Prior untracked artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit): `c40_gate_*`, `c40_probe_campaign_*`, `c38_*`, etc.
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; no `.venv`; run with `PYTHONPATH` set to repo root. Declared deps in `requirements.txt` (`numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`).
- **Baseline verified green (this refresh):** all editable modules (`costs`, `regime`, `shorting`, `sizing`, `cli`, `metrics`, `attribution`) import cleanly; gate-1 data-loader subset passes 25/25 rc=0. Treat as confirmed starting baseline; Step 1 below must still re-verify all three gate floors with durable logs.
- **Prior recorded (C40 base):** Gate 1 898p/5s/rc=0; Gate 2 2234p/5s/rc=0; Gate 3 164p/rc=0. Base probe campaign 58/58 PASS (`/home/runner/work/_temp/kilo-tmp/c40_probe_campaign_20261112T041519Z.log`). Treat as last-known baseline; Step 1 must re-verify.

## Next focus campaign (binding)
**Primary:** complete **C40 EXTENDED** campaign above with ≥20 new probes and durable evidence, preserving all gate floors. **Do not stop at gate re-verification.**
**If C40 extended closes with no proven gaps:** refresh handoff and immediately define/execute **C41 rotation** targeting remaining unexhausted editable surfaces (e.g. `attribution.py`, `metrics.py`, `scripts/bab_gate.sh`/controller script contracts, deeper `cli`/report I-O and serialization edges, `costs/regime/shorting/sizing` cross-parameter interactions) with the same heavy evidence standard (≥20 new probes, durable logs, gate floors green).

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C39/C40-base without a new statable reproducible failure + durable evidence.

(End of file)