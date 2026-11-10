# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T15:49:04Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `78a33fe` (`chore(kilo): checkpoint agent session`, `main`; ahead of `origin/main` per local state; working tree clean; `tests/test_bab_cli_campaign16.py` + `HANDOFF.md` committed in this checkpoint)
**Working tree:** clean — no untracked/modified files. No production code changes. No competing handoff files. C16 executed and closed in prior session; gates re-verified fresh at HEAD `78a33fe`.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; 2026-11-10T15:47Z)
- Campaign 14 CLI reporting: **164 passed, rc=0** (`tests/test_bab_cli_campaign11m*.py ... tests/test_bab_cli_campaign14_cli_reporting.py`) — re-verified 2026-11-10T15:47Z
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (2026-11-10T15:47Z)
- Full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`): **4724 passed, 35 skipped, rc=0** (2026-11-10T15:47Z; hard floor 4708 maintained — +16 is exactly the new C16 test file)
- C16 probe evidence log (outside repo): `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; **no blocked or inefficient in-repo sessions identified**. C16 **COMPLETE**: 13 probe combos executed (console + module CLI + in-process parity; REAL/EXP/ETH; lookback/quantile/cost variants; determinism; nested/unwritable/directory --output; defect/NaN/junk fixtures; in-process parity). All success paths rc=0, finite cumulative, periods=398 (REAL/EXP) / 252 (synthetic), stdout non-empty/stderr empty, deterministic; cost monotonicity non-increasing (carried from C15); NaN/defect fixtures fail clean rc=1 with actionable validation error (no Traceback/crash), no partial/corrupt JSON; `--output` to directory → rc=1 clean actionable error; nested/new parent dir → rc=0 file created valid JSON. In-process `BABStrategy.run` parity confirmed equal to console full-float values for REAL default (0.45632700835934265), EXP default (0.5311665101149625), REAL ETH (2.1986969529723432). **No proven gaps for C16** (evidence: log above). Regression tests added in `tests/test_bab_cli_campaign16.py` (16 passed). Proceed directly to C17 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

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

