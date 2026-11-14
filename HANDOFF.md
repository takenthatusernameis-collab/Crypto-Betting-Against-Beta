# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T17:31:36Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `0d92bf7` (`feat(bab): add opt-in public Coinbase fetch with parity tests`)
- **Branch:** `main`
- **Working tree:** clean (nothing to commit)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T17:31:36Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Verified baseline (2026-11-14T17:31:36Z UTC, clean working tree at HEAD 0d92bf7)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Targeted tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **10 passed** (6.79s, 0 failed) |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (exit 0) |
| Perf baseline check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |

**No P0/P1/P2/P3/P4 bottlenecks.** Offline deterministic default path unchanged.

### Priority 5 — Opt-in public no-auth fetcher: COMPLETE (committed at 0d92bf7)
- `--source coinbase-exchange-public` behind explicit opt-in `--allow-public-api` and exact `--accept-terms`.
- Rate-limit pacing/retries, loud failure on network/HTTP/rate-limit/invalid-source/parse errors, no silent fallback.
- `load_prices`-compatible output; incremental merge idempotent.
- Tests in `tests/test_fetch_real_bab_prices.py` for opt-in/ToS gating, schema parity, loud failure.

### Priority 6 — Next focus campaign (MANDATORY NEXT, heavy lifting) — BINDING INITIAL TASK
Harden and operationalize the new public fetch path for reproducible research runs. All items required; none are optional.

1. **Contract + resilience tests** (add to `tests/test_fetch_real_bab_prices.py`; all must fail loudly with clear `BABDataError`/stderr):
   - Partial/missing symbol coverage (symbol unavailable on public market) → loud `BABDataError`, no silent partial alignment.
   - Non-JSON/invalid candle payloads → loud `BABDataError`.
   - Empty-range responses (no candles in window) → loud `BABDataError`.
   - Chunked multi-window fetch behavior (250-day chunks across multi-year ranges) → deterministic, correct coverage.
   - Incremental update idempotency when merging public-sourced data into an existing CSV (re-run → identical file; no duplicate dates; no history corruption).

2. **Metadata/audit trail:** emit machine-readable fetch metadata:
   - New `--metadata-out <path>` flag writing JSON sidecar including: source, URL base, product/quote, request pacing settings, ToS acknowledgement flag (boolean, not raw text secrets), UTC fetch time, row/date coverage, symbol universe.
   - Keep console `--print-metadata` stable and human-readable.
   - Metadata must not leak secrets/tokens.

3. **CLI parity/docs:** document metadata output (`--metadata-out`) and all failure modes in `README.md`; keep offline default and fixture behavior unchanged.

4. **Verification + commit + refresh handoff:**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` → all pass
   - `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → exit 0
   - perf baseline check → `failures: []`
   - Commit with evidence (git log + git status + ruff + test output + smoke + perf).
   - **Refresh this handoff** before stopping: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

Acceptance: P6 items implemented, offline default unchanged, ruff green, targeted tests pass (existing + new), real-data smoke + perf check still pass, committed with evidence, and this handoff refreshed. Future agents must not skip verification or commit steps.

### Known non-issues (do not churn)
- Large test suite intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P6 (resilience tests + metadata/audit output + docs + verification + commit + handoff refresh). 3. Refresh this handoff before stopping. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory:** Complete **Priority 6** (public-fetch resilience/coverage tests + machine-readable metadata/audit output via `--metadata-out` + README docs, then verify, commit, and refresh this handoff) before any new feature work. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, targeted test output, `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC`, and perf check evidence. No analysis-only handoff.
