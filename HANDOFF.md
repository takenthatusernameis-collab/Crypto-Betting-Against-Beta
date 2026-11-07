# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work (miss reduction **or** new file:line unreachable proof evidence).

**Handoff refreshed (UTC):** 2026-11-07T04:55Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `7dff1f8` (verify with `git rev-parse --short HEAD`; working tree has uncommitted batch87/proof/handoff updates unless committed by explicit user request)
**Measured anchor (fresh, 2026-11-07T04:55Z):** batches 40-69,71-74,76-87 — **1458 passed, 0 failed, 17 skipped, 105 warnings**. Guard **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **57 miss, 1693 stmts, 97%** (re-verify before hunting).

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

**Anchor (2026-11-07T04:55Z):** miss **57/1693 (97%)**, **1458 passed, 0 failed, 17 skipped** (40-69,71-74,76-87), guard **44 passed, 5 warnings**.

**Remaining 57 lines (current aggregate anchor):**
`43-44, 92-93, 196, 227-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1226-1227, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Cluster map / required attack order (plausibility first):**
1. **`791-792`** — candidate-name promotion tz-normalization outer `except` (760-792). Batch87: `BadParsed.tz` property raising / `apply` raising under forced else-branch did **not** hit in isolated coverage attribution; all inner statements appear individually guarded and `hasattr` swallows exceptions. **Proof-first** unless a genuinely new uncaught-statement mechanism is found.
2. **`641-642, 694-695`** — `_detect_and_normalize_exchange_format` outer handlers (OHLCV/epoch promotion blocks). Batch87 probes 0-delta. Need a non-`BABDataError` exception escaping all inner handlers with realistic shape; otherwise add/strengthen proof.
3. **`196`** — `_normalize_index` nested numeric-path `except BABDataError: raise`. Batch87 probe did not attribute hit to 196. Refine nesting-targeted mechanism or proof.
4. **`1226-1227`** — `_coerce_numeric` outer `except (ValueError,TypeError,AttributeError)`. Second pass raises `BABDataError` re-raised earlier; likely structural-dead.
5. **`1626-1627, 1663-1664`** — parquet/hdf5 outer `OSError/ValueError`. Inner handlers catch read `ImportError/Exception` and re-raise `BABDataError`; monkeypatched `OSError` converted in probe. Find bypass-of-inner-catch mechanism or proof.
6. **`227-247`** — dayfirst last-ditch. Elementwise coercer raises (not NaT) so NaN guard is false; structurally dead unless a new NaT-producing coercion path is introduced (do **not** change production semantics just for coverage).
7. **`43-44, 92-93, 322, 326, 334-335, 338-342, 351-352, 403-404, 953, 1319-1320, 1926-1927`** — documented dead/subsumed/inspect-gated. **Do not re-probe without a genuinely new mechanism.** Convert remaining ambiguity into explicit proof entries. (`322`, `326` are campaign_d inspect-gating — guard-relevant, do not alter.)

**Known covered context:** `1257-1258, 912-914, 859, 861-862, 561, 620, 679, 901-903, 867-868` covered by prior batches/batch87. Batch87 zero-delta probes recorded in `docs/unreachable_proofs.md`; do not repeat without a new mechanism.

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
| **Total (vs 139 start)** | **-82** | **57 miss** | **1458 passed, 0 failed, 17 skipped; guard 44 passed** |

Next batch number: **88**.

---

## INITIAL TASK MESSAGE — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T04:55Z
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit.

### Mission (mandatory)
Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (57 miss / 1693 stmts / 97%)** in a fresh canonical aggregate, OR add new high-confidence unreachable proofs that close remaining ambiguity in `docs/unreachable_proofs.md`. **Do not stop after baseline.** The session is not done until miss decreases **or** proofs gain new file:line evidence with entrypoint + shape/monkeypatch for clusters touched. Many remaining lines carry structural-death/probe evidence; any further delta requires a genuinely new mechanism — production semantics must not change solely to manufacture coverage.

### Step 0 — Environment + fresh rebaseline (MANDATORY, run first)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')" || (python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy && export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib)
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..87}.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```
Record actual baseline. If different from anchor (57 miss, 1458/0/17, guard 44), reconcile before hunting.

### Campaign loop (repeat until measurable success — no early exit)
1. Pick highest-plausibility cluster: **791-792** (refine mechanism, else proof) → **641-642, 694-695** → **196** → **1226-1227** → **1626-1627, 1663-1664** → proof clusters (`227-247`, `43-44, 92-93, 322, 326, 334-335, 338-342, 351-352, 403-404, 953, 1319-1320, 1926-1927`). (`867-868, 901-903` covered — do not retarget.)
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch88.py` (next sequential). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch88. Record before/after/delta. If miss decreased, update HANDOFF + proofs and continue hunting.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch tried, observed behavior, why dead/unreachable in current aggregate). Update HANDOFF cluster map. Move on immediately.
5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract
- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files (40-69,71-74,76-87, plus any new batch). `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome (binary)
**Success =** measured miss below fresh baseline (below 57 miss) in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
