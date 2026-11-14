# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-14T23:46:03Z
- **HEAD:** `ee1d42c` (main), working tree DIRTY with one uncommitted reviewed fix (`tests/test_bab_strategy_campaign_gaps.py`: `cfg.cost_model = None` in `TestFreezeFallback` — scope correction, R3 validation untouched). Commit nothing unless explicitly requested.
- **Environment:** sandbox has no Python deps by default; run the idempotent venv/bootstrap + preflight block at top of `HANDOFF.md` (`/home/runner/work/_temp/kilo-tmp/bab-venv`) before any work. Do not claim missing deps as blockers.
- **State:** R1 closed/locked. R2 closed/locked — green on `ee1d42c` (preflight RC=0; 155 passed R2 suites; scale 151ms/383ms within ceilings). R3 closed/locked — `tests/test_bab_execution_realism_r3.py` present and green (62 passed), R3-B rebalance-frequency sweep measured and green, full gate RC=0 (5590 passed / 35 skipped / ~419s / coverage 96%). Bottleneck removed: `TestFreezeFallback` no longer trips R3 loud `cost_model` validation.
- **R4 (active campaign):** live-readiness — dry-run/portfolio-risk report, drawdown-limit kill switch, reproducible paper-trading replay harness against real fixtures. See binding INITIAL TASK in `HANDOFF.md` (timestamped 2026-11-14T23:46:03Z). Heavy; ship code/tests/evidence; do not stop at analysis.

Historical diagnostics in `research_state/workflow_run_diagnostics.jsonl` are not current failures. Do not stop at analysis.