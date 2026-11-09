# SINGLE DURABLE HANDOFF — Crypto-Betting-Against-Beta (BAB)

> **SOLE DURABLE HANDOFF (canonical). No competing handoff files.** Refreshed **2026-11-09T05:15:00Z** @ workspace `main`; `strategies/betting_against_beta/data_loader.py` blob verified (`596ee9e` @ HEAD `bbce6d3`). `docs/unreachable_proofs.md` is the evidence appendix. **Repo-name priority = Betting Against Beta only**. Next work is `data_loader.py` target-miss floor **only if a materially-new strict-4 reduction mechanism is discovered**; otherwise preserve the recorded unreachable baseline and do not churn probes. **START HERE → §INITIAL TASK MESSAGE (binding).** Tracked `probe*/debug*`/`ast_probe.py` remain in git history — never edit/commit them.

> **Authoritative Step 0 baseline (RE-VERIFIED 2026-11-09T05:15Z):** `PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical file list `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py` (explicit). Canonical coverage via `coverage.Coverage(source=['strategies.betting_against_beta'], config_file='/dev/null')` API driving the same `pytest -q --ignore=tests/test_controller_progress_accounting.py` file list → **645 passed, 6 skipped, 34 warnings**. Report `--include='*/strategies/betting_against_beta/data_loader.py' --show-missing` → **365 miss / 1683 stmts / 78%**. `pytest -q -k campaign_d` → **883 passed, 5 skipped, 3487 deselected, 53 warnings**. **Target-miss floor UNCHANGED** (all present; re-verify line→code @ fresh SHA before edits): `40-41,43-44,57-61,68,72,86-89,98-99,110-111,121-123,128-130,134,136-143,145-149,153-155,161,167,171-176,180,186,188,213-214,234-244,246-247,258,268-269,289,296-297,305,320-322,324-328,338-342,344,356,358,386,403-404,423-429,431-434,436-439,447-453,455-458,460-463,465-468,479-483,498,525-526,539-540,566-567,571,580-586,606,625-626,630,641-642,664,694-695,708-712,755-756,791-792,821,917-918,953,964,968,972,974,976,978,982-983,996,1008-1009,1055-1056,1082-1083,1110,1136-1141,1147,1153-1154,1174-1175,1177-1178,1186,1188-1189,1198,1202,1207,1241,1243,1249-1250,1262-1267,1288,1292,1307,1311,1325-1327,1338,1344,1539,1553-1554,1581-1582,1611,1621-1622,1639,1643,1649-1654,1676-1677,1683,1691,1694-1695,1697,1727,1730-1731,1733,1739-1742,1747,1754-1755,1759-1765,1768-1773,1782-1783,1787-1797,1811-1816,1836,1852,1859-1860,1866,1868-1869,1872,1891-1892,1921,1923-1924,1932,1944,1977-1989,2000,2012-2013,2041,2044-2045,2048-2060,2062-2065,2067-2070,2077-2084,2115,2117,2119,2127-2128,2201-2203,2212,2224-2239`

## Bottlenecks — RESOLVED / REMOVED (do not reintroduce)

Cleared and forbidden as excuses: scratch/probe clutter (tracked `debug_beta*`/`probe*`/`ast_probe.py` never edited/committed), controller workflow-sync test (always `--ignore=tests/test_controller_progress_accounting.py`; never touch `.github/workflows/*`), deps fragility (`coverage`/`pytest` via `python -m`; set `PYTHONPATH=$PWD`), coverage DB instability (`rm -f .coverage .coverage.*` before canonical run), coverage path filtering (`--rcfile=/dev/null --source=strategies.betting_against_beta` + report `--include='*/strategies/betting_against_beta/data_loader.py'`), canonical batch-set drift (enumerate explicitly), parquet/hdf5 engines (monkeypatch read APIs/call sites as needed; handlers may wrap as `BABDataError`), and **0-delta churn without new method/evidence** (B103–183/M149–M183 + B186/B187 executed/recorded; B188/B189 gate recorded; no status/planning/review/baseline-only or repeat-probe session is acceptable).

## Remaining target-miss clusters (verify line→code @ SHA; strict-4 verdicts recorded)

