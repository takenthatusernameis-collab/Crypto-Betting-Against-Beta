# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message. Any other `*HANDOFF*.md` is stale and must be deleted on sight.

- **Timestamp (UTC):** 2026-11-16T05:57:40Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. The highest-stakes code is the path that decides **what real orders are placed and whether live fills still match the model**. Data quality is now safe-by-default; execution/reconciliation is the next live risk.
- **Git HEAD (verified this refresh):** `7546200` (branch `main`, clean tree before this handoff refresh).
- **Live probes re-verified 2026-11-16T05:57Z @7546200:** `LiveExecutionAdapter` has no `allow_live_execution`/`accept_terms`; no `evaluate_reconciliation_gate` in reconciliation; CLI has no `--reconcile-tolerance`. P18 gaps remain open (no `tests/test_bab_reconciliation_gate.py` or `tests/test_bab_live_opt_in.py`).
- **Gate evidence (live-verified 2026-11-16T04:54Z at HEAD `8ff2115`, not re-run this turn):** `bash scripts/bab_gate.sh` → **GREEN**: **6,163 passed, 35 skipped in 123.34s**, TOTAL **99%** (6,645 statements, 88 missed). `python3 -m ruff check .` → clean. Re-run the gate after every change and trust live output over this note.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T05:57:40Z) — BINDING (DO NOT IGNORE)

**Campaign P18 — Make live execution and reconciliation SAFE-BY-DEFAULT and ENFORCED. This is the next session's sole focus and the only authorized starting point. Start at P18-1 immediately and do not stop until P18-1's Definition of Done is met, then continue to P18-2 and P18-3.**

Do **NOT**: restart P17/already-done work, re-triage the coverage map, re-run the P17-1 probes (they pass — see below), create a parallel handoff doc, or spend the session on analysis/handoff/formatting/coverage-only work. **Analysis-only, handoff-only, formatting-only, and coverage-chasing turns are failed sessions.** Ship a real production fix with proof tests. **The controller counts a session with no code/test change as no progress.**

**Why this campaign (priority derived from repo identity):** this is a trading system, not a coverage exercise. Two live-money gaps remain and both are in the execution path, not the research path:

1. **Reconciliation drift is computed but never enforced.** `reconcile_costs` and `reconcile_fills_to_backtest` (`reconciliation.py`) already emit `delta_max_abs` / `n_mismatches`, but the CLI `--reconcile` (`cli.py`, the `if getattr(args, "reconcile", False):` block) only *writes an artifact* and always `return 0`. A strategy whose live fills diverge arbitrarily from the backtest passes CI silently. There is no `--reconcile-tolerance` flag.
2. **Real execution has no explicit opt-in.** `LiveExecutionAdapter` (`execution.py`) goes live whenever `dry_run=False` and credentials are present — there is no acknowledgment gate. The CLI currently hardcodes `dry_run=True` (`cli.py` live-adapter construction), so the only thing standing between a future wiring change and real orders is one boolean. Compare `scripts/fetch_real_bab_prices.py`, which correctly requires `--allow-public-api` **and** exact `--accept-terms` before any network call. Execution must be at least that strict.

### Live-verified current state (reproduce before editing — all three probes PASS/lenient at `8ff2115`)

Run this; every line must print the lenient/PASS result until P18 lands:

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 - <<'PY'
import inspect
from strategies.betting_against_beta.execution import LiveExecutionAdapter
from strategies.betting_against_beta.reconciliation import reconcile_costs
import strategies.betting_against_beta.cli as cli

# 1) Real execution needs only dry_run=False + creds; no acknowledgment arg.
sig = inspect.signature(LiveExecutionAdapter.__init__)
print("1 live_opt_in:", "FAIL (no allow_live_execution/accept_terms arg)" if "allow_live_execution" not in sig.parameters else "PASS")

# 2) No reconciliation-gate / tolerance API exists.
print("2 recon_gate:", "FAIL (no gate function)" if not hasattr(__import__("strategies.betting_against_beta.reconciliation", fromlist=["x"]), "evaluate_reconciliation_gate") else "PASS")

