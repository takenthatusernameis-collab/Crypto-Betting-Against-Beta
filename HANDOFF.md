# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it. Only `HANDOFF.md` is tracked at repo root; keep it that way.**

- **Timestamp (UTC):** 2026-11-25T18:21:33Z — single durable handoff refreshed this session. **P39 WP0 is DONE:** the `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` full gate finished **GREEN end-to-end**, exit 0 — pytest TOTAL **100%** (0 missed / 6730 statements), `7675 passed / 39 skipped` in 3360.6s (0:56:00), coverage floor met, replay gate + P30 + P33–P39 post-pytest phases all GREEN (log `/tmp/bab_gate_p39w0_v2.log`). Coverage recorded in `docs/COVERAGE_NOTES.md`. Frozen P27/P30 artifacts restored after the run.
- **HEAD:** `44e2868b8033ac59bb963f172bcb5e5d18ddfc6f` (`chore(kilo): checkpoint agent session`). The checkpoint hash advances every session — re-derive with `git rev-parse HEAD` at session start; never cite a stale hash. Campaign code is frozen at its campaign commits (P38 at `726d4bd`, P39 WP3 at ancestor `3d08169`); treat those as ancestors, never as HEAD. Working tree carries one **uncommitted** intentional fix: `scripts/bab_gate.sh` P30 quoting bug (flags moved outside the quoted path) — this was the real blocker that kept the full gate from ever reaching GREEN; commit it only on explicit user request.
- **Working tree (verified 2026-11-25T18:21:33Z):** clean at HEAD `44e2868` except the uncommitted `scripts/bab_gate.sh` P30 quoting fix. Frozen P27 `.md` files restored (no trailing-newline mutation left); P30 `ledger_summary.json` restored (no `analyzed_at_utc` mutation left). No background process running; no gate PID to reconcile. Do NOT start a background gate and leave it running — that recreates the stale-PID bottleneck.
- **Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta factor strategy** for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence about a factor strategy*. Synthetic fixtures are NOT real market data — never present them as evidence of real profitability.

**BINDING ROW = Campaign P40**

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-25T18:21:33Z)

**PRIORITIZATION BY REPO NAME (binding & inescapable):** this is a *factor strategy* repo (`Crypto-Betting-Against-Beta`). The repo's entire value proposition is honest, reproducible, artifact-gated evidence about the Betting Against Beta factor. The highest-value next heavy work is **factor robustness** — does the BAB factor's apparent edge survive across independently parameterized synthetic universes, under a pre-registered multiplicity correction, and net of costs — NOT docs, NOT handoff churn, NOT CI plumbing (maintainer-gated). That work is **Campaign P40**. It is inescapable and ordered WP1→WP4. **P39 WP0 is GREEN (full gate exit 0, TOTAL 100%), so P40 is UNBLOCKED starting this session.** Any session that does not execute P40 WP1→WP4 in order has FAILED its binding obligation.

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable):** P39 WP0 is GREEN — start P40 WP1 in this session and carry WP1→WP4 to completion. A handoff-only / docs-only / gate-only / count-only / planning commit that substitutes for P40 is a FAILED session.

**State you inherit (verified firsthand 2026-11-25T18:21:33Z):**
- **P39 WP0 full-gate close-out is DONE:** `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` → exit 0, TOTAL 100% (6730/0 missed), 7675 passed / 39 skipped, coverage floor met, replay gate + P30 + P33–P39 post-pytest phases GREEN (log `/tmp/bab_gate_p39w0_v2.log`). Coverage recorded in `docs/COVERAGE_NOTES.md`.
- **Bottleneck removed — P30 quoting bug fixed:** `scripts/bab_gate.sh` invoked `python3 "$ROOT/scripts/bab_workflow_diagnostics.py --self-test"` (flag trapped inside the quoted path → Errno 2), which made the full gate fail at P30 no matter what. Fixed by moving flags outside the quotes (`python3 "...py" --self-test`, same for `--analyze-ledger` / `--summary-json`). The gate now reaches GREEN end-to-end. Do NOT revert this fix.
- **Doc-pointer guard is GREEN:** `python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py` → **7 passed, 1 skipped**. Do NOT re-fix it.
- **P33 doc-consistency is GREEN:** `--check-doc-summary` prints OK (P38/P39 entries present). Do NOT hand-edit or revert it.
- **All fast post-pytest phases are GREEN** firsthand (ruff clean, P33 fidelity/registry/doc-consistency, P34–P39 `--check-*` byte-identical). Re-verify with `--check-*` flags only; frozen P27/P28–P39 artifacts untouched except the trailing-newline/P30-ledger mutations a full run makes (restore with `git checkout -- research_state/bab_p27/ research_state/bab_p30/ledger_summary.json` after any full run).
- **Baseline is GREEN:** `ruff check .` → All checks passed; `bash scripts/bab_quick.sh` → 104 + 195 passed.

