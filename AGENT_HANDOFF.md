# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T00:46:20Z
- **HEAD:** `45563ba` (main). Working tree has only this handoff's doc/script edits (no product/test code). Supersedes stale `ee1d42c`/`4dfbc17` references.
- **Environment:** run the idempotent venv/bootstrap + preflight block at the top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`). Prefix the gate with `PATH="$VENV/bin:$PATH"`. Do not claim missing deps as blockers.
- **State:** R1/R2/R3 closed/locked — preflight RC=0 (155 passed; scale 163 ms / 393 ms within ceilings); full gate RC=0 (5590 passed / 35 skipped / 416.96s / coverage 96%), verified on `45563ba`.
- **R4 (active campaign):** live-readiness — R4-A dry-run/portfolio-risk report, R4-B drawdown-limit kill switch, R4-C deterministic paper-trading replay harness. Not started. See the binding INITIAL TASK in `HANDOFF.md` (timestamped 2026-11-14T00:46:20Z). Heavy; ship code/tests/evidence; do not stop at analysis.
- **Mechanical gate:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` fails with an itemized TODO until R4 ships. Run it every session.

Historical diagnostics in `research_state/workflow_run_diagnostics.jsonl` are not current failures.