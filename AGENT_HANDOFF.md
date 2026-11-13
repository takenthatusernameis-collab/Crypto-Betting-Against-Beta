# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T15:19:11Z
- **HEAD:** `960e277` (attribution single-pass sanitize + `TestAttributionSanitizationParity`)
- **Working tree:** 2 modified, uncommitted files — `attribution.py` (broadened defensive fallback in `_finite_series`, added `_finite_sum` fallback, trailing newline) and `test_bab_attribution.py` (test assertion uses saved `real_isfinite`). No commit made.
- **Gate:** GREEN — `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, 371.99s**. The prior RC=1 bottleneck (broken defensive-fallback test + missing `_finite_sum` fallback) is removed.
- **State:** prior PENDING attribution task was already executed at `960e277`; this session fixed the red gate and captured real-data E2E / causality / performance evidence (see `HANDOFF.md`).
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T15:19:11Z) — PENDING:** Execute the **BAB Real-Data & Scale Correctness Campaign (R1)** in four mandatory stages: (A) causality/no-lookahead regression harness; (B) real-data E2E invariant suite (dollar neutrality, beta target, attribution/report identities, determinism, all-NaN/date-gap fixtures); (C) independent naive-oracle parity for beta/signals/portfolio/backtest at `rtol=atol=1e-12`; (D) E2E performance guard at 2500×120 `beta_neutral=True` (baseline 116 ms → ceiling 0.60 s). Full spec, commands, and exit requirements are in `HANDOFF.md`. Commit nothing unless explicitly requested.

(End of file - total 11 lines)