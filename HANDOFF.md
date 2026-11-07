# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions. Every session must do heavy measurable work.

**Handoff refreshed (UTC):** 2026-11-07T03:40:12Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `1fb4134` (verify with `git rev-parse --short HEAD`)
**Measured canonical (fresh, 2026-11-07T03:39Z, this rebaseline):** batches 40-69,71-74,76-85 — **1449 passed, 0 failed, 17 skipped, 105 warnings**. Guard **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **1693 stmts, 62 miss, 96%**.

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below 62** in a **fresh completed canonical aggregate**, OR add **new high-confidence file:line unreachable proofs with mechanism evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## BOTTLENECKS — REMOVED / ROUTED

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | Ignored in `.gitignore`; removed from working tree. | Removed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` then `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` (or `strategies/betting_against_beta/*data_loader*`) with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner `except Exception` often wraps as `BABDataError` — only target if a real bypass exists. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct calls to canonical helpers with real shapes and tight scoped monkeypatches. Always verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Stale HANDOFF/ledger drift | Rebaselined this session against fresh canonical + guard + SHA. | Removed |
| 10 | `No data to report` from stale/filtered coverage DB | Run `rm -f .coverage .coverage.*` before coverage and use `--include='*data_loader.py'`. | Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh canonical (2026-11-07T03:39Z):** miss **62/1693 (96%)**, **1449 passed, 0 failed, 17 skipped, 105 warnings** (40-69,71-74,76-85), guard **44 passed, 5 warnings**.

**Remaining 62 lines (current aggregate):**
`43-44, 92-93, 196, 227-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 867-868, 901-903, 953, 1226-1227, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Cluster map / required attack order (plausibility first):**
1. **`901-903`** — last-resort promotion: `getattr(parsed, "tz", None)` truthy path. Prior probes failed because `pd.to_datetime(Series)` returns a Series without `.tz` and names normalize. Only retry with a **new mechanism** (e.g., monkeypatch `pd.to_datetime` to return a tz-aware DatetimeIndex-like object for the exact renamed object column while satisfying `parsed.isna().any()` false and later assignment/return flow), then prove in canonical.
2. **`867-868`** — unnamed-column per-element loop `except/pass` then `if coerced is not None`. Try a shape where loop body escapes to 866-867 without going to outer 874-875 (requires exception inside 853-865 that is not from `_coerce_to_datetime_scalar` apply and not swallowed by inner handlers) — max 1 focused probe.
3. **`791-792`** — candidate-name promote outer `except`. All inner statements are caught; only retry if you can make a statement after 766-790 (e.g., `pd.Series(parsed)`-adjacent control flow not present, or monkeypatched attribute access in an uncovered statement) actually propagate.
4. **`196, 268-269, 641-642, 694-695, 1226-1227, 1626-1627, 1663-1664`** — outer/defensive handlers. Treat as **proof-first**: one direct bypass attempt each max; if impossible under realistic pandas + current control flow, add/update exact structural proof and move on.
5. **`227-247`** — dayfirst last-ditch. Elementwise coercer raises (not NaT) so NaN guard is false; structurally dead unless a new NaT-producing coercion path is introduced (do **not** change production semantics just for coverage).
6. **`43-44, 92-93, 322, 326, 334-335, 338-342, 351-352, 403-404, 953, 1319-1320, 1926-1927`** — documented dead/subsumed/inspect-gated. **Do not re-probe without a genuinely new mechanism.** Convert any remaining ambiguity into explicit proof entries.

**Known covered/proved context:** `1257-1258, 561, 620, 679, 859, 861-862, 901-903?` — **901-903 remain MISSING**; `912-914` covered by batch85. Batch85 zero-delta probes are recorded in `docs/unreachable_proofs.md`; do not repeat without a new mechanism.

---

## SESSION BATCH LEDGER (cumulative, measured)

| Batch | Delta (miss) | Result | Notes |
|---|---:|---|---|
| 71–74 | -13 | measured | 108→96 across targeted reachable clusters |
| 75-probe | 0 | excluded | not in canonical |
| 76 | -2 | measured | `load_returns` price path (1853,1868) |
| 77 | -2 | measured | metadata drop inner exception (1928-1929) |
| 78 | -8 | measured | validation remap + normalize_schema drop except |
| 79 | -4 | measured | last-resort promotion (908-911 region) |
| 80 | -2 | measured | DQ tz fallback (1257-1258) |
| 81–84 | -6 | measured | aggregate 80→74 |
| 85 | -12 | measured | 74→62; covered 1257-1258 re-confirmed, 912-914, 859, 861-862, 561, 620, 679 |
| **Total (vs 139 start)** | **-77** | **62 miss** | **1449 passed, 0 failed, 17 skipped; guard 44 passed** |

Next batch number: **86**.

---

## INITIAL TASK MESSAGE — EXECUTE IMMEDIATELY (HEAVY WORK, NO COASTING)

**Timestamp (UTC):** 2026-11-07T03:40:12Z
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality.

### Mission
Push `strategies/betting_against_beta/data_loader.py` below **62 miss** in a fresh canonical aggregate, or add new high-confidence unreachable proofs that close remaining ambiguity. **Do not stop after baseline.** The session is not done until miss < 62 **or** `docs/unreachable_proofs.md` gains new file:line evidence with entrypoint + shape/monkeypatch for the clusters you touched.

### Step 0 — Environment + fresh rebaseline (MANDATORY)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy >/tmp/bab_pip_bootstrap.log 2>&1 || true
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..85}.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline. Expected anchor: **62 miss, 1449 passed, 0 failed, 17 skipped, guard 44 passed**. If different, reconcile before hunting.

### Campaign loop (repeat until session end or measurable success)
1. Pick the highest-plausibility reachable cluster: **901-903** → **867-868** → **791-792** → outer-handler/proof clusters.
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch86.py` (next sequential). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch86. Record before/after/delta. If miss < 62, update HANDOFF + proofs and continue.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch tried, observed behavior, why dead/unreachable in current aggregate). Update HANDOFF cluster map. Move on immediately.
5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract
- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files (40-69,71-74,76-85, plus any new batch). `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome
**Success =** measured miss < 62 in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss below 62 or strengthen proofs — no status-only output.**
