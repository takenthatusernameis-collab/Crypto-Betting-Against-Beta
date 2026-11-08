# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T15:49Z** @ HEAD `61f639a` (checkpoint). Step 0 rebaseline executed at this SHA; `strategies/betting_against_beta/data_loader.py` unchanged since `e945fde` (line→code stable). Batch 165 Step 0 rebaseline complete @ `61f639a`; heavy work (reduction / per-cluster strict-4 proof) **NOT yet done → rolled into Batch 166**. **Batch 166 initial task message is the ONLY active next-session directive** (see §“INITIAL TASK MESSAGE — 2026-11-08T15:49Z (Batch 166) — BINDING, EXECUTE IMMEDIATELY”). **Repo-name priority = BAB only — `data_loader.py` remaining miss floor.**
>
> **No session is blocked.** All known bottlenecks are routed/resolved (table below). `tests/test_bab_data_loader_batch163.py` does **not** exist (Batch 163 produced 0 delta; no cluster met strict 4 criteria).
>
> **Binding rules (non-negotiable):** Read completely → rebaseline → do heavy work. No status-only, planning-only, review-only, or “floor closed” exit without required heavy work. Every session must produce **measurable heavy work**: (A) miss reduction in a fresh canonical aggregate, **OR** (B) genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster `file:line@SHA`, method, observed result, and strict 4-criteria verdict for **every remaining cluster**. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Measured state (fresh rebaseline, 2026-11-08T15:46Z @ `61f639a`)

- **Branch/SHA:** `main` @ `61f639a` HEAD (checkpoint only). `data_loader.py` unchanged since `e945fde` (line→code stable). `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked files remain — **do not modify/commit them**). `docs/unreachable_proofs.md` is evidence appendix (not a task directive); `HANDOFF.md` is sole durable task directive.
- **Canonical BAB subset (re-verified):** `rm -f .coverage .coverage.* && PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_betting_against_beta*.py tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149}.py` → **632 passed, 6 skipped, 34 warnings**.
- **Coverage (re-verified, same canonical subset):** `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest ...` + `coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing` → **380 miss / 1683 stmts / 77%** (`data_loader.py`). **Target-miss floor clusters all still missing:** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953` (target-floor unchanged). `322` covered; `326` guard-relevant — **preserve semantics**.
- **Guard:** `pytest -q --ignore=tests/test_controller_progress_accounting.py -k campaign_d` → **883 passed, 5 skipped, 3406 deselected, 53 warnings** (campaign_d-sensitive coverage healthy). **Never alter `322,326`.**
- **Deps:** `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib` → pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**.

## Bottlenecks — resolved (no blocked/inefficient sessions)

| # | Bottleneck | Resolution | Status |
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
| 10 | Repeated 0-delta inefficiency | B103–163 executed/measured/proved (M149–M163). No repeat probes of closed mechanisms. 0-delta without materially-new method + recorded evidence = **failed session**. | Routed |
| 11 | HANDOFF internal contradiction / stale SHA refs | Resolved in this refresh @ `61f639a`. B162–B163 marked complete; B165 Step 0 rebaseline complete (632/6/34; 380 miss/77%; campaign_d 883/5/3406); heavy work pending → B166 binding directive. | Resolved |

**No competing handoff files exist.** (`docs/unreachable_proofs.md` = evidence appendix only.)

## Remaining target-miss cluster map (verify line→code @ current SHA every session)

