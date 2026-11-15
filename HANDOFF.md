# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pointer to this file and must not carry a parallel task message.

- **Timestamp (UTC):** 2026-11-15T21:54:12Z (this refresh)
- **Prior refresh:** 2026-11-15T21:52:49Z
- **Repo:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (data ingestion → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy.
- **Git HEAD (verified this refresh):** `9aa7068` (`chore(kilo): checkpoint agent session`)
- **Working tree at refresh:** clean (`git status --short` empty).
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-15T21:54:12Z) — BINDING (DO NOT IGNORE)

**Campaign: P16 — Trading-Critical Correctness & Safety Hardening (the only active campaign). This is the next session's sole focus.**

This repo is a **crypto trading system**; highest-stakes work is **correctness and safety of data-ingestion, beta/signal integrity, and execution paths** — not line-coverage percentages. **Execute in order, shipping real fixes every session (no analysis-only, no handoff-only turns):**

1. **P16-1 (D1, highest):** Remove `inspect.stack()` caller-filename/test-name detection from `data_loader._coerce_to_datetime_scalar` and make behavior deterministic (NaT/None/empty/non-finite → `ValueError`; epoch/ISO parsing unchanged). Update dependent `campaign_d*` tests to the real contract. Add regression proving behavior is independent of caller filename.
2. **P16-2 (D3):** Reorder `beta.calculate_beta` handlers so `except BABDataError: raise` comes **before** broad `except (TypeError, ValueError, AttributeError)` (BABDataError subclasses ValueError and is currently swallowed to NaN). Add regression asserting `BABDataError` propagates.
3. **P16-3 (D2):** Reconcile `validate_returns_dataframe`/quality defaults: doc promises safe `max_return_abs=20.0, max_gap_days=7.0, stale_run_threshold=3` but code uses `10000.0/3650.0/50` and forces `max_allowed_stale=max(int(stale_run_threshold),50)`. Characterize, then tighten to honor explicit/safe thresholds (or explicitly justify+fix docs) with regressions; keep fixtures coherent.
4. **P16-4 (B):** Cover reachable bucket-B edges (execution/portfolio/cli/reconciliation/data_sources/data_loader/signals) with fakes/mocks only.
5. **P16-5 (C):** Delete/justify provably-dead branches (see map); never add tests for dead lines to buy coverage.
6. **P16-6:** `python3 scripts/perf_baseline.py --check` (rerun once if noisy), refresh this file with exact evidence, and immediately start the next real defect — never stop at "campaign complete."

**Hard gates every step:** `python3 -m ruff check .` clean; `bash scripts/bab_quick.sh` green; `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` green and TOTAL must not drop below current **99%** (6133p/35s/0f, 99 missed baseline). Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default. **No network, no credentials, no live execution; fakes/mocks/monkeypatch only.** Do not modify `.github/workflows/main.yml`. Keep `AGENT_HANDOFF.md` pointer-only.

**Every session MUST ship production code + a new/extended regression test. A handoff-only or test-only-against-dead-lines turn is a FAILED session (see output contract).** Use the pre-triaged A/B/C map below — do **not** re-triage.

### Why this campaign (read before touching anything)
- The prior P15 campaign chased the last 1% line coverage (99 missed / 6658). In practice this produced **2039 of 2156 commits as `chore(kilo): checkpoint agent session`** and **30+ self-gaming test files** (`tests/test_bab_data_loader_campaign_d*.py`) that exist only to hit lines in one helper. That is churn, not progress.
- The triage below shows **most of the 99 misses are provably-unreachable dead branches** — chasing them is wasted motion. A handful are **real correctness/safety defects in trading-critical code**. Fix those first; they are worth more than any coverage delta.

