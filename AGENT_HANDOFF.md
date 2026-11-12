# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth.

- **Refreshed:** 2026-11-12T21:39:15Z
- **HEAD:** `15b472166d72fadb55d510a85537a372e367aaa5`
- **State:** **C53 CLOSED — suite unblocked.** 2 real failures fixed in `tests/test_controller_progress_accounting.py` (false workflow-pattern-sync premise; `.github/workflows/*` is protected by `git restore`/`git clean`, not a `case` pattern). Full non-data_loader gate now **2334 passed / 0 failed** (was 2 failed / 5066 passed). Coverage 99%. Product code unchanged.
- **Policy change (binding):** probe-count quotas abolished. The prior "≥40 new adversarial probes per session, then C54/C55…" loop was the bottleneck: coverage is already 99% (289 test files / 5066 tests for a 6.7k-line product), and Gate 2 hid the controller tests with `--ignore`.
- **Next binding: C54** — (1) run the **full** suite with no ignores and make that the gate; (2) reduce the **244 broad `except Exception` / 101 silent `pass`** in product code (167 in `data_loader.py`) with per-module proven, behavior-preserving fixes + regressions; (3) perf only with before/after numbers; (4) replace the 2152-line `docs/unreachable_proofs.md` busywork log with a short coverage note. Heavy execution required; no planning-only turn; no probe-volume manufacturing.