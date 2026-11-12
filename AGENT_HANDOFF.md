# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T23:10:00Z
- **HEAD at session start:** `c568d0fc38cfdc09dcd5f494b35b8743ae64a411` (working tree NOT clean — C54 Step 2 cli.py changes + regressions uncommitted)
- **State:** C53+C54 Step 1 closed historically. **C54 Step 2 `cli.py` batch DONE:** direct silent `pass` 8 -> 3 (lines 87/433/448 remain intentional, tested); `_extract_cumulative` lines 483/498/507 now surface corrupt cumulative extraction; `main()` surfaces extraction failures as rc=1 + message; `_json_safe` 562 and `_json_default` 192 return `str(obj)`. Regressions in `tests/test_bab_cli_c54_regressions.py` (9 tests). Full suite **5078 passed / 35 skipped / RC=0, no ignores**. `docs/unreachable_proofs*` replaced by `docs/COVERAGE_NOTES.md`.
- **Binding next action:** continue **C54 Step 2** module-by-module, starting with **`costs.py` (lines 59, 281)** — re-AST first, convert only proven-invalid-path silences with regressions, full suite green at module boundary. Then `config.py`, `regime.py`, `backtest.py`, `portfolio.py`, `strategy.py`. No probe-volume work; no handoff-only session. One module per batch.
