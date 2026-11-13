# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T20:46:15Z
**HEAD:** `d8cf5b1` — `chore(kilo): checkpoint agent session` (main). Working tree: clean.
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> **This is the single source of truth.** `AGENT_HANDOFF.md` is a pointer only. Read this whole file
> before doing anything. Do not create a second handoff. If a number here conflicts with a live run,
> **the live run wins** — re-record it and note the delta.

---

## DO THIS FIRST — every session (binding, ~90 seconds)

The environment in this sandbox has **no Python deps by default** (numpy/pandas/pytest all missing).
Remove that bottleneck first, then run the preflight. Do not skip to "work" on a broken env.

```bash
# 1. Remove env bottleneck (idempotent; reuses the venv if present).
VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis" "coverage"

# 2. Preflight (read-only measurement): R2 pass/fail + live scale baseline.
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
```

**IMPORTANT state delta since the last R2 verification:** `backtest.py`/`config.py`/`strategy.py` changed at `d8cf5b1` (R3-A wiring committed after R2 was last proven green at `258f660`). The default (no-model) path is *intended* to be byte-identical, but that is **unproven against `d8cf5b1`**. Re-run the preflight and reconcile R2 against `d8cf5b1` before treating R2 as shipped. Do **not** claim R2 green on `d8cf5b1` without a fresh `PREFLIGHT_RC=0`.

**Status correction (resolves the prior "unverified" bottleneck):** the earlier `rc=1 / "No module named pytest"` was purely an environment artifact, not a product defect. The env fix is the top-of-file venv block. Do **not** claim "pytest missing" as a blocker — install it.

---

## BINDING INITIAL TASK (next session) — Finish **R3 — Execution Realism** (heavy, non-optional)

**Inference from repo name (`crypto-betting-against-beta`):** the BAB engine is the product. R1 (correctness/oracle/perf) is closed. R2 (regime + horizon + scale stress) was green at `258f660` but must be re-verified against `d8cf5b1` (see Stage 0). The next existential risk for a *trading* strategy is **execution realism**.

**R3-A code is SHIPPED** (committed at `d8cf5b1` — see "Confirmed gap / done" below). What remains is the **test + measure + gate** work:

**No partial completion.** Session is not done until: (1) R2 re-verified green on `d8cf5b1` (preflight `rc=0`, 155 passed), (2) R3-A regression tests written and green, (3) R3-B rebalance-frequency sweep implemented and measured, (4) `bash scripts/bab_gate.sh` RC=0 recorded, (5) this handoff refreshed with evidence. If one stage blocks, record exact evidence and continue to the next — do not stop.

### R3-A status — code done, tests missing (file:line evidence — do not re-discover)

**DONE (committed `d8cf5b1`):**
- `config.py:104-117` — `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation` fields added to `BABConfig`.
- `config.py:133-169` — `__post_init__` coerces a dict `cost_model` into `TransactionCostModel` (mirrors `shorting_constraints` dict-coercion at `config.py:121-132`); raises `BABConfigError` on wrong type; validates `partial_fill` is bool and `max_participation ∈ (0,1]`.
- `strategy.py` — added `_resolve_cost_model(cfg)` static method; `run()` now passes `cost_model`, `prices_df`, `adv_usd`, `partial_fill`, `max_participation` into `run_backtest()`. When `cost_model is None`, returns `(None, None, None)` → byte-identical pre-R3 flat path.
- `backtest.py:189-197` — `cost_model` path still applies `compute_transaction_costs(weights, weights_prev, prices_df, cost_model, adv_usd=...)`.
- `backtest.py:138-176` — opt-in `partial_fill`/`max_participation` participation-aware slippage; no-op when disabled (bit-identical to flat slippage).
- Locked columns preserved: `["returns","gross_return","cost_drag","slippage_drag","cumulative"]` (backtest.py:241-247).

