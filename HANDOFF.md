# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T17:41:57Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `8cdeaf1` (`docs: refresh canonical handoff with verified P6 binding task (2026-11-14T17:39:23Z)`)
- **Branch:** `main`
- **Working tree:** clean (verified 2026-11-14T17:41:57Z)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T17:41:57Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Verified baseline (2026-11-14T17:39:23Z UTC, clean working tree at HEAD 591d248)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Targeted tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **10 passed** (6.65s, 0 failed) |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (exit 0) |
| Perf baseline check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |

**No P0/P1/P2/P3/P4/P5 bottlenecks.** Offline deterministic default path unchanged. P5 opt-in public Coinbase fetch (ToS gating, pacing/retries, no silent fallback) is complete at `0d92bf7`.

### Priority 6 — Next focus campaign (MANDATORY, heavy lifting) — BINDING
Harden and operationalize the public fetch path for reproducible research runs. All items required; none optional.

1. **Contract + resilience tests** (extend `tests/test_fetch_real_bab_prices.py`; failures must be loud/clear `BABDataError` or equivalent documented behavior, never silent partial success):
   - Partial/missing symbol coverage (symbol unavailable on public market) → loud `BABDataError`, no silent partial alignment.
   - Non-JSON/invalid candle payloads → loud `BABDataError`.
   - Empty-range responses (no candles in window) → loud `BABDataError`.
   - Chunked multi-window fetch behavior (e.g. 250-day chunks across multi-year ranges) → deterministic, correct date/symbol coverage.
   - Incremental update idempotency when merging public-sourced data into an existing CSV (re-run → identical file; no duplicate dates; no history corruption).

2. **Metadata/audit trail (machine-readable):**
   - Add `--metadata-out <path>` writing a JSON sidecar with: `source`, URL base, product/quote, request pacing/retry settings, ToS acknowledgement flag (boolean only — do not persist raw acknowledgement text/secrets), UTC fetch time, row/date coverage, symbol universe, and outcome/error context as appropriate.
   - Keep console `--print-metadata` stable and human-readable.
   - Metadata must not leak secrets/tokens/credentials.

3. **CLI parity/docs:**
   - Document `--metadata-out` and all failure modes in `README.md` (opt-in/public path).
   - Keep offline `deterministic-offline` default and fixture behavior unchanged.

4. **Verification + commit + refresh handoff (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` → all pass (existing + new)
   - `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → exit 0 (`cumulative_return`/`periods` stable)
   - `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Commit with evidence (include: `git log -1 --oneline`, `git status --short`, ruff, targeted tests, smoke, perf).
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P6 items implemented and tested, offline default unchanged, all verification above green, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets, but do not regress.
- Pandas/numpy warnings in stress tests are expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P6 (tests + metadata/audit output + docs + verification + commit + handoff refresh). 3. Refresh this handoff before stopping. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T17:41:57Z UTC):** Complete **Priority 6** end-to-end (resilience/coverage tests, `--metadata-out` JSON audit sidecar, README docs, verification, commit, handoff refresh) before any new feature work. Do not stop at analysis. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, targeted test output, smoke output, and perf-check evidence.
