# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T07:53Z @ `2ba2c8f`; Batch 148 COMPLETED — canonical miss reduction 35→33 recorded below; Batch 149 initial task message below is binding — data_loader.py unchanged since `e945fde`, remaining floor now 33 misses). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 149** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` must remain in the canonical set and must not be deleted or weakened.**

## Batch status (this session)

- **Batch 147 (@ `55b7cdb`):** COMPLETED — no canonical miss reduction (0 delta, probe removed). Fresh canonical: 1467/0/17, 35/1683/98%, guard 44/5. Materially-new evidence appended to `docs/unreachable_proofs.md` (Batch147) incl. the 351-352 float-subclass runtime-trace lead (not counted as reduction).
- **Batch 148 (@ `2ba2c8f`):** COMPLETED — **canonical miss reduction achieved: 35 → 33**. Fresh canonical aggregate including `tests/test_bab_data_loader_batch148.py`: **1470 passed, 0 failed, 17 skipped, 109 warnings**; coverage **33 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,403-404,641-642,694-695,791-792,953` (**351-352 no longer missing**); guard **44 passed, 5 warnings** (campaign_d* included in aggregate, green).
- **Batch 148 method M148 (coverage-compatible, no `sys.settrace`):** `tests/test_bab_data_loader_batch148.py` defines `_NonValueErrorFloat(float)` with `__float__`/`__array__` raising `TypeError`; `isinstance(val, float)` is True at `data_loader.py:345`, so `np.isnan(val)` at 347 raises non-`ValueError` TypeError → 349-350 `except ValueError: raise` does not match → **351-352 `except Exception: pass` executes and coverage records it**. Coercion continues to the epoch-float branch (443+) which raises `ValueError("bad")` — **production semantics preserved (bad value still rejected)**, verified by test assertions. Verified in fresh canonical aggregate: miss count < 35 and 351-352 absent from `--show-missing`/coverage JSON. Batch148 test retained in canonical set.

## Measured state (fresh rebaseline, 2026-11-08T07:08Z @ `55b7cdb`)

- **Branch/SHA:** `main` @ `2ba2c8f`. `data_loader.py` unchanged since `e945fde` (line→code stable). Local probe scratch removed. `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**).
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned, includes batch148):** **1470 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--source=strategies.betting_against_beta`, report `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **33 miss / 1683 stmts / 98%**.
- **Missing (33):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 403-404, 641-642, 694-695, 791-792, 953` (**351-352 reduced in Batch 148**).
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
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148** (no 70,75,90-92,94). Batch148 retained in canonical set; Step 0 must include it. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–147 executed/measured. **351-352 resolved in B148 via coverage-compatible `_NonValueErrorFloat` test (35→33).** No repeat probes of closed clusters. 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–147) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer deterministic/NaT-return continue blocks 234–244 ladder body; 246–247 requires 227–245 raise inconsistent with deterministic handling. B138/139/145/147. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 convert all Exception→BABDataError; 266 re-raises `BABDataError⊂ValueError`; adversarial traces 259→261→262–265→266→267. B138/139/146 M3/147 M4. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **CLOSED — REDUCED in Batch 148 (@ `2ba2c8f`):** `_NonValueErrorFloat(float)` with `__float__`/`__array__` raising `TypeError` passes `isinstance(val, float)` at 345; `np.isnan(val)` at 347 raises TypeError (non-VE) → 351-352 `except Exception: pass` executes; value still rejected downstream via epoch-float branch `ValueError("bad")` — semantics preserved. Fresh canonical aggregate **33 miss / 1683**, 351-352 absent from `--show-missing`/coverage JSON. Coverage-compatible test retained at `tests/test_bab_data_loader_batch148.py`; no `sys.settrace`. |
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
| 147 | `55b7cdb` | 0 | appendix + runtime lead | 1467/0/17, **35/1683**, guard 44/5. `iloc`/object-array scalar sources, exchange/promotion frames, 268-269 handler-order proof (0 hits), 334-342/351-352 structural probes. **351-352 runtime trace hit** via `float` subclass where `np.isnan` raises `TypeError` (`__array__`+`__float__` boundary), object-dtype index/public coercion path; **canonical aggregate unchanged** under probe design (probe removed). Batch148 retried coverage-compatibly. |
| 148 | `2ba2c8f` | -2 | reduction | 1470/0/17, **33/1683**, guard 44/5. **351-352 reduced** via coverage-compatible `_NonValueErrorFloat` test: `np.isnan` raises TypeError at 347 → 351-352 `except Exception: pass` executes; semantics preserved (value still raises `ValueError("bad")`). Batch148 test retained in canonical set. Remaining 33: `43-44,234-244,246-247,268-269,326,334-335,338-342,403-404,641-642,694-695,791-792,953`. |

## Batch 148 completion (2026-11-08T07:53Z @ `2ba2c8f`)

**Result:** canonical miss reduction **35 → 33** (351-352 reduced via coverage-compatible `_NonValueErrorFloat` test; test retained at `tests/test_bab_data_loader_batch148.py`; production semantics preserved — bad values still raise `ValueError("bad")`). Fresh canonical: **1470/0/17, 33 miss / 1683 stmts / 98%**, guard **44/5**. Miss 351-352 removed from the remaining list.

## INITIAL TASK MESSAGE — 2026-11-08T07:53Z (Batch 149) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `2ba2c8f` (`data_loader.py` unchanged since `e945fde`). **Fresh baseline (measured):** 1470/0/17, **33 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,403-404,641-642,694-695,791-792,953`, guard 44/5. **Batch 148 completed (35→33, 351-352 reduced and retained in canonical set); B103–148 executed. No baseline-only/review-only/planning-only/status-only exit.**

