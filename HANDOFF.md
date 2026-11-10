# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T17:00:00Z (this session); source handoff timestamp 2026-11-10T16:02:41Z retained for provenance
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `288f69b` (`chore(kilo): checkpoint agent session`, `main`; up-to-date with `origin/main`)
**Working tree:** one untracked file only — `tests/test_bab_cli_campaign17.py` (new C17 regressions, 16 passed this session, NOT committed; commit/push only if explicitly requested). No production code changes. No competing handoff files. C16 executed and closed in prior session; all gates re-verified fresh at HEAD `288f69b` this session.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; re-verified 2026-11-10T16:47Z)
- Campaign 14 CLI reporting: **17 passed, rc=0** (`tests/test_bab_cli_campaign14_cli_reporting.py`) — re-verified this session (164 passed total incl. C11 bundle 11m/n/o/p/q/s/11ab + 14, rc=0)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** — re-verified this session
- Full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`): **4740 passed, 35 skipped, rc=0** — re-verified this session (hard floor 4708 maintained; +16 = exactly the new C17 test file `tests/test_bab_cli_campaign17.py`)
- C16 probe evidence log: `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`
- C17 probe evidence log: `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; **no blocked or inefficient in-repo sessions identified**. C16 **COMPLETE** (13 probe combos; no proven gaps; regressions in `tests/test_bab_cli_campaign16.py`, 16 passed). C17 **COMPLETE**: 13 matrix subprocess combos + in-process parity ×3 + weights neutrality/shorting + defective-fixture error paths, all rc=0 or clean rc=1, no Traceback, no non-finite/corrupt JSON, stdout non-empty/stderr empty on success paths. REAL default cum=0.45632700835934265 periods=398; EXP default cum=0.5311665101149625 periods=398; REAL ETH cum=2.1986969529723432 periods=398 — bit-identical to C16/C15 values, no regression. Determinism: repeat runs byte-identical stdout/JSON. In-process `BABStrategy.run` parity equal to console full-float values for REAL default/EXP default/REAL ETH. Weights dollar-neutral (row sums ≈0, atol=1e-6) with negative (short) weights present, 8 assets × 398 rows. Defective fixtures (`degenerate_metrics.csv`, `benchmark_nan_window.csv`, `real_data_defects.csv`, `junk_columns.csv`, `all_nan_column.csv`) → rc=1, actionable "Data load/validation failed: ..." messages, no Traceback, no output JSON created. **No proven gaps for C17** (evidence: c17 log above). Regression tests added in `tests/test_bab_cli_campaign17.py` (16 passed). No production code touched. Proceed directly to C18 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr and JSON validity where applicable) and either (a) new regression tests for proven gaps or (b) an explicit "no proven gaps" conclusion with evidence references.

### 1) Stabilize baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **≥164 passed, rc=0**
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **≥883 passed, 5 skipped, rc=0**
- `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **≥4708 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)

Treat prior campaign regressions as evidence; do not revert without cause.

### 2) Campaigns 6–16 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity, C13 CLI dry-run + JSON output edge cleanliness, C14 CLI reporting fidelity + real-data console-script parity, C15 BAB end-to-end real-data pipeline parity (≥18 combos), **C16 BAB output/reporting schema & metrics fidelity (13 combos, no proven gaps, regressions in tests/test_bab_cli_campaign16.py)**. Evidence: C15 log `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`; C16 log `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`. Do not churn without a new, statable, reproducible failure.

### 3) Campaign 17 — CLOSED (evidence-backed, no churn)
C17 **COMPLETE and closed** this session (2026-11-10T16:47Z @ HEAD `288f69b`). Evidence log `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`; regressions locked in `tests/test_bab_cli_campaign17.py` (16 passed). No proven gaps — do not churn without a new, statable, reproducible failure.

### 4) Execute C18 — BAB metrics, report, attribution & sizing fidelity on real & defective data (≥12 distinct probe combos, HEAVY)
Goal: verify **BAB reporting/analytics correctness and robustness** — `BABStrategy.report()`/`tear_sheet()`/`report_to_json()` metric finiteness & JSON-strictness, trade attribution totals, position-sizer dict shorthands, regime filter, beta-neutral enforcement — across fixtures and parameterizations, with subprocess CLI edges (`--dry-run`, `--version`, bad `--from-prices`) included.
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/degenerate_metrics.csv`, `tests/fixtures/benchmark_nan_window.csv`, `tests/fixtures/junk_columns.csv`, `tests/fixtures/all_nan_column.csv`, `tests/fixtures/real_data_defects.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log` (cmd, rc, stdout, stderr, JSON parse/validity with `allow_nan=False`, key set, value finiteness, determinism, neutrality/shorting checks where applicable).

