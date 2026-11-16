# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T08:20:06Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. Highest-stakes paths: what real orders are placed and whether live fills still match the model.
- **Git HEAD (verified this refresh):** `934f008` (`main`, working tree has uncommitted P18-3 changes: `scripts/bab_reconcile_gate.sh`, `.github/workflows/main.yml`, `README.md` — not yet committed; commit when authorized).
- **Live probes re-verified 2026-11-16T08:15Z @934f008:** Core test suite **6193 passed / 35 skipped** (excluding broken P17-2 targeted gap tests). `python3 -m ruff check .` **clean**. Coverage **99%** (91 missing stmts across 10 modules — see coverage report below). Full gate fails only due to `tests/test_bab_p17_2_targeted_gaps.py` (24 failures from API mismatches in the test file itself — the production code is sound).
- **P18-3 DONE @934f008 (uncommitted):** `scripts/bab_reconcile_gate.sh` created — deterministic CI reconcile gate proving drift fails closed (rc=2 on intentional drift) and clean passes (rc=0). Wired into `.github/workflows/main.yml` as a dedicated step after controller tests. `README.md` documents `--reconcile-tolerance`, `--reconcile-max-mismatch` (enforcement semantics, `--reconcile` alone emit-only/backward-compatible) and `--allow-live-execution` + `--accept-terms` (exact token `I_UNDERSTAND_LIVE_TRADING`, dry-run default, never echoed/logged). Proof recorded: drift `rc=2` with "Reconciliation drift gate breached: costs.delta_max_abs: actual=0.02 tolerance=0.0"; clean `rc=0`; emit-only `rc=0`.

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T08:20:06Z) — BINDING (DO NOT IGNORE)

**Campaign P18-3 is COMPLETE** — reconciliation/live-safety gate is enforced in CI and documented. DoD met (proof recorded in ledger below).

**Next focus (binding, immediate):** deferred backlog **P17-2** — fix and complete targeted behavior tests for reachable missed lines to push per-module coverage from 99% toward the 98.5%+ floor. The file `tests/test_bab_p17_2_targeted_gaps.py` exists but has **24 test failures due to API mismatches** (wrong function signatures, missing imports, incorrect parameter names). The production code is correct; the test file must be repaired to match actual APIs.

**Current coverage gaps (91 missing statements, `bash scripts/bab_gate.sh`):**
- `beta.py`: lines 125, 163, 170-171, 189, 435-436, 552-556 (12 missed)
- `data_loader.py`: lines 280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1355, 1615, 1654-1655, 1660-1662, 1676-1681, 1958-1959, 2762-2763 (34 missed)
- `execution.py`: lines 139-141, 182-185, 563-564, 1295-1296 (11 missed)
- `cli.py`: lines 75, 657-658, 836-838, 893-894 (8 missed)
- `portfolio.py`: lines 152-153, 170-177, 180 (11 missed)
- `data_sources.py`: lines 480-481, 499-500, 507-508 (6 missed)
- `reconciliation.py`: lines 82-83, 309, 455, 458 (5 missed)
- `signals.py`: lines 37, 75 (2 missed)
- `metrics.py`: line 94 (1 missed)
- `replay.py`: line 172 (1 missed)

**Repair strategy for `test_bab_p17_2_targeted_gaps.py`:**
1. Fix imports: `BABPortfolioError` from `portfolio` (not `errors`); `ReplayHarness` from `replay` (not `ReplayEngine`); `reconcile_costs` not `_reconcile_costs`; `_sanitize_for_json` from `execution` (not `reconciliation`); `turnover` not `mean_turnover`.
2. Fix API calls per module:
   - `construct_portfolio(signals_df=..., betas_df=..., weights_df=...)` — three required positional-or-kw args.
   - `calculate_rolling_beta(df, window=..., min_obs=...)` — no `benchmark=` kwarg; benchmark is a column in `df`.
   - `LiveExecutionAdapter(exchange=..., dry_run=...)` — no `prices=`; prices set via internal frame or adapter methods.
   - `LiveExecutionAdapter._adv_from_frame_value` is private; test via public method or remove.
   - `load_prices/load_returns` do not accept `min_finite_fraction`/`stale_run_threshold` directly; those are internal quality params.
   - `reconcile_costs(backtest_returns, backtest_weights, fills, ...)` — different signature.
   - `evaluate_reconciliation_gate(costs_rec, fills_rec, cost_tolerance, max_mismatch)` — no `returns`/`weights` args.
   - `_series_is_parseable(series, mask)` — no `threshold` kwarg.
3. Fix test logic: use valid date ranges (gap ≤7 days), sufficient rows (≥2), correct exception types (`BABDataError` not generic).

**Do NOT coverage-chase without correctness.** Use fakes/mocks with behavior assertions matching actual code paths. Do not stop at "campaign complete"; the controller counts a session with no code/test change as no progress. **Do not reply with a handoff-only update.**

## Verified completion state (do not redo)

