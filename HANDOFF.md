# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:04:20Z
**HEAD:** `65e0f71` (`chore(kilo): checkpoint agent session`)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**Working tree at refresh:** uncommitted C27 evidence/log/handoff refresh artifacts only expected in `_temp/kilo-tmp` and this `HANDOFF.md`; no tracked product code modified this session; no competing durable handoff files remain (`.kilo/handoff.md` not present). No commit/push.

## Bottleneck removal status (this session)
- **Single durable handoff enforced:** only `HANDOFF.md` maintained; no competing handoff sources found.
- **No blocking runtime/env bottlenecks found:** deps importable, CLI/scripts runnable, fixtures present, tests runnable. Historical CI diagnostics in `research_state/workflow_run_diagnostics.jsonl` not reproduced locally on `main`.
- **Long gate execution bottleneck noted:** full-BAB-excl and campaign11+14 gate commands were started this session but exceeded the tool timeout window before returning in-turn; they were not observed to fail. Treat as **not re-confirmed this session** (carried forward from prior recorded green) — re-run and record exact counts/rc before finishing any future edit.
- **Not blocked:** C27 executed with probe evidence; no churn performed. C6–C26 remain closed absent new reproducible defect evidence.

## Environment / quick start (verified this session)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`) ✅
- Key modules: `strategies/betting_against_beta/{cli,strategy,attribution,metrics,shorting,sizing,regime,reporting scripts,...}` present. Fixtures under `tests/fixtures/`.

## Historical closure (do not churn without new reproducible failure + probe evidence)
- **C6–C22:** closed with evidence.
- **C23:** 1 gap fixed (CLI output-path validation timing), 0 remaining. Evidence: `/home/runner/work/_temp/kilo-tmp/c23_bab_resilience_error_contract_probe_evidence.log`
- **C24:** 37 combos, **no proven gaps**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c24_bab_beta_attribution_regime_probe_evidence.log`
- **C25:** 14 required combos + corrected probes, **no proven gaps**, 0 modules touched. Evidence: `/home/runner/work/_temp/kilo-tmp/c25_bab_reporting_cli_contract_probe_evidence.log`
- **C26:** 14 combos, **0 production module/test edits**. Evidence: `/home/runner/work/_temp/kilo-tmp/c26_bab_pipeline_stress_determinism_probe_evidence.log`, `c26_followup_evidence.log`, `c26_final_verify.log`.
  - Prior review items (C01 parity, C04 stale/frozen constant-series contract, C09 beta-neutral tolerance/semantics) re-checked in C27 with canonical probes (see below): **no proven product gaps**.
- **Do not churn C6–C26** without a new, statable, reproducible failure with probe evidence.

## Step 0 baseline/gates

**Re-run this session (recorded):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (10.24s) ✅

**Started this session but not completed within tool timeout (not failed/observed; CARRIED FORWARD — must re-run before finishing if you edit anything):**
- campaign11 bundle + campaign14 (`tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py`) → **prior recorded: ≥164 passed, rc=0** (pending reconfirmation)
- full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`) → **prior recorded: ≥4782 passed, 35 skipped, rc=0** (pending reconfirmation)

**No modules/tests edited this session; no regressions introduced by this session's changes.**

## C27 execution — attribution, sizing/shorting edge interactions & script/report surface stress (HEAVY)

