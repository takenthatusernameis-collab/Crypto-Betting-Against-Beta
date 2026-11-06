# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read this file completely, fix any environment bottleneck, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-06T23:44:10Z
**Last verified canonical (UTC):** 2026-11-06T23:44:10Z (batches 40-69, 71-74, 76-78; **1428 passed, 0 failed, 17 skipped**) — *fresh aggregate completed this session.*
**Branch/SHA:** `main` @ `45c2a9b` (verify with `git rev-parse --short HEAD`).
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

- **Verified canonical (2026-11-06T23:44:10Z):** batches 40-69, 71-74, 76-78 — **1428 passed, 0 failed, 17 skipped**.
- **`strategies/betting_against_beta/data_loader.py`: 1693 stmts, 86 miss, 95%**.
- **Missing lines (exact, 86):** `43-44, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 908-914, 953, 1226-1227, 1257-1258, 1319-1320, 1591-1592, 1626-1627, 1663-1664, 1926-1927`
- **Batch78 (measured delta, this session):** covered **1530-1531, 1533-1536, 2192-2193** via `tests/test_bab_data_loader_batch78.py` (tight `DataFrame.rename`/`drop` monkeypatches). **Miss 94→86 (-8)**.
- **Exhaustion status:** 86 lines documented in `docs/unreachable_proofs.md`. Batch78 proved benchmark-remap and normalize_schema metadata-drop exception handlers reachable under case-mismatch/monkeypatch conditions — keep hunting.
- **`campaign_d*` guard:** 44 passed, 5 warnings.

**Measured improvement to date:** 139→86 miss (-53). Stop condition (miss < 107 with measured deltas + exhaustion-proofing) was SATISFIED; **do not coast** — any newly reachable gap below 86 is required heavy work.

---

## BOTTLENECKS — ROUTED (do not block)

