# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:38:00Z
**HEAD:** `81072d5` (`chore(kilo): checkpoint agent session`), branch `main`, worktree: `HANDOFF.md` modified this session (no tracked product code modified)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**Durable handoff:** this file only (`.kilo/handoff.md` absent). No commit/push performed.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST DO HEAVY WORK NOW (C28, IN-FLIGHT / CONTINUE)

**YOU MUST DO HEAVY WORK. No planning-only exits. No single-pass probes. No evidence-free exits.** Continue/complete Campaign 28 end-to-end before finishing; produce probe evidence and either (a) regressions for proven gaps or (b) explicit "no proven gaps" with evidence refs for any remaining items. Do not declare "blocked" without an evidenced attempt. Do not churn C6–C27 without a new, statable, reproducible failure with probe evidence.

### 0) Environment / mandatory preflight (record)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0 (verified 2026-11-11T11:32Z)**
- C28 evidence log (MANDATORY): `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (**CREATED/POPULATED 2026-11-11T11:34Z; combos 1–12 executed this cycle**)

### 1) Step 0 baseline gates (status as of 2026-11-11T11:38Z)
- `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0** (re-run 2026-11-11T11:32Z) ✅
- campaign11 bundle + campaign14: `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` → **INCOMPLETE at handoff time** (multiple runs exceeded 120–600s timeout in this session without final summary; no failure observed in streamed output). **MUST be re-run to completion and recorded with exact counts/rc.**
- full BAB excl `data_loader`/`controller`: `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **INCOMPLETE/RUNNING at handoff time** (bg pid ~25522, log `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log`, progress observed ~11%+). **MUST complete and be recorded with exact counts/rc.**

If any gate regresses, stop feature work, diagnose with probe evidence, and fix the smallest proven cause before proceeding. Do not revert prior fixes without cause.

### 2) C28 execution status — probe matrix (evidence-backed, 2026-11-11T11:34Z)
Evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log`

1. **CLI↔API parity (synthetic + knobs):** REVIEW. `--synthetic --output` CLI (BTC, beta_window=90, q=0.3/0.3, tx=0.001, slip=0.0005) produced `final_cumulative=0.4124625210306529`, universe `ASSET0-4`, periods 252, strict JSON finite/keys OK, rc=0. API `BABStrategy(BABConfig(...same...)).run()` produced `0.3156954937661637` (deterministic). **Parity false in this probe** — likely due to config/strategy synthetic-generation/default-resolution differences (CLI path vs direct cfg) rather than proven corruption; requires apples-to-apples canonical parity investigation before claiming gap/fix.
2. **`--dry-run` contract matrix:** PASS/contract-clean on exercised cases. Valid synth/from-prices rc=0 no traceback/side-effects; invalid/missing/dir/conflict/from-prices-without-data/output-is-dir cases rc=1 with actionable messages, no traceback. `--output` validated in dry-run (rejects existing dir target) — no write side effect observed.
3. **Config boundary/validation:** mostly PASS/explicit. Negative/out-of-range quantiles/windows/costs/slippage rejected (`BABConfigError`), empty universe rejected at run (`BABConfigError` overlap). **REVIEW:** `long_quantile=0.6, short_quantile=0.6` (sum≥1) accepted by cfg/run with finite output (0.503575…); `benchmark='BTC', universe=['BTC','ETH']` accepted (final 0.962076…) — document/confirm intended contract vs validation gap with evidence before change.
4. **Synthetic reproducibility:** PASS (3× identical `0.31664543005633267`).
5. **Real-fixture multi-run determinism (costs/slippage/regime/rebalance combos):** PASS. 5 combos ×3 runs identical and finite on `tests/fixtures/real_market_prices.csv` (base/cost_slip/regime/weekly/all).
6. **Metrics/report JSON/schema stability & strict finiteness:** PASS. CLI synthetic JSON keys/finite OK; `scripts/bab_backtest_report.py --json` rc=0 no traceback, keys `[config,metrics,rebalances]` finite; `BABStrategy.report()` returns dict, `tear_sheet()` returns str.
7. **Attribution/report/tear_sheet cross-consistency:** PARTIAL. Probe called `trade_attribution(res.weights,res.returns)` and got `TypeError` (signature differs) — **probe misuse, not a proven product gap**. Needs correct API call and reconciliation check.
8. **Script outputs deterministic & overwrite-safe:** PASS. `bab_backtest_report.py --json` 3× identical stdout rc=0; `load_real_bab_example.py` 3× identical stdout/file rc=0, overwrite-safe.
9. **Edge universes:** PASS. 2-asset `ETH/BTC` finite (0.1675405863065047), short 120-row slice w/ `beta_window=30` finite (0.9391223464932164), no traceback.
10. **Non-monotonic/defect fixture handling contracts:** PASS (exercised paths). `non_monotonic_dates.csv` and `real_data_defects.csv` via CLI returns/prices modes all rc=0, no traceback, finite degenerate-ish outputs (periods 7–30, cumulative 1.0 in probed cases) — verify these match intended contract (clean accept/normalize vs reject) across all supported paths.
11. **Output path/overwrite handling:** PASS. Nested create rc=0, overwrite produces valid JSON, existing-dir target rc=1 clean error, no traceback/corrupt partial output observed.
12. **C27 carry-over `beta_neutral=True` ex-post `strategy_beta`:** REVIEW. `metrics.strategy_beta` exists; on real fixture with `beta_neutral=True` ex-post beta = `0.059632543547352916` (finite), not NaN. Backtest cols include returns/gross/cost/slippage/cumulative. Canonical apples-to-apples semantic/tolerance expectation still must be stated/documented before any change; no proven product gap concluded from this single probe.

**Proven product-code gaps fixed this cycle:** none.
**Regressions added:** none.
**No modules touched** (only `HANDOFF.md` and temp evidence/probe artifacts in `/home/runner/work/_temp/kilo-tmp/`).

### 3) Required follow-up (heavy, next agent)
- Complete Step 0 pending gates and record exact counts/rc (`campaign_d` already green).
- Resolve REVIEW items with minimal evidence: (1) CLI↔API synthetic parity canonical equivalence, (3) quantile-sum/benchmark-in-universe contract, (7) correct attribution API usage + reconciliation, (12) beta-neutral semantic/tolerance contract.
- Expand C28 matrix where needed (additional CLI knob combos, API report/tear_sheet strict finiteness on degenerate inputs, all defect fixtures/modes, permission-like unwritable path if feasible, more regime/cost/slippage/rebalance combos) and add regressions only for proven gaps.
- Re-run all Step 0 gates + touched suites after any edit.

### 4) Next binding heavy campaign — C29 (prepare/execute after C28 closes)
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

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: complete C28 with full gate counts, resolve REVIEW items with evidence, remove bottlenecks if found, and leave a refreshed handoff.*
