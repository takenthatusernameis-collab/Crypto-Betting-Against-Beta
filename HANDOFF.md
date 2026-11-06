# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read this file completely, fix any environment bottleneck, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-06T23:58:54Z
**Last verified canonical (UTC):** 2026-11-06T23:58:54Z (batches 40-69, 71-74, 76-79; **1431 passed, 0 failed, 17 skipped**) — *fresh aggregate completed this session.*
**Branch/SHA:** `main` @ `a41d713` (verify with `git rev-parse --short HEAD`). Uncommitted work in this session: `tests/test_bab_data_loader_batch79.py`, `docs/unreachable_proofs.md`, `HANDOFF.md`.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, OR a **documented unreachable-branch proof with file:line evidence** while immediately moving to the next reachable cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## CURRENT VERIFIED STATE (rebaseline if drift suspected)

- **Verified canonical (2026-11-06T23:56:00Z):** batches 40-69, 71-74, 76-79 — **1431 passed, 0 failed, 17 skipped**.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 82 miss, 95%**.
- **Missing lines (exact, 82):** `43-44, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 912-914, 953, 1226-1227, 1257-1258, 1319-1320, 1591-1592, 1626-1627, 1663-1664, 1926-1927`
- **Batch79 (measured delta, this session):** covered **908-911** via `tests/test_bab_data_loader_batch79.py`. Reachable via `_promote_datetime_column` last-resort promotion of an exotic non-candidate object date column (`when_recorded`) not consumed by exchange normalization/named-candidate paths (with tz-normalization exception path exercised). **Miss 86→82 (-4)**.
- **Exhaustion status:** Remaining 82 lines documented with file:line proofs in `docs/unreachable_proofs.md`. Key dead clusters: `_not_null` outer except (43-44), `_coerce_series_to_datetime_index` outer except (92-93), `_normalize_index` elementwise/dayfirst/tz/outer excepts (194,196,227-247,268-269,285-286), `_coerce_to_datetime_scalar` inspect/campaign_d + post-reraise/outer passes (322,326,334-335,338-342,351-352,403-404), exchange tz branches where coercer already normalizes (561,620,641-642,679,694-695), promote tz/index fallbacks (713-714,733-734,791-792,859,861-862,867-868,901-903,912-914), asset-name empty-token restore (953), numeric/quality outer excepts (1226-1227,1257-1258,1319-1320), loader defensive/outer handlers (1591-1592,1626-1627,1663-1664), metadata sequential-int subsumed (1926-1927).
- **`campaign_d*` guard:** 44 passed, 5 warnings.
- **Measured improvement to date:** 139→82 miss (-57). Stop condition (miss < 107 with measured deltas + exhaustion-proofing) SATISFIED; **do not coast** — any newly reachable gap below 82 is required heavy work.

---

## BOTTLENECKS — ROUTED (do not block)

| # | Bottleneck | Route-around | Status |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 2 | Deps/bootstrap fragility | `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` then `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. Verified this session: deps import OK (pandas present). | **Resolved** |
| 3 | Remaining clusters largely unreachable | 82 lines documented in `docs/unreachable_proofs.md`. Hunt *genuinely reachable* gaps via (a) real shapes, (b) subclass/attribute behavior, (c) tight scoped monkeypatches of `pd`/`np`/`data_loader` internals when control flow is plausible. Max 1 probe per cluster; 0 delta → document proof + move on. | Exhaustion-proofed / active hunt |
| 4 | Batch32 failures | Fixed as test bugs only. Canonical 0 failed. | Removed |
| 5 | Missing parquet/hdf5 deps | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Routed |
| 6 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 7 | Aggregate-context sensitivity | Prefer direct calls to canonical entrypoints/helpers with real shapes, tight scoped monkeypatches in context. Always verify in fresh canonical aggregate. | Routed |
| 8 | Coverage DB instability | Use `rm -f .coverage .coverage.*` before canonical coverage run if SQLite/data errors appear. | Routed |
| 9 | Regression risk | Rebaseline every session; do not assume miss floor is stable. | Active |

---

## SESSION BATCH LEDGER

| Batch | Targets | Focused | Guard | Canonical delta (miss) | Notes |
|---|---|---|---|---|---|
| 32-fix | Test bugs (13 failures) | 33 passed | 44 passed | 96→96 (0) | Test-only fixes; canonical 0 failed |
| 71 | line 400 | 1 passed | 44 passed | 108→107 (-1) | `'1700000000.5'` via canonical paths |
| 72 | line 84 | 1 passed | 44 passed | 108→107 (-1) | tz-aware strings via `_coerce_series_to_datetime_index` |
| 73 | lines 1033-1034 | 1 passed | 44 passed | 107→105 (-2) | `_normalize_columns` via `_BadStr` |
| 74 | lines 2160-2163,2167-2168,2187-2189 | 4 passed | 44 passed | 105→96 (-9) | exception propagation in `normalize_schema` |
| 75-probe | 1926-1929,901-903/908-914 (excluded) | 2 passed | 44 passed | 96→96 (0) | 0 delta, not in canonical |
| 76 | lines 1853,1868 (`load_returns` price path) | 2 passed | 44 passed | 98→96 (-2) | Reachable price-detection branches |
| 77 | lines 1928-1929 (`load_prices` metadata drop) | 1 passed | 44 passed | 96→94 (-2) | Forced `np.allclose` exception in 1923-1927 inner try |
| 78 | lines 1530-1531,1533-1536,2192-2193 | 3 passed | 44 passed | 94→86 (-8) | `validate_returns_dataframe` benchmark remap + `normalize_schema` metadata-drop outer except |
| 79 | lines 908-911 (`_promote_datetime_column` last resort) | 3 passed | 44 passed | 86→82 (-4) | Exotic non-candidate object date column (`when_recorded`); tz exception path exercised |

