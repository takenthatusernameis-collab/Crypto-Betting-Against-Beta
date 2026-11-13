# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T07:24:33Z
- **HEAD:** `230e2c07` (working tree dirty — uncommitted Step 3e changes)
- **Gate (verified this session):** `bash scripts/bab_gate.sh` → **5144 passed / 35 skipped / RC=0** (2026-11-13T07:24Z). Re-run before/after any change.
- **Binding next action (initial task):** **Ship Step 3f `BABStrategy.run()` hot spots** — start at `strategies/betting_against_beta/beta.py:331` `calculate_rolling_beta`, then `portfolio.py:43` `construct_portfolio`, then `backtest.py:9` `run_backtest`. Re-measure before each change; add oracle-equivalence + perf-ceiling tests (pattern `tests/test_beta_performance.py`); keep full gate RC=0. Step 3e stale-run vectorization in `data_loader.py` is shipped in working tree with oracle tests and ~14% `validate_returns_dataframe` improvement; details/deltas in `HANDOFF.md`. No measurement-only churn. No commits unless explicitly requested.