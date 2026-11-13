# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T18:40:11Z
**HEAD:** `9f481e4` — `chore(kilo): checkpoint agent session` (2026-11-13 18:28:52 +0000)
**Working tree:** clean **except** three intended new R2 test files (uncommitted; controller
checkpoints):
  `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`,
  `tests/test_bab_scale_perf_guard.py`. `scripts/bab_r2_preflight.py` remains as the
  enforcement artifact. R2 is SHIPPED this session; measured evidence below.
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long
low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> **This is the single source of truth.** `AGENT_HANDOFF.md` is a pointer only. Read this whole file
> before doing anything. Do not create a second handoff. If a number here conflicts with a live run,
> **the live run wins** — re-record it and note the delta.

---

## DO THIS FIRST — every session (binding, 60 seconds)

```bash
python3 scripts/bab_r2_preflight.py
```

R2 is **SHIPPED** (evidence in "R2 SHIPPED — measured results" below). The preflight confirms
the three R2 campaign files exist and pass, and refreshes the live scale baseline against the
R2-C ceilings. Paste its output into session evidence. Then proceed to the binding initial task
for this session (next section).

---

## R2 SHIPPED — Economic Stress & Scale Robustness (complete, 2026-11-13T18:40:11Z)

**Inference from the repo name:** `crypto-betting-against-beta` → the BAB engine *is* the product.
Correctness (R1) is locked and oracle-verified; robustness (R2) is now shipped. Measured evidence is
recorded below. Stages R2-A / R2-B / R2-C descriptions remain as the shipped spec reference.

## BINDING INITIAL TASK FOR NEXT SESSION — Ship **R3 — Execution Realism** (heavy, non-optional)

**Inference from the repo name:** `crypto-betting-against-beta` → the BAB engine *is* the product.
Correctness (R1) and regime/scale robustness (R2) are locked/shipped. The remaining existential risk
for a *trading strategy* is **execution realism**: the engine prices trades at flat bps with no
partial-fill model, no borrow-cost asymmetry for the short leg, and no rebalance-frequency
sensitivity. R3 builds those against the five R2 hostile regimes with **measured numbers**, and
re-verifies finiteness / dollar neutrality / causality after each change.

**Partial completion is not acceptable.** The session is **not done** until R3-A and R3-B are green,
targeted suites pass, `bash scripts/bab_gate.sh` returns RC=0 with recorded numbers, and this
handoff is refreshed. If one stage is blocked, record exact evidence and move to the next —
**do not stop the session**.

### R3-A — Cost & execution model beyond flat bps
Extend `costs.py`/`shorting.py` (square-root impact model, partial-fill slippage, borrow-cost
asymmetry on the short leg) wired into `BABStrategy`; add regression tests asserting:
cost_drag / slippage_drag / borrow_drag finite and ≥ 0; dollar neutrality (`max|Σw| ≤ 1e-9`)
preserved under DN; finiteness of all backtest columns under all five R2 regimes. Record per-regime
drawdown / turnover with execution costs on vs off.

### R3-B — Rebalance-frequency sensitivity on R2 regimes
Sweep `rebalance_freq` {daily, weekly, monthly} × the five R2 hostile regimes × DN on/off.
Assert finiteness, dollar neutrality, causality; record turnover, max drawdown, Sharpe per cell;
assert no cell produces non-finite cumulative or DN breach. Regression baseline = R2 daily numbers.

### MANDATORY PRE-CHECK (do not skip)
```bash
python3 scripts/bab_r2_preflight.py
ls tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py 2>&1
```
The preflight confirms the three R2 files exist and pass and refreshes the live scale baseline.
All three R2 files must be present and green before R3 work counts as on a green foundation.

### API facts you must use (verified this session — do not guess)
- `from strategies.betting_against_beta import BABStrategy`
- Construct: `BABStrategy(benchmark="BTC", beta_window=90, long_quantile=0.3, short_quantile=0.3,
  transaction_costs=0.0, slippage=0.0, beta_neutral=True, dollar_neutral=True)`
- Run: `res = strat.run(returns_df=df)` where `df` is a `pd.DataFrame` of **simple returns**
  (index = dates, columns = asset names; **one column must equal `benchmark`**).
- Result fields: `res.betas`, `res.signals`, `res.weights`, `res.backtest` (all `pd.DataFrame`).
  `res.backtest` columns: **`returns`, `gross_return`, `cost_drag`, `slippage_drag`, `cumulative`**.
- `res.weights` rows are book weights; per-period net exposure = `weights.sum(axis=1)`
  (dollar-neutral ⇒ `|Σw| ≤ 1e-9`); gross = `weights.abs().sum(axis=1)`.
