# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T18:40:11Z
- **HEAD:** `9f481e4` (working tree clean except intended new R2 test files:
  `tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`,
  `tests/test_bab_scale_perf_guard.py` — not committed; controller checkpoints)
- **Gate:** `bash scripts/bab_gate.sh` green baseline **5373 passed, 35 skipped, RC=0**, ~657 s;
  full-gate re-run started this session after R2 shipped — record result when it finishes.
- **State:** R1 CLOSED (oracle-verified). **R2 SHIPPED** — 155 passed across
  `tests/test_bab_stress_regimes.py` (40 runs), `tests/test_bab_stress_horizon.py` (108 runs),
  `tests/test_bab_scale_perf_guard.py`. Measured evidence in HANDOFF.md. No blockers.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T18:40:11Z — DO FIRST):**
  1. **Run the preflight (60 s):** `python3 scripts/bab_r2_preflight.py` — confirms R2 files exist
     and pass; paste output into evidence.
  2. **Ship R3 — Execution Realism** (heavy, non-optional): R3-A cost/execution model beyond flat bps
     (square-root impact, partial fills, borrow-cost asymmetry on the short leg) with regression
     tests; R3-B rebalance-frequency {daily, weekly, monthly} × five R2 regimes sweep with measured
     drawdown/turnover/Sharpe per cell. Exit: targeted suites green, `bash scripts/bab_gate.sh` RC=0
     with recorded numbers, refresh this handoff.
  3. Fix genuine defects with regression tests; never weaken assertions. Commit nothing unless
     explicitly requested.
- **Full spec + measured R2 results + verified API facts:** see `HANDOFF.md`.
