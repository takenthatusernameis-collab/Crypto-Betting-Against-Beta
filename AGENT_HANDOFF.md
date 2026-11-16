# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T12:29:00Z (UTC)
- **Git HEAD (at refresh):** `8562f91`
- **Binding task:** `HANDOFF.md` → **P19-1 — CI ENFORCEMENT ARMBAR (ship, do not narrate)**. Prior claims that P19-1 was done are **unverified/false on current `main`**: `.github/workflows/main.yml` still has no `bab-gate` job and does not run `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`; README was corrected to match reality. Prove RED-on-injected-failure and GREEN-on-clean in CI/workflow evidence before marking P19-1 done.
- **Verified done (do not redo):** P17-1, P18-1, P18-2, P18-3 (script exists/passes locally), P17-2 — see `HANDOFF.md`.
- **Local probes @8562f91:** `ruff` clean; `bab_reconcile_gate.sh` GREEN; `bab_gate.sh` GREEN 6215 passed / 35 skipped / 99% (89 missed).

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.