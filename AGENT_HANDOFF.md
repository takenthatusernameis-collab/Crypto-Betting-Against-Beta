# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T03:56:48Z (UTC)
- **HEAD at refresh:** `34af42d` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R4 shipped on prior verified evidence; **re-verify on current HEAD before claiming green**.
- **Start here:** follow `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T03:56:48Z UTC)” for mandatory bootstrap, baseline verification, and binding **R5 Execution Integration** campaign.
- **Bottlenecks removed:** single handoff enforced, env bootstrap + `PATH` for gate documented, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
