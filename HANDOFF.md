# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read this file completely and execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-06T23:21:43Z
**Last fresh canonical verification (UTC):** 2026-11-06T23:20:30Z (batches 40-69, 71-74, 76, 77; **1425 passed, 0 failed, 17 skipped**)
**Branch/SHA:** `main` @ `5b52b73` (verify with `git rev-parse --short HEAD`). Working tree has staged batch77/proofs/handoff updates (not committed).
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Guard rechecked (UTC):** 2026-11-06T23:18:45Z — `campaign_d*` **44 passed, 5 warnings**. `docs/unreachable_proofs.md` updated.

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, OR a **documented unreachable-branch proof with file:line evidence** while immediately moving to the next reachable cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## CURRENT VERIFIED STATE (2026-11-06T23:20:30Z)

- **Env:** Python 3.12.3, deps in `/home/runner/work/_temp/kilo-home/.local/`. pyarrow/tables/fastparquet missing → monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batches 40-69, 71-74, 76, 77):** **1425 passed, 0 failed, 17 skipped.**
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 94 miss, 94%.**
- **Missing lines (exact, 94):** `43-44, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1226-1227, 1257-1258, 1319-1320, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1927, 2192-2193`
- **Batch77 (measured delta):** covered **1928-1929** in `_drop_metadata_columns` (`load_prices` metadata-drop inner try/except) via `tests/test_bab_data_loader_batch77.py::test_load_prices_metadata_drop_inner_exception_1928_1929` (forced `np.allclose` exception on the 1925 diff-shape check for `[0,2,4,6,8]`). **Miss 96→94 (-2)**. 1926-1927 remain subsumed by 1915-1918 (unreachable).
- **Exhaustion status:** 94 remaining clusters documented as unreachable in `docs/unreachable_proofs.md` with exact file:line, function, code path, and evidence. `1591-1592` probed this session and confirmed dead (`df.empty` is evaluated at 1583 before the 1586-1592 defensive try). `1530-1536` probed; unreachable because `_normalize_columns` normalizes benchmark names before `validate_returns_dataframe` remap logic.
- **`campaign_d*` guard:** 44 passed, 5 warnings (green).

**Measured improvement:** 139→94 miss (-45). Current: 94 miss, canonical: 0 failed. Stop condition (miss < 107 with measured deltas + exhaustion-proofing) is SATISFIED; batch77 improved the floor.

---

## BOTTLENECKS — ROUTED (do not block)

| # | Bottleneck | Route-around | Status |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 2 | Remaining clusters largely unreachable | 94 clusters documented in `docs/unreachable_proofs.md`. Still hunt for *genuinely reachable* gaps NOT in the missing set or any path reachable by a real shape/monkeypatch through canonical entrypoints. Max 1 probe per cluster; 0 delta → document proof + move on. | Exhaustion-proofed / active hunt |
| 3 | Batch32 failures | Fixed as test bugs only. Canonical 0 failed. | Removed |
| 4 | Missing parquet/hdf5 deps | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Routed |
| 5 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 6 | Aggregate-context sensitivity | Prefer direct calls to canonical entrypoints/helpers with real shapes, tight scoped monkeypatches in context. Always verify in fresh canonical aggregate. | Routed |
| 7 | Coverage DB instability in workspace | Use `rm -f .coverage .coverage.*` before canonical coverage run if SQLite/data errors appear. | Routed |
| 8 | Regression risk | Rebaseline every session; do not assume miss floor is stable. | Active |

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
| 77 | lines 1928-1929 (`load_prices` metadata drop) | 1 passed | 44 passed | 96→94 (-2) | Forced `np.allclose` exception in 1923-1927 inner try; 1926-1927 still subsumed |

**Total:** 139→94 miss (-45). Canonical: 1425 passed, 0 failed, 17 skipped. Guard green.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (EXECUTE IMMEDIATELY)

**Timestamp (UTC):** 2026-11-06T23:21:43Z
**Target:** Next coding agent working in this repo
**Mode:** HEAVY WORK ONLY. No analysis-only, no planning-only, no status summaries without action.
**Scope:** `strategies/betting_against_beta/data_loader.py` ONLY.

