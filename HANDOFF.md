# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-08T20:35:00Z** @ `bc9ce31` workspace (`main`). `docs/unreachable_proofs.md` is evidence appendix only. **Repo-name priority = Betting Against Beta only** — next work targets `strategies/betting_against_beta/data_loader.py` remaining target-miss floor.
>
> **Authoritative Step 0 baseline (re-verified 2026-11-08T20:28Z–20:35Z, Batch 173; next agent MUST rerun fresh before any claim):** env `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `rm -f .coverage .coverage.*`; coverage `--rcfile=/dev/null --source=strategies.betting_against_beta`, report `--include='*/strategies/betting_against_beta/data_loader.py' --show-missing`. Canonical subset incl. batch172 (retained): `--ignore=tests/test_controller_progress_accounting.py` + `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` → **645 passed, 6 skipped, 34 warnings** (~41.5s). `data_loader.py`: **365 miss / 1683 stmts / 78%**. **Target-miss floor UNCHANGED (all present; verify line→code @ fresh SHA before edits): `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`** (`data_loader.py` semantic line-stable @ `e945fde`; `326` intact). `campaign_d*` guard: **883 passed, 5 skipped, 3487 deselected, 53 warnings**.
>
> **BINDING — execute immediately. BATCH 174 is reduction-first heavy work.** B103–173/M149–M173 have produced no target-floor reduction since 149 and now include complete per-cluster strict-4 verdicts through Batch 173 (`docs/unreachable_proofs.md` §B173). Next agent must still run fresh Step 0, then attempt **only materially-new, production-realistic** reduction mechanisms not disproven by B103–173; if none exist, produce **new-method evidence** (not repeats) and update the durable artifacts. **Forbidden exits:** status-only, planning-only, review-only, baseline-only, or “closed/unreachable/no mechanism” without required heavy work and evidence.

## INITIAL TASK MESSAGE — 2026-11-08T20:35:00Z (Batch 174, binding)

**Objective (repo priority):** reduce the `strategies/betting_against_beta/data_loader.py` target-miss floor in a fresh canonical aggregate, OR produce complete materially-new strict-4 unreachable-proof evidence for every remaining cluster using methods not used in B103–173/M149–M173.

**State:** `main@bc9ce31` workspace (dirty only with durable handoff/proof updates from Batch 173); `strategies/betting_against_beta/data_loader.py` line→code verified stable @ `e945fde`. **`326` is LIVE/GUARD-RELEVANT — never alter.** Target floor: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`.

### Forced heavy-work steps (do in order)

1. **Step 0 — fresh baseline (mandatory):**
   - `export PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`
   - `rm -f .coverage .coverage.*`
   - Canonical: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` with `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py ...`
   - `coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - Run `pytest -q -k campaign_d`. Verify line→code for every target cluster. **Continue immediately — baseline is not an outcome.**

2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–173/M149–M173** + current code and Batch 173 structural findings (e.g. 641-642/694-695 are shadowed second `except Exception` handlers; 268-269 shadowed by 261/266; 234-244 blocked by deterministic scalar contract; 953 construction-unreachable). If any cluster satisfies all 4 with a **new** production-realistic mechanism, implement `tests/test_bab_data_loader_batch174.py`, prove target-floor reduction in a fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172 green.

3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M174 probes over **all remaining clusters**. Forbidden repeats: all B103–173/M149–M173 methods/mechanisms. New-only directions (only if genuinely applicable and not already disproven): unmocked public-loader paths through real file I/O and pandas read options not yet exercised in aggregate (`parse_dates` combinations, `dtype_backend` where available, `na_values`/`keep_default_na` interactions on real CSV/JSON, `date_format`), exchange/wide/long frames with realistic vendor column variants, production-plausible `Index`/`Series` subclass behavior flowing through unpatched public APIs, and any real pandas behavior that can produce a first-handler bypass **without** changing production semantics or using pathological harness objects. Append `docs/unreachable_proofs.md` `## Batch 174` per cluster: `file:line@SHA`, materially-new method, observed result, strict-4 verdict. Cover **all clusters**: `43-44,234-244,246-247,268-269,326(guard-only),338-342,403-404,641-642,694-695,791-792,953`.

4. **Forbidden:** status/planning/review/baseline-only exit; M149–M173 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in fresh canonical aggregate, OR **(B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` §Batch 174 covering all clusters + HANDOFF ledger updated. Report exact commands, counts, miss lines, artifact paths.

## Bottlenecks (resolved — do not reintroduce)

| # | Bottleneck | Resolution |
|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`. **Tracked `debug_beta*`/`probe*` files already exist — never edit/commit them.** |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** |
| 3 | Deps fragility | Use `/home/runner/work/_temp/kilo-tmp/pylib`; set PATH+PYTHONPATH. |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='*/strategies/betting_against_beta/data_loader.py'`. |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326`.** |
| 9 | Canonical batch set drift | Canonical: 40-69,71-74,76-89,93,95,96,148,149,172 (no 70,75,90-92,94). Step 0 command authoritative. |
| 10 | Repeated 0-delta inefficiency | B103–173/M149–M173 executed. 0-delta without materially-new method + recorded evidence = failed session. |

**No competing handoff files exist.**

## Remaining target-miss clusters (verify line→code @ SHA)

| Cluster | Lines | Status (post-B173) |
|---|---|---|
| `_not_null` outer except | `43-44` | B173: not reducible (production-realistic structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | B173: dataflow/contract-shadow (deterministic scalar, 232/233). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | B173: handler-order shadow/MRO (261/266). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | B173: not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | B173: defensive/guarded. |
| exchange detect outer handlers | `641-642,694-695` | B173: **second `except Exception` handlers shadowed by 639/693**; no realistic escape observed. |
| promote datetime column outer handler | `791-792` | B173: nested/guarded tz-normalization except; no realistic escape observed. |
| `_normalize_asset_name` empty token continue | `953` | B173: construction-unreachable (`str.split()` default). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by B103–173 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path (no semantic change, no pathological harness).
4. Stated control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | Delta | Result | Notes |
|---|---|---|---|
| 148 | -2 | reduction | 351-352; semantics preserved. |
| 149 | -2 | reduction | 334-335 (M149). |
| 150–168 | 0 | proof | M150–M168 recorded. |
| 169 | 0 | state-only | Superseded. |
| 170 | 0 | proof | M170.1–M170.5. |
| 171 | 0 | proof | M171.A–F. |
| 172 | 0 | proof+probes | M172.1–M172.7; batch172 retained; canonical incl. batch172 645/6/34, 365 miss; target floor unchanged. |
| 173 | 0 | proof+probes (complete) | M173.1–M173.8; fresh Step 0 645/6/34, 365 miss/78%; target floor unchanged; per-cluster strict-4 verdicts in `docs/unreachable_proofs.md` §Batch 173; campaign_d 883/5/3487. No batch173 test (no reduction). |
| 174 | **PENDING — EXECUTE NOW (binding)** | binding | Fresh Step 0 → reduction attempt with only materially-new production-realistic mechanism or materially-new per-cluster proofs. 0-delta without materially-new method + recorded evidence = failed session. |

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
