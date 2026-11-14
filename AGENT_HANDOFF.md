# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-14T06:49:52Z (UTC)
- **HEAD at refresh:** `a01118d` (main). **Live run wins** if evidence conflicts. Code is byte-identical to `fde12bf` (only handoff docs changed).
- **State:** R1–R5 + R5-D verified green on `a01118d` (R2 preflight RC=0, R4 preflight RC=0, R5 tests 23 passed, R5-D + default-path CLI RC=0). Full gate last green on `fde12bf` (5644 passed / 35 skipped / 425.16s / coverage 93%); code identical on `a01118d` — re-run gate before release claim.
- **Start here:** `HANDOFF.md` → “INITIAL TASK MESSAGE (START HERE, 2026-11-14T06:49:52Z UTC) — BINDING” for bootstrap, fast re-verify, and the **R5-E** campaign: execution-adapter realism + reconciliation hardening (deterministic paper/mock, no network/creds), consuming the already-shipped R3 cost-model knobs (`partial_fill`, `max_participation`, `adv_usd`, `prices`) without re-implementing R3 and preserving default-path invariance.
- **Bottlenecks removed/enforced:** single handoff, env bootstrap + `PATH` for gate, historical `research_state/workflow_run_diagnostics.jsonl` quarantined as non-blocking, no real-venue creds (external dependency, do not fake), no new lettered campaign / no probe archaeology, no `.github/workflows/*` or tracked root probe/debug edits.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.