# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T10:36:11Z
- **HEAD:** `36d6eec` (working tree **clean**)
- **Gate (verified 2026-11-13T10:29Z):** `bash scripts/bab_gate.sh` → **5172 passed / 35 skipped / RC=0** (303.71s). Re-run before/after any shipped change.
- **BINDING INITIAL TASK (2026-11-13T10:36:11Z):** Ship a real, oracle-equivalent optimization of **`construct_portfolio`** (`strategies/betting_against_beta/portfolio.py`, esp. `_write_book` ~110-158 and `enforce_beta_neutrality` ~331-360) — current top hot spot (~3.27 ms @ 2500×50, ~11 ms @ 2500×120). Beta/signals are shipped/locked. Profile now, implement a materially different vectorized fix (not the known-bad `is_numeric_dtype` tweak), prove oracle equivalence (tol 1e-12, NaN/inf/degeneracy), add/update a CI-stable perf ceiling, pass targeted tests + `bash scripts/bab_gate.sh` RC=0, and record before/after medians+deltas in `HANDOFF.md`. If no measurable win after a genuine attempt, revert and immediately apply same cycle to `run_backtest` (`backtest.py:39-78`). No measurement-only sessions. Read `HANDOFF.md` in full before starting.