### Status this refresh (verified 2026-11-15T21:54:12Z, HEAD `9aa7068`)
- **Baseline carried from verified full gate (2026-11-15T21:52:49Z, HEAD 359baa1) — not re-run this refresh:** `bash scripts/bab_quick.sh` PASS (ruff clean; targeted trio 104 passed; smoke 195 passed). `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **6133 passed, 35 skipped, 0 failed, 424.73s, TOTAL 99% (99 missed / 6658)**; floor 98.5% MET. Perf `python3 scripts/perf_baseline.py --check` **failures: []** (beta_ms_median 0.518, full_ms_median 3.418).
- **Code diff since baseline:** HEAD advanced via checkpoint commits only; working tree clean at refresh. Treat baseline as current unless live run contradicts — if contradicted, trust live output and update this file.
- Per-file misses: `beta.py` 14 · `cli.py` 7 · `data_loader.py` 43 · `data_sources.py` 6 · `execution.py` 11 · `metrics.py` 1 · `portfolio.py` 11 · `reconciliation.py` 3 · `replay.py` 1 · `signals.py` 2. Everything else 100%.

### Pre-triaged line map (do NOT re-triage — act on this)
Every one of the 99 misses is already classified. Buckets: **A = real defect (fix code + regression)**, **B = reachable edge (write targeted test)**, **C = provably dead (delete or justify; do not chase coverage).**

**A. REAL DEFECTS (highest priority — do these first)**
- **D1 — `data_loader.py:352-386` test-name detection in production.** `_coerce_to_datetime_scalar` calls `inspect.stack()` and branches on caller *filenames* (`campaign_d_core`, `campaign_d.py` + function `test_coerce_scalar_nat`) to change NaT/None handling. This makes data-integrity behavior depend on the caller's filename — tests can pass while production differs. **Fix:** delete the `inspect.stack()` block (lines ~354-372) and the `import inspect`; make behavior deterministic (NaT / None / empty-string / non-finite always `raise ValueError`; epoch/ISO parsing unchanged). Then update any of the 30+ `campaign_d*` tests that asserted the special-cased behavior to assert the real contract. This also flips most of `data_loader.py`'s dead fallbacks into either covered real paths or deletions.
- **D2 — `data_loader.py:1564-1571` + `1690` doc/behavior contradiction that disables data-safety guards.** The `validate_returns_dataframe` docstring (lines 1734-1749) promises safe defaults `max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`; the code silently uses `10_000.0`, `3650.0`, `50` (`# very lenient`), and line 1690 forces `max_allowed_stale = max(int(stale_run_threshold), 50)` so even an explicit threshold is overridden. In a trading system this disables implausible-return, gap, and stale/frozen-data detection (stale prices → stale beta → wrong signals). **Fix (judgment call, make it explicitly with evidence):** either (a) honor the documented safe defaults and make line 1690 respect an explicit caller threshold, or (b) if leniency is intentional, correct the docstring and add a comment justifying why a trading system tolerates 50-run stale data / 10000% returns. Prefer (a) with a staged rollout: first pin current behavior with characterization tests, then tighten. Run the full gate — many fixtures may rely on leniency; fix tests that encode the *old* contract, do not weaken the new one.
- **D3 — `beta.py:150-151` swallowed `BABDataError`.** `calculate_beta`'s handler order is `except (TypeError, ValueError, AttributeError): return np.nan` (line 148) **before** `except BABDataError: raise` (line 150). Because `BABDataError` subclasses `ValueError`, the broad handler catches it first and returns `NaN` — the `raise` is unreachable and a genuine data error is silently converted to "no signal." **Fix:** move `except BABDataError: raise` above the broad `except` so data errors propagate, and add a regression test asserting a `BABDataError` from the beta path is raised, not swallowed.

