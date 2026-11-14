# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T04:40:26Z (UTC)
- **HEAD at refresh:** `196a492` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R5 verified green on `196a492` (R2 155 passed 170/406ms, R4 31+217 passed, R5 23 passed). Full gate not re-run this refresh (last recorded green on `479ee9f`).
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T04:40:26Z UTC) — BINDING” for bootstrap, fast re-verify, and the **R5-D** campaign: additive CLI/report execution + reconciliation productization (deterministic paper/mock, no network/creds), preserving default-path invariance.
- **Bottlenecks removed/enforced:** single handoff, env bootstrap + `PATH` for gate, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no real-venue creds (external dependency, do not fake) — proceed with R5-D, no archaeology/probe churn, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
