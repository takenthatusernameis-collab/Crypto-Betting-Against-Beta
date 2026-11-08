# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T12:58Z** (this session) @ `a522e82`. Batch 157 recorded 2026-11-08T11:44Z @ `1a80e85`; Batch 158 executed 2026-11-08T12:58Z @ `a522e82` (0 delta, materially-new proof work M158.A-D recorded in `docs/unreachable_proofs.md` §Batch 158); Batch 159 initial task message is the **only active next-session directive** (§“INITIAL TASK MESSAGE — 2026-11-08T12:58Z (Batch 159)”). Step 0 rebaseline re-verified 2026-11-08T12:58Z @ `a522e82`: canonical **1473/0/17, 31 miss / 1683 stmts / 98%** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`, guard `campaign_d*` 44/5 green. `data_loader.py` unchanged since `e945fde` (line→code stable). **Repo-name priority = BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor.**
>
> **Status:** B148 (-2, 351-352) and B149 (-2, 334-335) reduced misses with semantics preserved. B150–158 produced 0-delta, materially-new proof work (M150-M158) recorded in `docs/unreachable_proofs.md`. B158 (this session, `a522e82`) re-verified fresh canonical baseline (1473/0/17, **31 miss / 1683 stmts / 98%**) and added §Batch 158 (M158.A — **CPython 3.12 ExceptionTable source-range feed analysis for 268-269 handler 4800**: only fed by offsets 248-272 `df.index` access/STORE_FAST/NOP on `pd.DataFrame` and 4786-4792/4794-4800 tail; range 261-265 has inner handler raising only `BABDataError` — no feeding range can deliver plain non-`BABDataError` `ValueError/TypeError` under production-realistic input; M158.B — pandas 3.1.1 exact 245 coerced-shape/`ensure_index` contract: bare `df.index=`/`Index`/`DatetimeIndex`/`ensure_index` OK for `[NaT, tz-aware Timestamp]` survivors; M158.C — public-loader CSV/JSON NaT/null/empty-date trace, 0 target hits; M158.D — construction/structural rechecks). **0 target-line hits / no satisfiable production path.** 234-247 dataflow+assignment-closed; 268-269 bytecode-source-range+conversion-closed; 338-342/403-404/43-44/641-695/791-792/953 structural/guarded/construction-closed. **No miss reduction achieved (strict-4-criteria miss reduction requires a semantics-preserving production-realistic path; none demonstrated).** This is not a permission to idle. “Floor closed”/status-only exits are forbidden unless the session performs required heavy work.
>
> **READ THIS FIRST — ACTIVE DIRECTIVE:** Jump to **“INITIAL TASK MESSAGE — 2026-11-08T12:58Z (Batch 159) — BINDING, EXECUTE IMMEDIATELY”** below. It is the only next-session task. Do not summarize, plan, or declare the floor closed without completing its heavy-work requirements.
>
> **Binding rules:** Read completely, rebaseline, then do heavy work. No status-only, planning-only, review-only, or “floor closed” exit without required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Measured state (fresh rebaseline, 2026-11-08T12:58Z @ `a522e82`)

- **Branch/SHA:** `main` @ `1a80e85`. Batch 156 work recorded at `6c488ea`; Batch 157 executed 2026-11-08T11:44Z @ `1a80e85` (0 delta, §Batch 157 recorded in `docs/unreachable_proofs.md`); Batch 158 pending at `1a80e85`. `data_loader.py` unchanged since `e945fde`; `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**). `HANDOFF.md` and `docs/unreachable_proofs.md` carry Batch 157 work; `tests/test_bab_data_loader_batch157.py` does not exist (no reduction found — correctly not added).
- **Canonical aggregate:** **1473 passed, 0 failed, 17 skipped, 109 warnings** (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned).
- **Coverage:** **31 miss / 1683 stmts / 98%**. Missing: `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`.
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. `322` covered; `326` remains guard-relevant — **preserve semantics**.
- **Deps:** `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` → pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**.

## Bottlenecks — routed (verified 2026-11-08T11:44Z; no blocked sessions)

| # | Bottleneck | Route | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; install there only if missing. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326` semantics.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained. Step 0 command is authoritative. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–157 executed/measured/proved (M149-M157). No repeat probes of closed mechanisms. 0-delta without new method + recorded evidence = failed session. | Routed |

**No session is blocked. No competing handoff files exist** (`HANDOFF.md` is sole; `docs/unreachable_proofs.md` is evidence appendix, not a task directive). All 10 bottlenecks routed.

## Remaining 31 — cluster map (verify line→code each session)

