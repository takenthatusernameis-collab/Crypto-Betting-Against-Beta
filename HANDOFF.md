# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it. Only `HANDOFF.md` is tracked at repo root; keep it that way.**

- **Timestamp (UTC):** 2026-11-25T07:51:17Z — single durable handoff refreshed this session. The full gate **RAN AND FAILED** (log `/tmp/bab_gate_p41_w1.log`): pytest phase GREEN (TOTAL 100%, 7670 passed, 39 skipped) but **5 doc pointer guard tests FAILED** because HANDOFF.md's secondary extraction pattern matched P40 while `test_handoff_binding_row_matches_landed_p34_tests` only allows P28/P34–P39. Since P39 WP0 has NOT completed, the binding row MUST be P39.
- **HEAD:** `0f417a43ff3812fbbbc72bc1b7306de201ab4b07` (`chore(kilo): checkpoint agent session`). The checkpoint hash advances every session — re-derive with `git rev-parse HEAD` at session start; never cite a stale hash. Campaign code is frozen at its campaign commits (P38 at `726d4bd`, P39 WP3 at ancestor `3d08169`); treat those as ancestors, never as HEAD.
- **Working tree (verified 2026-11-25T07:51:17Z):** clean. The gate run completed (PID gone); no background process to reconcile.
- **Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta factor strategy** for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence about a factor strategy*. Synthetic fixtures are NOT real market data — never present them as evidence of real profitability.

**BINDING ROW = Campaign P39**

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-25T07:51:17Z)

**PRIORITIZATION BY REPO NAME (binding & inescapable):** this is a *factor strategy* repo (`Crypto-Betting-Against-Beta`). The highest-value next heavy work is **factor robustness** — does the BAB factor's apparent edge survive across independently parameterized synthetic universes, under a pre-registered multiplicity correction, and net of costs — NOT docs, NOT handoff churn, NOT CI plumbing (maintainer-gated). That work is **Campaign P40** (charter below). It is inescapable and ordered WP1→WP4. Any session that does not execute P40 after P39 WP0 lands GREEN has FAILED its binding obligation.

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable): land P39 WP0 full-gate close-out — reconcile to a GREEN `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` (TOTAL 100%, exit 0), record TOTAL coverage in `docs/COVERAGE_NOTES.md`, and restore the frozen P27 `.md` files. Then start P40 WP1 in the same session. A handoff-only / docs-only / gate-only / count-only / planning commit that substitutes for WP0 is a FAILED session while WP0 is open.**

**State you inherit (verified firsthand 2026-11-25T07:51:17Z):**
- **The gate RUN COMPLETED BUT FAILED** (log `/tmp/bab_gate_p41_w1.log`): pytest phase GREEN — `TOTAL 6730 0 100%` and `7670 passed, 39 skipped in 1978.51s` — but **5 doc pointer guard tests FAILED**:
  - `test_readme_campaign_not_older_than_handoff` — README.md names P39 as binding, HANDOFF.md extracted P40
  - `test_coverage_notes_campaign_not_older_than_handoff` — COVERAGE_NOTES.md names P39 as binding, HANDOFF.md extracted P40
  - `test_handoff_binding_row_matches_landed_p34_tests` — HANDOFF.md binding row extracted as P40, but allowed set is P28/P34–P39
  - `test_no_stale_campaign_references_in_readme` — README.md cites 'P39' as 'Binding next campaign' but HANDOFF.md binding row is P40
  - `test_no_stale_campaign_references_in_coverage_notes` — COVERAGE_NOTES.md cites 'P39' as 'Active work is binding' but HANDOFF.md binding row is P40
