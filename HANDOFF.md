# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T13:48:11Z (handoff refreshed; baseline re-verified firsthand at this timestamp)
- **Re-verification Timestamp (UTC):** 2026-11-23T13:48:11Z — ALL BASELINE CHECKS GREEN (ruff, bab_quick.sh, P38 --check-deflated-summary, P38 --check-tail-risk-summary, P39 --check-regime-summary, P39 --check-cross-fixture-summary, bab_replay_full --self-test, bab_replay_decisions --self-test, pytest test_bab_p39_*.py). Working tree CLEAN. HEAD `2b6d438`. **Binding row confirmed: P39 WP3 (Decision doc + documentation-integrity closure + gate wire) — NOT STARTED.**
- **HEAD:** `2b6d438` (last commit). **P38 is fully COMMITTED at `726d4bd` (code frozen there). P39 WP1 is DONE AND COMMITTED (checkpoint commits `2e5a336..23ca0a8`). P39 WP2 is DONE AND COMMITTED — the WP2 artifacts (`scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.{json,md}`, `tests/test_bab_p39_cross_fixture.py`) plus P39-WP1 files are tracked in HEAD; `git diff --stat 726d4bd HEAD` = those P39 files + HANDOFF.md + docs/COVERAGE_NOTES.md only — no other code drift.** Working tree is CLEAN. There is **no uncommitted work to commit** — the old claim of "uncommitted WP1/WP2 work" is stale and REMOVED.
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **P38 is COMPLETE and committed (WP1–WP3).** **P39 WP1 (regime-conditional) is COMPLETE and committed; honest verdict `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`.** **P39 WP2 (cross-fixture replication) is COMPLETE and committed; honest verdict `DOES_NOT_REPLICATE` (3 of 8 seeds survive deflation over n_trials_total=552; all neutrality OK).** The binding row is now **P39 WP3 "Decision doc + documentation-integrity closure + gate wire"** → then WP0 close-out. P39 WP3 has NOT been started — no `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py` exist yet; the `p39_decision.md` registration exists in `bab_replay_decisions.py` but its generator module does not.
  - **P39 WP0 (full-gate + determinism close-out) — NOT DONE:** `tests/test_bab_p38_determinism.py` does not exist; the full `bash scripts/bab_gate.sh` (with `BAB_GATE_MIN_COVERAGE=100`) has NOT been run to completion. Large-time-budget hygiene; does NOT block WP3.
  - **P39 WP1 — DONE & committed.** `scripts/bab_p39_regime_conditional.py` + `research_state/bab_p39/regime_summary.{json,md}` + `tests/test_bab_p39_regime_conditional.py`; `--check-regime-summary` byte-identical; 91 tests pass; ruff clean.
  - **P39 WP2 — DONE & committed.** `scripts/bab_p39_cross_fixture.py` + `research_state/bab_p39/cross_fixture_summary.{json,md}` + `tests/test_bab_p39_cross_fixture.py`; `--check-cross-fixture-summary` byte-identical; verdict `DOES_NOT_REPLICATE` (see summary). Do NOT re-do it.
  - **P39 WP3 — NOT STARTED (BLOCKING FIRST TASK).** `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py` missing; `regime_summary` + `cross_fixture_summary` registered in `bab_replay_full.py` (done); `p39_decision.md` registered in `bab_replay_decisions.py` (done) but `generate_p39_decision.py` missing so the registration is dangling; no P39 block in `bab_gate.sh`; no P39 block in `tests/test_bab_p34_doc_pointer_guard.py` allow-list; `docs/BAB_P39_DECISION.md` not created; `doc_replay_summary.json` not regenerated for P39.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T13:48:11Z)

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable): land P39 WP3 (decision doc + documentation-integrity closure + gate wire)** — create `generate_p39_decision.py` + `docs/BAB_P39_DECISION.md` + `tests/test_bab_p39_decision_consistency.py`; register `p39_decision.md` (already present in `bab_replay_decisions.py` — implement the generator so it is not dangling); register `regime_summary` + `cross_fixture_summary` in `bab_replay_full.py` (already present); wire a P39 block into `scripts/bab_gate.sh`; add `"P39"` to the pointer-guard allow-list if needed; regenerate `research_state/bab_p32/doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`; keep `ruff check .` clean. **P39 WP1 and WP2 are DONE and committed — do NOT re-do them. A handoff-only / docs-only / verification-only commit that substitutes for WP3 work is a FAILED session while WP3 is open.** If you catch yourself producing only a handoff refresh, a green re-run log, or a planning note without new `generate_p39_decision.py` + `docs/BAB_P39_DECISION.md` + `tests/test_bab_p39_decision_consistency.py` code + tests + byte-identical registrations, STOP — that is a failed session, not progress.

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. **P20–P38 are COMPLETE and frozen — do NOT re-open them. P39 WP1 and WP2 are COMPLETE — do NOT re-open them. Your binding heavy work is P39 WP3 → WP0 (close-out). Start WP3 immediately.**