**TODO — R3-A regression tests (new file `tests/test_bab_execution_realism_r3.py`):**
Reuse the R2 hostile-regime injector from `tests/test_bab_stress_regimes.py` (`REGIMES`/`REGIME_BUILDERS`/`_base_frame`; do not duplicate the injector). On the **five R2 hostile regimes**, assert:
- With `cost_model` wired: all backtest columns finite; `cost_drag` finite and `≥ 0`; `max|Σw| ≤ 1e-9` when dollar-neutral; every column finite across all five regimes.
- **Costs-on vs costs-off per regime:** drawdown, turnover, and total `cost_drag` with model on vs off (record deltas; assert model-on total drag `≥` flat-only when impact/borrow positive).
- **Borrow asymmetry:** under identical borrow cost, a book with more short notional pays strictly more `cost_drag` than a long-biased book.
- **Backward-compat:** `cost_model=None` path byte-identical to pre-R3 flat path (compare to a run with `transaction_costs=cfg.transaction_costs`).
- `report()`/`tear_sheet()` finite + strict JSON on every wired run.
- Wrong-typed `cost_model` raises `BABConfigError`/`BABDataError` (never silently ignored).

### R3-B — Rebalance-frequency sensitivity (execution × regime)
- Sweep `rebalance_freq` ∈ {`daily`, `weekly`, `monthly`} × the **5 R2 hostile regimes** × dollar_neutral on/off (with the R3-A cost model enabled), asserting: all outputs finite; dollar neutrality when configured; causality (betas at `t` use only data ≤ `t`); no non-finite cumulative or `|Σw|` breach.
- **Record** turnover, max drawdown, Sharpe per cell, and the measured relationship between rebalance frequency and turnover (weekly/monthly should reduce turnover vs daily; assert the ordering holds, not a hard-coded number). Regression baseline = R2 daily numbers for the daily cells (must not regress vs R2-A recorded worst-case drawdowns).

### MANDATORY EVIDENCE TO RECORD (paste into the refresh)
- Preflight output (post-env-setup) vs `d8cf5b1`; targeted R2 + R3 command results; `bash scripts/bab_gate.sh` RC/counts/timing; per-regime/per-cell measured metrics; any defect+fix. Refresh `HANDOFF.md` (keep `AGENT_HANDOFF.md` pointer-only). Commit nothing unless explicitly requested.

### API facts you must use (verified — do not guess)
- `from strategies.betting_against_beta import BABStrategy`
- Construct: `BABStrategy(benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3, transaction_costs=0.0, slippage=0.0, beta_neutral=True, dollar_neutral=True)` — plus the new R3-A kwargs (`cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation`).
- Run: `res = strat.run(returns_df=df)` where `df` is a `pd.DataFrame` of **simple returns** (index = dates, columns = assets; **one column must equal `benchmark`**).
- Result fields: `res.betas`, `res.signals`, `res.weights`, `res.backtest` (all `pd.DataFrame`). `res.backtest` columns: **`returns`, `gross_return`, `cost_drag`, `slippage_drag`, `cumulative`** (locked — do not add/remove without updating every dependent test and the R2 column assertion).
- `res.weights` rows are book weights; per-period net exposure = `weights.sum(axis=1)` (dollar-neutral ⇒ `|Σw| ≤ 1e-9`); gross = `weights.abs().sum(axis=1)`.
- Reports: `strat.report(res)` → dict with `"metrics"`; `strat.tear_sheet(res)` → non-empty `str`; `strat.report_to_json(report)` → strict JSON string.
- `TransactionCostModel` (`costs.py`): `linear_fee`, `bid_ask_bps`, `impact_coefficient`, `participation_cap` (∈ (0,1]), `borrow_bps_per_year`, `fixed_fee_per_trade`, `trading_days_per_year`, `adv_usd`. `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd=...)` returns a per-period `pd.Series` named `transaction_costs` (≥ 0, finite).
- Synthetic helper: `strategies.betting_against_beta.data.generate_synthetic_returns`; for hostile regimes **build your own deterministic frame** (reuse `tests/test_bab_stress_regimes.py::_base_frame` / `REGIMES`).

### Live baselines you must NOT regress (re-measure on `d8cf5b1` this session)
| Frame      | live median (at `258f660`) | ceiling to assert |
|------------|---------------------------|-------------------|
| 5000 × 200 | **161 ms**                | **≤ 0.8 s**       |
| 5000 × 500 | **392 ms**                | **≤ 2.0 s**       |
| 5000 × 40  | ~35 ms                    | (informational)   |

