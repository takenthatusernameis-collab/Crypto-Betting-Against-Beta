# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T18:14:41Z (active handoff for next session); prior sessions 2026-11-10T17:53:28Z / 17:17:56Z / 17:18:00Z, source handoff 2026-11-10T16:02:41Z retained for provenance
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `27a36fa` (`chore(kilo): checkpoint agent session`, `main`; up-to-date with `origin/main`; prior checkpoint `288f69b` only refreshed this HANDOFF, so recorded gates below remain valid)
**Working tree:** clean; `tests/test_bab_cli_campaign17.py` (new C17 regressions, 16 passed, committed in a6f025f) and `tests/test_bab_cli_campaign18.py` (new C18 regressions, 24 passed, committed in 185f1fa) both tracked. No production code changes. No competing handoff files. C16/C17/C18 executed and closed; all gates re-verified fresh this session at `288f69b` (unchanged by `27a36fa`).

**Environment/gates (rerun fresh this session before any production edit; recorded below):**
- deps: `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0 (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; re-verified 2026-11-10T17:53Z)
- Campaign 14 CLI reporting: **17 passed, rc=0** (`tests/test_bab_cli_campaign14_cli_reporting.py`) — re-verified this session (164 passed total incl. C11 bundle 11m/n/o/p/q/s/11ab + 14, rc=0)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** — re-verified this session
- Full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`): **4764 passed, 35 skipped, rc=0** — re-verified this session (hard floor 4708 maintained; +40 = new C17 16 + new C18 24 test files).
- C16 probe evidence log: `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`
- C17 probe evidence log: `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`
- C18 probe evidence log: `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log` (15 probes, 0 failures)
- **C19 probe evidence log does NOT exist yet** — C19 is unexecuted and is the binding next campaign.

**Bottlenecks removed/notes:** single durable handoff kept current and unambiguous; no stale/competing handoff files; **no blocked or inefficient in-repo sessions identified**. Stale HEAD reference (`288f69b`) corrected to `27a36fa`; inaccurate "NOT committed" note for C18 corrected (committed in 185f1fa). C16 **COMPLETE** (13 probe combos; no proven gaps; regressions in `tests/test_bab_cli_campaign16.py`, 16 passed). C17 **COMPLETE**: 13 matrix subprocess combos + in-process parity ×3 + weights neutrality/shorting + defective-fixture error paths, all rc=0 or clean rc=1, no Traceback, no non-finite/corrupt JSON, stdout non-empty/stderr empty on success paths. REAL default cum=0.45632700835934265 periods=398; EXP default cum=0.5311665101149625 periods=398; REAL ETH cum=2.1986969529723432 periods=398 — bit-identical to C16/C15 values, no regression. Determinism: repeat runs byte-identical stdout/JSON. In-process `BABStrategy.run` parity equal to console full-float values for REAL default/EXP default/REAL ETH. Weights dollar-neutral (row sums ≈0, atol=1e-6) with negative (short) weights present, 8 assets × 398 rows. Defective fixtures (`degenerate_metrics.csv`, `benchmark_nan_window.csv`, `real_data_defects.csv`, `junk_columns.csv`, `all_nan_column.csv`) → rc=1, actionable "Data load/validation failed: ..." messages, no Traceback, no output JSON created. **No proven gaps for C17** (evidence: c17 log above). Regression tests added in `tests/test_bab_cli_campaign17.py` (16 passed). No production code touched. C18 **COMPLETE**: 15 probe combos (in-process report()/tear_sheet()/report_to_json() metric finiteness + strict JSON; tear_sheet rendering; attribution_totals finiteness; metrics.summary finiteness sweep REAL×{tc=0.0,0.001}+degenerate never-raises; dollar-neutral + shorting across quantiles {0.1,0.3,0.5}; position-sizer dict shorthands equal/kelly/vol_target/risk_parity + unknown→BABDataError; regime_filter True vs False finite + deterministic; beta_neutral=True runs with finite dollar-neutral weights; CLI --dry-run rc=0 + --version rc=0; CLI --from-prices w/o --data rc=1 clean + nonexistent --data rc=1 clean; CLI --output to existing dir rc=1 clean; report_to_json strict JSON + key set + metrics/totals finite; report determinism x2). Parity values bit-identical to C16/C17. **No proven gaps for C18**. Regression tests locked in `tests/test_bab_cli_campaign18.py` (24 passed). No production code touched. C6–C18 closed/evidenced. **C19 is the next binding heavy campaign and has not been executed.**

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

