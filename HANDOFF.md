# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-10T01:27:00Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `27574e0` (`chore(kilo): checkpoint agent session`, local main). Working tree: **dirty** — untracked `tests/test_bab_cli_universe_whitespace_dryrun_campaign11k.py` (5 regression tests, green) + this HANDOFF refresh; tracked `probe*`/`debug*`/`ast_probe.py` unchanged — **do not edit/commit** unless explicitly requested.
**Environment:** deps `numpy/pandas/scipy/pytest` installed; `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`.

**Step 0 gates (re-verified this session @ `27574e0`, before HANDOFF refresh):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3864 deselected, 53 warnings, rc=0** (floor held)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1973 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 247.92s** (floor held; +5 vs prior)
- `PYTHONPATH=$PWD python3 -m pytest -q tests/test_bab_cli_universe_whitespace_dryrun_campaign11k.py` → **5 passed, rc=0 in 6.34s** (untracked)
- Campaign11 suite spot-check: `tests/test_bab_cli_universe_{subset,edge,explicit_contract,campaign11}.py`, `tests/test_bab_cli_warmup_parity_campaign11.py`, `tests/test_bab_cli_real_data_regression_campaign11.py`, `tests/test_bab_cli_slice_i_defensive_invariants.py` → **61 passed** (rc=0)

**Bottlenecks removed / fixes (all closed, evidence-backed):**
- Duplicate-token `--universe`/config universe leak into reported `resolved_universe` → **FIXED+regressed**.
- Warmup/cumulative parity invariant → **LOCKED**.
- Universe edge contract (benchmark-only, partial overlap, duplicates) → **LOCKED**.
- Whitespace-padded universe token normalization (success path) + benchmark-duplicated-in-universe + `--dry-run` deep `--output` validates/no-write → **LOCKED (campaign11k, evidence-probed 2026-11-10, 5 new tests, no production edits)**.
- Universe-subset real bug, duplicate-token reporting bug, controller progress pattern sync → **FIXED+regressed** (prior sessions).
- `config.BABConfig.resolved_universe` backward-compat preserved. `data_loader` (98%/40 miss) and `beta.py` (92%) remain **GATE CLOSED**.
- **No active session locks/`.bab_active` found**; git clean of blockers. Bottlenecks: none blocking — proceed to heavy work.

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening** with **heavy, evidence-backed engineering**. campaign7–10 closed/verified. `beta.py` and `data_loader.py` gates **CLOSED** (no churn). A planning-only exit is unacceptable when deps are available. Prioritize by repo name (Betting Against Beta) — every change must serve BAB correctness/robustness.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy working; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1973/5 (current verified floor @ `27574e0`). Fix regressions before new work.
2. **Real-data/defensive regressions (keep green):** `test_bab_cli_real_data_regression_campaign11.py` (2), `test_bab_cli_slice_i_defensive_invariants.py` (22), `test_bab_cli_universe_subset_campaign11.py` (4), `test_bab_cli_universe_edge_campaign11.py` (6), `test_bab_cli_universe_explicit_contract_campaign11.py`, `test_bab_cli_warmup_parity_campaign11.py` (10), `test_bab_cli_universe_whitespace_dryrun_campaign11k.py` (5, untracked), `test_bab_config_deep_coverage.py`, `test_bab_cli_reporting_robustness.py`, `test_bab_cli_error_reporting.py`, `test_bab_cli_numeric_reporting.py`, `test_bab_backtest_contract_smoke.py`. Extend only with evidence-backed, non-duplicative cases.
3. **Heavy probe+prove campaign (do not stop at one test file):** systematically probe `strategies/betting_against_beta/cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py` integration edges for proven gaps: (a) `--output` summary parity vs in-process `BABStrategy` result on real fixture (`tests/fixtures/real_market_prices.csv`) for exercised flags (universe subset/explicit, benchmark-in-universe, `--from-prices`, `--transaction-costs`/`--slippage` if exercised) — compare `final_cumulative`, `periods`, `benchmark`, `universe`; add focused parity module only if divergence proven. (b) Non-finite propagation boundaries (inject NaN/Inf via constrained paths) — probe JSON/reporting/CLI for leaks; ensure `_json_safe`/`_json_default`/`_build_output_summary` remain strict. (c) Error-path cleanliness (no Traceback, stable `BABDataError`/`BABConfigError` messages, correct rc) for malformed paths, directories as `--data`/`--output`, whitespace-only `--universe`, bad quants/windows, missing benchmark handling, `--dry-run` combos. **Probe before asserting; add tests only for proven/defensive gaps; no production edits unless real bug proven with evidence + minimal regression test.**
4. **Coverage/dead-branch evidence (only where meaningful):** if probing reveals reachable-but-untested CLI/strategy branches not covered, add targeted tests. Do not chase `beta.py`/`data_loader` gate-closed misses.
5. **Bug fix rule:** if real bug found, fix minimally with evidence + regression test; re-run gates and record before/after.
6. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1973/5 (or updated verified count with explanation); all touched BAB tests green.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`; no commit/push unless explicitly requested.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl 1973/5). Fix regressions before new work.
1. **Heavy probe pass (evidence-first):** Run (a)-(c) probes against real fixture with concrete commands; capture rc/stdout/stderr/JSON. For any proven gap, write minimal regression test(s) in appropriate `tests/test_bab_cli_*campaign11*` module (or new non-duplicative module), fix production minimally if bug proven, re-test.
2. **Validate:** Run new/touched tests + `campaign_d` + full excl (timeout >=450000). Record counts/rc/modules touched/deltas.
3. **Handoff refresh:** Update this HANDOFF (timestamp/SHA/dirty-state, commands+counts+rc, modules touched, proven gaps/fixes, next slice). Keep §INITIAL TASK MESSAGE binding. Do not revert uncommitted tests without cause.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):** `portfolio.py` 100% (244/0) CLOSED. `sizing.py` 100% (176/0) CLOSED. `cli.py` 100% (320/0) CLOSED. `strategy.py` 100% (306/0) CLOSED. `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (218, miss `123-124`), `costs.py` 98% (130, miss `59-60`) closed-without-edit. `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (**DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.
**ACTIVE:** campaign11 next = **heavy evidence-first probe+prove campaign** (CLI/strategy/config/portfolio/metrics/backtest integration parity, non-finite/reporting boundaries, error-path cleanliness). campaign11k (5 tests, untracked) locked whitespace/dry-run invariants with no production edits. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED. **No planning-only exit — produce evidence or fixes for proven gaps.**

---

# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-10T01:27:00Z @ `27574e0`, dirty: +`tests/test_bab_cli_universe_whitespace_dryrun_campaign11k.py` untracked). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
