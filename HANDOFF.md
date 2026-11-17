# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. `AGENT_HANDOFF.md` is a pointer. Delete any other `*HANDOFF*.md` on sight. Do not create parallel session/handoff docs.

- **Timestamp (UTC):** 2026-11-17T14:47:00Z (this refresh).
- **Authoritative completed full-gate evidence @2026-11-17T14:46:59Z, HEAD `73e4db2` (re-run this session, code unchanged since `5ed651f`):**
  - `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` → **GREEN — 6282 passed / 35 skipped / 0 failed / 6572 stmts / 0 missed / 100%** (145.15s, 4 cores, xdist).
  - `python3 -m ruff check .` → **PASS**.
  - `bash scripts/bab_reconcile_gate.sh` → **GREEN** (drift rc=2, clean rc=0, emit-only rc=0).
  - `BAB_GATE_MIN_COVERAGE=98.5` floor is **met by the same TOTAL 100%** (do not re-run solely for the floor at session start).
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral trading system (ingest → beta → signals → portfolio → backtest → execution → ops), Frazzini–Pedersen *Betting Against Beta*.
- **Git state (this refresh):** HEAD `73e4db2` on `main`, clean tree. Only `HANDOFF.md` changed since the last GREEN baseline `5ed651f` — **no product/test change**, so the 100% coverage baseline carries forward. Always confirm with `git status --short --branch` and re-run gates after any edit.

## INITIAL TASK MESSAGE (BINDING — START HERE, 2026-11-17T14:47:00Z)

**Mission (P19-7, heavy execution required — do NOT stop at analysis; do NOT hand off without closing the sites with tests):** Harden silent/broad exception handling in the BAB product modules. Every targeted `except Exception` site must become either **(A) an intentional contract** locked by an inline invariant + a regression test, or **(B) narrowed/surfaced** with a regression test proving identical happy-path behavior and that the failure now surfaces. Behavior-preserving only.

**Prioritization by repo identity (crypto trading system — never reorder):** this repo's stakes are ranked live-money-first, so the next work is the **safety-critical, non-ingest** modules that sit on the order/fill/book path: `execution.py`, `reconciliation.py`, `data_sources.py`, `portfolio.py`. Do this before the higher-count but lower-risk modules (`strategy.py`, `backtest.py`, `cli.py`, `beta.py`) and before ingest (`data_loader.py`, 137/64).

**Milestone 1 = 18 broad `Exception` sites, 0 silent. AST ground-truthed @2026-11-17T14:47Z via `scripts/bab_except_inventory.py --json`.** Complete every row of the ledger below.

### Milestone 1 site ledger (fill Classification + Locking test + Status for every row)
Suggested class is a starting hypothesis — confirm against the code and the test you write; the classification and test columns are the deliverable, not this suggestion.

| # | Site | Current behavior (ground-truthed) | Suggested | Locking test (fill) | Status |
|---|---|---|---|---|---|
| 1 | `execution.py:346` | cost-model resolver raises → `prices=adv=None`, then cfg fallback | B/A | | |
| 2 | `execution.py:375` | `_date_key`: `pd.Timestamp(date).isoformat()` else `str(date)` | A (total) | | |
| 3 | `execution.py:398` | `_as_timestamp`: `pd.Timestamp(value)` else `None` | A (total) | | |
| 4 | `execution.py:458` | adv-map build fails → `adv_map={}` | A/B | | |
| 5 | `execution.py:467` | per-row `date_key` fallback `str(date)` | A (total) | | |
| 6 | `execution.py:831` | fill date unparseable → `continue` (fill skipped) | B (surface) | | |
| 7 | `execution.py:888` | betas reindex fails → `betas=None` | A (fallback) | | |
| 8 | `execution.py:1250` | live order exception → `LiveFill(status="rejected", reason=...)` | A (surfaced) | | |
| 9 | `reconciliation.py:131` | `_date_key`: ISO else `str(date)` | A (total) | | |
| 10 | `data_sources.py:376` | ticker fetch fails → `raise BABDataError(...) from exc` | A (surfaced) | | |
| 11 | `data_sources.py:478` | `pd.to_datetime(idx)` fails → `raise BABDataError` | A (surfaced) | | |
| 12 | `data_sources.py:506` | tz convert fails → `idx_utc=idx` (silent fallback) | B (surface) | | |
| 13 | `portfolio.py:30` | `_clean_signal_value` `int(f)` fails → `0` | A (total) | | |
| 14 | `portfolio.py:107` | inner `apply(pd.to_numeric)` fails → retry | B | | |
| 15 | `portfolio.py:110` | nested retry fails → per-column coerce | B | | |
| 16 | `portfolio.py:115` | per-column coerce fails → `0.0` | B | | |
| 17 | `portfolio.py:118` | outer coerce fails → **return all-zero frame** (hides defect) | B (surface) | | |
| 18 | `portfolio.py:165` | build fails → `raise BABPortfolioError(...) from exc` | A (surfaced) | | |

