# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T19:43:52Z (UTC)
- **Git HEAD:** `3a0a789` (local == remote `origin/main` `3a0a789`; sync verified). Working tree clean.
- **Binding task:** `HANDOFF.md` → **P19-3 — CLOSE 86-LINE CORRECTNESS GAP *CORRECTLY*** (ship behavior tests this session for each missed line, or delete/justify with concrete unreachability proof; P19-2 complete with `tests/test_p19_2_hardening.py`). P19-1 (CI enforcement) is NO LONGER a gate: the workflow-file push is impossible for agents (repo token lacks `workflows:write`) and its commit was lost. It is a maintainer-only follow-up in `HANDOFF.md` → Deferred. Do not re-attempt it.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3, P19-2 — see `HANDOFF.md`.
- **Local gates last verified:** `ruff` clean; `bab_reconcile_gate.sh` GREEN; `bab_gate.sh` GREEN 6244 passed / 35 skipped / 99% (86 missed) (see `HANDOFF.md`).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.