# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T15:19:11Z
**HEAD:** `960e277` — `chore(kilo): checkpoint agent session` (attribution.py finite-repair sanitize + `TestAttributionSanitizationParity`)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs a BTC benchmark (`README.md`, `strategies/betting_against_beta/`).
**Working tree:** 2 modified, uncommitted files (this session's gate-blocker fix):
- `strategies/betting_against_beta/attribution.py` — `_finite_series` now catches `Exception` (was `(TypeError, ValueError)`); `_finite_sum` gained the same defensive `replace([inf,-inf],nan).fillna(0.0)` fallback; trailing newline added.
- `tests/test_bab_attribution.py` — `test_attribution_defensive_fallback_wired` now asserts with the saved `real_isfinite` instead of the monkeypatched `np.isfinite`.

---

## State reconciliation (2026-11-13T15:19:11Z)

**Previous handoff was stale.** It claimed HEAD `a099c71`, 2 modified files, and a PENDING `attribution.py` task. Reality at session start: HEAD `960e277` already shipped that task (attribution single-pass sanitize + `TestAttributionSanitizationParity`), and the tree was clean. This file is now reconciled to the real state.

**Gate was RED at session start — bottleneck removed.**
- `bash scripts/bab_gate.sh` → `1 failed, 5203 passed, 35 skipped, 371.31s`.
- Failure: `tests/test_bab_attribution.py::TestAttributionSanitizationParity::test_attribution_defensive_fallback_wired`.
- Root cause (two defects):
  1. `_finite_series` caught only `(TypeError, ValueError)`, so the forced `RuntimeError` escaped the documented defensive fallback.
  2. `_finite_sum` had no fallback at all, and the test then asserted with the monkeypatched `np.isfinite` instead of the saved `real_isfinite`.
- Fix: broaden `_finite_series` to `except Exception`; add the identical defensive fallback to `_finite_sum`; fix the test assertion. No math/API change; attribution parity at `rtol=atol=1e-12` preserved (all 28 attribution tests pass).
- **Gate now GREEN:** `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, 371.99s**.

**Attribution task (prior session) — EXECUTED at `960e277`:** `_finite_series` / `_finite_sum` collapse the 9 redundant pandas `replace([inf,-inf],nan).fillna(0.0)` passes into one numpy finite-repair pass with an `isfinite` fast path; `TestAttributionSanitizationParity` (8 tests) proves parity at `rtol=atol=1e-12`; defensive fallbacks wired. This surface is now closed.

**Empirical evidence captured this session (scratch: `/home/runner/work/_temp/kilo-tmp/`):**

Real-data E2E (`load_prices` on the shipped fixtures, `beta_window=90`):
| fixture | beta_neutral | shape | runtime | portfolio_beta | max\|Σw\| | attribution identity |
|---|---|---|---|---|---|---|
| `real_market_prices.csv` | False | (398, 5) | ~5.0 ms | -0.434453 | 0.0 | 0.0 |
| `real_market_prices.csv` | True | (398, 5) | ~6.4 ms | -0.000051 | 5.00e-16 | 0.0 |
| `real_market_prices_expanded.csv` | False | (398, 5) | ~4.4 ms | -0.335713 | 0.0 | 0.0 |
| `real_market_prices_expanded.csv` | True | (398, 5) | ~6.1 ms | -0.000067 | 5.59e-16 | 0.0 |

Causality / no-lookahead probe (real fixture, cut at row 200, future returns scaled + ETH shock):
- `weights` before cut: `max|delta| = 0.0`
- `betas` before cut: `max|delta| = 0.0`
- post-cut weights changed: `True` (guards against a vacuous pass)

E2E performance baseline (warm, seed=1234, `BABStrategy.run`, `beta_neutral=True`, 2500×120):
- median **116.0 ms** (min 115.1 / max 119.9), 9 reps, this machine, 2026-11-13.

Interpretation: the core engine is correct and causal on real data, but **these invariants are not yet protected by regression tests**, and there is **no E2E performance guard**. That is the next campaign.

---

## INITIAL TASK FOR THE NEXT AGENTIC SESSION (2026-11-13T15:19:11Z) — PENDING

> **Inference from repo name:** `crypto-betting-against-beta` → the BAB engine is the product. The core math (`beta.py`, `signals.py`, `portfolio.py`, `backtest.py`, `strategy.py` finiteness) is locked, optimized, and proven. The highest-value remaining work is **end-to-end correctness on real market data, causal integrity, independent-oracle parity, and scale/performance regression protection**. This is the **BAB Real-Data & Scale Correctness Campaign (R1)**.
>
> **Binding objective:** Ship the R1 campaign end-to-end: turn the empirical invariants above into permanent regression tests, prove the vectorized engine against an independent naive oracle on real data, fix any divergence with a regression test, and lock E2E performance with a recorded ceiling. **All four stages are mandatory.** Partial completion is not acceptable; if a stage is blocked, record the exact evidence and move to the next stage — do not stop the session.
>
> **Stage R1-A — Causality / no-lookahead harness (new file `tests/test_bab_causal_no_lookahead.py`):**
> - For both real price fixtures (`tests/fixtures/real_market_prices.csv`, `real_market_prices_expanded.csv`) and a synthetic 2500×120 frame: choose a cut index `t`, perturb `returns_df` strictly after `t` (scale returns, add an idiosyncratic shock to one asset), re-run, and assert `weights`, `betas`, `signals`, and `backtest[...]` up to and including `t` are **exactly identical** (not merely close).
> - Assert post-cut outputs **do** change (non-vacuous).
> - Parametrize over `beta_neutral` ∈ {False, True}, `dollar_neutral` ∈ {False, True}, `rebalance_freq` ∈ {daily, weekly, monthly}, and costs/slippage on/off. Keep runtime bounded (real fixtures are ~5 ms/run; cap synthetic at 2500×120).
> - If any divergence is found, fix the product code and add the minimal regression; do not weaken the assertion.
>
> **Stage R1-B — Real-data E2E invariant suite (new file `tests/test_bab_real_data_e2e_invariants.py`):**
> - Load `real_market_prices.csv`, `real_market_prices_expanded.csv`, `returns.json`, plus the degenerate fixtures (`all_nan_column.csv`, `benchmark_nan_window.csv`, `degenerate_metrics.csv`, `junk_columns.csv`, `messy_returns.csv`, `non_monotonic_dates.csv`, `real_data_defects.csv`) through `load_prices`/`load_returns`.
> - Assert, parametrized over `beta_neutral` and costs/slippage: backtest contract (columns, monotonic index, all finite); **dollar neutrality** (`max|Σw| ≤ 1e-9` when `dollar_neutral`); **beta target** (`portfolio_beta` within `beta_tolerance` of `beta_target` when `beta_neutral`); **attribution identity** (`net == gross - cost_drag - slippage_drag` at `rtol=atol=1e-12`); totals identity; `report()` finite and strict-JSON (`json.dumps(..., allow_nan=False)`); `tear_sheet()` non-empty; determinism across two runs.
> - Explicitly cover the all-NaN delisted column and the mid-series date gap; assert no exception and finite output.
>
> **Stage R1-C — Independent naive-oracle parity on real data (new file `tests/test_bab_real_data_oracle.py`):**
> - Write a deliberately naive, loop-based reference for: rolling beta (per-asset OLS over the window), signal ranking (long bottom quantile / short top quantile), portfolio construction (equal-weight, dollar-neutral), and one-step backtest P&L/cost/slippage. Keep the oracle in the test file, independent of the vectorized implementation.
> - Compare against `calculate_rolling_beta`, `generate_bab_signals`, `construct_portfolio`, and `run_backtest` on the real fixtures at `rtol=atol=1e-12`.
> - If any divergence is found, fix the product code and add a focused regression; if none, record the parity evidence. Do not edit locked files without reproducible evidence.
>
> **Stage R1-D — E2E performance guard (new file `tests/test_bab_e2e_performance_guard.py`):**
> - Warm-median `BABStrategy.run` at 2500×120 `beta_neutral=True`; assert under a recorded ceiling (baseline **116 ms** this session → use a ceiling of **0.60 s** to avoid machine noise while still catching order-of-magnitude regressions).
> - Assert `report()` + `tear_sheet()` complete under a ceiling (record the measured value first).
> - Do **not** reopen the locked component benches (`scripts/bench_beta_neutrality.py`, `tests/test_beta_neutrality_performance.py`); only add the E2E guard.
>
> **Session exit requirements (mandatory):**
> 1. Targeted tests for every new/changed file pass.
> 2. `bash scripts/bab_gate.sh` → **RC=0** (record passed/skipped/RC/time; the current green baseline is 5204 passed, 35 skipped, RC=0, ~372 s).
> 3. Record per-stage evidence: measured before/after or parity/no-defect results, with concrete numbers.
> 4. Refresh `HANDOFF.md` (timestamp, HEAD, gate result, shipped changes, remaining candidates/status) and keep `AGENT_HANDOFF.md` pointer-only and in sync.
> 5. Commit nothing unless explicitly requested (the controller checkpoints).
>
> **Anti-churn / execution rules (binding):** ship code/tests, not commentary; no probe-count campaigns; no re-profiling old baselines except as before/after for code you change; no reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`); no weakening/deleting protected tests (see Locks).

