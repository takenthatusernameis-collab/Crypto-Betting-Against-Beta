# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T06:44:17Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. Highest-stakes paths: what real orders are placed and whether live fills still match the model.
- **Git HEAD (verified this refresh):** `5c1a6fb` (`main`, clean working tree).
- **Live probes re-verified 2026-11-16T06:44Z @5c1a6fb:** P18-1 and P18-2 are DONE in code/tests: `reconciliation.evaluate_reconciliation_gate` + CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (enforced, `--reconcile` alone emit-only) and `execution.LiveExecutionAdapter`/CLI two-key live opt-in (`--allow-live-execution` + exact `--accept-terms`, dry-run by default). Characterization suites present and green: `tests/test_bab_reconciliation_gate.py` (9) and `tests/test_bab_live_opt_in.py` (5) → **14 passed**. `python3 -m ruff check .` clean. Prior recorded full gate: **6,172 passed / 35 skipped / 99%** (≥98.5%) — rerun `bash scripts/bab_gate.sh` after every change and trust live output.
- **Open (P18-3, sole authorized focus):** no CI step proves reconciliation enforcement fails-closed on injected drift, and README does not document the new P18 flags/safety semantics. Do not declare P18 complete until P18-3 DoD is met.

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T06:44:17Z) — BINDING (DO NOT IGNORE)

**Campaign P18-3 — enforce the reconciliation/live-safety gate in CI and document it. Start immediately and finish with proof; this is the only authorized starting point.**

Do **NOT**: redo P18-1/P18-2, re-triage coverage, create parallel handoff docs, or do analysis/handoff/formatting/coverage-only work. **The controller counts a session with no code/test change as no progress. A handoff-only turn is a failed session.**

### P18-3 required work (execute in order)

1. **Add a reconciliation-enforcement gate that CI can run deterministically (no network).** Create `scripts/bab_reconcile_gate.sh` (or equivalent) that: runs a minimal fixture/backtest path with `--reconcile --reconcile-tolerance <small>` (and/or `--reconcile-max-mismatch`) against intentionally drifted fills/costs and **asserts non-zero exit** (exit 2) and a violation message; and runs a clean/no-drift case asserting exit 0. Keep it fast and self-contained (use synthetic data / temp files).
2. **Wire it into `.github/workflows/main.yml`.** Add a dedicated step next to existing controller/gate checks that runs the new reconcile gate script (or `pytest -k reconciliation_gate` plus an explicit CLI drift-fail invocation) so dropping enforcement turns CI RED. If you touch `stage_safe_changes` path handling, update **both** Python `EXCLUDE_PATTERNS` in `scripts/controller_progress.py` and the bash case in the workflow together. **Do not** add a nested-workflow case pattern; nested `.github/workflows` is protected by force-restore/clean, not case patterns.
3. **Document new safety flags in `README.md`.** In CLI/execution sections add: `--reconcile-tolerance`, `--reconcile-max-mismatch` (enforcement semantics, `--reconcile` alone emit-only/backward-compatible), and `--allow-live-execution` + `--accept-terms` (exact token required, dry-run default, never echoed/logged). Keep examples accurate.
4. **Proof obligation:** demonstrate the gate fails when enforcement is removed/bypassed (e.g. temporarily run with no tolerance or show non-zero on injected drift) and passes when intact; record exact commands and observed rc/output in the ledger.

### Definition of Done for P18-3 (and to close P18)
- [ ] Deterministic reconcile-gate script/check exists and is invoked by `.github/workflows/main.yml`.
- [ ] Proven fail-closed on intentional drift (non-zero) and pass on clean case; proof recorded in ledger.
- [ ] `README.md` documents `--reconcile-tolerance`, `--reconcile-max-mismatch`, `--allow-live-execution`, `--accept-terms` with correct safety semantics.
- [ ] `python3 -m ruff check .` clean AND `bash scripts/bab_gate.sh` GREEN (≥ 6,172 passed / 35 skipped, 99%).
- [ ] HANDOFF updated with honest ledger entry and next focus (deferred backlog) only after DoD met.

