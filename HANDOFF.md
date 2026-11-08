# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF — canonical, no competing handoff files.** Refreshed **2026-11-08T17:48:55Z** @ workspace state (includes uncommitted `HANDOFF.md`, `docs/unreachable_proofs.md` §Batch 172, and `tests/test_bab_data_loader_batch172.py`; **no production semantic changes**). `strategies/betting_against_beta/data_loader.py` unchanged since `e945fde` (line→code stable for all target clusters; verified at current SHA `d5f195f`). **Last fresh Step 0 rebaseline (2026-11-08T17:48:55Z, authoritative commands, fresh `.coverage*`):** BAB canonical subset (explicit list, batches 40-69,71-74,76-89,93,95,96,148,149; **no batch172**) **632 passed, 6 skipped, 34 warnings**; `data_loader.py` **380 miss / 1683 stmts / 77%**; target-miss floor **`43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953` all still present**. `campaign_d*` guard **883 passed, 5 skipped, 3419 deselected**. Batch 172 probes added as `tests/test_bab_data_loader_batch172.py` (13 tests): aggregate including batch172 **645 passed, 6 skipped, 34 warnings**, `data_loader.py` **365 miss / 78% overall**, **target floor unchanged** (0 reduction of specified clusters). `docs/unreachable_proofs.md` contains **§Batch 172** (M172.1–M172.7, per-cluster strict-4 verdicts). **Repo-name priority = BAB only — next heavy work targets `strategies/betting_against_beta/data_loader.py` remaining miss floor.**
>
> **No session is blocked. No inefficient bottlenecks remain** (see table). The only risk to progress is a future agent exiting without heavy work; this document forbids that.
>
> **ACTIVE NEXT-SESSION DIRECTIVE (execute immediately, no alternatives): BATCH 173 — reduction-first heavy campaign.** Batch 172 is complete and recorded (no reduction). The next session **must not** summarize, plan, or rebaseline-and-stop. It **must** run Step 0 (decide whether to include batch172 in canonical list per repo convention; record choice), then spend the session on reduction attempts and/or materially-new proof probes across **every remaining cluster** until it produces a measurable outcome.
>
> **Binding rules (non-negotiable):** Read completely → rebaseline → do heavy work. **No status-only, planning-only, review-only, baseline-only, or “floor closed / unreachable / no mechanism” exit** without required heavy work. Every session must produce **measurable heavy work**: (A) miss reduction in a fresh canonical aggregate, **OR** (B) genuinely new, non-repeat, high-confidence unreachable-proof evidence in `docs/unreachable_proofs.md` using a **materially new method** with per-cluster `file:line@SHA`, method, observed result, and strict 4-criteria verdict for **every remaining cluster**. “No new mechanism exists” is invalid unless you actually ran materially-new checks and recorded negative evidence. **Never change production semantics solely for coverage. Never alter `322,326` semantics. Never touch `.github/workflows/*`. Never commit/push unless explicitly requested. `tests/test_bab_data_loader_batch148.py` and `tests/test_bab_data_loader_batch149.py` must remain in the canonical set and must not be deleted or weakened. Do not modify/commit tracked historical `probe*`/`debug*` files. Keep batch172 tests passing if retained.**

## Measured state (fresh rebaseline, **2026-11-08T17:48:55Z** @ `d5f195f` workspace; `data_loader.py` @ `e945fde`, line-stable)

