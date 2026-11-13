# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T17:24:19Z
- **HEAD:** `f7fe638` (R1-A/B/C/D all shipped; working tree clean)
- **Gate:** GREEN — `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0, ~446 s**.
- **State:** R1 campaign CLOSED (correctness oracle-verified); core engine correct, causal, fast on real data.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T17:24:19Z):** Ship **R2 — Economic Stress & Scale Robustness** as three new test files with hard assertions and measured numbers: **R2-A** hostile-regime injector (`tests/test_bab_stress_regimes.py`: correlation→1, crash, liquidity evaporation, dispersion spike, trend reversal; record drawdown/turnover per regime), **R2-B** long-horizon drawdown & limit sweep (`tests/test_bab_stress_horizon.py`: 5000×200/5000×40 grid), **R2-C** scale perf guard (`tests/test_bab_scale_perf_guard.py`: 5000×200 / 5000×500 with hard ceilings). Fix any genuine defect found; do not weaken assertions. Full spec, commands, and exit requirements are in `HANDOFF.md`. Commit nothing unless explicitly requested.