- **Root cause:** HANDOFF.md's secondary extraction pattern `(?:binding|active).*?Campaign\s+P(\d+)` matched "(binding & inescapable):** this is a *factor strategy* repo... That work is **Campaign P40**" and returned P40. The test `test_handoff_binding_row_matches_landed_p34_tests` only allows binding row ∈ {P28, P34, P35, P36, P37, P38, P39} — P40 is NOT allowed because P39 WP0 is not yet complete.
- **Baseline is GREEN firsthand (2026-11-25T06:59:53Z):** `ruff check .` → All checks passed; `bash scripts/bab_quick.sh` → quick preflight OK (targeted trio 104 passed, smoke 195 passed); `pytest tests/test_bab_p30_ledger_analyzer.py` → 11 passed; P37/P38/P39 `--check-*` summaries all `PASS (byte-identical)`; `research_state/bab_p27/` clean (no trailing-newline mutation).
- **The WP0 test blocker is already FIXED and COMMITTED (`cff863e`):** `tests/test_bab_p30_ledger_analyzer.py::TestSince::test_since_filters_runs` recomputes the expected count independently from the 50-run ledger (exact recomputation, not a loosening). Do NOT re-touch it or re-introduce a hard-coded count.

**FIRST ACTION (before anything else) — fix the doc pointer mismatch, then re-run the gate:**
1. **Fix the three docs to declare P39 as the binding row** (since P39 WP0 is not yet complete):
   - HANDOFF.md: Ensure primary pattern `BINDING ROW = Campaign P39` exists (this file now has it at line 60)
   - README.md: Change "Binding next campaign: Campaign **P39**..." to explicitly reference **P39 WP0 full-gate close-out**
   - docs/COVERAGE_NOTES.md: Change "Active work is binding: Campaign **P39 WP0 full-gate close-out**, then **Campaign P40**" (already correct but verify)
2. **Re-run the full gate** (exactly one concurrent run):
   ```bash
   BAB_GATE_LOG=/tmp/bab_gate_p41_w2.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
   ```
   Budget ~60 min uninterrupted (pytest phase alone was ~1978 s; the post-pytest replay/`--xproc`/`--check-provenance` rebuild adds more). If the runner cannot keep a background process alive, run the fast 95% first, then `--check-provenance` and `--xproc` once on a large uninterrupted budget.