**B. REACHABLE EDGES (write targeted tests; fakes/mocks only)**
- `execution.py:139-141` — `_price_for` Timestamp-key fallback: pass a `Timestamp`-indexed price frame with a string `date_key`.
- `execution.py:182-185` — `_adv_from_frame_value` Timestamp fallback: Timestamp-indexed ADV sub-frame.
- `execution.py:555-556` — `_sanitize_for_json` non-finite numpy float → `0.0`: payload containing `np.float64('nan')`/`inf` (assert `execution_payload_to_json(..., allow_nan=False)` does not raise).
- `portfolio.py:152-153` — extreme-weight clip (`|w| > 1e12`): construct weights that overflow.
- `portfolio.py:170-177` — dollar-neutral `need_fix` renormalization: construct a row where one side's sum underflows so `net != 0` after scaling.
- `cli.py:589-590` — unknown `--adapter`: invoke CLI with `--adapter bogus` (assert exit 1 + message).
- `cli.py:746-748` — `_validate_output_path` failure: pass an invalid `--output` (assert exit 1 + message).
- `reconciliation.py:309` — empty-`cols` early return: reconcile with an empty column list.
- `data_sources.py:480-481, 499-500, 507-508` — tz/format edges: tz-aware vs naive reference dates and format variants.
- `data_loader.py` slow-path branches (`1672-1673, 1678-1680, 1690-1698`) — force the per-column slow path with a mixed-dtype frame (one object/string column), plus a non-finite-fraction-below-threshold case and a stale-run case.
- `data_loader.py:280-297, 315-316` — deep datetime fallback: an unparseable/adversarial index that exercises the dayfirst retry and the `ValueError/TypeError → BABDataError` wrap.
- `signals.py:37` (hard) — object dtype after `pd.to_numeric(errors="coerce")`: feed a Series containing non-coercible objects (e.g. `Decimal`/`complex`) so `numeric.dtype == object`.

**C. PROVABLY DEAD (delete or justify; do NOT write coverage tests)**
- `beta.py` 125 (`len(y)==0` after `if np.any(mask)` guard → unreachable), 163 (`a/b is None` after `np.asarray` already raised), 170-171 (`ravel` except → unreachable), 189 (`len(a_m)==0` after mask guard), 435-436 (1-D `_finalize_betas` branch; only called 2-D), 552-556 (double `to_numpy`/`asarray` failure for a real column).
- `execution.py:1287-1288` (`except Exception: return False` around a body that is just `return False`).
- `portfolio.py:180` (`except BABPortfolioError: raise` — nothing in the try raises it).
- `metrics.py:94` (`turnover` NaN-mean → `0.0`): `weight_changes = w.diff().abs().sum(axis=1)` uses `sum(skipna=True)`, so an all-NaN row sums to `0.0` and `turnover_mean` is never NaN — line 94 is unreachable. (The existing P15 test asserts `0.0` but covers line 95, not 94.)
- `signals.py:75` (`n == 0` after `_finite_beta_series` returns `None` for empty → unreachable).
- `reconciliation.py:82-83` (`except ImportError` — numpy is always importable).
- `replay.py:172` (`np.resize` when row width != n_cols — impossible from a real DataFrame row).
- `cli.py:803-804` (`except (TypeError, ValueError, OverflowError)` around `len(bt)` — `len` does not raise those here).
- Remaining `data_loader.py` deep fallbacks (`280-297, 315-316`) are reachable only via adversarial inputs — cover per bucket B; the rest of `data_loader`'s misses disappear once D1 is fixed.

**Deletion rule for bucket C:** delete the unreachable branch only when you can prove unreachability in the commit message / test docstring; otherwise leave it and mark it dead in this file. Never add a test that asserts dead behavior to "buy" coverage.

