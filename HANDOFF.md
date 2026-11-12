# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T06:28:17Z
**HEAD:** `3fb8234` on `main` (tracked working tree clean at refresh; `git status --porcelain` empty)
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

**Bottleneck removal (this refresh):** revalidated repo state (HEAD `3fb8234`, tree clean), confirmed C41 gate floors are GREEN with durable logs, removed stale HEAD/timestamp ambiguity, and kept one binding kickoff for the next session. Prior C40/C40-extended evidence remains historical baseline only. No workflow edits or code changes made.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (start immediately)

**Start work now. Do not plan-only, do not re-diagnose historical CI noise, do not declare "blocked" without an evidenced attempt and durable logs.**

The repo is **Crypto-Betting-Against-Beta**: controller infrastructure plus a market-neutral Betting Against Beta (BAB) crypto strategy (long low-beta / short high-beta vs benchmark BTC). The only binding product is BAB correctness/robustness across `attribution.py`, `metrics.py`, `cli.py`, `scripts/bab_gate.sh`/controller contracts, and `costs`/`regime`/`shorting`/`sizing` cross-surface interactions. All work must flow through the gate floors + durable evidence standard below.

1. **Gate floors already GREEN (C41 @ `3fb8234`) — do not re-run unless a fix lands.**
   - Gate 1 `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py`: **898 passed, 5 skipped, rc=0 (4.92s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate1_20261112T061648Z.log`
   - Gate 2 `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`: **2234 passed, 5 skipped, rc=0 (205.51s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate2_20261112T062047Z.log`
   - Gate 3 `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*`: **164 passed, rc=0 (77.97s)** → `/home/runner/work/_temp/kilo-tmp/c41_gate_gate3_20261112T062421Z.log`
   - Environment: system Python 3.12.3 (`/usr/bin/python3`), repo root, `PYTHONPATH=$PWD`, no `.venv`. Declared deps in `requirements.txt` (`numpy`, `pandas`, `scipy`, `pytest`, `hypothesis`, `coverage`).

2. **Execute Step 2 C41 ROTATION adversarial probe campaign (minimum 20 NEW probes).** Rotate shapes/cases; do not reuse C40/C40-extended probe scripts/shapes. Target unexhausted editable/allowed surfaces:
   - `attribution.py`: `trade_attribution` / `attribution_totals` with singular/near-singular inputs, index misalignment, zero/NaN exposures, constant returns, missing dates, unknown method fallback.
   - `metrics.py`: `compute_metrics`/`sharpe_ratio`/`sortino_ratio`/`calmar`/`max_drawdown`/`omega_ratio`/`tail_ratio` with non-finite returns (inf/-inf/NaN), zero/negative denominators, all-positive/flat equity, threshold at distribution extremes, <2 observations, `annual_factor` edge values (0, 1, 365, 10000), Series vs DataFrame coercion.
   - `scripts/bab_gate.sh` / controller contracts: invalid/unknown gate selection, missing test globs, exit-code propagation on partial failure, parallel vs sequential interaction, timeout handling, output dir creation/permissions.
   - `cli.py` / report I-O deeper: stdin/pipe `--data`, `--from-prices` duplicate timestamps (keep=first/last), `--universe` case/whitespace normalization, `--benchmark` alias resolution, `--output` format auto-detection, `--config` YAML/JSON merge precedence, `--dry-run` side-effect freedom, `--json` strict-finite nested output.
   - Cross-parameter interactions: `costs`+`sizing` (cost model → vol-target leverage), `regime`+`shorting` (regime gating borrow availability), `metrics`+`attribution` (metrics on attributed residuals), `sizing`+`shorting` (weight caps vs borrow constraints).
   - Every probe: durable log under `/home/runner/work/_temp/kilo-tmp/` with rc, duration, PASS/FAIL, repro path. Smoke checks are insufficient.

3. **If any proven regression:** smallest fix in allowed area only → minimal regression test → re-run affected tests + all three gate floors → record evidence.

4. **If no proven gaps:** record **"C41 rotation: no proven gaps"** with per-area/per-probe evidence and log paths.

5. **Before exit, refresh this same `HANDOFF.md`** (single durable handoff) with timestamp/HEAD, gate results+logs, full probe matrix outcomes, working-tree notes, and the next concrete heavy task.

### Step 0 — Controller/workflow sync
- `.github/workflows/*` unchanged. **Do not edit** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).
- `research_state/workflow_run_diagnostics.jsonl` contains **historical** CI/log excerpts/signals only; not evidence of a current checkout failure. Do not use it to justify inaction.

### Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with durable evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` for probes/logs).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C40 without a new statable reproducible failure + durable evidence.

## Next focus campaign (binding)

**Primary:** complete **C41 ROTATION** (≥20 new probes, durable evidence, all gate floors green) — this is the immediate binding task and must not stop at gate re-verification.

**If C41 rotation closes with no proven gaps:** refresh handoff and immediately define/execute **C42 rotation** targeting remaining unexhausted editable surfaces (deeper `quality.py`, `signals.py`, `portfolio.py` cross-module edges, `config.py` validation boundaries, `backtest.py` serialization/round-trip, `data_sources.py` emitter contracts) with the same heavy evidence standard (≥20 new probes, durable logs, gate floors green).

**Current status (verified at this refresh):**
- Working tree: clean tracked state. Untracked artifacts may exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit).
- Quick sanity: key editable modules import cleanly (`cli, metrics, attribution, costs, regime, shorting, sizing`) with `PYTHONPATH=$PWD` → `imports_ok`.
- C41 gates GREEN (see above). C41 probe campaign **NOT yet executed** — ≥20 new probes required before any handoff refresh/closure.