3. **On GREEN (`TOTAL 100% >= 100%`, exit 0):** record TOTAL coverage % + pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`.
4. **Restore frozen P27 artifacts:** `git checkout -- research_state/bab_p27/` to undo the trailing-newline mutation the full run makes to `risk_controls.md` and `reconciliation_e2e.md`. (If the P30 ledger test ran, also `git checkout -- research_state/bab_p30/ledger_summary.json`.)
5. **Re-run baseline:** `bash scripts/bab_quick.sh` + `python3 -m ruff check .`; confirm `git status --porcelain` shows only intended changes.
6. **Then Campaign P40 WP1 immediately** (charter below). Stopping after WP0 with P40 unstarted and no maintainer-gate is a FAILED session.

**Gate-exit handling:**
- Exit 0 + `TOTAL 100% >= 100%` → WP0 DONE; proceed to steps 3–6.
- Exit 1 with a real test failure → bisect to a **code change** (never an artifact hand-edit, never a loosened/`xfail`ed test); re-run the fast inner loop, then the gate.
- Exit 1 with `COVERAGE FLOOR NOT MET` → inspect the `Missing` column, add targeted tests (mirror P35 `TestValidationErrors` / reconciliation non-finite pattern), re-run. Coverage is saturated at 100%; do not lower the floor.
- Do NOT commit unless the user explicitly asks.

**Do NOT re-do (all COMPLETE & frozen):** P20–P38; P39 WP1 (`--check-regime-summary` byte-identical); P39 WP2 (`--check-cross-fixture-summary` byte-identical, verdict `DOES_NOT_REPLICATE`); P39 WP3 (ancestor `3d08169`, `--subset p39_decision.md` byte-identical); `tests/test_bab_p38_determinism.py` (EXISTS, committed). Both P39 verdicts are honest negatives — report them, never reverse them. Do NOT re-fix the xproc timeout (now 3600 s), the 8-record P29 provenance ledger, the P35 tests, or the P30 ledger-count test.

---

## NEXT FOCUS CAMPAIGN — P40 (defined so heavy work is unavoidable after WP0)

**Campaign P40 — "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict".** Declared 2026-11-24T15:35:11Z · Priority HIGH · Status: PENDING (starts only after P39 WP0 lands GREEN). Fully offline, deterministic, zero maintainer dependency. **IN-ESCAPABILITY CLAUSE (prioritized by repo name — a *factor* strategy, so the next heavy work must be factor-robustness, not docs):** the moment P39 WP0 is GREEN, P40 WP1 is the binding row. There is no "no explicit directions" escape: if a future session finds no new user directive, it MUST execute P40 WP1→WP4 in order. Rationale: P38 answered the pooled questions; P39 WP1/WP2 answered within-regime and single-second-fixture replication (both honest negatives). P40 generalizes replication to a *battery* of independently parameterized synthetic universes and consolidates P34–P39 into one authoritative, multiplicity-controlled verdict. Do NOT reverse any prior negative; report whatever P40 finds honestly.

- **P40 WP1 (heavy):** `scripts/bab_p40_fixture_battery.py` + `research_state/bab_p40/fixture_battery_summary.{json,md}` — replicate over K≥4 independently parameterized synthetic universes (vary beta grid, idio vol, seed base, asset count N∈{24,32,40}, market-beta dispersion); per-seed DSR/PSR over `n_trials_total` (read-only from P38 WP1) + neutrality invariants at every cell; survival-frequency table. `--check-fixture-battery-summary` byte-identical.
- **P40 WP2 (heavy):** `scripts/bab_p40_meta_analysis.py` + `research_state/bab_p40/meta_analysis_summary.{json,md}` — pool all (seed, regime, fixture) cells, apply a pre-registered multiplicity correction (Benjamini–Hochberg across the full grid), report overall survival rate against a pre-registered decision rule. `--check-meta-analysis-summary` byte-identical.
- **P40 WP3 (heavy):** `scripts/bab_p40_costed_survival.py` + `research_state/bab_p40/costed_survival_summary.{json,md}` — re-run the surviving (fixture, seed, regime) cells under the P37 cost/capacity surfaces; report whether any survive net of costs. `--check-costed-survival-summary` byte-identical.
- **P40 WP4:** `generate_p40_decision.py` + `docs/BAB_P40_DECISION.md` + `tests/test_bab_p40_decision_consistency.py` (zero hand-typed numbers; independent JSON re-render byte-identity; numeric-leaf check; explicit honest verdict incl. "not market evidence"/"no real alpha"; AST no-harness scan); register `fixture_battery_summary`/`meta_analysis_summary`/`costed_survival_summary` in `scripts/bab_replay_full.py` (`json_only, no_xproc`) and `p40_decision.md` in `scripts/bab_replay_decisions.py` (regenerate `research_state/bab_p32/doc_replay_summary.json`); add a P40 block to `scripts/bab_gate.sh`; add `"P40"` to the pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py`; `tests/test_bab_p40_determinism.py` (mirror `test_bab_p38_determinism.py`); full-gate close-out at `BAB_GATE_MIN_COVERAGE=100`.
- **P40 acceptance:** all `--check-*` byte-identical; `ruff check .` clean; full `bab_gate.sh` GREEN at `BAB_GATE_MIN_COVERAGE=100`; honest verdict recorded; P27 `.md` restored; decision doc committed (only on explicit user request). Reuse the P38/P39 generator + decision + determinism templates.

---

## COMPLETED CAMPAIGNS (frozen — do NOT re-do)

- **P20–P33 — COMPLETE & frozen** (BAB core, cost/impact/capacity, short haircut, regime split, charters, provenance replay layer, decision docs).
- **CAMPAIGN P34** "Wide-Universe Robustness & Strategy-Honesty Closure" — COMPLETE & frozen.
- **P35** "Beta-Estimation Robustness & Signal-Stability Closure" — COMPLETE & frozen.
- **P36** "Walk-Forward / OOS Validation + Rank-Weighted Construction Closure" — COMPLETE & frozen.
- **P37** "Cost-Aware Turnover & Capacity Closure" (verdict RETAIN shipped default) — COMPLETE & frozen.
- **P38** "Deflated Significance & Tail-Risk Closure" — COMPLETE & committed at `726d4bd`; WP1 `SURVIVES_DEFLATION` over `n_trials_total=552` (marginal p 0.079/0.056, reported honestly); WP2 tail-risk/CVaR `ALL_NEUTRALITY_OK` (8/8 seeds); WP3 `docs/BAB_P38_DECISION.md` + replay/gate wire.
- **P39 WP1** "Regime-Conditional Deflated Significance & Tail Risk" — COMPLETE; honest negative `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`.
- **P39 WP2** "Cross-Fixture Replication" — COMPLETE; honest negative `DOES_NOT_REPLICATE` (3 of 8 seeds survive over `n_trials_total=552`; all neutrality OK).
- **P39 WP3** "Decision Doc + Documentation-Integrity Closure + Gate Wire" — COMPLETE & committed at ancestor `3d08169`.
- **P39 WP0 determinism test** `tests/test_bab_p38_determinism.py` — EXISTS (committed).
- **P28 WP2–WP4 — MAINTAINER-GATED (not agent-executable):** WP2 CI gate enforcement needs `workflows:write` (repo token lacks it); WP3 real-market data needs a maintainer-supplied licensed CSV (Coinbase public API returns 403); WP4 live deployment needs WP2+WP3 + maintainer authorization. Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment — route to the maintainer.

