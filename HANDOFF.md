# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T16:50:36Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `19f5711` (`chore(kilo): checkpoint agent session`) — trust live `git log -1 --oneline` / `git status` if they differ.
- **Branch:** `main` — working tree clean (P2/P3 delivered work already committed).

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T16:50:36Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Verified baseline (2026-11-14T16:50:36Z)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Targeted pipeline tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **7 passed** (6.02s, 0 failed) |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (exit 0) |
| Perf baseline check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |

**No P0/P1/P2/P3 bottlenecks.** All blockers remain resolved — do not reopen. Working tree clean; P2 fetch pipeline + P3 perf guard committed and green.

---

### Priority 4 — Evidence refresh, commit hygiene & handoff maintenance: COMPLETE
All P4 work done: P2/P3 artifacts committed (`scripts/fetch_real_bab_prices.py`, `scripts/perf_baseline.py`, `tests/test_fetch_real_bab_prices.py`, `tests/test_perf_baseline_guard.py`, `research_state/perf_baseline_real_fixture.json`), baseline evidence recorded above, `AGENT_HANDOFF.md` kept as pointer only. Root `probe_*.py`/`debug_*.py` noise untouched.

### Priority 5 — Next focus campaign (MANDATORY NEXT, heavy lifting)
Extend the real-data pipeline with an **explicitly opt-in, documented, no-auth public market data API fetcher** that:
- Fails loudly on network/ToS/rate-limit/invalid-source errors (no silent fallbacks to bad data).
- Retains deterministic offline default/fallback as the only default path.
- Is wired through `scripts/fetch_real_bab_prices.py` behind an explicit `--source` opt-in flag.
- Has focused tests proving schema/contract parity with the deterministic-offline generator and the existing fixture source.
- Includes documented rate-limit/ToS handling.

Acceptance: new opt-in network path added, offline default unchanged, ruff green, targeted tests pass (existing + new), real-data smoke + perf check still pass, committed with evidence, and this handoff refreshed.

### Known non-issues (do not churn)
- Large test suite intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P5 (opt-in public fetcher + tests + evidence + commit). 3. Refresh this handoff before stopping: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory:** Complete **Priority 5** (opt-in public no-auth fetcher with loud failure + offline fallback + parity/contract tests, then commit + refresh this handoff) before any new feature work. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, targeted test output, `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC`, and perf check evidence. No analysis-only handoff.
