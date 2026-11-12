# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T10:54:26Z
**HEAD:** `b98c6e2` on `main` (gates previously confirmed GREEN on `b7df039`, working tree clean since)
**Working tree (tracked):** clean. Untracked `/home/runner/work/_temp/kilo-tmp/` probe/log artifacts may exist and must not be committed.
**Env:** Python 3.12.3, Linux, repo root, `PYTHONPATH=$PWD`.

**Repo priority (binding):** advance **Crypto-Betting-Against-Beta** (market-neutral BAB: long low-beta / short high-beta vs BTC benchmark) via proven correctness/robustness work in allowed editable surfaces only. No unrelated refactors, no planning-only sessions.

## Bottlenecks cleared / status
- **Single durable handoff:** this file is canonical. `AGENT_HANDOFF.md` is pointer-only. No duplicate/stale task blocks.
- **Historical diagnostics only:** `research_state/workflow_run_diagnostics.jsonl` contains captured CI/log excerpts from prior runs/heads (tool-arg noise, timeouts, old head SHAs). Treat as historical; not evidence of a current-checkout failure and must not justify inaction or "blocked" claims.
- **No proven runtime blocker reproduced:** core BAB modules import cleanly on current HEAD.
- **Gate invocation note (current env):** pytest glob-expansion for `tests/test_bab_data_loader_campaign_d*.py` is brittle in this shell; Gate 1 was executed with explicit campaign_d file list. Gate 2/3 must run from repo root with `PYTHONPATH=$PWD` (running from wrong cwd produced `ModuleNotFoundError: strategies` collection failures in early attempt; corrected reruns launched).

## Gate floors (gates confirmed GREEN on `b7df039`; tree unchanged since, HEAD `b98c6e2`)