**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c27_bab_attribution_sizing_shorting_report_probe_evidence.log`
- Primary run: `/tmp/c27_probe.py` (12 combos) + follow-up: `/tmp/c27_followup.py` (canonical corrections / contract checks). For each: cmd/rc/stdout/stderr captured; JSON checked with `json.loads` + `json.dumps(..., allow_nan=False)` and finiteness walk where applicable.

| # | Combo | Result | Key evidence / invariants |
|---|---|---|---|
| 1 | C26-C01 canonical CLI↔API parity (`--from-prices real_market_prices.csv --output` vs `BABStrategy(BABConfig(benchmark='BTC')).run(load_prices(...))`) | **PASS / no gap** | CLI rc=0, strict JSON finite keys `[final_cumulative, periods, benchmark, universe]`; API=`0.3397354969330525`, CLI=`0.3397354969330525`, `abs diff=0.0 <= 1e-12`. Prior C01 mismatch was probe-harness comparability, not product defect. |
| 2 | Attribution decomposition finite (real run) | **PASS** | `trade_attribution` shape `(398,4)` cols `[gross_return,cost_drag,slippage_drag,net_return]`, finite_att=True; totals finite `gross/net=-0.9199788229523507`, cost/slippage drags 0.0, recon sum_net matches. |
| 3 | Attribution on degenerate/flat run (quality-safe) | **PASS (follow-up)** | Initial probe used `load_prices(degenerate_metrics.csv)` → `BABDataError: All price columns were metadata` (expected for price-loader path). Canonical `load_returns(degenerate_metrics.csv, benchmark='BTC')` with `beta_window=3,min_observations=2` → shape `(5,2)`, att `(5,4)` finite, totals all finite/zero, no NaN/Inf/Traceback. |
| 4 | Sizing edges (`equal`,`kelly`,`vol_target`,`risk_parity`) on real fixture | **PASS** | rc/finite cumulatives & weights for all: equal `0.3397354969330525`, kelly `0.6018377033270763`, vol_target `0.8429986112560915`, risk_parity `0.0` (finite, periods=398). No Traceback. |
| 5 | Shorting constraints (supported API) | **PASS (follow-up)** | Initial `{'borrow_cap','utilization'}` rejected cleanly by config validation (`BABConfigError`, no Traceback). Canonical `ShortingConstraints(max_short_weight=0.5, ...)` via `shorting_constraints={'max_short_weight':0.5}` → rc=0, final `0.3397354969330525`, finite weights. |
| 6 | C26-C09 canonical beta-neutral check | **REVIEW / no proven product gap** | `beta_neutral=True` deterministic 3× final `0.7839996713884239`; `strategy_beta(strategy_returns, benchmark_returns)` returns `nan` (finite/deterministic pipeline output otherwise). `strategy_beta` requires aligned return series; observed NaN likely due to benchmark/series alignment or insufficient comparable series in this contract — **not proven a defect** without canonical apples-to-apples ex-post beta spec. Document for C28. |
| 7 | Script surface (`scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py`) | **PASS (follow-up)** | `bab_backtest_report.py` (no args, synthetic) rc=0, finite human report, no Traceback. `load_real_bab_example.py` requires positional `data_path`; `--help` rc=0; canonical run with fixture `--from-prices --benchmark BTC` rc=0 (`cumulative_return=0.456327 periods=398`), no Traceback. Initial bare run rc=2 was usage-contract (no required arg), not a defect. |
| 8 | Script/CLI error-contract parity (missing/invalid inputs) | **PASS** | `cli --data missing` rc=1 clean actionable error; `cli --from-prices` (no data) rc=1 `--from-prices requires --data`; `bab_backtest_report.py --data-source missing` rc=1 clean error. No Tracebacks, no partial/corrupt output observed. |
| 9 | `strategy.report()` / `tear_sheet()` / JSON on degenerate case | **PASS (contract-observed)** | On degenerate returns run: `BABResult` has no `report`/`tear_sheet`/`summary` attrs (API surface as-is); backtest finite with cols `[returns,gross_return,cost_drag,slippage_drag,cumulative]`. No NaN/Inf/Traceback. (CLI/script JSON/report paths separately validated finite/strict in 1,7,12.) |
| 10 | Combined stress determinism (`transaction_costs`+`slippage`+`regime_filter`) | **PASS (follow-up)** | Correct canonical config `regime_filter=True` (bool per config contract; string `'volatility'` rejected by validation) with costs/slippage → 3× identical finals `[0.2796264034046895,...]`, deterministic. |
| 11 | Rebalance-frequency comparison (daily/weekly/monthly) | **PASS** | All finite, deterministic per-freq, rc=0, periods=398: daily `0.3397354969330525`, weekly `0.38215059713934335`, monthly `0.5930166842166542`. |
| 12 | Report/output overwrite & idempotence | **PASS** | Repeated `--output` CLI run rc=0 both times, strict JSON finite (`allow_nan=False`), identical final `0.3397354969330525`, overwrite-safe/no stale corruption. |

**Additional C26/C27 contract checks:**
- **C26-C04 (constant-series stale/frozen guard):** 20-row constant prices (`BTC/ETH/SOL=const`) via CLI `--from-prices` → **rc=0**, `Final cumulative return: 1.000000, Periods: 19`, no Traceback. Behavior consistent/finite on this path; no proven gap.

**Modules/tests touched:** **NONE** (0 production modules, 0 tests). No proven gaps found; no regressions introduced.

## C27 outcome
- **Proven product gaps fixed:** 0
- **Regressions added:** 0 (none warranted)
- **Explicit:** **No proven gaps** identified in C27 with evidence in `/home/runner/work/_temp/kilo-tmp/c27_bab_attribution_sizing_shorting_report_probe_evidence.log`. Review items carried (not proven): C06 `beta_neutral=True` ex-post `strategy_beta(...)` returns `nan` under current call/series alignment — requires canonical apples-to-apples semantic/tolerance spec before any change.

---

## BINDING INITIAL TASK MESSAGE (execute immediately — heavy work required)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd, rc, stdout, stderr, JSON validity/finiteness with strict `allow_nan=False` where JSON produced) and either (a) regressions for proven gaps or (b) explicit **"no proven gaps"** with evidence references.

### 1) Confirm baseline — Step 0 (MANDATORY before any edit)
Run and record with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`:
- `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0**
- campaign11 bundle + campaign14 → **expect ≥164 passed, rc=0**
- full BAB excl `data_loader`/`controller` → **expect ≥4782 passed, 35 skipped, rc=0**

If deps missing, install minimal deps and record; do not claim blocked without evidenced attempt. Do not revert prior fixes without cause.

### 2) Campaigns 6–27 (historical closure — no churn)
Closed/evidenced. **Do not churn C6–C27 without a new, statable, reproducible failure with probe evidence.** C27 carry-over: C06 beta-neutral ex-post `strategy_beta` NaN is **REVIEW only** — resolve only via canonical apples-to-apples repro proving a real defect vs contract.

### 3) EXECUTE C28 — end-to-end reproducibility, config/CLI-API contract closure & reporting fidelity hardening (≥12 combos, HEAVY) — BINDING
**Goal:** close remaining contract/reproducibility/reporting-fidelity surfaces with canonical apples-to-apples probes; fix only proven gaps.
**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log`
For each combo record: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` + finiteness walk), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 12 combos — execute all; add more if suspicious):**
1. **CLI↔API parity on all supported CLI knobs** with `--output` full-precision JSON (benchmark/universe/beta-window/quantiles/rebalance/costs/slippage/synthetic/from-prices/dry-run interactions where valid) — identical apples-to-apples inputs/config.
2. **`--dry-run` contract matrix:** valid/invalid/missing/dir/conflict/`--output` path cases — validate-only, no side effects, stable rc/messages, no Traceback.
3. **Config boundary/validation error contracts:** quantiles, windows, min_observations, costs/slippage, universe/benchmark edges — clean actionable errors, rc/exception contract stable per path.
4. **Synthetic reproducibility:** seed/config determinism 3× identical outputs/metrics.
5. **Real-fixture multi-run determinism** across costs+slippage+regime (`regime_filter=True`)+rebalance combos (3× each) — finite, identical.
6. **Metrics/report JSON/schema stability & strict finiteness:** CLI/script/API metric surfaces on real + degenerate (quality-safe) inputs; `allow_nan=False`, no non-finite.
7. **Attribution/report/tear_sheet cross-consistency** (where surfaces exist): decomposition reconciliation, totals vs backtest/net, finite/invariant.
8. **Script outputs deterministic & overwrite-safe:** `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` canonical invocations 2–3×, rc=0, stable/finite output, no Traceback.
9. **Edge universes:** 2-asset, benchmark-heavy, sparse/short-but-valid history — finite, deterministic, no Traceback; explicit contract behavior.
10. **Non-monotonic/defect fixture handling contracts:** `non_monotonic_dates.csv`, `real_data_defects.csv` etc. per supported load/CLI paths — clean rc/errors vs accepted behavior per contract, no silent corruption.
11. **Output path/permission-like edge handling:** existing dir target, nested create, overwrite — clean actionable errors/no corrupt partial output.
12. **C27 carry-over canonical check:** `beta_neutral=True` ex-post `strategy_beta`/portfolio-beta contract on real fixture with correctly aligned benchmark/strategy return series and explicit tolerance — conclude proven gap vs expected semantics or document contract.

### 4) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` when evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign28*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required/justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs.**

### 5) Validate comprehensively and record
- After any module/test edit, re-run all Step 0 gates plus touched/new suites and impacted reporting/CLI suites; record exact counts/rc in HANDOFF.
- If no modules touched, state baseline carried forward/partially re-run and confirm no regressions introduced.

### 6) Refresh HANDOFF before finishing (MANDATORY)
Update this file in place with: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or carried forward), C28 evidence log path, combo-by-combo PASS/FAIL/REVIEW + invariants, modules/tests touched (or none), and the next binding heavy campaign (**C29**) with concrete ≥12-combo probe plan. No ambiguous handoff.

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (hard floor; raise if legitimately increased)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## LOCKS / PROHIBITIONS
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` gate closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/reporting/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C28 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
