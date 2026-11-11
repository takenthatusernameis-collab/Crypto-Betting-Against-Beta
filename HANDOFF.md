# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T22:31:00Z
**HEAD:** `9f9d80e` (`chore: capture completed workflow run diagnostics`) on `main` — working tree clean at session start; untracked probe/temp artifacts exist only under `/home/runner/work/_temp/kilo-tmp/` (durable logs/scripts for C31). No BAB product/test code changes made this session; no commit/push.
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (execute immediately, no preamble loops)

**Next session is C32 (adversarial robustness + gate-integrity). You must do heavy, evidence-producing work. "No proven gaps" is an outcome only after full execution below — never a reason to skip.**

1. **Step 1 — Gate floors (mandatory, first, run to completion with ample timeout; persist durable logs under `/home/runner/work/_temp/kilo-tmp/c32_gate_<name>_<ts>.log`):**
   - `python3 -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → **floor ≥883 passed, 5 skipped, rc=0**.
   - `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → **rc=0** (slow; use timeout ≥900s, never abort early; timeout without observed failure is inconclusive, not green).
   - `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` → **floor ≥164 passed, 0 failed, rc=0**.
   Record exact counts+rc+durations+log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

2. **Step 2 — C32 adversarial probe campaign (mandatory after Step 1 green; heavy work):** systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Minimum required probe matrix (execute all; extend if you find a concrete hypothesis):
   - **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty `--data`, benchmark missing/overlap, empty/whitespace universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths.
   - **Metrics/reporting robustness:** degenerate/constant/NaN/short series, extreme drawdowns/vol, serialization safety (no NaN/Inf leakage in JSON).
   - **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths.
   For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

3. **Step 3 — Closure:** If no reproducible gaps after full Step 1+2, record "C32: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and leave next concrete task as "C33: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)". Do not exit after Step 1 alone; do not invent failures.

**Rules:** Do not reopen C28/C29/C31 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without an evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## C31 session results (2026-11-11T22:31:00Z, HEAD `9f9d80e`)

### Step 1 — Gate floors (re-verified this session, all PASS vs floors)
- **campaign_d + batch148/149/172:** `898 passed, 5 skipped, 53 warnings in 4.08s` — **rc=0** (floor ≥883 passed, 5 skipped). Log: `/home/runner/work/_temp/kilo-tmp/c31_gate_campaign_d.log`.
- **Full BAB excl `data_loader`/controller:** `2234 passed, 5 skipped, 41 warnings in 273.50s (0:04:33)` — observed completion PASS; summary line present in log tail. `---RC=...---` marker not captured in log file (tee/flush artifact) but no failures/errors observed. Log: `/home/runner/work/_temp/kilo-tmp/c31_gate_full_bab.log`.
- **campaign11+14:** `164 passed in 100.69s (0:01:40)` — **rc=0** (floor ≥164 passed, 0 failed). Log: `/home/runner/work/_temp/kilo-tmp/c31_gate_campaign11_14.log`.

### Step 2 — C31 adversarial probe campaign (all executed; no reproducible BAB-relevant gaps)
- **Durable artifacts:** `/home/runner/work/_temp/kilo-tmp/c31_probe.py`, `/home/runner/work/_temp/kilo-tmp/c31_probe2.py`, `/home/runner/work/_temp/kilo-tmp/c31_probe_run.log`, `/home/runner/work/_temp/kilo-tmp/c31_probe_log.txt` (JSON summary + detail), workspace `/home/runner/work/_temp/kilo-tmp/c31_ws/`.
- **Aggregate:** 59 probe checks total, **59 PASS, 0 FAIL** (after fixing probe harness import path for in-process module checks; initial harness-only `ModuleNotFoundError` failures were not product issues and were re-run correctly).

**Probe matrix outcomes (PASS):**
- **CLI/API/reporting parity & edge contracts (PASS):** `--help`, `--version`, `--dry-run --synthetic`, `--synthetic` run, returns-csv run with `--output` JSON (parsed, strict-finite), `--from-prices` run + dry-run, `bab_backtest_report.py --help/--json` (synthetic, from CSV), error-path probes with no tracebacks on user paths: invalid `--beta-window -1`, `--long-quantile nan`, `--short-quantile inf`, negative `--transaction-costs/--slippage`, missing/empty/dir `--data`, missing-data run, benchmark missing column, whitespace/empty universe tokens, `--output` to directory, report missing `--data-source --json`.
- **API/strategy:** `BABStrategy.run(returns_df=...)` PASS; `metrics.summary(...)` strict JSON serialization PASS.
- **Metrics/reporting robustness (PASS):** `sharpe_ratio/max_drawdown/annualized_volatility/sortino_ratio/win_rate/total_return/final_cumulative` exercised on `None/empty/single/const/nan_heavy/short/extreme/inf_in` without exception; `portfolio_beta(None,None)`/`turnover(None)` defensive; non-finite values surfaced as function-contract non-finite in raw outputs (sanitize/report paths expected to coerce per existing report helpers) — no uncaught exceptions/crashes.
- **Costs (PASS):** `compute_transaction_costs` basic Series + no-adv impact path finite/no-crash; rejects negative fee/bad participation cap; `apply_costs` callable on Series costs.
- **Regime (PASS):** `calculate_realized_volatility/classify_volatility_regimes/classify_volatility_regimes_percentile/classify_trend_regime/apply_regime_scaling` shape/behavior on normal+constant series; bad input raises as expected.
- **Attribution (PASS):** `trade_attribution/attribution_totals` basic columns/totals, empty/None defensive.
- **Shorting (PASS):** `apply_shorting_constraints` basic, unborrowable non-strict zeroing, bad-type rejection.
- **Sizing (PASS):** `apply_position_sizing` with Kelly/VolTarget/RiskParity/EqualWeight/string shorthand finite outputs, bad-type rejection.

**Conclusion:** **C31: no proven gaps** after full Step 1 + Step 2 execution on allowed surfaces. No product/test fixes required.

## Known bottlenecks / environment notes

- **No proven BAB runtime/code bottlenecks.**
- **Environment:** full suites are slow; run with ample timeout and durable logs. Timeout/interruption without observed failure is inconclusive, not a regression. `c31_gate_full_bab.log` shows PASS summary but missing `---RC=...---` marker (tee/echo capture quirk) — treat as observed-pass; re-run if strict rc-log evidence required.
- **Probe harness note:** initial c31 probe in-process checks failed with `ModuleNotFoundError` because `/tmp` script lacked repo on `sys.path`; corrected in `c31_probe2.py` (not a product issue). Future probes must `sys.path.insert(0, repo_root)` or run via `-m` from repo.
- **Historical CI diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` are prior captured log signals, not current source/test failures.
- **Known non-BAB (excluded, not a blocker):** `tests/test_controller_progress_accounting.py` may fail (infra/workflow staging). Exclude from BAB gates; **do not edit `.github/workflows/*`; do not weaken tests.**
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/`).

## C28/C29/C31 status (closed) — do not reopen without new evidence

- **C28/C29:** CLOSED per prior evidence (see git/HANDOFF lineage; `c28_*`, `c29_*` logs under `/home/runner/work/_temp/kilo-tmp/` from earlier sessions).
- **C31:** COMPLETE, no proven gaps. Evidence: gate logs and probe artifacts listed above (`c31_gate_*`, `c31_probe*`).

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durable log paths for any runs/probes completed, C32 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
