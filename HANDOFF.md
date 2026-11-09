# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T03:21Z** @ workspace `cccc97c` (`main`); `strategies/betting_against_beta/data_loader.py` blob `596ee9e` **unchanged**. `docs/unreachable_proofs.md` is the evidence appendix (includes `## Batch 186` @ `596ee9e`, outcome B: 0-delta, 0 target hits, strict-4 verdicts for all clusters). **Repo-name priority = Betting Against Beta only**. Next work is `strategies/betting_against_beta/data_loader.py` target-miss floor **only if a materially-new strict-4 reduction mechanism is discovered**; otherwise preserve the recorded unreachable baseline and do not churn probes. **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative Step 0 baseline (VERIFIED 2026-11-09T03:21Z @ `cccc97c`; next agent must rerun fresh before claiming any reduction — this verification is not an outcome):** env `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical coverage `--rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py` over explicit canonical file list (`tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py`; build list with `seq` if shell brace expansion misbehaves) → **647 passed, 6 skipped, 34 warnings** (~39s). `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing` → **362 miss / 1683 stmts / 78%**. `campaign_d`: **883 passed, 5 skipped, 3487 deselected, 53 warnings**. `data_loader.py` blob `596ee9e`. **Target-miss floor UNCHANGED** (all present; re-verify line→code @ fresh SHA before edits): `40-41,43-44,57-61,68,72,86-89,98-99,110-111,121-123,128-130,134,136-143,145-149,153-155,161,167,171-176,180,186,188,213-214,234-244,246-247,258,268-269,289,296-297,305,320-322,324-328,338-342,344,356,358,386,403-404,423-429,431-434,436-439,447-453,455-458,460-463,465-468,479-483,498,525-526,539-540,566-567,571,580-586,606,625-626,630,641-642,664,694-695,708-712,755-756,791-792,821,917-918,953,964,968,972,974,976,978,982-983,996,1008-1009,1055-1056,1082-1083,1110,1136-1141,1147,1153-1154,1174-1175,1177-1178,1186,1188-1189,1198,1202,1207,1241,1243,1249-1250,1262-1267,1288,1292,1307,1311,1325-1327,1338,1344,1539,1553-1554,1581-1582,1611,1621-1622,1639,1643,1649-1654,1676-1677,1683,1691,1694-1695,1697,1727,1730-1731,1733,1739-1742,1747,1754-1755,1759-1765,1768-1773,1782-1783,1787-1797,1811-1816,1836,1852,1859-1860,1866,1868-1869,1872,1891-1892,1932,1944,1977-1989,2000,2012-2013,2041,2044-2045,2048-2060,2062-2065,2067-2070,2077-2084,2115,2117,2119,2127-2128,2201-2203,2212,2224-2239`. **`326` is LIVE/GUARD — never alter `322,326`.**

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='*/strategies/betting_against_beta/data_loader.py'`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed; handlers may wrap as `BABDataError`), and **0-delta churn without new method/evidence** (B103–183/M149–M183 + B186 executed/recorded; no status/planning/review/baseline-only or repeat-probe session is acceptable).

## Remaining target-miss clusters (verify line→code @ SHA; B186 strict-4 verdicts recorded)

| Cluster | Lines | Current verdict (B186, `596ee9e`) |
|---|---|---|
| `_not_null` outer except | `43-44` | Not reducible (production-realistic, structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Not reducible (dataflow/contract-shadow). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Not reducible (handler-order shadow/MRO). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | Not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Not reducible (defensive/guarded). |
| exchange detect outer handlers | `641-642,694-695` | Not reducible (structural shadow + production-realistic). |
| promote datetime column outer handler | `791-792` | Not reducible (nested/guarded). |
| `_normalize_asset_name` empty token continue | `953` | Not reducible (construction-unreachable; `str.split()` default). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA/blob.
2. Mechanism not disproven by B103–183/M149–M183/B186 and recorded proofs.
3. Production-realistic `pd.DataFrame`/index/dtype/column-label/file-format path (no semantic change, no pathological harness).
4. Stated control-flow path consistent with (2)-(3).

## Session batch ledger

| Batch | Delta | Result | Notes |
|---|---|---|---|
| 148 | -2 | reduction | 351-352; semantics preserved. |
| 149 | -2 | reduction | 334-335 (M149). |
| 150–171 | 0 | proof | M150–M171 recorded. |
| 172 | 0 | proof+probes | M172.1–M172.7; batch172 retained; target floor unchanged. |
| 173–183 | 0 | proof+probes | M173–M183 complete strict-4 evidence; no reduction. |
| 184 | 0 | superseded | No proof appendix entry required; superseded by later recorded batches. |
| 185 | 0 | unverified ledger row | No `## Batch 185` appendix found; treated as superseded by B186 evidence. Do not claim B185 proof. |
| 186 | 0 | proof+probes (complete) | **`docs/unreachable_proofs.md##Batch 186`** — M186 materially-new CLI real-file/entrypoint trace + masked/recarray/sparse/attrs + read_csv NA-marker combos under `sys.settrace`; 0 target hits all clusters; strict-4 verdicts recorded; 365 miss/78%, campaign_d green; `326` preserved. |
| 0 (this session, 2026-11-09T03:21Z) | 0 | baseline-verify+handoff | Fresh Step 0 @ `cccc97c`: 647/6/34, 362 miss/1683/78%, campaign_d 883/5/3487; blob `596ee9e`; durable handoff refreshed. No production/test semantic changes. |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T03:21Z (Batch 187 gate, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** preserve the verified BAB `data_loader.py` baseline and pursue **only** a materially-new strict-4 reduction of the target-miss floor (**362 miss / 1683 stmts / 78% @ blob `596ee9e`**) if a real production-realistic mechanism is discovered that is **not** disproven by B103–183/M149–M183/B186. B186 outcome B is complete in `docs/unreachable_proofs.md`; **do not repeat M149–M186 probe families**.

**State (verified 2026-11-09T03:21Z):** HEAD `cccc97c` (`main`), `data_loader.py` blob `596ee9e`, line→code verified for all target clusters. Canonical baseline: **647 passed, 6 skipped, 34 warnings; 362 miss / 1683 stmts / 78%**; `campaign_d` **883 passed, 5 skipped, 3487 deselected, 53 warnings**. Target floor unchanged. No competing handoff files.

### Forced steps (execute in order; skip none)

1. **Step 0 — fresh baseline (mandatory, not an outcome):**
   - `export PYTHONPATH=$PWD`
   - `rm -f .coverage .coverage.*`
   - Canonical files: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` (explicit list via `seq` if needed).
   - `python -m coverage run --rcfile=/dev/null --source=strategies.betting_against_beta -m pytest -q --ignore=tests/test_controller_progress_accounting.py [FILE_LIST]`
   - `python -m coverage report --rcfile=/dev/null --include='*/strategies/betting_against_beta/data_loader.py' --show-missing`
   - `python -m pytest -q -k campaign_d`
   - Re-verify line→code for every target cluster at current SHA/blob. **Continue immediately.**

2. **Reduction gate (primary, evidence-first):** for each cluster, state whether any **new** mechanism satisfies strict 4 given B103–183/M149–M183/B186 + current code. If **any** cluster satisfies strict 4, implement the minimal production-realistic test(s) (new batch file only if needed), prove target-floor reduction in a fresh canonical aggregate, keep `322,326` and `campaign_d*`/batch148/149/172 green, then update `docs/unreachable_proofs.md` + this HANDOFF with exact commands/counts/lines. If **no** cluster satisfies strict 4, do **not** invent probe churn.

3. **If no reduction mechanism exists (expected):** produce a short, concrete **Batch 187 gate note** in `docs/unreachable_proofs.md` only if you found a genuinely new method to evaluate (not M149–M186 repeats) and record per-cluster strict-4 disposition + evidence. Otherwise, **stop after Step 0 + gate analysis** and refresh only this HANDOFF timestamp/state if needed — no fake progress, no probe spam.

4. **Forbidden:** status/planning/review/baseline-only exit presented as completion; M149–M186 repeats; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in a fresh canonical aggregate with exact commands/counts/miss lines, **OR** **(B)** documented strict-4 gate confirming no new reduction mechanism after B186 (and, only if a genuinely new method was evaluated, a `docs/unreachable_proofs.md` Batch 187 note with evidence). A session that only repeats prior probes or stops at baseline without (A)/(B) is blocked/inefficient.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T03:21Z** @ `cccc97c`.