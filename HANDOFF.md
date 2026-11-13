# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T21:27:51Z
**HEAD:** `5e715c5` — `chore(kilo): checkpoint agent session` (main). Working tree: clean at refresh.
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> **This is the single source of truth.** `AGENT_HANDOFF.md` is a pointer only. Read this whole file before doing anything. Do not create a second handoff. If a number here conflicts with a live run, **the live run wins** — re-record it and note the delta.

## INITIAL TASK FOR NEXT SESSION (clear, binding, timestamped)

**As of 2026-11-13T21:27:51Z on `5e715c5`: complete R3 (Execution Realism) end-to-end.** This is not optional and not partially satisfiable.

### Verified this refresh (env bottleneck removed)
- Env bootstrap used: `/home/runner/work/_temp/kilo-tmp/bab-venv` with `numpy==2.5.4 pandas==3.1.1 scipy==1.18.1 pytest==9.2.0 hypothesis==6.170.15 coverage==7.17.3`.
- `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` => **`PREFLIGHT_RC=0`**.
- R2 suites on `5e715c5`: `tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py` => **155 passed, 6 warnings, ~31.9 s**.
- Live scale (median, 9 warm reps, this run): **5000×200 = 164 ms** (ceiling 800 ms), **5000×500 = 384 ms** (ceiling 2000 ms). Default/no-model path still within R2-C ceilings on `5e715c5`.

### Current state (do not rediscover)
- **R1:** closed/locked.
- **R2:** re-verified green on `5e715c5` this refresh (above). Keep green.
- **R3-A code:** SHIPPED at `5e715c5` (`config.py:104-117,133-169` fields+dict-coercion/validation incl. `cost_model`/`partial_fill`/`max_participation`; `strategy.py` `_resolve_cost_model()` + wired `run()` args; `backtest.py` cost_model path and opt-in participation-aware slippage; locked columns preserved `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`).
- **R3-A tests:** **MISSING** (`tests/test_bab_execution_realism_r3.py` does not exist).
- **R3-B:** not implemented/measured (rebalance-frequency sensitivity sweep).
- **Full gate:** not re-run this refresh; prior baseline 5373 passed / 35 skipped / RC=0 (~657 s). Must be proven green on final `HEAD` before closing R3.

### Required work order (heavy; do all)
1. **Start-of-session (every session, ~90s, no excuses):** run env bootstrap + preflight block below; paste output in your notes/handoff refresh. Do not claim blockers like "pytest missing" — install into the venv.
2. **R3-A regression tests** — create `tests/test_bab_execution_realism_r3.py` (reuse `tests/test_bab_stress_regimes.py` hostile-regime builders; do not duplicate injectors):
   - Run on the 5 R2 hostile regimes with cost model wired: all backtest columns finite; `cost_drag` finite and `≥ 0`; dollar-neutral runs have `max|Σw| ≤ 1e-9`; `report()`/`tear_sheet()` finite and `report_to_json` strict JSON.
   - **Costs-on vs costs-off per regime:** record drawdown, turnover, total `cost_drag` deltas; assert model-on total drag `≥` flat-only when impact/borrow positive.
   - **Borrow asymmetry:** identical borrow cost, more short notional ⇒ strictly higher `cost_drag` than long-biased book.
   - **Backward-compat:** `cost_model=None` path byte-identical to pre-R3 flat path (`transaction_costs`/`slippage` only).
   - **Validation:** wrong-typed `cost_model` / invalid config raises `BABConfigError` or `BABDataError` loudly (never silently ignored).
3. **R3-B rebalance-frequency sensitivity** (execution × regime): sweep `rebalance_freq ∈ {daily, weekly, monthly}` × 5 R2 hostile regimes × dollar_neutral on/off with R3-A cost model enabled.
   - Assert: outputs finite, DN when configured, causality preserved (betas at `t` use data ≤ `t`), no non-finite cumulative or `|Σw|` breach.
   - Record per-cell turnover, max drawdown, Sharpe and cost_drag; assert turnover ordering holds (weekly/monthly should reduce turnover vs daily) — no hard-coded targets except invariants/ceilings.
   - Daily cells must not regress vs R2 recorded behavior/ceilings.
4. **Gate and evidence:** run targeted R2 + R3 suites, then `bash scripts/bab_gate.sh` and record RC/counts/timing + per-regime/per-cell metrics + any defect+fix in `HANDOFF.md`. Keep `AGENT_HANDOFF.md` as pointer only. Commit nothing unless explicitly requested.

**Completion bar (all required):** R2 still green on final HEAD, R3-A tests written+green, R3-B implemented+measured+green, `bash scripts/bab_gate.sh` RC=0 recorded, `HANDOFF.md` refreshed with concrete evidence. If a stage blocks, record exact error/evidence and continue to next unblocked stage — do not stop at analysis.

---

## DO THIS FIRST — every session (binding, ~90 seconds)

The sandbox has **no Python deps by default**. Env bottleneck is solved by this idempotent block — run it before any work.

```bash
# 1. Remove env bottleneck (idempotent; reuses venv if present).
VENV=/home/runner/work/_temp/kilo-tmp/bab-venv
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet "numpy==2.5.4" "pandas==3.1.1" "scipy==1.18.1" "pytest==9.2.0" "hypothesis" "coverage"

# 2. Preflight (read-only): R2 pass/fail + live scale baseline.
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py; echo "PREFLIGHT_RC=$?"
```

**Do not** claim "pytest/numpy missing" as a blocker. **Do not** claim R2/R3 green without fresh command evidence on current `HEAD`. If preflight or tests fail, record exact output and fix/continue per completion bar.

---

## R3 execution details (file:line anchors — do not re-discover)

