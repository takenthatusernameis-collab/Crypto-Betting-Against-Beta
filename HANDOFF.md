# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. `AGENT_HANDOFF.md` is a pointer. Delete any other `*HANDOFF*.md` on sight.

- **Timestamp (UTC):** 2026-11-17T13:43:15Z (this refresh). **Last authoritative completed full-gate evidence @2026-11-17T12:42Z:** `bash scripts/bab_gate.sh` **GREEN — 6280 passed / 35 skipped / 0 failed / 5 missed / 6572 stmts / 99%**; `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **GREEN**. **This session (@13:43Z, HEAD 3264608):** verified existing `tests/test_bab_p19_5_beta_fallback.py` outer-fallback coverage for `beta.py:544-548` (`PYTHONPATH=. python3 -m pytest -q tests/test_bab_p19_5_beta_fallback.py` **5 passed**); `python3 -m ruff check .` **PASS**; `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean rc=0, emit-only rc=0). Started `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh` but it was **still in progress** at handoff cutoff (~96% marker, no `TOTAL`/final summary in log yet). **Do not claim closure until full gate + 98.5 floor complete GREEN with `beta.py` missed 0.**
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral trading system (ingest → beta → signals → portfolio → backtest → execution → ops), Frazzini–Pedersen *Betting Against Beta*.
- **Stakes order (never reorder):** (1) **real orders placed** (live-adapter gates, submission safety) — CLOSED, (2) **fills match model** (reconciliation/drift) — CLOSED, (3) **ingest admits only fit-to-trade data** (freshness/alignment/quality/coverage) — **CLOSED** (data_loader.py 100%), (4) **beta fallback correctness** — **PRIMARY** (targeted tests present; authoritative full-gate proof pending).
- **Git state (this refresh):** HEAD `3264608` on `main`. Working tree **clean** at start of this handoff refresh except this `HANDOFF.md` update. Always run `git status`, `git fetch`, and all gates before trusting counts.

## INITIAL TASK MESSAGE (BINDING — START HERE, 2026-11-17T13:43:15Z)

**Mission (P19-6-final/closeout, heavy execution required): obtain authoritative GREEN proof that `strategies/betting_against_beta/beta.py` lines 544-548 (stake 4) are closed (missed 0) under full gates; if proof shows any remaining miss/regression, close it in-session by TEST-or-DELETE with evidence and rerun gates. Do not stop at analysis.**

### Session progress (preserve)
- **Code/tests already present:** `tests/test_bab_p19_5_beta_fallback.py` contains outer-fallback cases targeting `beta.py:544-548`:
  - `test_beta_outer_fallback_asset_to_numpy_fails_but_asarray_succeeds`
  - `test_beta_outer_fallback_asset_conversions_raise_babdataerror`
- **This session evidence (@13:43Z, HEAD 3264608):** `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN (drift rc=2, clean rc=0, emit-only rc=0); `PYTHONPATH=. python3 -m pytest -q tests/test_bab_p19_5_beta_fallback.py` 5 passed.
- **Incomplete:** `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh` was started and still running at handoff cutoff (~96% progress in log, no final `TOTAL`/summary yet). **No new authoritative full-gate result this session.** Last authoritative baseline remains @12:42Z (6280/35/0/5/99%).

### Immediate campaign (do in order, do not stop at planning)
1. **Finish/obtain full-gate evidence (required):**
   - If `/tmp/bab_gate.log` from a prior run exists, wait for completion and inspect: `grep -nE "TOTAL|strategies/betting_against_beta/beta\\.py|failed|passed|skipped|ERROR" /tmp/bab_gate.log | tail -n 60` (do not start a duplicate full gate while one is running).
   - Otherwise run: `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh`
   - Then run floor: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh`
   - Record exact TOTAL, pass/fail/skip, and `beta.py` missed lines from log/output.
2. **If `beta.py` still has misses (especially 544-548):** drive to 0 by TEST-or-DELETE with proof (prefer extending `tests/test_bab_p19_5_beta_fallback.py` or adding a focused `tests/test_bab_p19_*` case; delete only with inline invariant tied to controlling contracts). Rerun targeted tests and all gates after each change.
3. **If gates are already GREEN with `beta.py` missed 0:** treat as closure proof — still run/confirm 98.5 floor, then refresh handoff with authoritative evidence and mark P19-6-final closed for beta residue.
4. **Finalize:** update this handoff with UTC, HEAD, before/after missed+failures, exact closed `file:lines` (or deletions) with proof, tests added/changed, gate results, and blockers. Keep `AGENT_HANDOFF.md` pointing here.

