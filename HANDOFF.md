# HANDOFF: Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-11T11:43:27Z
**HEAD:** `81072d5` (`chore(kilo): checkpoint agent session`), branch `main`, worktree: `HANDOFF.md` modified this session (no tracked product code modified)
**Repo priority (binding):** `Crypto-Betting-Against-Beta` — every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors.
**Durable handoff:** this file only (`.kilo/handoff.md` absent). No commit/push performed.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT MUST DO HEAVY WORK NOW (C28 CONTINUATION → C29)

**YOU MUST DO HEAVY WORK. No planning-only exits. No single-pass probes. No evidence-free exits.** Complete C28 closure end-to-end before finishing: finish/confirm all baseline gates with exact counts+rc, resolve every C28 REVIEW item with probe evidence, and either (a) land minimal regressions/fixes for proven gaps or (b) record explicit "no proven gaps" with evidence refs per item. Do not declare "blocked" without an evidenced attempt. Do not churn C6–C27 without a new, statable, reproducible failure with probe evidence.

### 0) Environment / mandatory preflight (record)
- `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
- `python3 -c "import numpy,pandas,scipy,pytest"` → **rc=0 (verified 2026-11-11T11:32Z)**
- C28 evidence log (POPULATED, combos 1–12): `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log` (2026-11-11T11:34Z)
- C28 probes/artifacts in `/home/runner/work/_temp/kilo-tmp/`: `c28_probe.py`, `c28_probe2.py`, `c28_probe3.py`

### 1) Step 0 baseline gates — CURRENT STATUS (must be finalized/recorded)

| Gate | Status (2026-11-11T11:43Z) | Evidence / action |
|---|---|---|
| `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` | **GREEN** — `883 passed, 5 skipped, 1808 deselected, 53 warnings, rc=0` | re-run 2026-11-11T11:32Z |
| `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` | **GREEN (log-complete)** — `4782 passed, 35 skipped, 231 warnings, rc=0` in `527.00s` | `/home/runner/work/_temp/kilo-tmp/c28_step0_full_bab.log` tail shows final summary; **re-run to confirm if any product/test edits occur** |
| `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py tests/test_bab_cli_campaign14_cli_reporting.py` | **NOT CONFIRMED COMPLETE** | prior attempts in this session exceeded tool timeouts without captured final summary; **MUST re-run to completion now and record exact counts/rc** (floor ≥164 passed, 0 failed) |

If any gate regresses, stop feature work, diagnose with probe evidence, and fix the smallest proven cause before proceeding. Do not revert prior fixes without cause.

### 2) C28 probe matrix — evidence-backed results (2026-11-11T11:34Z)
Evidence: `/home/runner/work/_temp/kilo-tmp/c28_bab_repro_config_cli_api_reporting_probe_evidence.log`

1. **CLI↔API parity (synthetic + knobs): REVIEW.** CLI `--synthetic --output` (BTC, beta_window=90, q=0.3/0.3, tx=0.001, slip=0.0005) final `0.4124625210306529` (ASSET0-4, periods 252, strict JSON finite) vs API `BABStrategy(BABConfig(...same...)).run()` `0.3156954937661637` (deterministic). **Not proven a bug** — likely config/default/synthetic-generation resolution differences between CLI path and direct API cfg. Requires apples-to-apples canonical parity investigation before claiming gap/fix.
2. **`--dry-run` contract matrix: PASS (exercised).** Valid synth/from-prices rc=0, no traceback/side-effects; invalid/missing/dir/conflict/from-prices-without-data/output-is-dir rc=1 with actionable messages, no traceback. `--output` validated in dry-run (rejects existing dir) with no write observed.
3. **Config boundary/validation: REVIEW.** Negative/out-of-range quantiles/windows/costs/slippage rejected (`BABConfigError`), empty universe rejected at run. **Review items:** `long_quantile=0.6, short_quantile=0.6` (sum≥1) accepted by cfg/run (finite 0.503575…); `benchmark='BTC', universe=['BTC','ETH']` accepted (0.962076…). Confirm intended contract vs validation gap with evidence before any change.
4. **Synthetic reproducibility: PASS.** 3× identical `0.31664543005633267`.
5. **Real-fixture multi-run determinism (costs/slippage/regime/rebalance): PASS.** 5 combos ×3 runs identical, finite on `tests/fixtures/real_market_prices.csv`.
6. **Metrics/report JSON/schema stability & strict finiteness: PASS.** CLI JSON keys/finite OK; `scripts/bab_backtest_report.py --json` rc=0 no traceback, keys `[config,metrics,rebalances]` finite; `BABStrategy.report()` dict, `tear_sheet()` str.
7. **Attribution/report/tear_sheet cross-consistency: PARTIAL (probe misuse).** `trade_attribution(res.weights,res.returns)` raised `TypeError` (wrong signature) — **not a proven product gap**. Must re-probe with correct API and reconcile attribution vs weights/returns/report.
8. **Script outputs deterministic & overwrite-safe: PASS.** `bab_backtest_report.py --json` 3× identical rc=0; `load_real_bab_example.py` 3× identical stdout/file rc=0, overwrite-safe.
9. **Edge universes: PASS.** 2-asset `ETH/BTC` finite (0.1675405863065047); short 120-row slice w/ `beta_window=30` finite (0.9391223464932164).
10. **Non-monotonic/defect fixture handling contracts: PASS (exercised).** `non_monotonic_dates.csv` and `real_data_defects.csv` via CLI returns/prices rc=0, no traceback, finite outputs (periods 7–30, cumulative 1.0 in probed cases) — verify contract intent (accept/normalize vs reject) across supported paths.
11. **Output path/overwrite handling: PASS.** Nested create rc=0, overwrite valid JSON, existing-dir target rc=1 clean error, no traceback/corrupt partial output.
12. **C27 carry-over `beta_neutral=True` ex-post `strategy_beta`: REVIEW.** `metrics.strategy_beta` present and finite (0.059632543547352916) on real fixture with `beta_neutral=True`, not NaN. Canonical apples-to-apples semantic/tolerance expectation must be stated/documented before any change; no proven gap concluded from single probe.

**Proven product-code gaps fixed this cycle:** none. **Regressions added:** none. **No modules touched** (handoff + temp evidence/probes only).

### 3) Mandatory C28 closure work (heavy, do now)
1. **Finalize gates:** run campaign11 bundle+campaign14 to completion and record exact counts/rc; keep campaign_d/full-BAB floors green.
2. **Resolve REVIEW items with evidence (minimal, canonical):**
   - (1) CLI↔API synthetic parity — identify canonical equivalent path/defaults; prove parity or document intended divergence with evidence.
   - (3) Quantile-sum≥1 and benchmark-in-universe — confirm intended contract; if validation gap, smallest fix + regression.
   - (7) Attribution — correct API call + reconciliation check; regression only if proven gap.
   - (12) `beta_neutral=True` ex-post `strategy_beta` semantics/tolerance — document or fix with evidence.
3. **Expand C28 matrix:** additional CLI knob combos, API report/tear_sheet strict finiteness on degenerate inputs, all relevant defect fixtures/modes, unwritable output path if feasible, more regime/cost/slippage/rebalance combos.
4. **For every proven gap:** smallest product fix + targeted regression (`tests/test_bab_cli_campaign28*.py` or most specific location). **If none:** explicit "no proven gaps" per item with evidence refs in next handoff.
5. **Re-run all Step 0 gates + touched suites** after any edit.

### 4) Next binding heavy campaign — C29 (execute after C28 closure)
**C29 — Real-data E2E pipeline hardening, attribution×sizing×shorting interaction stress, adversarial defect-fixture contract closure, and perf/regression gate parity (≥12 combos, HEAVY):**
1. **Real-fixture E2E determinism:** `tests/fixtures/real_market_prices.csv` + `tests/fixtures/real_market_prices_expanded.csv` via CLI `--from-prices` and API `load_prices`→`BABStrategy(...).run()` — 3× each, byte/strict-JSON identical, rc=0.
2. **Attribution×sizing×shorting interaction matrix:** sizing modes (`equal`,`kelly`,`vol_target`,`risk_parity`) × shorting constraints (`max_short_weight` 0.2/0.5/1.0) × attribution on/off — finite, no Traceback, 2× deterministic.
3. **Regime filter × costs × slippage × rebalance-freq factorial** on real fixture — finite, deterministic, `allow_nan=False`.
4. **Adversarial defect-fixture contract:** `messy_returns.csv`, `junk_columns.csv`, `all_nan_column.csv`, `benchmark_nan_window.csv` per load/CLI path — clean rc/errors vs contract, no silent corruption/partial output.
5. **Quality gate edge branches:** constant/flat/insufficient-history — flat zero-weight periods, finite, no NaN/Inf/Traceback.
6. **CLI script hardening:** `scripts/bab_backtest_report.py`, `scripts/load_real_bab_example.py` with missing/invalid args, nested `--output`, overwrite — actionable errors, stable rc, no Traceback.
7. **Nonfinite serialization guard:** CLI/script/API JSON on degenerate runs — `allow_nan=False`, finiteness walk, no `Infinity`/`NaN` tokens.
8. **Dry-run side-effect absence:** no files/writes, stable rc/messages across valid/invalid inputs.
9. **Gate parity after edits:** floors `campaign_d` ≥883/5/0; full BAB excl loaders/controller ≥4782/35/0; campaign11+14 ≥164/0.
10. **Output-path edge matrix:** existing-dir target, nested non-existent dir create, overwrite-existing-file — clean rc, no corrupt partial output.
11. **Config-API equivalence on real fixture:** every CLI knob has equivalent `BABStrategy`/`BABConfig` kwarg producing identical final cumulative (≤1e-12) — parity log.
12. **Determinism under repeated invocation:** same CLI 3× quick succession — identical strict JSON, no corruption.
**Evidence log (MANDATORY):** `/home/runner/work/_temp/kilo-tmp/c29_bab_realtime_e2e_interaction_stress_probe_evidence.log`
**Regression file:** `tests/test_bab_cli_campaign29*.py` for every proven fix; if none, explicit "no proven gaps" with evidence refs.

## Gates that must stay green (non-negotiable)
- `campaign_d` **≥883 passed, 5 skipped, rc=0**
- full BAB excl `data_loader`/`controller` **≥4782 passed, 35 skipped, rc=0** (raise floor if legitimately increased)
- campaign11 bundle incl. 11ab + campaign14 **≥164 passed, rc=0**

## Locks / prohibitions
- Do **not** edit `.github/workflows/*`.
- Do **not** edit/commit tracked `probe*`/`debug*`/`ast_probe.py`.
- Do **not** weaken/delete `batch148/149/172` or `campaign_d*` tests.
- `beta.py`/`data_loader.py` closed — do not alter without new disproving evidence and minimal fix.
- `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`config.py` locked unless disproven by new evidence.
- `cli.py`/`metrics.py`/reporting/`scripts`/`costs.py`/`regime.py`/`attribution.py`/`shorting.py`/`sizing.py` editable only for smallest proven fix from probe evidence.
- No commit/push unless explicitly requested. No planning-only or evidence-free exits.

*Single durable handoff for `Crypto-Betting-Against-Beta`. Future agents: finish C28 gate closure + REVIEW resolution with evidence, remove bottlenecks, then execute C29 heavy campaign and refresh this handoff.*
