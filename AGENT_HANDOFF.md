# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting.

- **Refreshed:** 2026-11-13T13:22:21Z
- **HEAD (at refresh):** `aaa1494` (`chore(kilo): checkpoint agent session`)
- **State:** `enforce_beta_neutrality` closed/locked for this cycle (no regression). Lock checks: enforce medians ~21.5/30.2/57.8 ms @2500x40/50/120; `tests/test_beta_neutrality_performance.py tests/test_bab_beta_neutrality.py` **27 passed**. E2E `beta_neutral=True` `BABStrategy.run` baselines ~35.3/45.3/94.3 ms @2500x40/50/120; component breakdown @2500x120 recorded in `HANDOFF.md`. Last recorded full gate **5191 passed, 35 skipped, RC=0** (prior checkpoint context; not rerun in handoff-only refresh).
- **BINDING INITIAL TASK (2026-11-13T13:22:21Z):** Execute heavy E2E `beta_neutral=True` campaign in `BABStrategy.run` integration/call-chain glue (start with `strategy.py:381-404` finiteness guard single-pass + provably-safe allocation/alignment trims in `strategy.py`/`backtest.py`) with before/after E2E+enforce medians, targeted oracle/regression tests (1e-12 parity where applicable), targeted suites, then `bash scripts/bab_gate.sh` RC=0. No reopening locked hot paths (`beta.py`, `signals.py`, `construct_portfolio`, `enforce_beta_neutrality`, core backtest semantics) or historical diagnostics without new reproducible evidence. No measurement-only stop. Record all evidence in `HANDOFF.md`.
