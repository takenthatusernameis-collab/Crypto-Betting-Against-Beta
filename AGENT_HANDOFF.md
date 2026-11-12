# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T14:42:00Z
- **HEAD:** `f9d84f808b7a5259f5663fa6db4e0d5cda17f630`
- **State:** Tracked tree dirty by one intentional fix + one new regression test. **C49 CLOSED CLEAN** — probes 67/67 PASS, gates 3/3 GREEN, 2 proven gaps fixed (`sharpe_ratio` non-finite `risk_free`; `turnover_series` non-numeric frame) with 7 regression tests. **C50 START (next)** — ≥20 NEW adversarial probes under `/home/runner/work/_temp/kilo-tmp/c50_probes/`, gates under `c50_gates/`.
- **Binding next task:** **Execute C50 probes now** (no C40–C49 reuse). Focus: `cli.py` reporting/serialization + arg parsing + `--output` failure modes; `data_loader.py` allowed loader edges; `quality.py` coercion/boundary paths; `costs.py`/`regime.py`/`shorting.py`/`sizing.py`/`attribution.py` adversarial combos and fresh cross-interactions. Heavy execution required; no planning-only turn.