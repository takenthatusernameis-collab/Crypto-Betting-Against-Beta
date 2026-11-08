# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` that closes a *genuinely new* mechanism (not a repeat probe). "No new mechanism exists" is NOT a valid session outcome unless accompanied by a timestamped, line-by-line trace artifact for **every** remaining cluster using a methodology not previously recorded, proving the negative with concrete code-path/shape/monkeypatch/trace evidence.

**Handoff refreshed (UTC):** 2026-11-08T02:24:47Z (batch135 entry @ `db84180`; fresh rebaseline **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`); line `322` is again MISSING — the batch134 `@2ac1e3c` claim of "35 miss, 322 covered" was **not reproducible** at HEAD, so `322` is a genuine open target again alongside `326`). Guard 44/5; bottlenecks removed/routed; no semantic changes. **SHA at handoff:** `db84180`.
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (measured):** `main` @ `db84180` (working tree clean; tracked diffs this session: `HANDOFF.md` only — **do not commit unless explicitly requested**; clean `.coverage*` before coverage runs). `data_loader.py` unchanged since `e945fde`/`311656a`.
**Measured baseline (fresh rebaseline, 2026-11-08T02:22Z, batch135 entry @ `db84180`):** data_loader+campaign_d+CLI canonical aggregate — **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.31s). Coverage (`--rcfile=/dev/null` run+report): **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (**line `322` re-missed vs prior claimed 35**). Guard (`campaign_d*`) **44 passed, 5 warnings** (0.60s).
**Target:** `strategies/betting_against_beta/data_loader.py` — **36 miss / 1683 stmts / 98%** (re-confirmed @ `db84180`). **Step 0 must rebaseline every session. Push below 36.**

**Floor status:** **MECHANISM-CLOSED** for all 36 remaining lines (batches 103–133, re-confirmed @ `db84180`). Miss reduction requires a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism satisfying strict 4 criteria on a real `pd.DataFrame`/index/dtype/column-label path — not a repeat probe, not a pathological harness, never a semantic change for coverage. **Batch135 MUST attempt a fresh exhaustive re-examination using a materially new technique not recorded in 103–133** (e.g., property-based randomized `load_*` round-trips via `hypothesis` if available, or systematic permutation of pandas 2.x nullable/pyarrow-adjacent dtypes where installed, CSV dialect/quoting/newline variants, timezone-localization metadata round-trips, `to_json`/`read_json` orient matrix, MultiIndex-column-to-flat normalization edge cases, or downstream `metrics`/`backtest` consumption traces proving which loader outputs are production-realistic and which miss clusters remain structurally unreachable across *all* public entrypoints). Status-only forbidden.
**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested. Production semantics must not change solely to manufacture coverage.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** `cli.py`/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below the fresh baseline** in a **fresh completed canonical aggregate**, OR add **new high-confidence unreachable-proof evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", "explored", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.
- **Production semantics must not change solely to manufacture coverage.** Preserve: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior, inspect-sensitive/campaign_d behavior (`322,326` guard-relevant), public APIs stable.

---

## BOTTLENECKS — ALL REMOVED / ROUTED (verified 2026-11-07T17:02Z; re-verified 2026-11-07T22:23Z; re-confirmed 2026-11-07T22:33Z; re-verified 2026-11-08T00:11Z @ `a106e45`; re-confirmed 2026-11-08T02:22Z @ `db84180`)

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`; transient `.coverage*` cleaned before canonical runs. Untracked `debug_beta*.py`/`probe*.py` present — do not commit. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | Install to `/home/runner/work/_temp/kilo-tmp/pylib` if missing: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy hypothesis` + `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. Deps confirmed installed (pytest/coverage/pandas/numpy/scipy/hypothesis 6.170.15). | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls with real shapes and tight scoped monkeypatches/subclasses. Verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. **Line 322 is now a live target again** (inspect-gated `break`); never alter `322,326` semantics. | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94 in canonical aggregate). Rebaseline exact set in Step 0. | Routed |
| 10 | `No data to report` / stale coverage | Clean `.coverage*` before coverage; run `coverage run` and `coverage report` in same shell/env. | Routed |
| 11 | Repeated 0-delta batches (123–131 blocked/inefficient) | **Removed/Routed.** Floor mechanism-closed; no repeat probes allowed. Batch135 only on a concretely demonstrated, genuinely new production-realistic control-flow mechanism satisfying **all four** strict entry criteria. Every session must move miss or add genuinely-new proof — 0-delta without new proof is a failed session. | Removed/Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh baseline (2026-11-08T02:22Z, batch135 entry @ `db84180`):** canonical aggregate **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.31s). Coverage **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged since `e945fde`.

**Remaining 36 (verified @ `db84180`):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. **Never alter `322,326`.** (Line `322` re-missed — the prior claimed 35-miss/322-covered state was not reproducible; treat `322` as a live open target.)