**Prioritization by repo name:** the repo implements a *factor* strategy. P38 answered the two *pooled* questions (deflated significance `SURVIVES_DEFLATION`; unconditional tail `ALL_NEUTRALITY_OK`). P39 WP1 answered the *within-regime stability* question — honest negative (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; high-vol regimes fail). P39 WP2 answered *cross-fixture replication* — honest negative (`DOES_NOT_REPLICATE`; 3/8 seeds survive; pooled P38 verdict is fixture-dependent). With both replication axes closed honestly, the binding work is to bind the results into a decision doc + gate (WP3) and close out hygiene (WP0). P39 WP3 → WP0, in that order. Start WP3 immediately; do not drift into re-verification of frozen campaigns.

## VERIFIED BASELINE — firsthand this session (working tree = CLEAN, HEAD `2b6d438`, code frozen at P38 `726d4bd` + committed P39 WP1 + WP2; numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED; re-verified 2026-11-23T13:48Z)

**Re-verified firsthand at 2026-11-23T13:48Z (HEAD `2b6d438`):**
- **GREEN (confirmed):**
  - `python3 -m ruff check .` → `All checks passed!` (exit 0).
  - `bash scripts/bab_quick.sh` → `quick preflight OK` (195 passed).
  - `python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p39_regime_conditional.py --check-regime-summary` → `PASS (byte-identical)` — WP1 DONE, do NOT re-do.
  - `python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary` → `PASS (byte-identical)` — WP2 DONE, verdict `DOES_NOT_REPLICATE`, do NOT re-do.
  - `python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary`, `--check-capacity-summary`, `--check-turnover-summary`, `bab_p36_rank_weighted.py --check-rank-weighted-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": true, "drift_detected": true, "pass": true}`.
  - `python3 scripts/bab_replay_decisions.py --self-test` → `pass:true`.
  - `python3 -m pytest -q tests/test_bab_p39_regime_conditional.py` → **91 passed**.
  - `python3 -m pytest -q tests/test_bab_p39_cross_fixture.py` → passed (part of 119 P39 tests).
  - `python3 -m pytest -q tests/test_bab_p38_tail_risk.py tests/test_bab_p38_decision_consistency.py` → 50 passed.
- **NOT completed (slow — do NOT treat as a blocker for P39 WP3):** the full `bash scripts/bab_gate.sh` (~5,800 tests + coverage + `--xproc` cross-process ledger + `--check-provenance`). A direct full-suite coverage run exceeded the 10-minute command budget and was terminated; this is **P39 WP0** close-out — run on a multi-hour budget session. It does NOT block WP3.

