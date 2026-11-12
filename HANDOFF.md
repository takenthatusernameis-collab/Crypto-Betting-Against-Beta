# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T13:37:36Z
**HEAD:** `e8e91315b4d5b518dd7ad955c9f47138a7ffe0a5` on `main` (tracked tree clean at refresh)
**Working tree (tracked):** clean. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log/gate artifacts must not be committed.
**Env (verified):** Python 3.12.3, Linux, repo root `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`, run commands from repo root with `PYTHONPATH=.`; deps available (`numpy,pandas,scipy,pytest,hypothesis,coverage`).

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions. Heavy execution required.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads. Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven current source blocker recorded:** deps importable at HEAD, tracked tree clean. Ephemeral `/home/runner/work/_temp/kilo-tmp/` artifacts may not persist across runners—absence of tmp artifacts is not a regression; re-probe/re-gate as required.
- **C46 state:** **CLOSED CLEAN — 38/38 PASS, 0 FAIL, no proven gaps** (per durable evidence referenced in prior handoff). No churn.
- **C47 state:** **PROBES 38/38 PASS, 0 FAIL** (durable `/home/runner/work/_temp/kilo-tmp/c47_probes/`, summary `2026-11-12T13:11:54.875973Z`) — no proven probe gaps. **Gates:** G1 GREEN (`c47_gates/gate1_20261112T132700Z.log`, 898 passed, 5 skipped, 53 warnings, rc=0), G3 GREEN (`c47_gates/gate3_20261112T132700Z.log`, 164 passed, rc=0), G2 **INCOMPLETE/NOT GREEN** (`c47_gates/gate2_20261112T132900Z.log`, last observed ~22% at 13:33Z, ~574 bytes, no final summary/rc). **C47 NOT CLOSED**.
- **Gate invocation note:** run from repo root with `PYTHONPATH=.` (or `$PWD`). For Gate 1 prefer explicit `tests/test_bab_data_loader_campaign_d*` file list if globbing is brittle. Save timestamped durable logs under `/home/runner/work/_temp/kilo-tmp/c47_gates/` (or `c48_gates/` once C48 starts). Capture final summary lines and `rc`.

## Gate status (C47 session; refreshed 2026-11-12T13:37:36Z)

| Gate | Status | Evidence / notes | Command | Log |
|---|---|---|---|---|
| 1 | **GREEN** | 898 passed, 5 skipped, 53 warnings, rc=0 | explicit `tests/test_bab_data_loader_campaign_d*` (32 files) + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate1_20261112T132700Z.log` |
| 2 | **INCOMPLETE (blocking)** | Observed stalled at ~22% with no final rc/summary (log tail 13:33Z). Must be rerun to completion and captured durably. | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate2_20261112T132900Z.log` (partial) |
| 3 | **GREEN** | 164 passed in 111.81s, rc=0 | campaign11ab/11m/11n/11o/11p/11q/11s/14 CLI bundle (8 files) | `/home/runner/work/_temp/kilo-tmp/c47_gates/gate3_20261112T132700Z.log` |

**Primary bottleneck:** Gate 2 has no durable green completion. Do not claim C47 closure/progress until Gate 2 finishes green with rc=0 and G1/G3 remain valid for the same checkout/env.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C42:** CLOSED — 38/38 PASS. **C43:** 39/39 PASS. **C44:** 44/44 PASS. **C45:** 43/43 PASS. **C46:** 38/38 PASS, gates green.
- **C47:** probes 38/38 PASS (durable `/home/runner/work/_temp/kilo-tmp/c47_probes/`), **gate closure pending** (Gate 2 incomplete).

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, execute now)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus (priority):** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only. **No planning-only turn; heavy execution mandatory.**
- **Immediate actions (in order):**
  1. **Preflight:** confirm tracked tree clean, record HEAD/env, `python3 -c "import numpy,pandas,scipy,pytest,hypothesis,coverage; print('deps ok')"`. Work from repo root with `PYTHONPATH=.`
  2. **Clear C47 blocking bottleneck — complete Gate 2 with durable rc:**
     - Do not trust the partial `gate2_20261112T132900Z.log` as complete. Run to completion and tee to a new timestamped log, e.g. `/home/runner/work/_temp/kilo-tmp/c47_gates/gate2_<ts>_final.log`:
       `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`
     - Capture final summary and `rc`. If it fails, treat as proven gap: smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates with durable logs.
  3. **Close C47 when green:** if Gate 2 completes green (rc=0) and G1/G3 remain valid, mark C47 **CLOSED CLEAN** here (probes 38/38 PASS, no proven gaps, all gates green with log paths/rc). If env/checkout changed materially, re-run G1/G3 for same-head evidence.
  4. **If C47 closes cleanly, immediately start C48 (mandatory, heavy):** NEW probe runner (no C40–C47 reuse) with ≥20 NEW adversarial probes across required surfaces/cross-interactions; execute and save per-probe logs + summary under `/home/runner/work/_temp/kilo-tmp/c48_probes/`; rerun gates with logs under `/home/runner/work/_temp/kilo-tmp/c48_gates/`; record C48 matrix/results/state here as binding next task.
     - **C48 focus (new shapes only):** `cli.py`/`metrics.py`/reporting/`scripts/*` arg/error/reporting robustness where provable; allowed loader/wrapper/path/IO edges; `costs.py`/`regime.py`/`shorting.py`/`sizing.py`/`quality.py`/`data_sources.py`/`attribution.py` adversarial combos and fresh cross-interactions not equivalent to C47.
  5. **Before exit (mandatory):** refresh this file (timestamp/HEAD, gate results+log paths+rc, C47/C48 state, fixes/tests or "no proven gaps" with evidence, working-tree notes) and update `AGENT_HANDOFF.md`. No planning-only exit. No commit/push unless explicitly requested.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
