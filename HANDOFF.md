# INITIAL TASK MESSAGE (leave this for next agent; highest priority)

**Timestamp:** 2026-11-10T01:04:13Z
**Repo:** Crypto-Betting-Against-Beta (priority: Betting Against Beta — repo-name priority binds every slice)
**HEAD (verified this session):** `4d26d57053987b24e2ba48f5acc2dfde6af99b5c` (`chore(kilo): checkpoint agent session`, local main). Working tree: **clean**. Not committed — commit only if explicitly requested. Tracked `probe*`/`debug*`/`ast_probe.py` unchanged — **do not edit/commit**.
**Environment:** deps `numpy/pandas/scipy/pytest` installed; `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`; `.coverage*` cleared before canonical runs.

**Step 0 gates (re-verified this session @ `4d26d57`, clean tree):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3859 deselected, 53 warnings, rc=0 in 5.86s** (floor held)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k "not data_loader and not controller"` → **1968 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0 in 241.61s** (floor held; exceeds verified floor of 1965/5)
- Full suite @ `4d26d57`: previously **4778 passed, 35 skipped, 2 failed** @ `d988d6c` (the 2 were `TestStageSafeChangesPatternSync`, pattern-sync regression); fix was committed in an intervening checkpoint. Re-run full suite only if a regression is suspected.

**Bottlenecks removed / fixes (all closed, evidence-backed):**
- Duplicate-token `--universe`/config universe leak into reported `resolved_universe` → **FIXED+regressed** (`config.py` `_dedupe_preserve_order` at every return path; `TestResolvedUniverse` 3 tests + `TestCliUniverseDuplicateTokensEdge`, red→green).
- Warmup/cumulative parity invariant → **LOCKED** (`_extract_cumulative` reads last row regardless of leading NaN warmup 0/1/3/5/10; `_coerce_finite_scalar` preserves finite tail; all-NaN → finite default 1.0; `test_bab_cli_warmup_parity_campaign11.py` 10 tests).
- Universe edge contract → **LOCKED** (benchmark-only → flat 1.0; partial overlap → absent dropped/overlap kept finite; duplicates → de-duplicated; `test_bab_cli_universe_edge_campaign11.py` 6 tests).
- `config.BABConfig.resolved_universe` backward-compat contract preserved (default-placeholder intersection; derive for custom universes; fallback available-minus-benchmark; CLI passes `universe=None` when `--universe` omitted).
- Controller progress pattern sync → **FIXED+regressed** (workflow `stage_safe_changes` bash case missing `*/.github/workflows/*` nested exclusion pattern present in Python `EXCLUDE_PATTERNS`; added; `TestStageSafeChangesPatternSync` now 4/4 pass).
- Real-data CLI end-to-end → **rc=0, finite strict JSON** (`--data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → `periods=398`, `final_cumulative` finite; `--dry-run` rc=0; universe subset `ETH SOL` → rc=0, `periods=398`).

**MISSION (repo priority):** Continue **campaign11 — BAB CLI/reporting + numeric robustness hardening**. campaign7–10 closed/verified. `beta.py` (92%, gate closed) and `data_loader.py` (98%/40 miss, gate closed) remain **GATE CLOSED** (no churn). A planning-only exit is unacceptable when deps are available.

**campaign11 — NEXT FOCUS CAMPAIGN (mandatory, heavy engineering; not avoidable):**
1. **Step 0 gates (must pass before any edit):** deps import; `campaign_d` 883/5; full excl ≥1965/5 (current verified floor @ `4d26d57`). Fix regressions before new work.
2. **Real-data regression tests (DONE, keep green):** `tests/test_bab_cli_real_data_regression_campaign11.py` (2), `tests/test_bab_cli_slice_i_defensive_invariants.py` (22), `tests/test_bab_cli_universe_subset_campaign11.py` (4), `tests/test_bab_cli_universe_edge_campaign11.py` (6), `tests/test_bab_cli_warmup_parity_campaign11.py` (10), `tests/test_bab_config_deep_coverage.py`. Extend only with evidence-backed cases; `--output` deep path already probed green.
3. **Defensive gaps only if proven:** probe before asserting; add tests only for proven/defensive gaps; **do not weaken assertions**. No speculative refactors. **No production edits unless a real bug is proven with evidence + minimal regression test.** Next probe targets (evidence-first): any remaining CLI/reporting edge not covered by slices g–k (e.g. `--universe` with empty/whitespace tokens; `--benchmark` equal to an asset token in a non-default universe). `--output` to deep/non-existent parent dir already probed green. All four HANDOFF item-3 targets (warmup parity, benchmark-only overlap, duplicate tokens, partial overlap) are **CLOSED** — re-probe only if a new mechanism is suspected.
4. **Bug fix rule:** if a real bug is found, fix minimally with evidence + regression test.
5. **Gates that must stay green:** `campaign_d` 883/5; full BAB excl `data_loader`/`controller` ≥1965/5 (or updated verified count with explanation); all touched BAB tests green.

**Prohibited:** `.github/workflows/*` edits (except the already-committed pattern sync fix); gate-closed churn (`beta.py` dead/unreachable, `data_loader` strict-4/322,326 + mechanism-closed misses — **DO NOT ALTER**); tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; weakening/deleting `batch148/149/172` or `campaign_d*`; no commit/push unless explicitly requested.

**IMMEDIATE ACTIONS (execute in order, no planning-only exit):**
0. Step 0 gates (deps, campaign_d 883/5, full excl floor 1965/5). Fix regressions before new work.
1. Probe evidence-first for next defensive gaps (item 3). Add a focused, non-duplicative test module for any proven gap/meaningful invariant — only with evidence of value; no production edits unless a real bug is proven. Run new tests + campaign_d + full excl (monitor `timeout>=450000`); record before/after counts+rc and modules touched.
2. Refresh this HANDOFF (timestamp/SHA/dirty-state, commands+counts+rc, modules touched, deltas, next slice). Keep §INITIAL TASK MESSAGE binding. Do not revert uncommitted fix/tests without cause.

**Coverage evidence (campaign7 floor — LOCKED, unchanged):** `portfolio.py` 100% (244/0) CLOSED. `sizing.py` 100% (176/0) CLOSED. `cli.py` 100% (320/0) CLOSED. `strategy.py` 100% (306/0) CLOSED. `signals.py` 98% (128, miss `37,75`), `metrics.py` 99% (134, miss `97`), `config.py` 99% (218, miss `123-124` — frozen-dataclass `except Exception: pass` fallback, unchanged), `costs.py` 98% (130, miss `59-60`) closed-without-edit. `beta.py` 92% gate closed; `data_loader.py` 40 miss / 98% gate closed (**DO NOT ALTER**).

**RULES:** no `data_loader` probe/gate churn without a concretely demonstrated, non-repeatable strict-4 mechanism from a production bug/feature need; do not touch lines `322,326` in `data_loader.py`; do not edit `.github/workflows/*` (pattern sync fix already committed); do not weaken/delete `batch148/149/172` or `campaign_d*`; no tracked `probe*`/`debug*`/`ast_probe.py` edits/commits; do not commit/push unless explicitly requested.
**ACTIVE:** campaign11 next = evidence-first defensive probing for any remaining CLI/reporting edge not covered by slices g–k; all four HANDOFF item-3 targets (warmup parity, benchmark-only overlap, duplicate tokens, partial overlap) are **CLOSED** this session. Universe-subset real bug **FIXED+regressed** (prior session). Duplicate-token reporting bug **FIXED+regressed** (prior session). Controller pattern sync **FIXED+regressed** (prior session). campaign7 floor LOCKED. `beta.py`/`data_loader` gates CLOSED.

---

# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB) (canonical; refreshed 2026-11-10T01:04:13Z @ `4d26d57`, clean). `docs/unreachable_proofs.md` is the evidence appendix. §INITIAL TASK MESSAGE above is binding. No competing handoff files.
