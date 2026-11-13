# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T01:39:13Z
**HEAD:** `8c2830a chore(kilo): checkpoint agent session` (working tree clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral product: long low-beta / short high-beta crypto vs BTC benchmark.

## READ THIS FIRST — what changed since the previous handoff

The previous handoff's binding instruction was **"Step 3 Performance on `beta.py` rolling OLS" with baseline rolling beta 1.02 ms / full run 17.23 ms.**

**That step is ALREADY DONE and shipped in HEAD (`8c2830a`).** A prior session replaced pandas `rolling().sum()` with a numpy cumulative-sum `_rolling_sum` helper (`beta.py:292`), hoisting benchmark rolling sums out of the per-asset path. Measured this session (2026-11-13T01:39:13Z, `PYTHONPATH=. python3 scripts/perf_bench.py`, median of 5, 3 consecutive runs stable):

| Metric | Handoff baseline (pre-8c2830a) | Current HEAD (measured now) | Delta |
|---|---|---|---|
| `calculate_rolling_beta` (720x12) | 1.02 ms | **0.70 ms** | **-31%** |
| full `BABStrategy.run` | 17.23 ms | **8.5 ms** | **-51%** |
| tracemalloc peak / run | 0.56 MB | 0.57 MB | flat |

**Do NOT reopen `beta.py` rolling OLS.** It is optimized, numerically equivalent to the oracle (`tests/test_beta_performance.py`, `tests/test_beta_perf_numpy_cache.py`), and covered by regression tests. Further work there needs a new reproducible defect + before/after numbers, not intuition.

## Measured gate (honest, this session)

- `python3 -m pytest -q -p no:cacheprovider` (single command, no ignores) → **5110 passed / 35 skipped / RC=0** (289.26s), 2026-11-13.
- Perf tests: `tests/test_beta_performance.py tests/test_beta_perf_numpy_cache.py tests/test_data_quality_stale_run_vectorized.py` → **29 passed / RC=0** (27.41s).
- Note: suite count rose 5090 → 5110 because `tests/test_data_quality_stale_run_vectorized.py` (108 lines) shipped with `8c2830a`. That is the *only* new test file this session; it is a legit regression guard, not probe volume.

## NEXT FOCUS CAMPAIGN — Step 3b: `construct_portfolio` is the new #1 hot spot (EXECUTE THIS)

The previous campaign exhausted the easy `beta.py` win. The **next real heavy work** is `portfolio.py::construct_portfolio`. Fresh cProfile of `BABStrategy().run()` over 20 iterations (720x12 synthetic, 2026-11-13T01:39:13Z):

| Rank | Location | cumtime | tottime | Share |
|---|---|---|---|---|
| **1** | **`portfolio.py:43 construct_portfolio`** | **0.109s** | **0.087s** | **~40%** |
| 2 | `strategy.py:181 _load_returns` → `data_loader.py:1848 load_returns` → `validate_returns_dataframe` (line 1372) → `_run_data_quality_campaign` (1258) | 0.077s | — | ~28% |
| 3 | `beta.py:331 calculate_rolling_beta` (already optimized) | 0.022s | 0.003s | ~8% |
| 4 | `backtest.py:9 run_backtest` | 0.050s | — | ~18% |

`construct_portfolio` is **already documented as "vectorized"** (`portfolio.py:50`) yet is still 40% of runtime and the single largest `tottime` (0.087s / 0.270s = 32% pure self time). This is genuine, reproducible headroom — not churn.

**Binding instructions for the next session (heavy work, cannot be deferred without reproducible evidence):**

1. **Baseline first.** Run `PYTHONPATH=. python3 scripts/perf_bench.py` AND the cProfile snippet below; record numbers in this handoff *before* proposing any change. Current baseline to beat: full run **8.5 ms**, `construct_portfolio` cumtime **0.109 s** / tottime **0.087 s** over 20 runs.
   ```bash
   PYTHONPATH=. python3 - <<'PY'
   import cProfile, pstats, io, numpy as np, pandas as pd
   from strategies.betting_against_beta import BABStrategy
   rng=np.random.default_rng(7)
   df=pd.DataFrame(rng.normal(0.0005,0.02,size=(720,12)),
       index=pd.bdate_range("2022-01-03",periods=720),
       columns=["BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOT","DOGE","LINK","MATIC","ARB"])
   s=BABStrategy(); s.run(returns_df=df)
   pr=cProfile.Profile(); pr.enable()
   for _ in range(20): s.run(returns_df=df)
   pr.disable(); st=pstats.Stats(pr); st.sort_stats('tottime')
   buf=io.StringIO(); st.stream=buf; st.print_stats(15); print(buf.getvalue())
   PY
   ```
2. **Optimize at most one hot path in `portfolio.py`** (`construct_portfolio`): look for redundant per-call allocations/copies (`signals_df.copy()` at line 83, `np.trunc` + nested `np.where` at 97-98, repeated `np.asarray`/`isinstance` checks, boolean-mask reductions). Preserve exact numeric contract and dtype/`BABPortfolioError` behavior. Every optimization must carry before/after numbers from steps 1 and 3.
3. **Optional secondary target (only if portfolio is exhausted):** `data_loader.validate_returns_dataframe` runs the full data-quality campaign (`_run_data_quality_campaign`, 0.029s) on *every* `run()` via `_load_returns` (`strategy.py:181`). Measure whether structural validation alone suffices when data is already trusted; do not weaken correctness/error surfacing. This module is **high-risk** (167 broad / 85 silent `except` handlers) — touch only for a measured win with tests, never a mechanical sweep.
4. **Prove it.** Add/extend a regression test under `tests/test_*perf*.py` that would fail on the old implementation (values identical to oracle + timing delta is the pattern used by `test_beta_performance.py`), then run the **full gate** `python3 -m pytest -q -p no:cacheprovider` (single command, no `--ignore`, RC=0).
5. **If no reproducible, measurable win exists** in `construct_portfolio`, record that with the profile numbers and stop. Do not manufacture probe volume or handoff-only churn. Deferral requires reproducible evidence that the baseline is already optimal, not opinion.

## Policy (unchanged, binding)

- **The product is saturated:** ~99% coverage, 5110 tests for a ~6.8k-line product. **Probe-count quotas are abolished.** Do not author probes for their own sake.
- **Every session must ship a durable, verifiable product improvement** (correctness, robustness, or measured performance) with tests as proof — or record evidence that none exists and stop.
- **Gates must be honest.** Never re-add per-file `--ignore` to a gate.

## Bottlenecks removed (do not reintroduce)

- `beta.py` rolling OLS optimization: **DONE / CLOSED** (numpy `_rolling_sum`, -51% full-run). Do not reopen without a new defect.
- Probe-count quotas abolished; 99% coverage — no new probe surface.
- No handoff-only churn: update this file only to record shipped evidence or a definitive "no candidates / no measurable win" audit with numbers.

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`.
- `data_loader.py` broad-silent sweep stays blocked (high-risk: 167 broad / 85 silent handlers) unless a specific reproducible defect is in scope.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C53:** CLOSED (historical probe campaigns; superseded).
- **C54 Step 1:** CLOSED — full suite is the gate, no ignores.
- **C54 Step 2 (broad-silent audit):** COMPLETE — zero justified conversions; `portfolio/strategy` have no broad/bare silent `Exception: pass`; `beta.py:130` min_obs fallback intentional.
- **C54 Step 4:** CLOSED — `docs/COVERAGE_NOTES.md`.
- **C54 Step 3 (beta.py rolling OLS perf):** CLOSED / SHIPPED in `8c2830a` — numpy `_rolling_sum`, rolling beta 1.02→0.70 ms, full run 17.23→8.5 ms.

## Before exit (mandatory)

1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark numbers (and cProfile delta) in this file.
3. Refresh timestamp/HEAD + what shipped + residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This handoff is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**