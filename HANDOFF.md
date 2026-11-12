# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T13:29:20Z
**HEAD:** `8bafd4d8c095493b59646b09ca542053faab7a2f` on `main` (tracked tree clean at refresh)
**Working tree (tracked):** clean. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log/gate artifacts must not be committed.
**Env (verified this session):** Python 3.12.3, Linux, repo root `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`, `PYTHONPATH=$PWD` (or `.` from repo root); `numpy,pandas,scipy,pytest,hypothesis,coverage` import OK.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads. Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven current source blocker recorded:** deps importable at HEAD, tracked tree clean. Ephemeral `/home/runner/work/_temp/kilo-tmp/` artifacts may not persist across runners—absence of tmp artifacts is not a regression; re-probe/re-gate as required.
- **C46 state:** **CLOSED CLEAN — 38/38 PASS, 0 FAIL, no proven gaps.** Durable logs under `/home/runner/work/_temp/kilo-tmp/c46_probes/` + gates under `/home/runner/work/_temp/kilo-tmp/c46_gates/` (Gate1 898p/5s, Gate2 2234p/5s, Gate3 164p, all rc=0 at C46). C6–C45 closed per prior evidence. No churn.
- **C47 state:** **PROBES 38/38 PASS, 0 FAIL** (durable `/home/runner/work/_temp/kilo-tmp/c47_probes/`, summary `2026-11-12T13:11:54.875973Z`) — no proven probe gaps. **Gates (this refresh):** G1 GREEN `gate1_20261112T132700Z.log` (898p/5s rc=0), G3 GREEN `gate3_20261112T132700Z.log` (164p rc=0), G2 **RUNNING/INCOMPLETE** `gate2_20261112T132900Z.log` (~22% observed, no final rc). **C47 NOT CLOSED** until G2 completes green with durable rc. No proven source gaps found.
- **Gate invocation note:** run from `repo root` with `PYTHONPATH=$PWD`. For Gate 1 prefer explicit `tests/test_bab_data_loader_campaign_d*` file list if globbing is brittle. Save timestamped durable logs under `/home/runner/work/_temp/kilo-tmp/c47_gates/` (or `c48_gates/` once C48 starts). Capture final summary lines and `rc`.

## Gate status (C47 session; refreshed 2026-11-12T13:29:20Z)
Run all from repo root with `PYTHONPATH=.` (or `$PWD`).