**Total:** 139→82 miss (-57). Canonical (this session): 1431 passed, 0 failed, 17 skipped. Guard green.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (EXECUTE IMMEDIATELY)

**Timestamp (UTC):** 2026-11-06T23:58:54Z
**Target:** Next coding agent working in this repo
**Mode:** HEAVY WORK ONLY. No analysis-only, no planning-only, no status summaries without action.
**Scope:** `strategies/betting_against_beta/data_loader.py` ONLY.

### Mission Status
`data_loader.py` miss reduced 139→82 (-57). 82 remaining lines are documented in `docs/unreachable_proofs.md`. **Do not coast**: each session must either (1) produce a measured miss reduction below 82 in a fresh canonical aggregate, or (2) add a new, specific unreachable proof with file:line + exact entrypoint/shape/monkeypatch evidence and immediately probe the next cluster.

**Batch79 lesson:** last-resort datetime promotion is reachable when a non-candidate object column (e.g. `when_recorded`) contains fully parseable datetimes and is not consumed by exchange normalization/named-candidate promotion. Probe remaining defensive branches there (901-903 tz-aware parsed series; 912-914 set_index fallback) with tight scoped index/assignment behavior if plausible.

### MANDATORY: Heavy Work Campaign (do not stop at baseline)

**Step 0 — Environment + rebaseline (REQUIRED, unblock first):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
# Bootstrap deps if missing (idempotent target dir)
python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy >/tmp/bab_pip_bootstrap.log 2>&1 || true
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..79}.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline (passed/failed/skipped/miss/guard). Expected: **miss == 82, 1431 passed, 0 failed, 17 skipped, guard 44 passed**. If miss != 82 or tests fail unexpectedly, investigate before hunting.

**Campaign Priority (ordered, HEAVY WORK):**
1. **Unblock + rebaseline** (Step 0). No further work until deps import and baseline is recorded at miss 82.
2. **Hunt reachable clusters** (max 1 probe each, then decide): prioritize plausible defensive/exception handlers — `901-903` (last-resort tz-aware `parsed` where `getattr(parsed,'tz')` is truthy; batch79 exercised tz string parsing but may not hit Series `.tz` branch in aggregate), `912-914` (last-resort fallback when assigned index not DatetimeIndex), `1626-1627`/`1663-1664` (parquet/hdf5 outer OSError/ValueError — inner `except Exception` wraps OSError/ValueError as BABDataError so outer is likely dead; prove with a case where `BABDataError` is bypassed or inner catch behavior differs), `1591-1592` (CSV defensive recheck — likely dead; prove), `953` (`_normalize_asset_name` all-unit token restore — construct input whose tokens all strip to unit/currency set while preserving non-empty restore), `791-792`/`859,861-862,867-868` (elementwise tz paths after coercer normalization — likely dead; prove), `561,620,641-642,679,694-695` (exchange tz-aware-from-naive Timestamp — likely dead; prove), `194,196,227-247,268-269,285-286` (normalize_index defensive paths), `43-44,92-93,334-335,338-342,351-352,403-404,1226-1227,1257-1258,1319-1320,1926-1927` (structurally dead/subsumed — prove only if a new mechanism appears). **Do not retarget** covered lines or clearly dead paths without a new mechanism.
3. **If you find a reachable cluster:** create `tests/test_bab_data_loader_batch80.py` (next). Minimal targeted tests hitting the real path. Run focused test → campaign_d guard → **fresh canonical aggregate** (include ALL batch40+ files, including batch79 and batch80). If miss decreases, record before/after/delta, update HANDOFF.md + `docs/unreachable_proofs.md`, repeat (batch81+).
4. **If a probe gives 0 delta:** do NOT keep the batch in canonical unless it adds value; document proof (file:line, function, entrypoint, shape/monkeypatch tried, why unreachable/dead) in `docs/unreachable_proofs.md` and update HANDOFF.md. Move to next cluster immediately.

**Execution Contract (NON-NEGOTIABLE):**
1. Step 0 bootstrap + baseline FIRST — no shortcuts.
2. Heavy work: either measured delta via batch80+ OR new unreachable proofs with file:line evidence.
3. Per batch: minimal tests → focused run → guard → fresh canonical aggregate → record before/after/delta.
4. Update this HANDOFF.md at end: refresh UTC, SHA, actual canonical results, ledger, remaining miss + proofs, next initial task message. Keep it the single durable handoff.
5. Preserve invariants: no lookahead, BABDataError on bad data, dollar-neutral/costs preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.

### Hard Rules
- BAB `data_loader.py` ONLY. No infra/controller refactors, no cli.py/other-module pivot.
- `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Never edit/commit/push `.github/workflows/*`.
- Smallest correct fix only if proven contract violation. No comments. No push unless explicitly requested.
- Batch numbers sequential starting at batch80.
- Zero-delta batches do not count — retarget immediately.

### Stop Criteria
- **Success:** miss < 82 with measured deltas in a fresh canonical aggregate, OR additional clusters have documented unreachable proofs with file:line evidence beyond current docs (and handoff is stronger/clearer).
- **Required output:** Updated HANDOFF.md as single durable handoff with refreshed timestamp and clear next task message.

**BEGIN HEAVY WORK NOW. Unblock deps, rebaseline, then hunt for reachable gaps below 82 or add new exhaustive proofs. Leave the handoff better than you found it.**
