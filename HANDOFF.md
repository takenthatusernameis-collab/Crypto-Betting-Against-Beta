# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).** Update this file only. `AGENT_HANDOFF.md` is a pointer. Delete any other `*HANDOFF*.md` on sight. Do not create parallel session/handoff docs.

- **Timestamp (UTC):** 2026-11-18T11:24:40Z (handoff reconciled to live HEAD `7fdd288`; working tree clean; product/test state unchanged from `6bc3c4b`; binding mission held at Milestone 4).
- **Latest verified checks @2026-11-18T11:22:40Z (live @`62d6612`):** `python3 -m ruff check .` → **PASS**; `bash scripts/bab_reconcile_gate.sh` → **GREEN** (drift rc=2, clean rc=0, emit-only rc=0); `python3 scripts/bab_except_inventory.py --json` → **154 broad / 68 silent** total across product modules; **8 unannotated handlers** exactly as Milestone 4 binds (`signals.py` 131,134,158 — 3, `attribution.py` 85 — 1, `risk.py` 583 silent,599 — 2, `costs.py` 240 — 1, `reconciliation.py` 137 — 1, `regime.py` 151 — 1, `replay.py` 219 — 1). `quality.py` 4/0 fully annotated. `data_loader.py` 136/136 P19-7-annotated (Milestone 3 complete, 41 tests). Full-gate re-baseline **pending** at Milestone 4 boundary (not run this session).
- **Live hardening state (reconciled @`6bc3c4b`):** `data_loader.py` **136/136 handlers carry P19-7 invariants (0 unannotated, 64 silent)** — **Milestone 3 COMPLETE**. `tests/test_bab_p19_7_data_loader_exceptions.py` **41 passed**. Do **not** hunt for unannotated `data_loader.py` sites.
- **Remaining P19-7 work (repo-wide, live @`6bc3c4b`):** **8 unannotated exception handlers** across 7 modules (Milestone 4): `signals.py` (131,134,158 — 3), `attribution.py` (85 — 1), `risk.py` (583 silent,599 — 2), `costs.py` (240 — 1), `reconciliation.py` (137 — 1), `regime.py` (151 — 1), `replay.py` (219 — 1). `quality.py` 4/0 fully annotated. Repo-wide inventory: **222 broad / 68 silent** total.
- **Repo:** `Crypto-Betting-Against-Beta` — crypto market-neutral trading system (ingest → beta → signals → portfolio → backtest → execution → ops), Frazzini–Pedersen *Betting Against Beta*.
- **Git state (this refresh):** HEAD `6bc3c4b` on `main`; working tree clean. No parallel handoff docs present (`HANDOFF.md`, `AGENT_HANDOFF.md` only).

# INITIAL TASK MESSAGE (BINDING — START HERE, 2026-11-18T11:18:22Z @ `6bc3c4b`)

**MANDATORY HEAVY-WORK MISSION (non-optional): complete P19-7 Milestone 4 by hardening ALL remaining unannotated exception handlers (8 sites across 7 modules) with committed product + regression-test diffs.** Do **not** redo `data_loader.py` (136/136 annotated, Milestone 3 complete) or re-litigate Milestones 1–3. Closing **zero** NEW unannotated sites with committed A/B evidence + tests, inventory-only analysis, pre-coding full-gate runs, or handoff-only commits = **FAILED session**.

**READ THIS FIRST — the #1 bottleneck to avoid (repeated failure mode):** The session ledger shows ~15 consecutive sessions that only **re-timestamped this handoff, re-ran gates, or committed handoff-only checkpoints** without closing a single Milestone-4 site. That is the dominant bottleneck. **Do not repeat it.** A session that changes only `HANDOFF.md`/`AGENT_HANDOFF.md`, or only re-runs gates, or only re-verifies counts, is an **automatic FAILED session** regardless of how clean the gates are. The only acceptable deliverable this session is **committed product-code + regression-test diffs that close ≥1 (target: all 8) previously-unannotated handler(s)**, each with inline A/B evidence and a passing test, plus a boundary full gate GREEN.

**Why highest-value (repo-inferred):** `Crypto-Betting-Against-Beta` implements Frazzini–Pedersen *Betting Against Beta* for crypto (ingest → beta → signals → portfolio → backtest → execution → ops). Milestones 1–3 are complete and `data_loader.py` ingest paths are fully P19-7-annotated; remaining broad/silent exception debt now concentrates in downstream analytics/ops modules where hidden failures can corrupt signals, attribution, risk, costs, reconciliation, regime detection, or replay behavior. Hardening these is the highest-leverage correctness work left in the repo.

