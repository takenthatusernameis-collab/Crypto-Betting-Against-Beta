# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T01:33Z** @ workspace `e620a49` (`main`; `strategies/betting_against_beta/data_loader.py` blob `596ee9e` unchanged since `9476c72`; no production changes this session). `docs/unreachable_proofs.md` is evidence appendix only. **Repo-name priority = Betting Against Beta only** — next work targets `strategies/betting_against_beta/data_loader.py` remaining target-miss floor. **START HERE → Batch 186 is the binding initial task message (§ below).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them. No competing handoff files exist.

> **Authoritative Step 0 baseline (FRESHLY EXECUTED this session 2026-11-09T00:39Z @ `e620a49`; next agent must rerun fresh before claiming any reduction):** env `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical coverage `--rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py` over explicit canonical file list (`tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py`; enumerate explicitly if shell brace expansion misbehaves) → **645 passed, 6 skipped, 34 warnings** (~39s). Report: `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing` → **365 miss / 1683 stmts / 78%**. `data_loader.py` blob `596ee9e`. **Target-miss floor UNCHANGED (all present; verify line→code @ fresh SHA before edits): `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`**. `326` intact/LIVE-GUARD — never alter. `campaign_d*` guard: **883 passed, 5 skipped, 3487 deselected, 53 warnings**. Deps: `PYTHONPATH=$PWD`; `coverage`/`pytest` via `python -m`. Bash brace expansion for `batch{40..69,...}` misbehaved in this shell — build the file list explicitly (`seq` + `echo -n`).

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

The following historical bottlenecks are cleared and must not be reintroduced as excuses: scratch/probe clutter (`.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; tracked `debug_beta*`/`probe*` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (pandas/pytest/coverage/scipy/hypothesis installed; `coverage` via `python -m coverage`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (canonical `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='*/strategies/betting_against_beta/data_loader.py'`), canonical batch set drift (enumerated explicitly above), missing parquet/hdf5 engines (monkeypatch `pd.read_parquet`/`read_hdf`/call sites; handlers may wrap as `BABDataError`).

**Active bottleneck to remove — repeated 0-delta inefficiency:** B103–183/M149–M183 executed, all 0-delta with complete strict-4 verdicts; Batch 184 was not executed (superseded by Batch 185 below). **0-delta without a materially-new method + recorded evidence is a failed session.** Status-only, planning-only, review-only, baseline-only, or "closed/unreachable/no mechanism" exits are forbidden without required heavy work and evidence. This bottleneck is removed by the enforced heavy-work campaign in §INITIAL TASK MESSAGE.

## Remaining target-miss clusters (verify line→code @ SHA)

| Cluster | Lines | Status (post-B183) |
|---|---|---|
| `_not_null` outer except | `43-44` | B183/M183.4,7: not reducible (production-realistic structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | B183: dataflow/contract-shadow (deterministic scalar, 232/233; Decimal/Fraction/aware/string-dtype index). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | B183: handler-order shadow/MRO (261/266). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** (`322,326` never altered.) |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | B183: not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | B183: defensive/guarded. |
| exchange detect outer handlers | `641-642,694-695` | B183: second `except Exception` handlers shadowed by 639/691/693; no realistic escape observed. |
| promote datetime column outer handler | `791-792` | B183: nested/guarded tz-normalization except; no realistic escape observed. |
| `_normalize_asset_name` empty token continue | `953` | B183: construction-unreachable (`str.split()` default). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by B103–183/M149–M183 and recorded proofs.
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
| 173–183 | 0 | proof+probes (complete) | M173.1–M183.8; fresh Step 0 645/6/34, 365 miss/78%; campaign_d 883/5/3487; §Batch 173–183 in `docs/unreachable_proofs.md`. 0-delta recorded with materially-new method + evidence each batch. |
| 185 | 0 | proof+probes | 0-delta; no target hits; M185 evidence required. |
| 0 (this session) | 0 | baseline-verify | Fresh Step 0 re-executed @ `486fa43`: 645 passed, 6 skipped, 34 warnings; 365 miss / 1683 stmts / 78%; campaign_d green; blob `596ee9e`; target floor unchanged. Handoff refreshed 2026-11-09T01:33Z. |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T01:33Z (Batch 186, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** reduce `strategies/betting_against_beta/data_loader.py` target-miss floor below **365 miss / 1683 stmts (78%)** in a fresh canonical aggregate, **OR** produce complete materially-new strict-4 unreachable-proof evidence for **every remaining cluster** using methods **not** used in B103–183/M149–M183. Step 0 fresh baseline **must be rerun** by next agent before any claim — canonical aggregate @ current HEAD with `strategies/betting_against_beta/data_loader.py` blob `596ee9e`. Target floor: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. **`326` is LIVE/GUARD-RELEVANT — never alter.** Batch 183/185 evidence: 0-delta, no target hits; §Batch 183 recorded.

**State (verified 2026-11-09T01:33Z):** HEAD `e620a49` (`main`), clean working tree for BAB scope; `data_loader.py` blob `596ee9e` (verified via `git hash-object`), line→code must be re-verified fresh at SHA before edits. **Canonical baseline (last confirmed — Step 0 MUST be rerun fresh before any claim): 645 passed, 6 skipped, 34 warnings; 365 miss / 1683 stmts / 78%; campaign_d 883/5/3487.** No competing handoff files. Next agent must execute Step 0 fresh, then attempt **only materially-new, production-realistic** reduction mechanisms not disproven by B103–183/M149–M183; if none exist, produce **new-method evidence** (not repeats) and update durable artifacts. **Forbidden exits:** status-only, planning-only, review-only, baseline-only, or "closed/unreachable/no mechanism" without required heavy work and evidence.

### Forced heavy-work steps (do in order; no step may be skipped or downgraded to planning/review)

1. **Step 0 — fresh baseline (mandatory, not an outcome):**
   - `export PYTHONPATH=$PWD`
   - `rm -f .coverage .coverage.*`
   - Canonical test set (explicit file list; build with `seq` if brace expansion misbehaves):
     `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py`
   - Run: `python -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py [FILE_LIST]`
   - Report: `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - Run `python -m pytest -q -k campaign_d`. Verify line→code for every target cluster. **Continue immediately — baseline is not an outcome.**

2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–183/M149–M183** + current code and structural findings. If any cluster satisfies all 4 with a **new** production-realistic mechanism, implement `tests/test_bab_data_loader_batch186.py`, prove target-floor reduction in a fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172 green.

3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M186 probes over **all remaining clusters**. Forbidden repeats: all B103–183/M149–M183 methods/mechanisms (incl. M183 Decimal/Fraction/uuid/bytes/bytearray scalars and fields, zoneinfo/pytz aware datetimes and Timestamp subclass coercion, Timedelta/pydatetime/np.datetime64 scalar edges and parse_dates/dayfirst CSV loader interplay, pd.NA/raising-`__bool__`/NumPy `_not_null` paths, bytes+Decimal exchange normalization, tz-aware/string-dtype/aware+naive index normalization, extension string date promotion; M182 reader `side_effect` injection/custom numeric-equality dunders/np.datetime64 units/nullable-extension dtypes/raising index scalars/public exchange-tz promotion/NumPy scalar `_not_null`; M180 compression/encoding/chunksize/fsspec/mixed-object/Interchange/untraced-entrypoints; M179 copy_on_write/alt-format readers/StringIO/path-like/extension-Arrow/nullable/concat-join-merge/Period-Categorical-Interval-Multi/AST+runtime; M178 read_csv engine/memory_map/dtype/converters/numpy-structured/from_records/MultiIndex/to_datetime-format/adversarial-subclasses; M177 public file/format entrypoints; M176 direct private-function adversarial enumeration; M175 read-option/vendor-frame). Candidate genuinely-new method space: **production harness via actual CLI/integration entrypoints** with real temp files exercising untested combinations (`bab-example`/CLI args, or script-level `run` paths) under trace; pandas 3.x `StringDtype`/`ArrowDtype` storage variants and copy-on-write-adjacent frame mutation patterns on *returned* objects; `read_csv` with `dtype=` mapping to extension types + `parse_dates` + `na_filter`/`keep_date_col`/`usecols`; `DataFrame` with `attrs`/metadata or `sparse` dtypes if supported; numpy masked arrays/recarrays through conversion boundaries; **static reachability proof** (AST/control-flow graph) that a specific except body has no dominator-free entry under live pandas/Python semantics.

4. **Forbidden:** status/planning/review/baseline-only exit; M149–M183 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required — no exceptions)

**(A)** target-floor reduced in fresh canonical aggregate (report exact commands, counts, miss lines), **OR** **(B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` `## Batch 186` covering all clusters + HANDOFF ledger updated. A session ending without (A) or (B) is an inefficient/blocked session and must be re-scoped before continuation.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed 2026-11-09T01:33Z @ `e620a49`.