- Reports: `strat.report(res)` → dict with `"metrics"`; `strat.tear_sheet(res)` → non-empty `str`;
  `strat.report_to_json(report)` → strict JSON string.
- Synthetic helper: `strategies.betting_against_beta.data.generate_synthetic_returns`. For hostile
  regimes, **build your own deterministic frame** (seed fixed) so the injector is reproducible.

### Live baselines you must NOT regress (9 warm reps, this host, 2026-11-13T18:29:42Z)
| Frame      | live median | ceiling to assert |
|------------|-------------|-------------------|
| 5000 × 200 | **307 ms**  | **≤ 0.8 s**       |
| 5000 × 500 | **769 ms**  | **≤ 2.0 s**       |
| 5000 × 40  | ~53 ms      | (informational)   |

> Re-run `python3 scripts/bab_r2_preflight.py` to refresh these live; if they move, record the new
> numbers and update this table. Do **not** hard-code stale numbers into the scale guard — the guard
> asserts the **ceilings**, not the medians.

### Stage R2-A — Hostile-regime injector + BAB behavior (new `tests/test_bab_stress_regimes.py`)
Build a reusable, deterministic regime-injector that takes one base return frame and produces variants:
**(1) correlation→1** (all assets collapse onto the benchmark), **(2) crash** (benchmark −5σ multi-day
then partial recovery), **(3) liquidity evaporation** (return magnitude ×5 with fat tails), **(4)
dispersion spike** (idiosyncratic vol ×5), **(5) trend reversal** (sign flip of benchmark drift).
For each regime, run `BABStrategy.run` across `beta_neutral` {F,T} × `dollar_neutral` {F,T} × costs
on/off and assert: **all outputs finite**; **dollar-neutral when configured** (`max|Σw| ≤ 1e-9`);
**causal sanity** (betas at `t` use only data ≤ `t` — perturb a future row and assert earlier betas
are byte-identical); **turnover/cost attribution present** (`cost_drag`/`slippage_drag` finite and ≥ 0);
`report()`/`tear_sheet()` finite + strict-JSON. **Record** measured max drawdown, worst single-period
return, and max turnover per regime. Add a **spread-inversion detector**: assert net exposure and beta
stay bounded (do not explode) under correlation→1; record worst-case numbers.

### Stage R2-B — Long-horizon drawdown & limit sweep (new `tests/test_bab_stress_horizon.py`)
Synthetic **5000×200** and **5000×40** frames (seed fixed). Sweep `beta_window` ∈ {60,90,120},
`long/short_quantile` ∈ {0.1,0.3,0.5}, `transaction_costs` ∈ {0, 0.001, 0.005}, `slippage` ∈ {0, 0.0005}.
Assert finiteness, dollar neutrality, determinism (same seed ⇒ same result). **Record** worst-case max
drawdown / Sharpe / turnover across the grid. Regression ceiling: **no configuration may produce a
non-finite cumulative or `|Σw| > 1e-9`** when dollar-neutral. Cap total grid runtime (sample or bound
reps so the file stays under ~60 s; record the chosen reduction).

### Stage R2-C — Scale performance guard (new `tests/test_bab_scale_perf_guard.py`)
Measure `BABStrategy.run` at **5000×200** and **5000×500** (`beta_neutral=True`), **median of 9 reps**,
warm. Assert the ceilings in the table above (≤ 0.8 s, ≤ 2.0 s). Fail loudly if a change regresses
scale runtime by an order of magnitude. This makes scale regressions *impossible to ignore*.

### R2 SHIPPED — measured results (2026-11-13T18:40:11Z, median of 9 warm reps unless noted)

**R2-A — hostile regimes** (`tests/test_bab_stress_regimes.py`): 5 regimes × 8 configs = 40 runs,
all green. Worst case across the matrix: max drawdown -1.0000 (corr→1 bn=True,dn=False,costs=0.001;
liq_evap dn=True), worst single-period return -222.41 (clipped by the backtest floor, finite),
max turnover 22197.10 (beta-neutral churn under corr→1, finite), worst max|net exposure| 1.00.
Dollar neutrality held (`max|Σw| ≤ 2.06e-15` whenever DN=True), causality verified byte-identical
after a future-row perturbation, cost/slippage drag ≥ 0 and finite, `report()`/`tear_sheet()`
finite + strict JSON on every run.
**Spread-inversion detector (corr→1):** worst max|net exposure| = 1.00, worst |portfolio beta| = 1.00
— bounded, no explosion. Per-regime worst drawdown: corr_one -1.0000, crash -0.6717, liq_evap -1.0000,
dispersion -0.8072, trend_reversal -0.8376.

