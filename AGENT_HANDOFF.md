# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T20:43:00Z (UTC)
- **Git HEAD:** `3a0a789` (local == remote `origin/main` verified 19:43Z)
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-3)** — close the 84-line correctness gap correctly by shipping behavior tests/proofs now. 24 lines classified as proven unreachable (ready for deletion). 15 lines reachable needing crafted tests. 45 lines long-tail. No handoff-only pass. No CI workflow push attempts (maintainer-only).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN; `bab_gate.sh` GREEN 6267 passed / 35 skipped / 99% (84 missed) @2026-11-16T20:41Z. Added `tests/test_bab_p19_3_remaining_easy.py` (8 tests), `tests/test_bab_p19_3_medium.py` (6 tests), `tests/test_bab_p19_3_easy_wins.py` (9 tests) this session.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.