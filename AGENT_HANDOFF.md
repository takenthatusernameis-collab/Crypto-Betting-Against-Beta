# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T18:29:42Z
- **HEAD:** `007f5dd` (working tree clean except intended `scripts/bab_r2_preflight.py`)
- **Gate (last verified):** GREEN — `bash scripts/bab_gate.sh` → **5373 passed, 35 skipped, RC=0**, wall-clock **~657 s** (gate budget ≤ 15 min).
- **State:** R1 CLOSED (oracle-verified). R2 NOT STARTED (confirmed by preflight). No blockers.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T18:29:42Z — DO FIRST):**
  1. **Run the preflight (60 s):** `python3 scripts/bab_r2_preflight.py` — paste its output into evidence. It proves R2 is unstarted and measures live scale.
  2. **Ship R2 — Economic Stress & Scale Robustness** (heavy, non-optional):
     - **R2-A** `tests/test_bab_stress_regimes.py`: hostile-regime injector (correlation→1, crash, liquidity evaporation, dispersion spike, trend reversal); full config grid; assert finite / dollar-neutral (|Σw|≤1e-9) / causal sanity / cost attribution / strict-JSON report; record drawdown, worst period, turnover per regime; spread-inversion boundedness.
     - **R2-B** `tests/test_bab_stress_horizon.py`: 5000×200 & 5000×40 sweeps (beta_window {60,90,120} × quantiles {0.1,0.3,0.5} × costs {0,0.001,0.005} × slippage {0,0.0005}); assert finite/DN/deterministic; record worst drawdown/Sharpe/turnover; no non-finite cumulative, no |Σw|>1e-9 when DN; cap runtime ~60 s.
     - **R2-C** `tests/test_bab_scale_perf_guard.py`: 5000×200 ≤0.8s, 5000×500 ≤2.0s hard ceilings, median of 9 warm reps (live this session: 307 ms / 769 ms).
  3. Fix genuine defects with regression tests; never weaken assertions. Exit: targeted suites green, `bash scripts/bab_gate.sh` RC=0 with recorded numbers, refresh this handoff.
  4. Commit nothing unless explicitly requested.
- **Full spec + verified API facts + baseline table:** see `HANDOFF.md`.