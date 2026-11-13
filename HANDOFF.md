# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T17:24:19Z
**HEAD:** `f7fe638` — `chore(kilo): checkpoint agent session` (working tree: clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).

> This is the **single source of truth**. `AGENT_HANDOFF.md` is a pointer only.
> Read this whole file before doing anything. Do not create a second handoff.

---

## State reconciliation (2026-11-13T17:24:19Z)

**Gate is GREEN:** `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0, ~446 s**
(baseline was 5204 passed; **+169** new tests, zero regressions).

**Working tree:** clean (all R1 deliverables committed).

**R1 campaign status — ALL STAGES SHIPPED:**
- R1-A Causality / no-lookahead — **SHIPPED** (`tests/test_bab_causal_no_lookahead.py`).
- R1-B Real-data E2E invariant suite — **SHIPPED (full spec)**: `tests/test_bab_real_data_e2e.py`, **68 tests** across all 10 fixtures.
- R1-C Independent naive-oracle parity — **SHIPPED**: `tests/test_bab_real_data_oracle.py`, **51 tests**, naive loop/lstsq oracle vs product at `rtol=atol=1e-12`.
- R1-D E2E performance guard — **SHIPPED** (`tests/test_bab_e2e_performance_guard.py`).

**Empirical evidence (this checkout, current HEAD):**
- Oracle parity (real fixtures, `beta_window=90`, `min_obs=60`): rolling-beta / signal / portfolio / one-step-backtest all match the independent `np.linalg.lstsq` + loop oracle at `rtol=atol=1e-12`, parametrized over `beta_neutral` {F,T}, `dollar_neutral` {F,T}, costs/slippage on/off — **no divergence found, no product defect, no locked file touched.**
- Beta-neutral convergence (`real_market_prices.csv`, w90): `portfolio_beta = -5.15e-5` (target 0.0, tol 1e-4); `max|Σw| = 5.0e-16`.
- Beta signal count on the real fixture: 3110/3582 finite rolling betas (warm-up + NaN windows correctly NaN).
- Real-data E2E invariants on all 10 fixtures: backtest contract, dollar neutrality, beta target (finite + no-worse-than-plain on tiny fixtures), attribution/totals identities, strict-JSON report, non-empty tear_sheet, determinism — all pass.

**Interpretation:** the core engine is correct, causal, oracle-verified, and fast on real data. The *next* highest-value work is **not** more of the same unit/oracle layer — it is **economically-adversarial, scale-and-stress robustness with performance ceilings** (R2, below). R1 is closed.

---

## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T17:24:19Z) — BINDING

> **Inference from repo name:** `crypto-betting-against-beta` → the BAB engine *is* the product. Correctness (R1) is now locked and oracle-verified. A trading strategy's remaining existential risk is **regime breakdown** (the BAB trade historically fails exactly when the spread inverts: crashes, correlation→1, liquidity evaporation, leverage-driven deleveraging) and **scale**. The next session must therefore **stress the engine against hostile regimes and scale, with measured performance ceilings**, and **harden any real defect found** — not re-run correctness proofs.
>
> **Binding objective:** Ship **R2 — Economic Stress & Scale Robustness** as *new test files* with hard assertions and recorded measurements. This is a **heavy campaign**: it must include genuinely large synthetic frames, hostile-regime injectors, a long-horizon drawdown/limit sweep, and a scale guard. **Partial completion is not acceptable**; if one stage is blocked, record exact evidence and move to the next — do not stop the session.
>
> **Stage R2-A — Hostile-regime injector + BAB behavior (new `tests/test_bab_stress_regimes.py`):**
> - Build a reusable regime-injector that produces, from one base return frame, deterministic variants: (1) **correlation→1** (all assets collapse onto the benchmark), (2) **crash** (benchmark −5σ multi-day then partial recovery), (3) **liquidity evaporation** (return magnitude ×5 with fat tails), (4) **dispersion spike** (idiosyncratic vol ×5), (5) **trend reversal** (sign flip of benchmark drift).
> - For each regime, run `BABStrategy.run` across `beta_neutral` {F,T} × `dollar_neutral` {F,T} × costs on/off and assert: **all outputs finite**, **dollar-neutral when configured**, **no lookahead** (pre-cut identity vs an un-injected baseline is impossible by construction — instead assert *causal sanity*: betas at t use only data ≤ t under injection), **turnover/cost attribution present**, `report()`/`tear_sheet()` finite + strict-JSON. **Record measured max drawdown, worst single-period return, and max turnover per regime.**
> - Add a **spread-inversion detector** test: assert the strategy's net exposure and beta stay bounded (do not explode) when correlation→1, and document the observed worst-case numbers.
>
> **Stage R2-B — Long-horizon drawdown & limit sweep (new `tests/test_bab_stress_horizon.py`):**
> - Synthetic 5000×200 (seed fixed) and 5000×40 frames. Sweep `beta_window` ∈ {60,90,120}, `long/short_quantile` ∈ {0.1,0.3,0.5}, costs ∈ {0, 0.001, 0.005}, slippage ∈ {0, 0.0005}. Assert finiteness, dollar neutrality, determinism, and **record worst-case max drawdown / Sharpe / turnover** across the grid. Add a regression ceiling: **no configuration may produce a non-finite cumulative or a |Σw| > 1e-9** when dollar-neutral.
>
> **Stage R2-C — Scale performance guard (extend the perf guard family; new `tests/test_bab_scale_perf_guard.py`):**
> - Measure `BABStrategy.run` at **5000×200** and **5000×500** (`beta_neutral=True`). Record median runtime (9 reps). Baseline measured this session (3 reps, warm): **5000×200 ≈ 303 ms**, **5000×500 ≈ 780 ms**. Set **hard ceilings** (start at ~2–2.5× the measured median, e.g. **≤ 0.8 s** for 5000×200 and **≤ 2.0 s** for 5000×500; tighten only with evidence). Fail loudly if a change regresses scale runtime by an order of magnitude. This makes scale regressions *impossible to ignore*.
>
> **Session exit requirements (mandatory):**
> 1. All new targeted tests pass: `pytest tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py`.
> 2. `bash scripts/bab_gate.sh` → **RC=0** (record passed/skipped/RC/time; green baseline is **5373 passed, 35 skipped, RC=0, ~446 s**).
> 3. Record **measured numbers** for every stage (drawdowns, worst period, turnover, runtimes) — not "no defect found" prose.
> 4. If a genuine defect is found (non-finite output, dollar-neutrality breach, lookahead leak, order-of-magnitude perf regression at scale), **fix the product code** with a focused regression test; do not weaken an assertion to make it pass.
> 5. Refresh `HANDOFF.md` (timestamp, HEAD, gate result, shipped changes, next candidates) and keep `AGENT_HANDOFF.md` pointer-only and in sync.
> 6. Commit nothing unless explicitly requested (the controller checkpoints).
>
> **Anti-churn / execution rules (binding):** ship code/tests + measured evidence, not commentary; no probe-count campaigns; no re-profiling old baselines except as before/after for code you change now; no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`); no weakening/deleting protected tests (see Locks). If a stage yields no measurable finding after a genuine implementation attempt, record the evidence and move to the next stage — do not stop the session.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value oracle; parity tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass, ≤50 passes, per-window min-norm correction. **Locked** (note: convergence is bounded by the pass cap and per-window `cnt ≥ min_obs`; on tiny/degenerate series a small residual drift is expected — do not "fix" it without a reproducible production-scale defect).
- `backtest.py` `run_backtest`: NaN-masked matmul, clipped `returns` (`max(net, -1+1e-12)`), log1p/cumsum/exp cumulative, final finite-repair sanitize, reuses `w_shifted` for turnover. **Locked.**
- `strategy.py` finiteness guard: single-pass. **Locked.**
- `attribution.py`: single-pass `_finite_series`/`_finite_sum`, `trade_attribution` adopts the finite `returns` column as `net_return`. **Closed.**
- R1-A/B/C/D suites (`test_bab_causal_no_lookahead.py`, `test_bab_real_data_e2e.py`, `test_bab_real_data_oracle.py`, `test_bab_e2e_performance_guard.py`) are shipped; do not weaken.
- `scripts/bench_beta_neutrality.py` + `tests/test_beta_neutrality_performance.py` are the canonical bench/oracle-guard artifacts for the locked hot spot.

