# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T12:07:15Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `40c78f4` (local main, clean tree, origin/main sync). Do not commit/push unless explicitly requested.
**data_loader blob:** `596ee9eed` (VERIFIED at HEAD — GATE CLOSED; lines `322,326` guarded, do not alter; `data_sources.py` blob `e02069db` 100% closed).
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** continue the **BAB Package Coverage Campaign** — reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing `data_loader`/`campaign_d` baselines. `data_loader.py` miss-floor work is GATE-CLOSED (no churn). `beta.py` residual 214 misses (33% coverage) are provably unreachable/dead code — **CLOSED WITHOUT EDITS** (no churn). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T12:07:15Z @ `40c78f4`, deps ok):**
- `export PYTHONPATH=$PWD; python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, rc=0** (baseline preserved)
- Full BAB suite excl controller: **timed out at 120s in this runtime** (no red observed before timeout). Collection excl controller: **4548 tests collected**. **Next session MUST run full suite to green in a capable environment before claiming global green; record exact count/rc.** Prior canonical baseline (362f1f2 history): **4445 passed, 35 skipped, rc=0**.

**campaign3 delivered (tests-only; no production code changed):**
- `tests/test_bab_signals_coverage_campaign3.py` — **15 passed**. Targets: `betas` object-dtype float64 coercion, quantile TypeError/ValueError/non-finite fallbacks/clamping (`<0`, `>=1`), zero-quantile branches, all-insufficient-finite guard (151–154), non-numeric/mixed dtype coercion, defensive fallbacks via scoped monkeypatch (outer coercion failure → zero frame 136–142; argsort `kind="stable"` failure → fallback rank 159–161; copy-failure fallback).
- `tests/test_bab_portfolio_coverage_campaign3.py` — **35 passed**. Targets: `_clean_signal_value`, kwargs alias routing, `max_position_size`/`max_turnover` validation & breaches, risk-check raises, object/garbage signal coercion, outer-exception fallback (159–160), dollar-neutral renormalization, `enforce_beta_neutrality` (None/empty/no-common/no-finite, `correction=False`, already-neutral, degenerate centered variance, invalid tolerance/target).
- Combined targeted suites: signals all-campaign+edge → **82 passed, rc=0**; portfolio all-campaign+edge+extra → **101 passed, rc=0**.

**Coverage (measured with `coverage run -m pytest <targets>` + `coverage report -m`; `.coverage*` cleared before canonical runs):**
- `strategies/betting_against_beta/signals.py`: **97%** (128 stmts, 4 miss). Remaining: `37, 75, 139-140` (defensive/uncommon object-dtype + inner-fallback edge residue).
- `strategies/betting_against_beta/portfolio.py`: **94%** (244 stmts, 14 miss). Remaining: `39-40, 95-96, 118-119, 131-132, 152-157` (defensive type/exception guards + dollar-neutral renorm micro-branches under specific numeric states).
- `strategies/betting_against_beta/strategy.py`: **98%** (297 stmts, 7 miss). Remaining: `379-385` (defensive double finiteness-guard "extra pass"; hard to hit because first pass already cleans).
- `strategies/betting_against_beta/beta.py`: **33%** (320 stmts, 214 miss) — **CLOSED; dead/unreachable code per `docs/unreachable_proofs.md`**.
- `strategies/betting_against_beta/data_loader.py`: **29%** — **GATE CLOSED**.
- `strategies/betting_against_beta/cli.py`: **0%** — never tested; next after quality.py.
- `strategies/betting_against_beta/quality.py`: **7%** — next heavy slice after strategy.py.
- `strategies/betting_against_beta/attribution.py`: **97%** (1 miss at line 62).
- `strategies/betting_against_beta/backtest.py`: **51%** (52 miss).
- `strategies/betting_against_beta/config.py`: **71%** (57 miss).
- `strategies/betting_against_beta/costs.py`: **18%** (107 miss).
- `strategies/betting_against_beta/data_sources.py`: **42%** (39 miss).
- `strategies/betting_against_beta/metrics.py`: **69%** (42 miss).
- `strategies/betting_against_beta/regime.py`: **62%** (75 miss).
- `strategies/betting_against_beta/shorting.py`: **64%** (59 miss).
- `strategies/betting_against_beta/sizing.py`: **48%** (92 miss).

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Run full BAB suite excl controller to completion in a capable env; record exact count/rc. Fix regressions before new work.

2. **campaign4 — `strategy.py` residual defensive misses (NEXT HEAVY SINGLE SLICE):** Target lines `379-385` (double finiteness guard extra pass). Baseline **98%** (7 miss). Snapshot before/after with `coverage run -m pytest`. Create `tests/test_bab_strategy_coverage_campaign4.py`. Production-realistic scenarios: config resolution, run paths (synthetic + real `returns_df`), dry-run, error/edge handling, output structure (`BABResult` fields), `report()`/`tear_sheet()`/`report_to_json()`. Use scoped monkeypatches/controlled inputs to force the second finiteness pass; do not churn if branches are unreachable without pathological mocks — document if closed-without-edit.

3. **Non-regression gates (all required):** full BAB suite green (capable env); `campaign_d` 883/5 green; every touched module's targeted tests green. Fix real bugs minimally with evidence + regression tests.

4. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** deps installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; prefer `coverage run -m pytest` over `pytest-cov` in this env to avoid double-import/collection issues; full-suite 120s timeout in this runtime is a runtime bottleneck — do not claim global green until a capable env runs it to completion.

**ACTIVE:** `strategy.py` coverage campaign (next heavy slice — lines 379-385). **beta.py 214 dead-code misses remain CLOSED — no churn. signals/portfolio residuals are narrow defensive; pursue only if real.**

**Measurable outcome (required next session):** materially improved coverage/tests on `strategy.py` (before/after evidence: target ≥99% or documented closed-without-edit) and all gates green, plus refreshed HANDOFF naming the following slice (`quality.py` coverage campaign).

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T12:07:15Z @ `40c78f4`, data_loader blob `596ee9eed` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.