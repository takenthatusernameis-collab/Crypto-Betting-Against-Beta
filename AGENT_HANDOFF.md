# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-17T04:28:51Z (UTC)
- **Git HEAD:** `6121323` == `origin/main` — P19-4 code/tests are **uncommitted in the working tree** (6 product files + `tests/test_bab_p19_4_heavy.py`); inspect `git diff`/`git status` first.
- **Binding task:** `HANDOFF.md` → **INITIAL TASK MESSAGE (P19-5, 2026-11-17T04:28:51Z)** — finish the 29-line hard-residue gap: **prove-and-delete unreachable defensive branches, test the genuinely reachable ones.** Work the ingest fit-to-trade cluster (`data_loader.py`, 24 lines: 280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1650-1651, 1954-1955) first, then `beta.py:544-548` (5). `reconciliation.py`, `execution.py`, `cli.py`, `data_sources.py`, `metrics.py`, `portfolio.py`, `replay.py` are now 100% — do not re-test them. The 9 proven-unreachable branches deleted this session (48→29) and the P19-4 tests must NOT be re-done. Handoff-only/no-op sessions are explicitly invalid. Prioritize by repo stakes: **(1) real orders/execution safety → 100% CLOSED**, **(2) live fills vs model/reconciliation → 100% CLOSED**, **(3) ingest fit-to-trade → NOW FIRST (24 lines)**, then the beta outer fallback. No CI workflow push attempts (maintainer-only, P19-1).
- **Last verified gates:** ruff clean; `bab_reconcile_gate.sh` GREEN (drift rc=2/clean rc=0/emit-only rc=0); `bab_gate.sh` GREEN **6277 passed, 35 skipped, 29 missed / 6631, 99%** @2026-11-17T04:28Z.

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.

(End of file - total 10 lines)