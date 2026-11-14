# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff docs.

- **Refreshed:** 2026-11-14T03:18:12Z (UTC)
- **HEAD:** `5870a0f` (main). Working tree clean at refresh except handoff update.
- **State:** R1–R4 shipped on prior verified evidence (`23d5145`: R2/R4 preflights RC=0, full gate RC=0, 5621 passed / 35 skipped / 95%). **Re-verify on current HEAD before claiming green; live run wins.**
- **Mandatory start:** idempotent venv bootstrap at `/home/runner/work/_temp/kilo-tmp/bab-venv`, then `PYTHONPATH=. "$VENV/bin/python" scripts/bab_r2_preflight.py` and `scripts/bab_r4_preflight.py`; gate via `PATH="$VENV/bin:$PATH" bash scripts/bab_gate.sh`. Do not claim missing deps as blockers.
- **Next campaign (binding):** **R5 — Execution integration**: (1) re-verify baseline, (2) live-order adapter contract/stubs (no network in tests, default path unchanged), (3) slippage/impact calibration + reconciliation vs executed-fill data, (4) executed-fills backtest reconciliation artifact/report, (5) add `test_bab_execution_integration_r5*` proofs + preflights + full gate + handoff update.
- **Bottlenecks removed:** single handoff enforced, env bootstrap documented, historical `research_state/workflow_run_diagnostics.jsonl` quarantined, no `.github/workflows/*` or tracked probe/debug edits.

If evidence here conflicts with live output, trust live output and update `HANDOFF.md`.
