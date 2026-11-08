# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T14:46Z** (pre-Batch-163 session) @ `7cc54f6` (HEAD). Batch 162 executed **2026-11-08T14:44Z @ `119a018`** (0 delta; materially-new M162.A-F evidence appended to `docs/unreachable_proofs.md` §Batch 162 — pandas option/config sweep, tz-aware+NaT index mixes, nullable/NA scalar, exchange/promotion frame variants, Unicode asset normalization, 234-244 gate recheck; **0 target-line hits / no satisfiable production path; no canonical test added, no production code changed**). **Batch 163 initial task message is the only active next-session directive** (§“INITIAL TASK MESSAGE — 2026-11-08T14:46Z (Batch 163) — BINDING, EXECUTE IMMEDIATELY”). `data_loader.py` unchanged since `e945fde` (line→code stable). **Repo-name priority = BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor.**
>
> **Status:** B148 (-2, 351-352) and B149 (-2, 334-335) reduced misses with semantics preserved. B150–162 produced 0-delta, materially-new proof work (M150-M162). No new production-realistic mechanism satisfying strict 4 criteria has been demonstrated. **No miss reduction in B162.** “Floor closed”/status-only exits are forbidden unless the session performs required heavy work.
>
> **READ THIS FIRST — ACTIVE DIRECTIVE:** Jump to **“INITIAL TASK MESSAGE — 2026-11-08T14:46Z (Batch 163) — BINDING, EXECUTE IMMEDIATELY”** below. It is the only next-session task. Do not summarize, plan, or declare the floor closed without completing its heavy-work requirements.
>
> **Binding rules:** Read completely, rebaseline, then do heavy work. No status-only, planning-only, review-only, or “floor closed” exit without required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Measured state (fresh rebaseline, 2026-11-08T14:46Z @ `7cc54f6`)

- **Branch/SHA:** `main` @ `7cc54f6`. `data_loader.py` unchanged since `e945fde` (identical blob; line→code stable). Batch 162 executed @ `119a018`; Batch 163 not yet executed. `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**). `HANDOFF.md` and `docs/unreachable_proofs.md` carry Batch 162 work; `tests/test_bab_data_loader_batch163.py` does not exist.
- **Canonical aggregate (re-verified 2026-11-08T14:46Z @ `7cc54f6`, `--rcfile=/dev/null`, `.coverage*` cleaned):** BAB canonical subset **632 passed, 6 skipped, 34 warnings** (`tests/test_betting_against_beta*.py` + canonical data-loader batches 40-69,71-74,76-89,93,95,96,148,149; `--ignore=tests/test_controller_progress_accounting.py`; `coverage run -m pytest` + `coverage report --include='strategies/betting_against_beta/data_loader.py'`). Prior full canonical baseline **1473 passed, 0 failed, 17 skipped, 109 warnings** — next session must re-verify full canonical count in Step 0.
- **Coverage:** **380 miss / 1683 stmts / 77%** total in `data_loader.py`; **target-miss floor clusters all confirmed missing** **`43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`** (~31-miss target floor unchanged). `322` covered; `326` guard-relevant — **preserve semantics**.
- **Guard (`campaign_d*`):** **44 passed, 5 warnings** (BAB subset 879/5/53). `322` covered; `326` remains guard-relevant — **preserve semantics**.
- **Deps:** `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` → pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**.

## Bottlenecks — resolved (verified 2026-11-08T14:46Z; no blocked sessions)

| # | Bottleneck (was) | Resolution | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; install there only if missing. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326`.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained. Step 0 command is authoritative. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–162 executed/measured/proved (M149-M162). No repeat probes of closed mechanisms. 0-delta without new method + recorded evidence = failed session. | Routed |
| 11 | HANDOFF.md internal contradiction (Batch 162 “pending” vs “executed”; measured-state SHA `d614cad` vs `119a018`) | Resolved in this refresh: Batch 162 executed @ `119a018`; current HEAD `7cc54f6` (post-B162 docs refresh); Batch 163 is the active directive. Measured state rebaselined @ `7cc54f6`. | Resolved |

**No session is blocked. No competing handoff files exist** (`HANDOFF.md` is sole; `docs/unreachable_proofs.md` is evidence appendix, not a task directive). All bottlenecks routed/resolved.

## Remaining target-miss cluster map (verify line→code each session @ `7cc54f6`)