### 2) Campaigns 6–18 remain CLOSED (evidence-backed, no churn)
C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity, C13 CLI dry-run + JSON output edge cleanliness, C14 CLI reporting fidelity + real-data console-script parity, C15 BAB end-to-end real-data pipeline parity (≥18 combos), **C16 BAB output/reporting schema & metrics fidelity (13 combos, no proven gaps, regressions in tests/test_bab_cli_campaign16.py)**. **C17 BAB strategy core fidelity (13 combos, no proven gaps, regressions in tests/test_bab_cli_campaign17.py)**. **C18 BAB metrics/report/attribution/sizing/regime/beta-neutral/CLI fidelity (15 combos, no proven gaps, regressions in tests/test_bab_cli_campaign18.py)**. Evidence: C15 log `/home/runner/work/_temp/kilo-tmp/c15_bab_pipeline_parity_probe_evidence.log`; C16 log `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`; C17 log `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`; C18 log `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log`. Do not churn without a new, statable, reproducible failure.

### 3) Campaign 17 — CLOSED (evidence-backed, no churn)
C17 **COMPLETE and closed** (2026-11-10T16:47Z @ HEAD `288f69b`). Evidence log `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`; regressions locked in `tests/test_bab_cli_campaign17.py` (16 passed). No proven gaps — do not churn without a new, statable, reproducible failure.
### 4) Campaign 18 — CLOSED (evidence-backed, no churn)
C18 **COMPLETE and closed** (2026-11-10T17:18Z @ HEAD `288f69b`). Evidence log `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log`; 15 probes, 0 failures, no proven gaps. Regression tests locked in `tests/test_bab_cli_campaign18.py` (24 passed). No production code touched. Parity values bit-identical to C16/C17 (REAL default cum=0.45632700835934265, EXP default cum=0.5311665101149625, REAL ETH cum=2.1986969529723432). Do not churn without a new, statable, reproducible failure.

### 5) Execute C19 — BAB config-validation edges, cost/slippage monotonic drag, universe/rebalance/shorting/sizing robustness on real & defective data (≥12 distinct probe combos, HEAVY)
Goal: verify **BAB configuration robustness and cost/slippage/position-sizing fidelity** — `BABConfig` validation errors (clean `BABConfigError`, no Traceback), transaction-cost monotonic drag across cost levels, slippage application, explicit-universe override rejection (no overlap), rebalance freq (weekly/monthly vs daily), shorting constraints, max_position_size bounding, and CLI `--output` strict-JSON schema on real & defective data. Fixtures: `REAL` (`tests/fixtures/real_market_prices.csv`), `EXP` (`tests/fixtures/real_market_prices_expanded.csv`), `degenerate_metrics.csv`, `junk_columns.csv`, `all_nan_column.csv`. Log: `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log` (cmd, rc, stdout, stderr, JSON validity/finiteness with `allow_nan=False`, key sets, determinism, neutrality/shorting/bounds checks where applicable).

**Required probe matrix (minimum 12 combos, in-process unless marked CLI):**
1. `BABConfig(beta_window=0)` → `BABConfigError` clean, no Traceback.
2. `BABConfig(long_quantile=0.0)` and `long_quantile=1.0` → `BABConfigError` clean (must be in (0,1)).
3. `BABConfig(short_quantile=0.0)` → `BABConfigError` clean.
4. `BABConfig(transaction_costs=-0.001)` → `BABConfigError` clean.
5. `BABConfig(vol_thresholds=[...], vol_percentiles=[...])` both set → `BABConfigError` clean ("set only one").
6. Cost monotonic drag: REAL default × `tc` ∈ {0.0, 0.0005, 0.001, 0.005} → `final_cumulative` non-increasing as `tc` rises; all metrics finite, strict JSON OK.
7. Slippage application: REAL default × `slippage` ∈ {0.0, 0.001} → `slippage_drag` > 0 when slippage>0, all finite, net_return = gross − cost − slippage.
8. Explicit universe override with no data overlap → `BABConfigError` clean (e.g. universe=["ZZZ","YYY"] on REAL).
9. Rebalance freq `weekly` vs `monthly` vs `daily` on REAL default → all run, metrics finite, weights dollar-neutral; determinism across two runs identical per freq.
10. Shorting constraints dict on REAL default → runs, weights finite, dollar-neutral, shorting present.
11. `max_position_size=0.2` on REAL default → runs, all |weights| ≤ ~0.2 + tolerance, weights finite.
12. CLI: `python -m strategies.betting_against_beta.cli --data REAL --from-prices --benchmark BTC --output <tmp>/out.json` → rc=0, valid strict JSON, keys {final_cumulative,periods,benchmark,universe}, periods=398, stderr empty.
13. CLI: `--output` to a nonexistent nested directory via module CLI → rc=0 (parents created), valid JSON written.
14. CLI: `--dry-run --output <existing-dir>` → rc=1 clean "is a directory" error, no Traceback.
15. (extra) CLI determinism: two identical REAL `--from-prices --output` runs → byte-identical stdout/JSON.

