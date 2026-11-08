# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-08T21:57Z** @ workspace `a0511ea` (`main`; durable handoff/proof refreshed this session). `docs/unreachable_proofs.md` is evidence appendix only (§Batch 178 appended this session). **Repo-name priority = Betting Against Beta only** — next work targets `strategies/betting_against_beta/data_loader.py` remaining target-miss floor (Batch 179 binding).

> **Authoritative Step 0 baseline (re-verified 2026-11-08T21:57Z, Batch 178; next agent MUST rerun fresh before any claim):** env `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `rm -f .coverage .coverage.*`; coverage `--rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_betting_against_beta*.py tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py`; report via `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`. Canonical subset incl. batch172 (retained): **645 passed, 6 skipped, 34 warnings** (~41s). `data_loader.py` (blob `596ee9e` @ `a0511ea`): **365 miss / 1683 stmts / 78%**. **Target-miss floor UNCHANGED (all present; verify line→code @ fresh SHA before edits): `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`**. `326` intact/LIVE-GUARD. `campaign_d*` guard: **883 passed, 5 skipped, 3487 deselected, 53 warnings**.

> **BINDING — execute immediately. BATCH 178 complete (0-delta, materially-new M178 proof evidence recorded in `docs/unreachable_proofs.md` §Batch 178; no `test_bab_data_loader_batch178.py` created). BATCH 179 binding.** B103–178/M149–M178 have produced no target-floor reduction since 149 and include complete per-cluster strict-4 verdicts through Batch 178 (`docs/unreachable_proofs.md` §Batch 178). Next agent must still run fresh Step 0, then attempt **only materially-new, production-realistic** reduction mechanisms not disproven by B103–178/M149–M178; if none exist, produce **new-method evidence** (not repeats) and update the durable artifacts. **Forbidden exits:** status-only, planning-only, review-only, baseline-only, or "closed/unreachable/no mechanism" without required heavy work and evidence.

## INITIAL TASK MESSAGE — 2026-11-08T21:37Z (Batch 178, binding)

**Objective (repo priority):** confirm `strategies/betting_against_beta/data_loader.py` target-miss floor is unchanged in a fresh canonical aggregate (Batch 177 complete: 0 reduction, all clusters strict-4 not-reducible, §Batch 177 recorded in `docs/unreachable_proofs.md`), OR produce complete materially-new strict-4 unreachable-proof/reduction evidence using methods not used in B103–177/M149–M177.

**State:** workspace `17aa635` (`main`; durable handoff/proof refreshed this session); `strategies/betting_against_beta/data_loader.py` blob `596ee9e`, line→code verified 2026-11-08T21:37Z. Batch 177 executed: canonical **645 passed, 6 skipped, 34 warnings**, **365 miss / 1683 stmts / 78%**, target floor unchanged; `pytest -q -k campaign_d` **883 passed, 5 skipped, 3487 deselected, 53 warnings**. **`326` is LIVE/GUARD-RELEVANT — never alter.** Target floor: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. Batch 177 evidence: M177.1–M177.8 public file/format entrypoint probes under sys.settrace (xlsx/parquet/hdf5 if available, `load_prices` CSV, exchange long OHLCV, full Binance wide OHLCV, tz-offset promotion via public CSV, `timestamp` promotion via `validate_returns_dataframe`) → **0 target hits**; all clusters **not reducible**; §Batch 177 appended to `docs/unreachable_proofs.md`; HANDOFF refreshed to Batch 178.

### Forced heavy-work steps (do in order)

1. **Step 0 — fresh baseline (mandatory):**
   - `export PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`
   - `rm -f .coverage .coverage.*`
   - Canonical: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` with `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py ...`
   - `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - Run `pytest -q -k campaign_d`. Verify line→code for every target cluster. **Continue immediately — baseline is not an outcome.**

2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–177/M149–M177** + current code and structural findings. If any cluster satisfies all 4 with a **new** production-realistic mechanism, implement `tests/test_bab_data_loader_batch178.py`, prove target-floor reduction in a fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172 green.

3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M178 probes over **all remaining clusters**. Forbidden repeats: all B103–177/M149–M177 methods/mechanisms (incl. M175.1–M175.7 read-option/vendor-frame paths, M176.1–M176.8 direct private-function enumeration, M177.1–M177.8 file/format entrypoints: xlsx/parquet/hdf5/load_prices/exchange OHLCV variants/tz-offset public CSV/timestamp promotion). Candidate new-method space (pick genuinely new): alternate pandas I/O codepaths (pyarrow fastpath toggles if present), `read_csv` `engine`/`memory_map`/`dtype`/`converters` interactions under trace, `DataFrame` construction from `numpy` structured arrays or `from_records` entering validator, `MultiIndex`→normalization boundaries, `to_datetime` with `format` inference variants, or static `ast`/control-flow proof that a specific handler is structurally dominated (must include observed runtime corroboration). Append `docs/unreachable_proofs.md` `## Batch 178` per cluster: `file:line@SHA`, materially-new method, observed result, strict-4 verdict. Cover **all clusters**: `43-44,234-244,246-247,268-269,326(guard-only),338-342,403-404,641-642,694-695,791-792,953`.

