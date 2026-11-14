# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T06:19:45Z (UTC)
- **HEAD at refresh:** `34e734b` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R5 + R5-D verified green on `34e734b`; full gate green on `34e734b` (5644 passed / 35 skipped / 426.48s / coverage 93%). One CLI-regression bottleneck cleared this session (`execution_adapter` kwarg only passed when an adapter is configured).
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:19:45Z UTC) — BINDING” for bootstrap, fast re-verify, and the **R5-D** campaign: additive CLI/report execution + reconciliation productization (deterministic paper/mock, no network/creds), preserving default-path invariance.
- **Bottlenecks removed/enforced:** single handoff, env bootstrap + `PATH` for gate, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no real-venue creds (external dependency, do not fake) — proceed with R5-E, no archaeology/probe churn, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
