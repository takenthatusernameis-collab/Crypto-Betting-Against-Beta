# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T20:30:49Z
**HEAD:** `258f660` — `chore(kilo): checkpoint agent session` (main)
**Working tree (at refresh):** clean. `git status --porcelain` empty. R2 files (`tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py`, `scripts/bab_r2_preflight.py`) are now **committed** at this HEAD. `__pycache__` is gitignored noise — do not commit.
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

**Preflight result (this refresh, 2026-11-13T20:30:49Z @ `258f660`, in the venv above):**
- `python3 scripts/bab_r2_preflight.py` → **rc=0**. R2 files present and **all pass (155 passed, 6 warnings, ~35.5 s)**.
- Live scale baseline (median of 9 warm reps): **5000×200 = 161 ms** (ceiling 800 ms) [OK]; **5000×500 = 392 ms** (ceiling 2000 ms) [OK].

**Status correction (resolves the prior "unverified" bottleneck):** R2 is **no longer unverified**.
The earlier `rc=1 / "No module named pytest"` was purely an environment artifact, not a product or test
defect. R2 is now **re-proven green on `258f660`/this env**. Do **not** re-litigate R2; treat it as shipped.

---

## BINDING INITIAL TASK (next session) — Ship **R3 — Execution Realism** (heavy, non-optional)

**Inference from repo name (`crypto-betting-against-beta`):** the BAB engine is the product. R1 (correctness/oracle/perf) and R2 (regime + horizon + scale stress) are **closed and green**. The next existential risk for a *trading* strategy is **execution realism**: the engine's backtest applies only flat `transaction_costs` and flat `slippage`, while the richer `TransactionCostModel` (square-root impact, participation cap, ADV-scaled impact, short borrow asymmetry) and any partial-fill/slippage realism are **implemented but never wired into `BABStrategy.run()`**. That is the heavy work below.

**No partial completion.** Session is not done until: (1) R3-A wiring + regression tests are green and recorded, (2) R3-B rebalance-frequency sweep is implemented and measured, (3) `bash scripts/bab_gate.sh` RC=0 recorded, (4) this handoff refreshed with evidence. If one stage blocks, record exact evidence and continue to the next — do not stop.

### Confirmed gap (file:line evidence — do not re-discover)
- `strategies/betting_against_beta/costs.py` fully implements `TransactionCostModel` + `compute_transaction_costs` (linear fee + bid-ask on turnover, `impact = trade·coeff·sqrt(min(|dw|·price/adv, cap))`, pro-rata borrow on short notional). Already unit-tested in `tests/test_betting_against_beta_costs.py` + `tests/test_bab_costs_coverage_campaign2.py`.
- `strategies/betting_against_beta/backtest.py:112-120` accepts `cost_model`/`prices_df`/`adv_usd` and subtracts `compute_transaction_costs` from returns — so the model is reachable **only** via a direct `run_backtest(..., cost_model=...)` call.
- `strategies/betting_against_beta/strategy.py:402` calls `run_backtest(returns, weights, transaction_costs=cfg.transaction_costs, slippage=cfg.slippage)` — **it never passes `cost_model`, `prices_df`, or `adv_usd`.** `BABConfig` has no `cost_model`/`prices`/`adv` fields (`config.py:43-103`). So through the public `BABStrategy.run()` entrypoint the impact/borrow model is **dead code**; the strategy silently uses flat bps only.
- `backtest.py` also has **no partial-fill/slippage realism** beyond the flat `slippage_drag` term (`backtest.py:98-109`): a large order is assumed fully filled at the same price, with no participation-driven shortfall.

### Stage 0 — Confirm env green (fast, do not skip)
- Run the preflight block at the top. It must print `PREFLIGHT_RC=0` and the R2 pass line (155 passed). If it does not, fix the **environment** (deps), not the tests; record the fix.

