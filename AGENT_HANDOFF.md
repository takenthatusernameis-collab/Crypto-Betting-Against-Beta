# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T10:52:00Z
- **HEAD:** `314f433` (working tree dirty — portfolio optimization edits, **uncommitted**)
- **Gate (verified 2026-11-13T10:51Z):** `bash scripts/bab_gate.sh` → **5173 passed / 35 skipped / RC=0** (301.39s). Re-run before/after any shipped change.
- **SHIPPED THIS SESSION:** `construct_portfolio` broadcast-product build (`portfolio.py:107-132`) — bit-exact oracle, −16.9% @ 2500×50 (5.50→4.57 ms), −16.1% @ 2500×120 (13.02→10.93 ms); added `test_portfolio_stage_perf_ceiling`; updated two `_write_book`-era failure tests. `beta.py`/`signals.py` remain locked.
- **BINDING INITIAL TASK (2026-11-13T10:52:00Z):** Ship the next oracle-equivalent win in the remaining hot spots — the per-row loop in `enforce_beta_neutrality` (`portfolio.py:256-370`) and/or `run_backtest` (`backtest.py:39-78`). Profile at production scale (2500×40–120) first; implement one materially different vectorization; prove oracle equivalence (tol 1e-12, NaN/inf/degeneracy); add/update a CI-stable perf ceiling; pass targeted tests + `bash scripts/bab_gate.sh` RC=0; record before/after medians+deltas in `HANDOFF.md`. If no measurable win after a genuine attempt, revert and move to the other stage. No measurement-only sessions. Read `HANDOFF.md` in full before starting.