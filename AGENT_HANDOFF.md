# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T22:06:11Z
- **HEAD:** `3c585f2` (main), working tree clean.
- **Environment:** sandbox has no Python deps by default; run the idempotent venv/bootstrap + preflight block at top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`) before any work. Do not claim missing deps as blockers.
- **State:** R1 closed/locked. R2 previously green on `5e715c5` (preflight RC=0; 155 passed R2 suites; scale within ceilings) — **must be re-verified on current HEAD**. R3-A execution-realism code is present; **R3 tests/sweep/gate evidence are missing**.
- **R3-A tests missing:** `tests/test_bab_execution_realism_r3.py` not present. R3-B (rebalance-frequency sensitivity: daily/weekly/monthly × 5 hostile regimes × DN on/off with cost model) not measured. Full `bash scripts/bab_gate.sh` not re-run/recorded on final R3 HEAD.
- **Binding initial task (2026-11-13T22:06:11Z, heavy, no partial completion):** bootstrap+preflight; confirm R2 green on current HEAD; create and pass `tests/test_bab_execution_realism_r3.py` (5 hostile regimes, finite/invariants, `cost_drag>=0`, DN `max|Σw|<=1e-9`, costs-on/off deltas, borrow asymmetry, byte-identical no-model path, finite report/tear_sheet+strict JSON, loud validation errors); implement/measure R3-B sweep with recorded per-cell metrics/invariants (no daily regression vs R2); run targeted R2+R3 then `bash scripts/bab_gate.sh` RC=0; refresh `HANDOFF.md` with concrete evidence. Commit nothing unless explicitly requested.

Historical diagnostics in `research_state/workflow_run_diagnostics.jsonl` are not current failures. Do not stop at analysis.