### 3) Execute C17 — BAB strategy core pipeline fidelity on real & defective data (≥12 distinct probe combos, HEAVY)
Goal: verify **core BAB pipeline correctness/robustness** on real and defective data — portfolio weights (dollar-neutral, sum≈0), shorting coverage, turnover, regime/attribution/sizing, backtest determinism, subprocess+in-process parity, metrics/JSON finiteness — across fixtures and parameterizations.
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/all_nan_column.csv`, `tests/fixtures/benchmark_nan_window.csv`, `tests/fixtures/degenerate_metrics.csv`, `tests/fixtures/junk_columns.csv`, `tests/fixtures/real_data_defects.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log` (cmd, rc, stdout, stderr, JSON parse/validity, key set, value finiteness, determinism notes, weight-neutrality/shorting checks).

**Required probe matrix (minimum 12 combos, include subprocess + in-process/API parity where interfaces overlap):**
1. `python -m strategies.betting_against_beta.cli --synthetic --output <tmp.json>` → rc=0, valid finite JSON, keys `{final_cumulative,periods,benchmark,universe}`, `periods>0`, stderr empty.
2. `bab-example REAL --from-prices --benchmark BTC --output <tmp.json>` → rc=0, periods==398, finite `final_cumulative`, stderr empty.
3. `bab-example EXP --from-prices --benchmark BTC --output <tmp.json>` → rc=0, periods==398, finite `final_cumulative`.
4. `bab-example REAL --from-prices --benchmark ETH --output <tmp.json>` → rc=0, JSON `benchmark=="ETH"`, finite metrics.
5. `bab-example REAL --from-prices --benchmark BTC --lookback 60 --output <tmp.json>` → rc=0, finite JSON metrics.
6. `bab-example REAL --from-prices --benchmark BTC --quantile 0.2 --output <tmp.json>` → rc=0, finite JSON metrics.
7. Determinism: run (2) twice to different outputs → JSON `final_cumulative`/`periods` identical, stdout identical.
8. `degenerate_metrics.csv` via bab-example (valid load mode) → clean rc (0 or 1), no Traceback, never emit non-finite JSON when `--output` written.
9. `benchmark_nan_window.csv` via console script → rc=0 or clean rc=1, no Traceback, never emit non-finite JSON when `--output` written.
10. `real_data_defects.csv` via bab-example → clean rc (0 or 1), actionable message/no Traceback; if rc=0 JSON/metrics finite.
11. In-process parity: compare console `--output` JSON `final_cumulative`/`periods` against `BABStrategy.run` for ≥3 combos (REAL default, EXP default, REAL ETH) with matched params.
12. In-process: verify portfolio weights dollar-neutral (sum≈0 within tolerance) and shorting coverage (negative weights present) for REAL default via `BABStrategy.run`/`strategy.weights`.
13. (extra) `junk_columns.csv` / `all_nan_column.csv` error paths → rc=1, actionable error, no Traceback, no output JSON created.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Smallest possible fix confined to non-locked modules (`scripts/load_real_bab_example.py`, `strategies/betting_against_beta/cli.py`, or `strategies/betting_against_beta/metrics.py`/`report.py` only if disproven-by-evidence and fix is minimal/safe — prefer CLI/reporting surface first).
- Add/extend regressions in `tests/test_bab_cli_campaign17*.py` (and targeted metrics/report tests only if clearly warranted by a proven gap).
- No gap → record explicit **"no proven gaps"** with evidence refs in HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 regression bundle (incl. 11ab) + C14, `campaign_d`, and full BAB excl `data_loader`/`controller` (plus any directly impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, completed C17 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence. `cli.py`/`metrics.py` editable only for smallest proven fix from probe evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T15:47:57Z @ dee276e)
- Repo state: HEAD `78a33fe` on `main`; working tree clean; `tests/test_bab_cli_campaign16.py` (16 C16 tests) + `HANDOFF.md` committed in checkpoint `78a33fe`; no competing handoff files.
- Step 0 gates (fresh): deps rc=0 (numpy 2.5.4/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0); C11 bundle **+ C14 164 passed, rc=0**; `campaign_d` **883 passed, 5 skipped, rc=0**; full BAB excl `data_loader`/`controller` **4724 passed, 35 skipped, rc=0** (floor 4708 maintained; +16 = new C16 tests).
- C16 EXECUTED (this session, 13 probes; log `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`): (1) REAL BTC rc=0 periods=398 cum=0.45632700835934265 JSON keys {final_cumulative,periods,benchmark,universe} stderr empty; (2) EXP BTC rc=0 periods=398 cum=0.5311665101149625; (3) REAL ETH rc=0 benchmark=ETH finite; (4) REAL lookback 60 rc=0 finite; (5) REAL quantile 0.2 rc=0 finite; (6) determinism identical stdout/JSON/periods; (7) module CLI --synthetic --output rc=0 valid finite JSON periods=252; (8) --output nested parent dir rc=0 file created valid JSON; (9) --output directory rc=1 clean actionable no Traceback; (10) real_data_defects.csv rc=1 clean "Insufficient finite history..." no Traceback; (11) benchmark_nan_window.csv rc=1 clean "Insufficient rows..." no Traceback; (12) in-process parity console↔BABStrategy.run equal for REAL default/EXP default/REAL ETH; (13) junk_columns/all_nan_column rc=1 actionable no Traceback no output JSON created.
- **No proven gaps.** C16 regression tests added: `tests/test_bab_cli_campaign16.py` (16 passed). No production code changes. C6–C16 closed/evidenced. C17 is the next binding heavy campaign.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C17 — BAB strategy core pipeline fidelity on real & defective data (≥12 probe combos).** Execute the matrix in §3 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C17 evidence and nominate **C18** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (never below recorded floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C17 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