## FIRST ACTION (verify baseline, then start P39 WP3)

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary # expect PASS (byte-identical)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary           # expect PASS (byte-identical)
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary     # expect PASS — WP1 DONE, do NOT re-do
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary   # expect PASS — WP2 DONE, do NOT re-do
python3 scripts/bab_replay_full.py --self-test                           # expect pass:true
python3 scripts/bab_replay_decisions.py --self-test                      # expect pass:true
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 -m pytest -q tests/test_bab_p39_*.py
```
If any of the above is RED, a regression was introduced — bisect with `git log`/`git diff`; do NOT hand-edit artifacts to force green.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, run the generator (writes the active campaign path only), then `git diff` to confirm the change is intentional, and restore any accidental mutation of a frozen artifact with `git checkout -- research_state/` immediately.

> **FROZEN-ARTIFACT TRAP (hit during the P38 close-out; still true):** running the FULL pytest suite (or `bash scripts/bab_gate.sh`) appends one trailing newline to the frozen `research_state/bab_p27/risk_controls.md` and `research_state/bab_p27/reconciliation_e2e.md` — the `run_*()` P27 tests write to the committed path and the current renderer emits one newline more than was committed. After ANY full run, restore them with `git checkout -- research_state/bab_p27/` so the working tree is clean and you never accidentally commit a frozen-artifact change. (JSON artifacts are unaffected — only the two `.md` files.)

## How the P38/P39 determinism layer works (context — do NOT redo; reuse the pattern if new drift appears)

The committed artifacts are byte-reproduced by canonicalization, not version pinning: signed-zero normalization (`-0.0`→`0.0`), 12-significant-digit rounding of float metrics, and round-before-hash in `reconciliation.py::_checksum`. **Pattern for any NEW drift:** identify whether it is signed-zero, ~1-ULP float (round to 12 sig-digits at the source via a `_round_floats` helper), or a raw hash over floats (canonicalize before hashing). Regenerate through the generator (confirm diff, keep), then cascade-regenerate any manifest/decision doc that embeds the changed artifact (e.g. `doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`, and any `docs/BAB_*_DECISION.md`).

## HARD GATES EVERY SESSION (repo root, in order — run after the baseline is green)

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
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh   # P39 WP0: multi-hour budget
```
**Inner loop while iterating P39 (use this, NOT the full gate, to keep sessions fast):**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p39_*.py
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary          # P39 WP1 (DONE)
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary        # P39 WP2 (DONE)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary     # P38 WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary                # P38 WP2 (DONE)
python3 scripts/bab_replay_decisions.py --subset p39_decision.md             # P39 WP3 (BLOCKING)
python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary,regime_summary,cross_fixture_summary
```

---

# BINDING ROW = Campaign P39 — "Regime-Conditional & Cross-Fixture Robustness Closure" (+ P28 WP2–WP4 MAINTAINER-GATED)

**Declared:** 2026-11-23T13:48:11Z (binding row re-declared at handoff refresh) · **Campaign:** P39 "Regime-Conditional & Cross-Fixture Robustness Closure" · **Priority: HIGH** · **Status: ACTIVE — WP1 DONE; WP2 DONE; WP3 is the sole next agent-executable binding row.** P20–P38 COMPLETE and frozen; do NOT re-do them.

**Why P39 (prioritized by repo name):** P38 answered the two *pooled* factor questions. P39 WP1 answered *within-regime stability* — honest negative. P39 WP2 answered *cross-fixture replication* — honest negative (`DOES_NOT_REPLICATE`; pooled P38 verdict is fixture-dependent). The remaining binding work is WP3 (decision doc + gate wire) then WP0 (close-out).

## P39 WP0 — Full-gate + determinism close-out (HYGIENE; run on a large-time-budget session; does NOT block WP3)

- Run `BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` to completion; record the TOTAL coverage % and pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`. **After the run, `git checkout -- research_state/bab_p27/`** to undo the trailing-newline mutation of the two frozen P27 `.md` files.
- Add `tests/test_bab_p38_determinism.py`: a cross-version determinism regression proving (i) `_round_floats` byte-identity (signed-zero `-0.0`→`0.0`, 12-sig-fig rounding) and (ii) `reconciliation._checksum` round-before-hash is stable — i.e. re-running the pure `build_*()` twice and asserting byte-identity, and asserting a deliberately un-round-tripped float would diverge. This is the only outstanding P38 WP0 item.
- WP0 does NOT block WP3.

## P39 WP1 — Regime-conditional deflated significance + tail risk — **DONE & COMMITTED (do NOT re-do)**

- `scripts/bab_p39_regime_conditional.py` + `research_state/bab_p39/regime_summary.{json,md}` + `tests/test_bab_p39_regime_conditional.py`; `--check-regime-summary` byte-identical; 91 tests pass; ruff clean.
- **Verdict `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`** (honest negative): high-vol regimes (bull_high_vol DSR mean 0.412, bear_mid/high_vol thin) fail to survive deflation over `n_trials_total=552` (read-only from P38 WP1); neutrality holds at every populated cell; regimes are causal/lagged (no lookahead). Synthetic-provenance caveat required.

## P39 WP2 — Cross-fixture replication — **DONE & COMMITTED (do NOT re-do)**

