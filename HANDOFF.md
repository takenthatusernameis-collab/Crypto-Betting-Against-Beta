# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` that closes a *genuinely new* mechanism (not a repeat probe).

**Handoff refreshed (UTC):** 2026-11-07T18:33:32Z (batch114 rebaseline @ `cfe353d`; measured floor is now **36 miss** with `--rcfile=/dev/null` in this env; 1626-1627/1663-1664 no longer in the miss set at HEAD — see baseline note; remaining 36 mechanism-closed; next session (batch115) only on a genuinely new, concretely demonstrated, production-realistic control-flow mechanism).
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (measured):** `main` @ `cfe353d` (HEAD; `data_loader.py` **modified at HEAD vs 311656a** — 1626-1627/1663-1664 shifted/covered relative to prior handoff; untracked `debug_beta*.py`/`probe*.py` and `.coverage` pre-existing — do not commit; clean `.coverage*` before coverage runs).
**Measured baseline (fresh canonical, 2026-11-07T18:33Z, this session):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.17s). Coverage (use `--rcfile=/dev/null` in this env): **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`, `--rcfile=/dev/null`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard (`campaign_d*`) **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **36 miss / 1683 stmts / 98%** (current measured floor @ e945fde). **Delta: -4 vs prior handoff claim (40) due to HEAD/code shift + measurement alignment; treat 36 as the rebaselined floor. Step 0 must rebaseline before hunting.**

**CRITICAL:** No `.github/workflows/*` edits/commits/pushes. No remote push performed. `--ignore=tests/test_controller_progress_accounting.py` ALWAYS. Do not commit unless explicitly requested. Production semantics must not change solely to manufacture coverage.

---

## PRIORITY (repo-name-driven, non-negotiable)

Repo name = **Crypto-Betting-Against-Beta** → **BAB strategy only**. **ONLY** `strategies/betting_against_beta/data_loader.py` matters.

- **NO** infra/controller refactors. **NO** `cli.py`/other-module pivots. **NO** sidetracks.
- Every session MUST produce a **measured `data_loader.py` miss-count reduction below the fresh baseline** in a **fresh completed canonical aggregate**, OR add **new high-confidence unreachable-proof evidence** to `docs/unreachable_proofs.md` while immediately moving to the next cluster.
- A session ending with "reviewed", "planned", "explored", or "ran baseline only" without measured delta/proof = **FAILED SESSION**.
- **Production semantics must not change solely to manufacture coverage.** Preserve: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior, inspect-sensitive/campaign_d behavior (`322,326` guard-relevant), public APIs stable.

---

## BOTTLENECKS — ALL REMOVED / ROUTED (verified 2026-11-07T17:02Z; re-verified this session)

| # | Bottleneck | Action | Status |
|---|---|---|---|
| 1 | Root scratch clutter | `.gitignore` ignores `diag*.py`, `_recon_cov.py`; transient `.coverage*` cleaned before canonical runs. Untracked `debug_beta*.py`/`probe*.py` present — do not commit. | Removed/Routed |
| 2 | Controller workflow-sync test | Always `--ignore=tests/test_controller_progress_accounting.py`. Never touch `.github/workflows/*`. | Routed |
| 3 | Deps/bootstrap fragility | Install to `/home/runner/work/_temp/kilo-tmp/pylib` if missing: `python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy` + `export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib`. Deps confirmed installed (pytest/coverage/pandas/numpy/scipy). | Routed |
| 4 | Coverage DB instability | `rm -f .coverage .coverage.*` before canonical coverage run. | Routed |
| 5 | Coverage report path filtering | Use `--include='*data_loader.py'` with `--source=strategies.betting_against_beta`. | Routed |
| 6 | Missing parquet/hdf5 engines | Monkeypatch `pd.read_parquet/read_hdf`/engine call sites; inner handlers may wrap as `BABDataError`. | Routed |
| 7 | Aggregate-context sensitivity | Prefer direct canonical helper calls with real shapes and tight scoped monkeypatches/subclasses. Verify in fresh canonical aggregate. | Routed |
| 8 | Inspect-sensitive/campaign_d semantics | Preserve `_coerce_to_datetime_scalar` inspect behavior and campaign_d filename/function behavior. Guard must stay green. | Preserved |
| 9 | Canonical batch set drift | Canonical data-loader batches: **40-69,71-74,76-89,93,95,96** (no 70,75,90-92,94 in canonical aggregate). Rebaseline exact set in Step 0. | Routed |
| 10 | `No data to report` / stale coverage | Clean `.coverage*` before coverage; run `coverage run` and `coverage report` in same shell/env. | Routed |
| 11 | Repeated 0-delta batches (97-112 + this session) | All remaining 40 lines proven structural-dead / inspect-gated / handler-order gated / construction-unreachable / pathological-only via mechanism-closure proofs in `docs/unreachable_proofs.md`. **The 40-miss floor is mechanism-closed; no repeat probes.** Next session (113) only if a genuinely new, concretely demonstrated production-realistic control-flow mechanism is identified (strict batch113 entry criteria in INITIAL TASK MESSAGE). | Removed/Routed |

---

## CURRENT MEASURED STATE (rebaseline every session — do not trust stale numbers)

**Fresh baseline (2026-11-07T18:31Z, this session rebaseline):** miss **36/1683 (98%)** with `--rcfile=/dev/null`, **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.04s), guard **44 passed, 5 warnings**. SHA `e945fde` (`data_loader.py` differs from `311656a` at HEAD; 1626-1627/1663-1664 not in current miss set).

**Remaining 36 lines (mechanism-closed @ e945fde):**
`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`

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
10. **`322,326`** — inspect-gated/campaign_d NaT guards (**guard-relevant, DO NOT ALTER**).

*Note (batch114, e945fde):* prior handoff listed `1626-1627,1663-1664` as missing; at HEAD they are no longer in the canonical miss set (handlers/line mapping shifted or covered). Do not re-target those line numbers without a fresh line-to-code check.

---

## SESSION BATCH LEDGER (cumulative, measured)

| Batch | Delta (miss) | Result | Notes |
|---|---|---|---|
| 71–89,93,95,96 | -56 | measured | 96→40 cumulative (see docs/unreachable_proofs.md). |
| 90–92,94,97–109 | 0 | proof-only/probe | mechanism-closure evidence strengthened; no production-realistic miss reduction found. |
| 110 | 0 | rebaseline + trace proofs | Fresh canonical **40/1693, 1466/0/17, guard 44/5** @ `311656a`. New direct coverage traces appended to `docs/unreachable_proofs.md` for 641-642/694-695 (exchange outer handlers), 1626-1627/1663-1664 (parquet/hdf5 handler conversion), 791-792 (fully guarded), 268-269 (handler order+conversion). No production change, no canonical test added. |
| 110-reconfirm | 0 | fresh rebaseline @ `50c2da3` | 2026-11-07T17:02Z: **1466 passed, 0 failed, 17 skipped, 107 warnings** (47.46s); **40 miss / 1693 stmts / 98%**; guard **44 passed, 5 warnings**. data_loader.py unchanged from `311656a`. Baseline re-confirmed, delta 0. |
| 111 | 0 | fresh rebaseline @ `20fcc7c` | 2026-11-07T17:09Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.51s); **40 miss / 1693 stmts / 98%**; missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged (no diff vs 311656a). All 40 lines remain mechanism-closed per `docs/unreachable_proofs.md` (batches 103–111). No new production-realistic control-flow mechanism identified; **no repeat probes**. |
| 112 | 0 | fresh rebaseline + strict entry-criteria assessment @ `2844791` | 2026-11-07T17:14Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.60s); **40 miss / 1693 stmts / 98%** (`--include=strategies/betting_against_beta/data_loader.py`); missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged. Strict batch112 entry criteria assessed: no new production-realistic control-flow mechanism for any cluster (all 4 criteria unsatisfied); no probe/test added. Proof appended to `docs/unreachable_proofs.md`. |
| 113-prep/reconfirm | 0 | fresh rebaseline @ `2d7ddd9` | 2026-11-07T17:22Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.31s); **40 miss / 1693 stmts / 98%** (`--include=strategies/betting_against_beta/data_loader.py`); missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953, 1626-1627, 1663-1664`. Guard **44 passed, 5 warnings**. `data_loader.py` unchanged from `311656a`. All bottlenecks remain removed/routed; batch113 entry criteria still unsatisfied. No probe/test added. |
| 114 | -4 (measured rebaseline / line-set shift) | fresh rebaseline @ `e945fde` | 2026-11-07T18:31Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.04s); with `--rcfile=/dev/null` **36 miss / 1683 stmts / 98%** (`--include=strategies/betting_against_beta/data_loader.py`); missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44 passed, 5 warnings**. `data_loader.py` differs from `311656a` at HEAD; prior refs `1626-1627,1663-1664` no longer in miss set. No new production-realistic mechanism found for remaining 36; 268-269 re-confirmed structural-dead (261-265 converts Exception→BABDataError caught by 266). Proof note appended. |


Next batch number: **115** (only on a concretely demonstrated, genuinely new production-realistic mechanism — see batch115 entry criteria in initial task).

---

## INITIAL TASK MESSAGE — 2026-11-07T18:31:29Z (batch114 rebaseline) — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T18:31:29Z (batch114 re-baseline @ `e945fde`; 36-miss mechanism-closed under `--rcfile=/dev/null`). **SHA at handoff/rebaseline:** `e945fde` (run `git rev-parse --short HEAD` in Step 0 and record actual SHA).
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Future agents cannot avoid heavy work by claiming ambiguity — this message is explicit. **The 36-miss floor is mechanism-closed** across all remaining lines (batches 97-112 + this reconfirm). Only a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism (not semantic change, not pathological harness, not repeat probe) may justify batch115 tests/proofs.

### Mission (mandatory, binary)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (36 miss / 1683 stmts / 98%, rcfile=/dev/null @ e945fde)** in a fresh canonical aggregate, **OR** add new high-confidence unreachable proofs that materially close remaining ambiguity in `docs/unreachable_proofs.md` with file:line + function + entrypoint + exact shape/monkeypatch/trace + observed behavior + why dead/unreachable. **Do not stop after baseline.**

**Reality (mechanism-closed @ e945fde):** remaining **36** — `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953` (measured with `--rcfile=/dev/null`). All mechanism-closed: handler-structure dead (`268-269`; prior parquet/hdf5 outer-handler line refs 1626-1627/1663-1664 not in current miss set @ e945fde), coercer-determinism/gate dead (`234-244`, `246-247`), re-raise-before-generic-pass (`334-335,338-342`), structural/construction dead (`43-44`, `403-404`, `641-642`, `694-695`, `791-792`, `953`), pathological semantic decision only (`351-352`, **disallowed**), inspect-gated guard-relevant (`322,326`, **DO NOT ALTER**). **Production semantics must not change solely to manufacture coverage.**

**Batch115 entry criteria (strict):** before writing any test/probe, state (1) the exact target line(s), (2) the new mechanism not disproven by batches 103–114/unreachable_proofs, (3) why it is production-realistic (real `pd.DataFrame`/index/dtype + plausible library behavior), and (4) the expected control-flow path. If you cannot state all four, do not probe — add a narrow proof refinement only if it closes genuinely new ambiguity.

### Step 0 — Environment + fresh rebaseline (MANDATORY, run first)

```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib
python3 -c "import pytest, coverage, pandas, numpy, scipy; print('deps ok')" || (python3 -m pip install --target /home/runner/work/_temp/kilo-tmp/pylib pytest coverage numpy pandas scipy && export PYTHONPATH=$PWD:/home/runner/work/_temp/kilo-tmp/pylib)
git rev-parse --short HEAD
rm -f .coverage .coverage.*
python3 -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py \
  tests/test_bab_data_loader_coverage_gaps.py tests/test_bab_data_loader_robust.py tests/test_bab_data_loader_promote.py tests/test_bab_data_loader_miss_fill.py \
  tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py \
  tests/test_bab_cli_coverage_campaign.py tests/test_bab_cli.py \
  tests/test_bab_data_loader_batch40.py tests/test_bab_data_loader_batch41.py tests/test_bab_data_loader_batch42.py tests/test_bab_data_loader_batch43.py tests/test_bab_data_loader_batch44.py tests/test_bab_data_loader_batch45.py tests/test_bab_data_loader_batch46.py tests/test_bab_data_loader_batch47.py tests/test_bab_data_loader_batch48.py tests/test_bab_data_loader_batch49.py tests/test_bab_data_loader_batch50.py tests/test_bab_data_loader_batch51.py tests/test_bab_data_loader_batch52.py tests/test_bab_data_loader_batch53.py tests/test_bab_data_loader_batch54.py tests/test_bab_data_loader_batch55.py tests/test_bab_data_loader_batch56.py tests/test_bab_data_loader_batch57.py tests/test_bab_data_loader_batch58.py tests/test_bab_data_loader_batch59.py tests/test_bab_data_loader_batch60.py tests/test_bab_data_loader_batch61.py tests/test_bab_data_loader_batch62.py tests/test_bab_data_loader_batch63.py tests/test_bab_data_loader_batch64.py tests/test_bab_data_loader_batch65.py tests/test_bab_data_loader_batch66.py tests/test_bab_data_loader_batch67.py tests/test_bab_data_loader_batch68.py tests/test_bab_data_loader_batch69.py tests/test_bab_data_loader_batch71.py tests/test_bab_data_loader_batch72.py tests/test_bab_data_loader_batch73.py tests/test_bab_data_loader_batch74.py tests/test_bab_data_loader_batch76.py tests/test_bab_data_loader_batch77.py tests/test_bab_data_loader_batch78.py tests/test_bab_data_loader_batch79.py tests/test_bab_data_loader_batch80.py tests/test_bab_data_loader_batch81.py tests/test_bab_data_loader_batch82.py tests/test_bab_data_loader_batch83.py tests/test_bab_data_loader_batch84.py tests/test_bab_data_loader_batch85.py tests/test_bab_data_loader_batch86.py tests/test_bab_data_loader_batch87.py tests/test_bab_data_loader_batch88.py tests/test_bab_data_loader_batch89.py tests/test_bab_data_loader_batch93.py tests/test_bab_data_loader_batch95.py tests/test_bab_data_loader_batch96.py
python3 -m coverage report --rcfile=/dev/null --include='strategies/betting_against_beta/data_loader.py' --show-missing
python3 -m pytest -q --tb=no --ignore=tests/test_controller_progress_accounting.py tests/test_bab_data_loader_campaign_d.py tests/test_bab_data_loader_campaign_d2.py tests/test_bab_data_loader_campaign_d3.py
```

Record actual baseline. If different from **36 miss, 1466/0/17, guard 44** (or if env lacks `--rcfile=/dev/null` behavior causing "No data to report"/stale misses), reconcile before hunting.

### Campaign loop (repeat until measurable success — no early exit)

1. Attack only with a **genuinely new production-realistic mechanism** not previously disproven: re-examine remaining clusters for pandas/internal exception types, frame/index/subclass shapes, or call-paths that throw through exact unguarded seams *without* changing BAB semantics. **Never alter `322,326`. Never change semantics to "fix" 351-352 pathological NaN-subclass slip.** Do **not** repeat disproven mechanisms: coercer determinism 216-224→232 (234-244), 225/227 NaT gate + same-length 245 assignment (246-247), `Exception→BABDataError` conversion + handler order (268-269, 1626-1627, 1663-1664), re-raise-before-generic-pass (334-335,338-342), builtin-`float(s)`/guarded `int(inf)`/datetime branches (403-404), `is None`/inner-guarded `pd.isna` (43-44), `str.split()` token construction (953), exchange setup purity + inner-swallow handlers (641-642,694-695), fully-guarded promote body (791-792), pathological `BadIsnan.__float__` (351-352) without explicit semantic decision.

2. **Max 1 probe per cluster** unless a probe proves a real path and needs a minimal focused harness. Use real DataFrame shapes, direct canonical helper entrypoints, and tight scoped monkeypatches/subclasses only where control flow is plausible.

3. **If hit:** create `tests/test_bab_data_loader_batch115.py` (data_loader only). Minimal deterministic tests. Run focused → guard → fresh canonical aggregate including batch115. Record before/after/delta. If miss decreased, update `HANDOFF.md` + `docs/unreachable_proofs.md` and continue hunting.

4. **If 0 delta:** do not add to canonical unless valuable. Add exact proof to `docs/unreachable_proofs.md` (file:line, function, entrypoint, shape/monkeypatch/trace tried, observed behavior, why dead/unreachable/pathological/semantic). Update HANDOFF cluster map. Move on immediately.

5. **Never** retarget already-covered/dead lines without a new mechanism. **Never** touch workflows. **Never** coast. **Never** change production semantics solely to manufacture coverage.

### Execution contract

- BAB `data_loader.py` only; smallest correct fix only if a proven contract violation.
- `--ignore=tests/test_controller_progress_accounting.py` always.
- Canonical aggregate must include all relevant batch files; `rm -f .coverage .coverage.*` before coverage.
- Preserve invariants: no lookahead, `BABDataError` on bad data, dollar-neutral/costs behavior preserved, inspect-sensitive/campaign_d behavior preserved, public APIs stable.
- Update **this HANDOFF.md** at end: refreshed UTC, SHA, actual baseline/canonical/guard, ledger, remaining miss/proof summary, next initial task message. Keep it the single durable handoff.

### Required session outcome (binary)

**Success =** measured miss below fresh baseline (**< 36**) in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with mechanism-closure evidence that materially improve `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