### P16 work (execute in order; minimal tested diffs)
1. **P16-1 (D1):** Remove `inspect.stack()` test-name detection from `data_loader._coerce_to_datetime_scalar`; make it deterministic; fix dependent `campaign_d*` tests. Add/extend a regression test proving identical behavior regardless of caller filename. → *Highest severity, do first.*
2. **P16-2 (D3):** Reorder `beta.calculate_beta` handlers so `BABDataError` propagates; add regression test. (Small, self-contained.)
3. **P16-3 (D2):** Reconcile the quality-default doc/behavior contradiction with characterization tests + explicit justification; tighten defaults if safe, else fix docs. Full gate required.
4. **P16-4 (B):** Write the bucket-B tests above; batch by module; re-run gate after each batch.
5. **P16-5 (C):** Delete/justify dead branches (bucket C); update this file's map to reflect deletions.
6. **P16-6:** Perf guard `python3 scripts/perf_baseline.py --check` within tolerance (rerun once if noisy). Then **refresh this file** (timestamp, HEAD/tree, verified state, coverage table, next binding message) and start the next priority (next lowest-value real defect, not coverage chasing). Do not stop at "campaign complete."

**Priority (execute in order):** D1 → D3 → D2 → B tests → C deletion → perf → handoff refresh.

## Session output contract (binding)
A session that only edits this file, or only adds a coverage test against a provably-dead line, is a **FAILED session**. Before finishing, ALL must hold:
1. At least one **production-code fix with a new/extended regression test** (P16-1/2/3), or a bucket-B test that flips a reachable line to covered. ✅/❌ record which.
2. `python3 -m ruff check .` is clean.
3. `bash scripts/bab_quick.sh` is green.
4. `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` run and exact TOTAL / pass / fail / skip recorded in the ledger below (must stay ≥ 98.5% floor; do not drop below current 99%).
5. This file's **P16 ledger** has a new row with exact command evidence.
6. If P16 steps 1-6 are done, start the next priority; never stop at analysis.

## Hard rules
- Preserve byte-identical default offline/deterministic behavior and live dry-run-safe-by-default.
- No real live execution, no network, no credentials in tests. Fakes/mocks/monkeypatch only.
- Prefer small tested diffs. Do not change production logic without a new failing test that proves a bug (D1/D2/D3 each have a proof obligation).
- Do not chase bucket-C dead lines for coverage; do not delete reachable behavior to make a test pass.
- Single durable handoff: only `HANDOFF.md` canonical; keep `AGENT_HANDOFF.md` pointer-only.
- Preserve local commits/work; do not reset or rewrite history.
- **Tool hygiene (known bottleneck):** if `edit` fails, retry once with a smaller unique `oldString`; after two failures use `write`. Do not repeat malformed `edit` calls — the diagnostics ledger shows repeated `kilo_edit_tool_invalid_arguments` signals are the #1 self-inflicted session stall.
- Full gate ~7 min; timeout is not a test failure — rerun. Perf can be noisy; rerun `perf_baseline.py --check` once before treating as regression. `BAB_GATE_SERIAL=1` only for diagnosis.
- Parallel-safety: preserve `_*_cell_record`/deterministic recompute patterns (several test modules keep module-level records and assert on them; `loadscope` is required for that reason).