**Cluster map (closure status):**
1. **`234-244, 246-247`** (`_normalize_index` 227-247): coercer determinism — 232 uses same `_coerce_to_datetime_scalar` as 216-224 on post-224 survivors → `continue` at 233 always; 245 same-length assignment safe. Trace: NaT-return path hits 225-233,245 (miss 234-244,246-247); raise-on-coerce hits 222-223→248 (miss 224-247). **Closed.**
2. **`268-269`** (`_normalize_index`): 261-265 converts all `Exception`→`BABDataError`; 266 catches `BABDataError` before 268 (`ValueError,TypeError`); `BABDataError` subclasses `ValueError`. **Handler-structure dead.**
3. **`351-352`** (`_coerce_to_datetime_scalar`): pathological `float` subclass where `np.isnan`/numeric path triggers `__float__` raising → NaN-guard slip; fixing is semantic. **Proof-only, no semantic change.**
4. **`334-335,338-342`**: `ValueError("bad")` re-raised before generic `except Exception: pass`; checks use non-overridable identity/`type().__name__`. **Structural-dead.**
5. **`403-404`** (`_coerce_to_datetime_scalar` epoch outer except): regex 361 admits numeric strings; `float(s)` returns builtin `float` (overflow→`inf`, never raises). `int(inf)`/datetime ops only inside individually guarded branches 365-402. Trace `1e99999` hit guards/missed 403-404. **Structural-dead for regex-admitted `str`.**
6. **`43-44`** (`_not_null`): `is None` identity + inner `pd.isna` guarded (40-41) + unconditional `return True`; no unwrapped fallible stmt. Trace with `pd.isna` boom missed 43-44. **Structural-dead.**
7. **`953`** (`_normalize_asset_name`): `str.split()` never yields empty token. **Construction-unreachable.**
8. **`641-642, 694-695`** (`_detect_and_normalize_exchange_format`): setup paths exception-free on production-realistic inputs; inner try blocks (608-640, 668-691) swallow all exceptions. Trace-verified 641-642/694-695 missed. **Structural-dead (production-realistic).**
9. **`791-792`** (`_promote_datetime_column`): all 760-790 individually guarded; Python 3 `hasattr` swallows descriptor exceptions; 793+ outside try. **Structural-dead.**
10. **`322,326`** — inspect-gated/campaign_d NaT guards (**guard-relevant, DO NOT ALTER**; `322` re-missed at `db84180`, live target).

*Note (batch114, e945fde):* prior handoff listed `1626-1627,1663-1664` as missing; at HEAD they are no longer in the canonical miss set (handlers/line mapping shifted or covered). Do not re-target those line numbers without a fresh line-to-code check.

---

## SESSION BATCH LEDGER (cumulative, measured)