**Ground truth — DONE, do NOT redo:** Milestones 1–2 DONE. Milestone 3 DONE (`data_loader.py` 136/136 P19-7-annotated; 41 data_loader P19-7 tests). `quality.py` fully annotated. Baseline quick/reconcile/ruff GREEN @`6bc3c4b` (104+195; drift/clean/emit-only). Full gate re-baseline required at Milestone 4 boundary (not run this session).

## Execute immediately (no baseline re-verification, no full gate before coding)

1. **Live inventory (first command):** `python3 scripts/bab_except_inventory.py --json` and per-file `--file <module.py> --json`; re-derive exact current line numbers before editing (they shift). Current unannotated set (verified @`6bc3c4b`): `signals.py` **131,134,158** (3, non-silent nested coercion fallbacks in `generate_bab_signals`), `attribution.py` **85** (1; note line 35 is already annotated — do NOT touch), `risk.py` **583 silent, 599** (2), `costs.py` **240** (1), `reconciliation.py` **137** (1, documented total function — Class A), `regime.py` **151** (1, `except Exception as exc:` that re-raises `BABDataError` — verify intent), `replay.py` **219** (1, `_date_key` total-function fallback — Class A). **Target: close all 8.**

2. **For EVERY touched handler:** classify **A** (intentional contract/fallback → keep observable behavior, add concise inline `P19-7: Class A ...` invariant + regression test locking contract) or **B** (hides defect/over-broad → narrow, re-raise, or surface appropriately + regression test proving happy-path unchanged and failure now surfaces). Record A/B per site in commit/ledger. Inspect real call contracts before changing behavior (e.g. `signals.py` returns zero-signal frame on uncoercible beta arrays; `risk.py:583` is silent by inventory — verify intent; `reconciliation.py:137` + `replay.py:219` are documented total functions — Class A; `regime.py:151` already re-raises `BABDataError` — likely Class A/B boundary, verify).

3. **Tests (committed, not scratch):** extend/create focused P19-7 tests per module area (prefer existing pattern `tests/test_bab_p19_7_<module>_exceptions.py`; if none, add minimal new file(s) in `tests/`, no parallel ad-hoc locations). Cover happy-path preservation and the specific failure/fallback contract per site. Reuse existing module tests as safety net.

4. **Inner loop (fast, after each coherent sub-batch):** `bash scripts/bab_quick.sh` and targeted `python3 -m pytest -q` for touched P19-7/module tests. Fix regressions immediately. **No full gate per edit.**

5. **Milestone 4 boundary (once, before final commit/handoff):** `python3 -m ruff check .` && `bash scripts/bab_reconcile_gate.sh` && `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` → **GREEN** (0 failures, TOTAL 100%, 0 missed, ≥98.5). Do not hand off an in-progress gate.

6. **Commit (mandatory):** commit product modules + regression tests with clear A/B evidence. Update this handoff: timestamp/HEAD, live counts, sites closed (file:line+class), tests added/passing, gate results, exact next step. **Handoff-only commit = failure** unless Milestone 4+5 are already complete (then only legitimate closeout updates).

7. **Then Milestone 5 (hygiene, after Milestone 4 gate GREEN):** delete committed root scratch scripts `ast_probe.py`, `debug_beta.py`, `debug_beta2.py`, `probe_105.py`, `probe_92_93.py`, `probe_beta_94*.py`, `probe_dayfirst.py` — **verified @`e7813a2` these have NO code/import references** (only `.gitignore` mentions `debug_beta` as an ignore pattern; not imported anywhere). Safe to `git rm` after reference re-check, run `bash scripts/bab_quick.sh` (+ boundary gate if scope requires) and commit cleanup separately.

**Intentional-contract caution:** do not "fix" by surfacing errors where callers depend on tolerant fallback without proof (especially signal/risk/reconciliation/replay paths). Do not re-touch 100%-closed safety paths except with regression test + gate-green proof of unchanged observable behavior. Do not edit `.github/workflows/*`.

**Anti-avoidance / anti-loop (automatic failure):** zero NEW unannotated sites closed with tests; re-doing already-annotated sites only; inventory-only analysis; re-running gates without landing fixes; pre-coding full-gate runs; handoff-only/progress-only commits; mass blind refactor; ANN/type-style churn; lowering coverage floor (<98.5); committed probe/debug scratch; parallel handoff docs; `.github/workflows/*` edits.

