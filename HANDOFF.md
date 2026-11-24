# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it. Only `HANDOFF.md` is tracked at repo root; keep it that way.**

- **Timestamp (UTC):** 2026-11-24T20:52:46Z (single durable handoff refreshed — P39 WP0 full gate RUNNING as persistent background process pid 2818 (id `bgp_20f515c52001ZS0OqmbHVvbYcM`), log at `/tmp/bab_gate_p39.log`; pytest ~34% complete, no `TOTAL` line yet; toolchain bootstrapped; ruff GREEN; `bab_quick.sh` GREEN).
- **HEAD:** `f87cf54f37beb643c390cf9f053e43fb71cdf09e` (a `chore(kilo): checkpoint agent session` commit — only HANDOFF.md refreshed; campaign code frozen at its campaign commits — P38 at `726d4bd`, P39 WP3 at ancestor `3d08169`. Do NOT cite `3d08169` as HEAD; it is an ancestor.)
- **Working tree:** CLEAN (`git status --short` empty at 2026-11-24T20:52:46Z; the frozen P27 `.md` files have NOT been mutated yet).
- **Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. Synthetic fixtures are NOT real market data — never present them as evidence of real profitability.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-24T20:52:46Z)

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable): land P39 WP0 full-gate close-out — a GREEN `bash scripts/bab_gate.sh` at `BAB_GATE_MIN_COVERAGE=100`, TOTAL coverage recorded in `docs/COVERAGE_NOTES.md`, and the frozen P27 `.md` files restored.**

**State you inherit (verified 2026-11-24T20:52:46Z):** the prior baseline was GREEN (ruff, `bab_quick.sh`, all P38/P39 `--check-*` byte-identical, replay self-tests pass). The full gate is ALREADY RUNNING as a persistent background process:
`BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` (pid 2818; started ~20:44Z; ~34% through the pytest suite per `/tmp/bab_gate_p39.log`, no `TOTAL` line yet, ~50 min remaining on the long poles). The gate covers pytest (all test files) + coverage floor + `--check-provenance`/`--xproc` replay gate + P30–P39 summary checks (~80 min for the long poles, +~2 min for P34–P39 checks + coverage floor).