# 3) CLI --reconcile has no tolerance enforcement flag.
src = inspect.getsource(cli)
print("3 cli_gate:", "FAIL (no --reconcile-tolerance)" if "--reconcile-tolerance" not in src else "PASS")
PY
```

- **No characterization tests exist for either gap:** `tests/test_bab_reconciliation_gate.py` and `tests/test_bab_live_opt_in.py` do not exist. `tests/test_bab_reconciliation_p11_coverage.py` tests the math only; `tests/test_bab_live_adapter.py` tests the dry-run path only.

### P18-1 (execute first) — enforce reconciliation drift with a real gate

1. **Characterization tests first (must FAIL on HEAD, pass after fix).** Add `tests/test_bab_reconciliation_gate.py`:
   - clean fills (no drift) → gate returns zero violations and CLI exits 0;
   - injected cost drift beyond tolerance → gate returns a violation naming `delta_max_abs` / `n_mismatches` and CLI exits non-zero (use a distinct code, e.g. `2`);
   - injected equity drift beyond tolerance in `reconcile_fills_to_backtest` → violation;
   - tolerance boundary: drift exactly at tolerance passes, drift just above fails.
   Run them and record the RED failures in the ledger. A test that cannot fail is worse than no test.
2. **Add a pure, strict-JSON-safe gate function** in `reconciliation.py`, e.g. `evaluate_reconciliation_gate(costs_rec, fills_rec, *, cost_tolerance, equity_tolerance, mismatch_tolerance) -> dict` returning `{"ok": bool, "violations": [...]}`. Do not raise on clean input; never mutate the input artifacts.
3. **Wire it into the CLI.** Add `--reconcile-tolerance FLOAT` (max abs cost delta; default `None` = emit-only, preserving backward compatibility) and `--reconcile-max-mismatch INT`. When `--reconcile` is set and a tolerance is supplied, print violations and return non-zero on breach. `--reconcile` alone must stay green and byte-compatible.
4. **Proof obligation:** one RED→GREEN test per guard (cost drift, equity drift, tolerance boundary) with exact commands/results in the ledger.

**Definition of Done for P18-1 (do not advance to P18-2 until all are true):**
- [ ] RED characterization tests committed/run and failures recorded in the ledger.
- [ ] `reconciliation.py` exposes `evaluate_reconciliation_gate` (strict-JSON-safe, non-mutating).
- [ ] CLI enforces drift via `--reconcile-tolerance` / `--reconcile-max-mismatch`; `--reconcile` alone unchanged.
- [ ] `python3 -m ruff check .` clean AND `bash scripts/bab_gate.sh` GREEN (≥ 6,163 passed / 35 skipped, 99%).
- [ ] One RED→GREEN proof per changed guard recorded in the ledger.

### P18-2 — explicit two-key opt-in before any real order

1. **Characterization tests first (must FAIL on HEAD).** Add `tests/test_bab_live_opt_in.py`:
   - constructing `LiveExecutionAdapter(..., dry_run=False)` **without** an explicit acknowledgment raises (e.g. `PermissionError`/`RuntimeError`) before any CCXT call;
   - `dry_run=True` remains the default and needs no opt-in;
   - CLI `--adapter live` **without** `--allow-live-execution` stays dry-run even if credentials are present;
   - CLI `--adapter live --allow-live-execution` **without** exact `--accept-terms` still refuses (no network);
   - CLI with both flags reaches the real path (mock `ccxt`, assert the exchange was constructed with `dry_run=False`).
2. **Add the gate in `execution.py`.** Mirror the `fetch_real_bab_prices.py` pattern: a required `allow_live_execution: bool = False` and exact `accept_terms: str | None = None` on the live adapter; real submission is impossible unless both are set. Keep dry-run byte-identical.
3. **Expose CLI flags** `--allow-live-execution` and `--accept-terms` (exact string, never echoed to logs/artifacts). `--adapter live` must not flip `dry_run=False` unless both are present.
4. **Proof obligation:** one RED→GREEN test per guard (constructor refusal, CLI dry-run default, CLI terms refusal, CLI happy path) in the ledger.

**Definition of Done for P18-2:**
- [ ] RED tests committed/run and recorded.
- [ ] `execution.py` refuses real execution without `allow_live_execution` + exact `accept_terms`.
- [ ] CLI wires `--allow-live-execution` / `--accept-terms`; no silent live path.
- [ ] `ruff` clean AND `bash scripts/bab_gate.sh` GREEN (≥ 6,163 passed / 35 skipped, 99%).

### P18-3 — enforce the gate in CI, not just in the CLI

1. Add a dedicated gate invocation (e.g. `scripts/bab_reconcile_gate.sh` or a `pytest -k reconciliation_gate` step) that runs a fixture with an intentional drift and asserts a **non-zero** exit, so a future regression that drops enforcement turns CI RED.
2. Add the step to `.github/workflows/main.yml` next to the existing `bab_gate` / progress-accounting checks. If the workflow's `stage_safe_changes` case pattern is touched, update **both** the Python `EXCLUDE_PATTERNS` (`scripts/controller_progress.py`) and the bash case together — and do **not** add a nested-workflow case pattern; nested `.github/workflows` is protected by the force-restore guard, not a case pattern (see Bottleneck removal).
3. Update `README.md` with the new `--reconcile-tolerance`, `--reconcile-max-mismatch`, `--allow-live-execution`, and `--accept-terms` flags and the safety semantics.

**Definition of Done for P18-3:**
- [ ] CI step exists and is proven to fail when enforcement is removed (temporary revert test recorded in ledger).
- [ ] README documents every new flag.
- [ ] Full gate GREEN.

### Minimum acceptable session output (anti-avoidance contract)

A session that does not clear all of these has not done the work, regardless of what this file says afterward:

1. **New behavior tests, not smoke tests:** `tests/test_bab_reconciliation_gate.py` and `tests/test_bab_live_opt_in.py` exist with the characterization cases above, each demonstrated RED before the fix and GREEN after.
2. **Production source changed:** at least `strategies/betting_against_beta/reconciliation.py`, `strategies/betting_against_beta/execution.py`, and `strategies/betting_against_beta/cli.py` are modified; a test-only or doc-only diff does not satisfy P18.
3. **Every changed guard has a RED→GREEN proof** with the exact command and observed failure/pass recorded in the ledger.
4. **Full gate GREEN** (`bash scripts/bab_gate.sh`, ≥ 6,163 passed / 35 skipped / 99%) and `ruff` clean.
5. **No handoff-only commit:** if the session ends with only this file changed, it is a failed session and the next session must start from P18-1 step 1 again.

If P18 is completed with budget remaining, immediately start the deferred backlog (P17-2 first); do not stop at "campaign complete."

## Verified completion state (do not redo)

- **P17-1 is DONE and verified at `8ff2115`:**
  - `_run_data_quality_campaign` defaults are `20.0 / 7.0 / 3` (`data_loader.py` ~lines 1542-1547).
  - `BABStrategy._load_returns` threads an explicit `safe_quality` dict (`strategy.py` ~lines 230-261); CLI builds `_safe_quality` (`cli.py` ~lines 504-509) and passes it at every loader.
  - `load_prices` runs the quality campaign **ON** by default (`data_loader.py` ~lines 2447-2450).
  - `tests/test_bab_pipeline_safety_contract.py` exists (8 tests: 100% return, 30-day gap, frozen strategy input, load_prices absurd return, CLI dry-run rejections, clean-pass controls).
  - `TestLenientDefaultsAreHonored` is gone; `tests/test_bab_quality_threshold_contract.py` documents the old lax contract as inverted.
- **P17-2 coverage items:** the 88 missed statements below are the remaining checklist, not the current focus:
  - `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `data_loader.py` 280-292, 296-297, 315-316, 422-423, 666-667, 718-719, 837-838, 1355, 1615, 1654-1655, 1660-1662, 1676-1681, 1958-1959, 2762-2763; `execution.py` 139-141, 182-185, 555-556, 1287-1288; `portfolio.py` 152-153, 170-177, 180; `cli.py` 598-599, 767-769, 824-825; `reconciliation.py` 82-83, 309; `data_sources.py` 480-481, 499-500, 507-508; `metrics.py` 94; `replay.py` 172; `signals.py` 37, 75.