| Cluster | Lines | Status (B103–163 / proofs) |
|---|---|---|
| `_not_null` outer except | `43-44` | Closed (structural) — M150.7/M151.B/C/M161.1/M162.A/C/M163. No production escape. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Closed (dataflow gate) — M150.3/M151.D/M161.2/M162.A/B/F/M163. 216-224 completion ⇒ 232 deterministic ⇒ 233 continue; 245 safe assignment. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Closed (handler-order shadow/MRO) — M150.2/M151.C/M161.3/M162.B/M163. 266 precedes 268; `BABDataError⊂ValueError`; no plain VE/TE escape. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** M161.4; `campaign_d*` green. |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | Closed (IS_OP/explicit-raise) — M150.1/M151.A/B/M161.5/M162.A/M163. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Closed (regex+float+guarded) — M150.4/M151.A/M161.6/M162.A/M163. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Closed for production-realistic frames — M150.5/M151.B/M161.7/M162.D/M163. |
| `_promote_datetime_column` outer handler | `791-792` | Closed (fully guarded) — M150.6/M151.C/M161.8/M162.D/M163. |
| `_normalize_asset_name` empty token continue | `953` | Closed (construction-unreachable) — M150.7/M151.A/B/M161.9/M162.E/M163. `str.split()` default never yields `''`. |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–163 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---:|---|---|
| 148 | `2ba2c8f` | -2 | reduction | 351-352 (`_NonValueErrorFloat`); semantics preserved. |
| 149 | `34f462e` | -2 | reduction | 334-335 (metaclass `__name__` descriptor, M149); semantics preserved. |
| 150 | `1630eda` | 0 | proof | M150.1–M150.7; 31 miss unchanged. |
| 151 | `55010c1` | 0 | proof | M151.A–M151.D. |
| 152 | `52d0d00` | 0 | proof | M152.A–D. |
| 153 | `03fd243` | 0 | proof | M153.A–D (`sys.settrace`). |
| 154 | `dc5294c` | 0 | proof | M154.A–F. |
| 155 | `ec637e9` | 0 | proof | M155.A–E (PEP 669). |
| 156 | `6c488ea` | 0 | proof | M156.A–E (bytecode/ExceptionTable). |
| 157 | `1a80e85` | 0 | proof | M157.A (settrace sweep). |
| 158 | `a522e82` | 0 | proof | M158.A–D. |
| 160 | `52b634b` | 0 | proof | M160.A–G. |
| 161 | `d614cad` | 0 | proof-strengthened | M161.1–M161.9. |
| 162 | `119a018` | 0 | proof | M162.A–F; 0 target hits; no canonical test/prod change. |
| 163 | `6836a26` | 0 | proof | M163.A–E (hypothesis falsification oracle + public loader temp files + structural re-derivation; pandas 3.1.1 nullable/epoch/exchange/OHLCV). 0 target hits; no canonical test/prod change. |
| 164 | `88c8503` | 0 | proof | M164.A–E; 0 target hits; no canonical test/prod change. |
| 165 | `61f639a` | 0 | partial | Step 0 rebaseline complete @ `61f639a` (632/6/34; 380 miss/77%; campaign_d 883/5/3406); target floor unchanged; heavy work (reduction / per-cluster strict-4 proof) pending → Batch 166. |
| 166 | `61f639a` | — | **PENDING (BINDING)** | Execute immediately — directive below. |

## INITIAL TASK MESSAGE — 2026-11-08T15:49Z (Batch 166) — BINDING, EXECUTE IMMEDIATELY

**SHA:** `61f639a` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Fresh rebaseline (Step 0, complete) @ this SHA:** BAB canonical subset **632 passed, 6 skipped, 34 warnings**; `data_loader.py` **380 miss / 1683 stmts / 77%**; target-miss floor clusters still present **`43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`** (target floor unchanged). Guard `campaign_d*` **883 passed, 5 skipped, 3406 deselected**. `tests/test_bab_data_loader_batch166.py` does **not** exist. **No baseline-only/review-only/planning-only/status-only exit. Repo-name priority = BAB only.**

### Mission (binary; heavy work required)

1. **Step 0 — mandatory rebaseline (DONE this session):** `.coverage*` cleaned; canonical BAB subset command run; canonical coverage for `data_loader.py` run; `campaign_d*` guard run; SHA, counts, exact miss list recorded above. Verify line→code for all target clusters before any claim.