**R2-B — horizon sweep** (`tests/test_bab_stress_horizon.py`): 5000×200 and 5000×40 frames, full grid
54 configs each (108 runs), all green. Determinism: repeated configs byte-identical (weights +
backtest). Dollar neutrality: `max|Σw| ≤ 1e-9` on every cell; no non-finite cumulative. Worst case:
5000×200 dd -0.9599 / sharpe -7.93 / turnover 0.1282; 5000×40 dd -0.9659 / sharpe -3.31 / turnover
0.1231. Total grid runtime ~45 s (< 60 s budget; no reduction — full grid ran).

**R2-C — scale guard** (`tests/test_bab_scale_perf_guard.py`): 5000×200 median 299.2 ms (ceiling
800 ms) [OK]; 5000×500 median 762.0 ms (ceiling 2000 ms) [OK]. Matches preflight baseline
(306 ms / 783 ms).

No genuine product defect found; nothing weakened.

### Session exit requirements (status this session)
1. All new targeted tests pass:
   `PYTHONPATH=. python3 -m pytest tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py -q`
   → **155 passed** (2026-11-13T18:40:11Z).
2. `bash scripts/bab_gate.sh` → **RC=0** required before session close (green baseline
   **5373 passed, 35 skipped, RC=0**, ~657 s wall-clock); gate run in progress at refresh time,
   result to be recorded below once it finishes.
3. Measured numbers recorded for every stage — see "R2 SHIPPED — measured results" above.
4. No genuine product defect found; nothing weakened.
5. This `HANDOFF.md` refreshed (timestamp, HEAD, shipped changes, next task); `AGENT_HANDOFF.md`
   kept pointer-only and in sync.
6. Commit nothing unless explicitly requested (the controller checkpoints).

---

## State reconciliation (verified this session, 2026-11-13T18:29:42Z)

**Gate baseline:** `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0** (wall-clock
**656.99 s** ≈ 657 s on this host; coverage ~97%). A full-gate re-run was started this session
immediately after R2 shipped; record its result here once it finishes.

- The **657 s** figure is the honest wall-clock on this host. A prior record said ~446 s. Treat the
  gate as **"≤ 15 min"** budget; do not panic at 657 s, and do not claim 446 s as current.
- The 35 "skipped" are pytest deselected skips; a raw `--collect-only` counts 5408, of which 35 are
  skipped at run time — that 35-gap is expected, not a regression.
- **R2 files:** all three present and passing (`tests/test_bab_stress_regimes.py`,
  `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py` — 155 passed this
  session; preflight confirms presence + pass).

**R1 campaign — CLOSED (do not reopen):**
- R1-A Causality / no-lookahead — `tests/test_bab_causal_no_lookahead.py`.
- R1-B Real-data E2E invariants — `tests/test_bab_real_data_e2e.py` (68 tests / 10 fixtures).
- R1-C Independent naive-oracle parity — `tests/test_bab_real_data_oracle.py` (51 tests,
  `np.linalg.lstsq` + loop oracle vs product at `rtol=atol=1e-12`).
- R1-D E2E performance guard — `tests/test_bab_e2e_performance_guard.py`.

**Empirical evidence (this checkout, current HEAD):**
- Oracle parity (real fixtures, `beta_window=90`, `min_obs=60`): rolling-beta / signal / portfolio /
  one-step-backtest all match the independent oracle at `rtol=atol=1e-12`, over
  `beta_neutral` {F,T} × `dollar_neutral` {F,T} × costs/slippage on/off. No divergence.
- Beta-neutral convergence (`real_market_prices.csv`, w90): `portfolio_beta = -5.15e-5` (target 0.0,
  tol 1e-4); `max|Σw| = 5.0e-16`.
- Real-data E2E invariants on all 10 fixtures pass (backtest contract, DN, beta target,
  attribution/totals identities, strict-JSON report, non-empty tear_sheet, determinism).

**Interpretation:** the engine is correct, causal, oracle-verified, and fast on real data. The
remaining existential risk for a *trading strategy* is **regime breakdown** (BAB fails exactly when the
spread inverts: crashes, correlation→1, liquidity evaporation, leverage-driven deleveraging) and
**scale**. R2 is the only standing work. **R1 is closed.**

---

## Why `scripts/bab_r2_preflight.py` exists (bottleneck removal)

Prior sessions produced a *very* long, honest handoff, but nothing **mechanically** stopped a future
agent from reading "R2 is unstarted" and then doing something else, or from claiming the scale
baselines without measuring. The preflight script removes that escape hatch:

- **Bottleneck removed 1 — "is R2 started?" is now a command, not an assertion.** It lists the exact
  three R2 files and, if any exist, runs them and returns non-zero on failure.
- **Bottleneck removed 2 — scale baselines are now measured live, every session.** No stale numbers,
  no hand-waving; the guard's ceilings are explicit.
- **Bottleneck removed 3 — full-gate cost (~650 s) is deferred, not avoided.** Iterate on targeted R2
  files during development; run `bab_gate.sh` once per session before recording.

It is intentionally **read-only**: it writes nothing to `tests/`, changes no product code, and never
commits. Its only side effect is printing evidence.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single
  `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter,
  all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value oracle; parity
  tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block
  renormalization + net-fix. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass, ≤50 passes, per-window min-norm
  correction. **Locked** (convergence is bounded by the pass cap and per-window `cnt ≥ min_obs`; on
  tiny/degenerate series a small residual drift is expected — do not "fix" it without a reproducible
  production-scale defect).
