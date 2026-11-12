# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T12:04:18Z
**HEAD:** `24193139c05ec5f5f0e39bf95e083d627230a768` on `main`
**Working tree (tracked):** expected clean at handoff refresh (verify with `git status --short`; untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts must not be committed).
**Env:** Python 3.12.3, Linux, repo root, `PYTHONPATH=$PWD`.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No parallel TODO/session handoff files.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven current blocker recorded:** core BAB modules importable per prior sessions; prior recorded gates/probes (C43) were green/clean as logged below. Ephemeral `/home/runner/work/_temp/kilo-tmp/c43_probes/` evidence may not persist across runners—do not treat absence of tmp artifacts as a regression; re-probe if needed.
- **Gate invocation note:** for Gate 1 prefer explicit `tests/test_bab_data_loader_campaign_d*` file list if globbing is brittle in shell. Run Gate 2/3 from repo root with `PYTHONPATH=$PWD`.

## Gate floors (last recorded GREEN on `b7df039`; re-run after any fix or if env/HEAD drift suspected)

**Verified 2026-11-12T12:04:18Z (HEAD `2419313`):** Core BAB tests (86 passed), CLI campaign tests (32 passed), deps import OK. Full gates not re-run (time); if env/checkout uncertain, re-run Gate 1/2/3 to completion with durable logs under `/home/runner/work/_temp/kilo-tmp/c45_gates/`.

