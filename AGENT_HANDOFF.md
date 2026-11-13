# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T15:30:44Z
- **HEAD:** `2cbd77a` (R1-A causal harness + R1-D perf guard committed; tree clean)
- **Working tree:** CLEAN — no uncommitted changes.
- **Gate:** GREEN — `bash scripts/bab_gate.sh` → **5204 passed, 35 skipped, RC=0, ~372 s**.
- **State:** attribution task CLOSED; R1-A (causal/no-lookahead) SHIPPED; R1-D (E2E perf guard) SHIPPED; R1-B (real-data E2E invariants) PARTIAL; R1-C (independent naive-oracle parity) **NOT STARTED — primary next campaign**.
- **NEXT SESSION BINDING INITIAL TASK (2026-11-13T15:30:44Z):** Complete **R1-C** (`tests/test_bab_real_data_oracle.py`: naive loop-based oracle for rolling beta / signal ranking / portfolio construction / one-step backtest, compared against `calculate_rolling_beta`, `generate_bab_signals`, `construct_portfolio`, `run_backtest` on real fixtures at `rtol=atol=1e-12`) and finalize **R1-B** (extend `tests/test_bab_real_data_e2e.py` to full spec: all fixtures, dollar neutrality, beta target, attribution/report/totals identities, strict-JSON report, tear_sheet, determinism, all-NaN + date gap). Full spec, commands, and exit requirements are in `HANDOFF.md`. Commit nothing unless explicitly requested.