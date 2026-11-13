# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T20:30:49Z
- **HEAD:** `258f660` (main). Working tree: clean at refresh (R2 files now committed).
- **Env:** sandbox ships with **no** numpy/pandas/pytest — install into the venv at `/home/runner/work/_temp/kilo-tmp/bab-venv` (exact block at top of `HANDOFF.md`) before anything else.
- **Gate (last recorded):** full gate `5373 passed, 35 skipped, RC=0` (~657 s) on prior host; R2 targeted suite **155 passed, ~35.5 s, preflight rc=0** re-verified this refresh on `258f660`.
- **State:** R1 CLOSED. R2 **VERIFIED GREEN** this refresh (env unblocked). R3 is the only standing work.
- **NEXT SESSION BINDING INITIAL TASK (DO FIRST, heavy):**
  1. **Unblock env** (venv block at top of `HANDOFF.md`); run `PYTHONPATH=. python3 scripts/bab_r2_preflight.py` (must print `PREFLIGHT_RC=0`, 155 passed) — R2 is already green, do not re-litigate it.
  2. **Ship R3 — Execution Realism:** wire `TransactionCostModel` (impact/participation, ADV-scaled square-root impact, borrow-cost asymmetry) + opt-in partial-fill/slippage realism into `BABStrategy.run()` (`costs.py`/`backtest.py`/`strategy.py`/`config.py`), with regression tests on the 5 R2 hostile regimes (finite drags ≥ 0, DN `max|Σw|≤1e-9`, costs on/off measured, borrow asymmetry strict). Preserve byte-identical default (no-model) path.
  3. **R3-B:** rebalance-freq {daily,weekly,monthly} × 5 hostile regimes × DN on/off with measured turnover/drawdown/Sharpe per cell; assert turnover ordering (weekly/monthly ≤ daily), not a hard-coded number.
  4. **Exit:** targeted suites + `bash scripts/bab_gate.sh` RC=0 with recorded numbers; refresh `HANDOFF.md` with evidence. Commit nothing unless explicitly requested.
- **Confirmed gap (do not re-discover):** `strategy.py:402` never passes `cost_model`/`prices_df`/`adv_usd` to `run_backtest`; `config.py` has no `cost_model`/`prices`/`adv` fields — so the impact/borrow model is dead code via the public `BABStrategy.run()` entrypoint.
- **Bottleneck removed:** env now installable in one idempotent block; preflight forces env-verification (Stage 0) before claiming R2/R3; no probe/churn campaigns; `research_state/workflow_run_diagnostics.jsonl` is historical only.