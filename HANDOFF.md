# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T18:22:00Z
**HEAD:** `aea56aa` — `chore(kilo): checkpoint agent session` (2026-11-13 18:16:19 +0000, working tree: clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> This is the **single source of truth**. `AGENT_HANDOFF.md` is a pointer only.
> Read this whole file before doing anything. Do not create a second handoff.
> If any number here conflicts with a live run, **the live run wins** — re-record it and note the delta.

---

## State reconciliation (verified this session, 2026-11-13T18:22:00Z)

**Gate baseline (re-verified this session, not inherited):** `bash scripts/bab_gate.sh`
→ **5373 passed, 35 skipped, RC=0** (this run **656.99 s** ≈ 657 s; coverage ~97%).

- The **657 s** figure is the honest wall-clock on this host right now. A prior record said
  **~446 s**. Treat the gate as **"≤ 15 min"** budget; do not panic at 657 s, and do not
  claim 446 s as current. (The 35 "skipped" are pytest deselected skips; a raw
  `--collect-only` counts 5408, of which 35 are skipped at run time — that 35-gap is expected,
  not a regression.)
- Test files are **unchanged since the recorded baseline** (`git diff 0f1bd55..HEAD -- tests`
  is empty). So the recorded baseline is trustworthy; only the wall-clock label was stale.

**Working tree:** clean. No active blockers. No R2 files present
(no `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`,
`tests/test_bab_scale_perf_guard.py`).

**R1 campaign — CLOSED (do not reopen):**
- R1-A Causality / no-lookahead — `tests/test_bab_causal_no_lookahead.py`.
- R1-B Real-data E2E invariants — `tests/test_bab_real_data_e2e.py` (68 tests / 10 fixtures).
- R1-C Independent naive-oracle parity — `tests/test_bab_real_data_oracle.py` (51 tests,
  `np.linalg.lstsq` + loop oracle vs product at `rtol=atol=1e-12`).
- R1-D E2E performance guard — `tests/test_bab_e2e_performance_guard.py`.

**Empirical evidence (this checkout, current HEAD):**
- Oracle parity (real fixtures, `beta_window=90`, `min_obs=60`): rolling-beta / signal /
  portfolio / one-step-backtest all match the independent oracle at `rtol=atol=1e-12`,
  over `beta_neutral` {F,T} × `dollar_neutral` {F,T} × costs/slippage on/off. No divergence.
- Beta-neutral convergence (`real_market_prices.csv`, w90): `portfolio_beta = -5.15e-5`
  (target 0.0, tol 1e-4); `max|Σw| = 5.0e-16`.
- Real-data E2E invariants on all 10 fixtures pass (backtest contract, DN, beta target,
  attribution/totals identities, strict-JSON report, non-empty tear_sheet, determinism).

**Interpretation:** the engine is correct, causal, oracle-verified, and fast on real data.
The remaining existential risk for a *trading strategy* is **regime breakdown** (BAB fails
exactly when the spread inverts: crashes, correlation→1, liquidity evaporation,
leverage-driven deleveraging) and **scale**. R2 is the only standing work. **R1 is closed.**

---

## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T18:22:00Z) — BINDING (DO FIRST)

> **Inference from repo name:** `crypto-betting-against-beta` → the BAB engine *is* the
> product. Correctness (R1) is locked and oracle-verified. So the next session must **stress
> the engine against hostile regimes and scale, with measured performance ceilings**, and
> **harden any real defect found** — not re-run correctness proofs, not add unit tests to a
> layer that is already proven.
>
> **Binding objective:** Ship **R2 — Economic Stress & Scale Robustness** as *new test files*
> with hard assertions and recorded measurements. This is a **heavy campaign** (real synthetic
> frames, hostile-regime injectors, a long-horizon drawdown/limit sweep, and a scale guard).
> **Partial completion is not acceptable.** If a stage is blocked, record exact evidence and
> move to the next — do not stop the session. See "Definition of Done" below: the session is
> **not done** until all three stages are committed-and-green or explicitly downgraded with
> evidence in this file.

### MANDATORY PRE-CHECK (do not skip — it is what makes progress non-avoidable)
Before writing any test, confirm the exact R2 files do not already exist (a `-k` filter is
**not** reliable here: `-k "scale_perf"` matches the unrelated
`test_data_quality_stale_run_vectorized.py::...::test_production_scale_perf_ceiling`):
```bash
ls tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py 2>&1
```
If all three report **"No such file or directory"**, the R2 campaign is genuinely unstarted —
proceed to build it. If any file exists: **run that file first**, record pass/fail, and only
extend it — never duplicate.

### API facts you must use (verified this session — do not guess)
- `from strategies.betting_against_beta import BABStrategy`
- Construct: `BABStrategy(benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3,
  transaction_costs=0.0, slippage=0.0, beta_neutral=True, dollar_neutral=True)`
- Run: `res = strat.run(returns_df=df)` where `df` is a `pd.DataFrame` of **simple returns**
  (index = dates, columns = asset names; **one column must equal `benchmark`**).
- Result fields: `res.betas`, `res.signals`, `res.weights`, `res.backtest` (all `pd.DataFrame`).
  `res.backtest` columns: **`returns`, `gross_return`, `cost_drag`, `slippage_drag`, `cumulative`**.
- `res.weights` rows are the book weights; per-period net exposure = `weights.sum(axis=1)`
  (dollar-neutral ⇒ `|Σw| ≤ 1e-9`); gross = `weights.abs().sum(axis=1)`.
- Reports: `strat.report(res)` → dict with `"metrics"`; `strat.tear_sheet(res)` → non-empty `str`;
  `strat.report_to_json(report)` → strict JSON string.
- Synthetic helper already present: `strategies.betting_against_beta.data.generate_synthetic_returns`.
  For hostile regimes, **build your own deterministic frame** (seed fixed) so the injector is
  reproducible — do not rely on the default generator.

### Measured baselines you must NOT regress (9 reps, warm, this host)
| Frame      | median run time | ceiling to assert |
|------------|-----------------|-------------------|
| 5000 × 200 | **297 ms**      | **≤ 0.8 s**       |
| 5000 × 500 | **759 ms**      | **≤ 2.0 s**       |
| 5000 × 40  | **53 ms**       | (informational)   |

### Stage R2-A — Hostile-regime injector + BAB behavior (new `tests/test_bab_stress_regimes.py`)
Build a reusable, deterministic regime-injector that takes one base return frame and produces
variants: **(1) correlation→1** (all assets collapse onto the benchmark), **(2) crash**
(benchmark −5σ multi-day then partial recovery), **(3) liquidity evaporation** (return
magnitude ×5 with fat tails), **(4) dispersion spike** (idiosyncratic vol ×5), **(5) trend
reversal** (sign flip of benchmark drift).
For each regime, run `BABStrategy.run` across `beta_neutral` {F,T} × `dollar_neutral` {F,T} ×
costs on/off and assert: **all outputs finite**; **dollar-neutral when configured**
(`max|Σw| ≤ 1e-9`); **causal sanity** (betas at `t` use only data ≤ `t` — perturb a future row
and assert earlier betas are byte-identical); **turnover/cost attribution present**
(`cost_drag`/`slippage_drag` finite and ≥ 0); `report()`/`tear_sheet()` finite + strict-JSON.
**Record** measured max drawdown, worst single-period return, and max turnover per regime.
Add a **spread-inversion detector**: assert net exposure and beta stay bounded (do not explode)
under correlation→1; record worst-case numbers.

### Stage R2-B — Long-horizon drawdown & limit sweep (new `tests/test_bab_stress_horizon.py`)
Synthetic **5000×200** and **5000×40** frames (seed fixed). Sweep `beta_window` ∈ {60,90,120},
`long/short_quantile` ∈ {0.1,0.3,0.5}, `transaction_costs` ∈ {0, 0.001, 0.005},
`slippage` ∈ {0, 0.0005}. Assert finiteness, dollar neutrality, determinism (same seed ⇒ same
result). **Record** worst-case max drawdown / Sharpe / turnover across the grid. Regression
ceiling: **no configuration may produce a non-finite cumulative or `|Σw| > 1e-9`** when
dollar-neutral. Cap total grid runtime (it is a sweep — sample or bound reps so the file stays
under ~60 s; record the chosen reduction).

### Stage R2-C — Scale performance guard (new `tests/test_bab_scale_perf_guard.py`)
Measure `BABStrategy.run` at **5000×200** and **5000×500** (`beta_neutral=True`), **median of 9
reps**, warm. Assert the ceilings in the table above (≤ 0.8 s, ≤ 2.0 s). Fail loudly if a
change regresses scale runtime by an order of magnitude. This makes scale regressions
*impossible to ignore*.

### Session exit requirements (mandatory — all must hold)
1. All new targeted tests pass:
   `PYTHONPATH=. python3 -m pytest tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py -q`
2. `bash scripts/bab_gate.sh` → **RC=0** (record passed/skipped/RC/wall-clock; green baseline is
   **5373 passed, 35 skipped, RC=0**; expect ~650 s).
3. Record **measured numbers** for every stage (drawdowns, worst period, turnover, runtimes) —
   not "no defect found" prose.
4. If a genuine defect is found (non-finite output, dollar-neutrality breach, lookahead leak,
   order-of-magnitude perf regression at scale), **fix the product code** with a focused
   regression test; do not weaken an assertion to make it pass.
5. Refresh this `HANDOFF.md` (timestamp, HEAD, gate result, shipped changes, next candidates) and
   keep `AGENT_HANDOFF.md` pointer-only and in sync.
6. Commit nothing unless explicitly requested (the controller checkpoints).

**Anti-churn / execution rules (binding):** ship code/tests + measured evidence, not commentary;
no probe-count campaigns; no re-profiling old baselines except as before/after for code you change
now; no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`); no
weakening/deleting protected tests (see Locks). If a stage yields no measurable finding after a
genuine implementation attempt, record the evidence and move to the next stage — do not stop.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single
  `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8
  scatter, all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value
  oracle; parity tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block
  renormalization + net-fix. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass, ≤50 passes, per-window
  min-norm correction. **Locked** (convergence is bounded by the pass cap and per-window
  `cnt ≥ min_obs`; on tiny/degenerate series a small residual drift is expected — do not "fix"
  it without a reproducible production-scale defect).
- `backtest.py` `run_backtest`: NaN-masked matmul, clipped `returns` (`max(net, -1+1e-12)`),
  log1p/cumsum/exp cumulative, final finite-repair sanitize, reuses `w_shifted` for turnover.
  **Locked.**
- `strategy.py` finiteness guard: single-pass. **Locked.**
- `attribution.py`: single-pass `_finite_series`/`_finite_sum`, `trade_attribution` adopts the
  finite `returns` column as `net_return`. **Closed.**
- R1-A/B/C/D suites are shipped; do not weaken.
- `scripts/bench_beta_neutrality.py` + `tests/test_beta_neutrality_performance.py` are the
  canonical bench/oracle-guard artifacts for the locked hot spot.

---

## Known contracts (so you don't mistake them for bugs)

- **`returns` column is clipped:** `run_backtest` reports `returns = clip(gross − cost − slip,
  lower=-1+1e-12)` so `log1p` stays finite. The raw attribution identity
  `returns == gross − cost − slip` holds only where the floor is inactive (all-finite fixtures).
  `trade_attribution.net_return == returns` always.
- **NaN returns are masked to 0** by `run_backtest`'s matmul and the final finite-repair. On
  fixtures with genuine NaN returns, `gross_return` drops those periods while cost/slippage
  still accrue, so the strict totals identity `net == gross − cost − slip` holds on all-finite
  fixtures; on NaN fixtures assert `net_return == sum(returns)`.
- **Beta-neutral convergence is bounded** by the ≤50-pass cap and per-window `cnt ≥ min_obs`.
  The exact `|portfolio_beta − target| ≤ 1e-4` contract is asserted on the two large price
  fixtures (enough post-warmup history); on tiny/degenerate fixtures assert "no worse than
  un-enforced" instead.
- **All-NaN delisted columns are dropped** by the loader (`ALT` in `all_nan_column.csv` does not
  appear in weights).

---

## Environment / bottlenecks (current) — and their removals

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis
  present. `coverage` **is** installed (gate prints a report, ~97% total). `pytest-xdist` absent.
- **Bottleneck 1 — full gate ~650 s.** REMOVAL: iterate on the targeted R2 files
  (`pytest tests/test_bab_stress_*.py ...`) while developing; run the full
  `bash scripts/bab_gate.sh` **once** per session before recording. Never gate a per-file loop.
- **Bottleneck 2 — probe-count / C-number rotation campaigns.** REMOVAL: prohibited (see Locks).
  Progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
  No `probe*`/`debug*`/`ast_probe.py` at repo root (root probe files exist and are **tracked**;
  do not touch them). Use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **Bottleneck 3 — re-profiling old recorded baselines.** REMOVAL: only before/after for code you
  change now. Do not re-open historical diagnostics as current failures.
- **No active blocker:** gate baseline is green; working tree clean. The only standing work is R2.

---

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression
  tests + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as
  current failures.

---

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug
  scripts; `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for
  new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`,
  `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or
  `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific
  reproducible defect + tests.
- Commit nothing unless explicitly requested.

---

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**