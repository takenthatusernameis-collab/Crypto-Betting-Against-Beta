# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (2026-11-08T10:35Z @ `dc5294c`; Step 0 rebaseline verified 2026-11-08T10:35Z — canonical 1473/0/17, coverage **31 miss / 1683 stmts / 98%** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`, guard `campaign_d*` 44/5 green). `data_loader.py` unchanged since `e945fde` (line→code stable). Repo-name priority = **BAB only — `strategies/betting_against_beta/data_loader.py` remaining miss floor.**
>
> **Status:** B148 (-2, 351-352) and B149 (-2, 334-335) reduced misses with semantics preserved. B150–154 produced 0-delta, materially-new proof work (M150-M154) recorded in `docs/unreachable_proofs.md`. B154 (this session, `dc5294c`) verified fresh canonical baseline, installed deps to `/home/runner/work/_temp/kilo-tmp/pylib`, and added §Batch 154 (M154.A-F): AST/MRO re-verification showing 261-265 always raises `BABDataError` and 266 intercepts before 268 (`BABDataError⊂ValueError`, no broad `Exception` on try@113) → 268-269 structurally dead; coercer NaT-outcome table extending M152.B (`'NaT'`/`np.datetime64 NaT` return NaT → 233 continue; `pd.NaT`/`None`/nan raise → 224 never completes so 227 never reached; 245 list assignment safe) → 234-247 dataflow-closed; exchange try enumeration and construction/identity checks for remaining clusters. **No miss reduction achieved (strict-4-criteria miss reduction requires a semantics-preserving production-realistic path; none demonstrated).** This is not a permission to idle. “Floor closed”/status-only exits are forbidden unless the session performs required heavy work.
>
> **Binding rules:** Read completely, rebaseline, then do heavy work. No status-only, planning-only, review-only, or “floor closed” exit without required heavy work. Every session must produce **measurable heavy work**: miss reduction in a fresh canonical aggregate **OR** genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster file:line, method, observed result, and strict 4-criteria verdict. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Measured state (fresh rebaseline, 2026-11-08T10:09Z @ `52d0d00`)

- **Branch/SHA:** `main` @ `52d0d00`. `data_loader.py` unchanged since `e945fde`. `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked probe/debug files remain — **do not modify/commit them**). `HANDOFF.md` and `docs/unreachable_proofs.md` carry Batch 152 work in this session.
- **Canonical aggregate:** **1473 passed, 0 failed, 17 skipped, 109 warnings** (fresh, `--rcfile=/dev/null`, `.coverage*` cleaned).
- **Coverage:** **31 miss / 1683 stmts / 98%**. Missing: `43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953`.
- **Guard (`campaign_d*`):** **44 passed, 5 warnings**. `322` covered; `326` remains guard-relevant — **preserve semantics**.
- **Deps:** `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` → pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**.

## Bottlenecks — routed (verified 2026-11-08T10:09Z)

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
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–152 executed/measured/proved. No repeat probes of closed mechanisms. 0-delta without new method + recorded evidence = failed session. | Routed |

No session is blocked. All 10 bottlenecks are routed.

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

## INITIAL TASK MESSAGE — 2026-11-08T10:35Z (Batch 156) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `dc5294c` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Fresh baseline (2026-11-08T10:35Z):** 1473/0/17, **31 miss / 1683 stmts / 98%**, missing `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`, guard 44/5 (deps via `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`: pytest 9.2.0, coverage 7.17.2, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, hypothesis 6.170.15). **Batch 154 materially-new proof work (M154.A-F) is recorded in `docs/unreachable_proofs.md` §Batch 154** (AST/MRO shadowing for 268-269, coercer NaT-outcome table extending M152.B for 234-247, exchange try enumeration, construction/identity checks, element contract sampling). No baseline-only/review-only/planning-only/status-only exit. This is the only active task message.

### Mission (binary; heavy work required)

1. **Primary (start here, reduction-first):** Re-verify every remaining cluster `43-44,234-244,246-247,268-269,338-342,403-404,641-642,694-695,791-792` (and `326` guard-only) at current SHA against strict 4 criteria. **Do not repeat B103-154 methods.** Focus only on demonstrably new production-realistic paths with line-level proof: (a) 234-247 — M154.B shows NaT-returning elements (`'NaT'`, `np.datetime64 NaT`) cause `continue` at 233 and NaT/None/nan-raising elements prevent 224 completion; only a *different* coercer outcome for the *same* `idx` element between 220 and 232 could help, but coercer is pure and `idx` unchanged/immutable — attempt only with a pandas 3.1.1 index/object mutation or coercer-non-determinism mechanism proven on a production-realistic `pd.DataFrame`/index; if found, add `tests/test_bab_data_loader_batch154.py` with semantics preserved and verify in fresh canonical aggregate. (b) 268-269 — M154.A shows 261-265 always raises `BABDataError` and 266 intercepts before 268; attempt only with a production-realistic path raising plain `ValueError/TypeError` outside BABDataError conversion before 266. (c) 641-642/694-695/791-792/403-404/338-342/43-44/953 — attempt only with a demonstrably new production-realistic mechanism. **Never alter `322,326` semantics; `campaign_d*` must stay 44/5 green.**
2. **Secondary (only if no cluster reduces canonically):** perform exhaustive **materially-new Batch 155** checks on all remaining clusters — methods must differ from B103-154/M149-M154 (e.g., `sys.monitoring`/PEP 669 line events or a different tracer boundary over a targeted helper invocation; pandas 3.1.1 C-level index/coercer behavior not captured by prior AST+Python-level traces; source-level liveness/dead-store analysis on the exact 216→224→225→227→232→245 path with runtime contradiction; or production-realistic DataFrame subclass/`_constructor`/array-like wrapper paths through public loaders not previously exercised with line-level proof). For every unresolved cluster, append per-cluster file:line @ SHA, method, observed result, and strict 4-criteria verdict to `docs/unreachable_proofs.md` §Batch 155. Update this HANDOFF ledger with measured results.
3. **Forbidden:** status-only, planning-only, review-only, “floor closed” without heavy work, repeat probes/methods from B103-154, semantic changes for coverage, altering `322,326` or weakening/deleting batch148/149 tests, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested.

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

Reconcile if different from 31 miss / 1473/0/17 / guard 44/5. Once `tests/test_bab_data_loader_batch154.py` exists (only if reduction found), add it to coverage/canonical runs.

### Forced campaign (no early exit)

For each remaining cluster: (1) verify file:line at current SHA; (2) apply strict 4 criteria; (3) reduce canonically or record materially-new-method proof. No cluster may be skipped without a verdict.

### Required session outcome

**Success =** miss **< 31** in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus Batch155 non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering all remaining clusters plus updated HANDOFF.md/ledger with measured results. Anything less is failure.

**BEGIN HEAVY WORK NOW.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