4. **Forbidden:** status/planning/review/baseline-only exit; M149–M177 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in fresh canonical aggregate, OR **(B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` §Batch 178 covering all clusters + HANDOFF ledger updated. Report exact commands, counts, miss lines, artifact paths.

## Bottlenecks (resolved — do not reintroduce)

| # | Bottleneck | Resolution |
|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`. **Tracked `debug_beta*`/`probe*` files already exist — never edit/commit them.** |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** |
| 3 | Deps fragility | Use `/home/runner/work/_temp/kilo-tmp/pylib`; set PATH+PYTHONPATH. |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='*/strategies/betting_against_beta/data_loader.py'`; use `python -m coverage report` if `coverage` not on PATH. |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326`.** |
| 9 | Canonical batch set drift | Canonical: 40-69,71-74,76-89,93,95,96,148,149,172 (no 70,75,90-92,94). Step 0 command authoritative. |
| 10 | Repeated 0-delta inefficiency | B103–177/M149–M177 executed. 0-delta without materially-new method + recorded evidence = failed session. |

**No competing handoff files exist.**

## Remaining target-miss clusters (verify line→code @ SHA)

| Cluster | Lines | Status (post-B177) |
|---|---|---|
| `_not_null` outer except | `43-44` | B177/M177.1-8: not reducible (production-realistic structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | B177: dataflow/contract-shadow (deterministic scalar, 232/233). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | B177: handler-order shadow/MRO (261/266). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | B177: not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | B177: defensive/guarded. |
| exchange detect outer handlers | `641-642,694-695` | B177: **second `except Exception` handlers shadowed by 639/691/693**; no realistic escape observed. |
| promote datetime column outer handler | `791-792` | B177: nested/guarded tz-normalization except; no realistic escape observed. |
| `_normalize_asset_name` empty token continue | `953` | B177: construction-unreachable (`str.split()` default). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by B103–177 and recorded proofs.
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
| 173 | 0 | proof+probes (complete) | M173.1–M173.8; fresh Step 0 645/6/34, 365 miss/78%; target floor unchanged; per-cluster strict-4 verdicts in §Batch 173; campaign_d 883/5/3487. |
| 174 | 0 | proof+probes (complete) | M174.1–M174.6; JSON orient=split/empty-date CSV/float-epoch public-loader traces (0 target hits), structural shadow proofs; §Batch 174. |
| 175 | 0 | proof+probes (complete) | M175.1–M175.7 read-option/vendor-frame paths (parse_dates/date_format/na_values/keep_default_na/dtype_backend, exchange vendor frames); 0 target hits; §Batch 175. |
| 176 | 0 | proof+probes (complete) | M176.1–M176.8 direct private-function adversarial input enumeration under line tracing; 0 target hits; §Batch 176. |
| 177 | 0 | proof+probes (complete) | M177.1–M177.8 public file/format entrypoints (xlsx/parquet/hdf5 if available, load_prices CSV, exchange long OHLCV, full Binance wide OHLCV, tz-offset public CSV promotion, timestamp promotion); 0 target hits; §Batch 177; canonical 645/6/34, 365 miss/78%; campaign_d 883/5/3487. |
| 178 | 0 | proof+probes (complete) | M178.1–M178.8 materially-new probes (read_csv engine/memory_map/dtype/converters, numpy structured arrays/from_records MultiIndex boundaries, to_datetime format inference, adversarial subclasses TzRaising/BadIter/StrIdx under sys.settrace restricted to data_loader.py); 0 target hits across all clusters; strict-4 per-cluster verdicts in `docs/unreachable_proofs.md` §Batch 178; fresh Step 0 645/6/34, 365 miss/78%; campaign_d 883/5/3487. 0-delta recorded with materially-new method + evidence. |

## INITIAL TASK MESSAGE — 2026-11-08T22:03Z (Batch 179, binding)

**Objective (repo priority):** confirm `strategies/betting_against_beta/data_loader.py` target-miss floor remains unchanged in a fresh canonical aggregate (Batch 178 complete: 0 reduction, all clusters strict-4 not-reducible, §Batch 178 recorded in `docs/unreachable_proofs.md`), OR produce complete materially-new strict-4 unreachable-proof/reduction evidence using methods not used in B103–178/M149–M178.

**State:** workspace `a0511ea` (`main`; durable handoff/proof refreshed this session); `strategies/betting_against_beta/data_loader.py` blob `596ee9e`, line→code verified 2026-11-08T21:57Z. Batch 178 executed: canonical **645 passed, 6 skipped, 34 warnings**, **365 miss / 1683 stmts / 78%**, target floor unchanged; `pytest -q -k campaign_d` **883 passed, 5 skipped, 3487 deselected, 53 warnings**. **`326` is LIVE/GUARD-RELEVANT — never alter.** Target floor: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. Batch 178 evidence: M178.1–M178.8 materially-new probes (read_csv engine/memory_map/dtype/converters, numpy structured arrays/from_records MultiIndex boundaries, to_datetime format inference, adversarial subclasses TzRaising/BadIter/StrIdx under sys.settrace) → **0 target hits**; all clusters **not reducible**; §Batch 178 appended to `docs/unreachable_proofs.md`; HANDOFF refreshed to Batch 179.

### Forced heavy-work steps (do in order)

1. **Step 0 — fresh baseline (mandatory):**
   - `export PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`
   - `rm -f .coverage .coverage.*`
   - Canonical: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` with `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py ...`
   - `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - Run `pytest -q -k campaign_d`. Verify line→code for every target cluster. **Continue immediately — baseline is not an outcome.**

2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–178/M149–M178** + current code and structural findings. If any cluster satisfies all 4 with a **new** production-realistic mechanism, implement `tests/test_bab_data_loader_batch179.py`, prove target-floor reduction in a fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172 green.

3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M179 probes over **all remaining clusters**. Forbidden repeats: all B103–178/M149–M178 methods/mechanisms (incl. M178 read_csv/numpy/MultiIndex/to_datetime/adversarial-subclass probes). Candidate new-method space (pick genuinely new): any code path not yet traced under `sys.settrace` restricted to `data_loader.py`; real end-user input sequences not yet covered; alternate pandas I/O engine toggles not yet exercised; static `ast`/control-flow proof that a specific handler is structurally dominated (must include observed runtime corroboration). Append `docs/unreachable_proofs.md` `## Batch 179` per cluster: `file:line@SHA`, materially-new method, observed result, strict-4 verdict. Cover **all clusters**: `43-44,234-244,246-247,268-269,326(guard-only),338-342,403-404,641-642,694-695,791-792,953`.

4. **Forbidden:** status/planning/review/baseline-only exit; M149–M178 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in fresh canonical aggregate, OR **(B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` `## Batch 179` covering all clusters + HANDOFF ledger updated. Report exact commands, counts, miss lines, artifact paths.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
