# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T14:46:40Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `b50a000` (`chore(kilo): checkpoint agent session`, `main`, ahead of `origin/main` per local state; working tree dirty with local `.git/kilo` + this `HANDOFF.md` refresh in this session)
**Working tree:** dirty — `.git/kilo` (runtime/state artifact, do not commit) and `HANDOFF.md` (this refresh). No production code changes. No competing handoff files. C15 executed and closed prior session; gates re-verified fresh this session.

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; 2026-11-10T14:46Z)
- Campaign 14 CLI reporting: **17 passed, rc=0** (`tests/test_bab_cli_campaign14_cli_reporting.py`) — re-verified 2026-11-10T14:46Z
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (2026-11-10T14:46Z)
- Full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`): **4708 passed, 35 skipped, rc=0** (2026-11-10T14:46Z; hard floor 4708 maintained)
- C15 probe evidence log (outside repo): `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; **no blocked or inefficient in-repo sessions identified**. C15 **COMPLETE**: ≥18 probe combos executed (required 1–14 + NaN-column sufficient-data cases + short-history lookback + 4 console↔in-process parity checks with matching params). All success paths rc=0, finite cumulative, periods>0, stdout non-empty/stderr empty, deterministic; cost monotonicity non-increasing on REAL/EXP; NaN fixture `all_nan_column.csv` fails with clean rc=1 actionable validation error (no Traceback/crash) as expected for insufficient valid rows; NaN column inside sufficient returns data handled rc=0/finite. **No proven gaps for C15** (evidence: log above). Proceed directly to C16 heavy work. Treat diagnostics as context, not as permission to revert proven fixes.

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

### 2) Campaigns 6–15 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity, C13 CLI dry-run + JSON output edge cleanliness, C14 CLI reporting fidelity + real-data console-script parity, **C15 BAB end-to-end real-data pipeline parity (≥18 combos, console + in-process, cost monotonicity, alt params, NaN safety, determinism, stdout/stderr)**. Evidence: `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`. Do not churn without a new, statable, reproducible failure.

