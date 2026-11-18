# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. `AGENT_HANDOFF.md` is a pointer. Delete any other `*HANDOFF*.md` on sight. Do not create parallel session/handoff docs.

- **Timestamp (UTC):** 2026-11-18T02:02:19Z (this refresh; verified on live HEAD).
- **Latest verified checks @2026-11-18T02:02Z, HEAD `ce1034f` (checkpoint past `94954b8`; `git diff --name-only 94954b8 ce1034f` → `HANDOFF.md`, `AGENT_HANDOFF.md` ONLY — zero product/test change), clean working tree:**
  - `python3 -m ruff check .` → **PASS** (re-run live).
  - `bash scripts/bab_reconcile_gate.sh` → **GREEN** (re-run live; drift rc=2, clean rc=0, emit-only rc=0).
  - `bash scripts/bab_quick.sh` → **GREEN** (re-run live; ruff + targeted trio 104 passed + smoke 195 passed).
  - `python3 scripts/bab_except_inventory.py` → **223 broad / 68 silent** across 16 product modules (counts unchanged — work is inline invariants + regression tests, not count reduction).
- **Authoritative full-gate evidence @HEAD `94954b8` (applies at `ce1034f` — no product/test change since):** `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` → **GREEN — 6379 passed / 35 skipped / 0 failed / 6562 stmts / 0 missed / 100%** (134.21s). Coverage floor 98.5 met by TOTAL 100%.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral trading system (ingest → beta → signals → portfolio → backtest → execution → ops), Frazzini–Pedersen *Betting Against Beta*.
- **Git state (this refresh):** HEAD `ce1034f` on `main`, clean working tree (checkpoint past green baseline; only handoff files differ from `94954b8`).

## INITIAL TASK MESSAGE (BINDING — START HERE, 2026-11-18T02:02:19Z)

**MANDATORY MISSION — close Milestone 3 module `data_loader.py` (137 broad / 64 silent) THIS session with committed regression tests. This is heavy work and is not optional.**

**Inferred from the repo identity (crypto live-money trading system, Frazzini–Pedersen *Betting Against Beta*):** the highest-value remaining engineering debt is the **ingest pipeline's exception hardening**. All four product stakes are CLOSED at 100% coverage — (1) live orders placed, (2) fills vs model, (3) ingest fit-to-trade, (4) beta fallback — and Milestones 1–2 are COMPLETE (see ledger). The single largest concentrated debt sits in `data_loader.py` (**137 broad / 64 silent**): this is the ingest gate that decides whether a bar/ticker/OHLCV frame is fit to trade. A swallowed parse or schema failure here silently degrades every downstream signal. **Closing `data_loader.py` is the heaviest remaining item and the explicit next focus of this campaign.**

**Ground truth — already DONE, do NOT redo:**
- **Milestone 1 (18/18 sites):** `execution.py` (8), `reconciliation.py` (1), `data_sources.py` (3), `portfolio.py` (6) — inline invariants + regression tests, all PASS (ledger below).
- **`strategy.py` (11 broad / 0 silent):** inline invariants at lines `318,375,385,400,425,536,539,833,836,1014,1027` + 12 tests in `tests/test_bab_p19_7_strategy_exceptions.py` (PASS; 473 stmts / 100%).
- **`backtest.py` (7 broad / 1 silent):** inline invariants at lines `144,155,211,252,267,286,314` (silent `211`) + 20 tests in `tests/test_bab_p19_7_backtest_exceptions.py` (PASS; 144 stmts / 100%).
- **`cli.py` (28 broad / 1 silent):** inline invariants at lines `99,209,288,328,333,340,559,632,639,684,689,731,737,750,806,816,821,841,871,876,889,903,924,961,978,993,1043,1059` (silent `209`) + regression tests in `tests/test_bab_p19_7_cli_exceptions.py` (PASS; 574 stmts / 100%).
- **`beta.py` (16 broad / 1 silent):** inline invariants at lines `40,43,50,55,58,67,129,188,394,397,479,482,518,521,544,547` (silent `129`) + regression tests in `tests/test_bab_p19_7_beta_exceptions.py` (PASS; 381 stmts / 100%).

