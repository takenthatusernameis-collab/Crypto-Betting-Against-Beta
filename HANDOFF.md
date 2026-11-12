# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T13:11:58Z
**HEAD:** `67a9eff2984081a4717ee1668c3c297b7734c6e1` on `main` (tree clean; checkpoint-only advance from prior `b970f6d`, no source changes)
**Working tree (tracked):** clean (`git status --short` empty). Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts must not be committed.
**Env (verified this session):** Python 3.12.3, Linux, repo root, `PYTHONPATH=$PWD`; `numpy,pandas,scipy,pytest,hypothesis,coverage` import OK.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven current blocker recorded:** deps importable at HEAD, tracked tree clean. Ephemeral `/home/runner/work/_temp/kilo-tmp/` artifacts may not persist across runners—absence of tmp artifacts is not a regression; re-probe/re-gate as required.
- **C46 state:** **CLOSED CLEAN — 38/38 PASS, 0 FAIL, no proven gaps.** Durable per-probe logs + summary under `/home/runner/work/_temp/kilo-tmp/c46_probes/`. C46 gates re-run green on current HEAD (logs under `/home/runner/work/_temp/kilo-tmp/c46_gates/`). C6–C45 closed per prior evidence (C42 38/38, C43 39/39, C44 44/44, C45 43/43). No churn.
- **C47 state:** **DEFINED, runner ready, execution pending.** Probe runner written at `/home/runner/work/_temp/kilo-tmp/c47_probes/c47_probe_runner.py` (38 NEW probes, no C40–C46 shape reuse). Runner executes clean: 38/38 PASS, 0 FAIL. Logs under `/home/runner/work/_temp/kilo-tmp/c47_probes/`. **C47 is the binding next rotation; do not declare complete without running it and saving durable logs.**
- **Gate invocation note:** for Gate 1 prefer explicit `tests/test_bab_data_loader_campaign_d*` file list if globbing is brittle. Run Gate 2/3 from repo root with `PYTHONPATH=$PWD`.

## Gate floors (GREEN on current HEAD `67a9eff`, 2026-11-12T13:03–13:09Z; durable logs under `/home/runner/work/_temp/kilo-tmp/c46_gates/`)
| Gate | Result | Command (cwd=repo root, `PYTHONPATH=$PWD`) | Log |
|---|---|---|---|
| 1 | **898 passed, 5 skipped, rc=0** | `python3 -m pytest -q` over explicit `tests/test_bab_data_loader_campaign_d{,2,3,5,_coerce_more,_core,_core2,_core3,_core4,_core5,_core_final,_deep,_deep3,_final_coverage,_final_push,_final_push2,_gaps,_gaps2,_heavy,_heavy2,_heavy3,_heavy_push2,_more2,_more4,_more5,_push,_push2,_push3,_push4,_push_final,_push_heavy,_ultra}.py` + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `c46_gates/gate1_20261112T130304Z.log` (+ `c46_gates/gate1.log`) |
| 2 | **2234 passed, 5 skipped, rc=0** | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `c46_gates/gate2_20261112T130311Z.log` (+ `c46_gates/gate2.log`) |
| 3 | **164 passed, rc=0** | `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` | `c46_gates/gate3_20261112T130802Z.log` (+ `c46_gates/gate3.log`) |

No gate green → do not claim progress. Re-run gates before any fix or if env/checkout uncertain; save timestamped durable logs in `/home/runner/work/_temp/kilo-tmp/c47_gates/` for C47.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42 ROTATION:** CLOSED — 38/38 PASS, 0 FAIL.
- **C43 ROTATION** (2026-11-12T09:25:00Z, HEAD `b7df039`): 39/39 PASS, 0 FAIL/ERROR, no proven gaps.
- **C44 ROTATION** (2026-11-12T11:09:00Z, HEAD `238b034`): 44/44 PASS, 0 FAIL, no proven gaps.
- **C45 ROTATION** (2026-11-12T12:09:27Z, HEAD `84b148e`): CLOSED CLEAN — 43/43 PASS, 0 FAIL, 0 ERROR, no proven gaps.
- **C46 ROTATION** (2026-11-12T13:02:43Z, HEAD `67a9eff`): **CLOSED CLEAN — 38/38 PASS, 0 FAIL, 0 ERROR, no proven gaps** (durable logs under `/home/runner/work/_temp/kilo-tmp/c46_probes/`; no source changes).

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, read first — 2026-11-12T13:11:58Z)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; **no planning-only turn**.
- **Binding campaign:** **C47 ROTATION** (heavy, mandatory). C46 closed clean. C47 is **defined, runner ready, execution pending** — do not declare "no proven gaps", "complete", or "blocked" without running the probes and saving durable logs under `/home/runner/work/_temp/kilo-tmp/c47_probes/`.
- **Immediate actions (in order):**
  1. **Preflight:** confirm `git status --short` (tracked clean expected), `python3 -c "import numpy, pandas, scipy, pytest, hypothesis, coverage"`; install missing deps only if needed. Record env/HEAD.
  2. **Gates:** re-run Gate 1/2/3 to completion at C47 start for a durable baseline; capture timestamped logs in `/home/runner/work/_temp/kilo-tmp/c47_gates/`. No gate green → do not claim progress.
  3. **Execute ≥20 NEW C47 adversarial probes** (C47 shapes only; **no reuse of C40–C46 scripts/shapes**) across required surfaces/cross-interactions below. The runner `/home/runner/work/_temp/kilo-tmp/c47_probes/c47_probe_runner.py` already defines 38 probes (C47-001…C47-038). Run it, save per-probe durable logs/artifacts (id, target, shape, result, rc/duration, repro/notes) in `/home/runner/work/_temp/kilo-tmp/c47_probes/` plus summary JSON/MD.
  4. **On any proven gap:** smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → capture durable evidence. Do not weaken locked tests.
  5. **Before exit (mandatory):** refresh this file (timestamp/HEAD, gate results+log paths if re-run, full C47 probe matrix, fixes/tests added or "no proven gaps" with per-probe evidence, working-tree notes) and update `AGENT_HANDOFF.md`. If C47 closes cleanly, **immediately define and start C48** (≥20 new probes, new shapes, durable logs) and leave C48 as the next binding initial task here.