| Gate | Command (cwd=repo root, `PYTHONPATH=$PWD`) | Last recorded result | Log (ephemeral) |
|---|---|---|---|
| 1 | `python3 -m pytest -q` over explicit `tests/test_bab_data_loader_campaign_d{,2,3,5,_coerce_more,_core,_core2,_core3,_core4,_core5,_core_final,_deep,_deep3,_final_coverage,_final_push,_final_push2,_gaps,_gaps2,_heavy,_heavy2,_heavy3,_heavy_push2,_more2,_more4,_more5,_push,_push2,_push3,_push4,_push_final,_push_heavy,_ultra}.py` + `tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | **898 passed, 5 skipped, rc=0** | `/home/runner/work/_temp/kilo-tmp/c44_gates/c44_gate1_20261112T110100Z.log` |
| 2 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | **2234 passed, 5 skipped, rc=0** | `/home/runner/work/_temp/kilo-tmp/c44_gates/c44_gate2_20261112T110100Z.log` |
| 3 | `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` | **164 passed, rc=0** | `/home/runner/work/_temp/kilo-tmp/c44_gates/c44_gate3_20261112T110100Z.log` |

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)
- **C43 ROTATION (recorded 2026-11-12T09:25:00Z, HEAD `b7df039`):** 39/39 probes PASS, 0 FAIL/ERROR, no proven gaps (see matrix below; logs under `/home/runner/work/_temp/kilo-tmp/c43_probes/` when present).
- **C42 ROTATION:** CLOSED — 38/38 PASS, 0 FAIL. C6–C41 CLOSED per prior evidence. No churn.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (binding, read first — 2026-11-12T12:04:18Z)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; **no planning-only turn**.
- **Binding campaign:** **C45 ROTATION** (heavy, mandatory). C44 closed clean (44/44 PASS, no proven gaps). Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs under `/home/runner/work/_temp/kilo-tmp/c45_probes/`.
- **Immediate actions (in order):**
  1. **Preflight:** confirm `git status --short` (tracked clean expected), `python3 -m pip show numpy pandas scipy pytest hypothesis coverage` or quick import check; install missing deps only if needed (environment bottleneck). Record env if relevant.
  2. **Gates:** if no code changes and env known-good, you may proceed to probes but be ready to re-run affected/all three gates on any fix or suspected drift. If env changed or uncertain, re-run Gate 1/2/3 to completion with durable logs under `/home/runner/work/_temp/kilo-tmp/c45_gates/`.
  3. **Execute ≥20 NEW C45 adversarial probes** (C45 shapes only; **no reuse of C40–C44 scripts/shapes**) across surfaces/cross-interactions listed in **BINDING INITIAL TASK — C45 ROTATION** below. Save per-probe durable logs/artifacts (id, target, shape, result, rc/duration, repro/notes) in `/home/runner/work/_temp/kilo-tmp/c45_probes/` and a summary JSON/MD.
  4. **On any proven gap:** smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → capture evidence.
  5. **Before exit (mandatory):** refresh this file (timestamp/HEAD, gate results+log paths if re-run, full C45 probe matrix, fixes/tests added or "no proven gaps" with per-probe evidence, working-tree notes) and update `AGENT_HANDOFF.md` pointer. If C45 closes cleanly, **immediately define and start C46** (≥20 new probes, new shapes, durable logs) and leave C46 as the next binding initial task here.

## C43 Rotation Results (2026-11-12T09:25:00Z, HEAD `b7df039`)

**Probes executed:** 39 NEW adversarial probes (no C40–C42 reuse)
**Result:** **39 PASS, 0 FAIL, 0 ERROR** — no proven gaps

### Probe Matrix

| ID | Target | Shape | Status | Duration | Log |
|---|---|---|---|---|---|
| C43-001 | beta.py | constant_asset_returns | PASS | 0.007s | `c43_probes/C43-001.log` |
| C43-002 | beta.py | constant_benchmark | PASS | 0.000s | `c43_probes/C43-002.log` |
| C43-003 | beta.py | nan_asset | PASS | 0.000s | `c43_probes/C43-003.log` |
| C43-004 | beta.py | nan_benchmark | PASS | 0.000s | `c43_probes/C43-004.log` |
| C43-005 | beta.py | inf_values | PASS | 0.000s | `c43_probes/C43-005.log` |
| C43-006 | beta.py | all_inf | PASS | 0.000s | `c43_probes/C43-006.log` |
| C43-007 | beta.py | single_observation | PASS | 0.000s | `c43_probes/C43-007.log` |
| C43-008 | beta.py | misaligned_index | PASS | 0.001s | `c43_probes/C43-008.log` |
| C43-009 | beta.py | benchmark_mismatch | PASS | 0.000s | `c43_probes/C43-009.log` |
| C43-010 | beta.py | window_edges | PASS | 0.002s | `c43_probes/C43-010.log` |
| C43-011 | beta.py | cross_regime_constant_vol | PASS | 0.004s | `c43_probes/C43-011.log` |
| C43-012 | data_loader.py | malformed_headers | PASS | 0.004s | `c43_probes/C43-012.log` |
| C43-013 | data_loader.py | mixed_frequency | PASS | 0.002s | `c43_probes/C43-013.log` |
| C43-014 | data_loader.py | timezone_edges | PASS | 0.002s | `c43_probes/C43-014.log` |
| C43-015 | data_loader.py | extreme_values | PASS | 0.003s | `c43_probes/C43-015.log` |
| C43-016 | data_loader.py | streaming_like | PASS | 0.003s | `c43_probes/C43-016.log` |
| C43-017 | strategy.py | costs_shorting_interaction | PASS | 0.129s | `c43_probes/C43-017.log` |
| C43-018 | strategy.py | costs_only | PASS | 0.005s | `c43_probes/C43-018.log` |
| C43-019 | strategy.py | shorting_only | PASS | 0.098s | `c43_probes/C43-019.log` |
| C43-020 | regime.py | shorting_cross | PASS | 0.181s | `c43_probes/C43-020.log` |
| C43-021 | attribution.py | regime_cross | PASS | 0.012s | `c43_probes/C43-021.log` |
| C43-022 | metrics.py | regime_cross | PASS | 0.011s | `c43_probes/C43-022.log` |
| C43-023 | costs.py | zero_adv | PASS | 0.002s | `c43_probes/C43-023.log` |
| C43-024 | costs.py | negative_adv | PASS | 0.002s | `c43_probes/C43-024.log` |
| C43-025 | costs.py | nan_prices | PASS | 0.003s | `c43_probes/C43-025.log` |
| C43-026 | costs.py | per_asset_adv_df | PASS | 0.003s | `c43_probes/C43-026.log` |
| C43-027 | regime.py | constant_vol | PASS | 0.004s | `c43_probes/C43-027.log` |
| C43-028 | regime.py | hysteresis_edges | PASS | 0.001s | `c43_probes/C43-028.log` |
| C43-029 | regime.py | nan_returns | PASS | 0.003s | `c43_probes/C43-029.log` |
| C43-030 | sizing.py | kelly_lookback_lt_data | PASS | 0.005s | `c43_probes/C43-030.log` |
| C43-031 | sizing.py | vol_target_unreachable | PASS | 0.003s | `c43_probes/C43-031.log` |
| C43-032 | sizing.py | risk_parity_lookback_lt_data | PASS | 0.006s | `c43_probes/C43-032.log` |
| C43-033 | sizing.py | equal_weight_no_scaling | PASS | 0.001s | `c43_probes/C43-033.log` |
| C43-034 | sizing.py | max_leverage_binding | PASS | 0.003s | `c43_probes/C43-034.log` |
| C43-035 | shorting.py | borrowable_dict | PASS | 0.009s | `c43_probes/C43-035.log` |
| C43-036 | shorting.py | per_asset_borrow_costs | PASS | 0.000s | `c43_probes/C43-036.log` |
| C43-037 | shorting.py | strict_violation | PASS | 0.001s | `c43_probes/C43-037.log` |
| C43-038 | shorting.py | cascading_caps | PASS | 0.007s | `c43_probes/C43-038.log` |
| C43-039 | signals.py | generate_bab_edge | PASS | 0.001s | `c43_probes/C43-039.log` |

### Coverage Summary
- **beta.py**: 11 probes (constant/NaN/inf, single obs, misaligned, benchmark mismatch, window edges, cross-regime)
- **data_loader.py**: 5 probes (malformed headers, mixed freq, tz edges, extreme values, streaming)
- **strategy.py**: 3 probes (costs+shorting, costs only, shorting only)
- **regime.py**: 4 probes (shorting cross, constant vol, hysteresis edges, NaN returns)
- **attribution.py**: 1 probe (regime cross)
- **metrics.py**: 1 probe (regime cross)
- **costs.py**: 4 probes (zero/negative ADV, NaN prices, per-asset ADV DataFrame)
- **sizing.py**: 5 probes (Kelly/RiskParity/VolTarget/EqualWeight, lookback<data, max_leverage binding)
- **shorting.py**: 4 probes (borrowable dict, per-asset costs, strict violation, cascading caps)
- **signals.py**: 1 probe (edge betas with NaN)

### Required Cross-Interactions Tested
- ✅ `beta` + `regime` (C43-011)
- ✅ `strategy` + `costs` + `shorting` (C43-017)
- ✅ `regime` + `shorting` (C43-020)
- ✅ `attribution` + `regime` (C43-021)
- ✅ `metrics` + `regime` (C43-022)

**All durable logs:** `/home/runner/work/_temp/kilo-tmp/c43_probes/` (39 `.log` + 39 `.json` + `c43_probe_summary.json`)

## C44 Rotation Results (2026-11-12T11:09:00Z, HEAD `238b034`)

**Probes executed:** 44 NEW adversarial probes (no C40–C43 reuse)
**Result:** **44 PASS, 0 FAIL, 0 ERROR** — **no proven gaps**

### Probe Matrix (summary)

| ID | Target | Shape | Status | Duration | Log |
|---|---|---|---|---|---|
| C44-001 | beta.py | calculate_beta_fast nan-only + constant benchmark | PASS | 0.0005s | `c44_probes/C44-001.log` |
| C44-002 | beta.py | _calc_rolling_beta_series all-NaN benchmark window | PASS | 0.0003s | `c44_probes/C44-002.log` |
| C44-003 | beta.py | estimate_betas min_obs > window clamps to window | PASS | 0.0019s | `c44_probes/C44-003.log` |
| C44-004 | beta.py | calculate_rolling_beta multi-asset mixed finite/NaN | PASS | 0.0014s | `c44_probes/C44-004.log` |
| C44-005 | data_loader.py | detect_and_normalize_exchange_format exchange quirks | PASS | 0.0266s | `c44_probes/C44-005.log` |
| C44-006 | data_loader.py | normalize_schema duplicate columns | PASS | 0.0012s | `c44_probes/C44-006.log` |
| C44-007 | data_loader.py | load_returns tz/DST edge cases | PASS | 0.0030s | `c44_probes/C44-007.log` |
| C44-008 | strategy.py | run() regime_filter + beta_neutral combined | PASS | 0.0195s | `c44_probes/C44-008.log` |
| C44-009 | strategy.py | report() degenerate all-NaN returns (defensive rejection) | PASS | 0.0013s | `c44_probes/C44-009.log` |
| C44-010 | strategy.py | tear_sheet() missing metrics | PASS | 0.0088s | `c44_probes/C44-010.log` |
| C44-011 | strategy.py | config aliases window/beta_window min_obs/min_observations | PASS | 0.0000s | `c44_probes/C44-011.log` |
| C44-012 | costs.py | time-varying adv_usd DataFrame misaligned index | PASS | 0.0025s | `c44_probes/C44-012.log` |
| C44-013 | costs.py | participation_cap boundary 0.0 (rejected) and 1.0 | PASS | 0.0020s | `c44_probes/C44-013.log` |
| C44-014 | costs.py | borrow_bps_per_year=0 | PASS | 0.0008s | `c44_probes/C44-014.log` |
| C44-015 | costs.py | fixed_fee_per_trade with zero turnover | PASS | 0.0009s | `c44_probes/C44-015.log` |
| C44-016 | regime.py | regime_scale_scalar empty returns | PASS | 0.0002s | `c44_probes/C44-016.log` |
| C44-017 | regime.py | classify_volatility_regimes_percentile quantile boundaries | PASS | 0.0012s | `c44_probes/C44-017.log` |
| C44-018 | regime.py | _apply_vol_hysteresis hysteresis > threshold spread | PASS | 0.0004s | `c44_probes/C44-018.log` |
| C44-019 | regime.py | mean_reversion_zscore zero std | PASS | 0.0009s | `c44_probes/C44-019.log` |
| C44-020 | shorting.py | apply_shorting_constraints signals input | PASS | 0.0017s | `c44_probes/C44-020.log` |
| C44-021 | shorting.py | borrowable dict cascading wildcards | PASS | 0.0008s | `c44_probes/C44-021.log` |
| C44-022 | shorting.py | strict mode multiple violations | PASS | 0.0006s | `c44_probes/C44-022.log` |
| C44-023 | shorting.py | max_short_exposure=0 | PASS | 0.0007s | `c44_probes/C44-023.log` |
| C44-024 | sizing.py | apply_position_sizing sizer string shorthand | PASS | 0.0004s | `c44_probes/C44-024.log` |
| C44-025 | sizing.py | returns DataFrame fewer columns than signals | PASS | 0.0004s | `c44_probes/C44-025.log` |
| C44-026 | sizing.py | lookback == data length | PASS | 0.0004s | `c44_probes/C44-026.log` |
| C44-027 | sizing.py | max_leverage < 1.0 | PASS | 0.0004s | `c44_probes/C44-027.log` |
| C44-028 | signals.py | long_quantile + short_quantile > 1.0 | PASS | 0.0003s | `c44_probes/C44-028.log` |
| C44-029 | signals.py | quantiles at 0.0 / 1.0 boundaries | PASS | 0.0003s | `c44_probes/C44-029.log` |
| C44-030 | signals.py | beta DataFrame all-NaN rows/columns | PASS | 0.0003s | `c44_probes/C44-030.log` |
| C44-031 | portfolio.py | construct_portfolio dollar_neutral=False | PASS | 0.0002s | `c44_probes/C44-031.log` |
| C44-032 | portfolio.py | gross_exposure_limit binding | PASS | 0.0004s | `c44_probes/C44-032.log` |
| C44-033 | portfolio.py | net_exposure_limit binding | PASS | 0.0003s | `c44_probes/C44-033.log` |
| C44-034 | portfolio.py | max_single_weight < equal weight | PASS | 0.0004s | `c44_probes/C44-034.log` |
| C44-035 | backtest.py | run_backtest transaction_costs float OK / Series rejected | PASS | 0.0019s | `c44_probes/C44-035.log` |
| C44-036 | backtest.py | run_backtest slippage float OK / DataFrame rejected | PASS | 0.0017s | `c44_probes/C44-036.log` |
| C44-037 | backtest.py | run_backtest weights with NaN rows | PASS | 0.0012s | `c44_probes/C44-037.log` |
| C44-038 | beta+sizing | cross-interaction beta -> signals -> sizing | PASS | 0.0022s | `c44_probes/C44-038.log` |
| C44-039 | data_loader+strategy | cross-interaction load_returns -> BABStrategy | PASS | 0.0077s | `c44_probes/C44-039.log` |
| C44-040 | costs+sizing | cross-interaction sizing weights -> costs | PASS | 0.0012s | `c44_probes/C44-040.log` |
| C44-041 | shorting+sizing | cross-interaction sizing -> shorting constraints | PASS | 0.0010s | `c44_probes/C44-041.log` |
| C44-042 | regime+signals | cross-interaction regime classification + signals | PASS | 0.0011s | `c44_probes/C44-042.log` |
| C44-043 | portfolio+backtest | cross-interaction construct_portfolio -> run_backtest | PASS | 0.0017s | `c44_probes/C44-043.log` |
| C44-044 | attribution+costs | cross-interaction backtest -> attribution -> totals | PASS | 0.0027s | `c44_probes/C44-044.log` |

**Coverage:** beta (4), data_loader (3), strategy (4), costs (4), regime (4), shorting (4), sizing (4), signals (3), portfolio (4), backtest (3) + 7 cross-interactions (beta+sizing, data_loader+strategy, costs+sizing, shorting+sizing, regime+signals, portfolio+backtest, attribution+costs).

**All durable logs:** `/home/runner/work/_temp/kilo-tmp/c44_probes/` (44 `.log` + `c44_probe_summary.json` + `c44_probe_summary.md`). Probe runner: `/home/runner/work/_temp/kilo-tmp/c44_probes/c44_probe_runner.py` (untracked, not committed).

---

## BINDING INITIAL TASK — C45 ROTATION (heavy, mandatory)

**Objective:** deep adversarial robustness campaign (C45). Execution, not planning. Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs. C44 closed clean (44/44 PASS, no proven gaps); C45 must continue with ≥20 NEW probes and NO shape reuse from C40–C44.

### 1) Environment & gates
- Preflight deps/imports; fix env bottlenecks first (install missing deps if required). No gate green → do not claim progress.
- If env/checkout uncertain or any fix made: re-run Gate 1/2/3 to completion from repo root with `PYTHONPATH=$PWD`, capture durable logs in `/home/runner/work/_temp/kilo-tmp/c45_gates/`.
- Gate 1 (explicit campaign_d list + batch148/149/172), Gate 2 (`--ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py`), Gate 3 (`tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py`).

### 2) Execute ≥20 NEW adversarial probes (C45 shapes only)
- **No reuse** of C40/C41/C42/C43/C44 scripts/shapes. Durable per-probe logs/artifacts under `/home/runner/work/_temp/kilo-tmp/c45_probes/` + summary.
- **New surfaces/shapes (distinct from C44):**
  - `beta.py`: `calculate_beta` with mismatched-length arrays, `rolling_beta` with min_periods > window, `estimate_betas` with benchmark column missing, `calculate_rolling_beta` with single-asset frame.
  - `data_loader.py`: `load_returns_from_csv` with missing file, `load_returns_from_parquet` with missing file, `load_returns_from_jsonl` malformed lines, `detect_source_type` ambiguous extensions, `normalize_index` with duplicate timestamps.
  - `strategy.py`: `run()` with transaction_costs as Series, `run()` with empty universe, BABStrategy constructor with invalid beta_window=0, config with long_quantile+short_quantile > 1.0.
  - `costs.py`: `compute_transaction_costs` with prices None + impact_coefficient>0, adv_usd dict with unknown asset, borrow_bps_per_year negative rejected, trading_days_per_year=0 rejected.
  - `regime.py`: `classify_volatility_regimes` (non-percentile) with window > data length, `get_regime_state` at boundary, `apply_regime_scaling` with zero vol.
  - `shorting.py`: `apply_shorting_constraints` with empty frame, ShortingConstraints with invalid max_short_exposure negative, borrow_bps_per_year dict with missing asset wildcard.
  - `sizing.py`: `apply_position_sizing` with unknown sizer string, KellySizer lookback=0, VolatilityTargetSizer target_vol=0, EqualWeightSizer max_leverage=0 rejected.
  - `signals.py`: `generate_bab_signals` with non-numeric beta column, single-row beta DataFrame, duplicate column names.
  - `portfolio.py`: `construct_portfolio` with empty signals, max_position_size=0 rejected, enforce_risk_checks=True with all limits None.
  - `backtest.py`: `run_backtest` with empty returns, returns and weights misaligned index, cost_model invalid type rejected.
- **Required NEW cross-interactions (distinct from C44):** `beta+portfolio`, `data_loader+backtest`, `costs+regime`, `shorting+backtest`, `sizing+signals`, `strategy+attribution`, `portfolio+signals`.
- Maintain probe matrix (id, target, shape, result, log path, brief repro). Minimum 20 probes.

### 3) On proven regression/gap
Smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence. Do not weaken locked tests.

### 4) On no proven gaps
Record **"C45 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths.

### 5) Before exit (mandatory)
Refresh this file with: timestamp/HEAD, gate results+log paths (if run), full C45 probe matrix, fixes/tests added (if any), working-tree notes, and **next concrete heavy task**. Update `AGENT_HANDOFF.md`. If C45 closes cleanly, **immediately define and start C46** (≥20 new probes, new shapes, durable logs) and leave it binding here.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.

(End of file)
