# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` while immediately moving to the next cluster.

**Handoff refreshed (UTC):** 2026-11-07T11:20:27Z (batch101 proof-only rebaseline; working tree clean at SHA 7927e0a)
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `7927e0a` (`chore(kilo): checkpoint agent session`) — working tree contains uncommitted proof/docs handoff updates from this session only; no production code changes. Canonical tests unaffected.
**Measured baseline (fresh canonical, 2026-11-07T11:16Z, batch101 rebaseline):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings**. Guard (`campaign_d*`) **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **40 miss / 1693 stmts / 98%** (`--source=strategies.betting_against_beta`, `--include='*data_loader.py'`). **Delta batch101: 0 (proof-only). Step 0 must rebaseline before hunting.**

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** `cli.py`/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below the fresh baseline** in a **fresh completed canonical aggregate**, OR add **new high-confidence file:line unreachable-proof evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", "explored", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.
- **Production semantics must not change solely to manufacture coverage.** Preserve: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior, inspect-sensitive/campaign_d behavior (`322,326` guard-relevant), public APIs stable.

---

## BOTTLENECKS — REMOVED / ROUTED (verified 2026-11-07T11:16Z)

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`; transient `.coverage*` cleaned before canonical runs. Untracked `debug_beta*.py`/`probe*.py` present — do not commit. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | Install to `/home/runner/work/_temp/kilo-tmp/pylib` if missing: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` + `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls with real shapes and tight scoped monkeypatches/subclasses. Verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94 in canonical aggregate). Rebaseline exact set in Step 0. | Routed |
| 10 | `No data to report` / stale coverage | Clean `.coverage*` before coverage; run `coverage run` and `coverage report` in same shell/env. | Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh baseline (2026-11-07T11:16Z, batch101):** miss **40/1693 (98%)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93,95,96), guard **44 passed, 5 warnings**. SHA `7927e0a`.

**Remaining 40 lines:**
`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`

**Cluster map / required attack order (plausibility first):**
1. **`234-244, 246-247`** (`_normalize_index` dayfirst 227-247): 234-244 coercer-determinism unreachable (232 same coercer as 216-224). 245 reachable on NaT-entry path; 246-247 `ValueError("unparseable")` not reached in production-realistic traces — 248 catches and NaT-robust fallbacks recover; outer conversion yields `BABDataError`. **Proof-first; no non-realistic DataFrame subclass harness.**
2. **`351-352`** (`_coerce_to_datetime_scalar`): trace showed reachable only for pathological `float` subclass where `np.isnan` triggers `__float__` raising `RuntimeError`; current behavior lets value slip past NaN guard (returns `NaT` later) — **any change is semantic**. Do not alter production semantics; proof-first/pathological-only.
3. **`334-335,338-342`**: `ValueError("bad")` re-raised by intended branches; `except Exception: pass` unreachable for production-realistic values (`type().__name__` compare / `is pd.NaT` identity safe). Structural-dead.
4. **`268-269`**: 261 catches `Exception` → 262-265 always convert/re-raise as `BABDataError`; 266 catches before 268. No plain VE/TE escape. Handler-structure dead.
5. **`403-404`**: 364 `abs(numf)` only unwrapped in 362-402; `float(s)` returns builtin float for regex-admitted `str`; all branches guarded. Structural-dead for normal input.
6. **`43-44`** (`_not_null`): identity + wrapped `pd.isna` + `return True`; no unwrapped fallible statement. Structural-dead.
7. **`953`** (`_normalize_asset_name`): `str.split()` never yields empty token; construction-unreachable.
8. **`641-642, 694-695`** (`_detect_and_normalize_exchange_format`): inner handlers swallow all `Exception`. Structural-dead.
9. **`791-792`** (`_promote_datetime_column` 760-792): all statements individually guarded; Python 3 `hasattr` swallows descriptor exceptions. Structural-dead.
10. **`1626-1627, 1663-1664`** (parquet/hdf5): inner read/validate convert to `BABDataError`. Structural-dead.
11. **`322,326`** — inspect-gated/campaign_d NaT guards (**guard-relevant, DO NOT ALTER**).

---

## SESSION BATCH LEDGER (cumulative, measured)

| Batch | Delta (miss) | Result | Notes |
|---|---:|---|---|
| 71–89,93,95,96 | -56 | measured | 96→40 cumulative (see docs/unreachable_proofs.md). |
| 90–92,94,97–101 | 0 | proof-only | mechanism-closure/handler-structure evidence strengthened; no production-realistic miss reduction found. |
| 101 | 0 | proof-only | Rebaseline 40/1693, 1466/0/17, guard 44 (SHA 7927e0a). Traced 245/246-247 NaT-entry + targeted index-fail recovery (246-247 not hit). Confirmed 351-352 reachable only by pathological `float.__float__`-raising subclass (semantic to "fix"); 334-335/338-342/43-44/953/268-269/403-404 structural-dead. |

Next batch number: **102**.

---

## INITIAL TASK MESSAGE — 2026-11-07T11:20:27Z — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T11:20:27Z
**SHA at handoff:** `7927e0a` (main)
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit.

### Mission (mandatory, binary)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (40 miss / 1693 stmts / 98%)** in a fresh canonical aggregate, **OR** add new high-confidence unreachable proofs that materially close remaining ambiguity in `docs/unreachable_proofs.md` with file:line + function + entrypoint + exact shape/monkeypatch/trace + observed behavior + why dead/unreachable. **Do not stop after baseline.**

**Reality (batch101 proof-only):** remaining **40** — `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. 351-352 is *technically* triggerable only by a pathological `float` subclass whose `__float__` raises during `np.isnan` (trace-confirmed); exercising/fixing it changes NaN-guard semantics — **disallowed**. 246-247 not reached by production-realistic NaT-entry/index-recovery traces. 234-244 coercer-determinism blocked. 268-269/334-335/338-342/43-44/403-404/641-642/694-695/791-792/953/1626-1627/1663-1664 structural-dead/handler-structure/construction-unreachable. **322,326 inspect-gated — DO NOT ALTER.** **Production semantics must not change solely to manufacture coverage.**

### Step 0 — Environment + fresh rebaseline (MANDATORY, run first)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')" || (python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy && export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib)
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py \
  tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py \
  tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..89}.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Record actual baseline. If different from **40 miss, 1466/0/17, guard 44**, reconcile before hunting.

### Campaign loop (repeat until measurable success — no early exit)

1. Attack only with a **new production-realistic mechanism** not previously disproven: re-examine remaining clusters for pandas/internal exception types, frame/index/subclass shapes, or call-paths that throw through exact unguarded seams *without* changing BAB semantics. **Never alter `322,326`. Never change semantics to "fix" 351-352 pathological NaN-subclass slip.** Do **not** repeat: coercer→NaT/same-index determinism, handler-order/BABDataError-MRO probes, 245 index-set failures that only confirm recovery absorption, is_numeric_dtype→BABDataError conversion, np.allclose global falsification, normal `str.split`/`_not_null`/`abs(numf)` structural probes.
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch102.py` (data_loader only). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch102. Record before/after/delta. If miss decreased, update `HANDOFF.md` + `docs/unreachable_proofs.md` and continue hunting.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch/trace tried, observed behavior, why dead/unreachable/pathological/semantic). Update HANDOFF cluster map. Move on immediately.
5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract

- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files; `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome (binary)

**Success =** measured miss below fresh baseline (**< 40**) in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with mechanism-closure evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
