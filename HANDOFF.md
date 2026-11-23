# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T12:56:09Z (handoff refreshed; baseline re-verified firsthand at this timestamp)
- **Re-verification Timestamp (UTC):** 2026-11-23T12:56:09Z — ALL BASELINE CHECKS GREEN (ruff, bab_quick.sh, P38 --check-deflated-summary, P38 --check-tail-risk-summary, P39 --check-regime-summary, bab_replay_full --self-test, bab_replay_decisions --self-test, pytest test_bab_p39_regime_conditional.py). Working tree CLEAN. HEAD `23ca0a8`. **Binding row confirmed: P39 WP2 (Cross-fixture replication) — NOT STARTED.**
- **HEAD:** `23ca0a8` (last commit; `2026-11-23T10:34:03Z`). **P38 is fully COMMITTED at `726d4bd` (code frozen there). P39 WP1 is now DONE AND COMMITTED — the WP1 artifacts (`scripts/bab_p39_regime_conditional.py`, `research_state/bab_p39/regime_summary.{json,md}`, `tests/test_bab_p39_regime_conditional.py`) are tracked in HEAD; they landed in the checkpoint commits `2e5a336..23ca0a8` (`git diff --stat 726d4bd HEAD` = those P39-WP1 files + HANDOFF.md only — no other code drift).** Working tree is CLEAN. There is **no uncommitted work to commit** — the old claim of "uncommitted P38/P39-WP1 work" is stale and REMOVED.
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **P38 is COMPLETE and committed (WP1–WP3).** **P39 WP1 (regime-conditional) is COMPLETE and committed; its honest verdict is `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME` (see below). The binding row is now P39 WP2 "Cross-Fixture Replication" → then WP3 (decision doc + gate wire) → then WP0 close-out. P39 WP2 has NOT been started** — no `scripts/bab_p39_cross_fixture.py`, `tests/test_bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.{json,md}`, or `cross_fixture_summary` registration exist yet.
  - **P39 WP0 (full-gate + determinism close-out) — NOT DONE:** `tests/test_bab_p38_determinism.py` does not exist; the full `bash scripts/bab_gate.sh` (with `BAB_GATE_MIN_COVERAGE=100`) has NOT been run to completion. This is a large-time-budget hygiene task that does **NOT** block WP2/WP3.
  - **P39 WP1 (regime-conditional deflated significance + tail risk) — DONE & committed.** `scripts/bab_p39_regime_conditional.py` + `research_state/bab_p39/regime_summary.{json,md}` + `tests/test_bab_p39_regime_conditional.py`; `--check-regime-summary` byte-identical; 91 P39 tests pass; `ruff check .` clean. **Honest verdict = `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`:** per-regime DSR across the 8 seeds — bull_low_vol mean 0.839, bull_mid_vol 0.606, bull_high_vol 0.412, bear_low_vol 0.613, bear_mid_vol/bear_high_vol thin (0 OK cells). Neutrality invariants hold at every populated cell. This is a reported negative result, not a defect — do NOT "fix" it by re-running with different labels.
  - **P39 WP2 (cross-fixture replication) — NOT STARTED (BLOCKING FIRST TASK).**
  - **P39 WP3 (decision doc + documentation-integrity closure + gate wire) — NOT STARTED.** `regime_summary` is **not yet registered** in `bab_replay_full.py`; no `p39_decision.md` in `bab_replay_decisions.py`; no P39 block in `bab_gate.sh`; no `docs/BAB_P39_DECISION.md`; no `generate_p39_decision.py`.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T12:56:09Z)

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable): land P39 WP2 (cross-fixture replication)** — create `scripts/bab_p39_cross_fixture.py` + `research_state/bab_p39/cross_fixture_summary.{json,md}` + `tests/test_bab_p39_cross_fixture.py`, with `--check-cross-fixture-summary` GREEN (byte-identical) and `ruff check .` clean. **P39 WP1 is DONE and committed — do NOT re-do it. A handoff-only / docs-only / verification-only / re-verification-only commit that substitutes for WP2 work is a FAILED session while WP2–WP3 are open.** If you catch yourself producing only a handoff refresh, a green re-run log, or a planning note without new `bab_p39_cross_fixture.*` code + tests + a byte-identical `--check-cross-fixture-summary`, STOP — that is a failed session, not progress.

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. **P20–P38 are COMPLETE and frozen — do NOT re-open them. P39 WP1 is COMPLETE — do NOT re-open it. Your binding heavy work is P39 WP2 (cross-fixture replication) → WP3 (decision doc + gate wire) → WP0 (close-out).**

