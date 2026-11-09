# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T11:34:26Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** 32b2b39 (origin/main synced at 362f1f2 lineage context; local checkpoint ahead may exist — verify with `git log --oneline -2`/`git status`). Do not commit/push unless explicitly requested.
**data_loader blob:** e945fde (UNCHANGED — GATE CLOSED)
**Status:** Environment deps available (`numpy/pandas/scipy/pytest` import OK). **Do not stop at planning; ship heavy engineering output (tests/fixes/evidence).**

**MISSION (repo priority):** continue the **BAB Package Coverage Campaign** — reduce real uncovered paths in `strategies/betting_against_beta/` with production-realistic tests/fixes, without regressing `data_loader`/`campaign_d` baselines. `data_loader.py` miss-floor work is GATE-CLOSED (lines `322,326` guarded — do not alter; `data_sources.py` 100% closed). `beta.py` residual 26 misses are provably unreachable/dead code — **CLOSED WITHOUT EDITS** (no churn). A planning-only exit is unacceptable when deps are available.

**Verified gates (this session, 2026-11-09T11:34:26Z @ 32b2b39, rc=0):**
- `python3 -c "import numpy,pandas,scipy,pytest; print('deps ok')"` → `deps ok`
- `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3592 deselected, rc=0** (baseline preserved)
- `python3 -m pytest -q tests/test_bab_costs_coverage_campaign2.py tests/test_bab_data_coverage_campaign2.py tests/test_bab_metrics_coverage_campaign2.py` → **61 passed, rc=0**
- Collection (excl. controller): **4480 tests collected**. Full-suite `pytest -q --ignore=tests/test_controller_progress_accounting.py` **timed out at 120s in this runtime** (not a red signal observed); next session MUST run full suite to green in a capable environment before claiming global green: record exact count/rc. Prior canonical baseline (362f1f2, HANDOFF history): **4445 passed, 35 skipped, rc=0**.

**Coverage baseline anchors (campaign2, historical verified):** `data.py` 100%, `costs.py` 88%, `metrics.py` 93%, `backtest.py` 100%, `regime.py` 100%, `beta.py` 92% (26 dead-code misses, closed). `cli.py` 99% (2 miss), `strategy.py` 98% (7), `signals.py` ~85% (19/128 miss reported historically), `portfolio.py` ~82% (44/244). Re-measure touched modules with `rm -f .coverage .coverage.*` before each canonical coverage run; avoid `pytest-cov` double-import collection issues seen here — prefer `coverage run -m pytest <target tests>` / `coverage report -m` for module snapshots.

**IMMEDIATE ACTIONS (execute in order — heavy working required):**

1. **Step 0 (mandatory):** `export PYTHONPATH=$PWD`; `python3 -c "import numpy,pandas,scipy,pytest"`; `rm -f .coverage .coverage.*`; `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → expect **883/5 rc=0**. Run full BAB suite excl controller to completion; if green record exact count/rc; if red, fix regressions before new work.
2. **campaign3 — `signals.py` residuals** (`tests/test_bab_signals_coverage_campaign3.py`, narrow/production-realistic, `tmp_path`/controlled DataFrames; scoped monkeypatch only for defensive branches): exercise non-numeric dtype coercion/fallback, quantile clamp/overlap edge cases (`lq<=0`,`>=1`,`sq` variants), all-finite fast path, `argsort`/exception fallback paths, single-asset & flat/no-finite rows, final finiteness guard. Capture before/after `coverage report -m` for `signals.py`.
3. **campaign3 — `portfolio.py` residuals** (`tests/test_bab_portfolio_coverage_campaign3.py`): `_clean_signal_value` (str/None/NaN/bad types), kwargs alias routing (`max_total_turnover*`, `max_pos_size`/position aliases), `enforce_risk_checks`/gross/net/max-single raise paths, `max_position_size`/`max_turnover` validation (incl. prev-weights/turnover breach), `enforce_beta_neutrality` branches (no-finite-beta, `correction=False`, `s2_centered<1e-18`, target handling). Before/after coverage.
4. **Then** `strategy.py` → `quality.py` → `attribution.py` → `shorting.py` → `sizing.py` → `cli.py` → `report` paths (one module slice per commit-worthy unit of evidence; keep diffs narrow).
5. **Non-regression gates (all required):** full BAB suite green; `campaign_d` 883/5 green; every touched module’s targeted tests green. Fix real bugs minimally with evidence + regression tests.
6. **Handoff refresh (durable, single file):** timestamp/SHA/blob, exact commands+counts+rc, modules touched, before/after coverage deltas, and the next concrete highest-value slice. Keep this section binding.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks to keep removed:** deps must be installed (fail fast otherwise); ignore `tests/test_controller_progress_accounting.py` & never touch workflows; `rm -f .coverage .coverage.*` before canonical runs; use scoped monkeypatches for defensive/unreachable-via-public-API branches; parquet/hdf5 engines via monkeypatch read APIs/call sites.

**ACTIVE:** `signals.py`/`portfolio.py` campaign3 (next heavy slice). **beta.py 26 dead-code misses remain CLOSED — no churn.**

**Measurable outcome (required):** materially improved coverage/tests on `signals.py` and/or `portfolio.py` with before/after evidence and all gates green, plus refreshed HANDOFF naming the following slice.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T11:34:26Z @ `32b2b39`, data_loader blob `e945fde` verified). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
