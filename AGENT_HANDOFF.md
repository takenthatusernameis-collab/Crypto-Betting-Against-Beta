# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-17T04:09:27Z (UTC)
- **Git HEAD:** `f513c0d` == `origin/main`
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-4, 2026-11-17T04:09:27Z)** — execute the heavy-work correctness campaign: close the remaining reachable-behavior clusters with real tests, starting with **reconciliation** (`reconciliation.py:309` invariant fixture) then **ingest fit-to-trade** (`data_loader.py` 33-line cluster, `data_sources.py:480-481,499-500`), then `beta.py`, `metrics.py:94`, `portfolio.py:166`, `replay.py:172`. Proven-unreachable branches already deleted this cycle (16 lines, 64→48) must NOT be re-tested. Repair weak `pass`/argparse-only P19-3 tests; prove every remaining line with before/after live coverage evidence. Handoff-only/no-op sessions are explicitly invalid. Prioritize by repo stakes: **(1) real orders/execution safety → CLOSED**, **(2) live fills vs model/reconciliation → NOW FIRST**, **(3) ingest fit-to-trade → NOW SECOND**, then remaining reachable clusters. No CI workflow push attempts (maintainer-only, P19-1).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN (drift rc=2/clean rc=0/emit-only rc=0); `bab_gate.sh` GREEN **6274 passed, 35 skipped, 48 missed / 6652, 99%** @2026-11-17T04:09Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.

(End of file - total 10 lines)