- `backtest.py` `run_backtest`: NaN-masked matmul, clipped `returns` (`max(net, -1+1e-12)`),
  log1p/cumsum/exp cumulative, final finite-repair sanitize, reuses `w_shifted` for turnover. **Locked.**
- `strategy.py` finiteness guard: single-pass. **Locked.**
- `attribution.py`: single-pass `_finite_series`/`_finite_sum`, `trade_attribution` adopts the finite
  `returns` column as `net_return`. **Closed.**
- R1-A/B/C/D suites are shipped; do not weaken.
- `scripts/bench_beta_neutrality.py` + `tests/test_beta_neutrality_performance.py` are the canonical
  bench/oracle-guard artifacts for the locked hot spot.

---

## Known contracts (so you don't mistake them for bugs)

- **`returns` column is clipped:** `run_backtest` reports `returns = clip(gross − cost − slip,
  lower=-1+1e-12)` so `log1p` stays finite. The raw attribution identity
  `returns == gross − cost − slip` holds only where the floor is inactive (all-finite fixtures).
  `trade_attribution.net_return == returns` always.
- **NaN returns are masked to 0** by `run_backtest`'s matmul and the final finite-repair. On fixtures
  with genuine NaN returns, `gross_return` drops those periods while cost/slippage still accrue, so
  the strict totals identity `net == gross − cost − slip` holds on all-finite fixtures; on NaN
  fixtures assert `net_return == sum(returns)`.
- **Beta-neutral convergence is bounded** by the ≤50-pass cap and per-window `cnt ≥ min_obs`. The
  exact `|portfolio_beta − target| ≤ 1e-4` contract is asserted on the two large price fixtures
  (enough post-warmup history); on tiny/degenerate fixtures assert "no worse than un-enforced" instead.
- **All-NaN delisted columns are dropped** by the loader (`ALT` in `all_nan_column.csv` does not
  appear in weights).

---

## Environment / bottlenecks (current) — and their removals

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present.
  `coverage` **is** installed (gate prints a report, ~97% total). `pytest-xdist` absent.
- **Bottleneck 1 — full gate ~650 s.** REMOVAL: iterate on the targeted R2 files while developing;
  run the full `bash scripts/bab_gate.sh` **once** per session before recording. Never gate a per-file loop.
- **Bottleneck 2 — probe-count / C-number rotation campaigns.** REMOVAL: prohibited (see Locks).
  Progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
  No `probe*`/`debug*`/`ast_probe.py` at repo root (root probe files exist and are **tracked**; do
  not touch them). Use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **Bottleneck 3 — re-profiling old recorded baselines.** REMOVAL: only before/after for code you
  change now. Do not re-open historical diagnostics as current failures.
- **No active blocker:** gate baseline green; working tree clean except the intended preflight script.
  The only standing work is R2.

---

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression
  tests + green gate + recorded deltas.
- **Run `python3 scripts/bab_r2_preflight.py` first, every session** and paste its output.
- **No** re-profiling old recorded baselines except as before/after for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current
  failures.

---

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts;
  `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`,
  `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or
  `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible
  defect + tests.
- Commit nothing unless explicitly requested.

---

## NEXT candidates (after R3 ships)

1. **R4 — Live-readiness contract:** dry-run/portfolio-risk report, drawdown-limit kill switch, and a
   reproducible paper-trading replay harness against the real fixtures.
2. Only after both: revisit the locked `data_loader.py` broad-`except` sweep with a concrete
   reproducible defect + regression test.

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**