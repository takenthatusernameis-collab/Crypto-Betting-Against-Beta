# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T23:47:40Z (UTC)
- **Git HEAD:** `3a0a789` (local == remote `origin/main` verified 19:43Z)
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-3, 2026-11-16T23:47:40Z)** — close the 64-line correctness gap correctly by shipping behavior tests/proofs now (use actual APIs/signatures: `reconcile_costs`/`reconcile_fills_to_backtest`, `BABResult` fields, `ReplayHarness`, `LiveExecutionAdapter`/`PaperExecutionEngine` real attrs) or delete proven-unreachable lines with proof. No handoff-only pass. No CI workflow push attempts (maintainer-only, P19-1).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN (drift rc=2/clean rc=0/emit-only rc=0); `bab_gate.sh` GREEN **6274 passed, 35 skipped, 99% (64 missed / 6681)** @2026-11-16T23:47:40Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.