---

## Evidence (this session, current checkout)

- **Env:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` not installed (gate runs without coverage).
- **Full gate (after fix):** `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, 371.99s**.
- **Attribution suites:** `tests/test_bab_attribution.py tests/test_bab_attribution_extra.py tests/test_bab_attribution_extra2.py` → **28 passed** (0.59s).
- **Lock checks (prior session, unchanged):** `enforce_beta_neutrality` ~21.6/32.3/58.6 ms @2500x40/50/120; `tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` → 27 passed.
- **Historical note:** `research_state/workflow_run_diagnostics.jsonl` contains prior CI/log excerpts (old SHAs/runs/tool noise); treat as historical diagnostics only, not current failures.

## SHIPPED / LOCKED (do NOT reopen without new reproducible evidence)

- `beta.py` `calculate_rolling_beta`: 2-D stacked rolling sums, hoisted benchmark sums, single `to_numpy(dtype=float)`, vectorized finiteness pass. **Locked.**
- `signals.py` `generate_bab_signals`: double-argsort rank + boolean-mask selection, int8 scatter, all-zero early return. **Locked.**
- `portfolio.py` `construct_portfolio`: broadcast-product equal-weight book; DN both-block renormalization + net-fix retained for oracle fidelity. **Locked.**
- `portfolio.py` `enforce_beta_neutrality`: vectorized masked-pass implementation. **Locked unless regression evidenced.**
- `backtest.py` `run_backtest`: final numpy finite-repair sanitize; reuses `w_shifted` for turnover. **Locked unless regression evidenced.**
- `strategy.py` finiteness guard: single-pass. **Locked unless regression evidenced.**
- `attribution.py`: single-pass `_finite_series` / `_finite_sum` with defensive fallbacks and `TestAttributionSanitizationParity`. **Closed.**
- `scripts/bench_beta_neutrality.py` and `tests/test_beta_neutrality_performance.py` are the canonical bench/oracle-guard artifacts for the locked hot spot.