> The scale guard asserts the **ceilings**, not the medians. If wiring `cost_model`/`adv` into `strategy.run()` slows the default (no-model) path, that is a regression — keep the default path model-free and only pay the cost-model overhead when it is actually configured.

---

## R2 VERIFIED GREEN — measured results (at `258f660`, 2026-11-13T20:30:49Z; **RE-VERIFY vs `d8cf5b1`**)
- **R2-A** (`tests/test_bab_stress_regimes.py`) + **R2-B** (`tests/test_bab_stress_horizon.py`) + **R2-C** (`tests/test_bab_scale_perf_guard.py`): **155 passed, 6 warnings, ~35.5 s**, preflight `rc=0`.
- **R2-C scale** (that env, median of 9 warm reps): 5000×200 = **161 ms** (≤ 800 ms); 5000×500 = **392 ms** (≤ 2000 ms).
- Prior-session full-gate green baseline: **5373 passed, 35 skipped, RC=0** (~657 s, ~97% cov). Re-run `bash scripts/bab_gate.sh` this session against `d8cf5b1` before closing R3.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value oracle; parity tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass, ≤50 passes, per-window min-norm correction. **Locked** (convergence bounded by pass cap and per-window `cnt ≥ min_obs`; on tiny/degenerate series a small residual drift is expected — do not "fix" without a reproducible production-scale defect).
- `backtest.py` `run_backtest`: NaN-masked matmul, clipped `returns` (`max(net, -1+1e-12)`), log1p/cumsum/exp cumulative, final finite-repair sanitize, reuses `w_shifted` for turnover. **Locked.** `cost_model` path exists (do not break its `TypeError`-on-non-model contract, `backtest.py:190`).
- `strategy.py` finiteness guard: single-pass. **Locked.**
- `attribution.py`: single-pass `_finite_series`/`_finite_sum`, `trade_attribution` adopts the finite `returns` column as `net_return`. **Closed.**
- R1-A/B/C/D and R2-A/B/C suites are shipped; do not weaken.
- `scripts/bench_beta_neutrality.py` + `tests/test_beta_neutrality_performance.py` are the canonical bench/oracle-guard artifacts.

---

## Known contracts (so you don't mistake them for bugs)

- **`returns` column is clipped:** `run_backtest` reports `returns = clip(gross − cost − slip, lower=-1+1e-12)` so `log1p` stays finite. The raw attribution identity `returns == gross − cost − slip` holds only where the floor is inactive (all-finite fixtures). `trade_attribution.net_return == returns` always.
- **NaN returns are masked to 0** by `run_backtest`'s matmul and the final finite-repair. On fixtures with genuine NaN returns, `gross_return` drops those periods while cost/slippage still accrue; on NaN fixtures assert `net_return == sum(returns)`.
- **Beta-neutral convergence is bounded** by the ≤50-pass cap and per-window `cnt ≥ min_obs`. The exact `|portfolio_beta − target| ≤ 1e-4` contract is asserted on the two large price fixtures; on tiny/degenerate fixtures assert "no worse than un-enforced".
- **All-NaN delisted columns are dropped** by the loader.

---

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
- **Run the preflight (after env setup) first, every session** and paste its output.
- **No** re-profiling old recorded baselines except as before/after for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- **Bottleneck removed (env):** the sandbox ships with no numpy/pandas/pytest; the top-of-file venv block is the single idempotent fix. Do not claim "pytest missing" as a blocker — install it.

---

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts; `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- **No** change to the locked `backtest` columns without updating every dependent test (R2 column assertion + R1 attribution/totals tests) and recording the delta.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---

## NEXT candidates (after R3 ships)

1. **R4 — Live-readiness contract:** dry-run/portfolio-risk report, drawdown-limit kill switch, and a reproducible paper-trading replay harness against the real fixtures.
2. Only after both: revisit the locked `data_loader.py` broad-`except` sweep with a concrete reproducible defect + regression test.

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