| Cluster | Lines | Status (B103–151 / proofs) |
|---|---|---|
| `_not_null` outer except | `43-44` | Proof-closed (structural) — M150.7/M151.B/C. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Proof-closed (determinism/continue) — M150.3/M151.D. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Proof-closed (handler-order/MRO) — M150.2/M151.C. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | Proof-closed (IS_OP/explicit-raise) — M150.1/M151.A/B. 334-335 closed B149. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Proof-closed (regex+float+guarded) — M150.4/M151.A. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Proof-closed for production-realistic frames — M150.5/M151.B. |
| `_promote_datetime_column` outer handler | `791-792` | Proof-closed (fully guarded) — M150.6/M151.C. |
| `_normalize_asset_name` empty token continue | `953` | Proof-closed (construction-unreachable) — M150.7/M151.A/B. |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–151 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 136 | `377a70c` | -1 | reduction | 35/1683, `322` covered. |
| 137 | `0d00688` | 0 | proof | Hypothesis/public-loader/nullable evidence. |
| 138 | `c3e44a3` | 0 | proof | Public loader trace, MRO/coercer-contract evidence. |
| 139 | `24db195` | 0 | heavy proof | AST/MRO/coercer static proofs; pandas 3.1.1 traces. |
| 140 | `ed0fda2` | 0 | confirmed | 1496/0/17, 35/1683, guard 44/5. |
| 141 | `d97339d` | 0 | appendix | Cross-module contract audit + AST caller map. |
| 142 | `2a272a7` | 0 | appendix | File-path loaders + nullable/Categorical/MultiIndex/np-dtype + Hypothesis fuzz. |
| 143 | `5af2dda` | 0 | confirmed | 1467/0/17, 35/1683, guard 44/5. |
| 145 | `2848cf7` | 0 | appendix | IO/parsing seams, ladder-state, exception-type boundaries. |
| 146 | `88ef267` | 0 | appendix | Parse variants, 268-269 control-flow trace, inspect/caller gate audit. |
| 147 | `55b7cdb` | 0 | appendix+lead | 351-352 runtime trace hit (probe removed). |
| 148 | `2ba2c8f` | -2 | reduction | **351-352 reduced** (`_NonValueErrorFloat`); semantics preserved. 1470/0/17, **33/1683**. |
| 149 | `34f462e` | -2 | reduction | **334-335 reduced** (metaclass `__name__` descriptor, M149); semantics preserved. 1473/0/17, **31/1683**. |
| 150 | `1630eda` | 0 | proof | M150.1–M150.7 per-cluster strict 4-criteria; 31 miss unchanged. |
| 151 | `55010c1` (proof appendix recorded) | 0 | proof | M151.A–M151.D (bytecode/520-object fuzz/branch trace/coercer determinism); 31 miss unchanged. |
| 152 | `52d0d00` | 0 | proof | M152.A–D (AST exhaustive-handler/shadowing for try@113/598/648; coercer→index dataflow gate contradiction 216-224⇒232; targeted runtime trace NaT-string hit 227-233,245 only; strict re-audit). 31 miss unchanged. |
| 153 | `03fd243` | 0 | proof | M153.A–D (sys.settrace frame-level line-hit proof: 268-269 handler-order/MRO dead — plain VE/TE converted to BABDataError at 261-265, intercepted by 266 before 268, `BABDataError⊂ValueError` shadows 268; all-unparseable object index trace hit 261-267 not 268-269). 234-244/246-247 dataflow-gate contradiction — 216-224 completion requires coercer success on all `idx` elements ⇒ same deterministic coercer at 232 cannot raise on same `idx` ⇒ `continue` 233 always; NaT-mixed index trace hit 227-233,245 not 234-244/246-247). 31 miss unchanged. |
| 154 | `dc5294c` | 0 | proof | M154.A-F (AST/MRO shadowing 268-269; coercer NaT-outcome table extending M152.B for 234-247; exchange try enumeration; construction/identity checks; element contract sampling). 31 miss unchanged. |
| 155 | `ec637e9` | 0 | proof | M155.A-E (PEP 669 `sys.monitoring` oracle; public-loader/DataFrame-subclass/wrapper sweep; epoch/coercer boundary sweep; stateful-element 216→224→227→232 gate probe). 0 miss-cluster hits; 31 miss unchanged. |
| 156 | `6c488ea` | 0 | proof | M156.A-E (CPython 3.12 bytecode/ExceptionTable path map for 216-247/248-271; coercer output homogeneity + 245 assignment contract; 216→224→227→232 gate re-derivation; `BABDataError⊂ValueError` MRO/construction corroboration). 31 miss unchanged. |

| 157 | `1a80e85` | 0 | proof | M157.A (`sys.settrace` frame-level production-realistic sweep): 0 target-line hits. 31 miss unchanged. |
| 158 | `a522e82` | 0 | proof | M158.A-D (ExceptionTable source-range feed for 268-269 handler 4800; pandas 3.1.1 exact 245 coerced-shape/`ensure_index` contract; public-loader CSV/JSON NaT trace; construction/structural rechecks): 0 target-line hits; no feeding range delivers plain non-`BABDataError` VE/TE. 31 miss unchanged. |