**R3-A shipped (committed `5e715c5`):**
- `config.py:104-117` — `cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation`.
- `config.py:133-169` — dict coercion/validation for `cost_model` (mirrors `shorting_constraints`), `BABConfigError` on wrong type; `partial_fill` bool; `max_participation ∈ (0,1]`.
- `strategy.py` — `_resolve_cost_model(cfg)` + `run()` passes `cost_model`, `prices_df`, `adv_usd`, `partial_fill`, `max_participation` to `run_backtest()`. No-model path remains flat/pre-R3.
- `backtest.py` — `cost_model` path uses `compute_transaction_costs(...)`; opt-in participation-aware slippage; no-op when disabled.
- Locked backtest columns unchanged: `["returns","gross_return","cost_drag","slippage_drag","cumulative"]`.

**R3-A TODO (`tests/test_bab_execution_realism_r3.py`, new):** reuse `tests/test_bab_stress_regimes.py` (`REGIMES`/`REGIME_BUILDERS`/`_base_frame`) over 5 hostile regimes. Cover: finite columns + `cost_drag>=0` + DN `max|Σw|<=1e-9`; costs-on/off recorded deltas (model-on total drag `>=` flat-only when impact/borrow positive); borrow asymmetry (more short notional => strictly higher drag); backward-compat byte-identical default/no-model path; `report()`/`tear_sheet()` finite + strict JSON; wrong-typed `cost_model` raises loudly.

**R3-B TODO:** sweep `rebalance_freq ∈ {daily,weekly,monthly}` × 5 hostile regimes × DN on/off with R3-A cost model enabled. Assert finite outputs, DN/causality/column invariants, no `|Σw|` breach; record turnover/max drawdown/Sharpe/cost_drag per cell; assert turnover ordering weekly/monthly < or ≤ daily trend as measured (invariant-based, no hard-coded numbers except ceilings/non-regression vs R2 daily). Daily cells must not regress vs R2.

**Evidence to record on completion:** preflight on final HEAD, targeted R2+R3 pytest outputs, `bash scripts/bab_gate.sh` RC/counts/timing, per-regime/per-cell metrics table/summary, defects fixed (if any), and refreshed handoff text. Keep `AGENT_HANDOFF.md` pointer-only. No commits unless explicitly requested.

### API facts you must use (verified — do not guess)
- `from strategies.betting_against_beta import BABStrategy`
- Construct: `BABStrategy(benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3, transaction_costs=0.0, slippage=0.0, beta_neutral=True, dollar_neutral=True)` — plus the new R3-A kwargs (`cost_model`, `prices`, `adv_usd`, `partial_fill`, `max_participation`).
- Run: `res = strat.run(returns_df=df)` where `df` is a `pd.DataFrame` of **simple returns** (index = dates, columns = assets; **one column must equal `benchmark`**).
- Result fields: `res.betas`, `res.signals`, `res.weights`, `res.backtest` (all `pd.DataFrame`). `res.backtest` columns: **`returns`, `gross_return`, `cost_drag`, `slippage_drag`, `cumulative`** (locked — do not add/remove without updating every dependent test and the R2 column assertion).
- `res.weights` rows are book weights; per-period net exposure = `weights.sum(axis=1)` (dollar-neutral ⇒ `|Σw| ≤ 1e-9`); gross = `weights.abs().sum(axis=1)`.
- Reports: `strat.report(res)` → dict with `"metrics"`; `strat.tear_sheet(res)` → non-empty `str`; `strat.report_to_json(report)` → strict JSON string.
- `TransactionCostModel` (`costs.py`): `linear_fee`, `bid_ask_bps`, `impact_coefficient`, `participation_cap` (∈ (0,1]), `borrow_bps_per_year`, `fixed_fee_per_trade`, `trading_days_per_year`, `adv_usd`. `compute_transaction_costs(weights, weights_prev, prices, model, adv_usd=...)` returns a per-period `pd.Series` named `transaction_costs` (≥ 0, finite).
- Synthetic helper: `strategies.betting_against_beta.data.generate_synthetic_returns`; for hostile regimes **build your own deterministic frame** (reuse `tests/test_bab_stress_regimes.py::_base_frame` / `REGIMES`).

### Live baselines you must NOT regress (re-measure on `5e715c5` this session)
| Frame      | live median (at `258f660`) | ceiling to assert |
|------------|---------------------------|-------------------|
| 5000 × 200 | **161 ms**                | **≤ 0.8 s**       |
| 5000 × 500 | **392 ms**                | **≤ 2.0 s**       |
| 5000 × 40  | ~35 ms                    | (informational)   |

> The scale guard asserts the **ceilings**, not the medians. If wiring `cost_model`/`adv` into `strategy.run()` slows the default (no-model) path, that is a regression — keep the default path model-free and only pay the cost-model overhead when it is actually configured.

---

## R2 VERIFIED GREEN — measured results
- **At `258f660`, 2026-11-13T20:30:49Z:** R2-A/B/C **155 passed, 6 warnings, ~35.5 s**, preflight `rc=0`; scale 5000×200 **161 ms**, 5000×500 **392 ms**.
- **Re-verified at `5e715c5`, 2026-11-13T21:27:51Z (this refresh):** preflight **`PREFLIGHT_RC=0`**; R2-A/B/C **155 passed, 6 warnings, ~31.9 s**; scale 5000×200 **164 ms** (≤800), 5000×500 **384 ms** (≤2000). R3-A wiring did not regress default/no-model R2 path on this host.
- Prior full-gate baseline (historical, earlier session): **5373 passed, 35 skipped, RC=0** (~657 s). Must be re-run and recorded on final R3 HEAD.

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
