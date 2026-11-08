# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T07:08Z @ `55b7cdb`; Batch 148 initial task message below is binding — data_loader.py unchanged since `e945fde`, same 35-miss floor). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 148** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Batch status (this session)

- **Batch 147 (@ `55b7cdb`):** COMPLETED — **no canonical miss reduction** (probe removed). Fresh canonical: **1467 passed, 0 failed, 17 skipped, 109 warnings**; coverage **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`; guard **44 passed, 5 warnings**. Materially-new evidence appended to `docs/unreachable_proofs.md` (Batch147): pandas `iloc`/object-array scalar sources (0 hits), exchange/promotion adversarial frames (0 hits), **268-269 handler-order/nesting structural proof + adversarial traces** (259→261→262–265→266→267, 0 hits), 334-342/351-352 structural/NumPy-boundary probes, 403-404/641-695/791-792/953 checks. **Concrete runtime lead (not counted as reduction):** a `float` subclass with `__array__`+`__float__` raising `TypeError` makes `numpy.isnan` raise non-`ValueError` at `data_loader.py:347`, exercising **351-352** via `_coerce_to_datetime_scalar`/`_normalize_index`/`load_returns` object-dtype index paths in `sys.settrace` probes — but canonical aggregate and isolated `coverage json` still showed 351-352 missing under the probe design used; probe test removed. **Batch 148 priority:** retry 351-352 with a **coverage-compatible** canonical test (no `sys.settrace` assertions inside test logic that conflicts with coverage; let `coverage` record execution) and verify **fresh canonical aggregate delta < 35** before claiming reduction.

## Measured state (fresh rebaseline, 2026-11-08T07:08Z @ `55b7cdb`)

- **Branch/SHA:** `main` @ `55b7cdb`. `data_loader.py` unchanged since `e945fde` (line→code stable). Local probe scratch removed. `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**).
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1467 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--source=strategies.betting_against_beta`, report `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T07:08Z)

| # | Bottleneck | Route | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; install there only if missing. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect/caller behavior and campaign_d behavior. **Never alter `322,326` semantics.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94). Reconcile in Step 0 if needed. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–147 executed/measured. **351-352 has a concrete runtime lead — retry with coverage-compatible design first.** No repeat probes. 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–147) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer deterministic/NaT-return continue blocks 234–244 ladder body; 246–247 requires 227–245 raise inconsistent with deterministic handling. B138/139/145/147. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 convert all Exception→BABDataError; 266 re-raises `BABDataError⊂ValueError`; adversarial traces 259→261→262–265→266→267. B138/139/146 M3/147 M4. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **Concrete runtime lead (not reduced):** `float` subclass with `__array__`+`__float__` raising `TypeError` makes `np.isnan` raise non-VE at 347, hits 351-352 in trace via object-dtype index/public coercion; canonical aggregate still 35 miss under prior probe design. **Batch 148 must retry coverage-compatibly.** |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | **Closed:** `except Exception: pass` follows `except ValueError: raise` after explicit `raise ValueError("bad")`; needs non-VE from NaT checks (not observed). Inspect/campaign_d semantics preserved. B138/139/145/147. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. B138/139/145/147. |
| `_not_null` outer except | `43-44` | **Closed (structural).** B103+/145/147. |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** Python `str.split()` cannot yield `''`. B139/145/147. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames.** B138/139/145/147. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. B138/139/145/147. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–147 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence; 0 hits. |
| 139 | `24db195` | 0 | heavy proof | 1496/0/17, 35/1683, guard 44/5. AST/MRO/coercer static proofs; pandas 3.1.1 traces 0 hits. |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5 rebaselined. |
| 141 | `d97339d` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. Cross-module contract audit + AST caller map; **0 target hits**. |
| 142 | `2a272a7` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. File-path loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz; **0 target hits**. |
| 143 | `5af2dda` | 0 | baseline confirmed | 1467/0/17, **35/1683**, guard 44/5 (data_loader unchanged since `e945fde`). |
| 144 | — | — | — | (reserved; no separate batch recorded) |
| 145 | `2848cf7` | 0 | appendix | 1467/0/17, **35/1683**, guard 44/5. IO/parsing seams, dtype/Unicode boundaries, ladder-state satisfiability, exception-type boundaries; `sys.settrace` 0 hits. |
| 146 | `88ef267` | 0 | appendix | 1467/0/17, **35/1683**, guard 44/5. Parse path variants, malformed-but-parseable frames, 268-269 `pd.to_datetime` control-flow trace (0 hits), inspect/caller gate audit (326 preserved). |
| 147 | `55b7cdb` | 0 | appendix + runtime lead | 1467/0/17, **35/1683**, guard 44/5. `iloc`/object-array scalar sources, exchange/promotion frames, 268-269 handler-order proof (0 hits), 334-342/351-352 structural probes. **351-352 runtime trace hit** via `float` subclass where `np.isnan` raises `TypeError` (`__array__`+`__float__` boundary), object-dtype index/public coercion path; **canonical aggregate unchanged** under probe design (probe removed). Batch148 must retry coverage-compatibly. |