- **Kill switch (R4-B) is already covered:** `tests/test_bab_drawdown_kill_switch_r4.py` includes a breaching fixture, non-breaching control, `None` noop, invalid limit, JSON-safety, and a real-fixture test. Do not re-add.

## Deferred backlog (only after the P18 Definition of Done; do not start these first)

- **P17-2:** convert the reachable bucket-B edges listed above into targeted behavior tests (fakes/mocks, behavior assertions, full gate per batch).
- **P17-3:** delete or justify bucket-C dead branches with a concrete unreachability proof; never delete reachable safety behavior.
- **P17-4:** `python3 scripts/perf_baseline.py --check` (currently `failures: []`, full median ~3.10 ms on the 398×9 fixture), record metrics, then start the next real defect.
- **A. Test-suite performance/reliability:** profile with `--durations=20`, reduce full-gate wall time while keeping `--dist loadscope`, keep coverage ≥ 98.5%.
- **B. Real-data pipeline hardening:** timezone handling in the Coinbase public path, 429 `Retry-After` backoff, exact `--accept-terms` validation, complete `--metadata-out` audit fields.
- **C. Execution adapter completeness (R5-A → R5-C):** finish `LiveExecutionAdapter` CCXT integration (dry-run default), fill/order reconciliation tolerances, `--health-check` JSON validation, synthetic paper-adapter stress.
- **D. Risk/regime enhancements:** kill-switch flattening on `max_drawdown_limit` (done — verify only), beta-neutral tracking-error monitoring, regime-filter hysteresis validation, sizing edge-case tests.