- `scripts/bab_p39_cross_fixture.py` + `research_state/bab_p39/cross_fixture_summary.{json,md}` + `tests/test_bab_p39_cross_fixture.py`; `--check-cross-fixture-summary` byte-identical; ruff clean.
- **Verdict `DOES_NOT_REPLICATE`:** second independent synthetic universe (seed base 20270101, increment 9973, 32 assets, idio vol 0.006, beta range [0.20, 2.40]) — 3 of 8 seeds survive deflation over n_trials_total=552; all neutrality OK; pooled P38 verdict (`SURVIVES_DEFLATION` + `ALL_NEUTRALITY_OK`) does NOT replicate on this fixture. Honest negative — the P38 result is fixture-dependent, not a universal factor property. Synthetic-provenance caveat required; not market evidence.

## P39 WP3 — Decision doc + documentation-integrity closure + gate wire — **BLOCKING FIRST TASK (NOT STARTED)**

- `generate_p39_decision.py` + `docs/BAB_P39_DECISION.md` + `tests/test_bab_p39_decision_consistency.py` (zero hand-typed numbers; independent JSON re-render byte-identity; numeric-leaf check; explicit verdicts incl. "marginal"/"not market evidence"/"no real alpha"; AST no-harness scan; ruff clean). Reuse `generate_p38_decision.py` + `tests/test_bab_p38_decision_consistency.py` as the template. The decision doc MUST surface **both** the WP1 within-regime negative (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`) **and** the WP2 cross-fixture negative (`DOES_NOT_REPLICATE`).
- `p39_decision.md` is already registered in `scripts/bab_replay_decisions.py` (module `generate_p39_decision`, `REPORT_PATH = docs/BAB_P39_DECISION.md`) but the generator is missing — implement `generate_p39_decision.py` so the registration is not dangling, then **regenerate** `research_state/bab_p32/doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`.
- `regime_summary` + `cross_fixture_summary` are already registered in `scripts/bab_replay_full.py` as `json_only, no_xproc` (done for both WP1 and WP2).
- Wire a P39 block into `scripts/bab_gate.sh` (mirror the P38 block at lines ~216–225: `--check-regime-summary`, `--check-cross-fixture-summary`, P39 tests).
- The pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py` must include `"P39"` — add it if a new doc-pointer test fails; keep it green.
- Keep README / `docs/COVERAGE_NOTES.md` naming P39 as binding.

## P39 chartered acceptance thresholds

- WP0: full `bab_gate.sh` GREEN with `BAB_GATE_MIN_COVERAGE=100`; `tests/test_bab_p38_determinism.py` green; frozen P27 `.md` restored (`git status` clean except intended changes).
- WP1: **MET** — per-regime DSR + PSR + CVaR/ES + neutrality invariants at every (seed, regime) cell; `--check-regime-summary` byte-identical; ruff clean.
- WP2: **MET** — replication verdict explicit + honest (`DOES_NOT_REPLICATE`); `--check-cross-fixture-summary` byte-identical; ruff clean.
- WP3: `tests/test_bab_p39_decision_consistency.py` green; replay registrations byte-identical; P39 block wired into `bab_gate.sh`; `doc_replay_summary.json` regenerated; `ruff check .` clean.

## P39 file manifest

- **DONE (WP1, do NOT create again):** `scripts/bab_p39_regime_conditional.py`, `research_state/bab_p39/regime_summary.{json,md}`, `tests/test_bab_p39_regime_conditional.py`.
- **DONE (WP2, do NOT create again):** `scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.{json,md}`, `tests/test_bab_p39_cross_fixture.py`.
- **Create (WP3, BLOCKING):** `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py`; ensure `scripts/bab_replay_decisions.py` p39 registration is satisfied by the generator; ensure `scripts/bab_replay_full.py` regime_summary + cross_fixture_summary registrations remain; edit `scripts/bab_gate.sh` (P39 block); regenerate `research_state/bab_p32/doc_replay_summary.json`.
- **Create (WP0):** `tests/test_bab_p38_determinism.py`.
- Do not create parallel docs.

---

# COMPLETED CAMPAIGNS (frozen — do NOT re-do)

- **P20–P33 — COMPLETE and frozen** (betting-against-beta core, cost/impact/capacity, short haircut, regime split, charters, provenance replay layer, decision docs).
- **CAMPAIGN P34 — COMPLETE** ("Wide-Universe Robustness & Strategy-Honesty Closure"): multi-seed robustness (8 seeds × 6 config cells) with neutrality invariants + honesty battery + doc pointer-rot guard. Frozen.
- **CAMPAIGN P35 — COMPLETE** ("Beta-Estimation Robustness & Signal-Stability Closure"). Frozen.
- **CAMPAIGN P36 — COMPLETE** ("Walk-Forward / OOS Validation + Rank-Weighted Construction Closure"). Frozen.
- **CAMPAIGN P37 — COMPLETE** ("Cost-Aware Turnover & Capacity Closure"); verdict RETAIN the shipped default. Frozen.
- **CAMPAIGN P38 — COMPLETE** ("Deflated Significance & Tail-Risk Closure"): WP1 `SURVIVES_DEFLATION` over `n_trials_total=552` (trials-adjusted p marginal: 0.079 / 0.056, reported honestly); WP2 tail-risk/CVaR `ALL_NEUTRALITY_OK` (bounded left tail, gross + costed, 8/8 seeds); WP3 `docs/BAB_P38_DECISION.md` + replay/gate wire. Frozen. Only WP0 remains (now P39 WP0).
- **P39 WP1 — COMPLETE** ("Regime-Conditional Deflated Significance & Tail Risk"): honest negative `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`. Frozen; do NOT re-do.
- **P39 WP2 — COMPLETE** ("Cross-Fixture Replication"): honest negative `DOES_NOT_REPLICATE`. Frozen; do NOT re-do.
- **P28 WP2–WP4 — MAINTAINER-GATED (not agent-executable):**
  - P28 WP2 — CI Gate Enforcement: needs `workflows:write` (repo token lacks it; agents cannot push `.github/workflows/main.yml`).
  - P28 WP3 — Real-Market Data Ingestion: needs a maintainer-supplied licensed CSV (Coinbase public API returns 403).
  - P28 WP4 — Live-Market Deployment Decision: needs WP2+WP3 + maintainer authorization.
  - Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. Route these to the maintainer.

### Bottlenecks removed (this and prior sessions)

0. **Stale handoff / phantom "uncommitted WP1/WP2 work" — REMOVED (this refresh).** The prior handoff claimed HEAD `23ca0a8` and that P39 WP1/WP2 were not committed. Both were false: P39 WP1 and WP2 ARE committed (HEAD `2b6d438` = P38 `726d4bd` + committed P39-WP1 + WP2 files + HANDOFF-only checkpoints on top). The stale pointer would have sent the next session to re-do WP1/WP2 or chase nothing — a wasted session. HEAD is now correct and WP1/WP2 are marked DONE; the binding row is WP3. Baseline re-verified firsthand this session (all GREEN above).
1. **P38 WP2 + WP3 landed AND committed — resolved.** P38 is committed at `726d4bd`. P38 is COMPLETE; the binding row is P39.
2. **P39 WP2 (cross-fixture) completed this session — resolved.** `scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.{json,md}`, `tests/test_bab_p39_cross_fixture.py` all tracked in HEAD; `--check-cross-fixture-summary` byte-identical; verdict `DOES_NOT_REPLICATE`. Binding row advances to WP3.
3. **Full-suite frozen-artifact trap — DOCUMENTED + restore path given.** Running the full pytest suite / `bab_gate.sh` appends a trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md`. Restore with `git checkout -- research_state/bab_p27/` after any full run.
4. **Slow full gate mis-classified as a WP-blocker — RESTRUCTURED.** The full `bab_gate.sh` exceeds the 10-minute command budget. It is explicitly **P39 WP0** (large-time-budget close-out) and does NOT block WP3 — the inner loop keeps P39 moving.
5. **RED ruff / provenance gates left by prior sessions — REMOVED.** `ruff check .` clean; determinism fix (signed-zero + 12-decimal rounding + round-before-hash) landed and GREEN.
6. **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

# FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P39 WP3 is active and heavy, so a handoff refresh that *substitutes for* landed WP3 progress is a failed session). Persisting this handoff via the normal session checkpoint is expected and is not what this rule forbids — what it forbids is calling a refresh "done" instead of doing P39 WP3.
- Editing any `research_state/bab_p20/**` … `research_state/bab_p39/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, `docs/BAB_P20..P38_DECISION.md`, or any P20–P38 script/generator (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement, or the documented `doc_replay_summary.json` / `docs/BAB_*_DECISION.md` cascade when a new campaign registers a decision doc.
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P39-WP2 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen). **Never commit the trailing-newline mutation of `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` — restore after any full run.**
- Hand-typing any number into a P20–P39 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe / tail number without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P39 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate way to handle any new drift is the documented determinism pattern (round-before-hash / signed-zero normalization via the generator), never a hand-forged hash.
- **Re-doing P20–P38 or P39 WP1/WP2** (all COMPLETE and frozen), including re-doing WP1 (verify with `--check-regime-summary`) or WP2 (verify with `--check-cross-fixture-summary`), do not redo.
- **Reversing the honest WP1/WP2 negatives to force a positive result.** The negatives are findings; report them, do not game them.
- Creating parallel handoff docs (this file is the single source of truth).

---

# BOTTLENECK REMOVALS — BLOCKED OR INEFFICIENT SESSIONS ARE UNBLOCKED

1. **Stale handoff / phantom uncommitted WP1/WP2 — REMOVED.** HEAD corrected to `2b6d438`; WP1 and WP2 are committed and marked DONE. Next session pointed at WP3, not at committing nothing or re-doing WP1/WP2.
2. **Slow full gate mis-classified as a WP-blocker — REMOVED.** Full gate is P39 WP0 only; does not block WP3. Use the cheap inner loop while iterating.
3. **Full-suite frozen-artifact trap — DOCUMENTED + restore path.** Restore P27 `.md` files after any full run.
4. **RED ruff / provenance gates — REMOVED.** `ruff check .` clean; determinism fix GREEN.
5. **Idle-wait dead-end — REMOVED.** Idle-wait only permitted with fresh full-gate GREEN log + WP2+WP3 complete + P28 maintainer-gated.

---

# INESCAPABLE FOCUS CAMPAIGN — P39 WP3 HEAVY WORK CANNOT BE AVOIDED

The repo `Crypto-Betting-Against-Beta` implements a *factor* strategy. P38 answered the pooled questions; P39 WP1 answered within-regime stability (honest negative); P39 WP2 answered cross-fixture replication (honest negative `DOES_NOT_REPLICATE`). Both replication axes are closed honestly. **P39 WP3 (decision doc + documentation-integrity closure + gate wire) is the sole agent-executable binding row and it has NOT been started** — no `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py` exist yet.

**P39 WP3 is the blocking first task and is inescapable.** A session that ends without new P39 WP3 artifacts is a FAILED session, even if every other check is GREEN. The only acceptable exit conditions for a P39 session are:
- P39 WP3 delivered (`generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py`, P39 block wired into `bab_gate.sh`, `doc_replay_summary.json` regenerated, `ruff check .` clean), OR
- a genuine RED baseline regression found during FIRST ACTION that is bisected and fixed (code change, not artifact hand-edit).

A handoff refresh, docs-only edit, gate-only re-run, count-only log, or planning note does **not** satisfy P39 WP3 and is treated as no progress. Future agents must produce the P39 WP3 artifacts before any session can be considered complete.

---

# FUTURE AGENTS: READ THIS ONCE

P20–P38 are COMPLETE and frozen; **P38 is COMMITTED at `726d4bd` (code frozen there); P39 WP1 is COMPLETE and COMMITTED; P39 WP2 is COMPLETE and COMMITTED (HEAD `2b6d438`) — there is NO uncommitted work to commit or continue from.** **P39 WP1 is DONE — do NOT re-do it; verify with `--check-regime-summary` only.** **P39 WP2 is DONE — do NOT re-do it; verify with `--check-cross-fixture-summary` only.** Both verdicts are honest negatives; do not reverse them. **The binding row is P39 WP3 (decision doc + gate wire) and it has NOT been started.** **Your first job is P39 WP3** → WP0 (the slow full `bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`, plus a cross-version determinism test). P39 WP0 is a large-time-budget close-out that does NOT block WP3. Before starting, verify the baseline with the FIRST ACTION commands (all GREEN); if any is RED, bisect — do NOT hand-edit artifacts. **Never run a generator with bare/no args — it overwrites the committed artifact.** **After any full pytest/`bab_gate` run, run `git checkout -- research_state/bab_p27/` to undo the trailing-newline mutation of the two frozen P27 `.md` files.** Do not re-open frozen P20–P39-WP2 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. **A handoff-only / docs-only / verification-only commit while P39 WP3 is open is a FAILED session — the only acceptable progress is new P39 WP3 code + tests + byte-identical registrations.** If P39 WP3 is complete AND the full gate (`bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`) is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log.