**Do this, in order, and DO NOT stop early:**
1. **`data_loader.py` (137 broad / 64 silent).** Run `python3 scripts/bab_except_inventory.py` and/or the AST snippet below to get exact line numbers. For each site classify **A** (intentional total contract → add an inline invariant comment + a regression test that locks the behavior) or **B** (hides a defect → narrow/re-raise/surface + a regression test proving identical happy-path output and that the failure now surfaces). Put new tests in `tests/test_bab_p19_7_data_loader_exceptions.py` (**does not exist yet — create it**). First broad sites to attack (AST-derived, re-derive live before editing): `96,114,149,326,491,495,739,991,1121,1162,1314,1467,1530,1762,1784,1948,1969,1980,2003,2013,2233,2415,2534,2575,2584,2612,2658,2667,...` (137 total). Run `bash scripts/bab_quick.sh` + targeted `python3 -m pytest -q tests/test_bab_data_loader*.py tests/test_beta*.py` in the inner loop.
2. **Full gate ONCE at the module boundary:** `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` → must be GREEN (0 failures, TOTAL 100%, 0 missed, ≥98.5 floor). If GREEN, append the session ledger entry.

**Efficiency / anti-loop directive:** The baseline full gate is GREEN at HEAD `94954b8` (6379 passed / 35 skipped / 0 failed / 6562 stmts / 0 missed / 100%, 134.21s) and **code is unchanged since** (`git diff --name-only 94954b8 ce1034f` → handoff files only). **Do NOT re-run the full gate before starting.** Go straight to `data_loader.py` site 1. Re-verifying gates or editing only `HANDOFF.md`/`AGENT_HANDOFF.md` is an **automatic session failure**. The fast inner loop is `bash scripts/bab_quick.sh`; save the ~134s full gate for the module boundary only.

**Anti-avoidance contract (automatic failure if violated):**
- A session that closes **zero** `data_loader.py` sites with committed tests is a **FAILED session**. Restating this brief, re-running gates, or a handoff-refresh-only commit = automatic failure.
- A commit that only edits `HANDOFF.md` / `AGENT_HANDOFF.md` is an **automatic failure**.
- Every touched site must land with a **Classification (A/B) + Locking test** committed, and the before/after broad/silent counts for `data_loader.py` recorded in the Milestone 3 ledger below.
- **Do not re-touch** the DONE sites: Milestone-1 modules (reconciliation, data_sources, portfolio, execution), `strategy.py`, `backtest.py`, `cli.py`, `beta.py`. They are closed with tests passing.
- **Do not re-touch** the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~line 6636 `test_promote_name_match_pandas_parse_unparseable_dates_left_in_place`, ~line 8249 `test_promote_datetime_column_bad_parse_left_in_place`) unless a real contract regression is proven.
- `data_loader.py` contains **intentional leave-in-place contracts** (unparseable dates left in place, name-match promotion). Classify A (contract → invariant + test) or B (defect → narrow/surface). Do NOT delete intentional contracts without concrete unreachability/defect proof.