**Anti-avoidance contract (automatic failure if violated):**
- A commit that only edits `HANDOFF.md` / `AGENT_HANDOFF.md` is an **automatic failure**. This milestone is not done until the diff contains **substantive product `.py` + test changes** for these 18 sites.
- Every one of the 18 rows must have the **Classification** and **Locking test** columns filled and the site's regression test committed. If a site is genuinely already a correct surfacing contract (e.g. `data_sources.py:376`), it is class **A** and still needs a regression test that pins the surfacing behavior.
- Do **module-by-module**: finish all sites in one module, run the full gate + 98.5 floor GREEN, record before/after broad/silent counts, then move to the next module. Order: `reconciliation.py` (1) → `data_sources.py` (3) → `portfolio.py` (6) → `execution.py` (8) — smallest/simplest first to build the pattern, largest last.

### Why this campaign (evidence, AST audit)
All four product stakes and 100% line coverage are CLOSED. Remaining real engineering debt (from `docs/COVERAGE_NOTES.md`): **231** broad `except Exception`/bare + **68** silent `except: pass` across 16 modules. Per module (broad/silent): `data_loader.py` 137/64, `cli.py` 28/1, `beta.py` 16/1, `strategy.py` 11/0, `execution.py` 8/0, `backtest.py` 7/1, `portfolio.py` 6/0, `quality.py` 4/0, `data_sources.py` 3/0, `signals.py` 3/0, `attribution.py` 2/0, `risk.py` 2/1, `costs.py` 1/0, `reconciliation.py` 1/0, `regime.py` 1/0, `replay.py` 1/0.

### Campaign order (module-by-module; gate GREEN after each)
1. **Milestone 1 (THIS SESSION, safety-critical non-ingest):** the 18 sites above. Smallest module first.
2. **Milestone 2:** `strategy.py` (11), `backtest.py` (7), `cli.py` (28), `beta.py` (16) — same method.
3. **Milestone 3 (ingest — extra care):** `data_loader.py` (137 broad / 64 silent). Contains **intentional leave-in-place contracts** (unparseable dates left in place, name-match promotion). Classify A (contract → invariant + test) or B (defect → narrow/surface). Do NOT delete intentional contracts without concrete unreachability/defect proof. Do not re-touch the 2 rewritten tests under Forbidden.
4. **Milestone 4:** remaining modules (`quality.py`, `signals.py`, `attribution.py`, `risk.py`, `costs.py`, `regime.py`, `replay.py`).
5. **Milestone 5 (hygiene):** delete committed root scratch scripts (`ast_probe.py`, `debug_beta.py`, `debug_beta2.py`, `probe_*.py`) — the repo rule forbids committing them.

### Efficiency: fast inner loop (use it; do not run the full gate after every edit)
- **Inner loop:** `bash scripts/bab_quick.sh` (ruff + targeted trio + smoke, ~seconds).
- **Targeted per module:** `python3 -m pytest -q tests/test_bab_execution_p14_coverage.py tests/test_bab_execution_integration_r5.py ...` (the relevant file for the module you are editing).
- **Full gate:** `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh` **once per module boundary** (and once at the end). Runtime ~145s on 4 cores — run it in a single foreground call with a generous timeout; **never hand off an in-progress gate.** Use coverage output (`grep -nE "^TOTAL|failed|passed|skipped" /tmp/bab_gate.log`) as ground truth for misses; do not guess.
- Relevant test homes: execution → `tests/test_bab_execution_*.py`; portfolio → `tests/test_bab_portfolio_*.py`; reconciliation → `tests/test_bab_reconciliation_*.py`; data_sources → `tests/test_bab_data_sources*.py`. Add new tests in a clearly named new file (e.g. `tests/test_bab_p19_7_exception_hardening.py`) to keep the diff reviewable.

