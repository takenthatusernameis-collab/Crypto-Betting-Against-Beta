# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T16:47:14Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `7a5bdf2` (`chore(kilo): checkpoint agent session`, local main). Working tree: **clean** (no uncommitted changes). Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `7a5bdf2`, deps installed `numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`
- `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3704 deselected, 53 warnings, rc=0**
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1813 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 135.24s** (FULL RUN COMPLETED this session; verified floor **1813/5**). Use `background_process` action `monitor` with `timeout>=360000` if a shell timeout would interrupt capture.
- Combined real-data repro: `tests/test_bab_real_data_cli_repro.py tests/test_bab_real_data_repro.py` → **13 passed, rc=0**

**campaign10 — COMPLETED (verified present @ `7a5bdf2`):**
- **Slice (d) done:** `tests/test_bab_real_data_cli_repro.py` (8 tests, rc=0) — real-data CLI/reporting reproducibility on committed price fixtures (`tests/fixtures/real_market_prices.csv`, `real_market_prices_expanded.csv`), no external data.
  - `load_prices(fixture, benchmark="BTC")` → `BABStrategy.run(returns_df=...)` finite + deterministic cumulative across runs (both fixtures).
  - CLI `--data <fixture> --from-prices --benchmark BTC --output /tmp/out.json` → rc=0, schema-stable JSON (`final_cumulative`, `periods`, `benchmark`, `universe` present/finite); repeated `--output` byte-for-byte identical.
  - `--dry-run --data <fixture> --from-prices --benchmark BTC` → rc=0.
- No production code changes; no bug found requiring fix.

**MISSION (repo priority):** Execute **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1813/5. Fix regressions before new work.
2. **Slice (a) — CLI/report output robustness (all committed fixtures + synthetic):** add `tests/test_bab_cli_reporting_robustness.py` (preferred) or extend `tests/test_bab_real_data_cli_repro.py` with:
   - `--output` to a nested path (parent created by CLI) and to an overwritten existing file → deterministic, rc=0, finite schema-stable JSON.
   - JSON schema keys/types stable across **all 3 data sources** (parametrize): `tests/fixtures/returns.json`, `tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv` (use `--from-prices` for price fixtures), AND `--synthetic` + `--output` → finite cumulative, `periods>0`, byte-deterministic repeat.
   - `--dry-run --synthetic` rc=0; `--dry-run --output <path>` validates without writing (CLI currently validates output in dry-run — assert file NOT created).
   - No external data; record counts+rc.
3. **Slice (b) — strategy/backtest numeric invariants on real fixtures:** add targeted tests asserting on `real_market_prices*.csv` path: `result.backtest` index monotonic/datetime-like, `cumulative` starts finite (and first/last finite), no NaN/Inf in `final_cumulative`/period metrics, and dollar-neutral/weight behavior consistent with config (inspect only exposed attributes: `result.weights`/`result.signals`/`result.backtest` — evidence-based; do not invent APIs). If a real invariant bug is found, fix minimally with regression test.
4. **Slice (c) — README↔CLI contract (test-only, evidence-first):** add a small test that README-documented CLI flags (`--data --from-prices --benchmark --dry-run --output --synthetic --version --universe --beta-window --long-quantile --short-quantile --rebalance-freq --transaction-costs --slippage`) are accepted by argparse (parse-only / `--dry-run`/`--version` smoke) and that `--version` matches `strategies.betting_against_beta.cli.__version__`. No production edits unless a real mismatch/bug is proven (if proven, fix minimally with regression).
5. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
6. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1813/5 (or updated verified count with explanation); all touched BAB tests green.
7. **Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1813/5). Fix regressions before new work.
1. Execute campaign11 slice (a) end-to-end; run new tests + campaign_d + full excl (monitor if needed); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**). BAB package slice **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes (unblock next agent):**
- Full excl run completes (~135s) — not a blocker; capture with `background_process monitor timeout>=360000` if the shell tool times out.
- `rm -f .coverage .coverage.*` before canonical runs to avoid stale coverage artifacts.
- `real_market_prices*.csv` produce meaningful cumulatives (≈0.384 / 0.652) unlike `returns.json` (1.0, flat-zero weights at window 90/8 rows) — assert finite/deterministic, not specific alpha.
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit**.
- `--dry-run --output` validates path without writing (see `cli.py:231-241`); campaign11(a) must assert no file created.

**ACTIVE:** campaign11 next. campaign10 complete (slice d: `tests/test_bab_real_data_cli_repro.py` 8 passed; excl floor 1813/5). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T16:47:14Z @ `7a5bdf2`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