Add more combos if behavior is ambiguous; do not stop at 12 when anomalies appear.

### 6) Triage and fix only proven gaps
(same constraints as C18: smallest non-locked-module change, regressions in `tests/test_bab_cli_campaign19*.py`, else record explicit "no proven gaps")

### 7) Validate comprehensively and record
Rerun: touched/new tests, full C11 bundle + C14, `campaign_d`, full BAB excl `data_loader`/`controller` (+ impacted suites). Record exact counts/rc in HANDOFF.

### 8) Refresh HANDOFF before finishing (MANDATORY)
Update timestamp/HEAD/state, C19 evidence (log path, combo summary, parity notes), gate results, touched modules, and the next binding heavy campaign (C20) with a concrete ≥12-combo probe plan. No generic "continue" handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by new evidence. `cli.py`/`metrics.py` editable only for smallest proven fix from probe evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T18:14:41Z @ 27a36fa)
- Repo state: HEAD `27a36fa` on `main`; up-to-date with `origin/main`; no competing handoff files. Working tree clean; C17/C18 regression test files committed. No production code changes.
- Step 0 gates (fresh re-verification at `288f69b`, unchanged by `27a36fa`): deps rc=0 (numpy 2.5.4/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0); C11 bundle incl. 11ab + campaign14 **164 passed, rc=0**; `campaign_d` **883 passed, 5 skipped, rc=0**; full BAB excl `data_loader`/`controller` **4764 passed, 35 skipped, rc=0** (floor 4708 maintained; +40 = new C17 16 + new C18 24 test files).
- C16/C17/C18 EXECUTED AND CLOSED: C16 log `/home/runner/work/_temp/kilo-tmp/c16_bab_reporting_metrics_probe_evidence.log`; C17 log `/home/runner/work/_temp/kilo-tmp/c17_bab_strategy_core_fidelity_probe_evidence.log`; C18 log `/home/runner/work/_temp/kilo-tmp/c18_bab_metrics_report_attribution_fidelity_probe_evidence.log` (15 probes, 0 failures). Parity values bit-identical across C16/C17/C18 (REAL default cum=0.45632700835934265, EXP default cum=0.5311665101149625, REAL ETH cum=2.1986969529723432). **No proven gaps for C16/C17/C18**. Regression tests: C17 16 passed, C18 24 passed. C6–C18 closed/evidenced. **C19 is the next binding heavy campaign and has NOT been executed (no c19 probe log exists).**

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C19 — BAB config-validation edges, cost/slippage monotonic drag, universe/rebalance/shorting/sizing robustness on real & defective data (≥12 probe combos).** Execute the matrix in §5 with subprocess + in-process evidence to `/home/runner/work/_temp/kilo-tmp/c19_bab_config_cost_slippage_sizing_fidelity_probe_evidence.log`. Triage/fix only proven gaps (smallest non-locked-module change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C19 evidence and nominate **C20** with a concrete ≥12-combo probe plan — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4708 passed, 35 skipped** (current recorded 4764, never below floor without investigation); campaign11 bundle incl. 11ab + campaign14 **≥164 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`. `.github/workflows/*` — do not edit. Commit/push only if explicitly requested.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record (already green: deps rc=0; C11+C14 164 passed; campaign_d 883 passed/5 skipped; full BAB excl data_loader/controller 4764 passed/35 skipped). 2) EXECUTE C19 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS `HANDOFF.md` with evidence and next binding campaign (C20).

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
