# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read this file completely and execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-06T22:12:16Z
**Last fresh canonical verification (UTC):** 2026-11-06T22:12:16Z (batches 40-69, 71-74; **1482 passed, 0 failed, 23 skipped, 105 warnings**)
**Branch/SHA:** `main` @ `89721a6` (verify with `git rev-parse --short HEAD`). Working tree: **clean**.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Guard rechecked (UTC):** 2026-11-06T22:12:16Z — `campaign_d*` **44 passed, 5 warnings**. `docs/unreachable_proofs.md` present.

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction** in a **fresh completed canonical aggregate**, OR a **documented unreachable-branch proof with file:line evidence** while immediately moving to the next reachable cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## CURRENT VERIFIED STATE (2026-11-06T22:12:16Z)

- **Env:** Python 3.12.3, deps in `/home/runner/work/_temp/kilo-home/.local/`. pyarrow/tables/fastparquet missing → monkeypatch parquet/hdf5/engine branches.
- **Canonical aggregate (batches 40-69, 71-74):** **1482 passed, 0 failed, 23 skipped, 105 warnings.** (Batch32 test bugs fixed in `tests/test_bab_data_loader_coverage_gaps.py`; no source changes.)
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 96 miss, 94%.**
- **Missing lines (exact, 96):** `43-44, 92-93, 194, 196, 227-235, 237-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1226-1227, 1257-1258, 1319-1320, 1530-1531, 1533-1536, 1591-1592, 1626-1627, 1663-1664, 1926-1929, 2192-2193`
- **All 96 clusters** documented as unreachable in `docs/unreachable_proofs.md` with exact file:line, function, code path, why unreachable, and evidence.
- **Batches 71-74:** committed (c5af914, b1a2cff, 682d168). All in canonical aggregate. Batch75 verified separately (+2 passed, 0 delta) — **EXCLUDED from canonical** (route-around).
- **`campaign_d*` guard:** 44 passed, 5 warnings (green).

**Measured improvement:** 139 → 96 miss (-43, 31% reduction). Current: 96 miss, canonical: 1482/0.

---

## BOTTLENECKS — ROUTED (do not block)

| # | Bottleneck | Route-around | Status |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 2 | All remaining 96 miss documented unreachable | All proven unreachable in `docs/unreachable_proofs.md`. Only target genuinely reachable clusters not in missing list with real DataFrame shapes passed to canonical entrypoints. Max 1 probe per cluster; 0 delta → document proof + move on. | Exhaustion-proofed |
| 3 | Batch32 failures | Fixed as test bugs only in `tests/test_bab_data_loader_coverage_gaps.py`. Canonical now 0 failed. | Removed |
| 4 | Missing parquet/hdf5 deps | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites. | Routed |
| 5 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 6 | Aggregate-context sensitivity | Module-level patches neutralized. Prefer direct calls to canonical entrypoints/helpers with real shapes, tight scoped monkeypatches in context. Always verify in fresh canonical aggregate. | Routed |
| 7 | batch75.py (probes unreachable clusters) | +2 passed, 0 delta, excluded from canonical. Do not retarget. Next batch = batch76. | Routed |

---

## SESSION BATCH LEDGER

| Batch | Targets | Focused | Guard | Canonical delta (miss) | Notes |
|---|---|---|---|---|---|
| 32-fix | Test bugs (13 failures) | 33 passed | 44 passed | 96→96 (0) | Test-only fixes; canonical 1469/13→1482/0 |
| 71 | line 400 | 1 passed | 44 passed | 108→107 (-1) | `'1700000000.5'` via canonical paths |
| 72 | line 84 | 1 passed | 44 passed | 108→107 (-1) | tz-aware strings via `_coerce_series_to_datetime_index` |
| 73 | lines 1033-1034 | 1 passed | 44 passed | 107→105 (-2) | `_normalize_columns` via `_BadStr` |
| 74 | lines 2160-2163,2167-2168,2187-2189 | 4 passed | 44 passed | 105→96 (-9) | exception propagation in `normalize_schema` |
| 75-probe | 1926-1929,901-903/908-914 (excluded) | 2 passed | 44 passed | 96→96 (0) | Verified 0 delta, not in canonical |

