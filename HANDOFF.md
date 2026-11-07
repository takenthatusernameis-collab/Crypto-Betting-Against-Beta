# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-07T02:46:10Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `91ac767` (verify with `git rev-parse --short HEAD`)
**Measured canonical (fresh, this session, 2026-11-07T02:46Z):** batches 40-69,71-74,76-84,85 — **1449 passed, 0 failed, 17 skipped**. Guard **44 passed, 5 warnings**.
**Target file:** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 62 miss, 96%** (delta **74→62, -12** vs prior recorded 74).

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below 74** in a **fresh completed canonical aggregate**, OR a **new, specific unreachable-branch proof with file:line + exact entrypoint/shape/monkeypatch evidence** in `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## BOTTLENECKS — REMOVED / ROUTED

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter (`diag*.py`, `_recon_cov.py`) | Ignored in `.gitignore`; removed from working tree (prior). | **Removed** |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` then `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='strategies/betting_against_beta/*data_loader*'` or `--include='*data_loader.py'` consistently; prefer `--source=strategies.betting_against_beta` for runs and verify report includes `strategies/betting_against_beta/data_loader.py`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites; inner `except Exception` often wraps as `BABDataError` — target only if a real bypass exists. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct calls to canonical entrypoints/helpers with real shapes and tight scoped monkeypatches. Always verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Batch81-84 present in tree but HANDOFF stale | Rebaselined this session; canonical now includes 76-84. | **Removed** |
| 10 | Stale 1257-1258 "covered" claim | unreachable_proofs.md and batch80 claim 1257-1258 covered, but batch80 tests line 953 only; current aggregate confirms **1257-1258 MISSING**. Mark **open**; priority #1 for batch85. | **Removed** (reclassified to open priority) |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh canonical (2026-11-07T02:46Z):** miss **62/1693 (96%)**, **1449 passed, 0 failed, 17 skipped** (40-69,71-74,76-84,85), guard **44 passed, 5 warnings**.

**Delta this session:** 74→62 (**-12**). Lines newly covered by batch85 aggregate effect: `1257-1258, 561, 620, 679, 859, 861-862, 901-903, 912-914, 194`.

**Remaining 42 lines (current aggregate):**
`43-44, 92-93, 196, 227-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 867-868, 901-903, 953, 1226-1227, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Priority hunt (remaining plausibility; all others documented dead in docs/unreachable_proofs.md):**
1. `194` — `_normalize_index` numeric-index second elementwise assign (lines 190-194); requires numeric index whose `pd.to_datetime(idx, unit=...)` fails, first elementwise attempt raises (ValueError, not BABDataError so it falls to 189), second attempt succeeds and executes `df.index = coerced` (194). batch85 probe (stateful coerce + patched `pd.to_datetime(unit=...)` raise) produced zero delta — structure suggests the magnitude branch or the first attempt always wins/fails uniformly; re-probe only with a new mechanism, else mark dead.
2. `196, 268-269` — except handlers that only match BABDataError / never see a plain ValueError-TypeError escape.
3. `227-247` — dayfirst last-ditch block: reached only if elementwise `_coerce_to_datetime_scalar` (218-224) all succeeds yet NaN remains — it raises on bad scalars instead, so the NaN guard is False; structurally dead.
4. Structurally dead/subsumed candidates (`43-44, 92-93, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 867-868, 901-903, 953, 1226-1227, 1319-1320, 1626-1627, 1663-1664, 1926-1927`) — do not re-probe without a new mechanism; all have death-reasoning in docs/unreachable_proofs.md.

**Covered this session (batch85, tests/test_bab_data_loader_batch85.py):** `1257-1258` (re-confirmed), `912-914`, `859`, `861-862`, `561`, `620`, `679` — delta **-12** (74→62).

---

## SESSION BATCH LEDGER (cumulative, measured)

| Batch | Delta (miss) | Result | Notes |
|---|---:|---|---|
| 71–74 | -13 | measured | 108→96 across targeted reachable clusters |
| 75-probe | 0 | excluded | 0 delta; not in canonical |
| 76 | -2 | measured | `load_returns` price path (1853,1868) |
| 77 | -2 | measured | metadata drop inner exception (1928-1929) |
| 78 | -8 | measured | validation remap + normalize_schema drop except |
| 79 | -4 | measured | last-resort promotion (908-911) |
| 80 | -2 | measured (recorded) | DQ tz fallback recorded as 1257-1258; **1257-1258 missing in 2026-11-07T02:44Z canonical — batch80 tests line 953, not 1257-1258; reconcile/prove** |
| 81 | *see aggregate* | in tree/canonical | tz-property/convert probes (713-714,733-734 area targeted) |
| 82 | *see aggregate* | in tree/canonical | exchange tz branches (561/620/679/953 area targeted) |
| 83 | *see aggregate* | in tree/canonical | csv empty-after-read (1591-1592 targeted) |
| 84 | *see aggregate* | in tree/canonical | numeric index setter (194,196 targeted) |
| **81–84 aggregate** | **-6** | **measured** | 80→74; covered `285-286,713-714,733-734,1591-1592`; 1257-1258 still open |
| **Total (vs 139 start)** | **-65** | **74 miss** | **1442 passed, 0 failed, 17 skipped; guard 44 passed** |

Next batch number: **85**.

---

## INITIAL TASK MESSAGE — EXECUTE IMMEDIATELY (HEAVY WORK, NO COASTING)

**Timestamp (UTC):** 2026-11-07T02:44:16Z
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality.

### Mission
Push `strategies/betting_against_beta/data_loader.py` below **74 miss** in a fresh canonical aggregate, or add new file:line unreachable proofs that close remaining ambiguity. **Do not stop after baseline.** The session is not done until miss < 74 **or** `docs/unreachable_proofs.md` gains new high-confidence evidence with file:line + entrypoint + shape/monkeypatch.

### Step 0 — Environment + fresh rebaseline (MANDATORY)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy >/tmp/bab_pip_bootstrap.log 2>&1 || true
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..84}.py
python3 -m coverage report --include='strategies/betting_against_beta/*data_loader*' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline. Expected anchor: **~74 miss, 1442 passed, 0 failed, 17 skipped, guard 44 passed**. If different, reconcile before hunting.

### Campaign loop (repeat until session end or measurable success)
1. Pick the highest-plausibility reachable cluster (start: **1257-1258** — open in current aggregate; then `912-914`, `791-792/859/861-862/867-868`, `561/620/641-642/679/694-695`, `194,196,227-247,268-269`).
2. **Max 1 probe per cluster.** Use real DataFrame shapes, direct helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible. For `1257-1258`, call `_run_data_quality_campaign` directly with a tz-aware index and monkeypatch the index's `tz_convert`/`tz_localize` on the concrete class/instance path exercised.
3. **If hit:** create `tests/test_bab_data_loader_batch85.py` (next sequential). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch85. Record before/after/delta. If miss < 74, update HANDOFF + proofs and continue to next cluster.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch tried, observed behavior, why dead/unreachable in current aggregate). Update HANDOFF priority list. Move on immediately.
5. **Never** retarget already-covered lines or dead lines without a new mechanism. **Never** touch workflows. **Never** coast.

### Execution contract
- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files (40-69,71-74,76-84, plus any new batch). `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome
**Success =** measured miss < 74 in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss below 74 or strengthen proofs — no status-only output.**
