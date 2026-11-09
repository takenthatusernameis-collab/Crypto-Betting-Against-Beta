# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T19:55:23Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `7b4f89f` (`chore(kilo): checkpoint agent session`, local main). Working tree: **clean**.
**Environment:** deps `numpy/pandas/scipy/pytest` installed; `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`; `.coverage*` cleared before canonical runs.

**Baseline/gates (re-verified this session @ `7b4f89f`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3816 deselected, 53 warnings, rc=0 in 5.43s** (floor held)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1925 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 169.50s** (floor held)
- Real-data CLI end-to-end: `--data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>` → **rc=0, finite `allow_nan=False` JSON, `final_cumulative` finite scalar, `periods` int>0, no traceback**; `--dry-run` same path → **rc=0, valid/resolved, no traceback**.

**Bottlenecks removed (unblock next agent):**
- Consolidated two competing handoff files into this single durable `HANDOFF.md` (removed `AGENT_HANDOFF.md`; "No competing handoff files"). This file is canonical and binding.
- Full excl run completes (~170s) — use `background_process monitor timeout>=450000` or large shell timeout if needed.
- `rm -f .coverage .coverage.*` before canonical runs.
- Real-data e2e regression locked (subprocess CLI, `real_market_prices.csv`, from-prices, output JSON finite/strict, dry-run valid). Do not regress.
- Repo has tracked `probe*`/`debug*`/`ast_probe.py` at root — **do not edit/commit** (scratch; gates already green without them).

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1925/5 (current verified floor). Fix regressions before new work.
2. **Real-data regression test:** DONE (`tests/test_bab_cli_real_data_regression_campaign11.py`, 2 tests) + `tests/test_bab_cli_slice_i_defensive_invariants.py` (22, slice i). Keep green; extend only with evidence-backed cases (e.g. `real_market_prices_expanded.csv` parity, `--universe` subset on real data) — do not duplicate existing fixture coverage without added value.
3. **Defensive gaps only if proven:** probe before asserting; add tests only for proven/defensive gaps; **do not weaken assertions**. No speculative refactors. **No production edits unless a real bug is proven with evidence + minimal regression test.** Next probe targets (evidence-first): CLI `--universe` filtering on real fixtures with benchmark-in-universe edge cases; `--output` parent-creation on deep nested paths vs unusual path types; JSON summary parity when backtest has leading warmup NaNs in cumulative tail-adjacent positions (verify `_extract_cumulative`/coercion path).
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test. Do not weaken assertions to paper over bugs.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1925/5 (or updated verified count with explanation); all touched BAB tests green.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`; no commit/push unless explicitly requested.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1925/5). Fix regressions before new work.
1. Probe evidence-first for next defensive gaps (item 3 targets above). Add a focused, non-duplicative test module for any proven gap or meaningful invariant not yet locked (e.g. real-data `real_market_prices_expanded.csv` e2e + universe-subset edge) — only with evidence of value; no production edits unless a real bug is proven. Run new tests + campaign_d + full excl (monitor `timeout>=450000`); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):**
- `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) — CLOSED.
- `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) — closed-without-edit.
- Other BAB modules 100% CLOSED; `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (mechanism-closed per `docs/unreachable_proofs.md`; **DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**ACTIVE:** campaign11 next = evidence-first defensive probing (real expanded fixture e2e/universe-subset, warmup/cumulative edge parity) + add proven/meaningful non-duplicative tests only. Mandatory real-data regression test DONE. Slices (a)–(i) implemented/verified. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T19:55:23Z @ `7b4f89f`). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