| # | Bottleneck | Route-around | Status |
|---|---|---|---|
| 1 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 2 | **Deps/bootstrap fragility** | Bootstrap once: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` then use `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` (or explicit `sys.path.insert` in one-liners) for all test/coverage commands. In this session pandas import via env var was flaky in one probe but worked via explicit path insertion; prefer explicit `PYTHONPATH` + verify with `python3 -c "import pandas,pytest,coverage,numpy,scipy"`. | **Active — fix in Step 0** |
| 3 | Remaining clusters largely unreachable | 86 lines documented in `docs/unreachable_proofs.md`. Hunt *genuinely reachable* gaps via (a) real shapes, (b) subclass/attribute behavior, (c) tight scoped monkeypatches of `pd`/`np`/`data_loader` internals when control flow is plausible. Max 1 probe per cluster; 0 delta → document proof + move on. | Exhaustion-proofed / active hunt |
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
| 77 | lines 1928-1929 (`load_prices` metadata drop) | 1 passed | 44 passed | 96→94 (-2) | Forced `np.allclose` exception in 1923-1927 inner try; 1926-1927 subsumed |
| 78 | lines 1530-1531,1533-1536,2192-2193 (`validate_returns_dataframe` benchmark remap; `normalize_schema` metadata-drop outer except) | 3 passed | 44 passed | 94→86 (-8) | Lowercase benchmark arg + normalized column case exposed remap; `rename`/`drop` monkeypatches hit exception handlers |

**Total:** 139→86 miss (-53). Canonical (this session): 1428 passed, 0 failed, 17 skipped. Guard green.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (EXECUTE IMMEDIATELY)

**Timestamp (UTC):** 2026-11-06T23:44:10Z
**Target:** Next coding agent working in this repo
**Mode:** HEAVY WORK ONLY. No analysis-only, no planning-only, no status summaries without action.
**Scope:** `strategies/betting_against_beta/data_loader.py` ONLY.

### Mission Status
`data_loader.py` miss reduced 139→86 (-53). 86 remaining lines are documented in `docs/unreachable_proofs.md`. **Do not coast**: each session must either (1) produce a measured miss reduction below 86 in a fresh canonical aggregate, or (2) add a new, specific unreachable proof with file:line + exact entrypoint/shape/monkeypatch evidence and immediately probe the next cluster.

**Batch78 lesson:** case-mismatch between caller args and normalized columns can expose remap/exception paths (`1530-1536`), and `normalize_schema` metadata-drop outer except is reachable when `DataFrame.drop` throws (`2192-2193`). Keep probing plausible internal-throw paths, not only input-shape dead ends.

### MANDATORY: Heavy Work Campaign (do not stop at baseline)

**Step 0 — Environment + rebaseline (REQUIRED, unblock first):**
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
# Bootstrap deps if missing (idempotent target dir)
python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy >/tmp/bab_pip_bootstrap.log 2>&1 || true
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/usr/local/lib/python3.12/dist-packages
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline (passed/failed/skipped/miss/guard). If miss != 86 or tests fail unexpectedly, investigate before hunting.

**Campaign Priority (ordered, HEAVY WORK):**
1. **Unblock + rebaseline** (Step 0). No further work until deps import and baseline is recorded.
2. **Hunt reachable clusters** (max 1 probe each, then decide): prioritize exception/defensive handlers plausibly reachable by monkeypatch or rare shapes — `1626-1627`/`1663-1664` (parquet/hdf5 outer `OSError`/`ValueError` handlers: can monkeypatch `pd.read_parquet`/`pd.read_hdf` or validation path to raise `OSError`/`ValueError` that escapes inner `except Exception`? inner catches `Exception` including OSError/ValueError and wraps as BABDataError, so likely dead — prove with targeted attempt), `901-903/908-914` (last-resort object-column datetime promotion after earlier candidate-name promotion failed/was skipped), `791-792`/`859,861-862,867-868` (tz conversion internals on odd scalar types), `561,620,641-642,679,694-695` (`_detect_and_normalize_exchange_format` tz-aware Timestamp branches where `pd.Timestamp(pdv)` becomes tz-aware from coercer output?), `194,196,227-247` (numeric/string last-ditch dayfirst/elementwise index coercion), `1226-1227,1257-1258,1319-1320,1591-1592` (defensive outer excepts — likely dead but require proof attempts where plausible). **Do not retarget** covered lines or clearly dead paths without a new mechanism.
3. **If you find a reachable cluster:** create `tests/test_bab_data_loader_batch79.py` (next). Minimal targeted tests hitting the real path. Run focused test → campaign_d guard → **fresh canonical aggregate** (include ALL batch40+ files, including batch78 and batch79). If miss decreases, record before/after/delta, update HANDOFF.md + `docs/unreachable_proofs.md`, repeat (batch80+).
4. **If a probe gives 0 delta:** do NOT keep the batch in canonical unless it adds value; document proof (file:line, function, entrypoint, shape/monkeypatch tried, why unreachable/dead) in `docs/unreachable_proofs.md` and update HANDOFF.md. Move to next cluster immediately.

**Execution Contract (NON-NEGOTIABLE):**
1. Step 0 bootstrap + baseline FIRST — no shortcuts.
2. Heavy work: either measured delta via batch78+ OR new unreachable proofs with file:line evidence.
3. Per batch: minimal tests → focused run → guard → fresh canonical aggregate → record before/after/delta.
4. Update this HANDOFF.md at end: refresh UTC, SHA, actual canonical results, ledger, remaining miss + proofs, next initial task message. Keep it the single durable handoff.
5. Preserve invariants: no lookahead, BABDataError on bad data, dollar-neutral/costs preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.

### Hard Rules
- BAB `data_loader.py` ONLY. No infra/controller refactors, no cli.py/other-module pivot.
- `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Never edit/commit/push `.github/workflows/*`.
- Smallest correct fix only if proven contract violation. No comments. No push unless explicitly requested.
- Batch numbers sequential starting at batch79.
- Zero-delta batches do not count — retarget immediately.

### Stop Criteria
- **Success:** miss < 86 with measured deltas in a fresh canonical aggregate, OR additional clusters have documented unreachable proofs with file:line evidence beyond current docs (and handoff is stronger/clearer).
- **Required output:** Updated HANDOFF.md as single durable handoff with refreshed timestamp and clear next task message.

**BEGIN HEAVY WORK NOW. Unblock deps, rebaseline, then hunt for reachable gaps below 86 or add new exhaustive proofs. Leave the handoff better than you found it.**