**FIRST ACTION — poll the already-running gate only (do NOT rerun the baseline, do NOT launch a second gate, and do NOT wrap the poll in a blocking call; parallel runs create the resource contention that stalled prior sessions):**
```bash
tail -n 40 /tmp/bab_gate_p39.log        # expect pytest output + a coverage TOTAL line
ps -eo pid,ppid,stat,etime,args | grep -E 'bab_gate|bab_replay' | grep -v grep
```
If the pids are alive and no `TOTAL` line exists, leave the gate running and poll again on the next turn. If the gate has DIED without `TOTAL`, relaunch it as a background process and poll; a dead gate is a real blocker, not a reason to idle. When the gate exits:
1. If exit 0 and `TOTAL 100% >= 100%` → record TOTAL coverage % + pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`.
2. Run `git checkout -- research_state/bab_p27/` to undo the trailing-newline mutation of the two frozen P27 `.md` files.
3. Re-run `bash scripts/bab_quick.sh` and `python3 -m ruff check .` to confirm still GREEN.
4. Confirm working tree clean except intended changes (`docs/COVERAGE_NOTES.md` + restored P27 `.md`).
5. Commit ONLY on explicit user request.

**Do NOT re-do (all COMPLETE & frozen):** P20–P38; P39 WP1 (`--check-regime-summary` byte-identical); P39 WP2 (`--check-cross-fixture-summary` byte-identical, verdict `DOES_NOT_REPLICATE`); P39 WP3 (committed at ancestor `3d08169`, `--subset p39_decision.md` byte-identical); `tests/test_bab_p38_determinism.py` (EXISTS, committed). Both P39 verdicts are honest negatives — report them, never reverse them.

**A handoff-only / docs-only / gate-only / count-only / planning commit that substitutes for WP0 work is a FAILED session while WP0 is open.** If you catch yourself producing only a handoff refresh, a green re-run log, or a planning note without the full gate GREEN at `BAB_GATE_MIN_COVERAGE=100` + P27 `.md` restored + coverage recorded, STOP — that is a failed session, not progress.

**After WP0 lands, the next binding heavy work is Campaign P40 (charter below) — it is inescapable and defined so no future session can idle.**

---

## VERIFIED BASELINE (firsthand 2026-11-24T14:38:15Z; re-confirmed GREEN at 15:35:11Z for ruff/quick/tree)

- `python3 -m ruff check .` → `All checks passed!`
- `bash scripts/bab_quick.sh` → `quick preflight OK` (targeted trio 104 passed; smoke 195 passed)
- `python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary` → `PASS (byte-identical)`
- `python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary` → `PASS (byte-identical)`
- `python3 scripts/bab_p39_regime_conditional.py --check-regime-summary` → `PASS (byte-identical)` — WP1 DONE
- `python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary` → `PASS (byte-identical)` — WP2 DONE, `DOES_NOT_REPLICATE`
- `python3 scripts/bab_replay_full.py --self-test` / `bab_replay_decisions.py --self-test` → `pass:true`
- `python3 scripts/bab_replay_decisions.py --subset p39_decision.md` → byte-identical — WP3 DONE
- Replay/registry/doc-pointer layer GREEN (152 passed / 2 skipped) after guard fixes.
- Only `HANDOFF.md` at repo root — no stray parallel doc to fold in.

### FIRST ACTION ONLY IF THE GATE IS DEAD OR A BASELINE REGRESSION IS FOUND (otherwise poll first; do NOT duplicate the active gate)
```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary # PASS
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary           # PASS
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary     # PASS (WP1 DONE)
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary   # PASS (WP2 DONE)
python3 scripts/bab_replay_full.py --self-test                           # pass:true
python3 scripts/bab_replay_decisions.py --self-test                      # pass:true
python3 scripts/bab_replay_decisions.py --subset p39_decision.md         # byte-identical (WP3 DONE)
python3 -m pytest -q tests/test_bab_p39_*.py tests/test_bab_p38_determinism.py
```

> **CRITICAL GUARDRAIL — NEVER run a generator with bare/no args or an unrecognized flag** (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where unsupported). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` and turning a RED gate falsely GREEN. Verify with `--check-*` flags ONLY. To intentionally regenerate during a fix, run the generator (writes the active campaign path only), `git diff` to confirm the change is intentional, and `git checkout -- research_state/` any accidental frozen-artifact mutation immediately.

> **FROZEN-ARTIFACT TRAP — running the FULL pytest suite / `bab_gate.sh` appends one trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md`** (the `run_*()` P27 tests write to the committed path). After ANY full run, `git checkout -- research_state/bab_p27/`. JSON artifacts are unaffected — only those two `.md` files.

---

## BINDING ROW = Campaign P39 — WP0 full-gate close-out (the ONLY remaining agent-executable P39 row; inescapable)

- `tests/test_bab_p38_determinism.py` EXISTS (committed) — do NOT re-create.
- Run `BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` to a GREEN completion (background + poll; ~80 min for `--xproc`/`--check-provenance`, +~2 min for the P34–P39 checks + coverage floor).
- Record TOTAL coverage % + pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`.
- `git checkout -- research_state/bab_p27/` to restore the two frozen P27 `.md` files.
- **Acceptable exits ONLY:** (a) WP0 delivered GREEN at `BAB_GATE_MIN_COVERAGE=100` + coverage recorded + P27 restored + tree clean; or (b) a genuine RED baseline regression found in FIRST ACTION, bisected and fixed with a code change (not an artifact hand-edit).

---

# NEXT FOCUS CAMPAIGN — P40 (defined so heavy work is unavoidable after WP0)