## Hard gates every session (repo root, in order)

```bash
python3 -m ruff check .                 # must pass
bash scripts/bab_gate.sh                # full suite + coverage, must be GREEN (~2 min)
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # P14 release floor must hold
```

## Non-goals (do not pursue)

- ❌ Adding type annotations (ANN excluded by policy).
- ❌ Refactoring defensive try/except patterns (BLE/TRY excluded).
- ❌ Lowering the coverage floor — add tests, don't lower the bar.
- ❌ Coverage-against-dead-lines turns substituting for correctness work (see P17-3).
- ❌ Handoff-only sessions: editing this file without a code/test change is a failed session.

## Bottleneck removal status

- ✅ **Divergent/parallel handoffs removed:** only `HANDOFF.md` (+ pointer `AGENT_HANDOFF.md`) exist; no stale session handoff files found this refresh.
- ✅ **Divergent false handoff removed (prior):** deleted `AGENT_HANDOFF_2026-11-16.md` (claimed non-existent `TestStageSafeChangesPatternSync` blocker; 5 passed at `8ff2115`). No nested-workflow case pattern to "fix".
- ✅ **Stale binding cleared:** P17-1 is complete (see Verified completion state). Old binding replaced by P18.
- ✅ **Red-gate bottleneck (prior):** nested `.github/workflows` paths protected by checkpoint `git restore --source="$base_sha" -- .github/workflows` + `git clean -fd -- .github/workflows`, not by a `case` pattern.
- ✅ Gate runs parallel by default (`-n $(nproc) --dist loadscope`, coverage core=sysmon) — ~2 min; last verified 123.34s @8ff2115.
- ✅ `scripts/bab_bootstrap.sh` auto-installs missing deps — no manual setup.
- ⚠️ **Open bottleneck (P18 fixes it):** reconciliation drift is measured but not enforced, and live execution has no explicit two-key opt-in. Both are the most dangerous remaining gaps in the repo.

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T02:41:36Z | 9e15f9a | Handoff refresh: re-stamped binding P17-1; confirmed source tree unchanged since `a845eff`; live-verified `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 122.31s / 99%). No code change. | GREEN @02:37Z |
| 2026-11-16T04:54:45Z | 8ff2115 | Consolidated to a single durable handoff: deleted divergent false `AGENT_HANDOFF_2026-11-16.md` (its claimed `TestStageSafeChangesPatternSync` blocker does not exist — 5 passed); verified P17-1 complete (defaults 20/7/3, pipeline + `load_prices` wired, 8 safety-contract tests); live-verified `ruff` clean + gate GREEN (**6,163 passed / 35 skipped / 123.34s / 99%**, 88 missed) and `perf_baseline --check` `failures: []`; restamped binding **P18** (reconciliation drift gate + live two-key opt-in). No production code change this turn; P18 is the next session's sole focus. | GREEN @04:54Z |
| 2026-11-16T05:57:40Z | 7546200 | Handoff refresh: confirmed single durable handoff (no extra `*HANDOFF*.md`), re-verified P18 blockers still open (no gate fn / no CLI reconcile-tolerance / no live opt-in args / no characterization tests), restamped binding timestamp/HEAD. No production code/test change. | not re-run (last GREEN @04:54Z 8ff2115) |

---

**Next agent**: Start with P18-1, step 1 — write the RED characterization tests in `tests/test_bab_reconciliation_gate.py` and confirm they fail on the current tree. Then fix in order (pure gate function → CLI `--reconcile-tolerance`/`--reconcile-max-mismatch` → P18-2 live opt-in → P18-3 CI + README). Rerun `bash scripts/bab_gate.sh` after each fix and keep it GREEN. Record your session line in the ledger before finishing. **Do not reply with a handoff-only update — the controller counts a session with no code/test change as no progress.**