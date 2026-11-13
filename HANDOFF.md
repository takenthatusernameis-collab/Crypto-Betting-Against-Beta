# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T01:40:42Z
**HEAD:** `1d6bb94 chore(kilo): checkpoint agent session` (working tree clean)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).

## CURRENT STATE (verified this session)

- **Product/gates (from latest recorded full run in repo state, 2026-11-13):** `python3 -m pytest -q -p no:cacheprovider` → **5110 passed / 35 skipped / RC=0** (single command, no `--ignore`). Do not regress gate honesty.
- **Perf baseline measured now (2026-11-13T01:40:42Z, `PYTHONPATH=. python3 scripts/perf_bench.py`, median of 5, 720x12 synthetic):**
  - `calculate_rolling_beta` **0.71 ms**
  - full `BABStrategy.run` **8.63 ms**
  - tracemalloc peak / run **0.57 MB**
- **Hotspot profile measured now (20-run cProfile of `BABStrategy().run`, 720x12 synthetic):**
  - **#1 `portfolio.py:43 construct_portfolio` — cumtime 0.140s, tottime 0.112s (~41% of profiled time / 33% self)** ← primary optimization target
  - `data_loader.load_returns` / `validate_returns_dataframe` / `_run_data_quality_campaign` path ~0.077s cum (~22%, high-risk)
  - `beta.py:331 calculate_rolling_beta` ~0.022s cum (already optimized)
  - `backtest.py` path ~0.050s cum
  - Isolated stage: `construct_portfolio` median **4.86 ms/call** (signals from 720x12 beta frame)

**What is closed (do not reopen without a new reproducible defect + durable evidence):**
`beta.py` rolling-OLS optimization shipped in `8c2830a` (numpy `_rolling_sum`), full run ~17.2 → ~8.5 ms; values/oracles covered by `tests/test_beta_performance.py`, `tests/test_beta_perf_numpy_cache.py`. Further `beta.py` work requires new failing evidence + before/after numbers.

## NEXT FOCUS CAMPAIGN — Step 3b: measurable `construct_portfolio` optimization (BINDING, HEAVY WORK)

`strategies/betting_against_beta/portfolio.py::construct_portfolio` is labeled "vectorized" but remains the dominant hot spot by tottime and a top cumtime contributor. This is the only authorized primary performance campaign. Execute end-to-end; do not substitute probe volume, coverage churn, or handoff-only edits for measured product improvement.

### Required execution plan

1. **Baseline & reproduce (before any edit):** capture and record in commit/handoff notes: `PYTHONPATH=. python3 scripts/perf_bench.py`, isolated `construct_portfolio` median, and cProfile totals for `construct_portfolio` (cum/tot) on the same 720x12 synthetic setup. Treat the numbers above as current reference; re-measure in your environment and report deltas.
2. **Implement one focused optimization in `construct_portfolio`** (or a directly supporting helper in `portfolio.py`) targeting measured overhead (e.g. avoid unnecessary `signals_df.copy()`/dtype coercion passes when already numeric, reduce per-row Python loops in dollar-neutral rebalance/net fixup, eliminate redundant allocations/mask recomputations) **without changing the public contract**: inputs/outputs, index/columns, dtypes, NaN/inf handling, `BABPortfolioError`/`BABDataError` conditions, dollar-neutral/gross/net/max-position/max-turnover semantics, and risk checks must remain behavior-compatible.
3. **Prove correctness:** add or extend a durable regression/perf-guard test under `tests/` (e.g. `tests/test_portfolio_performance.py` or existing perf-pattern tests) that (a) asserts numerical equivalence vs a clear oracle/reference path for representative and edge cases and (b) encodes a reasonable, non-flaky performance expectation consistent with repo style (avoid brittle micro-thresholds; justify with measured before/after).
4. **Prove improvement:** report before/after for `scripts/perf_bench.py` (full run + beta stage) and `construct_portfolio` cum/tottime or isolated median. A “win” must be reproducible and explained; if profiling shows no meaningful win after a serious attempt, record concrete evidence (profiles/numbers) and stop — do **not** ship speculative churn.
5. **Full honest gate:** `python3 -m pytest -q -p no:cacheprovider` (single command, no `--ignore`, RC=0). Run relevant targeted perf/portfolio tests first for fast feedback, but final proof is the full gate.

### Secondary (only if Step 3b is measurably exhausted with evidence)

- **`data_loader.validate_returns_dataframe` / `_run_data_quality_campaign` invoked on every run:** potential to skip redundant heavy validation when inputs are already validated/trusted — **high-risk module** (167 broad / 85 silent `except` handlers per prior audit). Any change requires a specific, measured win, zero correctness regression, and targeted tests. No mechanical exception-sweep refactors.

## Bottlenecks removed (do not reintroduce)

- `beta.py` rolling OLS: **DONE/CLOSED** (`8c2830a`).
- Probe-count quotas abolished; suite/product saturated (~99% coverage). No new probe campaigns.
- No handoff-only churn without shipped, verifiable evidence (or a definitive evidence-backed “no measurable win” conclusion).

## Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 4:** `docs/COVERAGE_NOTES.md`.

## Before exit (mandatory)

1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + cProfile/isolated numbers for any perf work in this handoff (or state “no measurable win” with evidence).
3. Refresh timestamp/HEAD, shipped changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
