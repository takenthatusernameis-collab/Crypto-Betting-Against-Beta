# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:22:41Z
**HEAD:** `f501210` (`chore(kilo): checkpoint agent session`), branch `main`, worktree clean (no tracked product code modified this session)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**Durable handoff:** this file only (`.kilo/handoff.md` absent). No commit/push performed.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST DO HEAVY WORK NOW (C28, IN-FLIGHT)

**YOU MUST DO HEAVY WORK. No planning-only exits. No single-pass probes. No evidence-free exits.** Execute Campaign 28 end-to-end before finishing; produce probe evidence and either (a) regressions for proven gaps or (b) explicit "no proven gaps" with evidence refs. Do not declare "blocked" without an evidenced attempt. Do not churn C6–C27 without a new, statable, reproducible failure with probe evidence.

### 0) Environment / mandatory preflight (record)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0 expected** (verified available 2026-11-11T11:22Z)
- C28 evidence log (MANDATORY, create/populate): `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (**MISSING as of 2026-11-11T11:22Z** — must be produced)

### 1) Step 0 baseline gates (MANDATORY before any edit; run and record exact counts/rc)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **expect ≥883 passed, 5 skipped, rc=0** (last recorded 2026-11-11T11:15Z: 883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0)
- campaign11 bundle + campaign14: `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **expect ≥164 passed, rc=0** (last recorded: 164 passed, rc=0, 194.89s)
- full BAB excl `data_loader`/`controller`: `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **expect ≥4782 passed, 35 skipped, rc=0** (last recorded: 4782 passed, 35 skipped, 231 warnings, rc=0, 506.15s)

If any gate regresses, stop feature work, diagnose with probe evidence, and fix the smallest proven cause before proceeding. Do not revert prior fixes without cause.

### 2) EXECUTE C28 — end-to-end reproducibility, config/CLI-API contract closure & reporting fidelity hardening (≥12 combos, HEAVY)
For **each** combo record in the evidence log: cmd, rc, stdout, stderr, JSON validity/finiteness (strict `allow_nan=False` + finiteness walk where JSON produced), key sets, determinism/parity/invariant notes.

**Required probe matrix (minimum 12 — execute all; add more if suspicious):**
1. **CLI↔API parity on all supported CLI knobs** with `--output` full-precision JSON (benchmark/universe/beta-window/quantiles/rebalance/costs/slippage/synthetic/from-prices/dry-run interactions where valid) — identical apples-to-apples inputs/config.
2. **`--dry-run` contract matrix:** valid/invalid/missing/dir/conflict/`--output` path cases — validate-only, no side effects, stable rc/messages, no Traceback.
3. **Config boundary/validation error contracts:** quantiles, windows, min_observations, costs/slippage, universe/benchmark edges — clean actionable errors, rc/exception contract stable per path.
4. **Synthetic reproducibility:** seed/config determinism 3× identical outputs/metrics.
5. **Real-fixture multi-run determinism** across costs+slippage+regime (`regime_filter=True`)+rebalance combos (3× each) — finite, identical.
6. **Metrics/report JSON/schema stability & strict finiteness:** CLI/script/API metric surfaces on real + degenerate (quality-safe) inputs; `allow_nan=False`, no non-finite.
7. **Attribution/report/tear_sheet cross-consistency** (where surfaces exist): decomposition reconciliation, totals vs backtest/net, finite/invariant.
8. **Script outputs deterministic & overwrite-safe:** `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` canonical invocations 2–3×, rc=0, stable/finite output, no Traceback.
9. **Edge universes:** 2-asset, benchmark-heavy, sparse/short-but-valid history — finite, deterministic, no Traceback; explicit contract behavior.
10. **Non-monotonic/defect fixture handling contracts:** `tests/fixtures/non_monotonic_dates.csv`, `tests/fixtures/real_data_defects.csv` etc. per supported load/CLI paths — clean rc/errors vs accepted behavior per contract, no silent corruption.
11. **Output path/permission-like edge handling:** existing dir target, nested create, overwrite — clean actionable errors/no corrupt partial output.
12. **C27 carry-over canonical check:** `beta_neutral=True` ex-post `strategy_beta`/portfolio-beta contract on real fixture with correctly aligned benchmark/strategy return series and explicit tolerance — conclude proven gap vs expected semantics or document contract.

### 3) Triage and fix only proven gaps
- Fix only statable, reproducible incorrectness (silent corruption, wrong parity/JSON/metrics/reporting, unexpected non-finite, incorrect rc/error contract, Traceback on user paths, side effects).
- **Smallest non-locked module(s) only**; prefer `cli.py`/`metrics.py`/reporting/`scripts/*`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` when evidence proves a gap.
- **Locked unless disproven with minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- Add regressions in `tests/test_bab_cli_campaign28*.py` (and/or narrowly scoped non-CLI BAB tests only if strictly required/justified) for every proven fix. **If none, record explicit "no proven gaps" with evidence refs.**

### 4) Validate comprehensively and record
- After any module/test edit, re-run all Step 0 gates plus touched/new suites and impacted reporting/CLI suites; record exact counts/rc.
- If no modules touched, state baseline carried forward/re-run and confirm no regressions introduced.

### 5) Refresh this HANDOFF before finishing (MANDATORY)
Update in place: timestamp/HEAD/worktree state, Step 0 counts/rc (re-run or carried forward), C28 evidence log path, combo-by-combo PASS/FAIL/REVIEW + invariants, modules/tests touched (or none), and next binding heavy campaign (**C29**) with concrete ≥12-combo probe plan. No ambiguous handoff.

---

## Bottleneck removal status (as of 2026-11-11T11:22Z)
- **Single durable handoff enforced:** only `HANDOFF.md`.
- **Long gate execution bottleneck RESOLVED (reconfirmed 2026-11-11T11:15Z):** campaign_d, campaign11+14, full-BAB-excl gates green with recorded counts/rc.
- **C28 execution bottleneck OPEN:** `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` missing; C28 probe matrix not yet executed this cycle — **next agent must run it**.
- **No blocking runtime/env bottlenecks found:** deps importable, CLI/scripts runnable, fixtures present, tests runnable. Historical CI diagnostics in `research_state/workflow_run_diagnostics.jsonl` not reproduced locally on `main`.
- **Not blocked:** no churn performed.

## Historical closure (do not churn without new reproducible failure + probe evidence)
- **C6–C22:** closed with evidence.
- **C23:** 1 gap fixed (CLI output-path validation timing), 0 remaining.
- **C24:** 37 combos, **no proven gaps**.
- **C25:** 14 required combos, **no proven gaps**.
- **C26:** 14 combos, **0 production module/test edits**. Prior review items (C01 parity, C04 stale/frozen constant-series contract, C09 beta-neutral tolerance/semantics) re-checked in C27: **no proven product gaps**.
- **C27:** attribution/sizing/shorting/reporting stress — **0 proven gaps fixed, 0 regressions added**. Carry-over REVIEW: `beta_neutral=True` ex-post `strategy_beta(...)` may return `nan` under current call/series alignment — requires canonical apples-to-apples semantic/tolerance spec before any change (C28 combo 12).
- **Do not churn C6–C27** without a new, statable, reproducible failure with probe evidence.

## Next binding heavy campaign — C29 (prepare/execute after C28 closes)
**C29 — Real-data E2E pipeline hardening, attribution×sizing×shorting interaction stress, adversarial defect-fixture contract closure, and perf/regression gate parity (≥12 combos, HEAVY):**
1. **Real-fixture E2E determinism:** `tests/fixtures/real_market_prices.csv` + `tests/fixtures/real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices`→`BABStrategy(...).run()` — 3× each, byte/strict-JSON identical, rc=0.
2. **Attribution×sizing×shorting interaction matrix:** all sizing modes (`equal`,`kelly`,`vol_target`,`risk_parity`) × shorting constraints (`max_short_weight` 0.2/0.5/1.0) × attribution on/off — finite weights/cumulatives, no Traceback, 2× deterministic.
3. **Regime filter × costs × slippage × rebalance-freq full factorial** on real fixture — finite, deterministic per combo, `allow_nan=False`.
4. **Adversarial defect-fixture contract:** `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv` per load/CLI path — clean rc/errors vs accepted behavior per contract, no silent corruption, no partial output.
5. **Quality gate edge branches:** constant/flat/insufficient-history series — flat zero-weight periods, finite, no NaN/Inf/Traceback.
6. **CLI script surface hardening:** `scripts/bab_backtest_report.py` and `scripts/load_real_bab_example.py` with missing/invalid `--data-source`, `--data`, nested `--output`, overwrite — clean actionable errors, rc contract stable, no Traceback.
7. **Nonfinite serialization guard:** CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens emitted.
8. **Dry-run side-effect absence:** `--dry-run` produces no files, no output writes, stable rc/messages across valid/invalid inputs.
9. **Performance/regression gate parity:** re-run Step 0 gates after any edit — counts must not regress below floors (`campaign_d` ≥883/5/0; full BAB ≥4782/35/0; campaign11+14 ≥164/0).
10. **Output-path edge matrix:** existing-dir target, nested non-existent dir create, overwrite-existing-file — clean rc, no corrupt partial output, overwrite-safe.
11. **Config-API equivalence on real fixture:** every CLI knob has an equivalent `BABStrategy`/`BABConfig` kwarg producing identical final cumulative (≤1e-12) — parity log.
12. **Determinism under concurrent/repeated invocation:** same CLI invoked 3× in quick succession — identical strict JSON outputs, no file-lock/corruption issues.
**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
**Regression file:** `tests/test_bab_cli_campaign29*.py` for every proven fix; if none, record explicit "no proven gaps" with evidence refs.

## Gates that must stay green (non-negotiable)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (hard floor; raise if legitimately increased)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## Locks / prohibitions
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` gate closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/reporting/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: execute heavy C28 with probe evidence, remove bottlenecks if found, and leave a refreshed handoff.*
