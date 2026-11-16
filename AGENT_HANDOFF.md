# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T12:39:43Z (UTC)
- **Git HEAD:** `700d2af` (clean working tree, `origin/main` synced)
- **Binding task:** `HANDOFF.md` → **P19-1 — SHIP CI ENFORCEMENT** (add `bab-gate` job to `.github/workflows/main.yml`, prove GREEN locally, commit/push, verify GREEN on `origin/main`). P19-1 is locally proven (ruff clean, bab_gate.sh GREEN @99%, bab_reconcile_gate.sh GREEN) but NOT yet in workflow. After P19-1 DoD, proceed to **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING**.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3 — see `HANDOFF.md`.
- **Local probes this session:** `ruff` clean; `bab_reconcile_gate.sh` GREEN (drift rc=2, clean/emit-only rc=0); `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN 6215 passed / 35 skipped / 99% (89 missed).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.