### 3) Execute C16 — BAB output/reporting schema & metrics fidelity (≥12 distinct probe combos, HEAVY)
Goal: verify end-to-end **reporting/serialization/metrics fidelity** on real-data runs (console script and `strategies.betting_against_beta.cli` where applicable) — JSON output correctness, schema stability, finite/non-NaN/inf handling, stdout/stderr cleanliness, and determinism across repeated runs and equivalent parameterizations.
Fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`, `tests/fixtures/all_nan_column.csv`, `tests/fixtures/benchmark_nan_window.csv`, `tests/fixtures/degenerate_metrics.csv`, `tests/fixtures/junk_columns.csv`, `tests/fixtures/real_data_defects.csv`.
Log: `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log` (cmd, rc, stdout, stderr, JSON parse/validity, key set, value finiteness, determinism notes).

**Required probe matrix (minimum 12 combos, include subprocess + in-process/API parity where interfaces overlap):**
1. `bab-example REAL --from-prices --benchmark BTC --output <tmp.json>` → rc=0, stdout has `cumulative_return=`+`periods=`, stderr empty, JSON parses, keys `{final_cumulative,periods,benchmark,universe}` present, `final_cumulative` finite, `periods==398`.
2. `bab-example EXP --from-prices --benchmark BTC --output <tmp.json>` → rc=0, valid JSON, finite `final_cumulative`, `periods==398`.
3. `bab-example REAL --from-prices --benchmark ETH --output <tmp.json>` → rc=0, JSON `benchmark=="ETH"`, finite metrics.
4. `bab-example REAL --from-prices --benchmark BTC --lookback 60 --output <tmp.json>` → rc=0, finite JSON metrics.
5. `bab-example REAL --from-prices --benchmark BTC --quantile 0.2 --output <tmp.json>` → rc=0, finite JSON metrics.
6. Determinism: run (1) twice to different outputs → JSON `final_cumulative` and `periods` identical, stdout identical.
7. `strategies.betting_against_beta.cli` synthetic/JSON-output path (if supported): `python3 -m strategies.betting_against_beta.cli --synthetic --output <tmp.json>` → rc=0, valid finite JSON, no Traceback, stderr empty.
8. CLI `--output` to nested/new parent dir (writable temp path) → rc=0, file created, valid JSON.
9. Invalid/unwritable `--output` target (directory or unwritable path as feasible) → clean rc!=0 or actionable error, no Traceback, no partial corrupt JSON.
10. Defect fixture `real_data_defects.csv` via `bab-example` (choose valid load mode) → clean rc (0 or 1) with actionable message/no Traceback; if rc=0 JSON/metrics finite.
11. `benchmark_nan_window.csv` or `degenerate_metrics.csv` via console script → rc=0 or clean rc=1, no Traceback, never emit non-finite JSON when `--output` written.
12. In-process parity: compare console `--output` JSON `final_cumulative` (6dp formatted console vs full float JSON as applicable) and `periods` against `BABStrategy.run` for ≥3 representative combos (REAL default, EXP default, REAL ETH) with matched params.
13. (extra) `junk_columns.csv` / `all_nan_column.csv` error paths → rc=1, actionable stderr/stdout error, no Traceback, no output JSON created.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 4) Triage and fix only proven gaps
- Smallest possible fix confined to non-locked modules (`scripts/load_real_bab_example.py`, `strategies/betting_against_beta/cli.py`, or `strategies/betting_against_beta/metrics.py`/`report.py` only if disproven-by-evidence and fix is minimal/safe — prefer CLI/reporting surface first).
- Add/extend regressions in `tests/test_bab_cli_campaign16*.py` (and targeted metrics/report tests only if clearly warranted by a proven gap).
- No gap → record explicit **"no proven gaps"** with evidence refs in HANDOFF.

### 5) Validate comprehensively and record
Rerun: touched/new tests, full C11 regression bundle (incl. 11ab) + C14, `campaign_d`, and full BAB excl `data_loader`/`controller` (plus any directly impacted suites). Record exact counts/rc in HANDOFF.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, completed C16 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign with a concrete ≥12-combo probe plan.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence. `cli.py`/`metrics.py` editable only for smallest proven fix from probe evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T14:46:40Z @ b50a000)
- Repo state: HEAD `b50a000` on `main`; dirty only `.git/kilo` + `HANDOFF.md`; no competing handoff files.
- Step 0 gates (fresh): deps rc=0 (numpy 2.5.4/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0); C14 **17 passed, rc=0**; `campaign_d` **883 passed, 5 skipped, rc=0**; full BAB excl `data_loader`/`controller` **4708 passed, 35 skipped, rc=0**.
- C15 EXECUTED (prior session, ≥18 probes; log `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`): (1)(2) in-process `load_returns` REAL/EXP BTC rc=0 finite cum periods=398; (3)(4) console `bab-example` REAL/EXP `--from-prices` rc=0 clean stdout/stderr; (5)(6) cost monotonicity tc 0/0.001/0.005 non-increasing on REAL `[0.472126,0.456327,0.398083]` and EXP `[0.585443,0.531167,0.359523]`; (7) alt benchmark ETH rc=0 finite; (8)(9) lookback 60/120 rc=0 finite; (10)(11) quantile 0.2/0.5 rc=0 finite; (12) `all_nan_column.csv` rc=1 clean actionable "Insufficient rows..." no Traceback; (12b/c) NaN column in sufficient returns data console+in-process rc=0 finite; (13) stdout non-empty/stderr empty; (14) determinism identical stdout; extra lookback 500 rc=0 finite; parity console↔in-process with matched params (`--lookback 252 --quantile q --transaction-cost 0.001`) confirmed equal to full-float values (console prints 6dp) for REAL default, EXP default, REAL ETH, REAL q0.2.
- **No proven gaps.** No production code changes. C6–C15 closed/evidenced. C16 is the next binding heavy campaign.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C16 — BAB output/reporting schema & metrics fidelity (≥12 probe combos).** Execute the matrix in §3 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C16 evidence and nominate **C17** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (never below recorded floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C16 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*