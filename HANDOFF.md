# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **THIS IS THE SOLE DURABLE HANDOFF.** Prioritize `Crypto-Betting-Against-Beta` (BAB) ONLY. Read completely, rebaseline, then execute the **INITIAL TASK MESSAGE** immediately. No off-ramps, no sidetracks, no status-only sessions, no planning-only sessions, no "review-only" exits. Every session must produce measurable heavy work: **miss reduction in a fresh canonical aggregate** OR **new high-confidence file:line unreachable-proof evidence** added to `docs/unreachable_proofs.md` that closes a *genuinely new* mechanism (not a repeat probe).

**Handoff refreshed (UTC):** 2026-11-07T20:21:30Z (batch123 prep; canonical re-confirmed @ `53555f6`; baseline unchanged).
**Repo:** `Crypto-Betting-Against-Beta` | **Path:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Branch/SHA (measured):** `main` @ `53555f6` (untracked `debug_beta*.py`/`probe*.py`/`.coverage` and kilo/session artifacts may exist — **do not commit**; clean `.coverage*` before coverage runs).
**Measured baseline (fresh canonical, 2026-11-07T20:21Z, batch123 prep):** batches 40-69,71-74,76-89,93,95,96 — **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.38s). Coverage (`--rcfile=/dev/null` run+report): **36 miss / 1683 stmts / 98%** (`--include='strategies/betting_against_beta/data_loader.py'`). Missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard (`campaign_d*`) **44 passed, 5 warnings**.
**Target:** `strategies/betting_against_beta/data_loader.py` — **36 miss / 1683 stmts / 98%** (measured floor @ `53555f6`). **Step 0 must rebaseline every session.** Historic refs to `1626-1627,1663-1664`/1693-stmt state are stale — re-check line→code before targeting.
**Floor status:** **MECHANISM-CLOSED** for all 36 remaining lines (batches 103–122). A miss reduction now requires a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism satisfying the strict 4 criteria — not a repeat probe, not a pathological harness, and never a production-semantics change solely for coverage.

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
| 115 | 0 | proof refinement @ `074753a` | 2026-11-07T19:08Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings**; **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`, run+report). Missing unchanged. Guard **44 passed, 5 warnings**. No production/test change. Added Batch 115 strict 4-criteria assessment + line-map reconciliation (stale 1626-1627/1663-1664 refs) to `docs/unreachable_proofs.md`. No mechanism satisfied entry criteria. |


| 116 | 0 | proof refinement + rebaseline @ `1122e26` | 2026-11-07T19:11Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings**; **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`, run+report). Missing unchanged. Guard **44 passed, 5 warnings**. No production/test change. Strict 4-criteria batch117 assessment added to `docs/unreachable_proofs.md`; no mechanism satisfied. |

| 117 | 0 | fresh rebaseline + strict 4-criteria + targeted probes @ `4dbcd7b` | 2026-11-07T19:18Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.31s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing unchanged. Guard **44 passed, 5 warnings**. Probed 268-269 (`pd.to_datetime`→plain `TypeError` converted to `BABDataError`, caught by 266 before 268 — handler-order/MRO gate confirmed), 351-352 (float subclass normal; pathological only), 641-642/694-695 (production-realistic OHLCV/epoch-ms frames normalize). 246-247 probe harness malformed (not evidence). Strict 4-criteria unsatisfied for all 36. No production/test change. Proof appended to `docs/unreachable_proofs.md`. |

