# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-14T08:49:22Z (UTC)
- **HEAD at refresh:** `186e70e` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R5 + R5-D + R5-E all COMPLETE. Full gate live-green on `9dc4ac1` (5667 passed / 35 skipped / 577.63s / coverage 92%, RC=0); fast checks green on `186e70e` (R2 preflight RC=0, R4 preflight RC=0, R5-E+R5 46 passed, R5-D CLI RC=0, default-path CLI RC=0). Product/test code is byte-identical to `bcebae0` where R5-E was proven.
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T08:49:22Z UTC) — BINDING” for bootstrap, fast re-verify, and the **R5-F** campaign: end-to-end execution-realism integration + hardening — prove the R5-E mechanisms actually move end-to-end results and close the under-exercised realism/edge branches (`execution.py` 72%, `reconciliation.py` 74%, `backtest.py` 83% slippage-drag, `cli.py` 81%), without re-implementing R3/R5-E and preserving default-path invariance.
- **Bottlenecks removed/enforced:** single handoff; env bootstrap + `PATH` for gate; historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking; no real-venue creds (external dependency, do not fake); no new lettered campaign / no probe archaeology; no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.