# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T11:44:00Z
- **HEAD:** `e5dc8ce` — prior `construct_portfolio` broadcast-product work is committed; tree clean at handoff start.
- **Gate (verified 2026-11-13T11:35Z at `e5dc8ce`):** `bash scripts/bab_gate.sh` → **5173 passed / 35 skipped / RC=0** (303.59s). **Re-run with the new oracle guard (2026-11-13T11:42Z):** **5182 passed / 35 skipped / RC=0** (304.58s). Re-run before/after any shipped change.
- **BINDING INITIAL TASK (2026-11-13T11:44:00Z):** Vectorize `enforce_beta_neutrality` (`strategies/betting_against_beta/portfolio.py:232-346`). Fresh warm medians: **212.9 ms @ 2500×40, 215.3 ms @ 2500×50, 249.2 ms @ 2500×120**, versus ~1.7–3.0 ms for `run_backtest`/`construct_portfolio` — this is the dominant remaining hot spot. Reproduce with `PYTHONPATH="$PWD" python3 scripts/bench_beta_neutrality.py --reps 35`; implement a 2-D masked correction preserving all break conditions; prove oracle equivalence at 1e-12 via `tests/test_beta_neutrality_performance.py`; tighten the perf ceiling; pass targeted tests + full gate RC=0; record before/after medians+deltas in `HANDOFF.md`. No measurement-only sessions. `beta.py`/`signals.py`/`construct_portfolio` remain locked without new reproducible evidence.