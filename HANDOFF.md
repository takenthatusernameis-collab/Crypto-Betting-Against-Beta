# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-08T19:41:46Z** @ `63dc952` (`main`, clean worktree). **Repo-name priority = Betting Against Beta only** — next heavy work targets `strategies/betting_against_beta/data_loader.py` remaining miss floor.
>
> **Authoritative Step 0 baseline (re-verified 2026-11-08T18:59Z; next agent MUST rerun fresh before any claim):** env `PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `rm -f .coverage .coverage.*`; canonical coverage `--rcfile=/dev/null --source=strategies.betting_against_beta`, report `--include='*/strategies/betting_against_beta/data_loader.py'`. Canonical subset incl. batch172 (retained): `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` → **645 passed, 6 skipped, 34 warnings** (~58s). `data_loader.py`: **365 miss / 1683 stmts / 78%**. **Target-miss floor UNCHANGED (all present; verify line→code @ current SHA before edits): `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`**. `campaign_d*` guard: **883 passed, 5 skipped, 3487 deselected**. Historical baseline excl. batch172: **632/6/34, 380 miss/77%**.
>
> **BINDING — execute immediately. BATCH 173 is reduction-first heavy work.** Run fresh Step 0, then reduction attempts and/or materially-new proof probes across **every remaining cluster** until a measurable outcome. **Forbidden exits:** status-only, planning-only, review-only, baseline-only, or “closed/unreachable/no mechanism” without the required heavy work and evidence.

## INITIAL TASK MESSAGE — 2026-11-08T19:41:46Z (Batch 173, binding)

**Objective (repo priority):** reduce the `strategies/betting_against_beta/data_loader.py` target-miss floor in a fresh canonical aggregate, OR produce complete materially-new strict-4 unreachable-proof evidence for every remaining cluster.

**State:** `main@63dc952` clean; `data_loader.py` line→code verified at current SHA (target lines present; `326` guard intact). **`326` is LIVE/GUARD-RELEVANT — never alter.** Target floor: `43-44,234-244,246-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`.

### Forced heavy-work steps (do in order)

1. **Step 0 — fresh baseline (mandatory):**
   - `export PATH=/home/runner/work/_temp/kilo-tmp/pylib/bin:$PATH PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`
   - `rm -f .coverage .coverage.*`
   - Canonical: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` with `coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py ...`
   - `coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - Run `pytest -q -k campaign_d` guard. Verify line→code for every target cluster. **Continue immediately — baseline is not an outcome.**

2. **Reduction sprint (primary):** for each cluster, re-check strict 4 criteria against **B103–172/M149–M172** + current code. If any satisfies all 4, implement `tests/test_bab_data_loader_batch173.py` with **production-realistic** inputs only (no semantic production change, no pathological harness). Prove target-floor reduction in a fresh canonical aggregate. Keep `322,326`; keep `campaign_d*` green; keep batch148/149/172 green.

3. **Proof probes (mandatory if no reduction):** exhaustive **materially-new** M173 probes over **all remaining clusters**. Forbidden repeats: all B103–172/M149–M172 methods/mechanisms. New-only examples only if genuinely applicable: real `read_json`/`to_json`/pickle round-trips through public BAB loaders; `dtype_backend`/`na_filter`/`parse_dates`/`date_format`/engine effects on real CSV paths; extension-array scalar boxing in unmocked BAB `apply`/`pd.to_datetime`; inspect/stack-sensitive paths **without altering 322,326**; long-format exchange records reaching uncovered branches; production-plausible pandas-internal raises inside currently-covered try bodies escaping to `641-642/694-695/791-792`. Append `docs/unreachable_proofs.md` `## Batch 173` per cluster: `file:line@SHA`, materially-new method, observed result, strict-4 verdict. Cover **all clusters**: `43-44,234-244,246-247,268-269,326(guard-only),338-342,403-404,641-642,694-695,791-792,953`.

4. **Forbidden:** status/planning/review/baseline-only exit; M149–M172 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in fresh canonical aggregate, OR **(B)** complete per-cluster strict-4 verdicts + `docs/unreachable_proofs.md` §Batch 173 covering all clusters + HANDOFF ledger updated. Report exact commands, counts, miss lines, artifact paths.

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
| 10 | Repeated 0-delta inefficiency | B103–172/M149–M172 executed. 0-delta without materially-new method + recorded evidence = failed session. |

**No competing handoff files exist.** `docs/unreachable_proofs.md` is evidence appendix only.

## Remaining target-miss clusters (verify line→code @ SHA)

| Cluster | Lines | Status |
|---|---|---|
| `_not_null` outer except | `43-44` | Proof-closed (B103–172); re-check before claiming unreachable. |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Proof-closed (dataflow/contract); deterministic coercer blocks 234-244 in exercised realistic paths. |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Proof-closed (handler-order/shadow). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | Proof-closed. |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Proof-closed/defensive. |
| exchange detect outer handlers | `641-642,694-695` | No reduction in recent batches; production-realistic escape not demonstrated. |
| promote datetime column outer handler | `791-792` | No reduction; defensive. |
| `_normalize_asset_name` empty token continue | `953` | Proof-closed (construction-unreachable). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA.
2. Mechanism not disproven by B103–172 and recorded proofs.
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
| 173 | **PENDING — EXECUTE NOW (binding, carried to next session)** | binding | Fresh Step 0 → reduction or materially-new proofs for all clusters. Next agent MUST run Step 0 baseline before any claim; 0-delta without materially-new method + recorded evidence = failed session. |

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document.
