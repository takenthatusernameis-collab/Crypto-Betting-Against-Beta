# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T12:13:43Z
**HEAD:** `b970f6db607a9fe002937fcf6d092717ba7066c8` on `main`
**Working tree (tracked):** clean (`git status --short` empty). Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts must not be committed.
**Env (verified this session):** Python 3.12.3, Linux, repo root, `PYTHONPATH=$PWD`; `numpy,pandas,scipy,pytest,hypothesis,coverage` import OK.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven current blocker recorded:** deps importable at HEAD, tracked tree clean. Ephemeral `/home/runner/work/_temp/kilo-tmp/` artifacts may not persist across runners—absence of tmp artifacts is not a regression; re-probe/re-gate as required.
- **C46 state (binding):** **NOT COMPLETE.** `/home/runner/work/_temp/kilo-tmp/c46_gates/` contains partial/stale baseline+coverage logs from a prior attempt (not durable proof for current HEAD); `/home/runner/work/_temp/kilo-tmp/c46_probes/` is empty — **no C46 probes executed**. Do not claim C46 closed or "no proven gaps" without ≥20 NEW C46 probes and durable per-probe evidence.
- **Gate invocation note:** for Gate 1 prefer explicit `tests/test_bab_data_loader_campaign_d*` file list if globbing is brittle. Run Gate 2/3 from repo root with `PYTHONPATH=$PWD`.

## Gate floors (last recorded GREEN on prior HEAD; re-validate for current work)
Prior recorded GREEN (HEAD `238b034`, 2026-11-12T11:09:00Z, logs under `/home/runner/work/_temp/kilo-tmp/c44_gates/`): Gate 1 **898 passed, 5 skipped, rc=0**; Gate 2 **2234 passed, 5 skipped, rc=0**; Gate 3 **164 passed, rc=0**. HEAD has advanced via checkpoint-only commits and no source changes are indicated in handoff history, but ephemeral logs are not durable proof for this checkout. **Before any fix or if env/checkout uncertain, re-run Gate 1/2/3 to completion and save durable logs in `/home/runner/work/_temp/kilo-tmp/c46_gates/`** (timestamped). No gate green → do not claim progress.

| Gate | Command (cwd=repo root, `PYTHONPATH=$PWD`) |
|---|---|
| 1 | `python3 -m pytest -q` over explicit `tests/test_bab_data_loader_campaign_d{,2,3,5,_coerce_more,_core,_core2,_core3,_core4,_core5,_core_final,_deep,_deep3,_final_coverage,_final_push,_final_push2,_gaps,_gaps2,_heavy,_heavy2,_heavy3,_heavy_push2,_more2,_more4,_more5,_push,_push2,_push3,_push4,_push_final,_push_heavy,_ultra}.py` + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` |
| 2 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` |
| 3 | `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` |

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42 ROTATION:** CLOSED — 38/38 PASS, 0 FAIL.
- **C43 ROTATION** (2026-11-12T09:25:00Z, HEAD `b7df039`): 39/39 PASS, 0 FAIL/ERROR, no proven gaps.
- **C44 ROTATION** (2026-11-12T11:09:00Z, HEAD `238b034`): 44/44 PASS, 0 FAIL, no proven gaps.
- **C45 ROTATION** (2026-11-12T12:09:27Z, HEAD `84b148e`): **CLOSED CLEAN — 43/43 PASS, 0 FAIL, 0 ERROR, no proven gaps** (durable logs/summary under prior `/home/runner/work/_temp/kilo-tmp/c45_probes/` when present; no source changes). C6–C41 closed per prior evidence. No churn.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, read first — 2026-11-12T12:13:43Z)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; **no planning-only turn**.
- **Binding campaign:** **C46 ROTATION** (heavy, mandatory). C45 closed clean. C46 is **open/unexecuted** — do not declare "no proven gaps", "complete", or "blocked" without attempted probes and durable logs under `/home/runner/work/_temp/kilo-tmp/c46_probes/`.
- **Immediate actions (in order):**
  1. **Preflight:** confirm `git status --short` (tracked clean expected), `python3 -c "import numpy, pandas, scipy, pytest, hypothesis, coverage"`; install missing deps only if needed. Record env/HEAD.
  2. **Gates:** if env/checkout uncertain or any fix made (and recommended at campaign start for durable baseline), re-run Gate 1/2/3 to completion with timestamped durable logs in `/home/runner/work/_temp/kilo-tmp/c46_gates/`.
  3. **Execute ≥20 NEW C46 adversarial probes** (C46 shapes only; **no reuse of C40–C45 scripts/shapes**) across required surfaces/cross-interactions below. Save per-probe durable logs/artifacts (id, target, shape, result, rc/duration, repro/notes) in `/home/runner/work/_temp/kilo-tmp/c46_probes/` plus a summary JSON/MD.
  4. **On any proven gap:** smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → capture durable evidence. Do not weaken locked tests.
  5. **Before exit (mandatory):** refresh this file (timestamp/HEAD, gate results+log paths if re-run, full C46 probe matrix, fixes/tests added or "no proven gaps" with per-probe evidence, working-tree notes) and update `AGENT_HANDOFF.md`. If C46 closes cleanly, **immediately define and start C47** (≥20 new probes, new shapes, durable logs) and leave C47 as the next binding initial task here.

