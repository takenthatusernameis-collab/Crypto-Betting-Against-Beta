# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` while immediately moving to the next cluster.

**Handoff refreshed (UTC):** 2026-11-07T11:04:53Z (batch100 proof-only)
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `73999ac` (`chore(kilo): checkpoint agent session`) — working tree has untracked `debug_beta*.py`/`probe*.py` scratch and uncommitted `tests/test_bab_data_loader_batch96.py` (do not commit unless explicitly requested); canonical tests unaffected.
**Measured baseline (fresh canonical, 2026-11-07T10:59Z, batch100 rebaseline):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings**. Guard (`campaign_d*`) **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **40 miss / 1693 stmts / 98%** (`--source=strategies.betting_against_beta`, `--include='*data_loader.py'`). **Delta batch100: 0 (proof-only). Step 0 must rebaseline before hunting.**

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** `cli.py`/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below the fresh baseline** in a **fresh completed canonical aggregate**, OR add **new high-confidence file:line unreachable-proof evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", "explored", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.
- **Production semantics must not change solely to manufacture coverage.** Preserve: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior, inspect-sensitive/campaign_d behavior (`322,326` guard-relevant), public APIs stable.

---

## BOTTLENECKS — REMOVED / ROUTED (verified 2026-11-07T09:38Z)

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`; transient `.coverage*` cleaned before canonical runs. Untracked `debug_beta*.py`/`probe*.py` present — do not commit. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | Deps present at `/home/runner/work/_temp/kilo-tmp/pylib`. Fallback: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` + `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. | Removed (present) |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls with real shapes and tight scoped monkeypatches/subclasses. Verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches currently **40-69,71-74,76-89,93** (no 70,75,90-92,94 in canonical aggregate; batch75/batch94 exist as non-canonical/misaligned artifacts — exclude batch94 beta-targeting probe). Rebaseline exact set in Step 0. | Routed |
| 10 | `No data to report` / stale coverage | Clean `.coverage*` before coverage; run `coverage run` and `coverage report` in same shell/env. | Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh baseline (2026-11-07T10:28Z, this session batch96):** miss **40/1693 (98%)**, **1466 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93,95,96), guard **44 passed, 5 warnings**. SHA `7c45311`.

**Remaining 40 lines:**
`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`

**Cluster map / required attack order (plausibility first):**
1. **`234-244, 246-247`** — `_normalize_index` dayfirst last-ditch remainder. **Batch94 mechanism-closure (proof-only):** 227-247 entered only when 216-224 completes (no coercer raise). 232 uses same deterministic `_coerce_to_datetime_scalar` on same `idx`; elements surviving 216-224 return same result at 232, `continue` at 233 fires, 234-244/246-247 never execute. **Structurally unreachable without coercer-semantics/non-deterministic change (disallowed).**
2. **`791-792`** — `_promote_datetime_column` outer `except` (760-792). **Structurally dead** (all 760-790 individually guarded; Python 3 `hasattr` swallows descriptor exceptions).
3. **`641-642, 694-695`** — `_detect_and_normalize_exchange_format` outer handlers. **Structurally dead** (inner handlers swallow all `Exception`).
4. **`1626-1627, 1663-1664`** — parquet/hdf5 outer `OSError/ValueError`. **Structurally dead** (inner read/validate handlers convert to `BABDataError`).
5. **`268-269`** — `_normalize_index` outer `except (ValueError,TypeError)` (160-271). **Batch96 probe:** `is_numeric_dtype` patched to raise `ValueError` was caught by inner 261 `except Exception`, reparse raised `BABDataError` at 263 path → caught by 266 (BABDataError subclasses ValueError). No realistic path raises plain `ValueError/TypeError` escaping 266. **Proof-first.**
6. **`403-404`** — `_coerce_to_datetime_scalar` epoch numeric-string outer `except` (362-404). Inner fallbacks at 365-402 each catch `Exception`; 361 regex-guarded numeric parse of `s` is deterministic. **Structurally unreachable** absent pathological float/int/pandas behavior outside tested shapes.
7. **`43-44`** — `_not_null` outer `except`. `v is None` uses identity (no `__eq__`/`__bool__`); `pd.isna` is inside inner `except Exception` (40-41). **Structurally dead.**
8. **`953`** — `_normalize_asset_name` token `if not tok_clean: continue` inside `for tok in s.split()`. `str.split()` never yields empty strings. **Unreachable by construction.**
9. **`322,326,334-335,338-342,351-352`** — inspect-gated/campaign_d NaT guards (`322,326` guard-relevant, **do not alter**) and defensive NaN/NaT re-raise wrappers; prior proofs stand. **No new mechanism.**

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
| 85 | -12 | measured | 74→62; tz/unnamed/last-resort paths |
| 86 | -3 | measured | last-resort tz body + except/pass (901-903); 62→59 |
| 87 | -2 | measured | unnamed-column per-element loop except/pass (867-868); 59→57 |
| 88 | -1 | measured | numeric-index BABDataError re-raise (`_normalize_index` 196); 57→56 |
| 89 | -2 | measured | `_coerce_numeric` copy/astype escape → outer `BABDataError` wrap (1226-1227); 56→54 |
| 90 | 0 | proof-only | structural proofs strengthened (641-642,694-695,1626-1627,1663-1664,1926-1927) |
| 91 | 0 | proof-only/probe | rebaseline 54 miss / 1460 passed; 227-247/791-792 not realistically reachable |
| 92 | 0 | confirmed | direct probes closed realistic NaT path to 227-247; all remaining structural-dead/subsumed/inspect-gated |
| 93 | -10 | measured | **54→44**; canonical **1463 passed, 0 failed, 17 skipped**; covered `92-93` + `227-233,245` |
| 94 | 0 | proof-refresh | reverified **44 miss / 1463 passed / guard 44** (40-69,71-74,76-89,93). Added mechanism-closure evidence: 234-244,246-247 unreachable due to 223 intercept + 232 coercer determinism (trace); 791-792 all-inner-guarded. Removed misaligned beta-targeting `test_bab_data_loader_batch94.py` probe. No production changes. |
| 95 | -2 | measured | `_drop_metadata_columns` sequential-int tolerance-window drop (1926-1927) covered; canonical included batch95. Baseline became 42 miss before batch96. |
| 96 | -2 | measured | **42→40**; canonical **1466 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93,95,96), guard **44 passed**. Covered quality `to_numeric(...).to_numpy` fallback **1319-1320** (`validate_returns_dataframe`, `quality=True`) via scoped `pd.to_numeric` monkeypatch for one column. Proved 268-269/403-404/43-44/953 remain structural-dead/proof-first. SHA `7c45311`. |
| 97 | 0 | proof-only | Rebaseline **40 miss / 1466 passed / guard 44** (SHA `8f1ec29`, 40-69,71-74,76-89,93,95,96). Direct probes added mechanism-closure evidence to `docs/unreachable_proofs.md`: **234-244** still unreachable (232 coercer deterministic after 216-224 gate); **245** can execute in dayfirst block but **246-247** not reached by pathological index-assignment failure under current nested recovery (no production-realistic mechanism); **268-269** BABDataError-MRO/handler-ordering gated (266 catches `BABDataError(ValueError)` first) — no plain VE/TE escape demonstrated; **403-404** overflow/inf/nan numeric strings miss outer except; **953** `split()` never yields empty token. **43-44,322,326,334-352,641-642,694-695,791-792,1626-1627,1663-1664** unchanged structural-dead/inspect-gated. No production-semantics changes. |
| 98 | 0 | proof-only | Rebaseline **40 miss / 1466 passed / guard 44** (SHA `8f1ec29`, 2026-11-07T10:48Z, 40-69,71-74,76-89,93,95,96). Targeted probes (1/cluster): **245-247** — DataFrame subclass raising `ValueError` on 2nd `index` assignment (target 245) completed with DatetimeIndex, 6 index-set attempts; **246-247 did not fire** (recovery absorbed). **268-269** — handler order 266 (`BABDataError`) before 268 (`ValueError/TypeError`) + 261-265 only re-raise/wrap as BABDataError; no plain VE/TE escape. **403-404** — `av=abs(numf)` (364) is the only unwrapped statement in 362-402; builtin float makes it safe for regex-admitted `str`. **43-44** identity+wrapped-pd.isna+returns only; **953** `split()` construction-unreachable. Others unchanged structural-dead/inspect-gated (`322,326` guard-relevant). `docs/unreachable_proofs.md` batch98 added. No production-semantics changes. |

Next batch number: **99**.

---

## INITIAL TASK MESSAGE — 2026-11-07T10:55Z — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T10:49:00Z
**SHA at handoff:** `8f1ec29` (main; working tree has untracked `debug_beta*.py`/`probe*.py` scratch and uncommitted `tests/test_bab_data_loader_batch96.py` — do not commit unless explicitly requested)
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit.

### Mission (mandatory, binary)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (40 miss / 1693 stmts / 98%)** in a fresh canonical aggregate, **OR** add new high-confidence unreachable proofs that materially close remaining ambiguity in `docs/unreachable_proofs.md` with file:line + function + entrypoint + exact shape/monkeypatch/trace + observed behavior + why dead/unreachable. **Do not stop after baseline.**

**Reality (batch98 proof-only):** remaining **40** lines — `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Batch98 confirmed: 234-244 coercer-determinism blocked; 245-executed but 246-247 not reached by forced `ValueError` on 2nd index assignment (6 index-set attempts, DatetimeIndex result, recovery absorbed). 268-269 handler-order + BABDataError-MRO gated (266 before 268; 261-265 only BABDataError). 403-404 only unwrapped statement is `av=abs(numf)` (364) — safe for regex-admitted `str`. 953 construction-unreachable (`split()`); 43-44 structural-dead. 322,326 inspect-gated (**do not alter**). 334-352/641-642/694-695/791-792/1626-1627/1663-1664 structural-dead per proofs. **Production semantics must not change solely to manufacture coverage.** If no *genuinely new, production-realistic* control-flow mechanism is found, strengthen proofs with exact mechanism-closure evidence; do not fake delta.

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

1. Attack only with a **new production-realistic mechanism**: re-examine `43-44,234-244,246-247,268-269,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953,1626-1627,1663-1664` for pandas/internal exception types, frame/index/subclass shapes, or call-paths that can throw through the exact unguarded seams *without* changing BAB semantics. **Never alter `322,326` (guard-relevant).** Do **not** repeat coercer→NaT, np.allclose global falsification, deterministic-coercer same-index probes, is_numeric_dtype→BABDataError-converted probes, BadStr/index-assignment subtype probes that only confirm MRO/handler ordering/recovery absorption, or semantics-altering probes.
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch99.py` (data_loader only). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch99. Record before/after/delta. If miss decreased, update `HANDOFF.md` + `docs/unreachable_proofs.md` and continue hunting.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch/trace tried, observed behavior, why dead/unreachable). Update HANDOFF cluster map. Move on immediately.
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