### R3-A — Wire & test realistic execution (impact / participation / borrow asymmetry / partial-fill)
1. **Wire the cost model into the strategy.** Add config fields so the model is reachable from `BABStrategy.run()`:
   - `cost_model: Optional[object] = None` (a `TransactionCostModel` or dict), `prices: Optional[object] = None` (a prices DataFrame or a loader path), `adv_usd: Optional[object] = None` (dict/Series/DataFrame).
   - In `strategy.py`, resolve/construct the model + prices + adv and pass them into `run_backtest(..., cost_model=..., prices_df=..., adv_usd=...)`. Preserve backward compatibility: when `cost_model is None`, behavior must be byte-identical to today (flat `transaction_costs`/`slippage` only) — assert this with a regression test (run with and without the new plumbing; identical backtest when `cost_model` unset).
   - Coerce a dict `cost_model` into `TransactionCostModel` (mirror the existing `shorting_constraints` dict-coercion pattern in `config.py:107-118` and `strategy.py`); raise `BABDataError`/`BABConfigError` on a wrong type rather than silently ignoring it (mirror `shorting_constraints` strictness).
2. **Borrow-cost asymmetry surfaced in results/attribution.** The model already charges borrow on short notional; ensure the wired path makes the **short-side drag** measurable/attributable (e.g. a `borrow_drag`-like breakdown or a test that compares a long-biased vs short-biased book under identical borrow cost and asserts the short book pays strictly more). If adding a dedicated `borrow_drag` column to `backtest` risks breaking the locked column contract (`["returns","gross_return","cost_drag","slippage_drag","cumulative"]`, asserted in R2 and many R1 tests), instead expose borrow via the existing `cost_drag` and assert the asymmetry on `cost_drag` — **do not** change the locked backtest columns.
3. **Partial-fill / participation-aware slippage realism.** Add an opt-in participation-driven shortfall (e.g. a `partial_fill`/`max_participation`-style knob) that, when enabled, scales realized fills/impact by participation vs a liquidity budget so a large order in a thin asset is penalized more than a small one. When disabled, it must be a no-op (bit-identical to flat slippage). Keep it strictly opt-in and finite (`≥ 0`, no NaN/inf).
4. **Regression tests (new file, e.g. `tests/test_bab_execution_realism_r3.py`):** on the **five R2 hostile regimes** (import the injector from `tests/test_bab_stress_regimes.py` — reuse `REGIMES`/`REGIME_BUILDERS`/`_base_frame`, do not duplicate the injector), assert:
   - With `cost_model` wired: all backtest columns finite; `cost_drag` finite and `≥ 0`; `max|Σw| ≤ 1e-9` when dollar-neutral; every column finite across all five hostile regimes.
   - **Costs-on vs costs-off measured** per regime: drawdown, turnover, and total `cost_drag` with model on vs off (record the deltas; assert model-on total drag `≥` flat-only when impact/borrow are positive).
   - **Borrow asymmetry:** under identical borrow cost, a book with more short notional pays strictly more `cost_drag` than a long-biased book.
   - **Backward-compat:** `cost_model=None` path is byte-identical to the pre-R3 flat path (compare to a run with `transaction_costs=cfg.transaction_costs`).
   - `report()`/`tear_sheet()` finite + strict JSON on every wired run.

### R3-B — Rebalance-frequency sensitivity (execution × regime)
- Sweep `rebalance_freq` ∈ {`daily`, `weekly`, `monthly`} × the **5 R2 hostile regimes** × dollar_neutral on/off (and with the R3-A cost model enabled), asserting: all outputs finite; dollar neutrality when configured; causality (betas at `t` use only data ≤ `t`); no non-finite cumulative or `|Σw|` breach.
- **Record** turnover, max drawdown, Sharpe per cell, and the **measured** relationship between rebalance frequency and turnover (weekly/monthly should reduce turnover vs daily; assert the ordering holds, not a hard-coded number). Regression baseline = R2 daily numbers for the daily cells (must not regress vs R2-A recorded worst-case drawdowns).

### MANDATORY EVIDENCE TO RECORD (paste into the refresh)
- Preflight output (post-env-setup), targeted R2 + R3 command results, `bash scripts/bab_gate.sh` RC/counts/timing, per-regime/per-cell measured metrics, and any defect+fix. Refresh `HANDOFF.md` (and keep `AGENT_HANDOFF.md` pointer-only). Commit nothing unless explicitly requested.

