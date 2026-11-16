# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T11:40:00Z (UTC)
- **Git HEAD (at refresh):** `91d6dc5`
- **Binding task:** `HANDOFF.md` → **P19-2 — real-data ingest + live-fill fidelity hardening**. P19-1 complete: `bab-gate` CI job enforces `ruff`, 6250-test suite, 98.5% coverage floor, and reconciliation fail-closed gate. Proven RED on injected failure (99.5% floor) / GREEN on clean main.
- **Prior campaigns P17-1, P18-1, P18-2, P18-3, P19-1, P17-2 are DONE** — do not redo; see `HANDOFF.md` → Verified completion state.
- **Live state @91d6dc5:** gate GREEN 6215 passed / 35 skipped / 99% coverage; `ruff` clean; `perf_baseline.py --check` PASS; `main` == `origin/main`.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.