| Gate | Status | Result / progress | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN** | **898 passed, 5 skipped, 53 warnings, rc=0** | explicit `tests/test_bab_data_loader_campaign_d*` (32 files) + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate1_20261112T132700Z.log` |
| 2 | **RUNNING / INCOMPLETE (non-green)** | last observed `~22%` in log tail at refresh; **no final summary/rc yet** (may still be active) | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate2_20261112T132900Z.log` |
| 3 | **GREEN** | **164 passed in 111.81s, rc=0** | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files) | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate3_20261112T132700Z.log` |

**Bottleneck to clear first:** Gate 2 must finish with durable final summary/rc (append/tee to same log or start `gate2_<ts>_final.log`). **C47 remains NOT CLOSED** until Gate 2 is green and G1/G3 re-confirmed if env changed. No gate green/no final rc → do not claim closure/progress. Gate 2 is long-running; wait to completion, do not kill. If interrupted, rerun Gate 2 to completion and capture rc. Note: an earlier attempt running from wrong cwd caused `ModuleNotFoundError`/collection noise for broad runs—always run from repo root with correct `PYTHONPATH`.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42:** CLOSED — 38/38 PASS. **C43:** 39/39 PASS. **C44:** 44/44 PASS. **C45:** 43/43 PASS. **C46:** 38/38 PASS, gates green.
- **C47:** probes 38/38 PASS (durable evidence in `/home/runner/work/_temp/kilo-tmp/c47_probes/`); **gate closure pending** (Gate 2/3 not finalized in this session).

## C47 probe matrix (executed, durable)
Runner: `/home/runner/work/_temp/kilo-tmp/c47_probes/c47_probe_runner.py` (38 probes, no C40–C46 reuse). Summary: `/home/runner/work/_temp/kilo-tmp/c47_probes/c47_probe_summary.md` / `.json`.

| ID | Target | Shape | Result |
|---|---|---|---|
| C47-001 | beta.py | `calculate_beta` inf values masked/finite-or-nan, no crash | PASS |
| C47-002 | beta.py | `rolling_beta` min_obs > window clamps, no crash | PASS |
| C47-003 | beta.py | `estimate_betas` min_obs > window clamps, no crash | PASS |
| C47-004 | beta.py | `calculate_rolling_beta` empty DF raises `BABDataError` | PASS |
| C47-005 | data_loader.py | `load_returns_from_csv` empty file raises `BABDataError` | PASS |
| C47-006 | data_loader.py | `load_returns_from_jsonl` empty file raises `BABDataError` | PASS |
| C47-007 | data_loader.py | `load_prices` missing file raises `BABDataError` | PASS |
| C47-008 | data_loader.py | `validate_returns_dataframe` None raises `BABDataError` | PASS |
| C47-009 | data_loader.py | `standardize_columns` empty DF returns empty, no crash | PASS |
| C47-010 | strategy.py | `run()` `data_source` min_rows insufficient raises `BABDataError` | PASS |
| C47-011 | strategy.py | `long_quantile=0.0` raises `BABConfigError` | PASS |
| C47-012 | strategy.py | `run()` benchmark-only DF raises `BABDataError` | PASS |
| C47-013 | costs.py | `compute_transaction_costs` empty weights returns empty Series | PASS |
| C47-014 | costs.py | `TransactionCostModel` negative `linear_fee` raises `BABCostError` | PASS |
| C47-015 | costs.py | `borrow_bps_per_year` float normalized to wildcard dict | PASS |
| C47-016 | regime.py | `calculate_realized_volatility` window=0 raises `ValueError` | PASS |
| C47-017 | regime.py | `apply_regime_scaling` empty signals returns empty | PASS |
| C47-018 | regime.py | `classify_trend_regime` z_window=0 falls back to MA, no crash | PASS |
| C47-019 | shorting.py | `ShortingConstraints` borrowable not dict raises `BABShortingError` | PASS |
| C47-020 | shorting.py | `apply_shorting_constraints` None constraints default empty DF | PASS |
| C47-021 | shorting.py | `max_short_notional_per_asset` binding scales short down | PASS |
| C47-022 | sizing.py | `VolatilityTargetSizer` lookback=0 raises `BABSizingError` | PASS |
| C47-023 | sizing.py | `RiskParitySizer` max_leverage=0 raises `BABSizingError` | PASS |
| C47-024 | sizing.py | `apply_position_sizing` empty signals returns empty | PASS |
| C47-025 | signals.py | `generate_bab_signals` long_quantile=1.0 all-long, no crash | PASS |
| C47-026 | signals.py | `generate_bab_signals` inf beta values no crash | PASS |
| C47-027 | signals.py | `generate_bab_signals` int64 dtype input no crash | PASS |
| C47-028 | portfolio.py | `construct_portfolio` gross_exposure_limit binding raises `BABDataError` | PASS |
| C47-029 | portfolio.py | `enforce_beta_neutrality` None weights returns None | PASS |
| C47-030 | backtest.py | `run_backtest` returns list input returns empty DF | PASS |
| C47-031 | backtest.py | `run_backtest` transaction_costs>0 applies `cost_drag` | PASS |
| C47-032 | beta+backtest | rolling beta → signals → portfolio → `run_backtest` cumulative | PASS |
| C47-033 | data_loader+signals | load returns DF → beta → bab signals non-empty | PASS |
| C47-034 | costs+signals | bab signals → portfolio → `compute_transaction_costs` sum>=0 | PASS |
| C47-035 | regime+backtest | `regime_scale_scalar` → scaled weights → `run_backtest` cumulative | PASS |
| C47-036 | shorting+portfolio | `apply_shorting_constraints` → `construct_portfolio` non-empty | PASS |
| C47-037 | backtest+sizing | `apply_position_sizing` → `run_backtest` cumulative | PASS |
| C47-038 | portfolio+attribution | portfolio → backtest → attribution totals net_return | PASS |

**C47 probe outcome:** "no proven gaps" from executed probes (38/38 PASS) — **pending full gate closure**.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, read first — 2026-11-12T13:29:20Z)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus (priority):** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only. **No planning-only turn; heavy execution mandatory.**
- **Immediate actions (in order):**
  1. **Preflight:** confirm tracked tree clean, record HEAD/env, `python3 -c "import numpy,pandas,scipy,pytest,hypothesis,coverage; print('deps ok')"`. Work from repo root with `PYTHONPATH=.`
  2. **Clear C47 gate bottleneck (blocking):** Gate 1 GREEN (`c47_gates/gate1_20261112T132700Z.log`, 898p/5s rc=0), Gate 3 GREEN (`c47_gates/gate3_20261112T132700Z.log`, 164p rc=0). Gate 2 is long-running and was observed at ~22% with no final rc in `/home/runner/work/_temp/kilo-tmp/c47_gates/gate2_20261112T132900Z.log`.
     - Check if Gate 2 process is still active and let it finish; capture final summary + rc durably (do not kill). If log ended without rc or process died, rerun to completion: `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → timestamped log with rc.
     - **C47 can close only when Gate 2 is green with durable rc and G1/G3 remain valid.**
  3. **On Gate 2 green:** mark C47 **CLOSED CLEAN** here (probes 38/38 PASS in `/home/runner/work/_temp/kilo-tmp/c47_probes/`, no proven gaps; all gates green with log paths/rc).
  4. **On any proven gap/failure:** smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence. Do not weaken locked tests. Record root cause/evidence/fix.
  5. **If C47 closes cleanly, immediately start C48 (mandatory, heavy):** NEW probe runner (no C40–C47 reuse) with ≥20 NEW adversarial probes across required surfaces/cross-interactions; execute and save per-probe logs + summary under `/home/runner/work/_temp/kilo-tmp/c48_probes/`; rerun gates with logs under `/home/runner/work/_temp/kilo-tmp/c48_gates/`; record C48 matrix/results/state here as binding next task.
     - **C48 focus (new shapes only):** `cli.py`/`metrics.py`/reporting/`scripts/*` arg/error/reporting robustness where provable; allowed loader/wrapper/path/IO edges; `costs.py`/`regime.py`/`shorting.py`/`sizing.py`/`quality.py`/`data_sources.py`/`attribution.py` adversarial combos and fresh cross-interactions not equivalent to C47.
  6. **Before exit (mandatory):** refresh this file (timestamp/HEAD, gate results+log paths+rc, C47/C48 state, fixes/tests or "no proven gaps" with evidence, working-tree notes) and update `AGENT_HANDOFF.md`. No planning-only exit. No commit/push unless explicitly requested.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
