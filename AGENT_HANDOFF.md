# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T10:29:56Z
- **HEAD:** `36d6eec` (working tree **clean**)
- **Gate (verified this session):** `bash scripts/bab_gate.sh` → **5172 passed / 35 skipped / RC=0** (2026-11-13T10:29Z, 303.71s). Re-run before/after any shipped change.
- **BINDING INITIAL TASK (2026-11-13T10:29:56Z):** The top remaining production-scale hot spot is **`construct_portfolio` (`portfolio.py:43`)** (~3.27 ms at 2500×50, ~11 ms at 2500×120). Beta and signals are shipped/locked — do **not** re-open them. Ship one real `construct_portfolio` stage optimization (target the `_write_book` fan-out / boolean-mask scatter at `portfolio.py:110-158`, or the per-row `enforce_beta_neutrality` loop at `:331-360`) with oracle-equivalence tests (tol 1e-12, NaN/inf/degeneracy, unchanged errors/ordering), a generous CI-stable perf-ceiling test in `tests/test_portfolio_performance.py`, then targeted tests and full `bash scripts/bab_gate.sh` RC=0. Record before/after warm medians in `HANDOFF.md`. Do NOT re-attempt the `is_numeric_dtype` dtype-check micro-tweak — it measured slower and was reverted. If portfolio yields no win, move immediately to `run_backtest`. Measurement-only turns are forbidden. Read `HANDOFF.md` in full before starting.
