# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-17T03:10:49Z (UTC)
- **Git HEAD:** `2dd5c93b825df5ac0bba5a34ce0cc014f48a7510` == `origin/main`
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-4, 2026-11-17T03:10:49Z)** — execute the heavy-work correctness campaign: close at least one execution/order-safety cluster and one reconciliation/ingest cluster with real behavior tests, repair placeholder/weak P19-3 tests, and prove any unreachable deletion with before/after live coverage evidence. Handoff-only/no-op sessions are explicitly invalid. Prioritize by repo stakes: **(1) real orders/execution safety → (2) live fills vs model/reconciliation → (3) ingest fit-to-trade**, then remaining reachable clusters. No CI workflow push attempts (maintainer-only, P19-1).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN (drift rc=2/clean rc=0/emit-only rc=0); `bab_gate.sh` GREEN **6274 passed, 35 skipped, 64 missed / 6681, 99%** @2026-11-17T03:10Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.