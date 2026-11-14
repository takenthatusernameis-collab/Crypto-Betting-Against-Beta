# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T16:55:39Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `2dad2c2` (`feat(bab): add opt-in public Coinbase fetch with parity tests`)
- **Branch:** `main`

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T16:55:39Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Verified baseline (2026-11-14T16:55:39Z, pre-commit working state)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Targeted tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **10 passed** (6.92s, 0 failed) |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (exit 0) |
| Perf baseline check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |

**No P0/P1/P2/P3/P4 bottlenecks.** Offline deterministic default path unchanged.

### Priority 5 — Opt-in public no-auth fetcher (explicit ToS/rate-limit, loud failure): COMPLETE
- Extended `scripts/fetch_real_bab_prices.py` with `--source coinbase-exchange-public` (Coinbase Exchange public candles, no auth) behind explicit opt-in `--allow-public-api` and exact `--accept-terms "I accept the data provider Terms of Service and rate limits"`.
- Enforced rate-limit pacing/retries for bounded transient 429/5xx cases, loud failure on network/HTTP/rate-limit/invalid-source/parse errors, **no silent fallback** to bad/synthetic data.
- Output remains `load_prices`-compatible (`date,BTC,<assets...>`), validated through existing schema contract and incremental merge path.
- Added focused tests in `tests/test_fetch_real_bab_prices.py` proving opt-in/ToS gating, schema/contract parity with offline/fixture loader path, and loud failure on network/rate-limit/invalid-source.
- Documented source/licensing/ToS/rate-limit handling and usage in `scripts/fetch_real_bab_prices.py` and `README.md`.
- Evidence above collected from modified working tree; commit and re-run checks after commit.

### Priority 6 — Next focus campaign (MANDATORY NEXT, heavy lifting)
Harden and operationalize the new public fetch path for reproducible research runs:
1. **Contract + resilience tests:** add tests for partial/missing symbol coverage, non-JSON/invalid candle payloads, empty-range responses, and chunked multi-window fetch behavior (all must fail loudly with clear `BABDataError`/stderr); ensure incremental update semantics remain idempotent when merging public-sourced data into an existing CSV.
2. **Metadata/audit trail:** emit machine-readable fetch metadata (JSON sidecar or `--metadata-out`) including source, URL base, product/quote, request pacing settings, ToS acknowledgement flag (boolean, not raw text secrets), UTC fetch time, row/date coverage, and symbol universe; keep console `--print-metadata` stable.
3. **CLI parity/docs:** document metadata output and failure modes in `README.md`; keep offline default and fixture behavior unchanged.
4. **Verification + commit:** run `python3 -m ruff check .`, targeted fetch/perf/example tests, `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC`, and perf baseline check; commit with evidence.

Acceptance: P6 items implemented, offline default unchanged, ruff green, targeted tests pass (existing + new), real-data smoke + perf check still pass, committed with evidence, and this handoff refreshed.

### Known non-issues (do not churn)
- Large test suite intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P6 (resilience tests + metadata/audit + docs + verification + commit). 3. Refresh this handoff before stopping: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory:** Complete **Priority 6** (public-fetch resilience/coverage tests + machine-readable metadata/audit output + docs, then verify, commit, and refresh this handoff) before any new feature work. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, targeted test output, `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC`, and perf check evidence. No analysis-only handoff.
