# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-14T06:46:17Z (UTC)
- **HEAD at refresh:** `fde12bf` (main). **Live run wins** if evidence conflicts.
- **State:** R1–R5 + R5-D verified green on `fde12bf`; full gate green on `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%). The stale-HEAD handoff bottleneck was cleared by re-verifying the CLI regression fix on its actual commit.
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:46:17Z UTC) — BINDING” for bootstrap, fast re-verify, and the **R5-E** campaign: additive execution-realism and reconciliation hardening (deterministic paper/mock, no network/creds), preserving default-path invariance.
- **Bottlenecks removed/enforced:** single handoff, env bootstrap + `PATH` for gate, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no real-venue creds (external dependency, do not fake) — proceed with R5-E, no archaeology/probe churn, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
