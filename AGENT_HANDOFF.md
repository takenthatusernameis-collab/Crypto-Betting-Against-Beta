# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T02:47:12Z (UTC)
- **HEAD:** `23d5145` (main). Working tree clean at refresh except handoff update. Baseline evidence (gate/preflight on `23d5145`) unchanged by subsequent checkpoint commits; re-verify on current `HEAD` before claiming green.
- **Environment:** run the idempotent venv/bootstrap + preflight block at the top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`). Prefix the gate with `PATH="$VENV/bin:$PATH"`. Do not claim missing deps as blockers.
- **State:** R1/R2/R3 closed/locked (last recorded: preflight RC=0, 155 passed, scale 161 ms / 374 ms within ceilings; full gate RC=0, 5621 passed / 35 skipped / 413.02s / 95% on `23d5145`). Live run on current HEAD wins if conflicting.
- **R4 (SHIPPED):** live-readiness — R4-A dry-run/portfolio-risk report, R4-B drawdown-limit kill switch, R4-C deterministic paper-trading replay harness. **All three implemented, tested, and green.** `bab_r4_preflight.py` run 2026-11-14T02:47:00Z on `23d5145` reported **RC=0** with all capabilities + tests present and R2/R3 baseline green. Full gate RC=0 with 5621 passed / 35 skipped / 95% coverage.
- **Mechanical gate:** `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r4_preflight.py` — run every session and record output.
- **Next campaign:** R5 — Execution integration (live-order adapter stubs, slippage/impact calibration against real fill data, cost-model backtest vs executed-fills reconciliation).

Historical diagnostics in `research_state/workflow_run_diagnostics.jsonl` are not current failures.