### Mission Status
`data_loader.py` miss reduced 139→94 (-45). 94 remaining clusters are documented as unreachable in `docs/unreachable_proofs.md`. Canonical aggregate **1425 passed, 0 failed, 17 skipped**. Stop condition is SATISFIED, but **do not coast**: each session must still hunt for any real, measurable gap reachable through canonical entrypoints (including scoped monkeypatches that model realistic library/subclass behavior) and leave a stronger handoff.

**Batch77 lesson:** a cluster can look unreachable by input shape yet be reachable when an internal library call throws (1928-1929). Probe exception handlers in metadata/normalization paths with tight, targeted monkeypatches only when the handler is plausibly entered.

### MANDATORY: Heavy Work Campaign (do not stop at baseline)

**Step 0 - Rebaseline (REQUIRED):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Confirm: miss==94, canonical **1425 passed, 0 failed, 17 skipped**, guard **44 passed, 5 warnings**.

**Campaign Priority (ordered, HEAVY WORK):**
1. **Rebaseline first** (Step 0). If miss != 94, investigate/regressions before hunting.
2. **Hunt reachable clusters**: scan `docs/unreachable_proofs.md` and code for exception/fallback branches that can be reached by (a) real DataFrame/Series shapes, (b) subclass/attribute behavior, or (c) a tight scoped monkeypatch of `pd`/`np` calls used by `data_loader` when the control flow is otherwise plausible. Prioritize: `1530-1536` (validate benchmark remap — check if any path bypasses `_normalize_columns` normalization), `1591-1592` is dead (do not retarget), `1626-1627/1663-1664` outer OSError/ValueError handlers (can any non-BABDataError OSError/ValueError escape the inner structure?), `2192-2193` (normalize_schema metadata-drop outer except), and `901-903/908-914` (last-resort date promotion) — max 1 probe each.
3. **If you find a reachable cluster:** create `tests/test_bab_data_loader_batch78.py` (next). Minimal targeted tests hitting the real path. Run focused test → campaign_d guard → **fresh canonical aggregate** (include ALL batch40+ files, including batch77 and batch78). If miss decreases, record before/after/delta, update HANDOFF.md + `docs/unreachable_proofs.md`, repeat (batch79+).
4. **If every probe gives 0 delta:** document proof (file:line, function, entrypoint, shape/monkeypatch tried, why unreachable/dead) and update HANDOFF.md. Confirm final exhaustion: miss 94, all clusters documented, stop condition met.

**Execution Contract (NON-NEGOTIABLE):**
1. Step 0 baseline FIRST - no shortcuts.
2. Heavy work: either measured delta via batch78+ OR new unreachable proofs with file:line evidence.
3. Per batch: minimal tests → focused run → guard → fresh canonical aggregate → record before/after/delta.
4. Update this HANDOFF.md at end: refresh UTC, SHA, canonical results, ledger, remaining miss + proofs, next initial task message. Keep it the single durable handoff.
5. Preserve invariants: no lookahead, BABDataError on bad data, dollar-neutral/costs preserved, inspect-sensitive behavior preserved, public APIs stable.

### Hard Rules
- BAB `data_loader.py` ONLY. No infra/controller refactors, no cli.py/other-module pivot.
- `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Never edit/commit/push `.github/workflows/*`.
- Smallest correct fix only if proven contract violation. No comments. No push unless explicitly requested.
- Batch numbers sequential starting at batch78.
- Zero-delta batches do not count - retarget immediately.

### Stop Criteria
- **Success:** miss < 94 with measured deltas in fresh canonical aggregate, OR all remaining clusters have documented unreachable proofs with file:line evidence (currently satisfied at 94; improvement still required if reachable path found).
- **Required output:** Updated HANDOFF.md as single durable handoff with refreshed timestamp and clear next task message.

**BEGIN HEAVY WORK NOW. Rebaseline first, then hunt for reachable gaps below 94 or add new exhaustive proofs. Leave the handoff better than you found it.**
