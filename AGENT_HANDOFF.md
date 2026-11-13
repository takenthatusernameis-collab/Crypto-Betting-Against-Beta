# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T07:48:12Z
- **HEAD:** `d412bb1` (working tree **clean**)
- **Gate (last recorded):** `bash scripts/bab_gate.sh` → **5144 passed / 35 skipped / RC=0** (2026-11-13T07:24Z). Re-run before/after any shipped change.
- **BINDING INITIAL TASK (2026-11-13T07:48:12Z):** **Execute Step 3f — ship real optimizations for `BABStrategy.run()` hot spots with oracle-equivalence + perf-ceiling tests and full green gate.** Start at `strategies/betting_against_beta/beta.py:331` `calculate_rolling_beta`, then `portfolio.py:43` `construct_portfolio`, then `backtest.py:9` `run_backtest` (`strategy.py:211` `BABStrategy.run`). Re-baseline before each edit, implement, test (edge-case equivalence, tol 1e-12/degeneracy/NaN/contracts), run targeted tests + `bash scripts/bab_gate.sh` RC=0, record before/after medians & deltas in `HANDOFF.md`. No measurement-only or handoff-only churn; if a stage shows no win after genuine attempt, document evidence and move to next stage immediately. No commits unless explicitly requested.