# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Repo-name priority = **BAB only**. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only/planning-only/review-only sessions. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` closing a new mechanism with materially-new method evidence. "No new mechanism exists" is not valid without timestamped, line-by-line trace/evidence for every remaining cluster using a methodology not previously recorded. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Measured state (fresh rebaseline, 2026-11-08T03:14Z @ `eb8cb67`)

- **Branch/SHA:** `main` @ `eb8cb67` (`data_loader.py` unchanged since `e945fde`; working tree dirty only by local scratch/untracked probe files and any handoff/doc updates from this session — do not commit unless requested).
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1494 passed, 0 failed, 17 skipped, 109 warnings** (46.26s).
- **Coverage (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing exactly (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings** (0.62s). **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps/bootstrap:** present in `/home/runner/work/_temp/kilo-tmp/pylib` (`pytest`, `coverage`, `numpy`, `pandas`, `scipy`, `hypothesis 6.170.15`). Use `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.
- **Target:** push `strategies/betting_against_beta/data_loader.py` **below 35 miss** in a fresh canonical aggregate, or produce materially new unreachable-proof evidence.

## Bottlenecks — removed/routed (verified 2026-11-08T03:14Z)

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`, `debug_beta*.py`, `probe*.py`; clean `.coverage*` before coverage runs. Do not commit probes. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps fragility | `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; install there only if missing. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites as needed; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect/caller behavior and campaign_d filename/function behavior. `322` covered via campaign_d_core tests in canonical aggregate; `326` live/guard-relevant — **never alter `322,326` semantics**. | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94). Reconcile exact set in Step 0 if needed. | Routed |
| 10 | `No data to report` / stale coverage | Clean `.coverage*`; run coverage run+report in same shell/env with `--rcfile=/dev/null`. | Routed |
| 11 | Repeated 0-delta/probe inefficiency | Floor mechanism-closed through batches 103–136. No repeat probes. Next session must satisfy all 4 strict criteria with a concretely demonstrated production-realistic mechanism, or add materially new-method proof. 0-delta without new proof = failed session. | Removed/Routed |

## Remaining 35 — cluster map (verify line→code each session)

Never alter `322,326`. `322` is covered; `326` is guard-relevant/live.

| Cluster | Lines | Current closure status |
|---|---|---|
| `_normalize_index` coercer determinism / last-ditch | `234-244,246-247` | Mechanism-closed: 232 uses same coercer as 216-224 on post-224 survivors (`continue` 233); 245 same-length assignment safe. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Handler-structure dead: 261-265 converts `Exception→BABDataError`; 266 catches `BABDataError` before 268; `BABDataError⊂ValueError`. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | Proof-only boundary: guarded NaN/inf raises `ValueError`; only pathological non-`ValueError`/semantic-bypass harness plausible — not production-realistic. |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | Structural-dead: `ValueError("bad")` re-raised before generic `except Exception: pass`; identity/type-name checks. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Structural-dead for regex-admitted `str`: `float(s)` gives builtin float (`inf` on overflow); epoch branches individually guarded. |
| `_not_null` outer except | `43-44` | Structural-dead: `is None`, inner `pd.isna` guarded, unconditional return. |
| `_normalize_asset_name` empty token continue | `953` | Construction-unreachable: `str.split()` never yields empty token. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Structural-dead for production-realistic frames; inner setup/try blocks swallow/guard. |
| `_promote_datetime_column` outer handler | `791-792` | Structural-dead: 760-790 individually guarded; Python 3 `hasattr` descriptor-safe. |
| inspect/campaign_d NaT guard | `326` | **Live/guard-relevant — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–136 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## INITIAL TASK MESSAGE — 2026-11-08T03:14:10Z (Batch 137) — EXECUTE IMMEDIATELY

**SHA at handoff:** `eb8cb67`. **Fresh baseline:** 1494/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`. **No baseline-only/review-only/planning-only exit.**

### Mission (binary)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `pd.DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`.
2. **Fallback (only after exhaustive new-method work):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in batches 103–136/public-entrypoint traces. Required appendix style: per cluster, quote/verify file:line at SHA, method used, observed result, and strict 4-criteria verdict. Do not repeat disproven mechanisms.
3. **Forbidden:** status-only, repeat probes, semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 137 materially-new methods (use at least one substantively; do not fake)

Choose methods not already exhausted as identical evidence in 103–136: `hypothesis` randomized public `load_*` round-trips/property tests (installed, 6.170.15); systematic pandas nullable/extension-dtype permutations available in this env (`Int64/Float64/string/boolean`, pyarrow dtypes only if installed); CSV dialect/quoting/newline/decimal/thousands/NA-marker/BOM/compression variants through public loaders; timezone-localization metadata round-trips across CSV/JSON/Parquet/Feather/Pickle/HDF5 as available; full `to_json`/`read_json` orient matrix including odd index/column labels; MultiIndex column flattening/promote/exchange-format edge cases with production-realistic shapes; downstream `metrics`/`backtest`/`portfolio`/strategy consumption traces proving loader outputs and confirming unreachable clusters across all public entrypoints. Record concrete commands/cases and outcomes.

### Step 0 — mandatory rebaseline

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_data_loader_campaign_d_core.py tests/test_bab_data_loader_campaign_d_core2.py tests/test_bab_data_loader_campaign_d_core3.py tests/test_bab_data_loader_campaign_d_core4.py tests/test_bab_data_loader_campaign_d_core5.py tests/test_bab_data_loader_campaign_d_core_final.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py tests/test_bab_data_loader_batch79.py tests/test_bab_data_loader_batch81.py tests/test_bab_data_loader_batch82.py tests/test_bab_data_loader_batch83.py tests/test_bab_data_loader_batch84.py tests/test_bab_data_loader_batch85.py tests/test_bab_data_loader_batch86.py tests/test_bab_data_loader_batch87.py tests/test_bab_data_loader_batch88.py tests/test_bab_data_loader_batch89.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Reconcile if different from 35 miss / 1494/0/17 / guard 44/5.

### Forced campaign (no early exit)

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only):
1. Verify file:line at current SHA.
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch137.py`, run focused → guard → fresh canonical aggregate including batch137, record measured delta.
3. If not: run ≥1 materially-new check, document method/result, append batch137 appendix to `docs/unreachable_proofs.md`.
4. Never repeat disproven mechanisms from 103–136.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete batch137 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Session batch ledger (cumulative)

| Batch | Delta | Result | Notes |
|---|---|---|---|
| 126–131 | 0 | proof/probe | mechanism-closure evidence strengthened; strict 4 criteria unsatisfied. |
| 131-reconfirm @ `04bdee3` | 0 | rebaseline | 1466/0/17, 36/1683, guard 44/5. |
| 134-recon @ `a5af9ba` | 0 | rebaseline | 1466/0/17, 36/1683, guard 44/5; `322` live again. |
| 136 @ `377a70c` | -1 | miss reduction | added `tests/test_bab_data_loader_campaign_d_core*.py` to canonical aggregate; 1496/0/17, **35/1683**, `322` covered, guard 44/5. |
| Reconfirm @ `444c636` | 0 | rebaseline | 1494/0/17, **35/1683**, `322` covered, guard 44/5. |
| **Reconfirm @ `eb8cb67`** | **0** | **fresh rebaseline (this session)** | **1494/0/17, 35/1683, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5.** Bottlenecks removed/routed. **Next: Batch 137.** |

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and prior git history; this HANDOFF is the single durable operational control document. Prior batch writeups (132/133, etc.) in the old handoff were informational and are superseded by this concise state; do not delete `docs/unreachable_proofs.md` history.
