# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T00:53:30Z (UTC)
- **HEAD:** `640d374` (main). Working tree clean at refresh except handoff update. Baseline evidence (gate/preflight on `45563ba`) unchanged by subsequent checkpoint commits through `640d374`; re-verify on current `HEAD` before claiming green.
- **Environment:** run the idempotent venv/bootstrap + preflight block at the top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`). Prefix the gate with `PATH="$VENV/bin:$PATH"`. Do not claim missing deps as blockers.
- **State:** R1/R2/R3 closed/locked (last recorded: preflight RC=0, 155 passed, scale 163 ms / 393 ms within ceilings; full gate RC=0, 5590 passed / 35 skipped / 416.96s / 96% on `45563ba`). Live run on current HEAD wins if conflicting.
- **R4 (active campaign, sole blocker):** live-readiness — R4-A dry-run/portfolio-risk report, R4-B drawdown-limit kill switch, R4-C deterministic paper-trading replay harness. **Not shipped**: `bab_r4_preflight.py` run 2026-11-14T00:53:22Z on `640d374` reported itemized TODOs for all three. Must reach RC=0 on final HEAD with green tests/evidence. See binding INITIAL TASK in `HANDOFF.md` (2026-11-14T00:53:30Z). Heavy; ship code+tests+evidence; do not stop at analysis.
- **Mechanical gate:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` — run every session and record output.

Historical diagnostics in `research_state/workflow_run_diagnostics.jsonl` are not current failures.