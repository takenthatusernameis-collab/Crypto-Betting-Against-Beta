# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T19:46:57Z (UTC)
- **Git HEAD:** `3a0a789` (local == remote `origin/main` verified 19:43Z)
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-3)** — close the 86-line correctness gap correctly by shipping behavior tests/proofs now. No handoff-only pass. No CI workflow push attempts (maintainer-only).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN; `bab_gate.sh` GREEN 6244 passed / 35 skipped / 99% (86 missed) @2026-11-16T19:43Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