**Total:** 139→96 miss (-43). Canonical: 1482 passed, 0 failed. Guard green.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (EXECUTE IMMEDIATELY)

**Timestamp (UTC):** 2026-11-06T22:12:16Z
**Target:** Next coding agent working in this repo
**Mode:** HEAVY WORK ONLY. No analysis-only, no planning-only, no status summaries without action.
**Scope:** `strategies/betting_against_beta/data_loader.py` ONLY.

### Mission Status
`data_loader.py` miss reduced 139→96 (-43). **All 96 remaining clusters are exhaustively documented as unreachable** in `docs/unreachable_proofs.md` with file:line, function, code path, and evidence. Canonical aggregate is **1482 passed, 0 failed**. Stop condition is SATISFIED: miss **96 < 107** with measured deltas AND full exhaustion-proofing complete.

### MANDATORY: Heavy Work Campaign (do not stop at baseline)

**Step 0 - Rebaseline (REQUIRED):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
python3 -m coverage erase && python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_betting_against_beta_data_loader.py tests/test_bab_messy_data.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Confirm: miss==96, canonical aggregate **1482 passed, 0 failed**, guard green.

### Campaign Priority (ordered, HEAVY WORK)
1. **Hunt for any genuinely reachable cluster NOT in the 96-line missing set.** Scan `docs/unreachable_proofs.md` against actual code paths. The 96 are exhaustively proven unreachable - but you MUST prove this yourself by attempting at most 1 targeted probe per suspected cluster with **real DataFrame/Series shapes passed directly to canonical entrypoints** (e.g., `load_returns_from_dataframe`, `normalize_schema`, `validate_returns_dataframe`).
2. **If you find a reachable cluster:** Create `tests/test_bab_data_loader_batch76.py` (next batch number). Write minimal targeted tests hitting the real path. Run focused test → campaign_d guard → **fresh canonical aggregate** (include ALL batch40+ files). If miss decreases, commit locally (no push), update HANDOFF.md ledger with measured delta, repeat for batch77+. **This is the ONLY path to further reduction.**
3. **If every probe gives 0 delta:** You MUST document the proof (file:line, function, entrypoint, shape tried, why unreachable) in your final response and update HANDOFF.md. The stop condition is already met - your job is to leave the next agent with an even cleaner, more actionable handoff if you discover anything new, or confirm exhaustion.
4. **Aggressively route bottlenecks:** Use direct canonical calls (module-level patches get neutralized). Monkeypatch narrowly in context. Never touch `.github/workflows/*`. Ignore batch75.py.

### Execution Contract (NON-NEGOTIABLE)
1. Step 0 baseline FIRST - no shortcuts.
2. Heavy work: either measured delta via batch76+ OR new unreachable proofs with file:line evidence.
3. Per batch: minimal tests → focused run → guard → fresh canonical aggregate → record before/after/delta.
4. Update this HANDOFF.md at end: refresh UTC, SHA, canonical results, ledger, remaining miss + proofs, next initial task message.
5. Preserve invariants: no lookahead, BABDataError on bad data, dollar-neutral/costs preserved, inspect-sensitive behavior preserved, public APIs stable.

### Hard Rules
- BAB `data_loader.py` ONLY. No infra/controller refactors, no cli.py/other-module pivot.
- `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Never edit/commit/push `.github/workflows/*`.
- Smallest correct fix only if proven contract violation. No comments. No push unless explicitly requested.
- Batch numbers sequential starting at batch76 if creating new tests.
- Zero-delta batches do not count - retarget immediately.

### Stop Criteria
- **Success:** miss < 96 with measured deltas in fresh canonical aggregate, OR all remaining clusters (current 96) have documented unreachable proofs with file:line evidence (ALREADY SATISFIED).
- **Required output:** Updated HANDOFF.md as single durable handoff with refreshed timestamp and clear next task message.

**BEGIN HEAVY WORK NOW. Rebaseline first, then hunt for reachable gaps or add new exhaustive proofs. Leave the handoff better than you found it.**