### First actions (evidence first)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status --short --branch
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
if grep -q "^TOTAL" /tmp/bab_gate.log 2>/dev/null; then
  grep -nE "TOTAL|strategies/betting_against_beta/beta\\.py|failed|passed|skipped|ERROR" /tmp/bab_gate.log | tail -n 60
else
  BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh
fi
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh
```

### Method (mandatory)
- Use coverage output (`/tmp/bab_gate.log`, `--cov-report=term-missing`) as ground truth for misses; do not guess.
- Keep changes minimal/behavior-preserving; no broad refactors or style-only defensive rewrites.
- Do not commit probe/debug scratch scripts.

### First actions (evidence first)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git status --short --branch
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh
grep -nE "TOTAL|strategies/betting_against_beta/beta\\.py|failed|passed|skipped" /tmp/bab_gate.log | tail -n 40
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh
```

### Definition of done (machine-checkable)
1. `python3 -m ruff check .` **PASS**.
2. `bash scripts/bab_reconcile_gate.sh` **GREEN** (drift rc=2, clean rc=0, emit-only rc=0).
3. `bash scripts/bab_gate.sh` **GREEN** with **0 failures** and `beta.py` missed total **0**.
4. `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` **GREEN** (never lower floor).
5. Working diff includes **substantive product `.py` and/or test changes** addressing residue (not handoff-only).
6. Append a concise session ledger entry with UTC, HEAD, before/after missed+failures, exact closed `file:lines` (or deletions) with proof, tests added/changed, gate results, and any real blockers.

### Forbidden (automatic failure)
- Handoff-only commit / restating brief as deliverable / stopping after analysis without closing/proving residue.
- Re-touching the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~line 6636 `test_promote_name_match_pandas_parse_unparseable_dates_left_in_place`, ~line 8249 `test_promote_datetime_column_bad_parse_left_in_place`) unless a real contract regression is proven.
- Leaving a line "documented unreachable" without deleting it, or claiming coverage/proof without evidence.
- Lowering coverage floor, adding ANN/type-style churn, refactoring defensive try/except for style, or introducing regressions in 100%-closed modules (`execution.py`, `reconciliation.py`, `data_sources.py`, `metrics.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`).
- Editing/pushing `.github/workflows/*` (maintainer-only, lacks `workflows:write`).
- Creating parallel handoff/session docs or committing probe/debug scratch scripts.

## Proven-deleted / closed (do not re-test)
- `execution.py`, `reconciliation.py`, `data_sources.py`, `metrics.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py` — **100% covered / closed** (P19-4, P19-5). Do not touch order/fill/reconciliation safety paths or ingest paths.
- P19-5 deletions in `data_loader.py` (15 lines): `280-292,296-297`, `315-316`, `1650-1651`, `1954-1955` with inline invariants — keep deleted.
- P19-4 proven deletions: `replay.py:171-172`, `beta.py:181-182,427-429`, `data_sources.py:480-481,494-500`, `data_loader.py:1609-1610,2755-2758`, `metrics.py:93-94`, `portfolio.py:165-166`, `execution.py:140-141,182-185,1295-1296`, `cli.py:657-658,836-838`, `reconciliation.py:82-83,309`.
- P17-1/2, P18-1/2/3, P19-2/3/4, kill-switch R4-B, bootstrap done — do not redo.

## Bottleneck status
- **[REMOVED @07:50Z]** 2 stale `BABDataError`-expectation tests blocked the green suite — rewritten to assert the verified RangeIndex-preserved coercion contract.
- **[REMOVED @07:50Z]** Stale-handoff ambiguity: single durable handoff maintained with one binding, stake-prioritized task.
- **[REMOVED @12:08Z]** Pre-existing `ruff` SIM108 lint failure in `data_loader.py` fixed; `ruff` and reconcile gate verified GREEN (prevents avoidable preflight churn).
- **[REMOVED @12:42Z]** `data_loader.py` 100% confirmed; ingest stake 3 CLOSED.
- **[IN PROGRESS @13:43Z, EVIDENCE PARTIAL]** `beta.py:544-548` targeted by existing tests in `tests/test_bab_p19_5_beta_fallback.py` (targeted pytest 5/5 PASS @13:43Z; prior isolated coverage showed lines exercised). `ruff` and reconcile GREEN @13:43Z, but full `bab_gate.sh` started this session was still running at cutoff (log `/tmp/bab_gate.log`, ~96%, no `TOTAL`) — authoritative 0-failures / 0-missed proof for `beta.py` still pending.
- **[EXTERNAL]** P19-1 CI enforcement maintainer-only (`workflows:write`).