## BINDING INITIAL TASK — C46 ROTATION (heavy, mandatory)

**Objective:** deep adversarial robustness campaign (C46). Execution, not planning.

### 1) Environment & gates
- Preflight deps/imports; fix env bottlenecks first. No gate green → do not claim progress.
- Re-run Gate 1/2/3 to completion from repo root with `PYTHONPATH=$PWD` when env/checkout uncertain or any fix made; capture durable logs in `/home/runner/work/_temp/kilo-tmp/c46_gates/`.

### 2) Execute ≥20 NEW adversarial probes (C46 shapes only)
- **No reuse** of C40–C45 scripts/shapes. Durable per-probe logs/artifacts under `/home/runner/work/_temp/kilo-tmp/c46_probes/` + summary.
- **Target surfaces/shapes (distinct from C45):**
  - `beta.py`: `calculate_beta` with object-dtype string arrays; `rolling_beta` window=1; `estimate_betas` min_obs=None & window=None; `calculate_rolling_beta` all-NaN benchmark raises `BABDataError`.
  - `data_loader.py`: `load_returns_from_hdf5` missing file raises; `load_returns_from_pickle` flat scalar list raises; `load_returns_from_json` empty file raises; `normalize_schema` duplicate columns raises; `standardize_columns` None raises.
  - `strategy.py`: `run()` data_source missing file raises; `run()` benchmark not in data raises; `tear_sheet()`/`report()` before `run()` raises `RuntimeError`.
  - `costs.py`: `compute_transaction_costs` weights None returns empty Series; `participation_cap` >1 rejected; `fixed_fee_per_trade` negative rejected.
  - `regime.py`: `classify_volatility_regimes_percentile` invalid quantiles; `mean_reversion_zscore` zero std; `classify_trend_regime` z_window>=1.
  - `shorting.py`: `apply_shorting_constraints` non-`ShortingConstraints` raises `BABShortingError`; `is_borrowable` wildcard fallback; `borrow_bps_per_year` dict missing asset + no wildcard uses default.
  - `sizing.py`: `RiskParitySizer` target_vol<=0 rejected; `apply_position_sizing` None sizer returns base weights; `KellySizer` fraction negative rejected.
  - `signals.py`: `generate_bab_signals` None input empty; all-NaN beta frame zero signals; long/short quantile = 0.0.
  - `portfolio.py`: `construct_portfolio` None returns empty; `max_single_weight` binding; `net_exposure_limit` binding.
  - `backtest.py`: `run_backtest` None returns/weights returns framed empty DataFrame.
- **Required NEW cross-interactions:** `beta+signals`, `data_loader+strategy`, `costs+portfolio`, `regime+sizing`, `shorting+sizing`, `backtest+attribution`, `signals+portfolio`.
- Maintain probe matrix (id, target, shape, result, log path, brief repro). Minimum 20 probes.

### 3) On proven regression/gap
Smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence.

### 4) On no proven gaps
Record **"C46 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths.

### 5) Before exit (mandatory)
Refresh this file with: timestamp/HEAD, gate results+log paths (if run), full C46 probe matrix, fixes/tests added (if any), working-tree notes, and **next concrete heavy task**. Update `AGENT_HANDOFF.md`. If C46 closes cleanly, **immediately define and start C47** (≥20 new probes, new shapes, durable logs) and leave it binding here.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