**Required probe matrix (minimum 12 combos, in-process unless marked CLI):**
1. In-process `BABStrategy.run(REAL, BTC, 252, 0.3, tc=0.001)` → `report()`: all summary metrics finite (`final_cumulative`, `total_return`, `sharpe_ratio`, `annualized_volatility`, `max_drawdown`, `turnover`, `strategy_beta`, `n_observations`), keys present, `report_to_json(report)` valid strict JSON (`allow_nan=False`).
2. Same as (1) on `EXP` default BTC → all metrics finite, strict JSON OK.
3. Same as (1) on `REAL` ETH → `strategy_beta` vs ETH finite, metrics finite.
4. `tear_sheet()` on REAL default → renders without exception, contains "BAB STRATEGY TEAR SHEET", all rendered values finite-formatted.
5. `trade_attribution`/`attribution_totals` on REAL default backtest → all totals finite (`gross_return`, `cost_drag`, `slippage_drag`, `net_return`, `cost_share`, `slippage_share`).
6. `metrics.summary` finiteness sweep: REAL × {tc=0.0, tc=0.001}, degenerate_metrics.csv (zeros) → no non-finite metric, no exception; degenerate never raises.
7. In-process weights dollar-neutral + shorting coverage across quantiles {0.1, 0.3, 0.5} on REAL default → row sums ≈0 (atol=1e-6), negative weights present when short_quantile>0.
8. Position-sizer dict shorthands on REAL default: `{"type":"equal"}`, `{"type":"kelly",...}`, `{"type":"vol_target",...}`, `{"type":"risk_parity",...}` → run completes, weights finite, no BABDataError for recognized types; unknown type → BABDataError clean.
9. `regime_filter=True` vs `False` on REAL default → both run, metrics finite, determinism across two runs identical.
10. `beta_neutral=True` on REAL default → runs, portfolio beta vs benchmark within tolerance of target 0.0, weights finite.
11. CLI: `python -m strategies.betting_against_beta.cli --dry-run --data REAL --from-prices --benchmark BTC` → rc=0, config printed, no file written; `--version` → rc=0 prints version.
12. CLI: `--from-prices` without `--data` → rc=1 clean BABDataError, no Traceback; nonexistent `--data` path → rc=1 clean "File not found", no Traceback.
13. (extra) `--output` to an existing directory via module CLI → rc=1 clean actionable error, no Traceback.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 5) Triage and fix only proven gaps
(same constraints as C17: smallest non-locked-module change, regressions in `tests/test_bab_cli_campaign18*.py`, else record explicit "no proven gaps")

### 6) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 7) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, C18 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence. `cli.py`/`metrics.py` editable only for smallest proven fix from probe evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T16:47Z @ 288f69b)
- Repo state: HEAD `288f69b` on `main`; up-to-date with `origin/main`; no competing handoff files. Untracked: `tests/test_bab_cli_campaign17.py` only (new C17 regressions; not committed).
- Step 0 gates (fresh re-verification at `288f69b`): deps rc=0 (numpy 2.5.4/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0); C11 bundle incl. 11ab + campaign14 **164 passed, rc=0**; `campaign_d` **883 passed, 5 skipped, rc=0**; full BAB excl `data_loader`/`controller` **4740 passed, 35 skipped, rc=0** (floor 4708 maintained; +16 = exactly the new C17 test file).
- C17 EXECUTED AND CLOSED (this session, log `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`):
  (1) module CLI --synthetic --output rc=0, valid finite JSON keys {final_cumulative,periods,benchmark,universe}, periods=252, stderr empty;
  (2) bab-example REAL BTC rc=0 periods=398 cum=0.45632700835934265 stderr empty;
  (3) bab-example EXP BTC rc=0 periods=398 cum=0.5311665101149625;
  (4) bab-example REAL ETH rc=0 benchmark=ETH cum=2.1986969529723432;
  (5) REAL lookback 60 rc=0 finite; (6) REAL quantile 0.2 rc=0 finite;
  (7) determinism byte-identical stdout/JSON across repeats;
  (8)-(10) degenerate_metrics/benchmark_nan_window/real_data_defects → rc=1 clean actionable "Data load/validation failed: ...", no Traceback, no output JSON;
  (11) in-process parity console↔BABStrategy.run equal for REAL default/EXP default/REAL ETH;
  (12) in-process weights dollar-neutral (row sums ≈0 atol=1e-6), negative weights present, 8 assets × 398 rows;
  (13) junk_columns/all_nan_column → rc=1 actionable, no Traceback, no output JSON.
- **No proven gaps.** C17 regression tests added: `tests/test_bab_cli_campaign17.py` (16 passed). No production code changes. C6–C17 closed/evidenced. C18 is the next binding heavy campaign.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C18 — BAB metrics, report, attribution & sizing fidelity on real & defective data (≥12 probe combos).** Execute the matrix in §4 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C18 evidence and nominate **C19** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (never below recorded floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`. `.github/workflows/*` — do not edit. Commit/push only if explicitly requested.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C18 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign (C19).

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
