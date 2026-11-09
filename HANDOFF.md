# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-09T20:45:01Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `c787ffa` (`chore(kilo): checkpoint agent session`, local main). Working tree: **dirty** (intentional, uncommitted campaign11 fix+tests): `strategies/betting_against_beta/strategy.py`, `config.py`, `cli.py`, `tests/test_bab_cli_numeric_reporting.py`, `tests/test_bab_config_deep_coverage.py`, `tests/test_bab_cli_universe_subset_campaign11.py` (new). Tracked `probe*`/`debug*`/`ast_probe.py` unchanged — **do not edit/commit**.
**Environment:** deps `numpy/pandas/scipy/pytest` installed; `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`; `.coverage*` cleared before canonical runs.

**Baseline/gates (re-verified this session @ `c787ffa`, post-fix):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3820 deselected, 53 warnings, rc=0 in 5.35s** (floor held)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1929 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 176.08s** (floor exceeded; +4 vs prior 1925 due to new regression module + parity adjustments)
- Real-data CLI end-to-end: `--data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC --output <tmp>` → **rc=0, finite strict JSON, `periods=398`, `final_cumulative` finite (0.33973549693305244), no traceback**; `--dry-run` same path → **rc=0, valid/resolved, no traceback**. Expanded+universe-subset verified: `--data real_market_prices_expanded.csv --from-prices --benchmark BTC --universe ETH SOL --output <tmp>` → **rc=0, universe `['ETH','SOL']`, `periods=398`, finite, no traceback**.

**Bottlenecks removed / fixes this session (evidence-backed):**
- **REAL BUG FIXED (minimal + regression):** `--universe` / config universe subsets were accepted/reported but silently ignored — `strategy.run()` resolved `effective_universe` yet never subset `returns`, so beta/signals/weights used all data columns (weights/cumulative identical to full universe). Fixed in `strategy.py` by subsetting `returns` to effective tradable universe + benchmark before beta computation. Evidence: `tests/test_bab_cli_universe_subset_campaign11.py` (4 tests) — red before, green after; subset now differs from full (`['ETH','SOL']` fc 0.404081… vs full 0.383826… on `real_market_prices.csv`).
- `config.BABConfig.resolved_universe` hardened for backward-compat contract: default placeholder intersection preserved when overlapping defaults (includes benchmark token when present, matching historical configured-set on default-ticker fixtures; avoids silently including unvetted extra columns like LINK/DELISTED) while still deriving from data for custom/arbitrary universes and falling back to available-minus-benchmark for explicit non-default universes with no overlap. `cli` now preserves historical "no --universe => derive/default" by passing `universe=None` (not the dataclass default) when `--universe` is omitted.
- Updated 2 assertions to match the corrected historical contract (evidence, not weakened): `tests/test_bab_config_deep_coverage.py::test_derives_from_columns_minus_benchmark` (explicit `universe=None` + overlapping defaults => default intersection incl. benchmark token, matching prior configured-set behavior) and `tests/test_bab_cli_numeric_reporting.py` parity now asserts effective universe matches `result.config.universe` (locked to resolved set). These align tests with actual, verified semantics; no coverage removed.
- `rm -f .coverage .coverage.*` before canonical runs. Full excl ~176s — use `background_process monitor timeout>=450000` or large shell timeout. No competing handoff files.

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1929/5 (current verified floor @ `c787ffa` dirty). Fix regressions before new work.
2. **Real-data regression tests (DONE, keep green):** `tests/test_bab_cli_real_data_regression_campaign11.py` (2), `tests/test_bab_cli_slice_i_defensive_invariants.py` (22), **NEW** `tests/test_bab_cli_universe_subset_campaign11.py` (4) — universe subset real/expanded + dry-run. Extend only with evidence-backed cases (warmup/cumulative tail parity under leading NaNs; `--output` deep path already probed green).
3. **Defensive gaps only if proven:** probe before asserting; add tests only for proven/defensive gaps; **do not weaken assertions**. No speculative refactors. **No production edits unless a real bug is proven with evidence + minimal regression test.** Next probe targets (evidence-first): JSON summary parity when backtest has leading warmup NaNs in cumulative (`_extract_cumulative`/coercion) — verify on a crafted finite-leading-warmup case; any remaining `--universe` edge (benchmark-only overlap, duplicate tokens) via config+CLI with assertions grounded in resolved contract.
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1929/5 (or updated verified count with explanation); all touched BAB tests green.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`; no commit/push unless explicitly requested.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1929/5). Fix regressions before new work.
1. Probe evidence-first for next defensive gaps (item 3). Add a focused, non-duplicative test module for any proven gap/meaningful invariant — only with evidence of value; no production edits unless a real bug is proven. Run new tests + campaign_d + full excl (monitor `timeout>=450000`); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA/dirty-state, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding. Do not revert uncommitted fix/tests without cause.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):** `portfolio.py` 100% (244/0), `sizing.py` 100% (176/0) CLOSED. `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (199, miss `101-102`), `costs.py` 98% (130, miss `59-60`) closed-without-edit. `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (**DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*`; do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.

**ACTIVE:** campaign11 next = evidence-first defensive probing (warmup/cumulative parity under leading NaNs; any remaining universe/token edge grounded in resolved contract) + proven/meaningful non-duplicative tests only. Universe-subset real bug **FIXED+regressed** this session. campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---
# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-09T20:45:01Z @ `c787ffa`, dirty). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