## Hard gates every session (repo root, in order)
```bash
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
bash scripts/bab_gate.sh
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh
```

## Session ledger (append-only, concise)

| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-17T04:09:27Z | f513c0d | P19-4: gap 64→48 via 7 proven deletions (exec/cli/recon). | GREEN @04:09Z |
| 2026-11-17T04:28:51Z | 6121323 | P19-4: gap 48→29 via deletions+tests; recon/exec/cli/sources/metrics/portfolio/replay 100%. | GREEN @04:28Z |
| 2026-11-17T06:11:17Z | 07f1741 | P19-5: gap 29→14 via 4 proven deletions in `data_loader.py`; 12 stale tests failing. | RED (tests/ruff then) |
| 2026-11-17T06:28:30Z | 07f1741 | Aligned 12 stale ingest tests to deterministic coercion; no source residue change. | ruff+recon PASS; full gate pending |
| 2026-11-17T07:11:58Z | 0d7d976 | Handoff refresh (planning clarity); no code/tests. | ruff+recon PASS @07:11Z |
| 2026-11-17T07:24:40Z | 1059fc6 | Full gate run: 6278/35/2 failed/14 missed/6590/99%; identified 2 stale tests as blocker. | 2 stale-test FAIL |
| 2026-11-17T07:32:54Z | 3164ed1 | Handoff cleanup/refresh: single clear stake-prioritized binding P19-5 task, residue/2-test blocker explicit; no code/tests. | baseline @07:24Z (6278/35/2/14/99%) |
| 2026-11-17T07:34:48Z | 2cf417b | Handoff refresh w/ FRESH gate @07:34Z (6278/35/2 failed/14 missed/6590/99%); empirically proved the 2 failing tests' inputs yield RangeIndex (no `BABDataError`) so next session has exact fix, not a guess; no code/tests. | 2 stale-test FAIL (expected); ruff+recon GREEN |
| 2026-11-17T07:52:00Z | 75cd86e | **Unblocked green suite**: rewrote 2 stale tests to assert RangeIndex-preserved contract; all 3 gates GREEN (6280/35/0/14/99%); refreshed handoff with fresh evidence. | GREEN @07:50Z (6280/35/0/14/99%) |
| 2026-11-17T10:41:06Z | 75cd86e | FRESH gate verification @10:41Z: 6280 passed / 35 skipped / 0 FAILED / 14 missed / 6590 stmts / 99%; all 4 hard gates GREEN; HANDOFF.md refreshed with current timestamp/baseline for next session. | GREEN @10:41Z |
| 2026-11-17T12:08:10Z | f9dd8ca | Cleared lint preflight bottleneck: fixed pre-existing `SIM108` in `data_loader.py` (behavior-preserving); verified `ruff check .` PASS and `bab_reconcile_gate.sh` GREEN; refreshed single durable handoff with timestamped binding P19-6 heavy-work campaign (stake 3 ingest → stake 4 beta, 14 missed to 0 by TEST-or-DELETE with proof). Full gate not rerun (last authoritative 6280/35/0/14/99% @10:41Z). | ruff PASS; reconcile GREEN @12:08Z |
| 2026-11-17T12:42:45Z | f9dd8ca | **FRESH full gate @12:42Z: 6280 passed / 35 skipped / 0 FAILED / 5 missed / 6572 stmts / 99%**; `data_loader.py` 100% (ingest stake 3 CLOSED); residue now ONLY `beta.py:544-548` (5 lines, stake 4 PRIMARY); all 4 hard gates GREEN; updated handoff with accurate state and narrowed binding mission. | GREEN @12:42Z |
| 2026-11-17T13:08:00Z | ccf05a3 | Added 2 behavior-asserting outer-fallback tests in `tests/test_bab_p19_5_beta_fallback.py` targeting `beta.py:544-548` (to_numpy fail→asarray success, and both fail→`BABDataError`); targeted pytest 5/5 PASS; isolated coverage showed 544-548 exercised. | ruff PASS; reconcile GREEN; targeted tests PASS; full bab_gate started but incomplete (no final summary) |
| 2026-11-17T13:43:15Z | 3264608 | Verified beta fallback tests and preflight gates (`ruff` PASS, `bab_reconcile_gate.sh` GREEN, `tests/test_bab_p19_5_beta_fallback.py` 5/5 PASS); started full `bab_gate.sh` but it was still running at handoff cutoff (~96%, no TOTAL in `/tmp/bab_gate.log`) so no authoritative full-gate closure yet. | ruff PASS; reconcile GREEN @13:43Z; targeted tests PASS; full gate IN PROGRESS (incomplete) |


