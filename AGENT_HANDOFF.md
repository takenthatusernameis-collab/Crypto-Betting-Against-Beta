# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T01:00:30Z (UTC)
- **Git HEAD (at refresh):** `99a841b` (working tree clean; `ruff` clean; gate live-verified GREEN 2026-11-16T01:00:30Z: 6,153 passed, 35 skipped, 132.01s, 99% total)
- **Start here:** `HANDOFF.md` → `INITIAL TASK MESSAGE (START HERE, 2026-11-16T01:00:30Z) — BINDING` (Campaign **P17 — Safe-by-default data-quality gate wired through the real trading pipeline**, sole focus, next action **P17-1**: RED characterization tests → safe defaults (20/7/3) → thread thresholds through `BABStrategy`/CLI → stop `load_prices` bypassing the gate with `quality=False`)

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.