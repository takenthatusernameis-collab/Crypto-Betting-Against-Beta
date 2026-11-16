# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T08:20:06Z (UTC)
- **Git HEAD (at refresh):** `934f008`
- **Binding task:** `HANDOFF.md` → P18-3 COMPLETE; next focus **deferred backlog P17-2** (repair `tests/test_bab_p17_2_targeted_gaps.py` — 24 API-mismatch failures blocking gate). Start at **P17-2 test repair** immediately.
- **Prior campaigns P17-1, P18-1, P18-2, P18-3 are DONE** — do not redo; see `HANDOFF.md` → Verified completion state.
- **Core test suite:** 6193 passed / 35 skipped (excl. P17-2 test file). `ruff` clean. Coverage 99% (91 missed stmts across 10 modules).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.