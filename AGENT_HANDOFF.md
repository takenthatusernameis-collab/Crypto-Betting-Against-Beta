# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T18:22:00Z
- **HEAD:** `aea56aa` (working tree clean)
- **Gate (re-verified this session):** GREEN — `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0**, wall-clock **~657 s** (not 446 s; gate budget ≤ 15 min).
- **State:** R1 CLOSED (oracle-verified). R2 NOT STARTED. No blockers.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T18:22:00Z — DO FIRST):** Ship **R2 — Economic Stress & Scale Robustness** (heavy, non-optional):
  - **PRE-CHECK:** `ls tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py` must report all three missing, else run/extend the existing files (a `-k "scale_perf"` filter is unreliable — it matches `test_production_scale_perf_ceiling`).
  - **R2-A** `tests/test_bab_stress_regimes.py`: hostile-regime injector (correlation→1, crash, liquidity evaporation, dispersion spike, trend reversal); run full config grid; assert finite/dollar-neutral (|Σw|≤1e-9)/causal sanity/cost-attribution present/strict-JSON report; record max drawdown, worst period, max turnover per regime; spread-inversion boundedness test.
  - **R2-B** `tests/test_bab_stress_horizon.py`: 5000×200 & 5000×40 sweeps (beta_window {60,90,120} × quantiles {0.1,0.3,0.5} × costs {0,0.001,0.005} × slippage {0,0.0005}); assert finite/DN/deterministic; record worst drawdown/Sharpe/turnover; no non-finite cumulative, no |Σw|>1e-9 when DN.
  - **R2-C** `tests/test_bab_scale_perf_guard.py`: 5000×200 ≤0.8s, 5000×500 ≤2.0s hard ceilings, median of 9 reps (measured this session: 297ms / 759ms).
  - Fix genuine defects with regression tests; never weaken assertions. Exit: targeted suites green, `bash scripts/bab_gate.sh` RC=0 with recorded numbers, refresh this handoff. Commit nothing unless explicitly requested.
  - **Full spec + verified API facts + baseline table:** see `HANDOFF.md`.