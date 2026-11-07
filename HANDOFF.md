# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` while immediately moving to the next cluster.

**Handoff refreshed (UTC):** 2026-11-07T09:38:42Z
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA:** `main` @ `a1cff65` (`chore(kilo): checkpoint agent session`) — **working tree dirty** (untracked `debug_beta*.py`, `probe*.py` scratch; removed transient `tests/test_bab_data_loader_batch94.py` beta-targeting probe; canonical tests unaffected)
**Measured baseline (fresh canonical, 2026-11-07T09:38Z, batch 94 session):** batches 40-69,71-74,76-89,93 — **1463 passed, 0 failed, 17 skipped, 107 warnings**. Guard (`campaign_d*`) **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **44 miss / 1693 stmts / 97%** (`--source=strategies.betting_against_beta`, `--include='*data_loader.py'`). **Delta this session: 0 (proof-refresh). Step 0 must rebaseline before hunting.**

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

**Fresh baseline (2026-11-07T09:38Z):** miss **44/1693 (97%)**, **1463 passed, 0 failed, 17 skipped, 107 warnings** (40-69,71-74,76-89,93), guard **44 passed, 5 warnings**.

**Remaining 44 lines:**
`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1319-1320, 1626-1627, 1663-1664, 1926-1927`

**Cluster map / required attack order (plausibility first):**
1. **`234-244, 246-247`** — `_normalize_index` dayfirst last-ditch remainder. **Batch94 mechanism-closure (proof-only):** 227-247 is reachable only when 216-224 completes (no coercer raise → 224/225 execute). 232 calls the same deterministic `_coerce_to_datetime_scalar` on the same `idx`; elements that survived 216-224 therefore return the same result at 232, `continue` fires at 233, and 234-244/246-247 never execute. Trace evidence: mixed `np.datetime64('NaT') + unparseable` took 223→248 (223 raise intercepted before 225). 245 assignment is equivalent to 224. **Structurally unreachable without coercer-semantics change or non-deterministic/prod-unrealistic failure (disallowed).**
2. **`791-792`** — `_promote_datetime_column` outer `except` (760-792). **Batch94 closure:** all 760-790 statements individually guarded; Python 3 `hasattr` swallows descriptor exceptions; no uncaught statement can propagate. **Structurally dead.**
3. **`641-642, 694-695`** — `_detect_and_normalize_exchange_format` outer handlers. Batch90: inner handlers swallow all `Exception`. **Structurally dead.**
4. **`1626-1627, 1663-1664`** — parquet/hdf5 outer `OSError/ValueError`. Batch90: inner read/validate handlers convert to `BABDataError`. **Structurally dead.**
5. **`1926-1927`** — `_drop_metadata_columns` sequential-int inner check. Batch90: subsumed by 1915-1918 (`first==0` + `allclose(diffs,1)` on same `vals[finite]`). **Subsumed/dead.**
6. **`43-44, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 953, 1319-1320`** — documented dead/subsumed/inspect-gated. **Do not re-probe without a genuinely new mechanism.** `322,326` campaign_d inspect-gating is guard-relevant — **do not alter**.

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

Next batch number: **95**.

---

## INITIAL TASK MESSAGE — 2026-11-07T09:38:42Z — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T09:38:42Z
**SHA at handoff:** `a1cff65` (main; working tree dirty with untracked scratch only)
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit.

### Mission (mandatory, binary)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (44 miss / 1693 stmts / 97%)** in a fresh canonical aggregate, **OR** add new high-confidence unreachable proofs that materially close remaining ambiguity in `docs/unreachable_proofs.md` with file:line + function + entrypoint + exact shape/monkeypatch/trace + observed behavior + why dead/unreachable. **Do not stop after baseline.** The session is not done until miss decreases **or** proofs gain new mechanism-closure evidence for clusters touched.

**Reality:** Batch 94 confirmed all 44 remaining lines are structural-dead, inspect-gated, subsumed, or blocked by production contracts (234-244,246-247 blocked by 223 intercept + 232 determinism; 791-792 all-inner-guarded; 641-642/694-695/1626-1627/1663-1664/1926-1927 structural; 322/326 guard-relevant inspect-gated). **Production semantics must not change solely to manufacture coverage.** If no *genuinely new, production-realistic* control-flow mechanism is found, strengthen proofs with exact mechanism-closure evidence; do not fake delta.

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
  tests/test_bab_data_loader_batch{40..69}.py tests/test_bab_data_loader_batch{71..74}.py tests/test_bab_data_loader_batch{76..89}.py tests/test_bab_data_loader_batch93.py
python3 -m coverage report --include='*data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Record actual baseline. If different from **44 miss, 1463/0/17, guard 44**, reconcile before hunting. (If batch90-92/94/95 data-loader tests exist and are valid data-loader canonical tests, include them explicitly after confirming they do not reduce signal or target wrong modules.)

### Campaign loop (repeat until measurable success — no early exit)

1. Attack only with a **new production-realistic mechanism**: re-examine `43-44,234-244,246-247,268-269,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953,1319-1320,1626-1627,1663-1664,1926-1927` for pandas/internal exception types, frame/index/subclass shapes, or call-paths that can throw through the exact unguarded seams *without* changing BAB semantics. **Never alter `322,326` (guard-relevant).** Do **not** repeat coercer→NaT, np.allclose global falsification, deterministic-coercer same-index probes, or semantics-altering probes.
2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.
3. **If hit:** create `tests/test_bab_data_loader_batch95.py` (data_loader only). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch95. Record before/after/delta. If miss decreased, update `HANDOFF.md` + `docs/unreachable_proofs.md` and continue hunting.
4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch/trace tried, observed behavior, why dead/unreachable). Update HANDOFF cluster map. Move on immediately.
5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract

- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files; `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome (binary)

**Success =** measured miss below fresh baseline (**< 44**) in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with mechanism-closure evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
