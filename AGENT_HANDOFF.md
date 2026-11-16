# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T18:42:46Z (UTC)
- **Git HEAD:** `b81ba35` (local == remote `origin/main` `b81ba35`; sync verified). Working tree clean.
- **Binding task:** `HANDOFF.md` → **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING** (ship behavior tests now; P19-2a fetch_real_bab_prices network path, P19-2b execution.py reconciliation fidelity, P19-2c `--health-check` JSON contract). Then **P19-3 — close the 89-line correctness gap** correctly.
- **P19-1 (CI enforcement) is NO LONGER a gate:** the workflow-file push is impossible for agents (repo token lacks `workflows:write`) and its commit was lost. It is a maintainer-only follow-up in `HANDOFF.md` → Deferred. Do not re-attempt it.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3 — see `HANDOFF.md`.
- **Local gates this session:** `ruff` clean; `bab_reconcile_gate.sh` GREEN; `bab_gate.sh` GREEN 6215 passed / 35 skipped / 99% (89 missed).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.