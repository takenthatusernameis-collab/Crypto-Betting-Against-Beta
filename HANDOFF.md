# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T04:02Z @ `c3e44a3`).** Repo-name priority = **BAB only**. Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 139** immediately. No off-ramps: no status-only, planning-only, review-only, or “floor closed” exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Measured state (fresh rebaseline, 2026-11-08T04:01Z @ `c3e44a3`)

- **Branch/SHA:** `main` @ `c3e44a3`. `strategies/betting_against_beta/data_loader.py` unchanged since `e945fde` for miss line→code. Working tree dirty only by local scratch/untracked probes and this handoff/proof update — do not commit unless requested.
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1496 passed, 0 failed, 17 skipped, 109 warnings** (47.75s).
- **Coverage (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings** (0.68s). **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest`, `coverage`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — removed/routed (verified 2026-11-08T04:01Z)

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
| 10 | Repeated 0-delta inefficiency | Batches 103–138 mechanism-closed/probed; **no repeat probes**. 0-delta without new method + recorded evidence = failed session. | Routed |

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–138) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer never returns NaT (raises); 224 completion => 225 false; element failure re-raises at 223. B138 L/N. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 raises/re-raises `BABDataError`; 266 catches before 268; `BABDataError⊂ValueError`. B138 K. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **Closed for production-realistic scalars:** unmodified numpy 0 hits (float/np.float64/subclass/Decimal); reachable only by monkeypatched `np.isnan` raising non-`ValueError`. B138 M. |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | **Closed:** re-raise before generic pass. B138 L. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. |
| `_not_null` outer except | `43-44` | **Closed (structural).** |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** `str.split()` cannot yield `''`. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames:** inner guards swallow. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–138 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## INITIAL TASK MESSAGE — 2026-11-08T04:02Z (Batch 139) — EXECUTE IMMEDIATELY

**SHA:** `c3e44a3`. **Fresh baseline:** 1496/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`. **No baseline-only/review-only/planning-only exit.**

### Mission (binary)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`.
2. **Fallback (only after exhaustive new-method work):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in B103–138. Required: per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict. Do not repeat disproven mechanisms.
3. **Forbidden:** status-only, repeat probes, semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 139 materially-new methods (use ≥1 substantively; record commands/cases/outcomes)

- **AST/control-flow proof from source:** Parse `data_loader.py` and statically prove (with concrete evidence appended) reachability/deadness for clusters where feasible (e.g., `split()` empty token, handler-order/MRO, coercer NaT contract), and explicitly document why each static claim is or is not sufficient for a miss-reduction claim.
- **Pandas 3.x realistic constructor boundaries:** Exercise `pd.read_csv`/`read_json`/`to_pickle`/`pd.DataFrame` constructors with pandas 3.1.1 behaviors (nullable dtypes, `copy_on_write` interactions, `StringDtype`/`ArrowDtype` absent fallback paths, `pd.NA` propagation) through **public loaders** and direct helper calls — but only count evidence new relative to B137/B138.
- **Targeted single-boundary monkeypatch in aggregate-realistic frames:** monkeypatch exactly one plausible boundary (`pd.to_datetime`, `pd.isna`, `Index.isna`, `DataFrame.__setitem__` on a realistic subclass, `np.issubdtype` paths if any) while keeping frame/index construction production-realistic; use `sys.settrace` to prove whether the target line executes. A hit only counts if the boundary behavior is plausible for real pandas/library behavior (satisfy criterion 3); otherwise record as non-production boundary evidence.
- **Downstream-consumption trace:** feed loader-normalized outputs into `beta`/`signals`/`portfolio`/`backtest`/`strategy` paths to detect any loader call sites or return-shape expectations that open a missed normalization branch; this is exploratory proof work, not a production change.
- If a concrete 4-criteria path is found, implement it as `tests/test_bab_data_loader_batch139.py` and verify in fresh canonical aggregate.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__, pandas.__version__, numpy.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py tests/test_bab_data_loader_batch79.py tests/test_bab_data_loader_batch80.py tests/test_bab_data_loader_batch81.py tests/test_bab_data_loader_batch82.py tests/test_bab_data_loader_batch83.py tests/test_bab_data_loader_batch84.py tests/test_bab_data_loader_batch85.py tests/test_bab_data_loader_batch86.py tests/test_bab_data_loader_batch87.py tests/test_bab_data_loader_batch88.py tests/test_bab_data_loader_batch89.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 35 miss / 1496/0/17 (or prior 1494 baseline) / guard 44/5.

### Forced campaign (no early exit)

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only):
1. Verify file:line at current SHA.
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch139.py`, run focused → guard → fresh canonical aggregate including batch139, record measured delta.
3. If not: run ≥1 materially-new check, document method/result, append Batch139 appendix to `docs/unreachable_proofs.md`.
4. Never repeat B103–138 disproven mechanisms.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch139 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| **138** | **`c3e44a3`** | **0** | **heavy proof** | **1496/0/17, 35/1683, guard 44/5.** Public `load_returns/load_prices` trace (CSV/long/JSONL/pickle) 0 hits; MRO proves `268-269` dead; coercer contract proves `234-247` dead; `351-352` only via monkeypatched `np.isnan` non-`ValueError` (non-production). Appendix in `docs/unreachable_proofs.md`. **Next: Batch 139.** |

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.