# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T15:30:44Z
**HEAD:** `2cbd77a` — `chore(kilo): checkpoint agent session` (R1-A causal harness + R1-D perf guard committed; tree clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Working tree:** CLEAN — no uncommitted changes, no stashes, no branches.

---

## State reconciliation (2026-11-13T15:30:44Z)

**Gate is GREEN:** `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, ~372 s**.

**R1 campaign status:**
- R1-A Causality / no-lookahead — **SHIPPED**: `tests/test_bab_causal_no_lookahead.py` committed (real fixtures + synthetic 2500×120, parametrized over beta_neutral/dollar_neutral/rebalance_freq/costs, pre-cut identity + post-cut change). Verified passing.
- R1-B Real-data E2E invariant suite — **PARTIAL**: `tests/test_bab_real_data_e2e.py` exists but only covers finite cumulative + dollar neutrality on two fixtures. **Not yet to spec:** missing the full fixture set (`returns.json`, `all_nan_column.csv`, `benchmark_nan_window.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `messy_returns.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv`), beta-target assertion, attribution/report/totals identities at `rtol=atol=1e-12`, strict-JSON `report()`, `tear_sheet()` non-empty, determinism, all-NaN + date-gap coverage.
- R1-C Independent naive-oracle parity — **NOT STARTED**: no `tests/test_bab_real_data_oracle.py`. This is the **primary remaining campaign**.
- R1-D E2E performance guard — **SHIPPED**: `tests/test_bab_e2e_performance_guard.py` committed (2500×120 `beta_neutral=True`, ceiling 0.60 s; baseline median ~102 ms this session). Verified passing.

Empirical evidence captured previously (scratch: `/home/runner/work/_temp/kilo-tmp/`):
- Real-data E2E (`load_prices`, `beta_window=90`): beta_neutral portfolio_beta ≈ -5e-5, max|Σw| ≈ 5e-16, attribution identity 0.0, runtimes ~5-6 ms per fixture.
- Causality probe: pre-cut weights/betas identical (max|delta| = 0.0), post-cut weights change (non-vacuous).
- E2E performance baseline (warm, seed=1234, `beta_neutral=True`, 2500×120): median **102.0 ms** (min 95.0 / max 120.5, 9 reps).

Interpretation: the core engine is correct and causal on real data, but **independent-oracle parity (R1-C) is not yet tested**, and **R1-B is not yet to spec**. That is the next campaign.

---

## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T15:30:44Z) — BINDING

