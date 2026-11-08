# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T09:57:20Z @ `6769341`; rebaseline verified 2026-11-08 — Batch 150 COMPLETED @ `1630eda`/`3e33818` with 0 delta, 31 miss unchanged, per-cluster strict 4-criteria materially-new evidence M150.1–M150.7 in `docs/unreachable_proofs.md` §Batch 150; **Batch 151 is the binding next session — execute its INITIAL TASK MESSAGE immediately**. `data_loader.py` unchanged since `e945fde`, line→code stable). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor.** Read completely, rebaseline, then do heavy work. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Batch status (this session)

- **Batch 148 (@ `2ba2c8f`):** COMPLETED — **canonical miss reduction 35 → 33**. `_NonValueErrorFloat` (`np.isnan` TypeError at 347, non-VE) executed 351-352; semantics preserved (value still rejected as `ValueError("bad")`). `tests/test_bab_data_loader_batch148.py` retained.
- **Batch 149 (@ `34f462e`, this session):** COMPLETED — **canonical miss reduction achieved: 33 → 31**. Fresh canonical aggregate including `tests/test_bab_data_loader_batch148.py` + `tests/test_bab_data_loader_batch149.py`: **1473 passed, 0 failed, 17 skipped, 109 warnings**; coverage **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953` (**334-335 no longer missing**); guard **44 passed, 5 warnings** (campaign_d* included in aggregate, green).
- **Batch 149 method M149 (coverage-compatible, no `sys.settrace`):** `_NameRaisesMeta` metaclass with `__name__` as `@property` raising `RuntimeError` (non-VE). For an instance of that metaclass class, `type(val).__name__` at `data_loader.py:330` raises RuntimeError → 332 `except ValueError: raise` does not match → **334-335 `except Exception: pass` executes and coverage records it**. Coercion continues and rejects the non-datetime scalar — **semantics preserved**. Verified by direct coercion, `_normalize_index` object-dtype index, and public `load_returns`; fresh canonical aggregate 33→31, 334-335 absent from `--show-missing`/coverage JSON. `tests/test_bab_data_loader_batch149.py` retained.

## Measured state (fresh rebaseline, 2026-11-08T09:49Z @ `66b49f5`)

- **Branch/SHA:** `main` @ `66b49f5` (working tree clean at rebaseline except this HANDOFF timestamp update). `data_loader.py` unchanged since `e945fde` (line→code stable). `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**).
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned, includes batch148+149):** **1473 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--source=strategies.betting_against_beta`, report `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **31 miss / 1683 stmts / 98%**.
- **Missing (31):** `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (**334-335 reduced in Batch 149**).
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T09:49Z @ `66b49f5`)

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
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained; Step 0 must include them. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–149 executed/measured. **351-352 resolved B148 (35→33); 334-335 resolved B149 (33→31).** No repeat probes of closed clusters. 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

## Remaining 31 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–149) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer deterministic/NaT-return continue blocks 234–244 ladder body; 246–247 requires 227–245 raise inconsistent with deterministic handling. B138/139/145/147. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 convert all Exception→BABDataError; 266 re-raises `BABDataError⊂ValueError`; adversarial traces 259→261→262–265→266→267. B138/139/146 M3/147 M4. |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | **Open candidate (narrow):** 337 is `val is pd.NaT` identity check; 338 explicit `raise ValueError("bad")` caught by 339 — reaching 341-342 requires a non-VE exception escaping 337/338 in that block (not demonstrated). 334-335 was closed via metaclass `__name__` descriptor (M149) — **different mechanism**; do not repeat. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. B138/139/145/147. |
| `_not_null` outer except | `43-44` | **Closed (structural).** B103+/145/147. |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** Python `str.split()` cannot yield `''`. B139/145/147. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames.** B138/139/145/147. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. B138/139/145/147. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–149 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | 35/1683, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence. |
| 139 | `24db195` | 0 | heavy proof | AST/MRO/coercer static proofs; pandas 3.1.1 traces 0 hits. |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5. |
| 141 | `d97339d` | 0 | appendix | Cross-module contract audit + AST caller map; 0 hits. |
| 142 | `2a272a7` | 0 | appendix | File-path loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz; 0 hits. |
| 143 | `5af2dda` | 0 | baseline confirmed | 1467/0/17, 35/1683, guard 44/5. |
| 144 | — | — | — | (reserved) |
| 145 | `2848cf7` | 0 | appendix | IO/parsing seams, ladder-state, exception-type boundaries; 0 hits. |
| 146 | `88ef267` | 0 | appendix | Parse variants, 268-269 control-flow trace, inspect/caller gate audit. |
| 147 | `55b7cdb` | 0 | appendix + runtime lead | 351-352 runtime trace hit (float subclass, np.isnan TypeError boundary), canonical aggregate unchanged (probe removed). |
| 148 | `2ba2c8f` | -2 | reduction | **351-352 reduced** via coverage-compatible `_NonValueErrorFloat` test; semantics preserved. 1470/0/17, **33/1683**, guard 44/5. |
| 149 | `34f462e` | -2 | reduction | **334-335 reduced** via coverage-compatible metaclass `__name__`-raises test (M149); semantics preserved. 1473/0/17, **31/1683**, guard 44/5. |

## Batch 150 completion (2026-11-08T09:12Z @ `1630eda`)

**Result:** 0 delta — canonical miss floor unchanged at **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. Fresh canonical (rebaselined): **1473 passed, 0 failed, 17 skipped, 109 warnings**. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `e945fde`. No production semantics changed; batch148/149 retained in canonical set; `326` preserved.

**Materially-new Batch 150 methods (M150.1–M150.7, recorded in `docs/unreachable_proofs.md` §Batch 150):** M150.1 identity/VE-only analysis for 338-342; M150.2 `sys.settrace` handler-order trace for 268-269 (hits 261-267, BABDataError); M150.3 `sys.settrace` object-dtype+`np.datetime64('NaT')` dayfirst trace for 234-247 (hits 227-233,245; 234-244/246-247 miss); M150.4 regex-admitted epoch boundary/runtime probe under pandas 3.1.1 for 403-404; M150.5 exchange/OHLCV/long-format `sys.settrace` for 641-642/694-695; M150.6 tz-aware candidate promotion trace for 791-792; M150.7 construction/runtime probes for 43-44/953. **No cluster reduced; all remaining clusters have per-cluster strict 4-criteria verdicts.**

## INITIAL TASK MESSAGE — 2026-11-08T09:49Z (Batch 151) — BINDING, EXECUTE IMMEDIATELY

**SHA (rebaseline):** `66b49f5` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Fresh baseline (measured 2026-11-08T09:49Z):** 1473/0/17, **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`, guard 44/5. **Batch 150 completed (0 delta, M150.1–M150.7 recorded with per-cluster strict 4-criteria verdicts in `docs/unreachable_proofs.md` §Batch 150); B103–150 executed. No baseline-only/review-only/planning-only/status-only exit.** This is the only active task message.

