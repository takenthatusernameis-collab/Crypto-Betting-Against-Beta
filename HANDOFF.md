# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T22:52:39Z (this refresh)
- **Repo:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (data ingestion → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy.
- **Git HEAD (verified this refresh):** `a0a0919` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean; `python3 -m ruff check .` passes. P16-1 and P16-2 are shipped at HEAD: caller-filename detection was removed, the three wrong-contract tests were rewritten, and `BABDataError` now precedes the broad coercion handler in `beta.calculate_beta` with four regression tests in `tests/test_bab_p16_beta_error_propagation.py` (all 4 pass; combined with `test_bab_p16_no_test_detection.py`: 7 passed).
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T22:52:39Z) — BINDING (DO NOT IGNORE)

**Campaign: P16 — Trading-Critical Correctness & Safety Hardening. This is the next session's sole focus. Start at P16-3; do not restart P16-1/P16-2 or re-triage the map.**

This is a **crypto trading system**. The highest-stakes work is correctness and safety of data ingestion, beta/signal integrity, portfolio construction, and execution/ops — not line-coverage percentages. **Ship real production fixes with proof tests every session. Analysis-only, handoff-only, formatting-only, and coverage-against-dead-lines turns are failed sessions.**

### Execute in this order

1. **P16-3 (highest, now unblocked) — resolve the quality-validation contract contradiction with a safety-first, staged rollout.**
   - Current code at `data_loader.py:1537-1541` still defaults to `max_return_abs=10_000.0`, `max_gap_days=3650.0`, `stale_run_threshold=50`; the public docstring at `:1713-1718` promises `20.0`, `7.0`, and `3`. Both stale paths at `:1622-1629` and `:1657-1664` still compute `max_allowed_stale = max(threshold, 50)`, so an explicit threshold of 3 cannot detect a 4–49 run.
   - First add characterization tests that document current behavior for: a 10000% return, a 100-day gap, a 4–49 equal-value run with explicit `stale_run_threshold=3`, and the fast numeric path. Then tighten behavior to honor explicit thresholds and the documented safe defaults. `quality=False` must remain an explicit opt-out; `quality=True` must not silently disable the documented guards.
   - Treat fixtures/tests that encode the old lenient contract as regressions to update, not contracts to preserve. Search all callers/tests before changing defaults, especially `validate_returns_dataframe`, `_run_data_quality_campaign`, real-data loaders, backtests, and validation-performance oracles.
   - If the full gate exposes unavoidable compatibility coupling, do not weaken the new checks: keep the stricter behavior, document the deliberate migration, and isolate any compatibility switch behind an explicit opt-in. Do not invent an undocumented global escape hatch.
   - Required proof: one test that fails on HEAD and passes after the fix for each changed safety guard; record exact commands/results in the ledger.

2. **P16-4 — convert the remaining reachable bucket-B edges into targeted tests.** Use fakes/mocks only; batch by module and rerun the full gate after each batch:
   - `execution.py:139-141` Timestamp-key fallback with a string `date_key`.
   - `execution.py:182-185` Timestamp-indexed ADV sub-frame.
   - `execution.py:555-556` non-finite numpy float JSON sanitization with `allow_nan=False`.
   - `portfolio.py:152-153` extreme-weight clipping; `portfolio.py:170-177` dollar-neutral `need_fix` renormalization under one-sided underflow.
   - `cli.py:589-590` unknown adapter; `cli.py:746-748` invalid output path.
   - `reconciliation.py:309` empty-column early return.
   - `data_sources.py:480-481, 499-500, 507-508` timezone/format edges.
   - `data_loader.py` mixed-dtype slow path, finite-fraction boundary, stale-run boundary, and adversarial datetime dayfirst retry/error wrap.
   - `signals.py:37` object dtype after numeric coercion.
   - Add behavior assertions, not coverage-only smoke tests. If a selected edge is no longer reachable, prove it and move it to bucket C instead of forcing a test.

4. **P16-5 — delete or justify bucket-C dead branches.** Do not add tests to “buy” coverage. The existing candidates are: `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `execution.py:1287-1288`; `portfolio.py:180`; `metrics.py:94`; `signals.py:75`; `reconciliation.py:82-83`; `replay.py:172`; `cli.py:803-804`. Delete only with a concrete unreachability proof in the test/commit rationale; otherwise leave and document why it is defensive/dead. Do not delete reachable safety behavior.

5. **P16-6 — prove performance and continue.** Run `python3 scripts/perf_baseline.py --check` (rerun once if noisy), record exact metrics, refresh this file with timestamp/HEAD/tree/ledger/coverage evidence, then immediately start the next real correctness or safety defect. **Never stop at “campaign complete.”**

### Hard gates every session

Run from the repository root, in order:

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh
python3 scripts/perf_baseline.py --check
```

The full gate is authoritative: record TOTAL coverage, passed, failed, skipped, duration, and missed lines. Preserve the current **99% TOTAL** baseline (latest recorded: 6136 passed / 35 skipped / 0 failed, 93 missed; floor 98.5% must remain met). A timeout is not a test result; rerun. `BAB_GATE_SERIAL=1` is diagnosis-only. Do not modify `.github/workflows/main.yml`. No network, credentials, live orders, or live execution in tests; fakes/mocks/monkeypatch only. Preserve offline deterministic behavior and dry-run-safe live defaults.

### Session output contract (binding)

A session is failed unless it does all of the following:

1. Ships at least one production-code fix with a new or extended regression test, **or** converts a reachable bucket-B line with a behavior test. Record ✅/❌.
2. Leaves `ruff` clean and `bab_quick.sh` green.
3. Runs the full gate and records exact evidence in the P16 ledger below.
4. Updates this file's timestamp, HEAD/tree, verified state, and next binding message.
5. Continues to the next unblocked P16 item; if blocked, records the exact command/output and works on another unblocked item.

