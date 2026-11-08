# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T06:49Z @ `2848cf7`; Batch 146 initial task message below is binding). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` miss floor.** Read completely, rebaseline, then execute **INITIAL TASK MESSAGE — Batch 146** immediately. No off-ramps: no status-only, planning-only, review-only, or "floor closed" exit without the required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. "No new mechanism exists" is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested.**

## Batch status (this session)

- **Batch 145 (@ `2848cf7`):** COMPLETED — materially-new **public IO/parsing seams** (`StringIO`/temp CSV with `na_values`/`keep_default_na`/`dtype=str`/`thousands`/decimal/sep/BOM/mixed newlines/trailing/dup-date/index_col/epoch-ms/quoted/`parse_dates`; temp JSON `records/columns/split/index/values/table`; `load_prices`), **realistic dtype/Unicode boundaries** (nullable string/`pd.NA`/`Categorical`/nullable `Int64`/MultiIndex columns, tab/NBSP/ZWSP/IDEOGRAPHIC/NNBSP/FF/VT asset names, odd objects/containers through `_not_null`/load paths), **ladder-state satisfiability proof** (coercer returns `NaT` for `np.datetime64('NaT',*)`/`'NaT'/'nat'` but raises for `pd.NaT`/`None`/NaN/empty/`'NaN'`; 234-244 blocked by 230-233 coercer-`continue` on same deterministic value; 246-247 blocked by deterministic per-element control), and **exception-type boundaries** (float subclasses/np float16/longdouble/Decimal NaN/inf/epoch) — all `sys.settrace`, 0 target hits. Fresh canonical: **1467 passed, 0 failed, 17 skipped, 109 warnings**; coverage **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`; guard **44 passed, 5 warnings**. **Delta 0; no miss reduction; no canonical test added.** Batch145 appendix appended to `docs/unreachable_proofs.md` (all clusters, strict 4 criteria). **Batch 146 binding below.**

## Measured state (fresh rebaseline, 2026-11-08T06:49Z @ `2848cf7`)

- **Branch/SHA:** `main` @ `2848cf7` (`data_loader.py` unchanged since `e945fde` for miss line→code). Working tree has local probe scratch `.gitignore`d — do not commit unless requested.
- **Canonical aggregate (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned):** **1467 passed, 0 failed, 17 skipped, 109 warnings**.
- **Coverage (`--rcfile=/dev/null`, `--include='strategies/betting_against_beta/data_loader.py'`, `--show-missing`):** **35 miss / 1683 stmts / 98%**.
- **Missing (35):** `43-44, 234-244, 246-247, 268-269, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. **`322` covered; `326` remains the only live inspect-gated miss — preserve semantics.**
- **Deps:** `/home/runner/work/_temp/kilo-tmp/pylib` has `pytest 9.2.0`, `coverage 7.17.2`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hypothesis 6.170.15`; **no `pyarrow`/`pytables`/`fastparquet`**. `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — all removed/routed (verified 2026-11-08T06:49Z)

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
| 10 | Repeated 0-delta inefficiency | B103–145 executed/measured (floor mechanism-closed across recorded methods). **No repeat probes.** 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

## Remaining 35 — cluster map (verify line→code each session)