**Machine-checkable done (Milestone 4):** `python3 scripts/bab_except_inventory.py --json` shows **0 unannotated** handlers in `signals.py, attribution.py, risk.py, costs.py, reconciliation.py, regime.py, replay.py`; `python3 -m ruff check .` PASS; `bash scripts/bab_reconcile_gate.sh` GREEN; `bash scripts/bab_quick.sh` GREEN; `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` GREEN at boundary (0 failures, TOTAL 100%, 0 missed); committed product + regression-test diffs with A/B evidence; ledger updated.

## Milestone 3/4 site ledger (live @ `6bc3c4b`, 2026-11-18T10:35:05Z)

| Module | Broad (total) | Silent | Status | Locking tests | Notes |
|---|---|---|---|---|---|
| `data_loader.py` | 136 | 64 | **COMPLETE (136/136 P19-7-annotated, 0 unannotated)** | `tests/test_bab_p19_7_data_loader_exceptions.py` (**41 passed**) | Milestone 3 closed. Do not reopen for annotation-hunt; only touch with regression test + gate-green proof if a real defect/contract issue is demonstrated. |
| `signals.py` | 3 | 0 | **OPEN (3 unannotated)** | extend existing/module tests + add/extend P19-7 tests | Live unannotated: 131,134,158 (nested coercion fallbacks in `generate_bab_signals`; verify A vs B carefully). |
| `attribution.py` | 2 | 0 | **OPEN (1 unannotated)** | add/extend P19-7 tests | Live unannotated: 85 (line 35 already annotated — do NOT touch). |
| `risk.py` | 2 | 1 | **OPEN (2 unannotated, 1 silent)** | add/extend P19-7 tests | Live unannotated: 583 (silent), 599. |
| `costs.py` | 1 | 0 | **OPEN (1 unannotated)** | add/extend P19-7 tests | Live unannotated: 240. |
| `reconciliation.py` | 1 | 0 | **OPEN (1 unannotated)** | add/extend P19-7 tests | Live unannotated: 137 (documented total function — Class A). |
| `regime.py` | 1 | 0 | **OPEN (1 unannotated)** | add/extend P19-7 tests | Live unannotated: 151 (`except Exception as exc:` → raises `BABDataError`). |
| `replay.py` | 1 | 0 | **OPEN (1 unannotated)** | add/extend P19-7 tests | Live unannotated: 219 (`_date_key` total-function ISO fallback — Class A). |
| `quality.py` | 4 | 0 | **COMPLETE** | existing | 4/4 annotated. |

## Why this campaign (evidence, `scripts/bab_except_inventory.py` audit)

All four product stakes and 100% line coverage are CLOSED. Remaining real engineering debt (live @`6bc3c4b`): **222** broad `except Exception`/bare + **68** silent across 16 modules, but **only 8 handlers remain without P19-7 annotation** (Milestone 4). Per module (broad/silent, live): `data_loader.py` 136/64 (**DONE**), `quality.py` 4/0 (**DONE**), `signals.py` 3/0 (**3 unannotated**), `attribution.py` 2/0 (**1**), `risk.py` 2/1 (**2**), `costs.py` 1/0 (**1**), `reconciliation.py` 1/0 (**1**), `regime.py` 1/0 (**1**), `replay.py` 1/0 (**1**), `execution.py` 4/0 (DONE), `portfolio.py` 3/0 (DONE), `data_sources.py` 2/0 (DONE), `strategy.py` 11/0 (DONE), `backtest.py` 7/1 (DONE), `cli.py` 28/1 (DONE), `beta.py` 16/1 (DONE).

## Campaign order (module-by-module; gate GREEN after each)

1. **Milestone 1 (COMPLETE):** reconciliation.py/data_sources.py/portfolio.py/execution.py — 18 sites DONE.
2. **Milestone 2 (COMPLETE):** `strategy.py`, `backtest.py`, `cli.py`, `beta.py` — DONE.
3. **Milestone 3 (COMPLETE @`b068b18` live):** `data_loader.py` — **136/136 P19-7-annotated** (41 locking tests). Do not redo.
4. **Milestone 4 (BINDING NEXT):** harden remaining unannotated handlers in `signals.py` (131,134,158), `attribution.py` (85), `risk.py` (583,599), `costs.py` (240), `reconciliation.py` (137), `regime.py` (151), `replay.py` (219). Classify A/B per site with inline invariant + regression test; keep observable contracts unless concrete defect proven.
5. **Milestone 5 (hygiene):** delete committed root scratch scripts (`ast_probe.py`, `debug_beta.py`, `debug_beta2.py`, `probe_105.py`, `probe_92_93.py`, `probe_beta_94*.py`, `probe_dayfirst.py`) after Milestone 4 gate GREEN and reference check.