## Environment / bottlenecks (current)

- **Deps:** python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, hypothesis present. `coverage`/`pytest-xdist` missing.
- **Full gate ~372 s.** Use targeted suites while iterating; run the full gate once before recording.
- **No active blocker:** the RC=1 gate bottleneck (broken defensive-fallback test + missing `_finite_sum` fallback) is removed; gate is green. Working tree has the 2-file fix above; no stashes/branches.
- **Scratch:** `/home/runner/work/_temp/kilo-tmp/` (`bab_real_e2e_probe.py`, `bab_causal_perf_probe.py`). Do NOT add tracked `probe*`/`debug*`/`ast_probe.py` at repo root.

## Anti-churn / execution rules (binding)

- **Ship code/tests, not commentary:** progress = measured win or correctness proof + regression tests + green gate + recorded deltas.
- **No** re-profiling old recorded baselines except as before/after measurements for code you change now.
- **No** probe-count campaigns, C-number rotation, or "no reduction identified" artifacts.
- **No** reopening historical diagnostics (`research_state/workflow_run_diagnostics.jsonl`) as current failures.
- If a stage yields no measurable win / no defect after a genuine implementation attempt, document the evidence and immediately move to the next stage; do not stop the session.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (root-level probe/debug scripts, `.cov_ds`, `.cov_target` are scratch); use `/home/runner/work/_temp/kilo-tmp/` for new scratch.
- **No** weakening/deleting `tests/test_beta_neutrality_performance.py`, `batch148/149/172`, `campaign_d*`, `tests/test_bab_*_c5*_regressions.py`, or `tests/test_bab_data_loader_batch62.py::test_1097_1098_drop_all_nan_getitem_except`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

---

**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**