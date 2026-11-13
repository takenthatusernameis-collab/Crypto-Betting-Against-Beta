# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T20:46:15Z
- **HEAD:** `d8cf5b1` (main). Working tree: clean.
- **Env:** sandbox ships with **no** numpy/pandas/pytest — install into the venv at `/home/runner/work/_temp/kilo-tmp/bab-venv` (exact block at top of `HANDOFF.md`) before anything else.
- **State:** R1 CLOSED. R2 green at `258f660` (155 passed, ~35.5 s) but **must be re-verified vs `d8cf5b1`** (backtest.py/config.py/strategy.py changed for R3-A). R3-A **execution-realism code SHIPPED** at `d8cf5b1` (`config.py` fields+validation, `strategy._resolve_cost_model()` wired into `run()`, `backtest.py` cost_model path + opt-in partial-fill; locked 5 columns preserved). Remaining: R3-A regression tests (`tests/test_bab_execution_realism_r3.py` not yet written), R3-B rebalance-frequency sweep, `bash scripts/bab_gate.sh` RC=0 vs `d8cf5b1`, then refresh `HANDOFF.md`.
- **NEXT SESSION BINDING INITIAL TASK (DO FIRST, heavy):**
  1. **Unblock env** (venv block at top of `HANDOFF.md`); run `PYTHONPATH=. python3 scripts/bab_r2_preflight.py` (must print `PREFLIGHT_RC=0`, 155 passed) — re-verify R2 against `d8cf5b1`, do not assume it is still green.
  2. **Write R3-A regression tests** (`tests/test_bab_execution_realism_r3.py`) on the 5 R2 hostile regimes: finite drags ≥ 0, DN `max|Σw|≤1e-9`, costs on/off measured, borrow asymmetry strict, backward-compat byte-identical default path, `report()`/`tear_sheet()` finite + strict JSON, wrong-typed `cost_model` raises loudly.
  3. **R3-B:** rebalance-freq {daily,weekly,monthly} × 5 hostile regimes × DN on/off with measured turnover/drawdown/Sharpe per cell; assert turnover ordering (weekly/monthly ≤ daily), not a hard-coded number.
  4. **Exit:** targeted suites + `bash scripts/bab_gate.sh` RC=0 with recorded numbers; refresh `HANDOFF.md` with evidence. Commit nothing unless explicitly requested.
- **Confirmed gap (do not re-discover):** R3-A code is done; the missing piece is the regression-test file + R3-B measurements + gate. `backtest.py` default (no-model) path is intended byte-identical to pre-R3 but unproven against `d8cf5b1` — re-verify.
- **Bottleneck removed:** env now installable in one idempotent block; preflight forces env-verification (Stage 0) before claiming R2/R3; no probe/churn campaigns; `research_state/workflow_run_diagnostics.jsonl` is historical only.