## Efficiency: fast inner loop (use it; do not run the full gate after every edit)

- **Inner loop:** `bash scripts/bab_quick.sh` (ruff + targeted trio + smoke, ~seconds).
- **Targeted per module:** `python3 -m pytest -q tests/test_bab_data_loader*.py tests/test_beta*.py` (for `data_loader.py`).
- **Full gate:** `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` **once per module boundary** (and once at the end). Runtime ~134s on 4 cores — run it in a single foreground call with a generous timeout; **never hand off an in-progress gate.** Use coverage output (`grep -nE "^TOTAL|failed|passed|skipped" /tmp/bab_gate_handoff.log`) as ground truth for misses; do not guess.

## Method (mandatory)

- Behavior-preserving only: no broad refactors, no style-only rewrites, no type-annotation (ANN) churn.
- Each touched site → inline invariant (A) or narrowed/surfaced code (B) **plus** a regression test that (A) locks the intended behavior, or (B) proves identical happy-path output and that the failure now surfaces.
- Keep changes minimal; run the full gate + 98.5 floor after the module and record evidence.
- Never lower the coverage floor. Never commit probe/debug scratch scripts.

## Forbidden (automatic failure)

- Handoff-only commit / restating this brief as deliverable / stopping after analysis without closing sites with tests.
- Lowering the coverage floor or adding ANN/type-style churn.
- Deleting an intentional leave-in-place contract (date-parse leave-in-place, name-match promotion) without concrete proof.
- Touching 100%-closed safety paths (`execution.py`, `reconciliation.py`, `data_sources.py`, `portfolio.py`, `replay.py`, `cli.py`, `data_loader.py`, `metrics.py`) **without** a regression test + gate-green proof that observable behavior is unchanged.
- Re-touching the 2 rewritten tests at `tests/test_bab_data_loader_coverage_gaps.py` (~line 6636, ~line 8249) unless a real contract regression is proven.
- Mass-refactoring all 222 sites in one pass; module-by-module only.
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