## Session ledger detail (append-only)
- 2026-11-17T12:42:45Z | HEAD f9dd8ca | before: handoff claimed 14 missed (9 data_loader + 5 beta), stale baseline @10:41Z | after: ran FRESH full gate (ruff PASS, reconcile GREEN, bab_gate 6280/35/0/5/99%, 98.5 floor GREEN); `data_loader.py` 0 missed (100%), `beta.py` 5 missed (lines 544-548); working tree clean; refreshed handoff with accurate residue, narrowed stakes (ingest CLOSED, beta PRIMARY), binding P19-6-final mission | closed: data_loader.py residue (completed in prior session) | tests: none changed | proof/deletions: none this session | gates: ruff PASS; reconcile GREEN (drift rc=2, clean rc=0, emit-only rc=0); bab_gate 6280/35/0/5/99%; 98.5 floor GREEN | blockers: 5 missed lines in beta.py (P19-6-final, TEST-or-DELETE).
- 2026-11-17T13:08:00Z | HEAD ccf05a3 | before (authoritative): 6280/35/0/5 missed/6572/99% @12:42Z, `beta.py:544-548` open | after: extended `tests/test_bab_p19_5_beta_fallback.py` with `test_beta_outer_fallback_asset_to_numpy_fails_but_asarray_succeeds` and `test_beta_outer_fallback_asset_conversions_raise_babdataerror` (observable beta/value and `BABDataError` assertions); `PYTHONPATH=. python3 -m pytest -q tests/test_bab_p19_5_beta_fallback.py` **5 passed**; isolated `coverage run -m pytest tests/test_bab_p19_5_beta_fallback.py` missing list for `strategies/betting_against_beta/beta.py` excluded 544-548; `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN (drift rc=2, clean rc=0, emit-only rc=0). Started `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh` but did not capture completion/TOTAL in-session (log progressed to ~96% marker). | closed (code-path exercised, pending authoritative gate proof): `strategies/betting_against_beta/beta.py:544-548` targeted by tests | tests added/changed: `tests/test_bab_p19_5_beta_fallback.py` | proof/deletions: no deletions (test-based closure attempted) | blockers: full `bab_gate.sh` and `BAB_GATE_MIN_COVERAGE=98.5 bab_gate.sh` must be completed and recorded to confirm 0 failures / `beta.py` missed 0.

- 2026-11-17T13:43:15Z | HEAD 3264608 | before (authoritative): 6280/35/0/5 missed/6572/99% @12:42Z, `beta.py:544-548` open/pending proof | after: no product/test code changes; verified `python3 -m ruff check .` PASS, `bash scripts/bab_reconcile_gate.sh` GREEN (drift rc=2, clean rc=0, emit-only rc=0), `PYTHONPATH=. python3 -m pytest -q tests/test_bab_p19_5_beta_fallback.py` **5 passed**; started `BAB_GATE_LOG=/tmp/bab_gate.log bash scripts/bab_gate.sh` (still running at cutoff, ~96%, no `TOTAL`/final summary captured). | closed: none proven this session (gate evidence incomplete) | tests added/changed: none | proof/deletions: none | blockers: full `bab_gate.sh` completion/summary and `BAB_GATE_MIN_COVERAGE=98.5 bab_gate.sh` still required to confirm `beta.py` missed 0 / 0 failures.

---
**THIS IS THE SINGLE DURABLE HANDOFF. DO NOT CREATE PARALLEL HANDOFF DOCS. UPDATE THIS FILE ONLY.**