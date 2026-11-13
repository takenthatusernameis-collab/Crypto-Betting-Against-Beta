# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T13:02:01Z
- **HEAD:** `c138353` (`chore: capture completed workflow run diagnostics`)
- **State:** `enforce_beta_neutrality` vectorization/scaffold appears present at HEAD but is **unverified** this session (no bench/targeted/full-gate run here). Re-run and record evidence before claiming closure.
- **BINDING INITIAL TASK (2026-11-13T13:02:01Z):** Verify and close `enforce_beta_neutrality` at HEAD — reproduce baseline (`scripts/bench_beta_neutrality.py --reps 35 --profile`), prove oracle equivalence at 1e-12 (extend `tests/test_beta_neutrality_performance.py` as needed), tighten perf ceiling to achieved safe win, run targeted tests + `bash scripts/bab_gate.sh` (RC=0), and record before/after medians/profile/deltas in `HANDOFF.md`. If no safe win/parity, document, revert non-winning code, and move to `strategy.py` beta-neutral-path profiling per fallback ladder. No measurement-only stop; no reopening locked hot paths without new reproducible evidence.