2. **Primary (reduction-first):** Re-verify every remaining cluster against strict 4 criteria. **Do not repeat B103-163 methods** (AST/MRO/shadowing; coercer NaT-outcome tables/gate re-derivations; `sys.settrace`/coverage/PEP 669 line events; CPython 3.12 bytecode/ExceptionTable path mapping/source-range feed proofs; coercer output-homogeneity/245 assignment; exchange try enumeration; construction/identity checks; element-contract sampling; production-realistic sweeps; handler-order shadowing; warnings-as-errors traces; expanded coercer/type-surface/public-loader/file-format traces; 234-244 gate re-probes; Unicode asset normalization traces; `np.seterr` epoch edges; pandas option/config sweeps; tz-aware+NaT index mixes; nullable `pd.NA` scalar traces; exchange/promotion frame variants incl empty/whitespace cols; per-cluster strict-4 verdict patterns M161.1–M161.9/M162.A–F/M163.A–E; hypothesis bounded falsification over production-contract scalars already performed in M163.D; M163 public-loader temp-file traces). Focus only on **demonstrably new production-realistic paths** with line-level proof. If any cluster meets strict 4 criteria, add **`tests/test_bab_data_loader_batch166.py`** (semantics-preserving), include in canonical aggregate, verify fresh aggregate shows miss **< 31** for the target floor (or measured reduction). Never alter `322,326`; `campaign_d*` must stay green. Batch148/149 remain in canonical set and must not be deleted/weakened.

3. **Secondary (only if no cluster reduces canonically):** perform **exhaustive materially-new Batch 166 checks** on **all** remaining clusters. For every unresolved cluster, append per-cluster `file:line@SHA`, method, observed result, and strict 4-criteria verdict to `docs/unreachable_proofs.md` §Batch 166. Update this HANDOFF ledger/measured state with actual results.

4. **Materially-new methods to attempt (choose/adapt; must be genuinely new vs B103-163):**
   - **M166.A — `pandas` 3.1.1 `to_datetime`/index coercion with `StringDtype`/`ArrowDtype`-unavailable fallbacks under real CSV object dtypes + `pd.options.mode.copy_on_write` toggles:** exercise production-realistic loader/index-normalization paths where CoW/view/copy behavior changes intermediate assignment outcomes (without pyarrow). Target 234-247/268-269/641-642/694-695/791-792 only with statable paths.
   - **M166.B — DataFrame-subclass/copy constructor edge cases reachable through `pd.read_csv`/public loaders:** if `DataFrame` subclass behavior is preserved by pandas 3.1.1 operations used in target try blocks, test only realistic subclass scenarios that could be returned/passed in production; avoid pathological harnesses. Record negative evidence.
   - **M166.C — targeted `Decimal`/`Fraction`/`numpy` scalar subclasses and `__index__`/`__float__` protocol objects that appear in realistic financial CSV/JSON parsing:** test whether any can traverse epoch/index coercion into target except branches with a statable control-flow path (not blind scalar sampling repeats).
   - **M166.D — `load_prices`/`load_returns` multi-asset pivot/stack/unstack realistic error paths:** construct realistic wide/long price frames where exchange-format detection, date promotion, and index normalization interact; trace target lines under public entrypoints.
   - **M166.E — if A–D produce a concrete candidate only:** line-level proof and strict 4 criteria; otherwise record negative evidence with method details (no generic restatement). If no reduction is possible, also explicitly identify which specific production API/behavior change would be required for any cluster and record it as a non-actionable external dependency note (no semantic change).

5. **Forced campaign (no early exit):** For each remaining cluster `(43-44, 234-244, 246-247, 268-269, 326 guard-only, 338-342, 403-404, 641-642, 694-695, 791-792, 953)`: (1) verify file:line @ current SHA; (2) apply strict 4 criteria; (3) reduce canonically **or** record a materially-new-method proof. No cluster may be skipped without a verdict. “Floor closed”/status-only exits are forbidden unless required heavy work is performed.

6. **Forbidden:** status-only, planning-only, review-only, "floor closed" without heavy work, repeat probes/methods from B103-163, semantic changes for coverage, altering `322,326` or weakening/deleting batch148/149 tests, workflow edits (`.github/workflows/*`), committing/pushing unless explicitly requested.

### Required session outcome

**Success =** miss floor reduced in fresh canonical aggregate **OR** complete per-cluster strict-4-criteria verdicts plus **Batch 166** non-repeat materially-new appendix in `docs/unreachable_proofs.md` covering **all** remaining clusters **plus** updated `HANDOFF.md` ledger/measured state with actual results. Anything less is failure.

**BEGIN HEAVY WORK NOW.****

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
