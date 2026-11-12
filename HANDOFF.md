# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T14:36:43Z
**HEAD at refresh:** `85f16528cae98e660e10874b7520211d8ffc54af` (`chore(kilo): checkpoint agent session`, 2026-11-12T14:35:29Z, `main`)
**Working tree (tracked):** clean at refresh. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log/gate artifacts may exist and must not be committed.
**Env (verified):** Python 3.12.3, Linux, repo root `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`; run commands from repo root with `PYTHONPATH=.`; deps importable (`numpy,pandas,scipy,pytest,hypothesis,coverage`).

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts from other runs/heads; treat as historical, not evidence of current-checkout failure, and never as justification for inaction/"blocked".
- **Env/blockers:** deps importable, Python 3.12.3, tracked tree clean at HEAD `85f1652`. No proven current source blocker recorded.
- **C49 closed and recorded:** prior planning-only gap cleared; C49 probes executed (67/67 PASS), gates 3/3 GREEN, and 2 proven fixes landed (`metrics.py` guards + `tests/test_bab_metrics_c49_regressions.py`). C50 is the only active campaign focus.
- **Gate invocation:** run from repo root with `PYTHONPATH=.`; G1 uses explicit `tests/test_bab_data_loader_campaign_d*` file list + batch148/149/172; save timestamped durable logs under `/home/runner/work/_temp/kilo-tmp/c50_gates/`; always capture final summary + `rc`.

## Gate status (baseline at HEAD 85f1652; last recorded C49 run 2026-11-12T14:42:00Z @ f9d84f8)

| Gate | Status | Evidence / notes | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN (recorded)** | 898 passed, 5 skipped, 53 warnings, rc=0 | explicit `tests/test_bab_data_loader_campaign_d*` (32 files) + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `/home/runner/work/_temp/kilo-tmp/c49_gates/gate1_20261112T143031Z.log` |
| 2 | **GREEN (recorded)** | 2241 passed, 5 skipped, 41 warnings, rc=0 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c49_gates/gate2_20261112T143040Z.log` |
| 3 | **GREEN (recorded)** | 164 passed in 121.05s, rc=0 | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files) | `/home/runner/work/_temp/kilo-tmp/c49_gates/gate3_20261112T143040Z.log` |

**C49 CLOSED CLEAN (recorded).** C50 must re-run and durably log all 3 gates under `/home/runner/work/_temp/kilo-tmp/c50_gates/` before exit after any C50 changes.

## C49 (prior session, recorded) — result + proven fixes
- **Probes:** 67 NEW adversarial probes under `/home/runner/work/_temp/kilo-tmp/c49_probes/` (runner `c49_probe_runner.py`, per-probe logs `C49-001.log`..`C49-067.log`, summary `c49_probe_summary.{json,md}` timestamp `2026-11-12T14:30:15Z`). No C40–C48 reuse.
- **Surfaces covered:** `metrics.py`, `attribution.py`, `quality.py`, `data_sources.py`/`DataCache`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `cli.py` (arg/error/reporting robustness, `--output` path validation, `_coerce_finite_scalar`, `_validate_rebalance_freq`).
- **Proven gaps fixed (landed at HEAD 85f1652):**
  1. `metrics.py:sharpe_ratio` guarded non-finite `risk_free` → `np.nan` (no misleading `-inf`).
  2. `metrics.py:turnover_series` coerces non-numeric frames via `pd.to_numeric(..., errors="coerce")`.
- **Regression tests (kept):** `tests/test_bab_metrics_c49_regressions.py` (7 tests). Must not be removed or weakened.
- **Intentional tracked state:** `strategies/betting_against_beta/metrics.py` + `tests/test_bab_metrics_c49_regressions.py` are part of baseline; do not revert.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42:** CLOSED — 38/38. **C43:** 39/39. **C44:** 44/44. **C45:** 43/43. **C46:** 38/38, gates green.
- **C47:** CLOSED CLEAN — 38/38 PASS, gates 3/3 GREEN.
- **C48:** CLOSED CLEAN — 66/66 PASS, gates 3/3 GREEN.
- **C49:** **CLOSED CLEAN** — 67/67 PASS, gates 3/3 GREEN, 2 proven gaps fixed with 7 regression tests.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, execute now)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus (priority):** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only. **No planning-only turn; heavy execution mandatory.**
- **Preflight (verify first, record in this file on exit):** `git rev-parse HEAD`, `git status --short`, `python3 -c "import numpy,pandas,scipy,pytest,hypothesis,coverage; print('deps ok')"`. Run from repo root with `PYTHONPATH=.`
- **Immediate execution (in order):**
  1. **START C50 (mandatory, heavy) — C49 closed cleanly.** Create a NEW probe runner (no C40–C49 reuse) with **≥20 NEW** adversarial probes; execute and save per-probe logs + summary under `/home/runner/work/_temp/kilo-tmp/c50_probes/`.
  2. **C50 focus (new shapes only, build the heavy working):**
     - **`cli.py` reporting/serialization deep edges:** `_build_output_summary` / `_json_default` / `_json_safe` / `_extract_cumulative` with NaN/inf/mixed-dtype/`--output` to JSON; arg parsing where `argparse` `type=float` receives `inf`/`nan`/empty; `--output` parent-creation failure modes (permission-denied dir, symlink-outside-allowed-base); dry-run vs run divergence.
     - **`data_loader.py` adversarial edges (allowed loader edges):** datetime col + numeric col coercion, duplicate dates, all-NaN column, mixed tz-aware/naive index, Parquet/HDF5/Pickle round-trips on tiny frames, `min_rows` boundaries, `benchmark` present/absent/in-bench-missing.
     - **`quality.py` numeric-coercion + boundary paths not yet probed:** `detect_outliers` with `iqr==0` + `std>0` fallback; `detect_gaps` with duplicate timestamps and single-row; `data_quality_report` on non-numeric-only frames; `compute_quality` column set.
     - **`costs.py`/`regime.py`/`shorting.py`/`sizing.py`/`attribution.py` cross-interactions:** `apply_costs` with both `transaction_costs` and `slippage` kwargs + weight/model mismatch; `regime_scale_factors` vs `regime_scale_scalar` agreement on a shared cfg; `ShortingConstraints` borrow-rate dict with non-string keys; `apply_position_sizing` `KellySizer`/`VolatilityTargetSizer`/`RiskParitySizer` with NaN/inf signal frames; `trade_attribution`+`attribution_totals` round-trip on frames carrying `cost_drag`/`slippage_drag` only (no `returns`).
  3. **On any proven gap:** smallest allowed fix + minimal regression test in `tests/test_bab_*_c50_regressions.py` + affected tests + full gates; record matrix/results/state and next binding task here.
  4. **Before exit (mandatory):** run all 3 gates with timestamped logs under `/home/runner/work/_temp/kilo-tmp/c50_gates/`; refresh this file (timestamp/HEAD, gate results+log paths+rc, C49/C50 state, fixes/tests or "no proven gaps" with evidence, working-tree notes); keep `AGENT_HANDOFF.md` pointer-only. No planning-only exit. No commit/push unless explicitly requested. Do not revert intentional changes.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py` (body), `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`. (C50 may *probe* `data_loader.py` edges but any fix must be the smallest proven one; prefer reporting/CLI-level fixes if the behavior is only observable there.)
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes (notably `metrics.py` C49 guards and `tests/test_bab_metrics_c49_regressions.py`).