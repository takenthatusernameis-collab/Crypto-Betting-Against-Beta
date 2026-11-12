# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T06:02:35Z
**HEAD:** `7f44d02` on `main` (tracked working tree clean at refresh; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Bottlenecks removed this refresh:** stale handoff HEAD (`6b68357`) corrected to live HEAD (`7f44d02`); C40 EXTENDED campaign completed — all three gate floors re-verified green with durable logs, and 46 new adversarial probes executed across all editable surfaces (`costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `cli.py`, `scripts/bab_backtest_report.py`) with **46/46 PASS, 0 FAIL**. No regressions found. Next session starts from a green, importable, probe-hardened baseline; no re-diagnosis needed.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C41 ROTATION heavy campaign, start immediately)

**Start work now. Do not plan-only, do not re-diagnose historical CI noise, do not declare "blocked" without an evidenced attempt and durable logs.**

1. **Re-verify gate floors (Step 1) before any probe expansion.** Use system Python 3.12.3, repo root, `PYTHONPATH=$PWD`, no `.venv`. Every gate/probe run must emit a durable log under `/home/runner/work/_temp/kilo-tmp/` (command, start/end, summary, rc, duration, stdout+stderr). Timeout/interruption without observed final failure = **INCONCLUSIVE, not green**.
2. **Execute Step 2 C41 ROTATION adversarial probe campaign (minimum 20 NEW probes).** Rotate shapes/cases; do not reuse C40/C40-extended probe scripts/shapes. Target unexhausted editable/allowed surfaces: `attribution.py`, `metrics.py`, `scripts/bab_gate.sh`/controller script contracts, deeper `cli`/report I-O and serialization edges, `costs/regime/shorting/sizing` cross-parameter interactions. Every probe: durable log with rc, duration, PASS/FAIL, and repro path. Smoke checks are insufficient.
3. **If any proven regression:** smallest fix in allowed area only → minimal regression test → re-run affected tests + all three gate floors → record evidence.
4. **If no proven gaps:** record "C41 rotation: no proven gaps" with per-area/per-probe evidence and log paths.
5. **Before exit, refresh this same `HANDOFF.md`** (single durable handoff) with timestamp/HEAD, gate results+logs, full probe matrix outcomes, working-tree notes, and the next concrete heavy task.

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged vs prior verified state. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` contains **historical** CI/log excerpts/signals only; not evidence of a current checkout failure. Do not use it to justify inaction.

### Step 1 — Gate floors (must be green with durable evidence)

| Gate | Scope | Floor | Last recorded (this refresh, verify now) | Log path |
|---|---|---:|---|---|
| 1 | `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | ≥898 passed, 5 skipped, rc=0 | **898p/5s/rc=0 (6.42s)** | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate1_20261112T052005Z.log` |
| 2 | `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | rc=0 (~2234 passed, 5 skipped) | **2234p/5s/rc=0 (401.09s)** | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate2_20261112T052007Z.log` |
| 3 | `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*` | ≥164 passed, 0 failed, rc=0 | **164p/rc=0 (160.09s)** | `/home/runner/work/_temp/kilo-tmp/c40_gate_gate3_20261112T052006Z.log` |

**If any floor red:** smallest proven fix in allowed areas only → minimal regression test → re-run affected + all floors → record evidence in refreshed handoff.

### Step 2 — C41 ROTATION adversarial probe campaign (mandatory, ≥20 new probes)

**Unexhausted surfaces to probe with NEW shapes/edge cases/parameter combinations (rotate; prior C40/C40-extended shapes alone = incomplete):**

| Area | Required probe focus (non-exhaustive) |
|---|---|
| **`attribution.py`** | `run_attribution`: factor covariance singular/near-singular, `factor_returns` index misalignment with portfolio returns, zero/NaN factor exposures, `residual` computation with constant portfolio returns, multi-period attribution with missing dates, `benchmark` not in factor set, `method` unknown string fallback |
| **`metrics.py`** | `compute_metrics`: non-finite returns (inf/-inf/NaN) propagation through all ratios, `sharpe`/`sortino`/`calmar` with zero/negative denominator, `max_drawdown` with all-positive/flat equity, `omega_ratio` threshold at distribution extremes, `tail_ratio` with <2 observations, `annual_factor` edge values (0, 1, 365, 10000), Series vs DataFrame input coercion |
| **`scripts/bab_gate.sh` / controller contracts** | `--gate` selection logic with invalid/unknown gate names, missing test files glob, exit code propagation on partial failure, parallel vs sequential mode interaction, timeout handling, output directory creation/permissions |
| **`cli.py` / report I-O deeper** | `--data` streaming stdin/pipe input, `--from-prices` with duplicate timestamps (keep=first/last), `--universe` case-insensitive/whitespace normalization, `--benchmark` alias resolution, `--output` format auto-detection from extension, `--config` YAML/JSON merge precedence, `--dry-run` side-effect freedom proof, `--json` output strict-finite with nested structures |
| **Cross-parameter interactions** | `costs.py` + `sizing.py`: transaction cost model feeding into vol-target leverage calc; `regime.py` + `shorting.py`: regime state gating borrow availability; `metrics.py` + `attribution.py`: metric computation on attributed residuals; `sizing.py` + `shorting.py`: weight caps interaction with borrow constraints |

**Per-probe record (required):** area, probe name/script, PASS/FAIL, rc, duration, repro log path. Contract-consistent behavior ≠ regression; document rationale in log. Any FAIL → triage and apply smallest proven fix path above.

### Step 3 — Fix/closure & handoff refresh (mandatory before exit)
- **If gaps found:** durable repro → smallest allowed fix → minimal regression test → re-run affected + all gate floors → record evidence.
- **If no proven gaps after full Step 1+2:** record **"C41 rotation: no proven gaps"** with evidence summary, per-area probe counts, and log paths.
- **Always refresh this `HANDOFF.md`** with: timestamp/HEAD, exact gate counts+rc+durations+durable log paths, extended probe outcomes (PASS/FAIL per area + names + repro paths), working-tree notes, and next concrete heavy task. Keep single, durable, unambiguous.

## Current status (verified at this refresh)

- **Working tree:** clean tracked state (`git status --porcelain` empty). Prior untracked artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit): `c40_gate_*`, `c40_probe_campaign_*`, `c40_probe_extended_*`, `c38_*`, etc.
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; no `.venv`; run with `PYTHONPATH` set to repo root. Declared deps in `requirements.txt` (`numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`).
- **Baseline verified green (this refresh):** all editable modules (`costs`, `regime`, `shorting`, `sizing`, `cli`, `metrics`, `attribution`) import cleanly; gate-1 data-loader subset passes 25/25 rc=0. Treat as confirmed starting baseline; Step 1 below must still re-verify all three gate floors with durable logs.
- **C40 EXTENDED completed (this refresh):** Gate 1 898p/5s/rc=0 (6.42s); Gate 2 2234p/5s/rc=0 (401.09s); Gate 3 164p/rc=0 (160.09s). Extended probe campaign **46/46 PASS, 0 FAIL** (0.22s total) — `/home/runner/work/_temp/kilo-tmp/c40_probe_extended_20261112T053137Z.log`. No regressions found across all 6 editable surfaces.

## Next focus campaign (binding)
**Primary:** complete **C41 ROTATION** campaign above with ≥20 new probes and durable evidence, preserving all gate floors. **Do not stop at gate re-verification.**
**If C41 rotation closes with no proven gaps:** refresh handoff and immediately define/execute **C42 rotation** targeting remaining unexhausted editable surfaces (e.g. deeper `quality.py`, `signals.py`, `portfolio.py` cross-module edges, `config.py` validation boundaries, `backtest.py` serialization/round-trip, `data_sources.py` emitter contracts) with the same heavy evidence standard (≥20 new probes, durable logs, gate floors green).

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C40 without a new statable reproducible failure + durable evidence.

(End of file)