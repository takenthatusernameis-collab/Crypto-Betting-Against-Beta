# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only.

- **Timestamp (UTC):** 2026-11-14T18:33:26Z
- **Repo:** `Crypto-Betting-Against-Beta`
- **HEAD:** `fc6faa0` (`fix(lint): resolve E501 line-length errors in fetch price tests`)
- **Branch:** `main`
- **Working tree:** clean (verified 2026-11-14T18:33:26Z)

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T18:33:26Z UTC) — BINDING

This is the only active task. Execute in order. No archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), no new handoff/session docs, no re-verification of green areas unless your change touches them. If blocked, record exact command + output and continue with the next unblocked priority. **Never stop at analysis — produce code, tests, and evidence.**

### Campaign objective
Keep the **Crypto Betting Against Beta (BAB)** strategy operational on **real, updatable, reproducible market data** with a clean lint/test baseline, a recorded performance guardrail, and evidence-backed commits.

### Completed — Priority 6 (public fetch hardening) — evidence at HEAD `fc6faa0`
P6 (resilience/coverage tests, `--metadata-out` JSON audit sidecar, README docs, verification, commit, handoff refresh) is DONE. Implementation landed in `scripts/fetch_real_bab_prices.py` + `tests/test_fetch_real_bab_prices.py` + `README.md` (post `8cdeaf1`); final lint blocker fixed in `fc6faa0`.

Verification evidence (2026-11-14T18:33:26Z UTC):
| Check | Command | Result |
|-------|---------|--------|
| Lint | `python3 -m ruff check .` | **All checks passed** (exit 0) |
| Targeted tests | `python3 -m pytest -q tests/test_fetch_real_bab_prices.py tests/test_perf_baseline_guard.py` | **18 passed** (12.25s, 0 failed) |
| Real-data fixture smoke | `python3 scripts/load_real_bab_example.py tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` | `cumulative_return=0.456327`, `periods=398` (exit 0) |
| Perf baseline check | `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` | **0 failures** (`failures: []`) |
| Commit | `git log -1 --oneline` / `git status --short` | `fc6faa0` / clean tree |

**No P0/P1/P2/P3/P4/P5/P6 bottlenecks.** Offline deterministic default path unchanged. P5 opt-in public Coinbase fetch complete. P6 complete and committed.

### Priority 7 — Next focus campaign (MANDATORY, heavy lifting) — BINDING
Full-suite regression + gate verification across the BAB strategy and controller infra. All items required; none optional.

1. **Full test suite (no targeted subsets):**
   - `python3 -m pytest -q` → must pass (prior baseline: 5674 passed / 35 skipped / 0 failed; confirm no regression from P6 changes to `fetch_real_bab_prices.py`, `load_real_bab_example.py`, `tests/test_fetch_real_bab_prices.py`).
   - Investigate any failure; never stop at analysis — produce fix + test + evidence.

2. **Controller/infra gate:**
   - `bash scripts/bab_gate.sh` → exit 0 (progress accounting / diagnostics / nonfinite serialization / campaign resume paths).
   - Confirm `tests/test_controller_progress_accounting.py` passes.

3. **CLI entrypoint parity:**
   - `python -m strategies.betting_against_beta.cli --synthetic` → exit 0.
   - `python -m strategies.betting_against_beta.cli --dry-run --data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → exit 0, no config surprises.
   - `bab-example --version` (installed console script) → exit 0.

4. **Verification + commit + refresh handoff (required before stopping):**
   - `python3 -m ruff check .` → exit 0
   - `python3 -m pytest -q` → all pass
   - `bash scripts/bab_gate.sh` → exit 0
   - `python3 scripts/perf_baseline.py --check --baseline research_state/perf_baseline_real_fixture.json --dataset tests/fixtures/real_market_prices.csv --repeats 2 --warmup 0 --time-tolerance 3.0 --mem-tolerance-mb 50` → `failures: []`
   - Commit with evidence (`git log -1 --oneline`, `git status --short`, ruff, full suite, gate, perf).
   - **Refresh this handoff**: new UTC timestamp, new HEAD, completed work with exact evidence, remaining gaps/risks, next binding task.

**Acceptance:** P7 items implemented/tested, full suite + gate green, perf guardrail holds, committed with evidence, and this handoff refreshed. No analysis-only handoff.

### Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets only when debugging, but do not regress full-suite green.
- Pandas/numpy warnings in stress tests are expected unless behavioral regression.
- Root `probe_*.py` / `debug_*.py` / `ast_probe.py` are historical noise — ignore.

### Protocol
1. Read this file fully. 2. Execute P7 (full suite + bab_gate + CLI parity + verification + commit + handoff refresh). 3. Refresh this handoff before stopping. 4. Keep `AGENT_HANDOFF.md` as a pointer only.

**Next Agent Mandatory (2026-11-14T18:33:26Z UTC):** Complete **Priority 7** end-to-end (full pytest suite, `scripts/bab_gate.sh`, CLI entrypoint parity, verification, commit, handoff refresh) before any new feature work. Do not stop at analysis. Report: `git log -1 --oneline`, `git status --short`, `ruff check .`, full pytest output, gate output, smoke/perf evidence.
