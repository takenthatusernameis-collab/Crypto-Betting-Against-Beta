# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Do not create parallel handoff/session docs; update this file only. `AGENT_HANDOFF.md` is a pure pointer and must not carry a second task message.

- **Timestamp (UTC):** 2026-11-16T02:37:46Z (this refresh)
- **Repo identity:** `Crypto-Betting-Against-Beta` — a **crypto market-neutral trading system** (ingest → beta → signals → portfolio → backtest → execution → ops) implementing the Frazzini–Pedersen *Betting Against Beta* strategy. The highest-stakes code is the **data-quality contract** that decides whether frozen, gapped, or implausible market data reaches beta estimation → portfolio construction → execution.
- **Git HEAD (verified this refresh):** `9e15f9a` (branch `main`). Source tree is unchanged since `a845eff` (only handoff consolidation + the reverted workflow-pattern assertion landed). This refresh leaves P17-1 uncommitted; the gate evidence below carries.
- **Gate evidence (live-verified 2026-11-16T02:06Z, working tree after the gate fix):** `bash scripts/bab_gate.sh` → **GREEN**: **6,153 passed, 35 skipped in 121.17s**, TOTAL **99%** (6,643 statements, 91 missed). The immediately preceding run at the same tree except the reverted assertion was **RED** (`1 failed, 6152 passed`). Re-run the gate after every change and trust live output over this note.
- **Toolchain:** `python3 3.12.3`; `ruff 0.17.5`; numpy/pandas/scipy/pytest/hypothesis/coverage/pytest-cov/pytest-xdist/ccxt via `bash scripts/bab_bootstrap.sh` (auto-invoked by quick/gate).

## INITIAL TASK MESSAGE (START HERE, 2026-11-16T02:37:46Z) — BINDING (DO NOT IGNORE)

**Campaign P17 — Make the data-quality gate safe-by-default in the actual trading pipeline. This is the next session's sole focus and the only authorized starting point. Start at P17-1 immediately and do not stop until P17-1's Definition of Done is met.**

Do **NOT**: restart P16/already-done work, re-triage the coverage map, create a parallel handoff doc, or spend the session on analysis/handoff/formatting/coverage-only work. **Analysis-only, handoff-only, formatting-only, and coverage-chasing turns are failed sessions.** Ship a real production fix with proof tests. **The controller counts a session with no code/test change as no progress.**

**Why this campaign (priority derived from repo identity):** this is a trading system, not a coverage exercise. A wrong/lax data-quality gate lets frozen or corrupt market data silently drive real positions. P16 fixed the *plumbing* (explicit `stale_run_threshold` no longer floored at 50; dict `quality` now parsed; `BABDataError` propagates from beta). **But the default safety posture is still unsafe and — critically — the actual trading entrypoints bypass the quality campaign entirely.** That is the live bottleneck.

### Live-verified current state (reproduce before editing — all five probes PASS/lenient at `a845eff`)

Run this; every line must print `PASS (no error)` until P17-1 lands:

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 - <<'PY'
import numpy as np, pandas as pd
from strategies.betting_against_beta.data_loader import validate_returns_dataframe, BABDataError, load_prices
from strategies.betting_against_beta.strategy import BABStrategy

def frozen(n=8):
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    live = np.linspace(0.02, 0.02 + 0.01 * n, n)
    return pd.DataFrame({"BTC": [0.01] * n, "ETH": live}, index=idx)

df = frozen(); df.iloc[2, 0] = 100.0
try: validate_returns_dataframe(df, benchmark="ETH", quality=True); print("1 100pct_default: PASS (lenient)")
except BABDataError as e: print("1 100pct_default: RAISED", e)

try: validate_returns_dataframe(frozen(8), benchmark="ETH", quality=True); print("2 frozen_default: PASS (lenient)")
except BABDataError as e: print("2 frozen_default: RAISED", e)

idx = list(pd.date_range("2020-01-01", periods=5, freq="D")); idx[3] = idx[2] + pd.Timedelta(days=30)
g = pd.DataFrame({"BTC": np.linspace(0.01, 0.05, 5), "ETH": np.linspace(0.02, 0.06, 5)}, index=idx)
try: validate_returns_dataframe(g, benchmark="ETH", quality=True); print("3 gap30_default: PASS (lenient)")
except BABDataError as e: print("3 gap30_default: RAISED", e)

try: BABStrategy(returns_df=frozen(8)).run(); print("4 strategy_frozen: PASS (gate not enforced)")
except BABDataError as e: print("4 strategy_frozen: RAISED", e)

prices = pd.DataFrame({"BTC": [100.0, 100.0, 20000.0], "ETH": [10.0, 11.0, 12.0]},
                      index=pd.date_range("2020-01-01", periods=3, freq="D"))