**Campaign P40 — "Multi-Fixture Robustness Meta-Analysis & Consolidated Factor Verdict".** Declared 2026-11-24T15:35:11Z · Priority HIGH · Status: PENDING (starts only after P39 WP0 lands GREEN). Fully offline, deterministic, zero maintainer dependency. Rationale (prioritized by repo name — a *factor* strategy): P38 answered the pooled questions, P39 WP1/WP2 answered within-regime and single-second-fixture replication (both honest negatives). P40 generalizes replication to a *battery* of independently parameterized synthetic universes and consolidates P34–P39 into one authoritative, multiplicity-controlled verdict. Do NOT reverse any prior negative; report whatever P40 finds honestly.

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

### Bottlenecks removed (condensed — load-bearing items kept)

- **#8 Stale exact-equality guards → RED gate on a green tree — REMOVED (do NOT revert/re-fix).** `tests/test_bab_p29_replay_coverage.py` `EXPECTED_NAMES` += 7 json-only summaries (`cost_surface_summary`, `capacity_summary`, `turnover_summary`, `deflated_summary`, `tail_risk_summary`, `regime_summary`, `cross_fixture_summary`); `tests/test_bab_p29_decision_replay.py` `EXPECTED_NAMES` += 9 docs (`p22_kickoff.md`, `p23_kickoff.md`, `p24_kickoff.md`, `p24_decision.md`, `p35_decision.md`, `p36_decision.md`, `p37_decision.md`, `p38_decision.md`, `p39_decision.md`); `docs/COVERAGE_NOTES.md` line 7 reworded; `tests/test_bab_p30_ledger_analyzer.py` count 20→27. Exact-equality preserved (a 37th artifact still fails closed). This is the documented guard-maintenance pattern.
- **#9 Structural RUNTIME bottleneck — DOCUMENTED, not a correctness problem.** `--check-provenance` and `--xproc` (also via `tests/test_bab_p31_provenance_replay.py`, `tests/test_bab_p29_xproc_determinism.py`) rebuild ~8 heavy Monte-Carlo artifacts twice each in fresh interpreters (~80 min). **Mitigation:** run the gate as a background/persistent process and poll the log across turns; do NOT wrap in one blocking call. If the runner cannot keep a background process alive, run the fast 95% first, then `--check-provenance` and `--xproc` once on a large uninterrupted budget. The provenance math is a legitimate determinism proof — do NOT delete, skip, or weaken it.
- **#10 Frozen P27 `.md` trailing-newline trap — DOCUMENTED + restore path given** (`git checkout -- research_state/bab_p27/` after any full run).
- **#11 Dead gate + missing toolchain — REMOVED in this session (2026-11-24T20:44:33Z).** Prior session's background gate process was dead (no pids, no `/tmp/bab_gate_p39.log`); `numpy`/`pandas`/`scipy`/`pytest`/`pytest-cov`/`xdist`/`hypothesis`/`coverage`/`ccxt`/`ruff` were all missing. Fixed by running `CI=true bash scripts/bab_bootstrap.sh` (toolchain ready) then relaunching `BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` as a persistent background process (pid 2818). Baseline re-verified GREEN: `ruff check .` → All checks passed; `bab_quick.sh` → quick preflight OK (195 passed).
- **Stale HEAD pointer — REMOVED.** Always cite the current `git rev-parse HEAD` (`f87cf54f37beb643c390cf9f053e43fb71cdf09e` at 2026-11-24T20:52:46Z); treat `3d08169` as an ancestor, never as HEAD.
- **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP0 is complete **and** P40 is either complete or explicitly maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

## HARD GATES EVERY SESSION (repo root, in order — run after baseline is green; while the P39 WP0 gate is active, poll it instead of launching these in parallel)

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
python3 -m pytest -q tests/test_bab_p39_*.py tests/test_bab_p38_determinism.py
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary          # P39 WP1 (DONE)
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary        # P39 WP2 (DONE)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary     # P38 WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary                # P38 WP2 (DONE)
python3 scripts/bab_replay_decisions.py --subset p39_decision.md             # P39 WP3 (DONE)
```

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