Do not spend a session re-deriving the A/B/C triage, rewording this handoff, or adding tests for provably dead lines.

## Current verified state

- **P16-1 (D1) shipped:** `inspect.stack()` caller-filename detection is gone; `pd.NaT`/`NaTType`, `None`, empty/non-finite values raise `ValueError`; `np.datetime64("NaT")` retains its legitimate passthrough. `tests/test_bab_p16_no_test_detection.py` proves caller-filename independence.
- **P16-2 (D3) shipped:** `BABDataError` is re-raised before the broad coercion handler in `calculate_beta`; `tests/test_bab_p16_beta_error_propagation.py` proves propagation from either argument path while plain `ValueError`/`TypeError` still become `NaN`. Verified this refresh: 4/4 pass (7/7 with the no-detection suite).
- **P16-3 still open:** contradictory defaults and the hard-coded 50-run floor disable explicit stale-data thresholds; safety-first tightening is the next production change.
- **Coverage baseline:** 99% TOTAL, 93 missed at the prior full gate. Per-file misses: `beta.py` 14 · `cli.py` 7 · `data_loader.py` 37 · `data_sources.py` 6 · `execution.py` 11 · `metrics.py` 1 · `portfolio.py` 11 · `reconciliation.py` 3 · `replay.py` 1 · `signals.py` 2; all other measured modules 100%. Treat this as a baseline to verify live, not a target.
- **Performance baseline:** `research_state/perf_baseline_real_fixture.json` records beta median `0.4852 ms`, full median `3.1852 ms`, peak `0.3441 MB`; this refresh’s `--check` reported `failures: []` (current: beta median `0.6585 ms`, full median `4.0471 ms`, peak `0.3447 MB`). Rerun rather than trusting stale output.

## Pre-triaged line map (authoritative — do not re-triage)

**A. Real defects:** D1 and D3 shipped; D2/P16-3 remains. D3 proof is green: an object whose `__array__` raises `BABDataError` passed as either return argument propagates. D2 proof: explicit `stale_run_threshold=3` currently cannot detect a 4–49 run because both implementations clamp the allowance to 50.

**B. Reachable edges:** the P16-4 list above. Use targeted, behavior-rich tests with fakes/mocks.

**C. Provably dead or defensive:** the P16-5 list above. Delete only with proof; never add coverage tests for dead lines.

## Bottlenecks removed this refresh (do not reopen)

- **Stale handoff pointer:** previous prose claimed P16-1 was unshipped while HEAD `8b9466d` already contained the production and regression changes; this refresh also advances past P16-2, which is shipped at `a0a0919`, and starts at P16-3.
- **Ambiguous next action:** “continue P16” is replaced by a named first fix, exact file/handler, proof obligation, and command order.
- **Quality-default stall:** the next session is told to characterize first, then tighten explicit thresholds and documented defaults, rather than debating the contradiction or weakening tests.
- **Coverage-chasing incentive:** the output contract fails handoff-only and dead-line-coverage sessions; reachable behavior tests and production fixes are mandatory.
- **Tool/edit stall:** if `edit` fails, retry once with a smaller unique `oldString`; after two failures use `write`. Do not repeat malformed edit calls. The diagnostics ledger contains many historical `kilo_edit_tool_invalid_arguments` signals; treat that as a known self-inflicted bottleneck, not a product defect.
- **CI/checkpoint noise:** the scheduled Kilo workflow can create frequent checkpoint commits. Do not modify the workflow and do not interpret checkpoint churn as progress. Real code + tests + gate evidence is the progress signal.
- **Fresh-runner bootstrap:** quick/gate auto-run `scripts/bab_bootstrap.sh`; missing optional dependencies are not a reason to abandon the gate.

## P16 campaign ledger (update every session)

| Step | Target | New/changed test | Status | Exact evidence |
|---|---|---|---|---|
| P16-1 | D1: remove caller-filename detection in `data_loader` | `tests/test_bab_p16_no_test_detection.py`; 3 wrong-contract tests | [x] | Shipped at HEAD `8b9466d`; clean tree and ruff pass verified 2026-11-15T22:09:38Z. Prior full gate: 6136p/35s/0f, 99% TOTAL (93 missed), floor 98.5%. |
| P16-2 | D3: propagate `BABDataError` from `beta.calculate_beta` | `tests/test_bab_p16_beta_error_propagation.py` | [x] | Shipped at HEAD `a0a0919`; 4/4 new tests pass (7/7 with no-detection suite) and `ruff check .` passes 2026-11-15T22:52:39Z. |
| P16-3 | D2: honor documented/explicit quality safety thresholds | characterization + regression tests | [ ] | Next action. Pin old behavior, then remove 50-run override and reconcile defaults with docs; full gate. |
| P16-4 | Bucket-B reachable edges | per-module tests | [ ] | execution/portfolio/cli/reconciliation/data_sources/data_loader/signals. |
| P16-5 | Bucket-C dead-branch deletion/justification | — | [ ] | Update map; no dead-line coverage tests. |
| P16-6 | Performance + next-defect handoff refresh | — | [ ] | `perf_baseline.py --check` failures must be `[]`; refresh and continue. |

## Protocol

1. Read this file and the `AGENT_HANDOFF.md` pointer.
2. Run `python3 -m ruff check .` and `bash scripts/bab_quick.sh` before editing.
3. Execute P16-2 → P16-3 → P16-4 → P16-5 → P16-6 top-down with minimal tested diffs.
4. If a step is blocked, record the exact command/output and switch to the next unblocked step; never stop at analysis.
5. Before finishing, run all applicable gates, update this file and the ledger, and leave the next session with a concrete next defect or task.