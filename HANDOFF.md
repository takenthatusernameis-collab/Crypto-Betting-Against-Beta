# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T05:00:57Z
**HEAD:** `b181823` on `main` (working tree clean; diff vs `5c53e60` touched only handoff files, no source change)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C40 extended heavy campaign)

**C40 base campaign COMPLETE. Gates 1/2/3 green. 58/58 probes PASS. Zero proven gaps. Do not declare victory. Execute the EXTENDED adversarial probe campaign immediately. Heavy, evidence-producing work only. No smoke checks. No deferral. Every probe must produce a durable log under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, and repro path. Rotate shapes — do not reuse `c40_probe_campaign.py`.**

### Step 0 — Controller/workflow sync (unchanged)
- `.github/workflows/*` unchanged vs prior verified state. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).

### Step 1 — Gate floors (re-verify before any probe expansion)
Run from repo root with system Python 3.12.3 (`/usr/bin/python3`); **no `.venv`**. `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest ...`
Every gate run writes a durable log under `/home/runner/work/_temp/kilo-tmp/` (stdout+stderr, start/end, summary, rc, duration). Timeout/interruption without observed final failure = **INCONCLUSIVE, not green**.

| Gate | Scope | Floor | Last verified | Log |
|---|---|---:|---|---|
| 1 | `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | ≥898 passed, 5 skipped, rc=0 | **PASS** 898p/5s/rc=0 (4.86s) | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate1_20261112T040157Z.log` |
| 2 | `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | rc=0 (~2234 passed, 5 skipped) | **PASS** 2234p/5s/rc=0 (392.36s) | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate2_20261112T040446Z.log` |
| 3 | `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*` | ≥164 passed, 0 failed, rc=0 | **PASS** 164p/rc=0 (150.03s) | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate3_20261112T040202Z.log` |

**If any floor red:** smallest proven fix in allowed areas only → minimal regression test → re-run affected + all floors → record evidence.

### Step 2 — C40 EXTENDED adversarial probe campaign (mandatory, binding)
**Target: editable/allowed surfaces NOT YET EXHAUSTED by the base 58-probe matrix.** Each area below must be probed with NEW shapes, NEW edge cases, NEW parameter combinations. Reusing only prior shapes = incomplete. Every probe script untracked under `/home/runner/work/_temp/kilo-tmp/`. Every probe produces durable log (rc, duration, PASS/FAIL + repro). **Minimum 20 new probes across the matrix below.**

**Required extended probe matrix (minimum):**

| Area | Specific unexhausted surfaces to probe (non-exhaustive, must rotate) |
|---|---|
| **costs.py** | `compute_transaction_costs`: market-impact participation cap boundary (adv_usd→0), borrow pro-rata with partial fills, multi-period adv DataFrame alignment (index mismatch, column mismatch), extreme `model` strings, `weights_prev` NaN/Inf, prices with zero/negative values, `adv_usd` as Series vs DataFrame vs scalar |
| **regime.py** | `get_regime_state`: hysteresis band transitions (cross up/down at boundary), z-window trend with NaN leading rows, percentile quantile edges (0.0, 1.0, outside), `window` < 2, `window` > len(returns), benchmark with constant returns, multi-column regime scaling |
| **shorting.py** | `apply_shorting_constraints`: total short exposure cap scaling with leverage > 1, multi-asset borrow dict with missing keys, `borrow_cost_bps` as DataFrame vs scalar, unborrowable assets with `strict=False` (weight=0), `max_short_weight` per-asset dict, interaction with `long_weight` sum constraint |
| **sizing.py** | `EqualWeightSizer`, `VolTargetSizer`, `KellySizer`, `RiskParitySizer`: lookback < 2 boundary, `target_vol` infeasible (zero vol, NaN vol), `max_leverage` clamp at boundary, `min_weight`/`max_weight` per-asset dicts, signals with all-NaN rows, signals with Inf, `VolTargetSizer` with `returns` misaligned index |
| **cli.py** | `--data`: huge-header CSV (>10k cols), duplicate columns, symlink-valid/invalid targets, empty file, malformed CSV (unterminated quotes), output to existing file overwrite race (concurrent write), `--from-prices` with misaligned timestamps, `--universe` with duplicate tokens, unicode/whitespace edge cases, `--benchmark` not in data columns |
| **report CLI** (`scripts/bab_backtest_report.py`) | `--data-source` malformed JSON, `--returns-csv` with non-finite metrics, `--json` output with internal non-finite values (must remain strict-finite in JSON), missing required columns, empty data source, `--benchmark` not found |

**Per-area outcome recording (required):** For EACH area above record: area, probe name, PASS/FAIL, repro log path, duration, rc. Any FAIL → triage: proven regression → smallest fix in allowed area + minimal regression test + re-run affected + all gates → refresh HANDOFF. Contract-consistent/not-a-regression → document rationale in log.

### Step 3 — Fix/closure & handoff refresh (before exit)
- **If gaps found:** durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors → record evidence.
- **If no proven gaps after full Step 1+2:** record **"C40 extended: no proven gaps"** with evidence summary, log paths, covered matrix, probe counts per area.
- **Always refresh this same `HANDOFF.md`** with: timestamp/HEAD, exact gate counts+rc+durations+durable log paths, extended probe matrix outcomes (PASS/FAIL per area + probe names + repro paths), working-tree notes, and the next concrete heavy task. Keep single, durable, unambiguous.

## Current status
- **Working tree:** clean tracked state at refresh (no intentional source changes). Untracked probe/gate artifacts under `/home/runner/work/_temp/kilo-tmp/` (do not commit): `c40_gate_gate1_*.log`, `c40_gate_gate2_*.log`, `c40_gate_gate3_*.log`, `c40_probe_campaign_20261112T041519Z.log` plus prior `c38_*` logs/scripts.
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; no `.venv`; `PYTHONPATH` to repo root; all declared requirements (`requirements.txt`) installed (`numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`).
- **`research_state/workflow_run_diagnostics.jsonl`:** historical CI/log signals, not evidence of current checkout failures.

## C40 conclusion / next focus campaign (binding for the next session)
**C40 base: no proven gaps.** Gates 1/2/3 green with durable evidence (898p/5s/rc=0; 2234p/5s/rc=0; 164p/rc=0). Step 2 base probe campaign 58/58 PASS, rc=0, durable log at `/home/runner/work/_temp/kilo-tmp/c40_probe_campaign_20261112T041519Z.log`. No source changes; working tree clean at `b181823`.

**Next concrete heavy task (binding, non-deferrable):** Execute the **C40 EXTENDED adversarial probe campaign** defined in Step 2 above. Minimum 20 new probes across the six target areas (`costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `cli.py`, report CLI) with NEW shapes, NEW edge cases, durable logs. Re-run all three gate floors before and after. Any proven regression → smallest allowed fix + minimal regression + re-run all gates → refresh HANDOFF. If zero proven gaps after extended campaign → record "C40 extended: no proven gaps" and define the next rotation. **Future agents must do this heavy work; smoke checks are explicitly insufficient.**

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C39 without a new statable reproducible failure + durable evidence.

(End of file - total 66 lines)