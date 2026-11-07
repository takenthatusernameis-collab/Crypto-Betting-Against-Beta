# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work (miss reduction **or** new file:line unreachable proof evidence).

**Handoff refreshed (UTC):** 2026-11-07T07:40:01Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `479db53` (working tree clean)
**Measured anchor (fresh rebaseline, 2026-11-07T07:40Z):** batches 40-69,71-74,76-89,93 — **1463 passed, 0 failed, 17 skipped, 107 warnings**. Guard **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **44 miss, 1693 stmts, 97%** (batch 93 delta -10; re-verified this session).

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** cli.py/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below the fresh baseline** in a **fresh completed canonical aggregate**, OR add **new high-confidence file:line unreachable proof evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", "explored", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.

---

## BOTTLENECKS — REMOVED / ROUTED

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`; transient `.coverage*`/`__pycache__` cleaned before canonical runs. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | Deps present in `/home/runner/work/_temp/kilo-tmp/pylib` (verified). If missing: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` and `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner handlers often wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls with real shapes and tight scoped monkeypatches. Verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Stale HANDOFF/ledger drift | Rebaselined this refresh against SHA/guard/anchor; re-verify numbers at session start. | Removed |
| 10 | `No data to report` from stale/filtered coverage DB | Clean `.coverage*` before coverage and use `--include='*data_loader.py'`. | Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Anchor (fresh, 2026-11-07T06:29Z, SHA 7a5b48b):** miss **54/1693 (97%)**, **1460 passed, 0 failed, 17 skipped** (40-69,71-74,76-89), guard **44 passed, 5 warnings**. Deps present at `/home/runner/work/_temp/kilo-tmp/pylib`.

**Remaining 44 lines (current aggregate anchor):**
`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Cluster map / required attack order (plausibility first):**
1. **`234-244, 246-247`** — `_normalize_index` dayfirst last-ditch remainder (237-247). Batch93 entered 227-233 via `np.datetime64('NaT')` passthrough through `_coerce_to_datetime_scalar` (verified: returns `pd.NaT` for `np.datetime64('NaT')`, raises `ValueError` for `pd.NaT`/`None`/unparseable strings) making `df.index.isna().any()` True at 225, then 227-245 elementwise dayfirst block executed and rows dropped at 291-295. Remainder 234-244/246-247 is the same dayfirst block's inner per-element `pd.to_datetime(..., dayfirst=True)` calls and final `except ValueError: raise` (246-247). **Proof-first** unless a production-realistic path reaching 246-247's `raise ValueError("unparseable")` without changing coercer semantics is demonstrated.
2. **`791-792`** — `_promote_datetime_column` candidate-name tz-normalization outer `except` (760-792). All inner statements individually guarded; `getattr(..., default)`/`hasattr` swallow exceptions in Python 3. Batch93 probe `92-93` (different function) is unrelated. **Proof-first**.
3. **`641-642, 694-695`** — `_detect_and_normalize_exchange_format` outer handlers. Batch90 structural proof: **dead** (641-642: 598 setup non-fallible, 608-640 swallowed by 639-640; 694-695: 648 setup safe, 668-691 swallowed by 690-691). **Proof-only** unless control flow changes.
4. **`1626-1627, 1663-1664`** — parquet/hdf5 outer `OSError/ValueError`. Batch90 structural proof: **dead** (inner handlers catch `Exception`/convert to `BABDataError`). **Proof-only**.
5. **`1926-1927`** — `_drop_metadata_columns` inner sequential-int check. Batch90 proof: **subsumed by 1915-1918** (same `first==0` + `allclose(diffs,1)` predicate). **Proof-only**.
6. **`43-44, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 953, 1319-1320`** — documented dead/subsumed/inspect-gated. **Do not re-probe without a genuinely new mechanism.** (`322`, `326` campaign_d inspect-gating — guard-relevant, do not alter.)

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
| 86 | -3 | measured | last-resort tz body + except/pass (901-903); 62→59 |
| 87 | -2 | measured | unnamed-column per-element loop except/pass (867-868); 59→57 |
| 88 | -1 | measured | numeric-index BABDataError re-raise (`_normalize_index` line 196); 57→56 |
| 89 | -2 | measured | `_coerce_numeric` copy/astype escape → outer `BABDataError` wrap (1226-1227); 56→54. `1926-1927` probe inconclusive. |
| 90 | 0 | proof-only | structural proofs strengthened (641-642,694-695,1626-1627,1663-1664,1926-1927); probe test removed (not canonical). Anchor remains **54 miss / 1460 passed**. |
| 91 | 0 | proof-only/probe | Rebaseline (2026-11-07T06:29Z, SHA 7a5b48b): canonical **1460 passed, 0 failed, 17 skipped, 105 warnings**, miss **54/1693 (97%)**, guard **44 passed**. Probe 227-247: monkeypatch-to-NaT reached guards but fell through 248 fallback — not production-realistic; coercer raises on unparseables. 791-792/outer handlers unchanged. |
| 92 | 0 | confirmed | rebaseline (2026-11-07T06:36Z, SHA 5b2d7ac): **54 miss / 1693 stmts (97%)**, **1460 passed, 0 failed, 17 skipped, 105 warnings**, guard **44 passed**. Direct module probes closed realistic NaT path to 227-247 (coercer raises `ValueError` on unparseables). All remaining clusters structural-dead/subsumed/inspect-gated. No production changes. |
| 93 | -10 | measured | **54→44**; canonical **1463 passed, 0 failed, 17 skipped, 107 warnings**, guard **44 passed**. Covered `92-93` (outer except in `_coerce_series_to_datetime_index` via `BadIter` pd.Series subclass whose `__iter__` raises — `tests/test_bab_data_loader_batch93.py::test_92_93_outer_except_via_series_iter_raises`) and `227-233`/`245` (dayfirst last-ditch entered via `np.datetime64('NaT')` passthrough through `_coerce_to_datetime_scalar` — `tests/test_bab_data_loader_batch93.py::test_227_245_dayfirst_block_via_np_datetime64_nat` + `::test_coercer_nat_passthrough_contract`). Remaining miss `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1319-1320, 1626-1627, 1663-1664, 1926-1927`. |

