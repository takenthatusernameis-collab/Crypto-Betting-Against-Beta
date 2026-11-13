# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-13T01:40:42Z
- **HEAD:** `1d6bb94 chore(kilo): checkpoint agent session`
- **State:** `beta.py` rolling-OLS perf **CLOSED** (`8c2830a`). Measured now (720x12): rolling beta **0.71 ms**, full `BABStrategy.run` **8.63 ms**, peak **0.57 MB**. Last recorded full gate: **5110 passed / 35 skipped / RC=0**.
- **Binding next action:** Execute **Step 3b** in `HANDOFF.md` — optimize `strategies/betting_against_beta/portfolio.py::construct_portfolio` (current #1 hot spot: cum 0.140s / tot 0.112s in 20-run cProfile, ~4.86 ms median/call). Baseline/profile first, one measured optimization, correctness + perf regression proof, full honest gate. Do not reopen `beta.py`. Optional high-risk secondary only after evidenced exhaustion: `data_loader` validation path.