---

## BOTTLENECKS REMOVED (condensed — load-bearing items kept; do NOT revert/re-fix)

- **#16 Stale handoff vs. checkpoint/gate state — REMOVED (refreshed 2026-11-25T07:51:17Z).** The prior handoff pointed at a running gate PID; that gate has now completed (FAILED on doc pointer tests). This refresh records the actual gate outcome so the next session FIXES the doc mismatch and re-runs — no phantom diff, no waiting on a nonexistent gate.
- **#8 Stale exact-equality guards → RED gate on a green tree — REMOVED.** `tests/test_bab_p29_replay_coverage.py` `EXPECTED_NAMES` += 7 json-only summaries; `tests/test_bab_p29_decision_replay.py` `EXPECTED_NAMES` += 9 docs; `docs/COVERAGE_NOTES.md` line 7 reworded; `tests/test_bab_p30_ledger_analyzer.py` count corrected. Exact-equality preserved (a new artifact still fails closed). This is the documented guard-maintenance pattern.
- **#9 Structural RUNTIME bottleneck — DOCUMENTED, not a correctness problem.** `--check-provenance`/`--xproc` rebuild ~8 heavy Monte-Carlo artifacts in fresh interpreters. **Mitigation:** run the gate as a background/persistent process and poll the log across turns; do NOT wrap in one blocking call and do NOT launch a second concurrent gate. The provenance math is a legitimate determinism proof — do NOT delete, skip, or weaken it.
- **#10 Frozen P27 `.md` trailing-newline trap — DOCUMENTED + restore path** (`git checkout -- research_state/bab_p27/` after any full run; JSON artifacts unaffected).
- **#12 xproc `signal_null_battery` timeout under xdist load — REMOVED.** `scripts/bab_replay_full.py` per-artifact `timeout` raised 600→3600 s (a runtime guard, NOT a weakening). Do NOT lower it back.
- **#13 Coverage 99%→100% gap (11 defensive lines) — REMOVED** via `TestValidationErrors` in `tests/test_bab_p35_beta_estimators.py` + a non-finite `_canonicalize` test in `tests/test_bab_reconciliation_p11_coverage.py`. Do not lower the 100% floor.
- **#14 Concurrent-session edits — DOCUMENTED.** Always `git status`/`git diff` before editing; never blindly revert another session's in-flight fix; never run two gates at once.
- **#15 Stale hard-coded ledger count → RED gate — REMOVED.** `test_since_filters_runs` now recomputes the expected count from `research_state/workflow_run_diagnostics.jsonl` (exact recomputation). Do NOT re-introduce a hard-coded count.
- **Stale `docs/COVERAGE_NOTES.md` — CORRECTED this session** to drop the obsolete "10 failed"/old-HEAD text and record the accurate current state (pytest phase TOTAL 100% / 7670 passed; full-gate close-out still pending). Update it again with the GREEN date/HEAD once WP0 lands.
- **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP0 is complete **and** P40 is either complete or explicitly maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

## HARD GATES EVERY SESSION (repo root, in order — run after baseline is green; while a gate is active, poll it instead of launching these in parallel)