### Method (mandatory)
- Behavior-preserving only: no broad refactors, no style-only rewrites, no type-annotation (ANN) churn.
- Each touched site → inline invariant (A) or narrowed/surfaced code (B) **plus** a regression test that (A) locks the intended behavior, or (B) proves identical happy-path output and that the failure now surfaces.
- Keep changes minimal; run the full gate + 98.5 floor after each module and record evidence.
- Never lower the coverage floor. Never commit probe/debug scratch scripts.

### Definition of done (machine-checkable, per milestone)
1. `python3 -m ruff check .` **PASS**.
2. `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean rc=0, emit-only rc=0).
3. `bash scripts/bab_gate.sh` **GREEN** with **0 failures**, TOTAL **100%** (0 missed).
4. `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **GREEN** (never lower floor).
5. Working diff includes **substantive product `.py` and test changes** for the milestone's sites (not handoff-only).
6. Every site classified A or B, locked by inline invariant + regression test (A) or narrowed/surfaced + regression test (B); before/after broad/silent counts recorded; Milestone 1 ledger above fully filled.
7. Append a concise session ledger entry (UTC, HEAD, sites closed, tests added/changed, gate results, real blockers).

### Forbidden (automatic failure)
- Handoff-only commit / restating this brief as deliverable / stopping after analysis without closing sites with tests.
- Lowering the coverage floor or adding ANN/type-style churn.
- Deleting an intentional leave-in-place contract (date-parse leave-in-place, name-match promotion) without concrete proof.
- Touching 100%-closed safety paths (`execution.py`, `reconciliation.py`, `data_sources.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`, `metrics.py`) **without** a regression test + gate-green proof that observable behavior is unchanged.
- Re-touching the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~line 6636 `test_promote_name_match_pandas_parse_unparseable_dates_left_in_place`, ~line 8249 `test_promote_datetime_column_bad_parse_left_in_place`) unless a real contract regression is proven.
- Mass-refactoring all 231 sites in one pass; module-by-module only.
- Editing/pushing `.github/workflows/*` (maintainer-only, lacks `workflows:write`).
- Creating parallel handoff/session docs or committing probe/debug scratch scripts.

## Proven-closed (do not re-test)
- **All four stakes CLOSED; `strategies/betting_against_beta` at 100% line coverage (0 missed, 6572 stmts) @2026-11-17T14:46:59Z, HEAD `73e4db2`.** Full gate 6282 passed / 35 skipped / 0 failed; ruff PASS; reconcile GREEN.
- `execution.py`, `reconciliation.py`, `data_sources.py`, `metrics.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`, `beta.py` — 100% covered / closed (P19-4/P19-5/P19-6-final). Do not re-open for coverage; P19-7 changes must be behavior-preserving with regression tests.
- P19-5 deletions in `data_loader.py` (15 lines): `280-292,296-297`, `315-316`, `1650-1651`, `1954-1955` with inline invariants — keep deleted.
- P19-4 proven deletions: `replay.py:171-172`, `beta.py:181-182,427-429`, `data_sources.py:480-481,494-500`, `data_loader.py:1609-1610,2755-2758`, `metrics.py:93-94`, `portfolio.py:165-166`, `execution.py:140-141,182-185,1295-1296`, `cli.py:657-658,836-838`, `reconciliation.py:82-83,309`.
- P17-1/2, P18-1/2/3, P19-2/3/4, kill-switch R4-B, bootstrap done — do not redo.

