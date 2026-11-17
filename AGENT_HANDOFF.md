# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-17T02:22:50Z (UTC)
- **Git HEAD:** `3a0a789` (local == remote `origin/main` verified 19:43Z)
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-3, 2026-11-17T02:22:50Z)** — close the 64-line correctness gap by shipping behavior tests/proofs now (real APIs/signatures) or deleting proven-unreachable lines with proof. Prioritize by repo stakes: **(1) real orders/execution safety → (2) live fills vs model (reconciliation) → (3) ingest fit-to-trade (data_loader/data_sources)**, then remaining reachable clusters. **No handoff-only pass.** No CI workflow push attempts (maintainer-only, P19-1).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN (drift rc=2/clean rc=0/emit-only rc=0); `bab_gate.sh` GREEN **6274 passed, 35 skipped, 99% (64 missed / 6681)** @2026-11-17T02:10:46Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.