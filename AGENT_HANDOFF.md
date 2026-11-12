# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T14:35:00Z
- **HEAD:** `c2ae24bf0410dd3d260e5ba81b8965dabbeccb9f`
- **State:** Tracked tree clean; deps OK (Python 3.12.3, `PYTHONPATH=.`). **C47 CLOSED CLEAN** — probes 38/38 PASS, gates 3/3 GREEN. **C48 CLOSED CLEAN** — probes 66/66 PASS, gates 3/3 GREEN. **C49 STARTED** — ≥20 NEW adversarial probes required under `/home/runner/work/_temp/kilo-tmp/c49_probes/`, gates under `c49_gates/`.
- **Binding next task:** **Execute C49 probes now** (no C40–C48 reuse). Focus: `cli.py`/`metrics.py`/reporting/`scripts/*` arg+error+reporting robustness; allowed loader/wrapper/path/IO edges; `costs.py`/`regime.py`/`shorting.py`/`sizing.py`/`quality.py`/`data_sources.py`/`attribution.py` adversarial combos and fresh cross-interactions. Heavy execution required; no planning-only turn.