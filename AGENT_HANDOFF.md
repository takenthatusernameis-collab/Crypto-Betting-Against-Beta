# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T20:27:40Z
- **HEAD:** `4850f3c` (main). Working tree: handoff/diagnostics modified; R2 campaign files + preflight present but **untracked/uncommitted** (`tests/test_bab_stress_regimes.py`, `tests/test_bab_stress_horizon.py`, `tests/test_bab_scale_perf_guard.py`, `scripts/bab_r2_preflight.py`).
- **Gate (last recorded):** 5373 passed, 35 skipped, RC=0 (~657 s) — **not re-run** (pytest missing in env).
- **State:** R1 CLOSED. R2 files exist but **UNVERIFIED** (preflight rc=1: `No module named pytest`). Prior R2 numbers in HANDOFF are historical.
- **NEXT SESSION BINDING INITIAL TASK (DO FIRST, heavy):**
  1. **Unblock env:** install pytest/deps; run `python3 scripts/bab_r2_preflight.py` (must pass) and `PYTHONPATH=. python3 -m pytest tests/test_bab_stress_regimes.py tests/test_bab_stress_horizon.py tests/test_bab_scale_perf_guard.py -q` — fix any current defects with smallest proven regression (no weakened assertions).
  2. **Ship R3 — Execution Realism:** R3-A realistic cost/execution (impact/participation, partial-fill/slippage, borrow-cost asymmetry on shorts wired+attributed) with regression tests on 5 R2 regimes (finite drags ≥0, DN `max|Σw|≤1e-9`, costs on/off measured). R3-B rebalance-freq {daily,weekly,monthly} × 5 regimes × DN on/off with measured turnover/drawdown/Sharpe per cell.
  3. **Exit:** targeted suites + `bash scripts/bab_gate.sh` RC=0 with recorded numbers; refresh HANDOFF with evidence. Commit nothing unless explicitly requested.
- **Bottleneck removed:** HANDOFF now forces env-verification (Stage 0) before claiming R2/R3; no probe/churn campaigns; `research_state/workflow_run_diagnostics.jsonl` is historical only.
