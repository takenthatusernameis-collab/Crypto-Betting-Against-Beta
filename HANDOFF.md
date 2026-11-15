# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T23:10:00Z (this refresh)
- **Repo:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (data ingestion → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy.
- **Git HEAD (verified this refresh):** `37e1922` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean; `python3 -m ruff check .` → `All checks passed!`
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T23:10:00Z) — BINDING (DO NOT IGNORE)

**Campaign P16 — Trading-Critical Correctness & Safety Hardening. This is the next session's sole focus. Start at P16-3. Do NOT restart P16-1/P16-2, re-triage the A/B/C map, or re-derive this handoff.**

This is a **crypto trading system**. The highest-stakes work is correctness and safety of data ingestion, beta/signal integrity, portfolio construction, and execution/ops — **not line-coverage percentages**. Ship real production fixes with proof tests every session. **Analysis-only, handoff-only, formatting-only, and coverage-against-dead-lines turns are failed sessions.**

### P16-3 (highest priority — execute first) — honor quality-safety thresholds, safety-first

The data-quality contract is currently **unsafe and self-contradictory**. Live-verified at HEAD `37e1922` (reproduce with the two probes below before editing):

- **Doc/impl contradiction.** `validate_returns_dataframe` docstring (`data_loader.py:1713-1716`) promises defaults `stale_run_threshold=3`, `max_gap_days=7.0`, `max_return_abs=20.0`. The implementation (`data_loader.py:1536-1541`) uses `10_000.0`, `3650.0`, `50` ("very lenient").
- **Explicit thresholds are ignored.** Both quality paths clamp the allowance with `max_allowed_stale = max(int(stale_run_threshold), 50)` — fast path `data_loader.py:1622-1636`, slow path `data_loader.py:1656-1668`. An explicit `stale_run_threshold=3` therefore **cannot** reject a 4–49 equal-value run.
- **Dict `quality` is silently dropped (worse than P16-3's prior framing).** `quality` is typed `bool` (`data_loader.py:1679`) and dispatched by truthiness only (`data_loader.py:1895`). **There is no dict parsing anywhere in the module.** Six tests already pass `quality={"stale_run_threshold": 3}` / `{"max_gap_days": 2}` / `{"allow_duplicate_timestamps": ...}` (all in `tests/test_bab_data_loader_coverage_gaps.py`, lines 5402, 5719, 5727, 5738), and `tests/test_bab_data_loader_batch46.py` etc. Those dicts are **silently ignored** — the campaign runs with the lenient defaults and the caller's intent is lost.

**Reproduce (run from repo root):**

```bash
python3 - <<'EOF'
import pandas as pd
from strategies.betting_against_beta import data_loader as dl
idx = pd.date_range("2020-01-01", periods=8, freq="D")
df = pd.DataFrame({"BTC":[0.01]*8, "ETH":[0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09]}, index=idx)
for label, kw in [
    ("explicit threshold=3 (direct)", dict(quality=True, stale_run_threshold=3)),
    ("dict quality threshold=3",      dict(quality={"stale_run_threshold": 3})),
]:
    try:
        dl.validate_returns_dataframe(df.copy(), benchmark="ETH", **kw)
        print(f"{label}: NO RAISE  <-- BUG (8-long frozen BTC run not rejected)")
    except Exception as e:
        print(f"{label}: rejected {type(e).__name__}")
EOF
```

**Fix, in this order:**

1. **Characterization tests first.** Add tests that pin *current* behavior for: (a) a 10000% return, (b) a 100-day gap, (c) a 4–49 equal-value run with explicit `stale_run_threshold=3`, (d) the fast numeric path, (e) `quality` passed as a dict. These must fail on HEAD for the cases you are about to fix and pass after.
2. **Remove the 50-run floor.** Delete `max(int(stale_run_threshold), 50)` in both paths (`data_loader.py:1623`, `:1662`) so an explicit threshold is honored. Keep the `finite_count >= threshold` / `int(stale_run_threshold) > 0` guards intact (threshold `0` still disables).
3. **Reconcile defaults with the docstring.** When `quality` is truthy and a threshold arg is `None`, use the documented safe defaults (`max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`) instead of `10000/3650/50`. Update the inline comments at `data_loader.py:1848-1854` that justify the lenient `10000` threshold — that justification is now wrong.
4. **Parse dict `quality`.** Accept `quality` as `bool | dict`. When it is a dict, treat it as per-call overrides merged under the explicit kwargs (`{max_return_abs, max_gap_days, stale_run_threshold, min_finite_fraction, allow_duplicate_timestamps}`), with explicit function kwargs taking precedence. Preserve `quality=False` as the explicit opt-out. `quality=True` must not silently disable the documented guards.
5. **Treat old-contract tests as regressions to update, not contracts to preserve.** Search every caller/test before flipping defaults: `validate_returns_dataframe`, `_run_data_quality_campaign`, the real-data loaders (`load_returns*`, `load_prices*`), backtests, and the performance oracles in `tests/test_validation_performance.py` (`_oracle_quality` at lines 54-97 and the `stale_run_threshold=50` references) — those must be updated to the new semantics or they will mask the fix.
6. **No undocumented global escape hatch.** If the full gate exposes unavoidable compatibility coupling, keep the stricter behavior, document the deliberate migration, and isolate any compatibility switch behind an explicit opt-in kwarg. Do **not** re-add a lenient default or a `max(...,50)` floor.
7. **Proof obligation:** one test that fails on HEAD and passes after the fix, for *each* changed guard (defaults, 50-run floor, dict parsing). Record exact commands/results in the ledger.

### P16-4 — convert remaining reachable bucket-B edges into targeted behavior tests

Use fakes/mocks only; batch by module and rerun the full gate after each batch. Add behavior assertions, not coverage-only smoke tests. If an edge is now unreachable, prove it and move it to bucket C.

- `execution.py:139-141` Timestamp-key fallback with a string `date_key`.
- `execution.py:182-185` Timestamp-indexed ADV sub-frame.
- `execution.py:555-556` non-finite numpy float JSON sanitization with `allow_nan=False`.
- `portfolio.py:152-153` extreme-weight clipping; `portfolio.py:170-177` dollar-neutral `need_fix` renormalization under one-sided underflow.
- `cli.py:589-590` unknown adapter; `cli.py:746-748` invalid output path.
- `reconciliation.py:309` empty-column early return.
- `data_sources.py:480-481, 499-500, 507-508` timezone/format edges.
- `data_loader.py` mixed-dtype slow path, finite-fraction boundary, stale-run boundary, adversarial datetime dayfirst retry/error wrap.
- `signals.py:37` object dtype after numeric coercion.

### P16-5 — delete or justify bucket-C dead branches

Do not add tests to "buy" coverage. Candidates: `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `execution.py:1287-1288`; `portfolio.py:180`; `metrics.py:94`; `signals.py:75`; `reconciliation.py:82-83`; `replay.py:172`; `cli.py:803-804`. Delete only with a concrete unreachability proof in the test/commit rationale; otherwise leave and document why it is defensive/dead. Never delete reachable safety behavior.

### P16-6 — prove performance, then continue to the next real defect

Run `python3 scripts/perf_baseline.py --check` (rerun once if noisy), record exact metrics, refresh this file with timestamp/HEAD/tree/ledger/coverage evidence, then immediately start the next real correctness or safety defect. **Never stop at "campaign complete."**

### Hard gates every session (run from repo root, in order)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh
python3 scripts/perf_baseline.py --check
```

The full gate is authoritative: record TOTAL coverage, passed, failed, skipped, duration, and missed lines. Preserve the current **99% TOTAL** baseline (latest recorded: 6136 passed / 35 skipped / 0 failed, 93 missed; floor 98.5% must remain met). A timeout is not a test result; rerun. `BAB_GATE_SERIAL=1` is diagnosis-only. Do not modify `.github/workflows/main.yml`. No network, credentials, live orders, or live execution in tests; fakes/mocks/monkeypatch only. Preserve offline deterministic behavior and dry-run-safe live defaults.

### Session output contract (binding)

A session is failed unless it does **all** of the following:

1. Ships at least one production-code fix with a new/extended regression test, **or** converts a reachable bucket-B line with a behavior test. Record ✅/❌.
2. Leaves `ruff` clean and `bab_quick.sh` green.
3. Runs the full gate and records exact evidence in the P16 ledger below.
4. Updates this file's timestamp, HEAD/tree, verified state, and next binding message.
5. Continues to the next unblocked P16 item; if blocked, records the exact command/output and works on another unblocked item.

Do not spend a session re-deriving the A/B/C triage, rewording this handoff, or adding tests for provably dead lines.

## Current verified state

- **P16-1 (D1) shipped:** `inspect.stack()` caller-filename detection is gone; `pd.NaT`/`NaTType`, `None`, empty/non-finite values raise `ValueError`; `np.datetime64("NaT")` retains its legitimate passthrough. `tests/test_bab_p16_no_test_detection.py` proves caller-filename independence.
- **P16-2 (D3) shipped:** `BABDataError` is re-raised before the broad coercion handler in `beta.calculate_beta`; `tests/test_bab_p16_beta_error_propagation.py` proves propagation from either argument path while plain `ValueError`/`TypeError` still become `NaN`. Verified prior refresh: 4/4 pass (7/7 with the no-detection suite).
- **P16-3 still open — now sharpened:** contradictory defaults, the hard-coded 50-run floor, **and** silent dict-`quality` dropping are all confirmed live at HEAD `37e1922` (see the reproduction block above). Safety-first tightening is the next production change.
- **Coverage baseline (verify live, do not trust):** 99% TOTAL, 93 missed at the prior full gate. Per-file misses: `beta.py` 14 · `cli.py` 7 · `data_loader.py` 37 · `data_sources.py` 6 · `execution.py` 11 · `metrics.py` 1 · `portfolio.py` 11 · `reconciliation.py` 3 · `replay.py` 1 · `signals.py` 2; all other measured modules 100%.
- **Performance baseline:** `research_state/perf_baseline_real_fixture.json` records beta median `0.4852 ms`, full median `3.1852 ms`, peak `0.3441 MB`. Rerun `--check` rather than trusting stale output.

## Pre-triaged line map (authoritative — do not re-triage)

**A. Real defects:** D1 and D3 shipped; D2/P16-3 remains and is broader than previously stated (defaults + 50-run floor + dict-`quality` drop). D2 proof: explicit `stale_run_threshold=3` cannot reject a 4–49 run because both implementations clamp the allowance to 50. Dict proof: `quality={"stale_run_threshold": 3}` is truthy but never parsed, so the campaign runs with lenient defaults.

**B. Reachable edges:** the P16-4 list above. Use targeted, behavior-rich tests with fakes/mocks.

**C. Provably dead or defensive:** the P16-5 list above. Delete only with proof; never add coverage tests for dead lines.

## Bottlenecks removed this refresh (do not reopen)

- **Understated P16-3:** prior prose framed it as "reconcile defaults + remove 50-run floor." The dict-`quality` silent drop is a *separate, higher-severity* contract break (six existing tests already rely on dict form). The fix now mandates parsing dict `quality` and honoring explicit thresholds. This is the primary unblocking.
- **Hidden coupling in the performance oracle:** `tests/test_validation_performance.py` `_oracle_quality` (lines 54-97) hard-codes `max(stale_run_threshold, 50)` and `stale_run_threshold=50` references. It will mask or contradict the fix. The next session is told to update it in the same change.
- **Stale HEAD pointer:** `AGENT_HANDOFF.md` previously pointed at HEAD `a0a0919`; HEAD is now `37e1922` (handoff-only checkpoint commits since). Code state for P16-1/P16-2 is unchanged. Trust live output over stale prose.
- **Ambiguous next action:** "continue P16" is replaced by a named first fix (P16-3), exact file/line targets, a reproduction script, and a per-guard proof obligation.
- **Quality-default stall:** the next session characterizes first, then tightens explicit thresholds and documented defaults, rather than debating the contradiction or weakening tests.
- **Coverage-chasing incentive:** the output contract fails handoff-only and dead-line-coverage sessions; reachable behavior tests and production fixes are mandatory.
- **Tool/edit stall:** if `edit` fails, retry once with a smaller unique `oldString`; after two failures use `write`. Do not repeat malformed edit calls. The diagnostics ledger contains many historical `kilo_edit_tool_invalid_arguments` signals; treat that as a known self-inflicted bottleneck, not a product defect.
- **CI/checkpoint noise:** the scheduled Kilo workflow can create frequent checkpoint commits. Do not modify the workflow and do not interpret checkpoint churn as progress. Real code + tests + gate evidence is the progress signal.
- **Fresh-runner bootstrap:** quick/gate auto-run `scripts/bab_bootstrap.sh`; missing optional dependencies are not a reason to abandon the gate.

## P16 campaign ledger (update every session)

| Step | Target | New/changed test | Status | Exact evidence |
|---|---|---|---|---|
| P16-1 | D1: remove caller-filename detection in `data_loader` | `tests/test_bab_p16_no_test_detection.py`; 3 wrong-contract tests | [x] | Shipped at HEAD `8b9466d`; clean tree and ruff pass verified 2026-11-15T22:09:38Z. Prior full gate: 6136p/35s/0f, 99% TOTAL (93 missed), floor 98.5%. |
| P16-2 | D3: propagate `BABDataError` from `beta.calculate_beta` | `tests/test_bab_p16_beta_error_propagation.py` | [x] | Shipped at HEAD `a0a0919`; 4/4 new tests pass (7/7 with no-detection suite) and `ruff check .` passes 2026-11-15T22:52:39Z. |
| P16-3 | D2: honor documented/explicit quality safety thresholds + parse dict `quality` | characterization + regression tests; update `_oracle_quality` in `tests/test_validation_performance.py` | [ ] | Next action. Pin old behavior, remove 50-run floor (both paths), reconcile defaults with docstring, parse dict `quality`; full gate. |
| P16-4 | Bucket-B reachable edges | per-module tests | [ ] | execution/portfolio/cli/reconciliation/data_sources/data_loader/signals. |
| P16-5 | Bucket-C dead-branch deletion/justification | — | [ ] | Update map; no dead-line coverage tests. |
| P16-6 | Performance + next-defect handoff refresh | — | [ ] | `perf_baseline.py --check` failures must be `[]`; refresh and continue. |

## Protocol

1. Read this file and the `AGENT_HANDOFF.md` pointer.
2. Run `python3 -m ruff check .` and `bash scripts/bab_quick.sh` before editing.
3. Reproduce the P16-3 bug with the script above, then execute P16-3 → P16-4 → P16-5 → P16-6 top-down with minimal tested diffs.
4. If a step is blocked, record the exact command/output and switch to the next unblocked step; never stop at analysis.
5. Before finishing, run all applicable gates, update this file and the ledger, and leave the next session with a concrete next defect or task.