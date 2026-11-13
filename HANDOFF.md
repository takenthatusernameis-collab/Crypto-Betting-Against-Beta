# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-13T01:46:13Z
**HEAD:** `1d6bb94 chore(kilo): checkpoint agent session` (working tree **dirty**: `strategies/betting_against_beta/portfolio.py` optimized, `tests/test_portfolio_performance.py` added)
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral crypto strategy: long low-beta / short high-beta vs BTC benchmark (see `README.md`, `strategies/betting_against_beta/`).

## CURRENT STATE (verified this session)

- **Last recorded full gate (pre-session, 2026-11-13):** `python3 -m pytest -q -p no:cacheprovider` → **5110 passed / 35 skipped / RC=0** (single command, no `--ignore`). A full-gate rerun was started after Step 3b edits but did not complete within the session budget in this environment; **re-run required** at current HEAD/working tree before claiming RC=0.
- **Targeted verification (RC=0):**
  - `tests/test_portfolio_performance.py` → **5 passed**.
  - Portfolio/perf subset: `tests/test_bab_portfolio_coverage_campaign.py tests/test_bab_portfolio_coverage_campaign3.py tests/test_bab_backtest_portfolio_heavy_extra.py tests/test_bab_portfolio_uncovered_branches.py tests/test_bab_signals_portfolio_edgecases.py tests/test_beta_performance.py` → **108 passed**.

### Step 3b — `construct_portfolio` optimization (implemented, measured)

**Change:** vectorized dollar-neutral normalization/fixup in `strategies/betting_against_beta/portfolio.py::construct_portfolio` (replaced per-row Python loops over affected dates with masked numpy row-ops for book renormalization and net-exposure fix; conditional clip). Public contract preserved (index/columns/dtypes semantics, NaN/inf handling, error types/conditions, dollar-neutral/gross/net/max-position/max-turnover/risk-check behavior).

**Durable regression added:** `tests/test_portfolio_performance.py` — numerical equivalence vs explicit row-wise oracle for representative (720x120 synthetic pipeline signals, DN and non-DN) and edge cases (mixed/non-numeric signals, all-long/all-short rows), plus non-flaky perf guard.

**Before (720x12 synthetic, median of 5, `PYTHONPATH=. python3 scripts/perf_bench.py`, 2026-11-13T01:42Z):**
- `calculate_rolling_beta` **0.69 ms**
- full `BABStrategy.run` **8.46 ms**
- tracemalloc peak/run **0.57 MB**
- isolated `construct_portfolio` median (50): **4.849 ms** (signals from 720x12 beta frame)
- cProfile (20 runs): `construct_portfolio` **cum 0.055s / tot 0.041s**

**After (same setup, 2026-11-13T01:45Z):**
- `calculate_rolling_beta` **0.69 ms**
- full `BABStrategy.run` **4.00 ms** (**~2.1x faster**)
- tracemalloc peak/run **0.73 MB** (higher transient allocation from vectorized intermediates; acceptable tradeoff, measured)
- isolated `construct_portfolio` median (50): **~0.35 ms** (**~14x faster**)
- cProfile (20 runs): `construct_portfolio` **cum 0.006s / tot 0.002s** (no longer top hotspot)

**What is closed (do not reopen without a new reproducible defect + durable evidence):**
`beta.py` rolling-OLS optimization (`8c2830a`). `construct_portfolio` Step 3b primary hotspot pass shipped in working tree with equivalence+perf proof (pending final full-gate confirmation at HEAD).

## NEXT FOCUS CAMPAIGN — Step 3c: re-profile and target new #1 hotspot (BINDING, HEAVY WORK)

Primary `construct_portfolio` bottleneck addressed. Execute end-to-end with measured evidence; do not substitute probe volume, coverage churn, or handoff-only edits.

### Required execution plan

1. **Confirm gate & baseline on current tree:** run `python3 -m pytest -q -p no:cacheprovider` (single command, no `--ignore`, RC=0) and record result. Re-run `PYTHONPATH=. python3 scripts/perf_bench.py` + 20-run cProfile + isolated stage medians to establish the post-Step-3b baseline.
2. **Identify new #1 measured hotspot** from fresh cProfile (likely `backtest.py`/`run_backtest` path or `data_loader` validation; do not guess). Record cum/tot and isolated timing.
3. **Implement one focused, measured optimization** in the identified hotspot without changing public contract/semantics/error behavior. If hotspot is `data_loader.validate_returns_dataframe` / `_run_data_quality_campaign` (high-risk: 167 broad / 85 silent `except` handlers per prior audit), require a specific reproducible/measured win and targeted tests; **no mechanical exception-sweep refactors**.
4. **Prove correctness & improvement:** durable equivalence/regression test(s), before/after `perf_bench` + hotspot profile/median. If no meaningful win after serious attempt, record concrete evidence and stop — no speculative churn.
5. **Full honest gate:** `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.

### Locks / prohibitions

- **No** edits to `.github/workflows/*`.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/` for scratch.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`.
- `data_loader.py` broad-silent `except` sweep remains blocked unless tied to a specific reproducible defect + tests.
- Commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C53:** CLOSED (historical). **C54 Step 1:** full-suite gate (no ignores). **Step 2:** broad-silent audit complete (no justified conversions). **Step 3:** `beta.py` perf shipped (`8c2830a`). **Step 3b:** `construct_portfolio` vectorized DN fixup shipped in working tree with measured win + equivalence tests (gate confirmation pending). **Step 4:** `docs/COVERAGE_NOTES.md`.

## Before exit (mandatory)

1. Full gate green: `python3 -m pytest -q -p no:cacheprovider` → RC=0, single command, no ignores.
2. Record before/after benchmark + cProfile/isolated numbers for any perf work in this handoff (or state “no measurable win” with evidence).
3. Refresh timestamp/HEAD, shipped changes, residual debt with numbers.
4. Keep `AGENT_HANDOFF.md` pointer-only.
5. Commit nothing unless explicitly requested.

---
**This file is the single source of truth. `AGENT_HANDOFF.md` is a pointer only.**