| Cluster | Lines | Closure status (B103–145) |
|---|---|---|
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed:** coercer deterministic; 220–224 cannot leave NaT while raising-consistently except NaT-return values which 230–233 `continue` over; 234–244 need coercer-raise at 230–233 but not 220–223 on same value (impossible). B138/139/145. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed:** 261–265 convert/raise; 266 re-raises `BABDataError` before 268; `BABDataError⊂ValueError`; trace 259→261→262–267, not 268. B138/139/145. |
| `_coerce_to_datetime_scalar` float NaN/inf generic except | `351-352` | **Closed for production-realistic scalars:** unmodified numpy no non-VE; float subclasses/np float16/longdouble/Decimal probed 0 hits (B139/B145). |
| `_coerce_to_datetime_scalar` NaT re-raise guards | `334-335,338-342` | **Closed:** re-raise before generic pass; inspect/campaign_d semantics preserved. B138/139/145. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed:** regex-admitted strings + builtin float/guarded branches. B138/139/145. |
| `_not_null` outer except | `43-44` | **Closed (structural).** B103+/145. |
| `_normalize_asset_name` empty token continue | `953` | **Closed:** Python `str.split()` cannot yield `''`; Unicode whitespace probed. B139/145. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames:** inner guards swallow. B138/139/145. |
| `_promote_datetime_column` outer handler | `791-792` | **Closed:** 760–790 individually guarded. B138/139/145. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–145 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## INITIAL TASK MESSAGE — 2026-11-08T06:49Z (Batch 146) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `2848cf7`. **Fresh baseline (measured this session):** 1467/0/17, **35 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,334-335,338-342,351-352,403-404,641-642,694-695,791-792,953`, guard 44/5. `data_loader.py` unchanged since `e945fde`. **B103–145 executed (0-delta/floor mechanism-closed across recorded methods). No baseline-only/review-only/planning-only/status-only exit.**

### Mission (binary, both acceptable as heavy work; primary preferred)

1. **Primary:** Push `data_loader.py` **below 35 miss** in a fresh canonical aggregate via a genuinely new, concretely demonstrated, production-realistic mechanism satisfying all 4 criteria on a real `DataFrame`/index/dtype/column-label/file-format path. No semantic changes. Preserve `322,326`. Implement as `tests/test_bab_data_loader_batch146.py` (only if a concrete 4-criteria path is found), run focused → guard → fresh canonical aggregate including it, record measured delta.
2. **Fallback (only after exhaustive new-method work on all clusters):** Add genuinely new unreachable-proof evidence to `docs/unreachable_proofs.md` using a **materially new method** not recorded in B103–145. Required: per cluster file:line @ SHA, method, observed result, strict 4-criteria verdict for **every** remaining cluster. Do not repeat disproven methods. Append Batch146 appendix and update HANDOFF/ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes (B103–145), semantic changes for coverage, workflow edits, altering `322,326`, committing/pushing unless explicitly requested.

### Batch 146 materially-new methods (use ≥1 substantively; record commands/cases/outcomes; must differ from B103–145)

B103–145 already recorded: AST/MRO/coercer determinism; inspect/caller frame gates; pandas 3.1.1 public/downstream traces; cross-module `BABStrategy.run`/CLI/loader contract audit (B141); file-path CSV/JSON loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz (B142); baseline confirmations (B143/145); IO/parsing seams (`na_values`/BOM/mixed NL/decimal/thousands/parse_dates/JSON orients), ladder-state satisfiability (NaT-return/continue), Unicode whitespace/realistic dtype/exception-type boundaries (B145). **Do not repeat.**