| 117-reconfirm | 0 | fresh rebaseline @ `56574bd` | 2026-11-07T19:22Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.32s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing unchanged (`43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`). Guard **44 passed, 5 warnings**. `data_loader.py` unchanged from `4dbcd7b` (HEAD commit `56574bd` touched only HANDOFF.md + docs/unreachable_proofs.md). Baseline re-confirmed at new SHA, delta 0.
| 118 | 0 | fresh rebaseline + mechanism re-confirm @ `8145832` | 2026-11-07T19:27Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.23s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing unchanged. Guard **44 passed, 5 warnings**. Targeted traces re-confirmed 268-269 handler conversion/order+MRO gate and 234-244 223-intercept/227-entry gate; strict 4-criteria unsatisfied. Proof appended to `docs/unreachable_proofs.md`. |
| 119 | 0 | fresh rebaseline + strict 4-criteria probes @ `b4fdaf5` | 2026-11-07T20:08Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (46.11s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing unchanged. Guard **44 passed, 5 warnings**. NaT-shape + 268-269 conversion/order probes + exchange-column pathological note: strict 4-criteria unsatisfied (no production-realistic new mechanism). No production/test change. Proof appended to `docs/unreachable_proofs.md`. |
| 120 | 0 | fresh rebaseline + strict 4-criteria assessment @ `9d2b1c6` | 2026-11-07T20:12Z: canonical aggregate → **1466 passed, 0 failed, 17 skipped, 107 warnings** (45.20s); **36 miss / 1683 stmts / 98%** (`--rcfile=/dev/null`). Missing unchanged. Guard **44 passed, 5 warnings**. Line-to-code verified; all 4 criteria unsatisfied for remaining 36. No production/test change, no probe added. Proof strengthened in `docs/unreachable_proofs.md`. |
| 121 | 0 | fresh rebaseline + strict 4-criteria @ `eab0c8d` | 2026-11-07T20:18Z: **1466/0/17, 36/1683 (98%)**. Missing unchanged. Guard **44/5**. Line-to-code re-verified; criteria unsatisfied. |
| 122 | 0 | fresh rebaseline @ `927c2d7` | 2026-11-07T20:19Z: **1466/0/17, 36/1683 (98%)**. Missing unchanged. Guard **44/5**. Proofs re-confirmed. |
| 123-prep | 0 | fresh rebaseline @ `53555f6` (this handoff refresh) | 2026-11-07T20:21Z: **1466/0/17, 107 warnings (46.38s)**; **36/1683 (98%)**; missing exactly `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. Guard **44/5**. Floor remains mechanism-closed; no new production-realistic mechanism found. Handoff refreshed as sole durable directive. |

Next batch number: **123** (only on a concretely demonstrated, genuinely new production-realistic mechanism satisfying all four criteria — see below).

---

## INITIAL TASK MESSAGE — 2026-11-07T20:11:31Z (batch120 rebaseline) — EXECUTE IMMEDIATELY (HEAVY WORK, NO ESCAPE HATCHES)

**Timestamp (UTC):** 2026-11-07T20:11:31Z (batch120; 36-miss mechanism-closed under `--rcfile=/dev/null`). **SHA at handoff:** `b4fdaf5` (run `git rev-parse --short HEAD` in Step 0 and record actual SHA).
**Mode:** HEAVY WORK ONLY. Every minute must move coverage or proof quality. Ambiguity is not an escape hatch — this message is explicit and non-negotiable. **The 36-miss floor is mechanism-closed** (batches 103–119). Only a *genuinely new, concretely demonstrated, production-realistic* control-flow mechanism (not semantic change, not pathological harness, not repeat probe) may justify batch120 tests/proofs.

### Mission (mandatory, binary)

Push `strategies/betting_against_beta/data_loader.py` **below the fresh measured baseline (36 miss / 1683 stmts / 98%, rcfile=/dev/null @ b4fdaf5)** in a fresh canonical aggregate, **OR** add new high-confidence unreachable proofs that materially close **genuinely new** ambiguity in `docs/unreachable_proofs.md` with file:line + function + entrypoint + exact shape/monkeypatch/trace + observed behavior + why dead/unreachable. **Do not stop after baseline.**

**Reality (mechanism-closed @ b4fdaf5):** remaining **36** — `43-44, 234-244, 246-247, 268-269, 322, 326, 334-335, 338-342, 351-352, 403-404, 641-642, 694-695, 791-792, 953`. All mechanism-closed (structural-dead/handler-order+MRO+conversion dead/coercer-determinism or NaT-gate dead/re-raise-before-generic-pass/construction-unreachable/pathological-semantic-only/inspect-gated). **Historic line refs stale — re-check line→code every session. Production semantics must not change solely to manufacture coverage.**

**Batch120 entry criteria (strict):** before writing any test/probe, state (1) the exact target line(s) *and current code at those lines*, (2) the new mechanism not disproven by batches 103–119/unreachable_proofs, (3) why it is production-realistic (real `pd.DataFrame`/index/dtype + plausible pandas/library behavior), and (4) the expected control-flow path. If you cannot state all four, do not probe — add a proof refinement only if it closes genuinely new ambiguity.

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

Record actual baseline/SHA. **Use `--rcfile=/dev/null` for run+report**. If baseline differs from **36 miss, 1466/0/17, guard 44**, reconcile before hunting.

### Campaign loop (repeat until measurable success — no early exit)

1. Attack only with a **genuinely new production-realistic mechanism** not previously disproven. **Never alter `322,326`. Never change semantics for 351-352.** Do **not** repeat disproven mechanisms (coercer determinism/223 intercept/NaT gate for 234-247; `Exception→BABDataError` + handler order/MRO for 268-269; re-raise-before-generic-pass 334-342; builtin `float(s)`/guarded epoch 403-404; identity+guarded `pd.isna` 43-44; inner-swallow/guarded setup 641-695; fully-guarded promote 791-792; `str.split()` tokens 953; pathological `__float__` 351-352).

2. **Max 1 probe per cluster** unless a probe proves a real path. Real DataFrame shapes, direct canonical helpers, tight scoped monkeypatches/subclasses only where plausible.

3. **If hit:** create `tests/test_bab_data_loader_batch120.py` (data_loader only). Run focused → guard → fresh canonical aggregate including batch120. Record before/after/delta. Update `HANDOFF.md` + `docs/unreachable_proofs.md`.

4. **If 0 delta:** add exact proof to `docs/unreachable_proofs.md`; update HANDOFF. No canonical test unless valuable.

5. **Never** retarget stale lines without fresh line→code check. **Never** touch workflows. **Never** change production semantics solely for coverage.

### Execution contract

- BAB `data_loader.py` only. `--ignore=tests/test_controller_progress_accounting.py` always. `rm -f .coverage .coverage.*` before coverage; `--rcfile=/dev/null` for run+report. Preserve invariants (no lookahead, `BABDataError` on bad data, dollar-neutral/costs, `322,326`/campaign_d semantics, public APIs). Update **this HANDOFF.md** as the single durable handoff.

### Required session outcome (binary)

**Success =** miss **< 36** in a fresh canonical aggregate **OR** new high-confidence unreachable proofs with genuinely-new mechanism-closure evidence materially improving `docs/unreachable_proofs.md` and this handoff. Anything less is failure.

**BEGIN HEAVY WORK NOW. Rebaseline, then reduce miss or strengthen proofs — no status-only output.**
