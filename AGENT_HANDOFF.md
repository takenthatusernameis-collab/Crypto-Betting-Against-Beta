# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T22:02:15Z
- **HEAD:** `809ee03`
- **State:** **C53 CLOSED + C54 Step 1 CLOSED.** Suite unblocked; full suite is the gate with **no ignores: 5069 passed / 35 skipped / RC=0** (476.99s). Coverage **99%** (4535 stmts / 66 miss). No product/test code changed since C53.
- **Policy change (binding):** probe-count quotas abolished. The prior "≥40 new adversarial probes per session, then C54/C55…" loop was the bottleneck: coverage is already 99% (289 test files / 5069 tests for a 6.7k-line product), and Gate 2 hid the controller tests with `--ignore`.
- **Next binding: C54 Step 2a** — reduce the **244 broad `except Exception` / 103 direct silent `pass`** (AST-verified: `cli.py` 7, `costs.py` 2, `config.py` 1, `regime.py` 1, `backtest.py` 3, `portfolio.py` 2, `strategy.py` 1; `data_loader.py` 85 and `beta.py` 1 are high-risk/proven-defect-only). Start with `cli.py` lines 470, 485, 494, 435. Full suite green after each module. Heavy execution required; no handoff-only turn; no probe-volume manufacturing.