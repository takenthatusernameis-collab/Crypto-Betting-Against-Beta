# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T04:18:31Z (UTC)
- **HEAD at refresh:** `479ee9f` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R4 shipped on prior evidence only (not re-verified this refresh); **re-verify on current HEAD before claiming green**.
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T04:18:31Z UTC) — BINDING” for mandatory bootstrap, baseline verification, and the **R5 Execution Integration** campaign (R5-A adapter contract, R5-B modeled-vs-executed reconciliation, R5-C executed-fills reconciliation).
- **Bottlenecks removed/enforced:** single handoff, env bootstrap + `PATH` for gate, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no archaeology/probe churn, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