## INITIAL TASK MESSAGE — 2026-11-08T07:08Z (Batch 148) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `55b7cdb` (`data_loader.py` unchanged since `e945fde`). **Fresh baseline (measured):** 1467/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. **B103–147 executed. No baseline-only/review-only/planning-only/status-only exit.**

### Mission (binary, both acceptable as heavy work; primary preferred)

1. **Primary (start here):** Re-attempt **351-352** using a **coverage-compatible** test. Batch147 showed a runtime `sys.settrace` hit: `float` subclass instance where `np.isnan` raises `TypeError` (non-`ValueError`) due to `__float__`/`__array__` boundary is passed through `_coerce_to_datetime_scalar` via production-realistic object-dtype index/coercion (`load_returns`/`_normalize_index` elementwise paths) — `data_loader.py:347` raises, 351-352 `except Exception: pass` executes, downstream coercion continues (semantics preserved: NaN/invalid remains rejectable; finite epoch-like magnitudes may coerce). **Do NOT use `sys.settrace` in the test to assert hits** (it can conflict with `coverage`); write a normal pytest case in `tests/test_bab_data_loader_batch148.py`, include batch148 in a **fresh canonical aggregate coverage run** (same Step 0 command pattern + batch148 file), and only claim reduction if **missing count < 35** and 351-352 absent from `--show-missing`/JSON. If aggregate still 35, record exact evidence (focused coverage vs aggregate, JSON line status) and do not claim reduction.
2. **Secondary (if 351-352 cannot be reduced canonically):** exhaustive new-method work on all remaining clusters. Only after that, append Batch148 materially-new unreachable-proof evidence to `docs/unreachable_proofs.md` (per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict; no repeats of B103–147). Update HANDOFF/ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–147), semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 148 materially-new methods (use ≥1 substantively; must differ from B103–147)

B103–147 already recorded the methods listed in prior handoffs/proofs; **do not repeat**. Batch147 added `iloc`/object-array scalar sources, exchange/promotion adversarial frames, 268-269 handler-order/nesting proof, 334-342/351-352 structural probes, and the 351-352 runtime-trace lead.

- **351-352 coverage-compatible closure attempt (primary):** try variants that preserve `isinstance(val,float)` but make `np.isnan`/`np.isinf` raise non-VE in numpy 2.5.4 without breaking coverage tracing: e.g. float subclass with `__float__` raising `TypeError` and/or `__array__` raising `TypeError`; ensure value reaches `_coerce_to_datetime_scalar` through public `load_returns`/`_normalize_index` object-dtype index; avoid `sys.settrace` in test; verify with canonical aggregate. If one variant hits in focused coverage but not aggregate, document call-path/aggregation difference as evidence (not reduction).
- **234-244/246-247 stateful ladder proof (new angle):** construct a `DataFrame`/object index where different code paths receive different effective values only if pandas copies/normalizes unexpectedly? (must be production-realistic) — or prove index element identity/values are identical across 220-224 and 230-233 passes under pandas 3.1.1 for object indices; record. Evidence-only is acceptable only if grounded in measured behavior.
- **268-269 final structural proof:** if a VE/TE not derived from `Exception`? impossible in Python; but confirm no `BaseException`/`KeyboardInterrupt` realistic path (not production-relevant) — keep criterion 3. Prefer measured handler-path assertion: patch `pd.to_datetime` at 261 to raise `TypeError` and confirm final exception is `BABDataError` from 264/266 (no 268) — control-flow evidence, not production criterion-3 hit.
- **641-642/694-695/791-792 targeted operation oracle:** list every non-locally-caught operation in those try regions and attempt production-realistic inputs (exchange CSV/JSON files, MultiIndex/nullable/categorical columns, unusual-but-valid timestamps) that can raise an unexpected type escaping local catches; trace targets.
- **334-335/338-342/403-404:** only if a production-realistic NaT-like scalar or epoch-like string can make a *different* operation than the guarded one raise non-VE before the explicit re-raise; otherwise record structural/non-triggerability tied to actual call sites/types.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__, pytest.__version__, coverage.__version__, scipy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py $(for i in $(seq 40 69); do echo tests/test_bab_data_loader_batch$i.py; done) $(for i in 71 72 73 74 76 77 78 79 80 81 82 83 84 85 86 87 88 89 93 95 96; do echo tests/test_bab_data_loader_batch$i.py; done)
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 35 miss / 1467/0/17 / guard 44/5.

### Forced campaign (no early exit)

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only): (1) verify file:line at current SHA; (2) apply strict 4 criteria — if all 4 met, create `tests/test_bab_data_loader_batch148.py`, run focused → guard → fresh canonical aggregate including batch148, record measured delta; (3) if not, run ≥1 materially-new Batch 148 check, document method/result, append Batch148 appendix to `docs/unreachable_proofs.md`; (4) never repeat B103–147; (5) every cluster ends with a 4-criteria verdict or recorded materially-new-method proof.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch148 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail



Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
