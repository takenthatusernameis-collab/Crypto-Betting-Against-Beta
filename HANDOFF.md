# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T23:02:30Z
**HEAD:** `4dfd861` (`chore(kilo): checkpoint agent session`) on `main` — working tree unchanged by this session except `HANDOFF.md` refresh (no BAB product/test code changes, no commit/push). Durable probe/gate logs written only under `/home/runner/work/_temp/kilo-tmp/` (untracked).
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every action must advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors, no `.github/workflows/*` edits, no commit/push unless explicitly requested.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (execute immediately, no preamble loops)

**Next session is C34 (adversarial robustness + gate-integrity). You must do heavy, evidence-producing work. "No proven gaps" is an outcome only after full execution below — never a reason to skip.**

1. **Step 1 — Gate floors (mandatory, first, run to completion with ample timeout; persist durable logs under `/home/runner/work/_temp/kilo-tmp/c34_gate_<name>_<ts>.log`). Run via `.venv/bin/python -m pytest ...` (system `python3` may lack pytest):**
   - `.venv/bin/python -m pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` → **floor ≥898 passed, 5 skipped, rc=0** (observed C33 baseline).
   - `.venv/bin/python -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` → **rc=0** (slow; use timeout ≥900s or monitor, never abort early; timeout without observed failure is inconclusive, not green). **C33 observed: 2234 passed, 5 skipped, rc=0**.
   - `.venv/bin/python -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` → **floor ≥164 passed, 0 failed, rc=0**.
   Record exact counts+rc+durations+log paths in this HANDOFF. A red floor is a proven blocker — fix smallest-possible in allowed areas only, add minimal regression, re-run affected gates, then continue.

2. **Step 2 — C34 adversarial probe campaign (mandatory after Step 1 green; heavy work):** systematically exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Minimum required probe matrix (execute all; rotate/expand beyond C33 — never skip heavy verification):
   - **CLI/API/reporting parity & edge contracts:** `--from-prices`/`--synthetic`/`--dry-run`/`--output` combos, invalid/NaN/Inf/negative args, missing/dir/empty/permission-denied `--data`, benchmark missing/overlap/duplicate, empty/whitespace/duplicate universe tokens, JSON/tear-sheet/report strict-finite & no-traceback on user paths, `bab_backtest_report.py` arg combos.
   - **Metrics/reporting robustness:** degenerate/constant/NaN/Inf/short/extreme series, serialization safety (raw `metrics.summary` may be non-finite by contract; CLI/report sanitized paths must remain strict-finite/no-leakage).
   - **Costs/regime/attribution/shorting/sizing:** boundary/zero/extreme params, monotonicity/invariants where applicable, interaction with backtest/report paths, no silent corruption or uncaught exceptions on reachable user paths. Use correct APIs/signatures (regime expects DataFrames; `compute_transaction_costs(weights, previous_weights, ...)`; `trade_attribution(weights, ...)` 1-arg form per signature; `sizing.SizingMethod` enum exists).
   For every probe record: command, rc, key outputs/invariants, PASS/FAIL. Any reproducible BAB-relevant failure → durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors.

3. **Step 3 — Closure:** If no reproducible gaps after full Step 1+2, record "C34: no proven gaps" with evidence summary/log paths, refresh timestamp/HEAD, and leave next concrete task as "C35: repeat gate floors + rotate/expand adversarial probe matrix on remaining allowed-surface edges (never skip heavy verification)". Do not exit after Step 1 alone; do not invent failures.

**Rules:** Do not reopen C28/C29/C31/C32/C33 without new statable reproducible failure + durable evidence. Do not churn locked modules. Do not declare "blocked" without an evidenced attempt and durable logs. This file is the sole durable coordination artifact.

## C33 session results (2026-11-11T23:02:30Z, HEAD `4dfd861`)

### Environment note (bottleneck removed)
- System `python3` had no `pytest`; gates/probes executed with `.venv/bin/python -m pytest` / `.venv/bin/python` (pytest 9.2.0 present). Initial full-gate shell invocations were interrupted/timed out and left a truncated log without PASS/rc marker (`c33_gate_full_bab_20261111T225340Z.log`, `c33_gate_full_bab_20261111T225600Z.log` — **inconclusive, not failures**); rerun completed via monitor with durable PASS evidence.

### Step 1 — Gate floors (all PASS vs floors)
- **campaign_d + batch148/149/172:** `898 passed, 5 skipped, 53 warnings in 5.36s` — **rc=0** (floor ≥898 passed, 5 skipped). Log: `/home/runner/work/_temp/kilo-tmp/c33_gate_campaign_d_20261111T225340Z.log`.
- **Full BAB excl `data_loader`/controller:** `2234 passed, 5 skipped, 41 warnings in 261.81s (0:04:21)` — **rc=0**. Log: `/home/runner/work/_temp/kilo-tmp/c33_gate_full_bab_20261111T230100Z.log` (monitor completed).
- **campaign11+14:** `164 passed in 117.52s (0:01:57)` — **rc=0** (floor ≥164 passed, 0 failed). Log: `/home/runner/work/_temp/kilo-tmp/c33_gate_campaign11_14_20261111T225340Z.log`.