**Definition of done (machine-checkable; a session that closes zero `data_loader.py` sites with committed tests is a FAILED session):**
- `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN; `bab_quick.sh` GREEN; `bab_gate.sh` GREEN (0 failures, TOTAL 100%, 0 missed); `BAB_GATE_MIN_COVERAGE=98.5` met (never lower the floor).
- Substantive product `.py` + test diffs for the touched sites (not handoff-only).
- Every touched site classified A/B with a locking/surfacing regression test committed; before/after broad/silent counts recorded per module in the Milestone 3 ledger below.
- Concise session ledger entry appended (UTC, HEAD, sites closed A/B per module, tests added, gate results, real blockers).

### Milestone 1 site ledger (Classification + Locking test + Status — COMPLETE)

| # | Site | Current behavior (ground-truthed) | Classification | Locking test (name + file) | Status |
|---|---|---|---|---|---|
| 1 | `execution.py:346` | cost-model resolver raises → `prices=adv=None`, then cfg fallback | **A (total)** | `test_configure_paper_adapter_resolver_fallback_contract` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 2 | `execution.py:375` | `_date_key`: `pd.Timestamp(date).isoformat()` else `str(date)` | **A (total)** | `test_date_key_string_fallback_contract`, `test_date_key_none_fallback_contract` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 3 | `execution.py:398` | `_as_timestamp`: `pd.Timestamp(value)` else `None` | **A (total)** | `test_as_timestamp_invalid_returns_none_contract` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 4 | `execution.py:458` | adv-map build fails → `adv_map={}` | **B (surface)** | `test_order_batches_from_weights_adv_map_failure_surfaces` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 5 | `execution.py:467` | per-row `date_key` fallback `str(date)` | **A (total)** | `test_order_batches_from_weights_date_key_fallback_contract` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 6 | `execution.py:831` | fill date unparseable → `continue` (fill skipped) | **B (surface)** | `test_paper_pnl_unparseable_fill_date_surfaces`, `test_paper_execution_engine_execute_unparseable_fill_date_surfaces` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 7 | `execution.py:888` | betas reindex fails → `betas=None` | **B (surface)** | `test_paper_execution_engine_execute_betas_reindex_failure_surfaces` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 8 | `execution.py:1250` | live order exception → `LiveFill(status="rejected", reason=...)` | **A (total)** | `test_ccxt_connector_submit_order_live_exception_contract` in `test_bab_p19_7_execution_exceptions.py` | **DONE** |
| 9 | `reconciliation.py:131` | `_date_key`: ISO else `str(date)` | **A (total)** | `test_date_key_fallback_contract` in `test_bab_p19_7_reconciliation_exceptions.py` | **DONE** |
| 10 | `data_sources.py:376` | ticker fetch fails → `raise BABDataError(...) from exc` | **A (surfaced)** | `test_ticker_fetch_failure_surfaces_babdataerror` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 11 | `data_sources.py:478` | `pd.to_datetime(idx)` fails → `raise BABDataError` | **A (surfaced)** | `test_unparseable_object_index_surfaces_babdataerror` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 12 | `data_sources.py:506` | tz convert fails → silent fallback **REMOVED** | **B (surface)** | `test_tz_failure_surfaces_instead_of_silent_fallback` in `test_bab_p19_7_exception_hardening.py` | **DONE** |
| 13 | `portfolio.py:30` | `_clean_signal_value` `int(f)` fails → `0` | **A (total)** | `test_clean_signal_value_total_contract` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |
| 14 | `portfolio.py:107` | inner `apply(pd.to_numeric)` fails → retry | **B (removed)** | unreachable — `pd.to_numeric(errors="coerce")` never raises | **DONE** |
| 15 | `portfolio.py:110` | nested retry fails → per-column coerce | **B (removed)** | unreachable — removed with #14 | **DONE** |
| 16 | `portfolio.py:115` | per-column coerce fails → `0.0` | **B (removed)** | unreachable — removed with #14 | **DONE** |
| 17 | `portfolio.py:118` | outer coerce fails → **return all-zero frame** (hides defect) | **B (surface)** | `test_portfolio_construction_surfaces_on_coercion_failure` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |
| 18 | `portfolio.py:165` | build fails → `raise BABPortfolioError(...) from exc` | **A (surfaced)** | `test_portfolio_construction_failure_surfaces_babportfolioerror` in `test_bab_p19_7_portfolio_exceptions.py` | **DONE** |

### Milestone 2 site ledger (COMPLETE)

| Module | Broad | Silent | Status | Locking tests | Notes |
|---|---|---|---|---|---|
| `strategy.py` | 11 | 0 | **DONE** | `tests/test_bab_p19_7_strategy_exceptions.py` (12 tests, all PASS) | Inline invariants sites 1-11 (lines 318,375,385,400,425,536,539,833,836,1014,1027); 473 stmts / 100% |
| `backtest.py` | 7 | 1 | **DONE** | `tests/test_bab_p19_7_backtest_exceptions.py` (20 tests, all PASS) | Inline invariants sites 1-7 (lines 144,155,211,252,267,286,314; silent 211); 144 stmts / 100% |
| `cli.py` | 28 | 1 | **DONE** | `tests/test_bab_p19_7_cli_exceptions.py` (26 tests, all PASS) | Inline invariants sites 1-29 (lines 99,209,288,328,333,340,559,632,639,684,689,731,737,750,806,816,821,841,871,876,889,903,924,961,978,993,1043,1059; silent 209); 574 stmts / 100% |
| `beta.py` | 16 | 1 | **DONE** | `tests/test_bab_p19_7_beta_exceptions.py` (18 tests, all PASS) | Inline invariants sites 1-17 (lines 40,43,50,55,58,67,129,188,394,397,479,482,518,521,544,547; silent 129); 381 stmts / 100% |

### Milestone 3 site ledger (FILL PER MODULE; `data_loader.py` IN PROGRESS — binding this session)

| Module | Broad | Silent | Status | Locking tests | Notes |
|---|---|---|---|---|---|
| `data_loader.py` | 137 | 64 | **IN PROGRESS** | `tests/test_bab_p19_7_data_loader_exceptions.py` (to create) | First broad sites: 96,114,149,326,491,495,739,991,1121,1162,1314,1467,1530,1762,1784,1948,1969,1980,2003,2013,2233,2415,2534,2575,2584,2612,2658,2667,...; intentional leave-in-place contracts (unparseable dates, name-match promotion) must be classified A not deleted |

### Why this campaign (evidence, `scripts/bab_except_inventory.py` audit)
All four product stakes and 100% line coverage are CLOSED. Remaining real engineering debt: **223** broad `except Exception`/bare + **68** silent `except: pass` across 16 modules. Per module (broad/silent, current inventory): `data_loader.py` 137/64, `quality.py` 4/0, `signals.py` 3/0, `attribution.py` 2/0, `risk.py` 2/1, `costs.py` 1/0, `reconciliation.py` 1/0, `regime.py` 1/0, `replay.py` 1/0, `execution.py` 4/0, `portfolio.py` 3/0, `data_sources.py` 2/0, `strategy.py` 11/0 (DONE), `backtest.py` 7/1 (DONE), `cli.py` 28/1 (DONE), `beta.py` 16/1 (DONE).

### Campaign order (module-by-module; gate GREEN after each)
1. **Milestone 1 (COMPLETE @2026-11-17T19:35Z):** **All 18 sites done** (reconciliation.py: 1, data_sources.py: 3, portfolio.py: 6, execution.py: 8). Quick gate GREEN, ruff PASS, reconcile GREEN.
2. **Milestone 2 (COMPLETE @2026-11-18T01:53Z):** `strategy.py` (11/0) DONE. `backtest.py` (7/1) DONE. `cli.py` (28/1) DONE. `beta.py` (16/1) DONE. Full gate GREEN after each module boundary.
3. **Milestone 3 (ingest — extra care):** `data_loader.py` (137 broad / 64 silent) — **BINDING THIS SESSION**. Contains intentional leave-in-place contracts (unparseable dates left in place, name-match promotion). Classify A (contract → invariant + test) or B (defect → narrow/surface). Do NOT delete intentional contracts without concrete unreachability/defect proof.
4. **Milestone 4:** remaining modules (`quality.py` 4/0, `signals.py` 3/0, `attribution.py` 2/0, `risk.py` 2/1, `costs.py` 1/0, `regime.py` 1/0, `replay.py` 1/0).
5. **Milestone 5 (hygiene):** delete committed root scratch scripts (`ast_probe.py`, `debug_beta.py`, `debug_beta2.py`, `probe_*.py`) — the repo rule forbids committing them.

### Efficiency: fast inner loop (use it; do not run the full gate after every edit)
- **Inner loop:** `bash scripts/bab_quick.sh` (ruff + targeted trio + smoke, ~seconds).
- **Targeted per module:** `python3 -m pytest -q tests/test_bab_data_loader*.py tests/test_beta*.py` (for `data_loader.py`).
- **Full gate:** `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` **once per module boundary** (and once at the end). Runtime ~134s on 4 cores — run it in a single foreground call with a generous timeout; **never hand off an in-progress gate.** Use coverage output (`grep -nE "^TOTAL|failed|passed|skipped" /tmp/bab_gate_handoff.log`) as ground truth for misses; do not guess.
- **Relevant test homes for data_loader.py:** `tests/test_bab_data_loader*.py` (existing campaign d/e batches). Add new tests in `tests/test_bab_p19_7_data_loader_exceptions.py` to keep the diff reviewable.

### Method (mandatory)
- Behavior-preserving only: no broad refactors, no style-only rewrites, no type-annotation (ANN) churn.
- Each touched site → inline invariant (A) or narrowed/surfaced code (B) **plus** a regression test that (A) locks the intended behavior, or (B) proves identical happy-path output and that the failure now surfaces.
- Keep changes minimal; run the full gate + 98.5 floor after the module and record evidence.
- Never lower the coverage floor. Never commit probe/debug scratch scripts.

### Forbidden (automatic failure)
- Handoff-only commit / restating this brief as deliverable / stopping after analysis without closing sites with tests.
- Lowering the coverage floor or adding ANN/type-style churn.
- Deleting an intentional leave-in-place contract (date-parse leave-in-place, name-match promotion) without concrete proof.
- Touching 100%-closed safety paths (`execution.py`, `reconciliation.py`, `data_sources.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`, `metrics.py`) **without** a regression test + gate-green proof that observable behavior is unchanged.
- Re-touching the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~line 6636, ~line 8249) unless a real contract regression is proven.
- Mass-refactoring all 223 sites in one pass; module-by-module only.
- Editing/pushing `.github/workflows/*` (maintainer-only, lacks `workflows:write`).
- Creating parallel handoff/session docs or committing probe/debug scratch scripts.

## Proven-closed (do not re-test)
- **All four stakes CLOSED; `strategies/betting_against_beta` at 100% line coverage (0 missed, 6572 stmts) @2026-11-17T14:46:59Z, HEAD `73e4db2`.** Full gate 6282 passed / 35 skipped / 0 failed; ruff PASS; reconcile GREEN.
- `execution.py`, `reconciliation.py`, `data_sources.py`, `metrics.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`, `beta.py` — 100% covered / closed (P19-4/P19-5/P19-6-final). Do not re-open for coverage; P19-7 changes must be behavior-preserving with regression tests.
- P19-5 deletions in `data_loader.py` (15 lines): `280-292,296-297`, `315-316`, `1650-1651`, `1954-1955` with inline invariants — keep deleted.
- P19-4 proven deletions: `replay.py:171-172`, `beta.py:181-182,427-429`, `data_sources.py:480-481,494-500`, `data_loader.py:1609-1610,2755-2758`, `metrics.py:93-94`, `portfolio.py:165-166`, `execution.py:140-141,182-185,1295-1296`, `cli.py:657-658,836-838`, `reconciliation.py:82-83,309`.
- P17-1/2, P18-1/2/3, P19-2/3/4, kill-switch R4-B, bootstrap done — do not redo.
- **Milestone 1 sites 9-18 (reconciliation, data_sources, portfolio) — DONE with tests passing.** `tests/test_bab_p19_7_exception_hardening.py` (5 tests) and `tests/test_bab_p19_7_reconciliation_exceptions.py` / `tests/test_bab_p19_7_portfolio_exceptions.py` all GREEN.

## Bottleneck status
- **[REMOVED @2026-11-18T02:02Z] "Which milestone is unstarted?" ambiguity:** ground-truth audit live on HEAD `ce1034f` re-confirmed Milestones 1 & 2 are COMPLETE (all DONE rows verified, 100% coverage, full gate GREEN at `94954b8`, code unchanged since). The only open heavy item is `data_loader.py` (137 broad / 64 silent). This handoff rebinds the next action firmly to `data_loader.py` site 1 and marks any handoff-only / re-verification-only commit as an **automatic failure**, so no session may stall on analysis or re-litigate closed modules.
- **[REMOVED @2026-11-18T02:02Z] Stale-handoff risk from HEAD drift:** HEAD advanced to `ce1034f` as a checkpoint past the green baseline `94954b8`; `git diff --name-only 94954b8 ce1034f` confirms ONLY `HANDOFF.md` + `AGENT_HANDOFF.md` differ (zero product/test change). This handoff records that explicitly so the next session does not re-run the full gate to "prove" the baseline — it is already proven and applies unchanged.
- **[REMOVED @2026-11-18T01:53Z] Milestone 2 `cli.py` + `beta.py` unstarted:** Both modules LANDED with 44 regression tests (26 CLI + 18 beta), inline invariants at all sites, full gate GREEN at 100% coverage (6379/35/0/6562/100%). Milestone 2 COMPLETE.
- **[REMOVED @2026-11-17T23:38Z] Re-verification / handoff-refresh loop (primary inefficiency):** the session ledger shows repeated sessions that only re-ran gates or rewrote `HANDOFF.md` while product modules stayed unstarted. This handoff removes that loop: baseline full gate is proven GREEN and code is unchanged, so the next session must go straight to `data_loader.py` site 1. Re-verifying gates or producing a handoff-refresh-only commit is now an **automatic failure**.
- **[EXTERNAL]** P19-1 CI enforcement maintainer-only (`workflows:write`). `.github/workflows/main.yml` does not invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`. Do not re-attempt from an agent session.
- **[LOW]** `README.md:246` still says "Binding next step (P19-3)" — stale; superseded by this P19-7 brief. Fix only if touching README for another reason.

## Hard gates every session (repo root, in order)
```bash
python3 -m ruff check .
bash scripts/bab_reconcile_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh
BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh   # only when TOTAL < 100 or floor proof needed
```

## Session ledger (append-only, concise)
| Session (UTC) | HEAD | Did | Gate |
|---|---|---|---|
| 2026-11-18T02:02:19Z | ce1034f | **Handoff refresh + anti-avoidance rebind to `data_loader.py`.** Verified live on HEAD `ce1034f`: ruff PASS, reconcile GREEN, quick GREEN (104 targeted + 195 smoke); `bab_except_inventory.py` = 223 broad / 68 silent (data_loader.py 137/64); confirmed `git diff --name-only 94954b8 ce1034f` = handoff files only (no product/test change). Rewrote INITIAL TASK MESSAGE to bind Milestone 3 `data_loader.py` (137/64) this session with committed regression tests; added explicit anti-avoidance contract (zero-site close = FAILED) and removed "which milestone unstarted" ambiguity. | ruff PASS; reconcile GREEN; quick GREEN; full-gate GREEN @94954b8 applies (6379/35/0/6562/100%) |
| 2026-11-18T01:53:34Z | 94954b8 | **Milestone 2 COMPLETE:** `cli.py` (28 broad/1 silent) hardened with 26 regression tests in `test_bab_p19_7_cli_exceptions.py`; `beta.py` (16 broad/1 silent) hardened with 18 regression tests in `test_bab_p19_7_beta_exceptions.py`. All 44 new tests PASS; inline invariants at all sites. Full gate GREEN 6379/35/0/6562/100% (134.21s). Milestone 3 (`data_loader.py` 137/64) now binding. | GREEN |
| 2026-11-18T00:32:52Z | cf4c633 | Retimestamped handoff; re-affirmed binding mission (close both cli.py 28/1 and beta.py 16/1 this session with committed regression tests); anti-loop directive intact; baseline gate GREEN at 7960113 applies. | ruff PASS; reconcile GREEN; quick GREEN; bab_gate 6335/35/0/100% @7960113 |
| 2026-11-17T22:35Z | 019a981 | P19-7 Milestone 2: backtest.py (7 broad/1 silent) hardened with 20 regression tests in `test_bab_p19_7_backtest_exceptions.py`; full gate GREEN 6335/35/0/6562/100%. | GREEN |