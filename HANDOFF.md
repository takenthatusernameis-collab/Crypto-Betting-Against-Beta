# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T16:40Z** @ HEAD `ca2f160` (checkpoint). Step 0 rebaseline re-verified this session (632 passed, 6 skipped, 34 warnings; 380 miss/1683/77%; campaign_d 883/5/3406). `strategies/betting_against_beta/data_loader.py` unchanged since `e945fde` (line→code stable). Batch 168 complete (0 delta; M168.A–H recorded). Batch 169 verified state-only (no reduction, no new probe added yet). **Batch 170 initial task message is the ONLY active next-session directive** (see §“INITIAL TASK MESSAGE — 2026-11-08T16:40Z (Batch 170) — BINDING, EXECUTE IMMEDIATELY”). **Repo-name priority = BAB only — `data_loader.py` remaining target-miss floor.**
>
> **No session is blocked.** All known bottlenecks are routed/resolved (table below). `tests/test_bab_data_loader_batch168.py` does **not** exist (Batch 168 produced 0 delta; no cluster met strict 4 criteria). `docs/unreachable_proofs.md` contains Batch 168 evidence (appendix only; not a task directive).
>
> **Binding rules (non-negotiable):** Read completely → rebaseline → do heavy work. No status-only, planning-only, review-only, or “floor closed” exit without required heavy work. Every session must produce **measurable heavy work**: (A) miss reduction in a fresh canonical aggregate, **OR** (B) genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster `file:line@SHA`, method, observed result, and strict 4-criteria verdict for **every remaining cluster**. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened.**

## Measured state (fresh rebaseline, 2026-11-08T16:40Z @ `ca2f160`)

- **Branch/SHA:** `main` @ `ca2f160` HEAD (checkpoint only). `data_loader.py` unchanged since `e945fde` (line→code stable). `.gitignore` ignores `probe*`/`debug*`/`diag*` (historical tracked files remain — **do not modify/commit them**). `docs/unreachable_proofs.md` = evidence appendix only; `HANDOFF.md` = sole durable task directive.
- **Canonical BAB subset (re-verified):** `rm -f .coverage .coverage.* && PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py tests/test_betting_against_beta*.py tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149}.py` → **632 passed, 6 skipped, 34 warnings**.
- **Coverage (re-verified, same canonical subset):** `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest ...` + `coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing` → **380 miss / 1683 stmts / 77%** (`data_loader.py`, canonical subset). **Target-miss floor clusters still present:** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. `322` covered; `326` guard-relevant — **preserve semantics**.
- **Guard:** `pytest -q --ignore=tests/test_controller_progress_accounting.py -k campaign_d` → **883 passed, 5 skipped, 3406 deselected, 53 warnings** (campaign_d-sensitive coverage healthy). **Never alter `322,326`.**
- **Deps (this session):** installed to `/home/runner/work/_temp/kilo-tmp/pylib` (pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**). Use `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`.

## Bottlenecks — resolved (no blocked/inefficient sessions)

| # | Bottleneck | Resolution | Status |
|---|---|---|---|
| 1 | Scratch/probe clutter | `.gitignore` ignores `diag*`, `_recon_cov.py`, `debug_beta*`, `probe*`; never commit probes. | Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. **Never touch `.github/workflows/*`.** | Routed |
| 3 | Deps fragility | Install/use deps in `/home/runner/work/_temp/kilo-tmp/pylib`; set PATH+PYTHONPATH. | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage. | Routed |
| 5 | Coverage path filtering | `--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='strategies/betting_against_beta/data_loader.py'`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/call sites; handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Direct canonical helper calls, real shapes, tight scoped monkeypatches/subclasses; verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve inspect/caller behavior and campaign_d behavior. **Never alter `322,326`.** | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96,148,149** (no 70,75,90-92,94). Batch148+149 retained. Step 0 command is authoritative. | Routed |
| 10 | Repeated 0-delta inefficiency | B103–168 executed/measured/proved (M149–M168). No repeat probes of closed mechanisms. 0-delta without materially-new method + recorded evidence = **failed session**. | Routed |
| 11 | HANDOFF stale/binding drift | Resolved this refresh @ `ca2f160`. Batch 168 complete (632/6/34; 380 miss/77%; campaign_d 883/5/3406; M168 evidence in proofs). Batch 169 binding directive below. | Resolved |

**No competing handoff files exist.** (`docs/unreachable_proofs.md` = evidence appendix only.)

## Remaining target-miss cluster map (verify line→code @ current SHA every session)

