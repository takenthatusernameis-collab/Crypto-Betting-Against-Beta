# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T12:50:00Z (UTC)
- **Git HEAD:** `de9eeac` (local commit, **1 ahead of `origin/main`**; push blocked by GH `workflows` permission policy — see HANDOFF.md)
- **Binding task:** `HANDOFF.md` → **P19-1 — SHIP CI ENFORCEMENT** (commit `de9eeac` done; `bab-gate` job added to `.github/workflows/main.yml:42-98`, gates `kilo` job via `needs: bab-gate`; all local gates GREEN incl. 99.5% fail-closed proof; **push rejected — needs maintainer `workflows` write access**). After P19-1 DoD (observed GREEN on `origin/main`), proceed to **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING**.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3 — see `HANDOFF.md`.
- **Local probes this session:** `ruff` clean; `bab_reconcile_gate.sh` GREEN (drift rc=2, clean/emit-only rc=0); `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN 6215 passed / 35 skipped / 99% (89 missed); `BAB_GATE_MIN_COVERAGE=99.5 bash scripts/bab_gate.sh` **RED** (rc=1, fail-closed proven).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.