> **Inference from repo name:** `crypto-betting-against-beta` → the BAB engine is the product. The core math (`beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py` finiteness) is locked, optimized, and proven. The highest-value remaining work is **independent-oracle parity on real data plus a complete real-data E2E invariant suite**. This is the **BAB Real-Data Correctness Campaign (R1), stages B-finalize + C**.
>
> **Binding objective:** Ship R1-C end-to-end and bring R1-B to full spec. **Both stages are mandatory.** Partial completion is not acceptable; if a stage is blocked, record the exact evidence and move to the next stage — do not stop the session.
>
> **Stage R1-C — Independent naive-oracle parity on real data (new file `tests/test_bab_real_data_oracle.py`):**
> - Write a deliberately naive, **loop-based** reference implementation, independent of the vectorized code, for:
>   1. Rolling beta: per-asset OLS slope over each rolling window (`np.linalg.lstsq` with intercept, per window), degenerate/insufficient windows -> NaN.
>   2. Signal ranking: per-row sort by beta; long bottom `long_quantile`, short top `short_quantile`; disjoint sets (shrink short if overlap); single-asset rows flat.
>   3. Portfolio construction: equal-weight long/short, dollar-neutral (weights sum to 0), guard divide-by-zero.
>   4. One-step backtest: lagged weights (no lookahead), P&L = sum(w_shifted * returns), cost_drag = turnover * transaction_costs, slippage_drag = turnover * slippage, cumulative via log1p/cumsum/exp.
> - Compare against `calculate_rolling_beta`, `generate_bab_signals`, `construct_portfolio`, and `run_backtest` on the real fixtures (`real_market_prices.csv`, `real_market_prices_expanded.csv`) at `rtol=atol=1e-12`, parametrized over `beta_neutral` ∈ {False, True} and costs/slippage on/off.
> - Compare full `BABStrategy.run` output (betas, signals, weights, backtest) between oracle and product at `rtol=atol=1e-12`.
> - If any divergence is found, fix the product code and add a focused regression; if none, record the parity evidence with concrete numbers. Do **not** edit locked files without reproducible evidence.
>
> **Stage R1-B (finalize) — Real-data E2E invariant suite (extend `tests/test_bab_real_data_e2e.py`):**
> - Load all fixtures through `load_prices`/`load_returns`: `real_market_prices.csv`, `real_market_prices_expanded.csv`, `returns.json`, `all_nan_column.csv`, `benchmark_nan_window.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `messy_returns.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv`.
> - Assert, parametrized over `beta_neutral` and costs/slippage: backtest contract (columns, monotonic index, all finite); **dollar neutrality** (`max|Σw| ≤ 1e-9` when `dollar_neutral`); **beta target** (`portfolio_beta` within `beta_tolerance` of `beta_target` when `beta_neutral`); **attribution identity** (`net == gross - cost_drag - slippage_drag` at `rtol=atol=1e-12`); totals identity; `report()` finite and strict-JSON (`json.dumps(..., allow_nan=False)`); `tear_sheet()` non-empty; determinism across two runs.
> - Explicitly cover the all-NaN delisted column and the mid-series date gap; assert no exception and finite output.
>
> **Session exit requirements (mandatory):**
> 1. Targeted tests for every new/changed file pass (`pytest tests/test_bab_real_data_oracle.py tests/test_bab_real_data_e2e.py`).
> 2. `bash scripts/bab_gate.sh` → **RC=0** (record passed/skipped/RC/time; green baseline is 5204 passed, 35 skipped, RC=0, ~372 s).
> 3. Record per-stage evidence: measured before/after or parity/no-defect results, with concrete numbers.
> 4. Refresh `HANDOFF.md` (timestamp, HEAD, gate result, shipped changes, remaining candidates/status) and keep `AGENT_HANDOFF.md` pointer-only and in sync.
> 5. Commit nothing unless explicitly requested (the controller checkpoints).
>
> **Anti-churn / execution rules (binding):** ship code/tests, not commentary; no probe-count campaigns; no re-profiling old baselines except as before/after for code you change; no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`); no weakening/deleting protected tests (see Locks). If a stage yields no measurable win / no defect after a genuine implementation attempt, document the evidence and immediately move to the next stage; do not stop the session.

---

## Evidence (this session, current checkout)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` not installed (gate runs without coverage).
- **Full gate:** `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, ~372 s**.
- **R1 suites verified passing:** `test_bab_causal_no_lookahead.py test_bab_real_data_e2e.py test_bab_e2e_performance_guard.py` → **56 passed** (53.16s).
- **Attribution suites:** `test_bab_attribution.py test_bab_attribution_extra.py test_bab_attribution_extra2.py` → **28 passed**.
- **Lock checks:** `tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → 27 passed.
- **Historical note:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts (old SHAs/runs/tool noise); treat as historical diagnostics only, not current failures.

---

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.** (`_reference_generate_bab_signals` is the value oracle; parity tests must not modify it.)
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix retained for oracle fidelity. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass implementation. **Locked unless regression evidenced.**
- `backtest.py` `run_backtest`: final numpy finite-repair sanitize; reuses `w_shifted` for turnover. **Locked unless regression evidenced.**
- `strategy.py` finiteness guard: single-pass. **Locked unless regression evidenced.**
- `attribution.py`: single-pass `_finite_series` / `_finite_sum` with defensive fallbacks and `TestAttributionSanitizationParity`. **Closed.**
- `scripts/bench_beta_neutrality.py` and `tests/test_beta_neutrality_performance.py` are the canonical bench/oracle-guard artifacts for the locked hot spot.
- R1-A `tests/test_bab_causal_no_lookahead.py` and R1-D `tests/test_bab_e2e_performance_guard.py` are shipped; do not weaken.

---

## Environment / bottlenecks (current)

- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` missing.
- **Full gate ~372 s.** Use targeted suites while iterating; run the full gate once before recording.
- **No active blocker:** gate is green; tree is clean. The only genuine gap is R1-C (oracle parity) + R1-B finalize.
- **Scratch:** `/home/runner/work/_temp/kilo-tmp/`. Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.

---

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after measurements for code you change now.
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

(End of file - total 119 lines)