| Cluster | Lines | Status (B103–168 / proofs) |
|---|---|---|
| `_not_null` outer except | `43-44` | Closed (structural) — M150.7/M151.B/C/M161.1/M162.A/C/M163/M168.A. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Closed (dataflow gate/contract) — M150.3/M151.D/M161.2/M162.A/B/F/M163/M168.B-D. 232 same deterministic coercer; 234-244 unreachable under live contract. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Closed (handler-order shadow/MRO) — M150.2/M151.C/M161.3/M162.B/M163/M168.D. |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD-RELEVANT — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise guards | `338-342` | Closed (explicit-raise/guarded) — M150.1/M151.A/B/M161.5/M162.A/M163/M168.A. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Closed (regex+float+guarded) — M150.4/M151.A/M161.6/M162.A/M163/M168.E. |
| `_detect_and_normalize_exchange_format` outer handlers | `641-642,694-695` | Closed for production-realistic frames — M150.5/M151.B/M161.7/M162.D/M163/M168.F-G. |
| `_promote_datetime_column` outer handler | `791-792` | Closed (fully guarded) — M150.6/M151.C/M161.8/M162.D/M163/M168.F-G. |
| `_normalize_asset_name` empty token continue | `953` | Closed (construction-unreachable) — M150.7/M151.A/B/M161.9/M162.E/M163/M168.H. |

## Strict 4 criteria (required for any miss-reduction claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by batches 103–168 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path with plausible pandas/library behavior (no semantic change, no pathological harness).
4. A statable control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | SHA | Delta | Result | Notes |
|---|---|---|---|---|
| 148 | `2ba2c8f` | -2 | reduction | 351-352; semantics preserved. |
| 149 | `34f462e` | -2 | reduction | 334-335 (M149); semantics preserved. |
| 150–164 | — | 0 | proof | M150–M164 recorded in proofs/history. |
| 165 | `61f639a` | 0 | partial→closed | Step 0 rebaseline; heavy work rolled to 166+. |
| 166 | `61f639a` | 0 | proof | directive executed historically; see proofs/HANDOFF history. |
| 167 | `61f639a` | 0 | proof | see proofs/HANDOFF history. |
| 168 | `ca2f160` | 0 | proof | M168.A–H (nullable extension scalars, np.datetime64 NaT gate, tz+NaT mixes, epoch edges, public loader temp CSV exchange/OHLCV, detect/promote edge frames, asset-name edges). 0 target hits; no canonical test/prod change. |
| 169 | `ca2f160` | 0 | state-only | Step 0 rebaseline re-verified (632/6/34; 380 miss/77%; campaign_d 883/5/3406). Heavy work (reduction or materially-new proof) **not yet executed** — rolled to Batch 170. |
| 170 | `ca2f160` (start) | — | **PENDING (BINDING)** | Execute immediately — directive below. |

## INITIAL TASK MESSAGE — 2026-11-08T16:40Z (Batch 170) — BINDING, EXECUTE IMMEDIATELY

**SHA (start):** `ca2f160` (`data_loader.py` unchanged since `e945fde`; line→code stable). **Measured baseline (Step 0 reference):** BAB canonical subset **632 passed, 6 skipped, 34 warnings**; `data_loader.py` **380 miss / 1683 stmts / 77%** (canonical subset report); target-miss floor clusters present `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`; guard `campaign_d*` **883 passed, 5 skipped, 3406 deselected**. `tests/test_bab_data_loader_batch169.py` does **not** exist. `tests/test_bab_data_loader_batch170.py` does **not** exist. **No baseline-only/review-only/planning-only/status-only exit. Repo-name priority = BAB only.**

### Mission (binary; heavy work required)

1. **Step 0 mandatory rebaseline (fresh):** run canonical BAB subset and coverage commands above; run `campaign_d*` guard; verify line→code for all target clusters at current SHA. Record any drift.

2. **Primary (reduction-first):** re-verify every remaining cluster against strict 4 criteria; if any cluster now satisfies all 4, add `tests/test_bab_data_loader_batch170.py` with production-realistic coverage, run fresh canonical aggregate, and verify target-floor reduction. **Never alter `322,326`; `campaign_d*` must stay green; batch148/149 retained.**

3. **Secondary (only if no reduction):** perform exhaustive **materially-new** Batch 170 checks on **all remaining clusters** (do not repeat B103–168/M149–M168 methods). For each cluster append to `docs/unreachable_proofs.md` §Batch 170: `file:line@SHA`, materially-new method, observed result, and strict-4 verdict. Update this HANDOFF ledger/measured state.

4. **Forced campaign:** every cluster `(43-44,234-244,246-247,268-269,326 guard-only,338-342,403-404,641-642,694-695,791-792,953)` gets verify + strict-4 + reduce **or** materially-new proof. **No skip without verdict. No "floor closed"/status-only exit without heavy work.** If a cluster is claimed structurally dead, you must run at least one materially-new probe (different entrypoint, different monkeypatch vector, different pandas subclass, different dtype mix) and record the negative result with strict-4 verdict before marking it closed.

5. **Forbidden:** status/planning/review-only exits; repeat B103–168 methods; semantic changes for coverage; altering `322,326`; weakening/deleting batch148/149; workflow edits; commit/push unless explicitly requested.

### Required session outcome

Success = miss floor reduced in fresh canonical aggregate **OR** complete per-cluster strict-4 verdicts plus Batch 170 materially-new appendix covering all remaining clusters plus updated HANDOFF ledger/measured state. Anything less is failure.

**BEGIN HEAVY WORK NOW.**
## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