**Prioritization by repo name:** the repo implements a *factor* strategy. P38 answered the two *pooled* questions (deflated significance, unconditional tail). P39 WP1 answered the *within-regime stability* question — and the honest answer was **partly negative** (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; high-vol regimes fail). The single decisive remaining scientific question is **cross-fixture replication**: does the *pooled* P38 verdict (`SURVIVES_DEFLATION` + `ALL_NEUTRALITY_OK`) reproduce on a *second, independently parameterized* synthetic universe — i.e. is it a property of the factor or an artifact of the one committed fixture? P20–P39-WP1 answered neither. Therefore the binding heavy campaign is **P39 WP2 → WP3 → WP0**, in that order. Start WP2 immediately; do not drift into re-verification of frozen campaigns or re-doing WP1.

## VERIFIED BASELINE — firsthand this session (working tree = CLEAN, HEAD `23ca0a8`, code frozen at P38 `726d4bd` + committed P39 WP1; numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED; re-verified 2026-11-23T12:48Z)

**Re-verified firsthand at 2026-11-23T12:56Z (HEAD `23ca0a8`):**
- **GREEN (confirmed):**
  - `python3 -m ruff check .` → `All checks passed!` (exit 0).
  - `bash scripts/bab_quick.sh` → `quick preflight OK` (299 passed: 104 targeted trio + 195 smoke).
  - `python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p39_regime_conditional.py --check-regime-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary`, `--check-capacity-summary`, `--check-turnover-summary`, `bab_p36_rank_weighted.py --check-rank-weighted-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": true, "drift_detected": true, "pass": true}`.
  - `python3 scripts/bab_replay_decisions.py --self-test` → `pass:true`.
  - `python3 -m pytest -q tests/test_bab_p39_regime_conditional.py` → **91 passed**.
  - `python3 -m pytest -q tests/test_bab_p38_tail_risk.py tests/test_bab_p38_decision_consistency.py` → 50 passed.
- **NOT completed (slow — do NOT treat as a blocker for P39 WP2/WP3):** the full `bash scripts/bab_gate.sh` (runs the ~5,800-test suite + coverage + `--xproc` cross-process ledger + `--check-provenance`). A direct full-suite coverage run **exceeded the 10-minute command budget and was terminated**; this is the **P39 WP0** close-out — run it on a session with a multi-hour budget. It does NOT block P39 WP2/WP3 — use the cheap inner loop below while iterating. (Last confirmed `TOTAL 100%` coverage is 2026-11-18 @`33b84e2`; P39 WP1 added scripts/tests only — no `strategies/` changes — so package coverage is unaffected.)