## INITIAL TASK MESSAGE — 2026-11-08T12:58Z (Batch 159) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `a522e82` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Fresh baseline (2026-11-08T12:58Z, re-verified @ `a522e82`):** 1473/0/17, **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`, guard 44/5 (deps via `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`: pytest 9.2.0, coverage 7.17.2, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.15). **Batch 158 executed (M158.A-D) — recorded in `docs/unreachable_proofs.md` §Batch 158**; `tests/test_bab_data_loader_batch158.py` correctly does NOT exist (no reduction found). Batch 159 has **not** been executed. No baseline-only/review-only/planning-only/status-only exit. This is the only active task message.

### Mission (binary; heavy work required)

1. **Primary (start here, reduction-first):** Re-verify every remaining cluster `43-44,234-244,246-247,268-269,338-342,403-404,641-642,694-695,791-792` (and `326` guard-only) at current SHA against strict 4 criteria. **Do not repeat B103-158 methods** (AST/MRO/shadowing; coercer NaT-outcome tables/gate re-derivations; `sys.settrace`/coverage/PEP 669 line events over same helper/public/subclass/epoch/stateful/CSV-JSON/file-format sweeps; CPython 3.12 bytecode/ExceptionTable path mapping and ExceptionTable *source-range feed* analysis for same `_normalize_index` ranges; coercer output-homogeneity/245 homogeneous-list assignment and pandas 3.1.1 index-constructor/`ensure_index` contract for the same 245 coerced shape; exchange try enumeration; construction/identity checks; element contract sampling; M157.A/M158.C production-realistic/public-loader sweeps; M158.D unicode/epoch construction rechecks). Focus only on demonstrably new production-realistic paths with line-level proof:
   - **234-247 (highest remaining ambiguity):** find a production-realistic pandas 3.1.1 / `pd.DataFrame` / `DatetimeIndex` / file-format path where (i) 227 loop completes and 245 `df.index = coerced` raises `Exception` for *coercer-produced* values (not pathological harness), OR (ii) 243 re-raises for a same-`idx` element after 232 exception *and* 224-completion is somehow satisfiable — both currently gate-closed (M158.B shows bare assignment/`ensure_index` safe for exact survivor shape). Prove with a concrete DataFrame/index/dtype/file-format path and hit lines, or record a materially-new proof.
   - **268-269:** only with a production-realistic plain `ValueError/TypeError` escaping try@113 *not* converted to `BABDataError` by 261-265 and *not* intercepted by 266 — AND delivered by a feeding bytecode range not covered by M158.A (248-272 is df.index access; 261-265 inner handler converts; tail ranges are plumbing). Any claim must identify the exact exception-producing bytecode offset/range and a concrete production-realistic trigger.
   - **641-642/694-695/791-792/403-404/338-342/43-44/953:** only with demonstrably new production-realistic mechanism (not re-proving inner-guard swallowing/construction/re-raise-ordering).
   If any cluster meets strict 4 criteria, add `tests/test_bab_data_loader_batch159.py` (semantics-preserving), include it in the canonical aggregate, and verify fresh aggregate shows miss **< 31**. **Never alter `322,326` semantics; `campaign_d*` must stay 44/5 green.**

2. **Secondary (only if no cluster reduces canonically):** perform exhaustive **materially-new Batch 159** checks on all remaining clusters. Methods must differ from B103-158/M149-M158. Examples that qualify only if genuinely new in effect: instrument pandas 3.1.1 `NDFrame.__setattr__`/`_mgr` index-replacement path *through* `_normalize_index` with a production-realistic `load_*`/DataFrame input to prove 245 cannot raise for coercer-produced survivor lists (beyond M158.B constructor contract); a complete AST+ExceptionTable proof enumerating every `raise`/implicit-exception site in bytecode offsets 248-4736 and showing no plain non-`BABDataError` VE/TE reaches 4800 (extends M158.A from feeding ranges to all enclosed sites with concrete type outcomes); or a real-format fuzz (CSV/JSON/JSONL with `np.nan`/`pd.NA`/`NaT`-string/epoch-mixed tokens parsed by pandas readers, not manual object-index construction) that traces into 216-247 and demonstrates gate satisfaction/impossibility with recorded line hits. For every unresolved cluster, append per-cluster file:line @ SHA, method, observed result, and strict 4-criteria verdict to `docs/unreachable_proofs.md` §Batch 159. Update this HANDOFF ledger with measured results.

3. **Forbidden:** status-only, planning-only, review-only, “floor closed” without heavy work, repeat probes/methods from B103-158, semantic changes for coverage, altering `322,326` or weakening/deleting batch148/149 tests, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested.

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

Reconcile if different from 31 miss / 1473/0/17 / guard 44/5. Once `tests/test_bab_data_loader_batch159.py` exists (only if reduction found), add it to coverage/canonical runs.

### Forced campaign (no early exit)

For each remaining cluster: (1) verify file:line at current SHA; (2) apply strict 4 criteria; (3) reduce canonically or record materially-new-method proof. No cluster may be skipped without a verdict.

### Required session outcome

**Success =** miss **< 31** in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus Batch158 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF.md/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