### Step 2 — C33 adversarial probe campaign (executed; no reproducible BAB-relevant gaps)
- **Durable artifacts:** `/home/runner/work/_temp/kilo-tmp/c33_probe.py`, `/home/runner/work/_temp/kilo-tmp/c33_probe2.py`, `/home/runner/work/_temp/kilo-tmp/c33_probe3.py`, `/home/runner/work/_temp/kilo-tmp/c33_probe4.py`, `/home/runner/work/_temp/kilo-tmp/c33_probe_run_20261111T225700Z.log`, `/home/runner/work/_temp/kilo-tmp/c33_probe2_run_20261111T225900Z.log`, `/home/runner/work/_temp/kilo-tmp/c33_probe3_run_20261111T230000Z.log`, `/home/runner/work/_temp/kilo-tmp/c33_probe4_run_20261111T230100Z.log`, `/home/runner/work/_temp/kilo-tmp/c33_probe_summary.json`.
- **Aggregate (final corrected run, v4):** 34 probe checks total, **34 PASS, 0 FAIL** (`c33_probe_summary.json`/`c33_probe4_run_20261111T230100Z.log`). Earlier probe iterations (v1–v3) had harness/signature issues only (wrong expected rc 2 vs actual 1 for error paths, wrong API args for costs/regime/attribution/sizing enum path) — **not product defects**; corrected and re-run.

**Probe matrix outcomes (PASS):**
- **CLI/API/reporting parity & edge contracts (PASS):** `--help`, `--version`, `--dry-run --synthetic`, `--synthetic` run, returns-csv run with `--output` JSON (parsed, **strict-finite**), `--from-prices` run + dry-run, `bab_backtest_report.py --help/--data-source synthetic --json/--data-source csv --returns ... --json`. Error-path probes (nonzero rc, **no tracebacks** on user paths): invalid `--beta-window -1`, `--long-quantile nan`, `--short-quantile inf`, negative `--transaction-costs`/`--slippage`, missing/empty/dir `--data`, benchmark missing column, whitespace/empty universe tokens, `--output` to directory.
- **API/strategy:** `BABStrategy.run(returns_df=...)` PASS. `metrics.summary(...)` raw contract observed non-finite for unavailable fields in isolation (`turnover/strategy_beta/portfolio_beta` NaN) but **CLI output JSON remained strict-finite** — consistent with existing sanitize/report behavior (not a regression).
- **Metrics/reporting robustness (PASS):** `sharpe_ratio/max_drawdown/annualized_volatility/sortino_ratio/win_rate/total_return/final_cumulative` exercised on `None/empty/all-nan/single/mixed/const/extreme/inf` without uncaught exceptions/crashes.
- **Costs (PASS):** `compute_transaction_costs(weights, previous_weights)` basic path finite/no-crash (sig `(weights, previous_weights, fee_rate=0.001, ...)`).
- **Regime (PASS):** `calculate_realized_volatility/classify_volatility_regimes/classify_volatility_regimes_percentile/classify_trend_regime/mean_reversion_zscore/get_regime_state` on DataFrame inputs — shape/behavior OK, no uncaught exceptions.
- **Attribution (PASS):** `trade_attribution(weights)` (1-arg signature) + `attribution_totals` basic/defensive — no uncaught exceptions.
- **Shorting (PASS):** `apply_shorting_constraints` basic/default and borrowable/non-strict paths — no uncaught exceptions.
- **Sizing (PASS):** `apply_position_sizing` with `EqualWeight/VolTarget/RiskParity/Kelly/equal_weight` produced finite outputs (or handled per contract) without uncaught exceptions.

**Conclusion:** **C33: no proven gaps** after full Step 1 + Step 2 execution on allowed surfaces. No product/test fixes required.

## Known bottlenecks / environment notes (bottlenecks removed/clarified — do not re-litigate)

- **`tests/test_controller_progress_accounting.py` — EXCLUDED, NOT a BAB blocker.** Fails on `.github/workflows/*` pattern sync (see `research_state/workflow_run_diagnostics.jsonl`). Infra/workflow staging, not BAB product. **Do not edit `.github/workflows/*`; do not weaken/delete this test; do not spend cycles trying to make it pass.** Excluded from all BAB gate floors.
- **Environment:** full suites are slow; run with ample timeout and durable logs. Timeout/interruption without observed failure is **inconclusive, not a regression**. Use `.venv/bin/python -m pytest` (system python may lack pytest).
- **Probe harness:** in-process probe scripts under `/tmp` must `sys.path.insert(0, repo_root)` or run via `python3 -m` from repo root. Use correct module APIs/signatures (regime DF inputs; costs/attribution/sizing actual signatures) and treat CLI error rc contract as "nonzero + no traceback on user paths" unless a stricter rc is evidenced by tests.
- **Historical CI diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` are prior captured log signals, not current source/test failures.
- **Off-limits tracked artifacts:** `probe*`, `debug*`, `ast_probe.py` — do not edit/commit (use untracked `/home/runner/work/_temp/kilo-tmp/`).

## C28/C29/C31/C32/C33 status (closed) — do not reopen without new evidence

- **C28/C29/C31/C32:** CLOSED per prior evidence (see HANDOFF lineage and `c28_*`–`c32_*` logs under `/home/runner/work/_temp/kilo-tmp/`).
- **C33:** COMPLETE, no proven gaps. Evidence: gate logs `c33_gate_campaign_d_20261111T225340Z.log`, `c33_gate_campaign11_14_20261111T225340Z.log`, `c33_gate_full_bab_20261111T230100Z.log`; probes `c33_probe.py`–`c33_probe4.py`, `c33_probe*_run_*.log`, `c33_probe_summary.json`.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/` probes).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.**

## Handoff refresh requirement (before exit)

Update this same `HANDOFF.md` with refreshed timestamp/HEAD, exact gate counts+rc+durable log paths for any runs/probes completed, C34 probe matrix outcomes (PASS/FAIL per area + repro paths for any failure), and the next concrete task. Keep it single, durable, unambiguous.
