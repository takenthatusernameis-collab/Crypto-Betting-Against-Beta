# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T21:27:51Z
- **HEAD:** `5e715c5` (main). Working tree: clean at refresh.
- **Env:** sandbox has no deps by default; idempotent venv/bootstrap+preflight block is at top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`). **Do not** claim pytest/numpy missing.
- **Verified this refresh (on `5e715c5`):** `PREFLIGHT_RC=0`; R2 (stress/horizon/scale) **155 passed, 6 warnings, ~31.9 s**; scale **5000×200=164 ms**, **5000×500=384 ms** (within ceilings). R2 is green against `5e715c5`.
- **State:** R1 closed. R3-A execution-realism code shipped at `5e715c5`; **missing work** is `tests/test_bab_execution_realism_r3.py`, R3-B rebalance-frequency sensitivity sweep/measurements, and `bash scripts/bab_gate.sh` RC=0 on final HEAD.
- **NEXT SESSION BINDING INITIAL TASK (heavy, no partial completion):**
  1. Run env bootstrap + preflight (top of `HANDOFF.md`) and confirm `PREFLIGHT_RC=0`.
  2. Write and pass R3-A regression tests (`tests/test_bab_execution_realism_r3.py`, 5 hostile regimes): finite columns, `cost_drag>=0`, DN `max|Σw|<=1e-9`, costs-on/off deltas, borrow asymmetry, byte-identical no-model path, finite report/tear_sheet + strict JSON, wrong-typed config raises loudly.
  3. Implement/measure R3-B: `rebalance_freq` {daily,weekly,monthly} × 5 hostile regimes × DN on/off with R3-A cost model; record turnover/drawdown/Sharpe/cost_drag per cell, assert invariants and turnover ordering, no daily regression vs R2.
  4. Run targeted R2+R3 + `bash scripts/bab_gate.sh` (RC=0), refresh `HANDOFF.md` with concrete evidence. Commit nothing unless explicitly requested.
- **Bottlenecks removed:** env install automated; R2 re-verified on current HEAD; no probe/churn campaigns; `research_state/workflow_run_diagnostics.jsonl` historical only. Do not stop at analysis.