## FIRST ACTION (verify baseline, then start P39 WP2)

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN (299 passed)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary # expect PASS (byte-identical)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary           # expect PASS (byte-identical)
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary     # expect PASS (byte-identical) — WP1 DONE, do NOT re-do
python3 scripts/bab_replay_full.py --self-test                           # expect pass:true
python3 scripts/bab_replay_decisions.py --self-test                      # expect pass:true
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 -m pytest -q tests/test_bab_p39_regime_conditional.py
```
If any of the above is RED, a regression was introduced — bisect with `git log`/`git diff`; do NOT hand-edit artifacts to force green.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, run the generator (writes the active campaign path only), then `git diff` to confirm the change is intentional, and restore any accidental mutation of a frozen artifact with `git checkout -- research_state/` immediately.

> **FROZEN-ARTIFACT TRAP (hit during the P38 close-out; still true):** running the FULL pytest suite (or `bash scripts/bab_gate.sh`) **appends one trailing newline** to the frozen `research_state/bab_p27/risk_controls.md` and `research_state/bab_p27/reconciliation_e2e.md` — the `run_risk_controls()` / `run_reconciliation_e2e()` P27 tests write to the committed path and the current renderer emits one newline more than was committed. After ANY full run, restore them with `git checkout -- research_state/bab_p27/` so the working tree is clean and you never accidentally commit a frozen-artifact change. (JSON artifacts are unaffected — only the two `.md` files.)

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
python3 scripts/bab_p39_cross_fixture.py --check-cross-fixture-summary        # P39 WP2 (BLOCKING)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary     # P38 WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary                # P38 WP2 (DONE)
python3 scripts/bab_replay_decisions.py --subset p39_decision.md             # P39 WP3
python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary,regime_summary,cross_fixture_summary
```

---

# BINDING ROW = Campaign P39 — "Regime-Conditional & Cross-Fixture Robustness Closure" (+ P28 WP2–WP4 MAINTAINER-GATED)

**Declared:** 2026-11-23T12:56:09Z (binding row re-declared at handoff refresh; originally drafted 2026-11-23T08:37:20Z) · **Campaign:** P39 "Regime-Conditional & Cross-Fixture Robustness Closure" · **Priority: HIGH** · **Status: ACTIVE — WP1 DONE; WP2 is the sole next agent-executable binding row.** P20–P38 COMPLETE and frozen; do NOT re-do them.

**Why P39 (prioritized by repo name):** P38 answered the two *pooled* factor questions (deflated significance + unconditional tail). P39 WP1 answered the *within-regime stability* question and returned an **honest negative** (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; high-vol regimes fail). The decisive remaining question is *cross-fixture replication*: does the pooled P38 verdict replicate on a second, independently parameterized synthetic universe — i.e. is the pooled result a property of the factor or an artifact of the single committed fixture? P39 WP2 closes that, then WP3 binds it into a decision doc + gate.