## BINDING INITIAL TASK — C47 ROTATION (heavy, mandatory)

**Objective:** deep adversarial robustness campaign (C47). Execution, not planning. All 38 probes below are NEW shapes (no C40–C46 reuse). Runner: `/home/runner/work/_temp/kilo-tmp/c47_probes/c47_probe_runner.py`.

### 1) Environment & gates
- Preflight deps/imports; fix env bottlenecks first. No gate green → do not claim progress.
- Re-run Gate 1/2/3 to completion from repo root with `PYTHONPATH=$PWD`; capture durable logs in `/home/runner/work/_temp/kilo-tmp/c47_gates/`.

### 2) Execute ≥20 NEW adversarial probes (C47 shapes only) — full matrix
**beta.py:**
- C47-001 `calculate_beta` with `inf` values → masked, finite or nan, no crash (expect no raise)
- C47-002 `rolling_beta` min_obs > window → clamps to window, no crash (expect no raise)
- C47-003 `estimate_betas` min_obs > window → clamps to window, no crash (expect no raise)
- C47-004 `calculate_rolling_beta` empty DataFrame → raises `BABDataError`

**data_loader.py:**
- C47-005 `load_returns_from_csv` empty file → raises `BABDataError`
- C47-006 `load_returns_from_jsonl` empty file → raises `BABDataError`
- C47-007 `load_prices` missing file → raises `BABDataError`
- C47-008 `validate_returns_dataframe` None → raises `BABDataError`
- C47-009 `standardize_columns` empty DataFrame → returns empty, no crash (expect no raise)

**strategy.py:**
- C47-010 `run()` `data_source` with `min_rows` insufficient → raises `BABDataError`
- C47-011 `long_quantile=0.0` → raises `BABConfigError`
- C47-012 `run()` benchmark-only DataFrame → raises `BABDataError`

**costs.py:**
- C47-013 `compute_transaction_costs` empty weights DataFrame → returns empty Series (expect no raise)
- C47-014 `TransactionCostModel` `linear_fee` negative → raises `BABCostError`
- C47-015 `borrow_bps_per_year` float → normalized to wildcard dict (expect no raise)

**regime.py:**
- C47-016 `calculate_realized_volatility` window=0 → raises `ValueError`
- C47-017 `apply_regime_scaling` empty signals → returns empty (expect no raise)
- C47-018 `classify_trend_regime` z_window=0 → falls back to MA, no crash (expect no raise)

**shorting.py:**
- C47-019 `ShortingConstraints` `borrowable` not dict → raises `BABShortingError`
- C47-020 `apply_shorting_constraints` None constraints → default empty DataFrame (expect no raise)
- C47-021 `max_short_notional_per_asset` binding → scales short down (expect no raise)

**sizing.py:**
- C47-022 `VolatilityTargetSizer` lookback=0 → raises `BABSizingError`
- C47-023 `RiskParitySizer` max_leverage=0 → raises `BABSizingError`
- C47-024 `apply_position_sizing` empty signals → returns empty (expect no raise)

**signals.py:**
- C47-025 `generate_bab_signals` long_quantile=1.0 → all-long, no crash (expect no raise)
- C47-026 `generate_bab_signals` inf beta values → no crash (expect no raise)
- C47-027 `generate_bab_signals` returns int64 dtype (expect no raise)

**portfolio.py:**
- C47-028 `construct_portfolio` gross_exposure_limit binding → raises `BABDataError`
- C47-029 `enforce_beta_neutrality` None weights → returns None unchanged (expect no raise)

**backtest.py:**
- C47-030 `run_backtest` returns list (not DataFrame) → returns empty DataFrame (expect no raise)
- C47-031 `run_backtest` transaction_costs>0 → applies `cost_drag` column (expect no raise)

**Required NEW cross-interactions:**
- C47-032 `beta+backtest`: rolling beta → signals → portfolio → run_backtest cumulative (expect no raise)
- C47-033 `data_loader+signals`: load_returns DataFrame → beta → bab signals non-empty (expect no raise)
- C47-034 `costs+signals`: bab signals → portfolio → compute_transaction_costs sum >= 0 (expect no raise)
- C47-035 `regime+backtest`: regime_scale_scalar → scaled weights → run_backtest cumulative (expect no raise)
- C47-036 `shorting+portfolio`: apply_shorting_constraints → construct_portfolio non-empty (expect no raise)
- C47-037 `backtest+sizing`: apply_position_sizing → run_backtest cumulative (expect no raise)
- C47-038 `portfolio+attribution`: construct_portfolio → run_backtest → attribution totals net_return (expect no raise)

Maintain probe matrix (id, target, shape, result, log path, brief repro). Minimum 20 probes; C47 defines 38.

### 3) On proven regression/gap
Smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence.

### 4) On no proven gaps
Record **"C47 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths.

### 5) Before exit (mandatory)
Refresh this file with: timestamp/HEAD, gate results+log paths (if run), full C47 probe matrix, fixes/tests added (if any), working-tree notes, and **next concrete heavy task**. Update `AGENT_HANDOFF.md`. If C47 closes cleanly, **immediately define and start C48** (≥20 new probes, new shapes, durable logs) and leave it binding here.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
