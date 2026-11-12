# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T21:49:30Z
- **HEAD:** `6a7180504f315744a76b776d703f4e764280474e`
- **State:** **C53 CLOSED + C54 Step 1 CLOSED.** Suite unblocked; full suite is now the gate with **no ignores: 5069 passed / 35 skipped / RC=0** (476.99s). Coverage **99%** (4535 stmts / 66 miss). Product code unchanged since C53.
- **Policy change (binding):** probe-count quotas abolished. The prior "≥40 new adversarial probes per session, then C54/C55…" loop was the bottleneck: coverage is already 99% (289 test files / 5069 tests for a 6.7k-line product), and Gate 2 hid the controller tests with `--ignore`.
- **Next binding: C54 Step 2** — reduce the **244 broad `except Exception` / 101 silent `pass`** (167 in locked `data_loader.py`) with per-module proven, behavior-preserving fixes + regressions. Start on editable surfaces: `cli.py` (27/15), `backtest.py` (7/7), `portfolio.py` (7/7), `strategy.py` (7/3), `signals.py` (3/3), `quality.py` (4/4), `costs.py` (3/3), `regime.py` (1/1), `config.py` (1/1). Full suite green after each module. Heavy execution required; no planning-only turn; no probe-volume manufacturing.