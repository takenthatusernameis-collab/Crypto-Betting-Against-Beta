# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T11:33:09Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** 362f1f2 (origin/main synced; `git status --short` clean except 3 new untracked campaign-2 test files below)
**data_loader blob:** e945fde (UNCHANGED - GATE CLOSED)
**Status:** Environment blocker REMOVED — `numpy`/`pandas`/`scipy`/`pytest` installed and gates verified in this runtime. **Do not stop at planning; ship heavy engineering output.**

**MISSION (repo priority — Crypto-Betting-Against-Beta):** continue the **BAB Package Coverage Campaign**: reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing the `data_loader`/`campaign_d` baselines. `data_loader.py` miss-floor work is GATE-CLOSED (lines `322,326` live/guarded — do not alter; `data_sources.py` 100% CLOSED). The `beta.py` residual 26 misses are provably unreachable/dead code — CLOSED WITHOUT EDITS, no test/probe churn solely to cover them. Future agents must produce heavy engineering output (tests/fixes/evidence), not status narration; a planning-only exit is inefficient and unacceptable once deps are available.

**Current state (HEAD 362f1f2, all gates verified this session):**
- Full BAB suite (excl. controller): `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → **4445 passed, 35 skipped, `rc=0`** (baseline 4384/35; delta +61 = the three new campaign-2 test files below).
- Campaign scope: `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, `rc=0`** (baseline preserved).
- Coverage deltas this session: `data.py` 0 miss/**100%** (new); `costs.py` **15 miss/88%** (new); `metrics.py` **9 miss/93%** (new); `backtest.py` 0 miss/100%; `regime.py` 0 miss/100%; `beta.py` 26 miss/92% (26 remaining = unreachable dead code, §Residual, closed).
- New artifacts: `tests/test_bab_data_coverage_campaign2.py`, `tests/test_bab_costs_coverage_campaign2.py`, `tests/test_bab_metrics_coverage_campaign2.py` (61 tests, all pass). `py_compile` OK on all touched. Prior verified slices (historical): `cli.py` 2/99%, `strategy.py` 7/98%, `signals.py` 19/128/85%, `portfolio.py` 44/244/82%.

**Residual uncovered lines — `beta.py` (26 miss / 92%; dead code — CLOSED WITHOUT EDITS):**
101-102 alignment `except`; 124 `len(y)==0`; 145-146 `lstsq` `LinAlgError`; 149-150 `BABDataError` re-raise; 162 `a is None`; 169-170 `np.array().ravel()`; 188 `len(a_m)==0`; 212-218 `lstsq`/`TypeError`; 356-359 `_finalize_betas` 1-D branch; 429-433 inner `except`/`raise`. **Requirement:** no test/probe churn solely to cover these lines; no production edits solely for coverage.

**IMMEDIATE ACTIONS (execute in order):**

1. **Step 0 — baseline (mandatory, every session):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; `python -m pytest -q --ignore=tests/test_controller_progress_accounting.py` → expect 4445 passed, 35 skipped, `rc=0` (count grows only with added tests; any red must be fixed before new work); `python -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883/5, `rc=0`**.

2. **Next coverage slices — create narrowest targeted test files (`tmp_path`/controlled DataFrames; scoped monkeypatches only for defensive branches unreachable with valid public inputs):**
   - `tests/test_bab_signals_coverage_campaign3.py` — `signals.py` residual misses: non-numeric dtype fallback path, quantile clamp branches (`lq<=0`,`>=1`,`sq` overlaps), all-finite fast path, `argsort` exception fallback, single-asset/flat rows.
   - `tests/test_bab_portfolio_coverage_campaign3.py` — `portfolio.py` residual misses: `_clean_signal_value` string/None/NaN branches, kwargs alias routing (`max_total_turnover`, `max_pos_size`, etc.), `enforce_risk_checks` gross/net/max-single raise paths, `max_position_size`/`max_turnover` validation, `enforce_beta_neutrality` no-finite-beta/`correction=False`/`s2_centered<1e-18`/`target` branches.
   - Then `strategy.py`, `quality.py`, `attribution.py`, `shorting.py`, `sizing.py`, `cli.py`, `report` paths.

3. **Close `beta.py`:** record the 26 dead-code misses as campaign-complete (evidence = line-by-line reason above); move on — do not chase unreachable lines.

4. **Non-regression gates (all required):** full BAB suite green; `campaign_d` green (883/5); touched-module tests green. Fix failures caused by new tests; fix real bugs minimally with evidence + regression tests.

5. **Handoff update (durable, single file):** refresh timestamp/SHA/blob, exact Step-0 + final commands/counts, modules touched, before/after coverage deltas, and the next concrete highest-value slice.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits or commits; do not commit/push unless explicitly requested.

**Bottlenecks — RESOLVED (do not reintroduce as excuses):**
- **ENVIRONMENT BLOCKER** — REMOVED: deps installed; all gates verified. Future session must run in an environment with project deps installed (`python3 -m pytest --version` and `python3 -c "import numpy,pandas,scipy"` must succeed).
- scratch/probe clutter (never edit/commit `debug_beta*`/`probe*`/`ast_probe.py`); controller workflow-sync test (always ignore `tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`); coverage DB instability (`rm -f .coverage .coverage.*` before canonical runs); parquet/hdf5 engines (monkeypatch read APIs/call sites).

**ACTIVE:** none.

**Measurable outcome (required every session):** materially improved coverage/tests on the next BAB module slice with all gates green and before/after evidence, plus a refreshed HANDOFF naming the following slice — or a concrete evidence-backed blocker with exact reproduction and unblocked next action. This session reports gates green: `data.py` 100%, `costs.py` 88%, `metrics.py` 93%, `backtest.py` 100%, `regime.py` 100%, `beta.py` 92% dead-code closed, full suite 4445/35 `rc=0`, `campaign_d` 883/5 `rc=0`. Next slice = **`signals.py` / `portfolio.py` residuals (campaign3)**, then `strategy.py`/`quality.py`/`attribution.py`/`shorting.py`/`sizing.py`/`cli.py`/`report`.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T11:33:09Z @ `362f1f2`, data_loader blob `e945fde` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