**BINDING FIRST ACTION (WP0 is GREEN — go straight to Campaign P40 WP1):**
1. **Start Campaign P40 WP1 immediately** (charter below: `scripts/bab_p40_fixture_battery.py` + `research_state/bab_p40/fixture_battery_summary.{json,md}` + `--check-fixture-battery-summary` byte-identical). Write the generator, run it to produce the battery summary, verify `--check-fixture-battery-summary` passes, add the P40 block to `scripts/bab_replay_full.py` (`json_only, no_xproc`) and `bab_p40` to `scripts/bab_gate.sh`, add the P40 determinism test mirroring `test_bab_p38_determinism.py`, and run `bash scripts/bab_quick.sh` + `python3 -m ruff check .` to keep the baseline green.
2. **Then P40 WP2** (meta-analysis with pre-registered multiplicity correction) → WP3 (costed survival) → WP4 (decision doc + gate wire + pointer-guard registration + determinism test + full-gate close-out at `BAB_GATE_MIN_COVERAGE=100`). Execute WP1→WP4 in order; do not skip ahead.
3. **Stopping after WP0 with P40 unstarted is a FAILED session.** P40 is the binding row; there is no "no explicit directions" escape — if a future session finds no new user directive, it MUST execute P40 WP1→WP4.

**Gate-exit handling (only if you re-run the full gate while iterating P40):**
- Exit 0 + `TOTAL 100% >= 100%` → proceed; record coverage in `docs/COVERAGE_NOTES.md`; restore frozen P27/P30 artifacts after the run.
- Exit 1 with a real test failure → bisect to a **code change** (never an artifact hand-edit, never a loosened/`xfail`ed test); re-run the fast inner loop, then the gate.
- Exit 1 with `COVERAGE FLOOR NOT MET` → inspect the `Missing` column, add targeted tests; coverage is saturated at 100%; do not lower the floor.
- Do NOT commit unless the user explicitly asks.

**Do NOT re-do (all COMPLETE & frozen):** P20–P38; P39 WP1 (`--check-regime-summary` byte-identical); P39 WP2 (`--check-cross-fixture-summary` byte-identical, verdict `DOES_NOT_REPLICATE`); P39 WP3 (ancestor `3d08169`, `--subset p39_decision.md` byte-identical); `tests/test_bab_p38_determinism.py` (EXISTS, committed); **the P33 doc-consistency regeneration (DONE this session — `--check-doc-summary` now OK; do not hand-revert it)**. Both P39 verdicts are honest negatives — report them, never reverse them. Do NOT re-fix the xproc timeout (now 3600 s), the 8-record P29 provenance ledger, the P35 tests, or the P30 ledger-count test.

---

## NEXT FOCUS CAMPAIGN — P40 (defined so heavy work is unavoidable after WP0)

**Campaign P40 — "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict".** Declared 2026-11-24T15:35:11Z · Priority HIGH · Status: STARTED (P39 WP0 GREEN 2026-11-25T18:15:00Z; WP1 binding now). Fully offline, deterministic, zero maintainer dependency. **IN-ESCAPABILITY CLAUSE (prioritized by repo name — a *factor* strategy, so the next heavy work must be factor-robustness, not docs):** the moment P39 WP0 is GREEN, P40 WP1 is the binding row. There is no "no explicit directions" escape: if a future session finds no new user directive, it MUST execute P40 WP1→WP4 in order. Rationale: P38 answered the pooled questions; P39 WP1/WP2 answered within-regime and single-second-fixture replication (both honest negatives). P40 generalizes replication to a *battery* of independently parameterized synthetic universes and consolidates P34–P39 into one authoritative, multiplicity-controlled verdict. Do NOT reverse any prior negative; report whatever P40 finds honestly.

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

