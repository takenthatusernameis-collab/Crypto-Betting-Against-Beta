# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-07T02:34:57Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `7b9c08e` (verify with `git rev-parse --short HEAD`)
**Last recorded canonical (per `docs/unreachable_proofs.md`, 2026-11-07T00:32Z):** batches 40-69,71-74,76-80 — **1432 passed, 0 failed, 17 skipped**. Guard **44 passed, 5 warnings**.
**Target file:** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 80 miss, 95%**.

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below 80** in a **fresh completed canonical aggregate**, OR a **new, specific unreachable-branch proof with file:line + exact entrypoint/shape/monkeypatch evidence** in `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## BOTTLENECKS — REMOVED / ROUTED

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter (`diag*.py`, `_recon_cov.py`) | Added ignore rules to `.gitignore`; removed tracked/untracked scratch files from working tree. | **Removed (this handoff)** |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never edit/commit/push `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` then `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf` and engine call sites; inner `except Exception` often wraps as `BABDataError` — target only if a real bypass exists. | Routed |
| 6 | Aggregate-context sensitivity | Prefer direct calls to canonical entrypoints/helpers with real shapes and tight scoped monkeypatches. Always verify in fresh canonical aggregate. | Routed |
| 7 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 8 | Remaining 80 lines are mostly defensive/dead | Hunt genuinely reachable gaps first; for zero-delta probes add file:line proof and move on immediately. | Active |

---

## CURRENT STATE (rebaseline every session — do not trust stale numbers)

**Recorded baseline (from proofs, 2026-11-07T00:32Z):** miss **80/1693 (95%)**, canonical **1432 passed, 0 failed, 17 skipped** (40-69,71-74,76-80), guard **44 passed, 5 warnings**.

**Measured progress:** 139→80 miss (-59). Batches 76–80 contributed recent deltas; batch80 covered `1257-1258` (`_run_data_quality_campaign` tz fallback). Zero-delta batch80 probes are already documented as dead/subsumed for: `901-903, 1319-1320, 953, 1226-1227, 1591-1592, 1626-1627, 1663-1664, 1926-1927` (see `docs/unreachable_proofs.md` tail).

**Remaining 80 lines (prove before re-probing dead ones):**
`43-44, 92-93, 194, 196, 227-247, 268-269, 285-286, 322, 326, 334-335, 338-342, 351-352, 403-404, 561, 620, 641-642, 679, 694-695, 713-714, 733-734, 791-792, 859, 861-862, 867-868, 901-903, 912-914, 953, 1226-1227, 1319-1320, 1591-1592, 1626-1627, 1663-1664, 1926-1927`

**Priority hunt (plausible before dead):**
1. `912-914` — last-resort fallback when assigned index is not `DatetimeIndex` after `__setitem__`/assignment edge; try a frame/index subclass or monkeypatched assignment path that leaves a non-DatetimeIndex while parse succeeded.
2. `713-714`, `733-734` — `_promote_datetime_column` index/series tz conversion fallbacks after coercer normalization; craft shapes where index/parsed has `.tz` truthy but `tz_convert`/`tz_localize` behaves unexpectedly under scope.
3. `791-792`, `859,861-862,867-868` — elementwise tz paths; likely dead but test with raw `Timestamp(tz=...)` objects that survive coercion differently than strings.
4. `561,620,641-642,679,694-695` — exchange tz-aware-from-naive Timestamp branches where coercer already normalizes; prove or find a path that passes a naive-coercible-but-tz-attr-bearing object.
5. `1591-1592`, `1626-1627`, `1663-1664` — loader defensive outer handlers; only pursue if you can bypass inner `BABDataError` wrapping (subclass/raise path).
6. `194,196,227-247,268-269,285-286` — `_normalize_index` defensive elementwise/dayfirst/tz/outer excepts; deep but high line count if any reachable.
7. Structurally dead/subsumed (`43-44,92-93,322,326,334-335,338-342,351-352,403-404,901-903,953,1226-1227,1319-1320,1926-1927`) — **do not re-probe** without a new mechanism; add only stronger proof if discovered.

---

## SESSION BATCH LEDGER (cumulative)

| Batch | Delta (miss) | Result | Notes |
|---|---:|---|---|
| 71–74 | -13 | measured | 108→96 across targeted reachable clusters |
| 75-probe | 0 | excluded | 0 delta; not in canonical |
| 76 | -2 | measured | 98→96 `load_returns` price path (1853,1868) |
| 77 | -2 | measured | 96→94 metadata drop inner exception (1928-1929) |
| 78 | -8 | measured | 94→86 validation remap + normalize_schema drop except |
| 79 | -4 | measured | 86→82 last-resort promotion (908-911) |
| 80 | -2 | measured | 82→80 DQ campaign tz fallback (1257-1258); several probes proven dead |
| **Total** | **-59** | **80 miss** | **1432 passed, 0 failed, 17 skipped; guard 44 passed** (recorded) |

Next batch number: **81**.

---

## INITIAL TASK MESSAGE — EXECUTE IMMEDIATELY (HEAVY WORK, NO COASTING)

**Timestamp (UTC):** 2026-11-07T02:34:57Z
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality.

### Mission
Push `strategies/betting_against_beta/data_loader.py` below **80 miss** in a fresh canonical aggregate, or add new file:line unreachable proofs that close remaining ambiguity. **Do not stop after baseline.**

### Step 0 — Environment + fresh rebaseline (MANDATORY)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy >/tmp/bab_pip_bootstrap.log 2>&1 || true
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..80}.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline. Expected anchor: **~80 miss, 1432 passed, 0 failed, 17 skipped, guard 44 passed**. If different, reconcile before hunting.

### Campaign loop (repeat until session end or measurable success)
1. Pick the highest-plausibility reachable cluster not already proven dead (start: `912-914`, then `713-714`/`733-734`, then `791-792`/`859,861-862,867-868`).
2. **Max 1 probe per cluster.** Use real DataFrame shapes, direct helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch81.py` (next sequential). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch81. Record before/after/delta. If miss < 80, update HANDOFF + proofs and continue to batch82.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch tried, observed behavior, why dead/unreachable). Update HANDOFF priority list. Move on immediately.
5. **Never** retarget already-covered lines or dead lines without a new mechanism. **Never** touch workflows. **Never** coast.

### Execution contract
- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files (40-69,71-74,76-80, plus any new batch). Remove `rm -f .coverage .coverage.*` artifacts before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome
**Success =** measured miss < 80 in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss below 80 or strengthen proofs — no status-only output.**