```bash
python3 -m ruff check .
bash scripts/bab_quick.sh
bash scripts/bab_reconcile_gate.sh
python3 scripts/bab_replay_full.py --self-test
python3 scripts/bab_replay_full.py --check-provenance
python3 scripts/bab_replay_decisions.py --self-test
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json
python3 scripts/bab_workflow_diagnostics.py --self-test
python3 scripts/bab_workflow_diagnostics.py --analyze-ledger
python3 -m pytest -q tests/test_bab_p31_registry_completeness.py
python3 -m pytest -q tests/test_bab_p32_decision_replay_p24.py tests/test_bab_p32_decision_registry_completeness.py
python3 -m pytest -q tests/test_bab_p33_*.py
python3 -m pytest -q tests/test_bab_p34_*.py
python3 scripts/bab_p34_multiseed_robustness.py --check-multiseed-summary
bash scripts/bab_replay_gate.sh
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh   # P39 WP0 / P40: multi-hour budget, background + poll
```
**Inner loop while iterating (use this, NOT the full gate, to stay fast):**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p30_ledger_analyzer.py tests/test_bab_p39_*.py tests/test_bab_p38_determinism.py
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary          # P39 WP1 (DONE)
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary        # P39 WP2 (DONE)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary     # P38 WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary                # P38 WP2 (DONE)
python3 scripts/bab_replay_decisions.py --subset p39_decision.md             # P39 WP3 (DONE)
```

> **CRITICAL GUARDRAIL — NEVER run a generator with bare/no args or an unrecognized flag** (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where unsupported). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` and turning a RED gate falsely GREEN. Verify with `--check-*` flags ONLY. To intentionally regenerate during a fix, run the generator (writes the active campaign path only), `git diff` to confirm the change is intentional, and `git checkout -- research_state/` any accidental frozen-artifact mutation immediately.

> **FROZEN-ARTIFACT TRAP — running the FULL pytest suite / `bab_gate.sh` appends one trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md`** (the `run_*()` P27 tests write to the committed path). After ANY full run, `git checkout -- research_state/bab_p27/`. (The P30 ledger test also rewrites `research_state/bab_p30/ledger_summary.json`'s `analyzed_at_utc`; revert with `git checkout -- research_state/bab_p30/ledger_summary.json`.)

---

## How the determinism layer works (reuse the pattern if new drift appears — do NOT redo)

Committed artifacts are byte-reproduced by canonicalization, not version pinning: signed-zero normalization (`-0.0`→`0.0`), 12-significant-digit rounding of float metrics, and round-before-hash in `reconciliation.py::_checksum`. **Pattern for NEW drift:** classify as signed-zero, ~1-ULP float (round to 12 sig-digits via a `_round_floats` helper), or raw hash over floats (canonicalize before hashing). Regenerate through the generator (confirm diff, keep), then cascade-regenerate any manifest/decision doc that embeds the changed artifact (`doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`, and any `docs/BAB_*_DECISION.md`).

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P39 WP0, then P40). Persisting this handoff via the normal session checkpoint is expected and is NOT what this forbids — what it forbids is calling a refresh "done" instead of doing the binding work.
- Re-creating `tests/test_bab_p38_determinism.py` (EXISTS, committed).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p39/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, `docs/BAB_P20..P39_DECISION.md`, or any P20–P39 script/generator (frozen). Exception: legitimate regeneration *through the generator* with a real determinism improvement, or the documented `doc_replay_summary.json` / `docs/BAB_*_DECISION.md` cascade when a new campaign registers a decision doc.
- Editing any P25/P26/P27/P28-WP0–W1/P30–P39-WP3 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen). **Never commit the trailing-newline mutation of `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md`.**
- Hand-typing any number into a P20–P40 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe/tail number without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P40 reproducibility** (hard-coding `sha256`/summary, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate fix is the documented determinism pattern, never a hand-forged hash.
- **Re-doing P20–P38 or P39 WP1/WP2/WP3** (COMPLETE & frozen; verify with the `--check-*`/`--subset` flags only).
- **Reversing the honest WP1/WP2 (and future P40) negatives to force a positive result.** Negatives are findings; report them, do not game them.
- Creating parallel handoff docs (this file is the single source of truth).