---

## Known contracts (so you don't mistake them for bugs)

- **`returns` column is clipped:** `run_backtest` reports `returns = clip(gross − cost − slip, lower=-1+1e-12)` so `log1p` stays finite. The raw attribution identity `returns == gross − cost − slip` holds only where the floor is inactive (all-finite fixtures). `trade_attribution.net_return == returns` always.
- **NaN returns are masked to 0** by `run_backtest`'s matmul and the final finite-repair. On fixtures with genuine NaN returns, `gross_return` drops those periods while cost/slippage still accrue, so the strict totals identity `net == gross − cost − slip` holds on all-finite fixtures; on NaN fixtures assert `net_return == sum(returns)`.
- **Beta-neutral convergence is bounded** by the ≤50-pass cap and per-window `cnt ≥ min_obs`. The exact `|portfolio_beta − target| ≤ 1e-4` contract is asserted on the two large price fixtures (enough post-warmup history); on tiny/degenerate fixtures assert "no worse than un-enforced" instead.
- **All-NaN delisted columns are dropped** by the loader (`ALT` in `all_nan_column.csv` does not appear in weights).

---

## Environment / bottlenecks (current)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` missing (gate runs without coverage).
- **Full gate ~446 s.** Use targeted suites while iterating; run the full gate once before recording.
- **No active blocker:** gate is green; the only uncommitted work is the two R1 test deliverables above.
- **Scratch:** `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.

---

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.

---

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**