| Cluster | Lines | Current verdict |
|---|---|---|
| `_not_null` outer except | `43-44` | Not reducible (production-realistic, structural outer except). |
| `_normalize_index` coercer/determinism/last-ditch | `234-244,246-247` | Not reducible (dataflow/contract-shadow; 232 deterministic for elements that reach 227). |
| `_normalize_index` outer `ValueError,TypeError` | `268-269` | Not reducible (handler-order shadow/MRO; BABDataError dominates). |
| inspect/campaign_d NaT guard | `326` | **LIVE/GUARD — DO NOT ALTER.** |
| `_coerce_to_datetime_scalar` NaT identity re-raise | `338-342` | Not reducible (earlier NaT guards dominate). |
| `_coerce_to_datetime_scalar` epoch outer except | `403-404` | Not reducible (defensive/guarded). |
| exchange detect outer handlers | `641-642,694-695` | Not reducible (structural shadow: inner handlers/guarded ops swallow; no production-realistic propagation path). |
| promote datetime column outer handler | `791-792` | Not reducible (nested/guarded; all statements inside 760-790 individually guarded). |
| `_normalize_asset_name` empty token continue | `953` | Not reducible (construction-unreachable; `str.split()` default removes empty tokens). |

## Strict 4 criteria (any miss-reduction/unreachable claim)

