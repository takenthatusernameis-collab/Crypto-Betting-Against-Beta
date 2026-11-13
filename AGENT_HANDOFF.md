# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T08:33:33Z
- **HEAD:** `05abdb0` (working tree **clean**)
- **Gate (verified prior session):** `bash scripts/bab_gate.sh` → **5145 passed / 35 skipped / RC=0** (2026-11-13T08:29Z, 301.70s). Re-run before/after any shipped change.
- **BINDING INITIAL TASK (2026-11-13T08:33:06Z):** The prior "optimize `calculate_rolling_beta` at `beta.py:331`" task is **STALE — the optimization already shipped** (0.62 ms on 720×12, not the 12.1 ms naive baseline). Do NOT re-optimize shipped stages. Instead: re-baseline at **production scale (2500 days × 40–60 assets)**, `cProfile`/`py-spy` to find where time actually goes at that scale, then ship one end-to-end stage optimization with oracle-equivalence tests (tol 1e-12, NaN/inf/degeneracy/min_obs, unchanged errors/ordering) + a generous CI-stable perf-ceiling test + `bash scripts/bab_gate.sh` RC=0. Record before/after medians in `HANDOFF.md`. Measurement-only/profiling-only turns are forbidden; if a stage has no win after a genuine attempt, document evidence and move to the next candidate immediately. No commits unless explicitly requested. Read `HANDOFF.md` in full before starting.