## P39 WP0 — Full-gate + determinism close-out (HYGIENE; run on a large-time-budget session; does NOT block WP2/WP3)
- Run `BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` to completion; record the TOTAL coverage % and pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`. **After the run, `git checkout -- research_state/bab_p27/`** to undo the trailing-newline mutation of the two frozen P27 `.md` files.
- Add `tests/test_bab_p38_determinism.py`: a cross-version determinism regression proving (i) `_round_floats` byte-identity (signed-zero `-0.0`→`0.0`, 12-sig-fig rounding) and (ii) `reconciliation._checksum` round-before-hash is stable — i.e. re-running the pure `build_*()` twice and asserting byte-identity, and asserting a deliberately un-round-tripped float would diverge (the drift the guard prevents). This is the only outstanding P38 WP0 item.
- WP0 does NOT block WP2/WP3.

## P39 WP1 — Regime-conditional deflated significance + tail risk — **DONE & COMMITTED (do NOT re-do)**
- `scripts/bab_p39_regime_conditional.py` + `research_state/bab_p39/regime_summary.{json,md}` + `tests/test_bab_p39_regime_conditional.py`; `--check-regime-summary` byte-identical; 91 tests pass; ruff clean.
- **Verdict `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`** (honest negative): high-vol regimes (bull_high_vol DSR mean 0.412, bear_mid/high_vol thin) fail to survive deflation over `n_trials_total=552` (read-only from P38 WP1); neutrality holds at every populated cell; regimes are causal/lagged (no lookahead). Synthetic-provenance caveat required.

## P39 WP2 — Cross-fixture replication (second independent synthetic universe) — **BLOCKING FIRST TASK**
- New `scripts/bab_p39_cross_fixture.py` (deterministic, seeded; `--check-cross-fixture-summary`; mirror `bab_p39_regime_conditional.py` + `bab_p38_deflated_significance.py` structure — `--output`/`--check-*` conventions, provenance block, `_round_floats`). **Do NOT run it bare** — it writes `research_state/bab_p39/cross_fixture_summary.*` by default; verify only with `--check-cross-fixture-summary`.
- Build a **second, independently parameterized** synthetic universe — different beta grid, different idiosyncratic vol, different seed base — clearly labelled synthetic (NOT real market data). Recompute **deflated significance (DSR/PSR)** and **tail risk (CVaR@95/@99 / expected shortfall / skew / drawdown)** and test whether the **P38 pooled verdicts replicate** (`SURVIVES_DEFLATION` + `ALL_NEUTRALITY_OK`) on the new fixture. Deflate over the same `n_trials_total=552` (read-only).
- Publish `research_state/bab_p39/cross_fixture_summary.json` (+ `.md`). Every number traces to a committed JSON leaf; synthetic-provenance caveat required. **Report the replication verdict honestly — it may be `REPLICATES` or `DOES_NOT_REPLICATE`; do NOT force a positive result.** Note the WP1 negative within-regime result is a separate axis; WP2 tests the pooled P38 result, not the per-regime one.
- Wire-in targets (do in WP3): register `cross_fixture_summary` in `bab_replay_full.py` as `json_only, no_xproc`.

## P39 WP3 — Decision doc + documentation-integrity closure + gate wire
- `generate_p39_decision.py` + `docs/BAB_P39_DECISION.md` + `tests/test_bab_p39_decision_consistency.py` (zero hand-typed numbers; independent JSON re-render byte-identity; numeric-leaf check; explicit verdicts incl. "marginal"/"not market evidence"/"no real alpha"; AST no-harness scan; ruff clean). Reuse `generate_p38_decision.py` + `tests/test_bab_p38_decision_consistency.py` as the template. The decision doc MUST surface **both** the WP1 within-regime negative (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`) **and** the WP2 cross-fixture replication verdict.
- Register `p39_decision.md` in `scripts/bab_replay_decisions.py` (mirror the `p38_decision.md` entry; `REPORT_PATH = docs/BAB_P39_DECISION.md`), then **regenerate** `research_state/bab_p32/doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`.
- Register `regime_summary` + `cross_fixture_summary` in `scripts/bab_replay_full.py` as `json_only, no_xproc` (this is currently MISSING for WP1's `regime_summary`).
- Wire a P39 block into `scripts/bab_gate.sh` (mirror the P38 block at lines ~216–225: `--check-regime-summary`, `--check-cross-fixture-summary`, P39 tests).
- The pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py` must include `"P39"` — add it if a new doc-pointer test fails; keep it green.
- Keep README / `docs/COVERAGE_NOTES.md` naming P39 as binding.

## P39 chartered acceptance thresholds
- WP0: full `bab_gate.sh` GREEN with `BAB_GATE_MIN_COVERAGE=100`; `tests/test_bab_p38_determinism.py` green; frozen P27 `.md` restored (`git status` clean except intended changes).
- WP1: **MET** — per-regime DSR + PSR + CVaR/ES + neutrality invariants at every (seed, regime) cell; `--check-regime-summary` byte-identical; ruff clean.
- WP2: replication verdict explicit + honest; `--check-cross-fixture-summary` byte-identical; ruff clean.
- WP3: `tests/test_bab_p39_decision_consistency.py` green; replay registrations byte-identical; P39 block wired into `bab_gate.sh`; `doc_replay_summary.json` regenerated; `ruff check .` clean.

## P39 file manifest
- **Create (WP2, BLOCKING):** `scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.json` (+ `.md`), `tests/test_bab_p39_cross_fixture.py`.
- **Create (WP3):** `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py`; edit `scripts/bab_replay_full.py` (register `regime_summary` + `cross_fixture_summary`), `scripts/bab_replay_decisions.py` (register `p39_decision.md`), `scripts/bab_gate.sh` (P39 block); regenerate `research_state/bab_p32/doc_replay_summary.json`.
- **Create (WP0):** `tests/test_bab_p38_determinism.py`.
- **DONE (WP1, do NOT create again):** `scripts/bab_p39_regime_conditional.py`, `research_state/bab_p39/regime_summary.{json,md}`, `tests/test_bab_p39_regime_conditional.py`.
- Do not create parallel docs.

---

## COMPLETED CAMPAIGNS (frozen — do NOT re-do)
- **P20–P33 — COMPLETE and frozen** (betting-against-beta core, cost/impact/capacity, short haircut, regime split, charters, provenance replay layer, decision docs).
- **CAMPAIGN P34 — COMPLETE** ("Wide-Universe Robustness & Strategy-Honesty Closure"): multi-seed robustness (8 seeds × 6 config cells) with neutrality invariants + honesty battery + doc pointer-rot guard. Frozen.
- **CAMPAIGN P35 — COMPLETE** ("Beta-Estimation Robustness & Signal-Stability Closure"). Frozen.
- **CAMPAIGN P36 — COMPLETE** ("Walk-Forward / OOS Validation + Rank-Weighted Construction Closure"). Frozen.
- **CAMPAIGN P37 — COMPLETE** ("Cost-Aware Turnover & Capacity Closure"); verdict RETAIN the shipped default. Frozen.
- **CAMPAIGN P38 — COMPLETE** ("Deflated Significance & Tail-Risk Closure"): WP1 `SURVIVES_DEFLATION` over `n_trials_total=552` (trials-adjusted p marginal: 0.079 / 0.056, reported honestly); WP2 tail-risk/CVaR `ALL_NEUTRALITY_OK` (bounded left tail, gross + costed, 8/8 seeds); WP3 `docs/BAB_P38_DECISION.md` + replay/gate wire. **Only the WP0 full-gate run remains (now P39 WP0).** Frozen.
- **P39 WP1 — COMPLETE** ("Regime-Conditional Deflated Significance & Tail Risk"): honest negative `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`. Frozen; do NOT re-do.
- **P28 WP2–WP4 — MAINTAINER-GATED (not agent-executable):**
  - P28 WP2 — CI Gate Enforcement: needs `workflows:write` (repo token lacks it; agents cannot push `.github/workflows/main.yml`).
  - P28 WP3 — Real-Market Data Ingestion: needs a maintainer-supplied licensed CSV (Coinbase public API returns 403).
  - P28 WP4 — Live-Market Deployment Decision: needs WP2+WP3 + maintainer authorization.
  - Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. Route these to the maintainer.

### Bottlenecks removed (this and prior sessions)
0. **Stale handoff / phantom "uncommitted WP1 work" — REMOVED (this refresh).** The prior handoff claimed HEAD `25cc8bf` and that P39 WP1 artifacts were "written but NOT yet committed." Both were false: P39 WP1 IS committed (checkpoint commits `2e5a336..23ca0a8`; `git diff --stat 726d4bd HEAD` = the P39-WP1 files + HANDOFF.md only), and HEAD is `23ca0a8`. The stale pointer would have sent the next session to "commit" nothing or re-do WP1 — a wasted session. HEAD is now correct and WP1 is marked DONE; the binding row is WP2. Baseline re-verified firsthand this session (all GREEN above).
1. **P38 WP2 + WP3 landed AND committed — resolved.** P38 is committed at `726d4bd` (WP2 tail-risk `--check` byte-identical, `ALL_NEUTRALITY_OK`; full WP3 decision doc + replay registrations + gate wire + regenerated `doc_replay_summary.json`). P38 is COMPLETE; the binding row is P39.
2. **Full-suite frozen-artifact trap — DOCUMENTED + restore path given.** Running the full pytest suite / `bab_gate.sh` appends a trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (the `run_*()` P27 tests write the committed path; renderer emits one more newline than committed). Restore with `git checkout -- research_state/bab_p27/` after any full run (see guardrail above) so the tree never carries a frozen-artifact change.
3. **Slow full gate mis-classified as a WP-blocker — RESTRUCTURED.** The full `bab_gate.sh` exceeds the 10-minute command budget (a direct full coverage run was terminated). It is explicitly **P39 WP0** (large-time-budget close-out) and does NOT block WP2/WP3 — the handoff's inner loop keeps P39 moving.
4. **RED ruff / provenance gates left by prior sessions — REMOVED.** `ruff check .` clean; determinism fix (signed-zero + 12-decimal rounding + round-before-hash) landed and GREEN.
5. **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P39 WP2–WP3 are active and heavy, so a handoff refresh that *substitutes for* landed WP2/WP3 progress is a failed session). Persisting this handoff via the normal session checkpoint is expected and is not what this rule forbids — what it forbids is calling a refresh "done" instead of doing P39 WP2.
- Editing any `research_state/bab_p20/**` … `research_state/bab_p38/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, `docs/BAB_P20..P38_DECISION.md`, or any P20–P38 script/generator (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement, or the documented `doc_replay_summary.json` / `docs/BAB_*_DECISION.md` cascade when a new campaign registers a decision doc.
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P39-WP1 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen). **Never commit the trailing-newline mutation of `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` — restore after any full run.**
- Hand-typing any number into a P20–P39 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe / tail number without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P39 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate way to handle any new drift is the documented determinism pattern (round-before-hash / signed-zero normalization via the generator), never a hand-forged hash.
- **Re-doing P20–P38 or P39 WP1** (all COMPLETE and frozen), including re-doing WP1 (verify with `--check-regime-summary`, do not redo).
- **Reversing the honest WP1 negative to force a positive result** (e.g. re-running with non-causal/overlapping labels to "rescue" high-vol regimes). The negative is a finding; report it, do not game it.
- Creating parallel handoff docs (this file is the single source of truth).

---

## BOTTLENECK REMOVALS — BLOCKED OR INEFFICIENT SESSIONS ARE UNBLOCKED

1. **Stale handoff / phantom uncommitted WP1 — REMOVED.** The prior handoff's HEAD (`25cc8bf`) and "WP1 uncommitted" claims were both false; P39 WP1 is committed and HEAD is `23ca0a8`. The next session is pointed at WP2, not at committing nothing or re-doing WP1. Bottleneck removed: no phantom work to chase, no wasted re-verification of WP1.

2. **Slow full gate mis-classified as a WP-blocker — REMOVED.** The full `bash scripts/bab_gate.sh` (~5,800 tests + coverage + `--xproc` cross-process ledger + `--check-provenance`) exceeds the 10-minute command budget and was terminated on a direct full coverage run. It is now explicitly **P39 WP0** (large-time-budget close-out) and does **NOT** block P39 WP2/WP3. Use the cheap inner loop (`bab_quick.sh` + `ruff` + `test_bab_p39_*.py` + `--check-cross-fixture-summary`) while iterating; run the full gate only on a multi-hour budget session. Bottleneck removed: WP2/WP3 progress is never gated on the slow gate.

3. **Full-suite frozen-artifact trap — DOCUMENTED + restore path.** Running the full pytest suite / `bab_gate.sh` appends one trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (the `run_*()` P27 tests write the committed path; renderer emits one more newline than committed). Restore with `git checkout -- research_state/bab_p27/` after any full run so the tree never carries a frozen-artifact change. Bottleneck removed: full runs no longer silently poison the tree.

4. **RED ruff / provenance gates left by prior sessions — REMOVED.** `ruff check .` clean; determinism fix (signed-zero + 12-decimal rounding + round-before-hash) landed and GREEN. Bottleneck removed: no RED gate to bisect before starting P39 WP2.

5. **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose. Bottleneck removed: no session may idle out on P39 work.

---

## INESCAPABLE FOCUS CAMPAIGN — P39 WP2 HEAVY WORK CANNOT BE AVOIDED

The repo `Crypto-Betting-Against-Beta` implements a *factor* strategy. P38 answered the two *pooled* questions (deflated significance `SURVIVES_DEFLATION`; tail risk `ALL_NEUTRALITY_OK`). P39 WP1 answered the *within-regime* question and returned an **honest negative** (`DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; high-vol regimes fail). The decisive remaining scientific question is **cross-fixture replication**: do the *pooled* P38 conclusions reproduce on a second, independently parameterized synthetic universe, or were they an artifact of the single committed fixture? P20–P39-WP1 answered neither. **P39 WP2 is the sole agent-executable binding row and it has NOT been started** — no `bab_p39_cross_fixture.*` scripts, tests, or state exist yet.

**P39 WP2 (cross-fixture replication) is the blocking first task and is inescapable.** A session that ends without new `bab_p39_cross_fixture.*` code + tests + a byte-identical `--check-cross-fixture-summary` is a FAILED session, even if every other check is GREEN. The only acceptable exit conditions for a P39 session are:
- P39 WP2 delivered (`scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.{json,md}`, `tests/test_bab_p39_cross_fixture.py`, `--check-cross-fixture-summary` byte-identical, `ruff check .` clean), OR
- a genuine RED baseline regression found during FIRST ACTION that is bisected and fixed (code change, not artifact hand-edit).

A handoff refresh, docs-only edit, gate-only re-run, count-only log, or planning note does **not** satisfy P39 WP2 and is treated as no progress. Future agents must produce the `bab_p39_cross_fixture.*` artifacts before any session can be considered complete.

---

## FUTURE AGENTS: READ THIS ONCE
P20–P38 are COMPLETE and frozen; **P38 is COMMITTED at `726d4bd` (code frozen there); P39 WP1 is COMPLETE and COMMITTED (HEAD `23ca0a8` = P38 `726d4bd` + committed P39-WP1 files + HANDOFF-only checkpoints on top) — there is NO uncommitted work to commit or continue from.** **P39 WP1 is DONE — do NOT re-do it; verify it with `--check-regime-summary` only.** Its honest verdict is `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; do not reverse it. **The binding row is P39 WP2 (cross-fixture replication) and it has NOT been started — no `bab_p39_cross_fixture.*` files exist yet.** **Your first job is P39 WP2 (cross-fixture replication)** → WP3 (decision doc + gate wire, including registering WP1's `regime_summary` in `bab_replay_full.py`) → WP0 (the slow full `bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`, plus a cross-version determinism test). P39 WP0 is a large-time-budget close-out that does NOT block WP2/WP3. Before starting, verify the baseline with the FIRST ACTION commands (all GREEN); if any is RED, bisect — do NOT hand-edit artifacts. **Never run a generator with bare/no args — it overwrites the committed artifact.** **After any full pytest/`bab_gate` run, run `git checkout -- research_state/bab_p27/` to undo the trailing-newline mutation of the two frozen P27 `.md` files.** Do not re-open frozen P20–P39-WP1 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. **A handoff-only / docs-only / verification-only commit while P39 WP2–WP3 are open is a FAILED session — the only acceptable progress is new `bab_p39_cross_fixture.*` code + tests + a byte-identical `--check-cross-fixture-summary`.** If P39 WP2+WP3 are complete AND the full gate (`bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`) is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log, not prose.