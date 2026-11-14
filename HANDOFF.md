# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T16:48:57Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `26210c8` (`chore(kilo): checkpoint agent session`) — trust live `git log -1 --oneline` / `git status` if they differ.
- **Branch:** `main` (worktree has uncommitted additions for real-data pipeline + perf guard; see `git status`)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T16:48:57Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Verified baseline (2026-11-14T16:48:57Z)
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (finite) |
| Deterministic fetch/create | `python3 scripts/fetch_real_bab_prices.py --output /tmp/bab_real_prices_check3.csv --benchmark BTC --universe BTC,ETH,SOL --start 2024-01-01 --end 2024-03-01 --print-metadata` | `mode=created`, `rows=45`, `source=deterministic-offline (embedded reproducible generator, no network)` |
| Fetch smoke via loader | `python3 scripts/load_real_bab_example.py /tmp/bab_real_prices_check3.csv --from-prices --benchmark BTC` | `cumulative_return` finite, `periods=44` (validated in-session) |
| Targeted pipeline tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **7 passed** (5.83s) |
| Perf baseline recorded | `python3 scripts/perf_baseline.py --record --dataset tests/fixtures/real_market_prices.csv --output research_state/perf_baseline_real_fixture.json --repeats 3 --warmup 1` | `beta_ms_median=0.4852`, `full_ms_median=3.1852`, `peak_tracemalloc_mb=0.3441`, shape `[398,9]` (numpy 2.5.4, pandas 3.1.1) |
| Perf guard check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** |

**No P0/P1 bottlenecks.** Prior blockers remain resolved — do not reopen.

---

### Priority 1 — Baseline: COMPLETE
Skip unless touched. Do not re-run the full 5k+ suite unless strategy/runtime behavior changes.

### Priority 2 — Real data fetch/update pipeline: COMPLETE (core delivered)
**Delivered this session (uncommitted, needs commit):**
- `scripts/fetch_real_bab_prices.py`: deterministic, idempotent fetch/update entrypoint producing `load_prices`/`load_returns`-compatible CSV (`date`, benchmark, asset columns), configurable `--universe/--benchmark/--start/--end/--output/--seed/--source/--fixture-path`.
- Incremental updates preserve existing history, append only new dates, dedupe by date, sort, and validate contract; re-runs are idempotent.
- Source/licensing semantics explicit: default `deterministic-offline` embedded generator (reproducible, no network/credentials/licensing). `--source fixture` ingests local verified fixture/path. **No silent network fetches; unavailable/invalid sources fail loudly.**
- Focused automated tests: `tests/test_fetch_real_bab_prices.py` (schema/contract, idempotency, incremental append-preserve, fixture source + failures, end-to-end smoke via `scripts/load_real_bab_example.py --from-prices`).

**Remaining P2 hardening (only if needed, do not churn):** optional integration with a public no-auth market data API as an explicitly opt-in, loudly-failing network path with documented ToS/rate-limit handling and deterministic offline fallback retained as default. Not required for current acceptance.

### Priority 3 — Performance baseline & regression guard: COMPLETE (core delivered)
**Delivered this session (uncommitted, needs commit):**
- `scripts/perf_baseline.py`: record/check harness on real-format dataset (default fixture) measuring beta/full median timings and tracemalloc peak.
- Baseline artifact: `research_state/perf_baseline_real_fixture.json` with command, dataset, shape, timings, memory, numpy/pandas versions.
- Deterministic regression guard: `--check` with tolerance thresholds (time factor + absolute MB delta) for CI-friendly/local checks.
- Test: `tests/test_perf_baseline_guard.py`.

### Priority 4 — Evidence refresh, commit hygiene & handoff maintenance (MANDATORY NEXT)
1. **Commit coherent, reviewable changes** (do not amend unrelated history): include `scripts/fetch_real_bab_prices.py`, `scripts/perf_baseline.py`, `tests/test_fetch_real_bab_prices.py`, `tests/test_perf_baseline_guard.py`, `research_state/perf_baseline_real_fixture.json`, and this handoff/pointer update if modified. Keep root historical `probe_*.py`/`debug_*.py` noise untouched.
2. **Record only commands relevant to your changes** (lint, targeted tests, real-data fetch/update smoke, perf check). Do not rerun full suite unless behavior changes.
3. **Update this file** before stopping: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, and the next binding task.
4. Keep `AGENT_HANDOFF.md` as a pointer only.

**If further product progress is needed after P4:** extend real-data pipeline with an opt-in documented public-source fetcher (no-auth preferred) that fails loudly and preserves deterministic offline default/fallback, with tests proving parity/contract.

### Known non-issues (do not churn)
- Large test suite intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P4 (commit + evidence refresh) then any justified hardening; document blockers with evidence and continue. 3. Leave repo coherent and refresh this handoff before stopping.

**Next Agent Mandatory:** Complete **Priority 4** (commit the delivered P2/P3 work + refresh evidence) before any new feature work. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, targeted test output, `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC`, and perf check evidence. No analysis-only handoff.
