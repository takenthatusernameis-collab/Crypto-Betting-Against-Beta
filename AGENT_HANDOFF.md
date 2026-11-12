# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T14:58:07Z
- **HEAD:** `2e5519d851d83bf569104ad949a6188f88c5b1bd`
- **State:** Tracked tree clean. **C49 CLOSED CLEAN** — probes 67/67 PASS, gates 3/3 GREEN, 2 proven gaps fixed (`sharpe_ratio` non-finite `risk_free`; `turnover_series` non-numeric frame) with 7 regression tests (verified at HEAD `2e5519d`, metrics.py:36-38).
- **C50 — NOT STARTED (bottleneck cleared).** No `c50_probes/`, `c50_gates/`, or `tests/test_bab_*_c50_regressions.py` exist. Prior sessions checkpointed in planning-only turns without executing C50. **Binding next task: execute C50 probes now** (no C40–C49 reuse), then gates, then refresh this file. Heavy execution required; no planning-only turn.