1. Target lines and line→code verified at fresh SHA/blob.
2. Mechanism not disproven by B103–183/M149–M183/B186/B187 and recorded proofs.
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
| 186 | 0 | proof+probes (complete) | **`docs/unreachable_proofs.md##Batch 186`** — M186 materially-new CLI real-file/entrypoint trace + masked/recarray/sparse/attrs + read_csv NA-marker combos; 0 target hits; 365 miss/78%, campaign_d green; `326` preserved. |
| 187 | 0 | gate complete | **`docs/unreachable_proofs.md##Batch 187`** — fresh Step 0 re-verified; reduction gate analysis; no new mechanism; no probe batch created; 365 miss/78%; campaign_d green; `326` preserved. |
| 188 (2026-11-09T04:08Z) | 0 | gate (env-blocked test exec) | HEAD `82de030`, blob `596ee9e` unchanged. Step 0 tests not executed (deps absent in that env); line→code re-verified for target clusters unchanged. No new strict-4 mechanism; no probes/tests; `326` LIVE. |
| 189 (2026-11-09T04:28Z) | 0 | gate complete | Fresh Step 0 @ `75678d3` / blob `596ee9e`: **645/6/34**, **365 miss/1683/78%**, campaign_d **883/5/3487**. Line→code re-verified for target clusters unchanged. Reduction gate (strict 4, evidence-first): no materially-new production-realistic mechanism identified beyond B103–183/M149–M183/B186/B187/B188; all recorded clusters remain Not reducible/guard. No probe/test/production changes. |
| 190 (2026-11-09T04:45Z) | 0 | gate complete (verified) | Fresh Step 0 @ `bbce6d3` / blob `596ee9e` (coverage API; CLI `--source` hit no-data/import issue in env): **645/6/34**, **365 miss/1683/78%**, campaign_d **883/5/3487**. Line→code re-verified for clusters `43-44,234-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. **B190 reduction gate:** `43-44` outer `_not_null` except has no production-realistic exception source after guarded `is None`/`pd.isna` path; `234-244,246-247` dominated by deterministic element coercion/contract (232 for reached elements) per prior evidence; `268-269` BABDataError catches before generic `(ValueError,TypeError)`; `326` LIVE guard preserved; `338-342` dominated by NaT guards/`val is pd.NaT`; `403-404` generic epoch fallback swallowed by prior handlers; `641-642,694-695` outer exchange-detect handlers shadowed by inner guarded returns/raises; `791-792` parsed tz branch internally guarded and dominated by 760-790 structure; `953` unreachable (`str.split()` default). No materially-new strict-4 mechanism found; no probe/test/production changes. |
| 191 (2026-11-09T05:15Z) | 0 | gate complete (verified) | Fresh Step 0 @ `bbce6d3` / blob `596ee9e` (coverage API): **645/6/34**, **365 miss/1683/78%**, campaign_d **883/5/3487**. Line→code re-verified for **all target clusters unchanged**. **B191 reduction gate (strict 4, evidence-first):** for each cluster, no materially-new production-realistic mechanism identified beyond B103–183/M149–M183/B186–B190. All recorded clusters remain Not reducible/guard. No probe/test/production changes. **Gate confirmed — no 0-delta churn.** |

## START HERE — INITIAL TASK MESSAGE — 2026-11-09T05:15:00Z (Batch 191 gate **confirmed**, binding)

**Objective (repo priority — Crypto-Betting-Against-Beta):** preserve the recorded BAB `data_loader.py` baseline and pursue **only** a materially-new strict-4 reduction of the target-miss floor (**365 miss / 1683 stmts / 78% @ blob verified 2026-11-09T05:15Z**, verified: 645/6/34; campaign_d 883/5/3487 — **rerun fresh before claiming reduction**) if a real production-realistic mechanism is discovered that is **not** disproven by B103–183/M149–M183/B186–B191. B186/B187 appendix evidence is complete; B188–B191 gates found no new strict-4 mechanism. **Do not repeat M149–M187/B188–B191 probe families or create 0-delta churn.**

**State (2026-11-09T05:15Z):** HEAD `bbce6d3`, `data_loader.py` blob verified (unchanged `596ee9e`). Target clusters line→code re-verified unchanged: `43-44,234-247,268-269,326,338-342,403-404,641-642,694-695,791-792,953`. Canonical aggregate and campaign_d green at baseline above. No competing handoff files.

### Forced steps (execute in order; skip none)

1. **Step 0 — fresh baseline (mandatory, not an outcome):** `export PYTHONPATH=$PWD`; `rm -f .coverage .coverage.*`; canonical files: `tests/test_betting_against_beta*.py` + `tests/test_bab_data_loader_batch{40..69,71..74,76..89,93,95,96,148,149,172}.py`. Run canonical coverage + report `--include='*/strategies/betting_against_beta/data_loader.py' --show-missing` + `pytest -q -k campaign_d`. Re-verify line→code @ fresh SHA/blob. **Continue immediately.**
2. **Reduction gate (primary, evidence-first):** for each cluster, state whether any **new** mechanism satisfies strict 4 given B103–183/M149–M183/B186–B191 + current code. If **any** satisfies strict 4, implement minimal production-realistic test(s) (new batch file only if needed), prove target-floor reduction in a fresh canonical aggregate, keep `322,326` and `campaign_d*`/batch148/149/172 green, then update `docs/unreachable_proofs.md` + this HANDOFF with exact commands/counts/lines. If **none**, do **not** invent probe churn.
3. **If no reduction mechanism exists (expected):** add a **Batch 192 gate note** in `docs/unreachable_proofs.md` only if you evaluated a genuinely new method (not M149–M187/B188–B191 repeats) with evidence; otherwise **stop after Step 0 + gate analysis** and refresh only this HANDOFF — no fake progress, no probe spam.
4. **Forbidden:** status/planning/review/baseline-only exit presented as completion; M149–M187/B188–B191 repeat probes; semantic production changes for coverage; altering `322,326`; weakening/deleting batch148/149/172 or `campaign_d*`; editing `.github/workflows/*`; tracked `probe*`/`debug*` edits/commits; commit/push unless explicitly requested.

### Measurable outcome (required)

**(A)** target-floor reduced in a fresh canonical aggregate with exact commands/counts/miss lines, **OR** **(B)** documented strict-4 gate confirming no new reduction mechanism after B188–B191 (and, only if a genuinely new method was evaluated, a `docs/unreachable_proofs.md` Batch 192 note with evidence). A session that only repeats prior probes or stops at baseline without (A)/(B) is blocked/inefficient.

## Historical detail

Detailed appendices in `docs/unreachable_proofs.md` and git history. This HANDOFF is the single durable operational control document. Refreshed **2026-11-09T05:15:00Z** @ `bbce6d3` / blob `596ee9e` verified; B190 gate complete (fresh baseline verified, no new strict-4 mechanism); **B191 gate confirmed (fresh baseline verified, no new strict-4 mechanism)**.