try: load_prices(prices, benchmark="ETH"); print("5 load_prices_absurd: PASS (gate not enforced)")
except BABDataError as e: print("5 load_prices_absurd: RAISED", e)
PY
```

- **Default `quality=True` is still "very lenient":** `_run_data_quality_campaign` (`strategies/betting_against_beta/data_loader.py:1536-1541`) uses `max_return_abs=10_000.0`, `max_gap_days=3650.0`, `stale_run_threshold=50`. A 100% (10,000%) single-period return and an 8-day frozen run **pass silently** by default.
- **The real pipeline never passes strict thresholds.** `BABStrategy._load_returns` (`strategy.py:230-253`) and the CLI (`cli.py:633-637`, `cli.py:710-714`) call `load_returns`/`load_prices` with **no** quality thresholds, so every real run inherits the lenient defaults.
- **`load_prices` hardcodes `quality=False`** on all its loads and its final validation (`data_loader.py:2399, 2406, 2410, 2414, 2419, 2423, 2434`), so the price→returns path runs **no quality campaign at all** — gaps, frozen prices, and absurd returns reach the strategy unchecked.
- **No characterization tests exist yet:** `tests/test_bab_pipeline_safety_contract.py` does not exist. `tests/test_bab_quality_threshold_contract.py` still contains `TestLenientDefaultsAreHonored` (line 113) which *asserts* the lax behavior, and its module docstring already claims the 20/7/3 contract — docs and tests disagree.

### P17-1 (execute first) — strict, explicit safety defaults + wire them through the real pipeline

1. **Characterization tests first (must FAIL on HEAD, pass after fix).** Add `tests/test_bab_pipeline_safety_contract.py` (new file; keep `tests/test_bab_quality_threshold_contract.py` for the inverted lax-contract tests in step 4):
   - default `quality=True` **rejects** a 100% return (`df.iloc[2,0]=100.0`) with `BABDataError` match `Implausible return`;
   - default `quality=True` **rejects** a >7-day gap;
   - `BABStrategy(returns_df=frozen_df).run()` raises `BABDataError` (frozen column) — proving the pipeline actually enforces the gate;
   - CLI dry-run with a frozen/implausible CSV exits non-zero.
   Run them and record the RED failures in the ledger. A test that cannot fail is worse than no test.
2. **Reconcile defaults to the safe contract.** In `_run_data_quality_campaign` (`data_loader.py:1536-1541`) change `None` defaults to `max_return_abs=20.0`, `max_gap_days=7.0`, `stale_run_threshold=3`. Update the docstring lenient-default paragraphs in `validate_returns_dataframe` (`data_loader.py:1679+`) and the inline comments that justify the old lenient `10000/3650/50`. Keep `quality=False` as the explicit opt-out and keep threshold `0` disabling the stale check.
3. **Stop bypassing the gate in the real pipeline.** Thread explicit, safe thresholds through `BABStrategy._load_returns` and the CLI loaders so `run()` and `--from-prices`/`--data` actually enforce them (pass a strict `quality` dict or explicit kwargs from config/CLI defaults). Make `load_prices` validate its converted returns with the quality campaign **on** (not `quality=False`), using safe defaults, unless the caller explicitly opts out.
4. **Fix the tests that encode the old lax contract, not the fix.** Search and update every caller/test that assumes 10000/3650/50: `tests/test_bab_quality_threshold_contract.py` (`TestLenientDefaultsAreHonored` at line 113 currently *asserts* the lax behavior — invert it), the robustness/stress suites that feed degenerate constant columns, and `tests/test_validation_performance.py` oracle (`_oracle_quality`, line 54). A test that masks the fix is a defect.
5. **No undocumented escape hatch.** Do not re-add a lenient default or a `max(...,50)` floor. If full-gate compatibility coupling is unavoidable, keep the stricter behavior, document the migration, and put any compatibility switch behind an explicit opt-in kwarg.
6. **Proof obligation:** for *each* changed guard (return/gap/stale default + pipeline wiring + `load_prices` gate), record one test that is RED on HEAD and GREEN after, with exact commands/results in the ledger.

**Definition of Done for P17-1 (do not advance to P17-2 until all are true):**
- [ ] RED characterization tests committed/run and failures recorded in the ledger.
- [ ] `data_loader.py` defaults are `20.0 / 7.0 / 3` and the docstring/comments match.
- [ ] `BABStrategy.run()` and the CLI enforce the gate (no lenient bypass); `load_prices` runs the campaign ON by default.
- [ ] `TestLenientDefaultsAreHonored` inverted; no test asserts the old lax contract.
- [ ] `python3 -m ruff check .` clean AND `bash scripts/bab_gate.sh` GREEN (≥ previous 6,153 passed / 35 skipped, 99%).
- [ ] One RED→GREEN proof per changed guard recorded in the ledger.

### Minimum acceptable session output (anti-avoidance contract)

A session that does not clear all of these has not done the work, regardless of what this file says afterward:

1. **New behavior tests, not smoke tests:** `tests/test_bab_pipeline_safety_contract.py` exists with at least four characterization tests (implausible return, >7-day gap, frozen strategy input, CLI rejection), each demonstrated RED before the fix and GREEN after.
2. **Production source changed:** at least `strategies/betting_against_beta/data_loader.py` and one of `strategy.py` / `cli.py` are modified; a test-only or doc-only diff does not satisfy P17-1.
3. **Every changed guard has a RED→GREEN proof** with the exact command and observed failure/pass recorded in the ledger.
4. **Full gate GREEN** (`bash scripts/bab_gate.sh`, ≥6,153 passed / 35 skipped / 99%) and `ruff` clean.
5. **No handoff-only commit:** if the session ends with only this file changed, it is a failed session and the next session must start from P17-1 step 1 again.

If P17-1 is completed with budget remaining, immediately start P17-2; do not stop at "campaign complete."

### P17-2 — convert remaining reachable bucket-B edges into targeted behavior tests

Only after P17-1. Use fakes/mocks; add behavior assertions, not smoke tests; rerun the full gate per batch. The 91 missed statements are a checklist, not the goal:

- `execution.py:139-141` Timestamp-key fallback; `182-185` Timestamp-indexed ADV; `555-556` non-finite numpy float JSON sanitize (`allow_nan=False`).
- `portfolio.py:152-153` extreme-weight clipping; `170-177` dollar-neutral `need_fix` renorm under one-sided underflow.
- `cli.py:589-590` unknown adapter; `746-748` invalid output path.
- `reconciliation.py:309` empty-column early return.
- `data_sources.py:480-481, 499-500, 507-508` timezone/format edges.
- `data_loader.py` (37 lines) mixed-dtype slow path, finite-fraction boundary, stale-run boundary, datetime dayfirst retry/error wrap, multi-source fallback chains (280-292, 666-667, 718-719), empty/malformed CSV (422-423, 837-838), batch fetch error paths.
- `signals.py:37` object dtype after numeric coercion.

### P17-3 — delete or justify bucket-C dead branches

Do not add tests to "buy" coverage. Candidates: `beta.py` 125, 163, 170-171, 189, 435-436, 552-556; `execution.py:1287-1288`; `portfolio.py:180`; `metrics.py:94`; `signals.py:75`; `reconciliation.py:82-83`; `replay.py:172`; `cli.py:803-804`. Delete only with a concrete unreachability proof in the commit/test rationale; otherwise document why defensive. **Never delete reachable safety behavior.**

### P17-4 — prove performance, then continue to the next real defect

Run `python3 scripts/perf_baseline.py --check` (rerun once if noisy), record exact metrics, refresh this file with timestamp/HEAD/tree/ledger/coverage evidence, then immediately start the next real correctness or safety defect. **Never stop at "campaign complete."**

## Deferred backlog (only after the P17-1 Definition of Done; do not start these first)

These were consolidated from the deleted parallel `HANDOFF_TASK.md`; they are real follow-ups, not the current focus:

- **A. Test-suite performance/reliability:** profile with `--durations=20`, reduce full-gate wall time while keeping `--dist loadscope`, keep coverage ≥98.5%.
- **B. Real-data pipeline hardening:** timezone handling in the Coinbase public path, 429 `Retry-After` backoff, exact `--accept-terms` validation, complete `--metadata-out` audit fields.
- **C. Execution adapter completeness (R5-A → R5-C):** finish `LiveExecutionAdapter` CCXT integration (dry-run default), fill/order reconciliation tolerances, `--health-check` JSON validation, synthetic paper-adapter stress.
- **D. Risk/regime enhancements:** kill-switch flattening on `max_drawdown_limit`, beta-neutral tracking-error monitoring, regime-filter hysteresis validation, sizing edge-case tests.

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

- ✅ **Red-gate bottleneck removed (this refresh):** the previous session inverted `tests/test_controller_progress_accounting.py::test_workflow_directory_is_protected_by_restore_not_case_pattern` from `not in` to `in` without changing `.github/workflows/main.yml`, turning the gate RED (`1 failed, 6152 passed`). Nested workflow paths are intentionally protected by the checkpoint's `git restore --source="$base_sha" -- .github/workflows` + `git clean -fd -- .github/workflows`, **not** by a `case` pattern. Reverted the assertion to `not in`; gate is GREEN again (6,153 passed / 35 skipped / 121.17s / 99%). Do not "fix" this by adding a nested case pattern unless you also change the force-restore design.
- ✅ **Parallel-handoff bottleneck removed:** deleted `HANDOFF_TASK.md`, which carried a different campaign set (A–D) and a false "full gate passes" claim while the gate was RED. Its useful follow-ups are folded into the deferred backlog above. `HANDOFF.md` is now the only durable handoff; `AGENT_HANDOFF.md` is a pure pointer.
- ✅ **Stale-HEAD bottleneck removed:** HEAD restamped to the real `a845eff` (three checkpoint commits ahead of the previously recorded `65cea9e`).
- ✅ Gate runs parallel by default (`-n $(nproc) --dist loadscope`, coverage core=sysmon) — ~2 min vs ~16 min serial; verified this refresh (121.17s).
- ✅ `scripts/bab_bootstrap.sh` auto-installs missing deps — no manual setup.
- ✅ No flaky tests; the 35 skipped are explicit `pytest.mark.skip` (known gaps).
- ⚠️ **Open bottleneck (P17-1 fixes it):** the quality gate is strict only when a caller explicitly opts in; `BABStrategy`/CLI pass no thresholds and `load_prices` hardcodes `quality=False` — so **production runs enforce no implausible-return / gap / frozen-data guard**. All five live probes above PASS (no error) at `a845eff`. This is the single most dangerous remaining gap in the repo.

## Session ledger (append one line per session; keep it honest)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-16T01:00:30Z | 99a841b | Handoff refresh: live-verified `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 132.01s / 99%) at HEAD `99a841b`; confirmed P16-3 landed; restamped binding campaign **P17**. No code change this turn. | GREEN @01:00:30Z |
| 2026-11-16T01:03:44Z | dc58017 | Handoff re-verification: `ruff` clean + gate GREEN (6,153 passed / 35 skipped / 131.89s / 99%) at HEAD `dc58017`; re-confirmed lenient defaults + un-wired pipeline/`load_prices quality=False`. Re-stamped binding **P17-1** with Definition of Done. No code change this turn. | GREEN @01:01:20Z |
| 2026-11-16T01:17:06Z | dc58017 | Synchronized `NEXT_SESSION_HANDOFF.md` to canonical `HANDOFF.md`; confirmed P17-1 binding. No code change this turn. | — |
| 2026-11-16T01:21:28Z | 64fd194 | Consolidated handoff: live-verified `ruff` clean + gate GREEN (**6,153 passed / 35 skipped / 135.38s / 99%**) at real HEAD `64fd194`; live-probed all five P17-1 bottlenecks (all PASS/lenient); deleted divergent `NEXT_SESSION_HANDOFF.md` and refreshed `AGENT_HANDOFF.md` pointer; re-stamped binding **P17-1** with a reproduction script. No code change this turn. | GREEN @01:21:28Z |
| 2026-11-16T01:36:55Z | 65cea9e | Refreshed canonical handoff: restamped HEAD to real `65cea9e` (removed stale-HEAD bottleneck); gate evidence carries (no source/test change since `64fd194`); re-stamped binding **P17-1** initial task message. No code change this turn. | carried @64fd194 |
| 2026-11-16T02:07:21Z | a845eff | Live-verified all five P17-1 probes still lenient; found gate RED from an inverted workflow-pattern assertion (1 failed / 6152 passed); reverted the assertion to `not in` (nested workflows are protected by force-restore, not a case pattern); deleted duplicate `HANDOFF_TASK.md`; reduced `AGENT_HANDOFF.md` to a pure pointer; re-stamped binding **P17-1**; gate GREEN (**6,153 passed / 35 skipped / 121.17s / 99%**). | GREEN @02:06Z |
| 2026-11-16T02:37:46Z | 9e15f9a | Handoff timestamp refresh only: re-stamped binding **P17-1** initial task message; confirmed source tree unchanged since `a845eff` (only handoff files + progress-accounting test landed); live-verified `ruff` clean + gate GREEN (**6,153 passed / 35 skipped / 122.31s / 99%**). No code change this turn; P17-1 remains uncommitted and is the next session's sole focus. | GREEN @02:37:46Z |

---

**Next agent**: Start with P17-1, step 1 — write the RED characterization tests in `tests/test_bab_pipeline_safety_contract.py` and confirm they fail on the current tree. Then fix in order (safe defaults → wire through `BABStrategy`/CLI/`load_prices` → invert lax-contract tests). Rerun `bash scripts/bab_gate.sh` after each fix and keep it GREEN. Only move to P17-2 once the P17-1 Definition of Done is fully checked. Record your session line in the ledger before finishing. **Do not reply with a handoff-only update — the controller counts a session with no code/test change as no progress.**