- **#16 Stale handoff vs. checkpoint/gate state — REMOVED (refreshed 2026-11-25T08:04:44Z).** The prior handoff described a gate that FAILED on 5 doc-pointer tests; verified firsthand this session that the doc-pointer guard is now GREEN (7 passed / 1 skipped), `ruff check .` is clean, `bab_quick.sh` is GREEN (104 + 195 passed), and the tree was clean at session start at HEAD `0b8d784`. This refresh records the true state so the next session goes straight to the full-gate close-out — no phantom doc fix, no waiting on a nonexistent gate. Do NOT start a background gate and leave it running; that recreates the stale-PID problem.
- **#17 Stale P33 doc-consistency manifest → RED post-pytest gate phase — REMOVED (2026-11-25T09:18:32Z).** `bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json` was RED because the committed manifest predated the P38/P39 decision docs and was missing their replay-gated entries (16 vs 18). Fixed by legitimate regeneration through the generator (`--summary-json`); diff is exactly the two P38/P39 blocks (+10 lines). No test pins the file, so this fails no exact-equality guard. This was the true, previously-unobserved WP0 post-pytest blocker. If a future campaign registers a new decision doc, regenerate this manifest the same way (never hand-edit). Do NOT revert it.
- **#9 Structural RUNTIME bottleneck — DOCUMENTED, not a correctness problem.** `--check-provenance`/`--xproc` rebuild ~8 heavy Monte-Carlo artifacts in fresh interpreters. **Mitigation:** run at most one gate as a tracked background process with an active reader in the same session; poll its log to terminal exit, record the exit code, and restore frozen artifacts. Do NOT wrap it in one blocking call when that would hit the runner timeout, do NOT launch a second concurrent gate, and never leave a live PID across sessions. The provenance math is a legitimate determinism proof — do NOT delete, skip, or weaken it.
- **#8 Stale exact-equality guards → RED gate on a green tree — REMOVED.** `tests/test_bab_p29_replay_coverage.py` `EXPECTED_NAMES` += 7 json-only summaries; `tests/test_bab_p29_decision_replay.py` `EXPECTED_NAMES` += 9 docs; `docs/COVERAGE_NOTES.md` line 7 reworded; `tests/test_bab_p30_ledger_analyzer.py` count corrected. Exact-equality preserved (a new artifact still fails closed). This is the documented guard-maintenance pattern.
- **#10 Frozen P27 `.md` trailing-newline trap — DOCUMENTED + restore path** (`git checkout -- research_state/bab_p27/` after any full run; JSON artifacts unaffected).
- **#12 xproc `signal_null_battery` timeout under xdist load — REMOVED.** `scripts/bab_replay_full.py` per-artifact `timeout` raised 600→3600 s (a runtime guard, NOT a weakening). Do NOT lower it back.
- **#13 Coverage 99%→100% gap (11 defensive lines) — REMOVED** via `TestValidationErrors` in `tests/test_bab_p35_beta_estimators.py` + a non-finite `_canonicalize` test in `tests/test_bab_reconciliation_p11_coverage.py`. Do not lower the 100% floor.
- **#14 Concurrent-session edits — DOCUMENTED.** Always `git status`/`git diff` before editing; never blindly revert another session's in-flight fix; never run two gates at once.
- **#15 Stale hard-coded ledger count → RED gate — REMOVED.** `test_since_filters_runs` now recomputes the expected count from `research_state/workflow_run_diagnostics.jsonl` (exact recomputation). Do NOT re-introduce a hard-coded count.
- **Stale `docs/COVERAGE_NOTES.md` — CORRECTED this session.** Now records the GREEN full-gate close-out (2026-11-25T18:21:33Z, HEAD `44e2868`, TOTAL 100%, 7675 passed/39 skipped). The heavy replay-gate single-run close-out is DONE (exit 0).
- **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP0 is complete **and** P40 is either complete or explicitly maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.
- **#18 Full gate blocked at P30 by quoting bug — REMOVED (2026-11-25T18:15:00Z).** `scripts/bab_gate.sh` invoked `python3 "$ROOT/scripts/bab_workflow_diagnostics.py --self-test"` with the flag trapped inside the quoted path (Errno 2), so the gate failed at P30 regardless of test results. Fixed by moving flags outside the quotes (`python3 "...py" --self-test`, same for `--analyze-ledger` / `--summary-json`). The full gate now reaches GREEN end-to-end (exit 0). Do NOT revert.

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