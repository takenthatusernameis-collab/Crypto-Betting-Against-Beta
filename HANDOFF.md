# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T21:25:41Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `5ed5088` (`docs: refresh canonical handoff — P6 complete, P7 binding task (2026-11-14T18:33:26Z)`)
- **Branch:** `main`
- **Working tree:** clean (verified 2026-11-14T21:25:41Z)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T21:25:41Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Completed — Priority 6 (public fetch hardening) — evidence at HEAD `fc6faa0`
P6 (resilience/coverage tests, `--metadata-out` JSON audit sidecar, README docs, verification, commit, handoff refresh) is DONE. Implementation landed in `scripts/fetch_real_bab_prices.py` + `tests/test_fetch_real_bab_prices.py` + `README.md` (post `8cdeaf1`); final lint blocker fixed in `fc6faa0`.

### Completed — Priority 7 (full-suite regression + gate verification) — evidence at HEAD `5ed5088`
P7 (full pytest suite, `scripts/bab_gate.sh`, CLI entrypoint parity, verification, handoff refresh) is DONE. All acceptance criteria met.

Verification evidence (2026-11-14T21:25:41Z UTC):
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Full test suite | `python3 -m pytest -q` | **5692 passed, 35 skipped** (585.30s, 0 failed) |
| Controller/infra gate | `bash scripts/bab_gate.sh` | **Exit 0** — 5692 passed, 35 skipped, 92% coverage |
| CLI synthetic | `python -m strategies.betting_against_beta.cli --synthetic` | **Exit 0** — `cumulative_return=0.413704`, `periods=252` |
| CLI dry-run | `python -m strategies.betting_against_beta.cli --dry-run --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | **Exit 0** — config resolved, no surprises |
| CLI version | `python -m strategies.betting_against_beta.cli --version` | **Exit 0** — `bab 0.1.0` |
| Real-data fixture smoke | `python scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | **Exit 0** — `cumulative_return=0.456327`, `periods=398` |
| Perf baseline check | `python scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |
| Git state | `git log -1 --oneline` / `git status --short` | `5ed5088` / clean tree |

**No P0/P1/P2/P3/P4/P5/P6/P7 bottlenecks.** Offline deterministic default path unchanged. P5 opt-in public Coinbase fetch complete. P6 complete. P7 complete and verified.

### Priority 8 — Next focus campaign (MANDATORY, heavy lifting) — BINDING
Extend the BAB strategy with **live/near-real-time execution readiness** while preserving the green baseline. All items required; none optional.

1. **Paper-trading scaffold (dry-run execution path):**
   - Add `ExecutionEngine` with `mode="paper"` that consumes `BABStrategy` weights and emits timestamped orders/fills to a local log (CSV/JSONL) without network calls.
   - Integrate with existing `strategies/betting_against_beta/execution.py` — reuse `Order`, `Fill`, `ExecutionReport` types; add `PaperExecutionEngine` class.
   - CLI flag `--paper-trading --output paper_fills.jsonl` on `strategies.betting_against_beta.cli` (dry-run by default; no auth required).
   - Unit tests: `tests/test_bab_paper_trading.py` covering order emission, fill simulation (next-bar open), P&L reconciliation vs backtest.

2. **Data freshness & staleness guards:**
   - Extend `data_loader.py` with `validate_freshness(max_staleness_days=2, max_gap_days=7)` raising `BABDataError` on stale/missing data.
   - Add `--max-staleness-days` / `--max-gap-days` to `fetch_real_bab_prices.py` and CLI; fail loudly on violations (no silent fallback).
   - Tests: `tests/test_bab_data_freshness.py` covering fresh, stale, gap, and boundary cases.

3. **Signal quality / regime observability:**
   - Add `StrategyDiagnostics` emitted per rebalance: beta distribution stats, quantile boundaries, long/short roster, turnover, concentration (HHI), beta-neutrality error.
   - Persist to `diagnostics.jsonl` alongside paper fills; include in `ExecutionReport`.
   - Tests: `tests/test_bab_diagnostics.py` verifying schema and invariants (beta-neutrality ~0, HHI bounds).

4. **Verification + commit + refresh handoff (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q` → all pass (baseline + new tests)
   - `bash scripts/bab_gate.sh` → exit 0
   - `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Paper trading smoke: `python -m strategies.betting_against_beta.cli --paper-trading --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output /tmp/paper_fills.jsonl` → exit 0, valid JSONL
   - Commit with evidence (`git log -1 --oneline`, `git status --short`, ruff, full suite, gate, perf, paper smoke).
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P8 items implemented/tested, full suite + gate green, perf guardrail holds, paper trading smoke passes, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets only when debugging, but do not regress full-suite green.
- Pandas/numpy warnings in stress tests are expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.
- `bab-example` console script requires `pip install -e .` — not a blocker; module CLI works.

### Protocol
1. Read this file fully. 2. Execute P8 (paper trading scaffold, data freshness guards, signal diagnostics, verification, commit, handoff refresh). 3. Refresh this handoff before stopping. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T21:25:41Z UTC):** Complete **Priority 8** end-to-end (paper trading scaffold, data freshness guards, signal diagnostics, verification, commit, handoff refresh) before any new feature work. Do not stop at analysis. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, full pytest output, gate output, paper trading smoke, perf evidence.