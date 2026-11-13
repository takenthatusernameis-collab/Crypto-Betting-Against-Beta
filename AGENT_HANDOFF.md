# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T18:15:16Z
- **HEAD:** `0f1bd55` (working tree clean)
- **Gate (baseline, unchanged):** GREEN — `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0, ~446 s**.
- **State:** R1 CLOSED (oracle-verified). R2 NOT STARTED. No blockers.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T18:15:16Z — DO FIRST):** Ship **R2 — Economic Stress & Scale Robustness** (heavy, non-optional): implement **R2-A** `tests/test_bab_stress_regimes.py` (hostile-regime injector: correlation→1, crash, liquidity evaporation, dispersion spike, trend reversal; run full config grid; record max drawdown/worst period/max turnover; assert finite/dollar-neutral/causal/bounded), **R2-B** `tests/test_bab_stress_horizon.py` (5000×200 & 5000×40 sweeps; record worst drawdown/Sharpe/turnover; no non-finite cumulative, no |Σw|>1e-9 when DN), **R2-C** `tests/test_bab_scale_perf_guard.py` (5000×200 ≤0.8s, 5000×500 ≤2.0s hard ceilings, median of 9 reps). Fix genuine defects with regression tests; never weaken assertions. Exit: targeted suites green, `bash scripts/bab_gate.sh` RC=0 with recorded numbers, refresh this handoff. Commit nothing unless explicitly requested. Full spec in `HANDOFF.md`.