- **Branch/SHA:** `main` HEAD `63c969a7`. `strategies/betting_against_beta/data_loader.py` last changed `e945fde` — **line→code stable** for all target clusters (verified 2026-11-08T17:35Z). Batch 171 completed: M171.A–F, 0 target hits, proofs §Batch 171 appended. `docs/unreachable_proofs.md` = evidence appendix only; `HANDOFF.md` = sole durable task directive.
- **Canonical BAB subset (re-verified):** `cd <repo> && files=(tests/test_betting_against_beta*.py $(for n in $(seq 40 69) 71 72 73 74 76 77 78 79 80 81 82 83 84 85 86 87 88 89 93 95 96 148 149; do echo tests/test_bab_data_loader_batch${n}.py; done)); rm -f .coverage .coverage.* && PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py "${files[@]}"` → **632 passed, 6 skipped, 34 warnings**.
- **Coverage (re-verified, same file list, fresh `.coverage*`):** `... coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest ...` + `... coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing` → **380 miss / 1683 stmts / 77%**. **Target-miss floor still present:** `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. `322` covered in production context elsewhere; **`326` guard-relevant — preserve semantics**.
- **Guard:** `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib python3 -m pytest -q --ignore=tests/test_controller_progress_accounting.py -k campaign_d` → **883 passed, 5 skipped, 3406 deselected, 53 warnings**. **Never alter `322,326`.**
- **Deps/env:** `/home/runner/work/_temp/kilo-tmp/pylib` (pytest 9.2.0, coverage 7.17.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, hypothesis 6.170.15; **no pyarrow/pytables/fastparquet**). Bash brace expansion for `batch{40..69}` can fail in some shells; the explicit `seq`/list command above is authoritative.


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
| 11 | HANDOFF stale/binding drift | **Resolved this refresh @ `9d8b7b1` (2026-11-08T17:37Z).** Batch 171 complete (632/6/34; 380 miss/77%; campaign_d 883/5/3406; M171.A–F in proofs §Batch 171). **Batch 172 binding directive is active below — next session must do heavy work.** | Resolved |

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
| 168 | `ca2f160` | 0 | proof | M168.A–H; 0 target hits; no canonical test/prod change. |
| 169 | `ca2f160` | 0 | state-only | Step 0 re-verified; heavy work rolled to 170. |
| 170 | `ba7feed` workspace | 0 | proof | M170.1–M170.5 (scalar-contract NaT gate probe hit 245 not 234-244/246-247; non-campaign_d NaT scalar frames; nullable string index/public temp CSV exchange loader; handler-shadow reconfirmation; construction checks). 0 target hits; no canonical test/prod change. Appendix in `docs/unreachable_proofs.md` §Batch 170. |
| 171 | `63c969a7` (workspace) | 0 | proof | M171.A–F (NaT-string scalar contract, actual `_normalize_index` trace showing 232 returns NaT→233 continue so 234-244 never reached; 245 assignment ok for normal/subclass/tz-aware; NaT CSV/long loader paths; detect/promote edge frames; np.datetime64 NaT units s-D/M/Y/h/m; DataFrame subclass/tz-aware+NaT index). 0 target hits; no canonical test/prod change. Appendix in `docs/unreachable_proofs.md` §Batch 171. |
| 172 | workspace @`97a9846` | 0 | proof+probes (no reduction) | M172.1–M172.7: DTI tz-op TypeError subclass, exchange epoch-ms/epoch-string + narrow `pd.to_datetime`/coercer/copy injection, tz-aware promote + `Timestamp.tz_convert` injection, epoch unit `OverflowError` fallback, `np.datetime64('NaT','s')` public normalize, `_not_null` sentinels, repeated-separator construction, public CSV empty-date/epoch-ms loaders. 13 tests added (`tests/test_bab_data_loader_batch172.py`); canonical baseline unchanged **632/6/34, 380 miss/77%**; aggregate incl. batch172 **645/6/34, 365 miss/78% overall, target floor unchanged**. `campaign_d*` green. `docs/unreachable_proofs.md` §Batch 172. |
| 173 | — | 0 (pending) | **BINDING — ACTIVE** | **Next session MUST execute Batch 173 heavy work immediately** (reduction attempt or M173.* materially-new evidence for every remaining cluster). No baseline-only exit. |

## INITIAL TASK MESSAGE — 2026-11-08T17:48:55Z (Batch 173) — BINDING, EXECUTE IMMEDIATELY

**Repo:** `Crypto-Betting-Against-Beta`. **Priority:** `strategies/betting_against_beta/data_loader.py` target-miss floor only (repo-name priority: BAB). **Workspace state:** uncommitted `HANDOFF.md`, `docs/unreachable_proofs.md` §Batch 172, `tests/test_bab_data_loader_batch172.py` (13 tests, keep passing); `data_loader.py` semantic SHA stable at `e945fde` (verify line→code). **Fresh Step 0 rebaseline just executed (2026-11-08T17:48:55Z):** canonical BAB subset **632 passed, 6 skipped, 34 warnings**; `data_loader.py` **380 miss / 1683 stmts / 77%**; target-miss floor **`43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953` all still present**; `campaign_d*` **883 passed, 5 skipped, 3419 deselected**. Batch 172/M172.1–M172.7 complete (0 reduction of target floor); aggregate incl. batch172 **645/6/34, 365 miss/78% overall** but same target misses. **No blockers. No baseline-only exit.**

### Forced heavy-work campaign (do not exit until measurable)

1. **Step 0 (mandatory, fresh):** rerun canonical BAB subset + coverage + `campaign_d*` guard using the authoritative explicit file-list commands in §Measured state (`rm -f .coverage .coverage.*`; `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `--rcfile=/dev/null --source=strategies.betting_against_beta`; report `--include='strategies/betting_against_beta/data_loader.py' --show-missing`). **Decide/record** whether to include `tests/test_bab_data_loader_batch172.py` in canonical list (repo convention has been adding prior batch tests; be explicit). Verify line→code for every target cluster at current SHA. Record drift. **Immediately continue.**
2. **Primary — reduction sprint:** for each remaining cluster, re-check strict 4 criteria against **B103–172 / M149–M172** and current code. If any cluster satisfies all 4, implement `tests/test_bab_data_loader_batch173.py` with **production-realistic** `pd.DataFrame`/index/dtype/column-label/file-format inputs (no semantic change, no pathological harness), run fresh canonical aggregate, and prove target-floor reduction. Keep `322,326` unchanged; keep `campaign_d*` green; keep batch148/149/172.
3. **Secondary — mandatory if no reduction:** run **exhaustive, materially-new** Batch 173 probes over **all remaining clusters**. Forbidden repeats: every B103–172/M149–M172 method, including M172.1 DTI tz-op TypeError subclass, M172.2 epoch-ms/epoch-string + `pd.to_datetime`/coercer/`DataFrame.copy` injection, M172.3 tz-aware promote + `Timestamp.tz_convert` injection, M172.4 epoch unit `OverflowError` fallback, M172.5 `np.datetime64('NaT','s')` public normalize/sentinels, M172.6 separator construction, M172.7 empty-date/epoch-ms CSV loaders. New mechanisms must differ materially (examples only if genuinely new): real `read_json`/`to_json`/pickle round-trips through public BAB loaders with production-plausible index/column shapes; `dtype_backend`/`na_filter`/`parse_dates`/`date_format`/engine selection effects on real CSV paths; extension-array scalar boxing during `DataFrame.apply`/`pd.to_datetime` in unmocked BAB code; inspect-frame/stack-sensitive paths **without altering 322,326 semantics**; long-format exchange records where symbol/date/price promotion reaches different BAB branches than M172; or targeted monkeypatch of *pandas internals called by unmocked BAB code* that can raise inside currently-covered try bodies to escape to 641-642/694-695/791-792 only if production-plausible. For **each cluster** append to `docs/unreachable_proofs.md` `## Batch 173 — ...` with `file:line@SHA`, materially-new method, observed result, strict-4 verdict.
4. **Coverage checklist (all required):** `43-44`, `234-244,246-247`, `268-269`, `326` (guard-only, do not alter), `338-342`, `403-404`, `641-642,694-695`, `791-792`, `953`. No skip without verdict. Any “closed/dead” claim requires at least one new probe + recorded negative evidence.
5. **Forbidden:** status/planning/review/baseline-only exits; repeating M149–M172 methods; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; `.github/workflows/*` edits; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Required measurable outcome (session fails otherwise)

**Success only if:** (A) miss floor reduced in a fresh canonical aggregate, **or** (B) complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` §Batch 173 materially-new appendix covering **all remaining clusters** + updated HANDOFF ledger/measured state. Report exact commands, counts, miss lines, and artifact paths.

**BEGIN HEAVY WORK NOW. DO NOT STOP AFTER BASELINE.**

## Historical detail

Detailed batch appendices remain in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