### Minimum acceptable session output (anti-avoidance contract)

1. Production/CI/script/docs changed as needed for P18-3 (not handoff-only).
2. Gate enforcement proven with real command evidence (fail-closed + pass cases).
3. `ruff` clean and full `bash scripts/bab_gate.sh` GREEN.
4. Ledger line appended with UTC, HEAD, concrete work, and gate result.

If P18-3 is completed with budget remaining, immediately start deferred backlog (P17-2 targeted behavior tests for reachable missed lines) — do not stop at "campaign complete."

## Verified completion state (do not redo)

- **P17-1 DONE:** safe data-quality defaults wired (20/7/3), `load_prices` runs quality campaign by default, `tests/test_bab_pipeline_safety_contract.py` (8) present; old lax contract inverted in `tests/test_bab_quality_threshold_contract.py`.
- **P18-1 DONE @7546200+/current:** `evaluate_reconciliation_gate` in `reconciliation.py`; CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` (exit 2 on breach, `--reconcile` alone unchanged); `tests/test_bab_reconciliation_gate.py` (9) RED→GREEN recorded.
- **P18-2 DONE (current):** `LiveExecutionAdapter` requires `allow_live_execution=True` + exact `accept_terms='I_UNDERSTAND_LIVE_TRADING'` for `dry_run=False` (refuses before CCXT); CLI `--allow-live-execution`/`--accept-terms` wired, dry-run default preserved; `tests/test_bab_live_opt_in.py` (5) present and green.
- **Kill switch (R4-B) covered:** `tests/test_bab_drawdown_kill_switch_r4.py` — verify only.
- **P17-2 coverage items (deferred):** reachable missed statements remain in `beta.py`, `data_loader.py`, `execution.py`, `portfolio.py`, `cli.py`, `reconciliation.py`, `data_sources.py`, `metrics.py`, `replay.py`, `signals.py` (see prior coverage notes); treat as backlog after P18-3, not current focus.

## Deferred backlog (only after P18-3 DoD)

- **P17-2:** targeted behavior tests for reachable missed branches (fakes/mocks, behavior assertions).
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
- ✅ Stale bindings cleared: P17 complete; P18-1/P18-2 complete; binding now **P18-3 only**.
- ✅ Gate parallel by default (`-n $(nproc) --dist loadscope`); `bab_bootstrap.sh` auto-installs deps.
- ✅ Nested `.github/workflows` protected by force-restore/clean (not case patterns).
- ⚠️ **Open bottleneck (P18-3):** reconciliation/live-safety enforcement is implemented in code but **not enforced in CI** and **not documented in README** — a future change can silently drop enforcement without CI signal. This is the priority fix.

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T02:41:36Z | 9e15f9a | Handoff refresh (no code). | GREEN @02:37Z |
| 2026-11-16T04:54:45Z | 8ff2115 | Consolidated handoff; verified P17-1/P18 binding set. | GREEN @04:54Z |
| 2026-11-16T05:57:40Z | 7546200 | Handoff refresh (no code). | not re-run |
| 2026-11-16T05:59:02Z | 7546200+ | P18-1 reconciliation drift gate + CLI tolerances + tests (9) RED→GREEN. | GREEN @05:59Z |
| 2026-11-16T06:44:17Z | 5c1a6fb | Handoff refresh: verified P18-1/P18-2 implemented and characterization suites green (14 passed), `ruff` clean; identified P18-3 (CI enforce + README docs) as sole remaining blocker and restamped binding. No production code change this turn. | not re-run (last GREEN recorded @05:59Z; rerun after P18-3 changes) |

---

**Next agent (binding):** Start at **P18-3 step 1** — add deterministic `scripts/bab_reconcile_gate.sh` proving drift is fail-closed (non-zero on intentional drift, zero on clean), then wire into `.github/workflows/main.yml`, then update `README.md` for `--reconcile-tolerance`, `--reconcile-max-mismatch`, `--allow-live-execution`, `--accept-terms`. Run `python3 -m ruff check .` and `bash scripts/bab_gate.sh` after changes and record proof in the ledger. **Do not reply with a handoff-only update.**