| Gate | Command (cwd=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta, PYTHONPATH=$PWD) | Result | Log |
|---|---|---|---|
| 1 | `python3 -m pytest -q` over explicit `tests/test_bab_data_loader_campaign_d{,2,3,5,_coerce_more,_core,_core2,_core3,_core4,_core5,_core_final,_deep,_deep3,_final_coverage,_final_push,_final_push2,_gaps,_gaps2,_heavy,_heavy2,_heavy3,_heavy_push2,_more2,_more4,_more5,_push,_push2,_push3,_push4,_push_final,_push_heavy,_ultra}.py` + `batch148/149/172` | **898 passed, 5 skipped, 53 warnings, rc=0** (4.32s) | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate1_20261112T085359Z.log` |
| 2 | `python3 -m pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | **2234 passed, 5 skipped, 41 warnings, rc=0** (384.33s) | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate2_20261112T085359Z_bg.log` |
| 3 | `python3 -m pytest -q tests/test_bab_cli_campaign11*.py tests/test_bab_cli_campaign14*.py` | **164 passed, rc=0** (156.29s) | `/home/runner/work/_temp/kilo-tmp/c43_gate_gate3_20261112T085359Z_bg.log` |

**All three gates GREEN on HEAD `b7df039`. No regressions. C43 probes executed and passed. Proceed to C44.**

## Completed campaign (do not reopen without new reproducible failure + durable evidence)
- **C42 ROTATION:** CLOSED — 38/38 adversarial probes PASS, 0 FAIL, no proven gaps. Evidence: `/home/runner/work/_temp/kilo-tmp/c42_probe_summary_20261112T082656Z.json` and `c42_probe_*`.
- C6–C41 CLOSED per prior evidence. No churn.

## INITIAL MESSAGE FOR NEXT AGENTIC SESSION (read this first — refreshed 2026-11-12T10:54:26Z)
- **Single durable handoff:** this file only. `AGENT_HANDOFF.md` pointer-only. `research_state/workflow_run_diagnostics.jsonl` is historical diagnostics, not a current blocker.
- **Repo focus:** `Crypto-Betting-Against-Beta` (market-neutral BAB vs BTC). Deliver proven correctness/robustness in allowed surfaces only; no planning-only turn.
- **Binding campaign:** **C44 ROTATION** (heavy, mandatory). Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs under `/home/runner/work/_temp/kilo-tmp/c44_probes/`.
- **Immediate actions (in order):**
  1. Gates 1/2/3 CONFIRMED GREEN — no further gate action needed unless a fix is made.
  2. C43 COMPLETE — 39 probes PASS, 0 FAIL, 0 ERROR, no proven gaps. Evidence in `/home/runner/work/_temp/kilo-tmp/c43_probes/`.
  3. Execute **≥20 NEW C44 adversarial probes** (C44 shapes only, no C40–C43 reuse) across the new surfaces/cross-interactions in section BINDING INITIAL TASK below, with per-probe durable logs (id, target, shape, result, rc, duration, repro).
  4. On any proven gap: smallest fix in allowed editable area only → minimal regression → re-run affected tests + all three gates → capture evidence.
  5. Before exit: refresh this file with full C44 matrix/evidence, working-tree notes, and next concrete heavy task. If C44 closes cleanly, **immediately define and start C45** (≥20 new probes, new shapes, binding) and leave it as the next initial task message.

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

---

## BINDING INITIAL TASK — C44 ROTATION (heavy, mandatory)

**Objective:** deep adversarial robustness campaign (C44). Execution, not planning. Do not declare "no proven gaps" or "blocked" without attempted probes and durable logs.

### 1) Gate floors finalized (current HEAD)
All three gates GREEN on `b7df039`: Gate 1 (898 passed), Gate 2 (2234 passed, 5 skipped), Gate 3 (164 passed). No regressions. C43 probes (39) all PASS. Proceed directly to C44 probes.

### 2) Execute ≥20 NEW adversarial probes (C44 shapes only)
- **No reuse** of C40/C41/C42/C43 scripts/shapes. Durable per-probe logs under `/home/runner/work/_temp/kilo-tmp/c44_probes/`.
- **New surfaces/shapes (distinct from C43):**
  - `beta.py`: `calculate_beta_fast` edge cases, `_calc_rolling_beta_series` NaN propagation, `estimate_betas` with min_obs > window, benchmark with all-NaN window, multi-asset rolling with mixed finite/NaN.
  - `data_loader.py`: `detect_and_normalize_exchange_format` with BINANCE/KRAKEN/COINBASE specific quirks, `normalize_schema` with duplicate columns, `load_returns` with partitioned parquet, timezone conversion edge cases (DST transitions).
  - `strategy.py`: `run()` with regime_filter + beta_neutral enforcement combined, `report()` with degenerate backtest (all NaN returns), `tear_sheet()` with missing metrics, config aliases (window vs beta_window, min_obs vs min_observations).
  - `costs.py`: `compute_transaction_costs` with time-varying adv_usd DataFrame misaligned index, participation_cap at boundary (0.0, 1.0), borrow_bps_per_year = 0, fixed_fee_per_trade with zero turnover.
  - `regime.py`: `regime_scale_scalar` with empty returns, `classify_volatility_regimes_percentile` with quantile boundaries (0.0, 1.0), `_apply_vol_hysteresis` with hysteresis > threshold spread, `mean_reversion_zscore` with zero std.
  - `shorting.py`: `apply_shorting_constraints` with signals (not weights) input, borrowable dict with cascading wildcards, strict mode with multiple violations, max_short_exposure = 0.
  - `sizing.py`: `apply_position_sizing` with sizer as string shorthand, returns DataFrame with fewer columns than signals, lookback == data length, max_leverage < 1.0.
  - `signals.py`: `generate_bab_signals` with long_quantile + short_quantile > 1.0, quantiles at 0.0/1.0 boundaries, beta DataFrame with all-NaN rows/columns.
  - `portfolio.py`: `construct_portfolio` with dollar_neutral=False, gross_exposure_limit binding, net_exposure_limit binding, max_single_weight < equal weight.
  - `backtest.py`: `run_backtest` with transaction_costs as Series vs float, slippage as DataFrame vs float, weights with NaN rows.
- **Required NEW cross-interactions (distinct from C43):**
  - `beta` + `sizing` (beta used in Kelly/VolTarget sizing)
  - `data_loader` + `strategy` (data_loader output directly fed to strategy.run)
  - `costs` + `sizing` (costs affect returns used for sizing)
  - `shorting` + `sizing` (shorting constraints applied before/after sizing)
  - `regime` + `signals` (regime scaling applied to signals before portfolio construction)
  - `portfolio` + `backtest` (portfolio weights directly backtested with costs)
  - `attribution` + `costs` (cost drag attribution accuracy)
- Maintain probe matrix (id, target, shape, result, log path). Minimum 20 probes.

### 3) On proven regression/gap
Smallest fix in allowed editable area only → minimal regression test → re-run affected tests + all three gates → durable evidence.

### 4) On no proven gaps
Record **"C44 rotation: no proven gaps"** only with per-area/per-probe evidence and log paths.

### 5) Before exit (mandatory)
Refresh this file with: timestamp/HEAD, gate results+log paths, full C44 probe matrix, fixes/tests added (if any), working-tree notes, and **next concrete heavy task**. If C44 closes cleanly, **immediately define and start C45** (≥20 new probes, new shapes, durable logs) and leave it binding.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except a newly proven controller/workflow sync regression reproduced with durable evidence (smallest proven fix only).
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `shorting.py`, `sizing.py`, `quality.py`, `data_sources.py`, `attribution.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.

(End of file)
