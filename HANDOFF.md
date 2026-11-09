# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T16:29:29Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (at session start):** `6d47075` (`chore(kilo): checkpoint agent session`, local main). Working tree: `HANDOFF.md` modified + new untracked `tests/test_bab_real_data_cli_repro.py` (this session, slice d). Do not commit/push unless explicitly requested.
**Baseline/gates (verified this session @ `6d47075`, deps installed `numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`, `.coverage*` cleared before canonical runs):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`
- `python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3696 deselected, 53 warnings, rc=0** (pre- and post-change; preserved).
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1813 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 136.13s** (FULL RUN COMPLETED this session; new verified floor **1813/5**, up +8 from 1805/5 due to `tests/test_bab_real_data_cli_repro.py`; no regression).

**campaign10 — COMPLETED (this session):**
- **Slice (d) done:** `tests/test_bab_real_data_cli_repro.py` added (8 tests, rc=0) — real-data CLI/reporting reproducibility on committed price fixtures (`tests/fixtures/real_market_prices.csv`, `real_market_prices_expanded.csv`), no external data.
  - `load_prices(fixture, benchmark="BTC")` → `BABStrategy.run(returns_df=...)` finite + deterministic cumulative across runs (both fixtures).
  - CLI `--data <fixture> --from-prices --benchmark BTC --output /tmp/out.json` → rc=0, schema-stable JSON (`final_cumulative`, `periods`, `benchmark`, `universe` present/finite); repeated `--output` byte-for-byte identical.
  - `--dry-run --data <fixture> --from-prices --benchmark BTC` → rc=0.
- Combined real-data repro: `tests/test_bab_real_data_cli_repro.py tests/test_bab_real_data_repro.py` → **13 passed, rc=0**.
- No production code changes; no bug found requiring fix.

**MISSION (repo priority):** Execute **campaign11 — BAB robustness & reporting hardening (post-repro)**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates:** deps import; `campaign_d` 883/5; full excl ≥1813/5. Fix regressions before new work.
2. **Slice (a) — CLI/report output robustness on committed fixtures:** extend `tests/test_bab_real_data_cli_repro.py` (or add `tests/test_bab_cli_reporting_robustness.py`) with: `--output` to a nested/overwritten path behaves deterministically; JSON schema keys/types stable across both price fixtures AND `returns.json` (parametrize all 3); `--synthetic` + `--output` produces schema-stable JSON with finite cumulative and byte-deterministic repeat; `--dry-run --synthetic` rc=0. No external data; record counts+rc.
3. **Slice (b) — strategy/backtest numeric invariants on real fixtures:** add targeted tests asserting on `real_market_prices*.csv` path: `result.backtest` index monotonic/datetime-like, `cumulative` starts finite, no NaN/Inf in `final_cumulative`/period metrics, portfolio weights sum behavior consistent with dollar-neutral config (inspect `result.weights`/`result.signals` as exposed) — evidence-based; do not invent APIs. If a real invariant bug is found, fix minimally with regression test.
4. **Slice (c) — docs/README contract check (test-only):** add a small test that `README.md` CLI flags mentioned (`--data --from-prices --benchmark --dry-run --output --synthetic --version`) are accepted by `strategies.betting_against_beta.cli.main`/argparse (parse-only / `--dry-run`/`--version` smoke) — keeps docs and CLI in sync. No production edits unless a real mismatch/bug is proven.
5. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
6. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl data_loader/controller ≥1813/5 (or updated verified count with explanation); all touched BAB tests green.
7. **No** `.github/workflows/*` edits, no gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses), no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits, no weakening `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (execute in order):**
0. Step 0 gates (deps, campaign_d, full excl floor 1813/5). Fix regressions before new work.
1. Execute campaign11 slice (a); run it + campaign_d + full excl; record before/after counts+rc.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**). BAB package slice **4407 stmts, 898 miss, 80%**.

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**Bottlenecks removed/notes:** full excl run completes (~136s) — not a blocker. `rm -f .coverage .coverage.*` before canonical runs. `real_market_prices*.csv` produce meaningful cumulatives (0.384 / 0.652) unlike `returns.json` (1.0, flat-zero weights at window 90/8 rows) — assert finite/deterministic, not specific alpha. Repo has tracked untracked `probe*`/`debug*`/`ast_probe.py` at root — do not edit/commit.

**ACTIVE:** campaign11 next. campaign10 complete (slice d: `tests/test_bab_real_data_cli_repro.py` 8 passed; excl floor 1813/5). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T16:29:29Z @ `6d47075`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