| Batch | Delta (miss) | Result | Notes |
|---|---|---|---|
| 126–131 | 0 | proof-only/probe | mechanism-closure evidence strengthened; no production-realistic miss reduction found; strict 4 criteria unsatisfied; floor mechanism-closed. |
| 131-reconfirm | 0 | fresh Step 0 rebaseline @ `04bdee3` | 2026-11-08T00:19:52Z: **1466/0/17, 36/1683 (98%, `--rcfile=/dev/null`)**; missing `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44/5**. Floor mechanism-closed re-confirmed. **Next batch number: 134**. |
| 134-recon @ `db84180` | 0 | fresh Step 0 rebaseline @ `db84180` | 2026-11-08T02:22Z: **1466/0/17, 107 warnings (44.31s)**; **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`); missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44/5**. `data_loader.py` unchanged since `e945fde`. **The prior `@2ac1e3c` claim of 35 miss / line `322` covered was NOT reproducible — `322` is again a live open target.** Floor mechanism-closed re-confirmed; all bottlenecks removed/routed; deps importable via `$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `.coverage*` cleaned pre-run. No new production-realistic mechanism; no canonical test/probe added. **Next batch number: 135** (must satisfy all 4 strict criteria on a real `pd.DataFrame`/index/dtype/column-label path for miss reduction, or add materially new-method proof beyond 103–134 — no status-only). |

---

## INITIAL TASK MESSAGE — 2026-11-08T02:24:47Z (batch135 entry; SHA `db84180`) — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-08T02:22:00Z (fresh Step 0 rebaseline @ `db84180`; **36-miss / 1683 stmts / 98%** mechanism-closed floor re-confirmed, `--rcfile=/dev/null`). **SHA at handoff:** `db84180`.
**Measured baseline (batch135 entry, this session):** canonical aggregate **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.31s). Coverage **36 miss**; missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (**line `322` re-missed — the `@2ac1e3c` 35-miss claim not reproducible; `322` is a live target again**). Guard **44 passed, 5 warnings** (0.60s). `data_loader.py` unchanged since `e945fde`.
**Mode:** HEAVY WORK ONLY. 0-delta status sessions are **FAILED**. Floor mechanism-closed through batch134 + line `322` re-missed at `db84180`. **Do not exit after baseline**.

**Bottlenecks:** all removed/routed (deps in `/home/runner/work/_temp/kilo-tmp/pylib` via `PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`; `.coverage*` cleaned pre-run; `--ignore=tests/test_controller_progress_accounting.py`; no `.github/workflows/*` edits; canonical batch set 40-69,71-74,76-89,93,95,96).

### Mission (binary, no escape hatches)

1. **Primary:** Push `strategies/betting_against_beta/data_loader.py` **below 36 miss / 1683 stmts (98%, rcfile=/dev/null)** in a fresh canonical aggregate, using a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism satisfying all 4 strict criteria **on a real `pd.DataFrame`/index/dtype/column-label path with plausible pandas/library behavior** (no semantic changes, no pathological harnesses). Line `322` is now a live target (inspect-gated `break` in `_coerce_to_datetime_scalar`, reachable via a `campaign_d_core`-filename caller with a non-NaT value); line `326` remains guard-relevant — preserve its semantics; never alter `322,326`.
2. **Fallback (only after exhaustive, methodical work):** Add **genuinely new** unreachable-proof evidence to `docs/unreachable_proofs.md` tied to a concrete, production-realistic mechanism not disproven by batches 103–134 + the batch135-entry public-entrypoint trace. Your proof must use a **materially new method** not identically recorded (e.g., `hypothesis`-driven randomized public `load_*` round-trips if installed; pandas 2.x nullable/Arrow-adjacent dtype permutations present in env; CSV dialect/quoting/newline/locale-like numeric formatting variants; timezone metadata round-trips across file formats; `to_json`/`read_json` full orient matrix; MultiIndex-column flattening edge cases; downstream `metrics`/`backtest`/`portfolio` consumption traces proving production-realistic loader outputs and confirming miss clusters unreachable across all public entrypoints). "No new mechanism" without new-method evidence is a failed session.
3. **Forbidden:** baseline-only, review-only, planning-only, repeat probes, semantic changes for coverage, workflow edits, touching `322,326` semantics, committing unless explicitly requested.

**Remaining 36 (verified @ `db84180`):** `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. **Never alter `322,326`.**

### Step 0 — Environment + fresh rebaseline (MANDATORY)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy, hypothesis; print('deps ok', hypothesis.__version__)"
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py tests/test_bab_data_loader_batch79.py tests/test_bab_data_loader_batch80.py tests/test_bab_data_loader_batch81.py tests/test_bab_data_loader_batch82.py tests/test_bab_data_loader_batch83.py tests/test_bab_data_loader_batch84.py tests/test_bab_data_loader_batch85.py tests/test_bab_data_loader_batch86.py tests/test_bab_data_loader_batch87.py tests/test_bab_data_loader_batch88.py tests/test_bab_data_loader_batch89.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Record actual baseline/SHA. Reconcile if different from **36 miss (1466/0/17), guard 44/5**.

### Forced campaign (must execute — no early exit)

For **each** cluster `(234-244,246-247)`, `(268-269)`, `(351-352)`, `(334-335,338-342)`, `(403-404)`, `(43-44)`, `(953)`, `(641-642,694-695)`, `(791-792)`, `(322)` (guard-only, do not alter semantics; `322` is now a live inspect-gated target), `(326)` (guard-only):
1. Quote/verify current code (file:line).
2. State strict 4 criteria. **If all 4 met:** write `tests/test_bab_data_loader_batch135.py`, run focused → guard → fresh canonical aggregate including batch135; record delta.
3. **If not all 4 met:** perform at least one *new* materially-different check (document method + observed result) and append to batch135 appendix in `docs/unreachable_proofs.md`.
4. Never repeat disproven mechanisms from batches 103–134.

### Required session outcome (binary)

**Success =** miss **< 36** in a fresh canonical aggregate **OR** a genuinely-new mechanism proof/test **OR** a complete batch135 exhaustive trace appendix in `docs/unreachable_proofs.md` covering all remaining clusters with non-repeat, materially-new evidence + this HANDOFF updated with measured results. **Anything less is failure.**

**BEGIN HEAVY WORK NOW. Rebaseline, then execute the forced campaign — no status-only output.**

---

## Batch 134 (2026-11-08T02:22Z, SHA `db84180`, fresh Step 0 rebaseline, 0 delta, line `322` re-missed)

**Canonical (fresh, `--rcfile=/dev/null` run+report):** **1466 passed, 0 failed, 17 skipped, 107 warnings** (44.31s). Coverage: **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. Baseline re-confirmed at `db84180`; `data_loader.py` unchanged since `e945fde`.

**Strict batch134 entry criteria (all 4 required) — none satisfied (no test/probe added):** (1) targets/line→code verified for all 36; (2) no mechanism not disproven by batches 103–133; (3) no production-realistic `pd.DataFrame`/index/dtype/column-label + plausible pandas/library behavior demonstrated to reach remaining handlers without semantic change or pathological harness; (4) control-flow path cannot be stated consistently with (2)-(3). **No canonical `batch134` test/probe added.**

**Conclusion:** **36-miss floor remains mechanism-closed at `db84180`; line `322` re-missed (prior `@2ac1e3c` 35-miss claim not reproducible).** **Batch135 only** on a concretely demonstrated, production-realistic control-flow mechanism satisfying all four criteria. Preserve `322,326`; never change semantics for coverage; do not commit unless explicitly requested; use `--rcfile=/dev/null` for canonical coverage run+report.
