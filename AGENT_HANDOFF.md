# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T12:34:01Z (UTC)
- **Git HEAD (prior probe):** `8562f91` (P19-1 workflow/handoff/README changes uncommitted in this session at refresh time)
- **Binding task:** `HANDOFF.md` → **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING**. P19-1 shipped: `bab-gate` CI job added to `.github/workflows/main.yml` (push/PR/workflow_dispatch) enforcing ruff + `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` + `bash scripts/bab_reconcile_gate.sh`; existing `kilo` job intact. Local RED/GREEN proof recorded in `HANDOFF.md`.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3/P19-1 (script + CI job shipped, locally proven) — see `HANDOFF.md`.
- **Local probes this session:** `ruff` clean; injected reconcile drift RC=2 (RED), clean RC=0 (GREEN), `bab_reconcile_gate.sh` GREEN; `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN 6215 passed / 35 skipped / 99% (89 missed).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