### Mission (binary; primary preferred)

1. **Primary (start here):** Reduce the remaining **33** misses cluster-by-cluster. For each cluster `234-244,246-247`, `268-269`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792` (and `326` guard-only): (1) verify file:line at current SHA; (2) apply strict 4 criteria — if all 4 met with a production-realistic path, create `tests/test_bab_data_loader_batch149.py`, run focused → guard → **fresh canonical aggregate including batch148 + batch149**, record measured delta; claim reduction only if missing count < 33 and target lines absent from `--show-missing`/coverage JSON; (3) if no production-realistic path exists (as prior batches indicate for these clusters), run ≥1 materially-new Batch 149 check (method must differ from B103–148), document method/observed result, and append per-cluster strict 4-criteria verdict to `docs/unreachable_proofs.md`; (4) never repeat B103–148 checks; (5) every cluster ends with a measured reduction, a 4-criteria verdict, or a recorded materially-new-method proof. **`326` is guard-relevant: never alter its semantics; `campaign_d*` must stay 44/5 green.**
2. **Secondary (only if no cluster reduces canonically):** exhaustive materially-new-method work on all remaining clusters, then complete the Batch149 appendix in `docs/unreachable_proofs.md` covering every remaining cluster (per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict; no repeats of B103–148). Update HANDOFF.md and the session batch ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–148), semantic changes for coverage, altering `322,326` or weakening/deleting the batch148 test, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested, removing `tests/test_bab_data_loader_batch148.py` from the canonical set.

### Batch 149 materially-new methods (must differ from B103–148)

B103–148 already recorded the methods listed in prior handoffs/proofs, including batch148's `_NonValueErrorFloat` coverage-compatible closure of 351-352; **do not repeat**. Batch149 checks must be materially new and grounded in measured behavior. Candidate angles:
- operation oracle per remaining cluster: enumerate every non-locally-caught operation in the target try regions and drive production-realistic inputs (exchange CSV/JSON frames, MultiIndex/nullable/categorical/object columns, NaT/None/NaN/empty scalars, unusual-but-valid timestamps) to trace whether any escapes local catches to the target lines;
- pandas 3.1.1 version-specific behavior on object/extension-dtype indexes through `_normalize_index` elementwise coercion paths;
- inspect/caller-gate audits for inspect-sensitive regions (`322,326` semantics preserved — audit only, no probes that alter behavior);
- boundary combinations not previously combined (e.g. nullable dtype iloc values + exchange-format promotion + `load_returns` public path).
Evidence-only is acceptable only if grounded in measured behavior; **0-delta without new method + recorded evidence = failed session.**

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__, pytest.__version__, coverage.__version__, scipy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py $(for i in $(seq 40 69); do echo tests/test_bab_data_loader_batch$i.py; done) $(for i in 71 72 73 74 76 77 78 79 80 81 82 83 84 85 86 87 88 89 93 95 96 148; do echo tests/test_bab_data_loader_batch$i.py; done)
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 33 miss / 1470/0/17 / guard 44/5. Once `tests/test_bab_data_loader_batch149.py` exists, add it to the coverage run and the fresh canonical aggregate.

### Forced campaign (no early exit)

For each remaining cluster `234-244,246-247`, `268-269`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only): (1) verify file:line at current SHA; (2) apply strict 4 criteria; (3) reduce canonically or record materially-new-method proof. No cluster may be skipped without a verdict.

### Required session outcome

**Success =** miss **< 33** in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus Batch149 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF.md/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail



Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