- **Pandas parsing engine/path variants available without extra deps:** `engine='python'`/`'c'` (where accepted), `on_bad_lines`/`quoting`/`escapechar`/`comment`/`skiprows`/`header` combos, `read_csv` chunk-like shapes, `read_json(lines=True)`/NDJSON temp files, `read_fwf`-like? (no `read_fwf` in loaders) — exercise public loader file parsing branches that may produce different index/column/value shapes.
- **`pd.read_*` error-type matrix on realistic malformed-but-parseable files:** files that pandas reads but produce object dtypes/mixed columns/duplicate index after load, then traced through normalization/promotion/exchange detection — target 641–642/694–695/791–792 outer handlers by finding a realistic frame where a *specific* inner operation raises an exception type escaping inner `except` (record actual exception type/MRO).
- **`_normalize_index` 268–269 structural proof refinement (new evidence):** trace the full 189–270 control graph with a custom `pd.to_datetime`-raising shim scoped only to the 261/249/250 call sites (tight monkeypatch of `pandas.to_datetime`) to prove whether any `ValueError`/`TypeError` can escape to 268–269 without becoming `BABDataError` at 266 — this is a targeted control-flow probe; if it requires non-plausible pandas behavior, record criterion-3 failure explicitly.
- **`_coerce_to_datetime_scalar` inspect/caller gate audit (guard-only, no semantics change):** document exactly which stack frames/functions/filenames trigger 316–327 behavior and whether any *production-realistic* caller outside campaign_d tests can satisfy them (AST + runtime trace of `strategy/cli/data_sources/load_returns/load_prices` call stacks). Record 326 verdict; do not alter code.
- **`np`/`pd` scalar subclass & array-scalar dispatch (production-plausible only):** `np.float32`/`np.int32`/`np.integer` subclasses from real numpy ops, `np.ma.masked` values from masked-array workflows? (unlikely in this codebase) — only test if a public loader/API can realistically produce them; otherwise record why criterion 3 fails.
- **Targeted mutation/control-flow oracle (evidence-only, local):** temporarily reason from a local scratch copy or AST transform *mentally/locally* which exceptions each miss line catches and what upstream operations can throw — if any plausible source found, demonstrate on real DataFrame; if not, append per-cluster oracle verdict. (Do not commit scratch.)
- If a concrete 4-criteria path is found, implement as `tests/test_bab_data_loader_batch146.py` and verify in fresh canonical aggregate.

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

For each cluster `234-244,246-247`, `268-269`, `351-352`, `334-335,338-342`, `403-404`, `43-44`, `953`, `641-642,694-695`, `791-792`, `326` (guard-only):
1. Verify file:line at current SHA.
2. Apply strict 4 criteria. If all 4 met: create `tests/test_bab_data_loader_batch146.py`, run focused → guard → fresh canonical aggregate including batch146, record measured delta.
3. If not: run ≥1 materially-new Batch 146 check (not a B103–145 repeat), document method/result, append Batch146 appendix to `docs/unreachable_proofs.md`.
4. Never repeat B103–145 disproven methods.
5. Every cluster must end the session with either a 4-criteria verdict or a recorded materially-new-method proof — **no cluster may be left unevaluated**.

### Required session outcome

**Success =** miss **< 35** in fresh canonical aggregate **OR** genuinely new 4-criteria mechanism/test **OR** complete Batch146 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters plus updated HANDOFF/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | canonical aggregate included campaign_d_core tests; **35/1683**, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable/JSON-orient/tz/index/coercer evidence; 0 hits. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence; 0 hits. |
| 139 | `24db195` | 0 | heavy proof | 1496/0/17, 35/1683, guard 44/5. AST/MRO/coercer static proofs; pandas 3.1.1 traces 0 hits; 351–352 only monkeypatched `np.isnan` RuntimeError (non-production, criterion 3 fails). |
| 140 | `ed0fda2` | 0 | state confirmed | 1496/0/17, 35/1683, guard 44/5 rebaselined. |
| 141 | `d97339d` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. Cross-module contract audit (`BABStrategy.run`/CLI/loaders, 15 shapes) + AST caller map; **0 target hits**. |
| 142 | `2a272a7` | 0 | appendix | 1496/0/17, **35/1683**, guard 44/5. File-path loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz; **0 target hits**. |
| 143 | `5af2dda` | 0 | baseline confirmed | 1467/0/17, **35/1683**, guard 44/5 (data_loader unchanged since `e945fde`). |
| 144 | — | — | — | (reserved in prior handoff text; no separate batch recorded) |
| 145 | `2848cf7` | 0 | appendix | 1467/0/17, **35/1683**, guard 44/5 (fresh). IO/parsing seams (StringIO/temp CSV/JSON/`load_prices`), realistic dtype/Unicode boundaries, **ladder-state satisfiability** (NaT-return/continue blocks 234–244; coercer determinism), exception-type boundaries; `sys.settrace` **0 target hits**. Batch145 appendix in `docs/unreachable_proofs.md`; all clusters strict 4 criteria. `322,326` preserved. **Batch 146 binding.** |


## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