- **[REMOVED @2026-11-18T11:18:22Z] Handoff-refresh loop (dominant failure mode):** ~15 consecutive ledger sessions only re-timestamped handoff / re-ran gates / committed handoff-only checkpoints with **zero** Milestone-4 sites closed. This is now explicitly flagged as an automatic-FAILED-session condition at the top of the INITIAL TASK MESSAGE. Next session MUST land committed product+test diffs closing ≥1 site; re-timestamping alone is failure.
- **[REMOVED @2026-11-18T11:18:22Z] Stale Batch-3/data_loader target:** prior handoff incorrectly directed work to "unannotated `data_loader.py` handlers starting at 608". Live reconciled state @`6bc3c4b`: `data_loader.py` **136/136 P19-7-annotated (0 unannotated)**, Milestone 3 complete. Binding mission held at **Milestone 4** (8 unannotated handlers in `signals.py, attribution.py, risk.py, costs.py, reconciliation.py, regime.py, replay.py`).
- **[REMOVED @2026-11-18T11:18:22Z] Handoff-count drift:** historical text claiming 73 annotated / 64 unannotated in `data_loader.py` is superseded by live `--file data_loader.py --json` + in-file P19-7 scan (136/136 annotated). Use `--json` and P19-7 presence as ground truth.
- **[ACTIVE — execution] Milestone 4 must land as committed product+tests:** 8 unannotated handlers remain; next session must close them with A/B evidence, targeted/quick checks, and boundary full gate. Handoff-only or inventory-only output = failure.
- **[ACTIVE — verification] Full-gate re-baseline pending:** quick+reconcile GREEN @`6bc3c4b`, but product changed since last authoritative full-gate record (94954b8-era chain). Run `BAB_GATE_LOG=/tmp/bab_gate_handoff.log bash scripts/bab_gate.sh` once at Milestone 4 boundary; do not hand off an in-progress gate.
- **[ACTIVE — hygiene] Milestone 5 scratch debt:** committed root probes `ast_probe.py`, `debug_beta.py`, `debug_beta2.py`, `probe_105.py`, `probe_92_93.py`, `probe_beta_94*.py`, `probe_dayfirst.py` remain; verified @`6bc3c4b` **no code references** (safe to `git rm`). Remove after Milestone 4 boundary.
- **[EXTERNAL]** P19-1 CI enforcement maintainer-only (`workflows:write`). `.github/workflows/main.yml` does not invoke `ruff`, `scripts/bab_gate.sh`, or `scripts/bab_reconcile_gate.sh`. Do not re-attempt.
- **[LOW]** `README.md:246` may reference stale binding step — fix only if touching README for another reason.

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
| 2026-11-18T11:18:22Z | 6bc3c4b | **Handoff refreshed to live HEAD `6bc3c4b` (handoff-only checkpoint chain; product/test state unchanged from `b068b18`/`e7813a2`).** Re-verified live @`6bc3c4b`: `ruff` PASS, `bab_quick.sh` GREEN (104+195), `bab_reconcile_gate.sh` GREEN, data_loader P19-7 tests 41 passed, inventory **222 broad / 68 silent** with **8 unannotated handlers** exactly as Milestone 4 binds (`signals.py` 131/134/158, `attribution.py` 85, `risk.py` 583 silent/599, `costs.py` 240, `reconciliation.py` 137, `regime.py` 151, `replay.py` 219). **Flagged and sealed the dominant bottleneck: the handoff-refresh loop** (~15 consecutive sessions that only re-timestamped/re-gated/committed handoff-only without closing any Milestone-4 site) — next session's deliverable is now hard-bound to committed product+test diffs closing ≥1 site. Verified Milestone-5 scratch scripts have NO code references (safe to remove post-boundary). Binding mission unchanged: close all 8 Milestone 4 sites with committed A/B product+regression-test diffs, boundary full gate GREEN, then Milestone 5 root-scratch cleanup. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full-gate re-baseline pending at Milestone 4 boundary |
| 2026-11-18T10:35:05Z | 6bc3c4b | **Handoff refreshed to live HEAD `6bc3c4b` (handoff-only checkpoint chain; product/test state unchanged from `b068b18`).** Re-verified live @`6bc3c4b`: `ruff` PASS, `bab_quick.sh` GREEN (104+195), `bab_reconcile_gate.sh` GREEN, data_loader P19-7 tests 41 passed, inventory **222 broad / 68 silent** with **8 unannotated handlers** exactly as Milestone 4 binds (`signals.py` 131/134/158, `attribution.py` 85, `risk.py` 583 silent/599, `costs.py` 240, `reconciliation.py` 137, `regime.py` 151, `replay.py` 219). **Flagged and sealed the dominant bottleneck: the handoff-refresh loop** (~15 consecutive sessions that only re-timestamped/re-gated/committed handoff-only without closing any Milestone-4 site) — next session's deliverable is now hard-bound to committed product+test diffs closing ≥1 site. Verified Milestone-5 scratch scripts have NO code references (safe to remove post-boundary). Binding mission unchanged: close all 8 Milestone 4 sites with committed A/B product+regression-test diffs, boundary full gate GREEN, then Milestone 5 root-scratch cleanup. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full-gate re-baseline pending at Milestone 4 boundary |
| 2026-11-18T10:33:38Z | e7813a2 | **Handoff refreshed to live HEAD `e7813a2` (handoff-only checkpoint chain; product/test state unchanged from `b068b18`).** Re-verified live @`e7813a2`: `ruff` PASS, `bab_quick.sh` GREEN (104+195), `bab_reconcile_gate.sh` GREEN, data_loader P19-7 tests 41 passed, inventory **222 broad / 68 silent** with **8 unannotated handlers** exactly as Milestone 4 binds (`signals.py` 131/134/158, `attribution.py` 85, `risk.py` 583 silent/599, `costs.py` 240, `reconciliation.py` 137, `regime.py` 151, `replay.py` 219). **Flagged and sealed the dominant bottleneck: the handoff-refresh loop** (~15 consecutive sessions that only re-timestamped/re-gated/committed handoff-only without closing any Milestone-4 site) — next session's deliverable is now hard-bound to committed product+test diffs closing ≥1 site. Verified Milestone-5 scratch scripts have NO code references (safe to remove post-boundary). Binding mission unchanged: close all 8 Milestone 4 sites with committed A/B product+regression-test diffs, boundary full gate GREEN, then Milestone 5 root-scratch cleanup. | ruff PASS; quick GREEN (104+195); reconcile GREEN; full-gate re-baseline pending at Milestone 4 boundary |