Next batch number: **94**.

---

## INITIAL TASK MESSAGE — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T07:40:01Z
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit.

### Mission (mandatory)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (44 miss / 1693 stmts / 97%, SHA 479db53, 1463 passed, guard 44 passed)** in a fresh canonical aggregate, OR add new high-confidence unreachable proofs that close remaining ambiguity in `docs/unreachable_proofs.md`. **Do not stop after baseline.** The session is not done until miss decreases **or** proofs gain new file:line evidence with entrypoint + shape/monkeypatch for clusters touched.

**Reality (batch93):** batch 93 covered `92-93` (outer except in `_coerce_series_to_datetime_index` via `BadIter` pd.Series subclass `__iter__` raise) and `227-233`/`245` (dayfirst last-ditch entered via `np.datetime64('NaT')` passthrough through `_coerce_to_datetime_scalar`). Miss dropped **54→44 (-10)**. Every remaining miss line is structural-dead, inspect-gated (`322,326`), or blocked by production contracts. **Production semantics must not change solely to manufacture coverage.** If no *genuinely new, production-realistic* control-flow mechanism is found, strengthen proofs with exact mechanism-closure evidence; do not fake delta.

### Step 0 — Environment + fresh rebaseline (MANDATORY, run first)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')" || (python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy && export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib)
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..93}.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Record actual baseline. If different from anchor (**44 miss, 1463/0/17, guard 44**), reconcile before hunting.

### Campaign loop (repeat until measurable success — no early exit)

1. Attack only with a **new production-realistic mechanism**: re-examine 227-247/791-792/641-642/694-695/1626-1627/1663-1664/1926-1927/268-269 for pandas/internal exception types or frame shapes not previously probed (e.g., DataFrame/Index subclasses that can throw through the exact unguarded seams *without* changing BAB semantics). Do **not** repeat coercer→NaT, `np.allclose` global falsification, or other semantics-altering probes.
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch94.py`. Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch94. Record before/after/delta. If miss decreased, update HANDOFF + proofs and continue hunting.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch tried, observed behavior, why dead/unreachable in current aggregate). Update HANDOFF cluster map. Move on immediately.
5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract

- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files (40-69,71-74,76-93, plus any new batch). `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome (binary)

**Success =** measured miss below fresh baseline (below 44 miss) in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