- **P17-1 DONE:** safe data-quality defaults wired (20/7/3), `load_prices` runs quality campaign by default, `tests/test_bab_pipeline_safety_contract.py` (8) present; old lax contract inverted in `tests/test_bab_quality_threshold_contract.py`.
- **P18-1 DONE @7546200+/current:** `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach, `--reconcile` alone unchanged); `tests/test_bab_reconciliation_gate.py` (9) RED→GREEN recorded.
- **P18-2 DONE (current):** `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False` (refuses before CCXT); CLI `--allow-live-execution`/`--accept-terms` wired, dry-run default preserved; `tests/test_bab_live_opt_in.py` (5) present and green.
- **P18-3 DONE @934f008 (uncommitted):** `scripts/bab_reconcile_gate.sh` created; wired into `.github/workflows/main.yml`; `README.md` documents all P18 safety flags. Fail-closed proven (rc=2 on drift) + pass on clean (rc=0). `ruff` clean, `bab_gate.sh` GREEN 6177/35/99%.
- **Kill switch (R4-B) covered:** `tests/test_bab_drawdown_kill_switch_r4.py` — verify only.
- **P17-2 coverage items (deferred → NOW):** reachable missed statements remain in 10 modules (see coverage report above). **NEXT FOCUS** — repair `test_bab_p17_2_targeted_gaps.py` to target these lines with correct APIs.

## Deferred backlog (only after P17-2 DoD)

- **P17-3:** delete/justify bucket-C dead branches only with concrete unreachability proof; never remove reachable safety behavior.
- **P17-4:** `python3 scripts/perf_baseline.py --check` (record metrics), then next real defect.
- **A.** test-suite perf/reliability (`--durations=20`, keep `--dist loadscope`, coverage ≥98.5%).
- **B.** real-data pipeline hardening (timezone, 429 Retry-After, exact `--accept-terms`, `--metadata-out` audit).
- **C.** execution adapter completeness (CCXT dry-run default preserved, reconciliation tolerances, `--health-check` JSON, paper-adapter stress).
- **D.** risk/regime enhancements (kill-switch flattening verify, beta-neutral tracking-error, regime hysteresis, sizing edges).

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # release floor must hold
```

## Non-goals (do not pursue)

- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Coverage-chasing instead of correctness/production fixes.
- ❌ Handoff-only sessions.

## Bottleneck removal status

- ✅ Single durable handoff: only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`).
- ✅ Stale bindings cleared: P17 complete; P18-1/P18-2 complete; binding now **P17-2**.
- ✅ Gate parallel by default (`-n $(nproc) --dist loadscope`); `bab_bootstrap.sh` auto-installs deps.
- ✅ Nested `.github/workflows` protected by force-restore/clean (not case patterns).
- ✅ **P18-3 RESOLVED** — reconciliation/live-safety enforcement implemented in code, enforced in CI via `scripts/bab_reconcile_gate.sh` invoked by `.github/workflows/main.yml`, documented in `README.md`. Future changes that drop enforcement will turn CI RED.
- ⚠️ **NEW BOTTLENECK (P17-2):** `tests/test_bab_p17_2_targeted_gaps.py` has 24 API-mismatch failures blocking gate. Must repair test file to match actual module APIs before gate passes.

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T02:41:36Z | 9e15f9a | Handoff refresh (no code). | GREEN @02:37Z |
| 2026-11-16T04:54:45Z | 8ff2115 | Consolidated handoff; verified P17-1/P18 binding set. | GREEN @04:54Z |
| 2026-11-16T05:57:40Z | 7546200 | Handoff refresh (no code). | not re-run |
| 2026-11-16T05:59:02Z | 7546200+ | P18-1 reconciliation drift gate + CLI tolerances + tests (9) RED→GREEN. | GREEN @05:59Z |
| 2026-11-16T06:44:17Z | 5c1a6fb | Handoff refresh: verified P18-1/P18-2 implemented and characterization suites green (14 passed), `ruff` clean; identified P18-3 (CI enforce + README docs) as sole remaining blocker and restamped binding. No production code change this turn. | not re-run (last GREEN recorded @05:59Z; rerun after P18-3 changes) |
| 2026-11-16T06:50:42Z | 934f008+ | P18-3 complete: created `scripts/bab_reconcile_gate.sh` (deterministic CI reconcile gate, fail-closed rc=2 on drift, pass rc=0 on clean); wired into `.github/workflows/main.yml`; documented `--reconcile-tolerance`, `--reconcile-max-mismatch`, `--allow-live-execution`, `--accept-terms` in `README.md`. Proof: drift `rc=2` "costs.delta_max_abs: actual=0.02 tolerance=0.0"; clean `rc=0`; emit-only `rc=0`. `ruff` clean; `bab_gate.sh` GREEN 6177 passed / 35 skipped / 99%. Changes uncommitted. | GREEN @06:50Z |
| 2026-11-16T06:52:04Z | 934f008+ | Handoff refresh: stamped new binding P17-2 with per-module missed-line targets. Verified ruff clean, gate GREEN 99%. | GREEN @06:50Z |
| 2026-11-16T08:20:06Z | 934f008+ | Repaired import errors in `test_bab_p17_2_targeted_gaps.py` (BABPortfolioError, ReplayHarness, reconcile_costs, turnover). Gate run: core 6193 passed, P17-2 test file 24 failures from API mismatches. Ruff clean. Coverage 99% (91 missed). **Binding now: repair P17-2 test file to match actual APIs.** | RED (P17-2 test file only) |

---

**Next agent (binding):** P18-3 is COMPLETE. Start immediately at **deferred backlog P17-2** — **repair `tests/test_bab_p17_2_targeted_gaps.py`** to fix 24 API-mismatch failures (wrong imports, signatures, parameters) so it correctly exercises the 91 missed lines across 10 modules listed above. Use the repair strategy in the INITIAL TASK MESSAGE. After test file passes, verify `bash scripts/bab_gate.sh` GREEN and coverage ≥98.5% per module. Do not stop at "campaign complete"; a session with no code/test change is no progress. **Do not reply with a handoff-only update.**