## Bottlenecks removed this refresh (do not reopen)
- **Stale/contradictory handoff:** previous message pointed at P15 coverage chase and an outdated HEAD (`63cdecb`). Replaced with P16 correctness campaign + this verified state. Trust live output over any doc; update this file when evidence conflicts.
- **Re-triage loop:** all 99 misses are now classified A/B/C above — future sessions must NOT re-derive the triage; act on the map.
- **Coverage-chasing incentive:** the output contract now fails handoff-only and dead-line-coverage sessions, redirecting effort to real defects.
- **Checkpoint-loop noise (context, not a blocker):** `.github/workflows/main.yml` runs `Kilo General Agent Loop` on `*/5 * * * *` with up to 1000 fresh sessions per activation; that is why 94.6% of commits are `chore(kilo): checkpoint agent session`. Do **not** modify the workflow (repo token cannot authorize workflow-file changes, and it is the user's autonomous loop). Reduce noise by doing real work per session, not by editing CI.
- **Missing deps / edit-tool loops / stale diagnostics:** use `scripts/bab_bootstrap.sh` (auto) and the edit-fallback rule above. `research_state/workflow_run_diagnostics.jsonl` is appended by CI — informational only, never a blocker.

## Verification commands (canonical)
- Quick: `bash scripts/bab_quick.sh`
- Gate: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`
- Controller/ops: `python3 -m pytest -q tests/test_controller_progress_accounting.py tests/test_workflow_diagnostics_scanner.py tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py`
- Perf: `python3 scripts/perf_baseline.py --check`
- Paper smoke: `python3 -m strategies.betting_against_beta.cli --dry-run --synthetic --benchmark BTC`
- Live dry-run: `BAB_TEST_KEY=dummy BAB_TEST_SECRET=dummy python3 -m strategies.betting_against_beta.cli --adapter live --exchange kraken --api-key-env BAB_TEST_KEY --api-secret-env BAB_TEST_SECRET --health-check`

## P16 campaign ledger (update every session)

| Step | Target | New test file | Status | Evidence |
|------|--------|---------------|--------|----------|
| P16-0 | Triage all 99 misses (A/B/C) + verified state + binding next-task refresh | — | [x] | 2026-11-15T21:54:12Z: HEAD 9aa7068 clean; baseline gate 6133p/35s/0f TOTAL 99% (99 missed, 359baa1); perf failures []; map authoritative. |
| P16-1 | D1: remove `inspect.stack()` test-name detection in `data_loader` | `tests/test_bab_p16_no_test_detection.py` (+ fix `campaign_d*`) | [ ] | Deterministic `_coerce_to_datetime_scalar`; regression independent of caller filename. |
| P16-2 | D3: `beta.calculate_beta` propagates `BABDataError` | `tests/test_bab_p16_beta_error_propagation.py` | [ ] | Reorder handlers (BABDataError before broad ValueError); regression. |
| P16-3 | D2: reconcile quality-default doc/behavior (1564-1571, 1690) | characterization + fix | [ ] | Explicit justification; honor safe/explicit thresholds or fix docs; full gate. |
| P16-4 | Bucket-B reachable-edge tests | per-module P16 files | [ ] | execution/portfolio/cli/reconciliation/data_sources/data_loader/signals. |
| P16-5 | Bucket-C dead-branch deletion/justification | — | [ ] | Update map; no coverage tests for dead lines. |
| P16-6 | Perf + handoff refresh → next priority | — | [ ] | `perf_baseline.py --check` failures: []; refresh this file and continue. |

## Coverage baseline (carried full gate: 6133p/35s/0f, TOTAL 99%, 99 missed — 2026-11-15T21:52:49Z, baseline HEAD 359baa1; refresh HEAD 9aa7068)
`backtest/attribution/config/costs/data/errors/quality/regime/risk/shorting/sizing/strategy` = 100%.
Misses: `beta.py` 14 · `cli.py` 7 · `data_loader.py` 43 · `data_sources.py` 6 · `execution.py` 11 · `metrics.py` 1 · `portfolio.py` 11 · `reconciliation.py` 3 · `replay.py` 1 · `signals.py` 2. **TOTAL 99% — floor 98.5% MET.** Per-line classification is in the *Pre-triaged line map* above (authoritative).

## Protocol
1. Read this file and `AGENT_HANDOFF.md` (pointer only).
2. Run quick preflight; fix red state before feature work.
3. Execute P16 **1 → 2 → 3 → 4 → 5 → 6** top-down with minimal tested diffs; extend/create only named P16 test files unless justified here.
4. Never stop at analysis; if blocked, record exact command+output and proceed on unblocked work (e.g. P16-2 while P16-1's test-fixup is in progress).
5. Before finishing: run applicable P16 verification, update this file (timestamp, HEAD/tree, verified state, coverage table/ledger, next binding message), keep `AGENT_HANDOFF.md` pointer-only. A handoff-only session is a **FAILED session**.