# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T10:33:28Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** 56a52be (origin/main synced context; `git status --short` clean aside from this session's new test files)
**data_loader blob:** 596ee9e (UNCHANGED - GATE CLOSED)
**Status:** Environment blocker REMOVED this session — `numpy`/`pandas`/`scipy`/`pytest`/`coverage` installed and every gate below verified in this runtime. **Do not stop at planning; ship heavy engineering output.**

**MISSION (repo priority — Crypto-Betting-Against-Beta):** continue the **BAB Package Coverage Campaign**: reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing the `data_loader`/`campaign_d` baselines. `data_loader.py` miss-floor work is GATE-CLOSED (B103–B192 exhausted; `data_sources.py` 100% CLOSED; lines `322,326` live/guarded — do not alter). The `beta.py` residual 26 misses are provably unreachable/dead code under the current implementation — documented as closed below, no semantic change solely for coverage per campaign rules. Future agents must produce heavy engineering output (tests/fixes/evidence), not status narration; a planning-only exit is inefficient and unacceptable once deps are available.

**Current state (HEAD 56a52be, all gates verified this session):**
- Full BAB suite (excl. controller): `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → **4384 passed, 35 skipped, `rc=0`** (baseline was 4367/35; delta = +17 new campaign2 tests).
- Campaign scope: `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3531 deselected, `rc=0`** (baseline preserved, unchanged).
- Coverage deltas this session: `backtest.py` 28 miss / 74% → **0 miss / 100%**; `regime.py` 11 miss / 94% → **0 miss / 100%**; `beta.py` 28 miss / 91% → **26 miss / 92%** (remaining 26 = unreachable dead code, §Residual).
- New artifacts: `tests/test_bab_backtest_coverage_campaign2.py` (incl. final `np.ones` fallback branch, lines 148-149), `tests/test_bab_beta_coverage_campaign2.py`, `tests/test_bab_regime_coverage_campaign2.py`. `py_compile` OK on all touched files. Prior verified slices (historical): `cli.py` 2/99%, `strategy.py` 7/98%, `signals.py` 19/128/85%, `portfolio.py` 44/244/82%.

**Residual uncovered lines — `beta.py` (26 miss / 92%; dead code — CLOSED WITHOUT EDITS):**
- 101-102: alignment `except` unreachable — `float` coercion at lines 78-79 throws first and exits at line 147-148.
- 124: `len(y) == 0` after masking — all-`False` mask returns at 118-119 first.
- 145-146: `np.linalg.lstsq` does not raise `LinAlgError` for singular systems.
- 149-150: `BABDataError` is raised at lines 74-75, before the `try`, so the re-raise never fires.
- 162: `a is None or b is None` — impossible after `np.asarray(..., dtype=float)`.
- 169-170: `np.array(a).ravel()` cannot raise once `a` is an ndarray.
- 188: `len(a_m) == 0` — impossible; `not np.any(mask)` returns at 179-180 first.
- 212-218: `lstsq`/`TypeError` excepts unreachable for the same reasons.
- 356-359: `_finalize_betas` 1-D branch — `calculate_rolling_beta` always passes a 2-D beta array (else branch at 360-365 runs).
- 429-433: inner `except`/`raise BABDataError` — outer `except` at 421 unreachable (fast path raises nothing catchable; `BABDataError` paths exit at 419-420 first).
**Requirement:** no test/probe churn solely to cover these lines; no production edits solely for coverage.

**IMMEDIATE ACTIONS (execute in order):**

1. **Step 0 — baseline (mandatory, every session):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → expect ~4384 passed, 35 skipped, `rc=0` (count grows only with added tests; any red must be fixed before new work); `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883/5, `rc=0`**.
2. **Next coverage slices:** target residual real misses across `strategies/betting_against_beta/` — `config.py`, `data.py`, `signals.py`, `portfolio.py`, `costs.py`, `metrics.py`, then `strategy.py`/`report` paths. Add narrowest targeted test files (`test_bab_<module>_coverage_campaign2.py`) using `tmp_path`/controlled DataFrames; scoped monkeypatches only for defensive branches unreachable with valid public inputs.
3. **Close `beta.py`:** record the 26 dead-code misses above as campaign-complete (evidence = line-by-line reason); move on — do not chase unreachable lines.
4. **Non-regression gates (all required):** full BAB suite green; `campaign_d` green (883/5); touched-module tests green. Fix failures caused by new tests; fix real bugs minimally with evidence + regression tests.
5. **Handoff update (durable, single file):** refresh timestamp/SHA/blob, exact Step-0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits or commits; do not commit/push unless explicitly requested.

**Bottlenecks — RESOLVED (do not reintroduce as excuses):**
- **ENVIRONMENT BLOCKER** (this session's `pytest`/`numpy`/`pandas`/`scipy` missing for `/usr/bin/python3`) — REMOVED: deps installed; all gates verified. Any future session must run in an environment with project deps installed (`python3 -m pytest --version` and `python3 -c "import numpy,pandas,scipy"` must succeed).
- scratch/probe clutter (never edit/commit `debug_beta*`/`probe*`/`ast_probe.py`); controller workflow-sync test (always ignore `tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`); coverage DB instability (`rm -f .coverage .coverage.*` before canonical runs); parquet/hdf5 engines (monkeypatch read APIs/call sites).

**ACTIVE:** none.

**Measurable outcome (required every session):** materially improved coverage/tests on the next BAB module slice with all gates green and before/after evidence, plus a refreshed HANDOFF naming the following slice — or a concrete evidence-backed blocker with exact reproduction and unblocked next action. This session reports the former: `backtest.py` 100%, `regime.py` 100%, `beta.py` 92% with dead-code misses closed, all gates green. Next slice = `config.py` / `data.py` / remaining `signals.py`/`portfolio.py` residual misses.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T10:33:28Z @ `56a52be`, data_loader blob `596ee9e` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
