# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T10:45:54Z (UTC)
- **Git HEAD (at refresh):** `91d6dc5`
- **Binding task:** `HANDOFF.md` → **P19-1 — CI enforcement armbar**. CI currently runs none of `ruff`, the 6250-test suite, the 99% coverage floor, or `scripts/bab_reconcile_gate.sh`. Wire them into a CI job and prove RED on injected failure / GREEN on clean `main`.
- **Prior campaigns P17-1, P18-1, P18-2, P17-2 are DONE** — do not redo; see `HANDOFF.md` → Verified completion state.
- **Live state @91d6dc5:** gate GREEN 6215 passed / 35 skipped / 99% coverage; `ruff` clean; `perf_baseline.py --check` PASS; `main` == `origin/main`.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.