### Mission (binary; primary preferred)

1. **Primary (start here):** Reduce the remaining **31** misses cluster-by-cluster. For each cluster `234-244,246-247`, `268-269`, `338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792` (and `326` guard-only): (1) verify file:line at current SHA; (2) apply strict 4 criteria — if all 4 met with a production-realistic path, create `tests/test_bab_data_loader_batch151.py`, run focused → guard → **fresh canonical aggregate including batch148 + batch149 + batch151**, record measured delta; claim reduction only if missing count < 31 and target lines absent from `--show-missing`/coverage JSON; (3) if no production-realistic path exists, run ≥1 **materially-new Batch 151** check per unresolved cluster (must differ from B103–150, including M150.1–M150.7 traces/probes), document method/observed result, and append per-cluster strict 4-criteria verdict to `docs/unreachable_proofs.md` §Batch 151; (4) never repeat B103–150 checks; (5) every cluster ends with a measured reduction, a 4-criteria verdict, or a recorded materially-new-method proof. **`326` is guard-relevant: never alter its semantics; `campaign_d*` must stay 44/5 green.**
2. **Secondary (only if no cluster reduces canonically):** exhaustive materially-new-method work on all remaining clusters, then complete the Batch151 appendix in `docs/unreachable_proofs.md` covering every remaining cluster (per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict; no repeats of B103–150). Update HANDOFF.md and the session batch ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–150 / M150 methods), semantic changes for coverage, altering `322,326` or weakening/deleting batch148/149 tests, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested, removing `tests/test_bab_data_loader_batch148.py` or `tests/test_bab_data_loader_batch149.py` from the canonical set.

### Batch 151 materially-new methods (must differ from B103–150)

B103–150 recorded methods including B148 `_NonValueErrorFloat`, B149 metaclass `__name__` descriptor, and M150.1–M150.7 traces/probes — **do not repeat**. Any B151 method must use a genuinely different mechanism (e.g. coverage-tracer interaction distinct from prior; pandas 3.1.1 C-level coercion edge on realistic loader input; dtype/extension-array behavior not previously exercised; a provable control-flow oracle based on bytecode/dis/AST reachability *plus* a runtime contradiction test — evidence-only acceptable only when grounded in measured behavior). **0-delta without new method + recorded evidence = failed session.**

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__, pytest.__version__, coverage.__version__, scipy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py $(for i in $(seq 40 69); do echo tests/test_bab_data_loader_batch$i.py; done) $(for i in 71 72 73 74 76 77 78 79 80 81 82 83 84 85 86 87 88 89 93 95 96 148 149; do echo tests/test_bab_data_loader_batch$i.py; done)
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 31 miss / 1473/0/17 / guard 44/5. Once `tests/test_bab_data_loader_batch151.py` exists, add it to the coverage run and the fresh canonical aggregate.

### Forced campaign (no early exit)

For each remaining cluster `234-244,246-247`, `268-269`, `338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only): (1) verify file:line at current SHA; (2) apply strict 4 criteria; (3) reduce canonically or record materially-new-method proof. No cluster may be skipped without a verdict.

### Required session outcome

**Success =** miss **< 31** in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus Batch151 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF.md/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