### API facts you must use (verified — do not guess)
- `from strategies.betting_against_beta import BABStrategy`
- Construct: `BABStrategy(benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3,
  transaction_costs=0.0, slippage=0.0, beta_neutral=True, dollar_neutral=True)` — plus the new R3-A kwargs (`cost_model`, `prices`, `adv_usd`) once wired.
- Run: `res = strat.run(returns_df=df)` where `df` is a `pd.DataFrame` of **simple returns** (index = dates, columns = assets; **one column must equal `benchmark`**).
- Result fields: `res.betas`, `res.signals`, `res.weights`, `res.backtest` (all `pd.DataFrame`). `res.backtest` columns: **`returns`, `gross_return`, `cost_drag`, `slippage_drag`, `cumulative`** (locked — do not add/remove without updating every dependent test and the R2 column assertion).
- `res.weights` rows are book weights; per-period net exposure = `weights.sum(axis=1)` (dollar-neutral ⇒ `|Σw| ≤ 1e-9`); gross = `weights.abs().sum(axis=1)`.
- Reports: `strat.report(res)` → dict with `"metrics"`; `strat.tear_sheet(res)` → non-empty `str`; `strat.report_to_json(report)` → strict JSON string.
- `TransactionCostModel` (`costs.py`): `linear_fee`, `bid_ask_bps`, `impact_coefficient`, `participation_cap` (∈ (0,1]), `borrow_bps_per_year`, `fixed_fee_per_trade`, `trading_days_per_year`, `adv_usd`. `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd=...)` returns a per-period `pd.Series` named `transaction_costs` (≥ 0, finite).
- Synthetic helper: `strategies.betting_against_beta.data.generate_synthetic_returns`; for hostile regimes **build your own deterministic frame** (reuse `tests/test_bab_stress_regimes.py::_base_frame` / `REGIMES`).

### Live baselines you must NOT regress (9 warm reps, this host, 2026-11-13T20:30:49Z)
| Frame      | live median | ceiling to assert |
|------------|-------------|-------------------|
| 5000 × 200 | **161 ms**  | **≤ 0.8 s**       |
| 5000 × 500 | **392 ms**  | **≤ 2.0 s**       |
| 5000 × 40  | ~35 ms      | (informational)   |

> The scale guard asserts the **ceilings**, not the medians. If wiring `cost_model`/`adv` into `strategy.run()` slows the default (no-model) path, that is a regression — keep the default path model-free and only pay the cost-model overhead when it is actually configured.

### R2 VERIFIED GREEN — measured results (re-proven this refresh, 2026-11-13T20:30:49Z @ `258f660`)
- **R2-A** (`tests/test_bab_stress_regimes.py`) + **R2-B** (`tests/test_bab_stress_horizon.py`) + **R2-C** (`tests/test_bab_scale_perf_guard.py`): **155 passed, 6 warnings, ~35.5 s**, preflight `rc=0`.
- **R2-C scale** (this env, median of 9 warm reps): 5000×200 = **161 ms** (≤ 800 ms), 5000×500 = **392 ms** (≤ 2000 ms).
- Prior-session full-gate green baseline: **5373 passed, 35 skipped, RC=0** (~657 s, ~97% cov). Re-run `bash scripts/bab_gate.sh` this session before closing R3.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value oracle; parity tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass, ≤50 passes, per-window min-norm correction. **Locked** (convergence bounded by pass cap and per-window `cnt ≥ min_obs`; on tiny/degenerate series a small residual drift is expected — do not "fix" without a reproducible production-scale defect).
- `backtest.py` `run_backtest`: NaN-masked matmul, clipped `returns` (`max(net, -1+1e-12)`), log1p/cumsum/exp cumulative, final finite-repair sanitize, reuses `w_shifted` for turnover. **Locked.** `cost_model` path exists (do not break its `TypeError`-on-non-model contract, `backtest.py:113`).
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