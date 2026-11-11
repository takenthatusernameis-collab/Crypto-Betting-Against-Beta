# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:15:00Z
**HEAD:** `cc7704d` (`chore(kilo): checkpoint agent session`), branch `main`, worktree clean
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**Working tree at refresh:** uncommitted artifacts only expected in `_temp/kilo-tmp` and this `HANDOFF.md`; no tracked product code modified this session; no competing durable handoff files remain (`.kilo/handoff.md` not present). No commit/push.

## Bottleneck removal status (this session)
- **Single durable handoff enforced:** only `HANDOFF.md` maintained; no competing handoff sources found.
- **Long gate execution bottleneck RESOLVED:** campaign11+14 and full-BAB-excl were re-run this session and returned green with exact counts/rc (see Step 0 below). No longer "pending reconfirmation."
- **No blocking runtime/env bottlenecks found:** deps importable, CLI/scripts runnable, fixtures present, tests runnable. Historical CI diagnostics in `research_state/workflow_run_diagnostics.jsonl` not reproduced locally on `main`.
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
  - Prior review items (C01 parity, C04 stale/frozen constant-series contract, C09 beta-neutral tolerance/semantics) re-checked in C27 with canonical probes: **no proven product gaps**.
- **C27:** attribution/sizing/shorting/reporting stress — **0 proven gaps fixed**, **0 regressions added**. Review carried (not proven): C06 `beta_neutral=True` ex-post `strategy_beta(...)` returns `nan` under current call/series alignment — requires canonical apples-to-apples semantic/tolerance spec before any change.
- **Do not churn C6–C27** without a new, statable, reproducible failure with probe evidence.

## Step 0 baseline/gates (re-run and recorded this session)

**Re-run this session (recorded):**
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0** (`deps_ok`) ✅
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (10.09s) ✅
- campaign11 bundle + campaign14 (`tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py`) → **164 passed, rc=0** (194.89s) ✅ **RE-CONFIRMED** (prior recorded ≥164, rc=0)
- full BAB excl `data_loader`/`controller` (`tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*`) → **4782 passed, 35 skipped, 231 warnings, rc=0** (506.15s) ✅ **RE-CONFIRMED** (prior recorded ≥4782 passed, 35 skipped, rc=0)

**No modules/tests edited this session; no regressions introduced by this session's changes.**

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

### 3) EXECUTE C28 — end-to-end reproducibility, config/CLI-API contract closure & reporting fidelity hardening (≥12 combos, HEAVY) — BINDING (IN-FLIGHT, NOT YET EXECUTED THIS SESSION)
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

---

## NEXT BINDING HEAVY CAMPAIGN — C29 (prepare after C28 closes)
**C29 — Real-data E2E pipeline hardening, attribution×sizing×shorting interaction stress, adversarial defect-fixture contract closure, and perf/regression gate parity (≥12 combos, HEAVY):**
1. **Real-fixture E2E determinism:** `real_market_prices.csv` + `real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices`→`BABStrategy(...).run()` — 3× each, byte/strict-JSON identical, rc=0.
2. **Attribution×sizing×shorting interaction matrix:** all sizing modes (`equal`,`kelly`,`vol_target`,`risk_parity`) × shorting constraints (`max_short_weight` 0.2/0.5/1.0) × attribution on/off — finite weights/cumulatives, no Traceback, 2× deterministic.
3. **Regime filter × costs × slippage × rebalance-freq full factorial** on real fixture — finite, deterministic per combo, `allow_nan=False`.
4. **Adversarial defect-fixture contract:** `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv` per load/CLI path — clean rc/errors vs accepted behavior per contract, no silent corruption, no partial output.
5. **Quality gate edge branches:** constant/flat/insufficient-history series — flat zero-weight periods, finite, no NaN/Inf/Traceback.
6. **CLI script surface hardening:** `bab_backtest_report.py` and `load_real_bab_example.py` with missing/invalid `--data-source`, `--data`, nested `--output`, overwrite — clean actionable errors, rc contract stable, no Traceback.
7. **Nonfinite serialization guard:** CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens emitted.
8. **Dry-run side-effect absence:** `--dry-run` produces no files, no output writes, stable rc/messages across valid/invalid inputs.
9. **Performance/regression gate parity:** re-run Step 0 gates after any edit — counts must not regress below floors (`campaign_d` ≥883/5/0; full BAB ≥4782/35/0; campaign11+14 ≥164/0).
10. **Output-path edge matrix:** existing-dir target, nested non-existent dir create, overwrite-existing-file — clean rc, no corrupt partial output, overwrite-safe.
11. **Config-API equivalence on real fixture:** every CLI knob has an equivalent BABStrategy/BABConfig kwarg producing identical final cumulative (≤1e-12) — parity log.
12. **Determinism under concurrent/repeated invocation:** same CLI invoked 3× in quick succession — identical strict JSON outputs, no file-lock/corruption issues.
**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
**Regression file:** `tests/test_bab_cli_campaign29*.py` for every proven fix; if none, record explicit "no proven gaps" with evidence refs.

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

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C28 (in-flight) then C29 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