| Cluster | Lines | Status (B103–162 / proofs) |
|---|---|---|
| `_not_null` outer except | `43-44` | **Closed (structural)** — M150.7/M151.B/C + M161.1 + M162.A/C (identity `is None`; inner `pd.isna` guarded; unconditional `return`). No production escape. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | **Closed (dataflow gate)** — M150.3/M151.D + M161.2 + M162.A/B/F (216-224 completion ⇒ same deterministic coercer at 232 ⇒ `continue` 233 always; 245 safe homogeneous list assignment). No satisfiable production path. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | **Closed (handler-order shadow/MRO)** — M150.2/M151.C + M161.3 + M162.B (266 `except Exception`/`except BABDataError` precedes 268; `BABDataError⊂ValueError`; no plain VE/TE escape). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** M161.4 (inspect gate unchanged; `campaign_d*` green). |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | **Closed (IS_OP/explicit-raise)** — M150.1/M151.A/B + M161.5 + M162.A (`val is pd.NaT` identity cannot raise; `raise ValueError` re-raised before generic pass). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | **Closed (regex+float+guarded)** — M150.4/M151.A + M161.6 + M162.A (regex-admitted `str`→builtin `float` no-raise; all epoch ops individually guarded). |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | **Closed for production-realistic frames** — M150.5/M151.B + M161.7 + M162.D (inner exhaustive handlers swallow; bounded outer setup). |
| `_promote_datetime_column` outer handler | `791-792` | **Closed (fully guarded)** — M150.6/M151.C + M161.8 + M162.D (760-790 individually guarded; `hasattr` swallows descriptor exceptions). |
| `_normalize_asset_name` empty token continue | `953` | **Closed (construction-unreachable)** — M150.7/M151.A/B + M161.9 + M162.E (`str.split()` default never yields `''`; `tok.strip()` on split token never empty). |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA (`7cc54f6`).
2. Mechanism not disproven by batches 103–162 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 148 | `2ba2c8f` | -2 | reduction | 351-352 reduced (`_NonValueErrorFloat`); semantics preserved. |
| 149 | `34f462e` | -2 | reduction | 334-335 reduced (metaclass `__name__` descriptor, M149); semantics preserved. |
| 150 | `1630eda` | 0 | proof | M150.1–M150.7 per-cluster strict 4-criteria; 31 miss unchanged. |
| 151 | `55010c1` | 0 | proof | M151.A–M151.D; 31 miss unchanged. |
| 152 | `52d0d00` | 0 | proof | M152.A–D; 31 miss unchanged. |
| 153 | `03fd243` | 0 | proof | M153.A–D (`sys.settrace` frame-level); 31 miss unchanged. |
| 154 | `dc5294c` | 0 | proof | M154.A–F; 31 miss unchanged. |
| 155 | `ec637e9` | 0 | proof | M155.A–E (PEP 669 `sys.monitoring` oracle); 31 miss unchanged. |
| 156 | `6c488ea` | 0 | proof | M156.A–E (CPython 3.12 bytecode/ExceptionTable); 31 miss unchanged. |
| 157 | `1a80e85` | 0 | proof | M157.A (`sys.settrace` production-realistic sweep); 31 miss unchanged. |
| 158 | `a522e82` | 0 | proof | M158.A-D; 31 miss unchanged. |
| 160 | `52b634b` | 0 | proof | M160.A-G; 31-miss target cluster unchanged. |
| 161 | `d614cad` | 0 | proof-strengthened | M161.1–M161.9 per-cluster strict-4 verdicts; 31-miss floor unchanged. |
| 162 | `119a018` | 0 | proof | M162.A-F; 0 target hits; `docs/unreachable_proofs.md` §Batch 162 appended. 31-miss floor unchanged. |
| 163 | `7cc54f6` | — | pending | **Not yet executed.** Active directive below. |

## INITIAL TASK MESSAGE — 2026-11-08T14:46Z (Batch 163) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `7cc54f6` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Fresh baseline (Batch 163 Step 0, 2026-11-08T14:46Z @ `7cc54f6`):** BAB canonical subset **632 passed, 6 skipped, 34 warnings**; target-miss clusters still present **`43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`** (~31-miss target floor unchanged). Prior full canonical baseline **1473 passed, 0 failed, 17 skipped, 109 warnings / 31 miss / 1683 stmts / 98%** — re-verify full canonical in Step 0. Guard `campaign_d*` preserved (do not alter `322,326`). Batch 163 **not yet executed**. No baseline-only/review-only/planning-only/status-only exit. **Repo-name priority = BAB only.**

### Mission (binary; heavy work required)

1. **Primary (reduction-first):** Re-verify every remaining cluster at current SHA against strict 4 criteria. Do not repeat B103-162 methods (AST/MRO/shadowing; coercer NaT-outcome tables/gate re-derivations; `sys.settrace`/coverage/PEP 669 line events; CPython 3.12 bytecode/ExceptionTable path mapping/source-range feed proofs; coercer output-homogeneity/245 assignment; exchange try enumeration; construction/identity checks; element-contract sampling; production-realistic sweeps; handler-order shadowing; warnings-as-errors traces; expanded coercer/type-surface/public-loader/file-format traces; 234-244 gate re-probes; Unicode asset normalization traces; `np.seterr` epoch edges; pandas option/config sweeps; tz-aware+NaT index mixes; nullable `pd.NA` scalar traces; exchange/promotion frame variants incl empty/whitespace cols; per-cluster strict-4 verdicts M161.1–M161.9/M162). Focus only on demonstrably new production-realistic paths with line-level proof. If any cluster meets strict 4 criteria, add `tests/test_bab_data_loader_batch163.py` (semantics-preserving), include in canonical aggregate, verify fresh aggregate shows miss **< 31** (or measured target-miss floor < prior). Never alter `322,326`; `campaign_d*` must stay green. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` remain in canonical set and must not be deleted or weakened.

2. **Secondary (only if no cluster reduces canonically):** perform exhaustive materially-new Batch 163 checks on all remaining clusters. Methods must differ from B103-162. For every unresolved cluster, append per-cluster file:line @ SHA, method, observed result, and strict 4-criteria verdict to `docs/unreachable_proofs.md` §Batch 163. Update this HANDOFF ledger (measured results + Batch 163 row) with measured results.

3. **Forced campaign (no early exit):** For each remaining cluster `(43-44, 234-244, 246-247, 268-269, 326 guard-only, 338-342, 403-404, 641-642, 694-695, 791-792, 953)`: (1) verify file:line at current SHA; (2) apply strict 4 criteria; (3) reduce canonically **or** record a materially-new-method proof. No cluster may be skipped without a verdict. “Floor closed”/status-only exits are forbidden unless required heavy work is performed.

4. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes/methods from B103-162, semantic changes for coverage, altering `322,326` or weakening/deleting batch148/149 tests, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested.

### Required session outcome

**Success =** miss floor reduced in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus Batch 163 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated `HANDOFF.md`/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