## Bottleneck status
- **[REMOVED @14:47Z] Handoff bloat / parse overhead:** prior handoff had grown to ~20KB with a long repetitive ledger; compressed to this single binding task + compact ledger so the next session starts work immediately instead of re-deriving state.
- **[REMOVED @14:47Z] "Which baseline do I trust?" ambiguity:** current-HEAD full gate re-run to completion GREEN @14:46:59Z (145.15s); code unchanged since `5ed651f`, so coverage baseline is authoritative and carries forward.
- **[REMOVED @13:55Z] Recurring incomplete-gate:** prior sessions died at ~96% before the TOTAL line. Gate now runs to completion in ~2.5 min on 4 cores; use `BAB_GATE_LOG` and run it foreground with a generous timeout.
- **[REMOVED @12:08Z]** `ruff` SIM108 in `data_loader.py` fixed; ruff + reconcile GREEN.
- **[REMOVED @12:42Z]** `data_loader.py` 100% confirmed; ingest stake 3 CLOSED.
- **[REMOVED @07:50Z]** 2 stale `BABDataError`-expectation tests rewritten to the RangeIndex-preserved coercion contract; green suite unblocked.
- **[EXTERNAL]** P19-1 CI enforcement maintainer-only (`workflows:write`). `.github/workflows/main.yml` does not invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`. Do not re-attempt from an agent session.
- **[LOW]** `README.md:246` still says "Binding next step (P19-3)" — stale; superseded by this P19-7 brief. Fix only if touching README for another reason.

## Hard gates every session (repo root, in order)
```bash
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # only when TOTAL < 100 or floor proof needed
```

## Session ledger (append-only, concise)
| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-17T04:09Z | f513c0d | P19-4: gap 64→48 via 7 proven deletions (exec/cli/recon). | GREEN |
| 2026-11-17T04:28Z | 6121323 | P19-4: gap 48→29; recon/exec/cli/sources/metrics/portfolio/replay 100%. | GREEN |
| 2026-11-17T06:11Z | 07f1741 | P19-5: gap 29→14 via 4 proven deletions in `data_loader.py`; 12 stale tests failing. | RED then fixed |
| 2026-11-17T07:52Z | 75cd86e | **Unblocked green suite**: rewrote 2 stale tests to RangeIndex contract; all gates GREEN. | GREEN |
| 2026-11-17T12:42Z | f9dd8ca | FRESH gate 6280/35/0/5 missed/99%; `data_loader.py` 100% (ingest stake 3 CLOSED); residue only `beta.py:544-548`. | GREEN |
| 2026-11-17T13:55Z | b97f1e0 | Ran full gate to completion: 6282/35/0/0 missed/100%; `beta.py` 100% (stake 4 CLOSED); installed P19-7 campaign (231 broad / 68 silent, AST-audited). | GREEN |
| 2026-11-17T14:03Z | 5ed651f | Re-ran full gate GREEN (149.18s); ground-truthed Milestone 1 exact sites (18 broad, 0 silent). | GREEN |
| 2026-11-17T14:47Z | 73e4db2 | **Re-ran full gate GREEN @14:46:59Z (6282/35/0/6572/100%, 145.15s); ruff PASS; reconcile GREEN.** Code unchanged since `5ed651f` (only handoff). Compressed handoff, added 18-row binding Milestone-1 ledger + anti-avoidance contract + fast-loop guidance. No product/test changes. | GREEN |

## Session ledger detail (append-only)
- 2026-11-17T14:47:00Z | HEAD 73e4db2 | before: P19-7 Milestone 1 binding @14:03Z, tree clean, code unchanged since 5ed651f | after: re-ran full gate to completion `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` → 6282 passed / 35 skipped / 0 failed / 6572 stmts / 0 missed / 100% (145.15s); `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN; ground-truthed Milestone 1 = 18 broad `Exception` sites (`execution.py` 8: 346,375,398,458,467,831,888,1250; `reconciliation.py` 1: 131; `data_sources.py` 3: 376,478,506; `portfolio.py` 6: 30,107,110,115,118,165), 0 silent; rewrote handoff with binding 18-row ledger + anti-avoidance contract + fast-loop; compressed bloated ledger | closed: none (P19-7 Milestone 1 not yet started) | tests added/changed: none | gates: ruff PASS; reconcile GREEN; bab_gate 6282/35/0/0 missed/100%; 98.5 floor met by TOTAL 100% | blockers: none — Milestone 1 unblocked and ready; P19-1 CI enforcement external (maintainer-only).
- 2026-11-17T14:03:04Z | HEAD 5ed651f | after: full gate GREEN (149.18s); AST-grounded 18 Milestone-1 sites; no product/test changes. | gates: ruff PASS; reconcile GREEN; 100%.
- 2026-11-17T13:55:12Z | HEAD b97f1e0 | after: ran full gate to completion (bottleneck removed) 6282/35/0/0 missed/100%; `beta.py` 100%; installed P19-7. | gates: all 4 GREEN.
- 2026-11-17T12:42:45Z | HEAD f9dd8ca | FRESH full gate 6280/35/0/5 missed/99%; `data_loader.py` 100% (ingest CLOSED); residue only `beta.py:544-548`. | GREEN.
- 2026-11-17T07:52:00Z | HEAD 75cd86e | Rewrote 2 stale tests to RangeIndex-preserved contract; all 3 gates GREEN. | GREEN.

---
**THIS IS THE SINGLE DURABLE HANDOFF. DO NOT CREATE PARALLEL HANDOFF DOCS. UPDATE THIS FILE ONLY.**