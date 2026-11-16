# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T01:03:44Z (UTC)
- **Git HEAD (at refresh):** `dc58017` (working tree clean; `ruff` clean; gate live-verified GREEN 2026-11-16T01:01:20Z: 6,153 passed, 35 skipped, 131.89s, 99% total)
- **Start here:** `HANDOFF.md` → `INITIAL TASK MESSAGE (START HERE, 2026-11-16T01:03:44Z) — BINDING` (Campaign **P17 — Safe-by-default data-quality gate wired through the real trading pipeline**, sole focus, next action **P17-1**: RED characterization tests in `tests/test_bab_pipeline_safety_contract.py` → safe defaults (20/7/3) at `data_loader.py:1537-1541` → thread thresholds through `BABStrategy._load_returns`/CLI → stop `load_prices` bypassing the gate with `quality=False`; see Definition of Done before advancing to P17-2)

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.