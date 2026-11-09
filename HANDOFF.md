# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T16:24:19Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD:** `0dcc613` (local main == `origin/main`, working tree clean; production code unchanged since `3bc2586`; only `HANDOFF.md` + new test file touched since `3bc2586`). Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `0dcc613`, deps installed via `python3 -m pip install --user numpy pandas scipy pytest hypothesis coverage`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3696 deselected, 53 warnings, rc=0 in 5.49s** (baseline preserved).
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1805 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 123.12s** (FULL RUN COMPLETED this session; new verified floor **1805/5**, up +5 from 1800/5 due to `tests/test_bab_real_data_repro.py` — record as new floor, no regression).
- BAB regression sanity samples green: `tests/test_bab_strategy_edge.py tests/test_bab_backtest_comprehensive.py tests/test_bab_backtest_coverage_campaign2.py tests/test_bab_portfolio_uncovered_branches.py tests/test_bab_portfolio_*.py` → **84 passed, rc=0** (use actual file globs; legacy names like `test_bab_backtest.py` do not exist as written).

**campaign9 — COMPLETED (script/tooling hardening):** `tests/test_scripts_campaign9.py` tracked (committed `c5d0c3c`). Script suite: `tests/test_bab_backtest_report.py tests/test_bab_report_strict_json.py tests/test_bab_cli_console_adversarial.py tests/test_bab_report_cli_edge_cases.py tests/test_bab_cli_report_hardening.py tests/test_scripts_campaign9.py` → **84 passed, rc=0**. Broader sanity incl. `test_bab_zero_silent_error.py` → **91 passed, rc=0**. No production code changes required/found in target scripts; no edits to `.github/workflows/*`, gate-closed modules, `data_loader` 322/326, or tracked `probe*`/`debug*`/`ast_probe.py`.

**MISSION (repo priority):** Execute **campaign10 — post-script BAB hardening / verification closure**. campaign7/8/9 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (40 miss / 98%, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign10 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Verification closure — COMPLETE this session:** full excl data_loader/controller baseline recorded as **1805/5 rc=0** (was 1800/5; +5 from `tests/test_bab_real_data_repro.py`). No regression. Do not re-run unless making non-script BAB changes.
2. **Slice (c) — EXECUTED this session:** `tests/test_bab_real_data_repro.py` added and green (**5 passed, rc=0**) covering the CLI end-to-end pipeline with committed fixture `tests/fixtures/returns.json` (no new external data): `--data ... --output /tmp/out.json` → rc=0, schema-stable JSON (`final_cumulative`, `periods`, `benchmark`, `universe` present and finite); `--dry-run ...` → rc=0 validates config + data; round-trip `load_returns("tests/fixtures/returns.json", benchmark="BTC")` → `BABStrategy.run(returns_df=...)` → cumulative finite and deterministic (1.0, 8 periods); repeated `--output` writes byte-for-byte identical. **Correction vs prior assumption:** `--data tests/fixtures/returns.json --from-prices` does NOT fail cleanly — returns are valid numerics so `load_prices` runs and exits 0 (7 periods); the test asserts rc=0, not a failure.
3. **Next slice (d) — binding initial task for the next session:** real-data CLI/reporting reproducibility on the committed price fixtures (`tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv`) — add regression tests in a new file `tests/test_bab_real_data_cli_repro.py` covering: `load_prices(fixture, benchmark="BTC")` → `BABStrategy.run(returns_df=...)` finite + deterministic cumulative across runs; CLI `--data <fixture> --from-prices --benchmark BTC --output /tmp/out.json` → rc=0, schema-stable JSON with `final_cumulative`/`periods`/`benchmark`/`universe` present and finite; repeated `--output` writes byte-for-byte identical; `--dry-run --data <fixture> --from-prices --benchmark BTC` → rc=0. Record before/after evidence (counts+rc). No new external data; no gate-closed churn.
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl data_loader/controller ≥1805/5 (or updated verified count with explanation); all BAB strategy/script tests touched; per-file BAB sets green as applicable.
6. **No** `.github/workflows/*` edits, no gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326), no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits, no weakening `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order):**
0. Step 0 gates: deps import ✓; `campaign_d` 883/5 ✓ rc=0; full excl **1805/5 ✓ rc=0** (complete — recorded as new floor). Fix regressions before new work.
1. Execute campaign10 slice (d): create `tests/test_bab_real_data_cli_repro.py` per item 3 above; run it + campaign_d + full excl; record before/after counts+rc.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — documented closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 1693 stmts / 98% gate closed (remaining miss `43-44, 234-244, 246-247, 268-269, 322, 326, 334-342, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664` — all mechanism-closed per `docs/unreachable_proofs.md`; structural-dead/inspect-gated, **DO NOT ALTER**). BAB package slice: **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** full BAB excl data_loader/controller (~2 min) completed this session — was the open incomplete run; not a blocker going forward. `rm -f .coverage .coverage.*` before canonical runs. campaign7 residual misses remain closed-without-edit. `tests/fixtures/returns.json` is small (8 rows × 3 assets incl. BTC) → rolling beta with window 90 yields flat zero weights (cumulative 1.0); slice (c) asserts finite/deterministic, not alpha. Slice (d) uses the larger price fixtures for a meaningful real-data path.

**ACTIVE:** campaign10 — verification closure complete (1805/5 floor recorded) + slice (c) done (`tests/test_bab_real_data_repro.py`, 5 passed). Next binding work: slice (d) real-data CLI/reporting reproducibility on committed price fixtures → `tests/test_bab_real_data_cli_repro.py`. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T16:24:19Z @ `0dcc613`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
