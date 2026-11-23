# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T10:19:57Z (handoff refreshed; baseline re-verified firsthand at this timestamp)
- **HEAD:** `4361960` (last commit). **P38 is fully COMMITTED at `726d4bd`; there is no uncommitted P38 work.** (Commits `726d4bd..4361960` are `chore(kilo): checkpoint agent session` touches to THIS file only — `git diff --stat 726d4bd 4361960` = `HANDOFF.md` only, no code. The only working-tree delta is this HANDOFF.md refresh itself — persist it via the normal session checkpoint; it is NOT work-to-do.) The P38 WP2 + WP3 close-out landed in commit `726d4bd` (`scripts/bab_p38_tail_risk.py`, `research_state/bab_p38/tail_risk_summary.{json,md}`, `docs/BAB_P38_DECISION.md`, `generate_p38_decision.py`, replay/gate wire, tests). **Start P39 WP1 directly.**
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **P38 is COMPLETE and committed (WP1–WP3).** The binding row is **Campaign P39 "Regime-Conditional & Cross-Fixture Robustness Closure"**. **P39 has NOT been started** — no `scripts/bab_p39_*`, `tests/test_bab_p39_*`, `research_state/bab_p39/`, or `docs/BAB_P39_*` exist yet.
  - **P38 WP1 (deflated significance) — DONE** (verdict `SURVIVES_DEFLATION` over `n_trials_total=552`; `--check-deflated-summary` byte-identical).
  - **P38 WP2 (tail-risk / CVaR) — DONE & committed.** `scripts/bab_p38_tail_risk.py` + `research_state/bab_p38/tail_risk_summary.{json,md}` + `tests/test_bab_p38_tail_risk.py`; `--check-tail-risk-summary` byte-identical; `tail_risk_status = ALL_NEUTRALITY_OK` (8/8 seeds, gross + costed).
  - **P38 WP3 (decision doc + gate wire) — DONE & committed.** `generate_p38_decision.py` + `docs/BAB_P38_DECISION.md` + `tests/test_bab_p38_decision_consistency.py`; registered `p38_decision.md` in `bab_replay_decisions.py`, `deflated_summary`+`tail_risk_summary` in `bab_replay_full.py` (json_only, no_xproc), P38 block wired into `bab_gate.sh`; `doc_replay_summary.json` regenerated (p38 replay_ok True).
  - **P38 WP0 close-out item STILL OPEN:** the full `bash scripts/bab_gate.sh` (coverage + cross-process `--xproc`/`--check-provenance`, >10 min) has NOT been run to completion — this is now **P39 WP0** (large-time-budget close-out; does NOT block WP1/WP2).

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T10:19:57Z)

**MINIMUM ACCEPTABLE OUTCOME (non-negotiable): land P39 WP1 (regime-conditional deflated significance + tail risk)** — create `scripts/bab_p39_regime_conditional.py` + `research_state/bab_p39/regime_summary.{json,md}` + `tests/test_bab_p39_regime_conditional.py`, with `--check-regime-summary` GREEN and `ruff check .` clean. **There is no uncommitted P38 work to commit — P38 is committed at `726d4bd` (the only working-tree delta is this handoff refresh, which is not work-to-do). A handoff-only / docs-only / verification-only / re-verification-only commit that substitutes for P39 work is a FAILED session while P39 WP1–WP2 are open.** If you catch yourself producing only a handoff refresh, a green re-run log, or a planning note without new `bab_p39_*` code + tests + a byte-identical `--check-*`, STOP — that is a failed session, not progress. (P39 WP0 — the full-gate run — is a large-time-budget close-out that does NOT block WP1; use the cheap inner loop while iterating.)

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. **P20–P38 are COMPLETE and frozen — do NOT re-open them.** **Your binding heavy work is P39 WP1 (regime-conditional) → WP2 (cross-fixture replication) → WP3 (decision doc + gate wire).**

**Prioritization by repo name:** the repo implements a *factor* strategy. P38 answered the two *pooled* questions — (1) is the Sharpe distinguishable from luck after multiple-testing deflation (`SURVIVES_DEFLATION`, WP1), and (2) what does the unconditional left tail look like (`ALL_NEUTRALITY_OK`, bounded, WP2). The decisive remaining scientific question for any factor is **stability**: do those conclusions hold (a) *within* causal market regimes (bull / bear / high-vol / low-vol) rather than only pooled, and (b) on a *second, independently parameterized* synthetic universe? P20–P38 answered neither. Therefore the binding heavy campaign is **P39 WP1 → WP2 → WP3**, in that order. Start WP1 immediately; do not drift into re-verification of frozen campaigns.

## VERIFIED BASELINE — firsthand this session (working tree = CLEAN at P38 close-out, HEAD `4361960`, numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED; re-verified 2026-11-23T09:27:15Z)

**Re-verified firsthand at 2026-11-23T09:27:15Z:** `ruff check .` clean, `bab_quick.sh` = **299 passed** (104 targeted + 195 smoke), `--check-deflated-summary` PASS (byte-identical), `--check-tail-risk-summary` PASS (byte-identical), both replay `--self-test` `pass:true`, both subset replays (`deflated_summary,tail_risk_summary` / `p38_decision.md`) OK. The remaining bullets below were last confirmed at the P38 close-out (`726d4bd`) and are re-checked by the FIRST ACTION block.

- **GREEN (confirmed):**
  - `python3 -m ruff check .` → `All checks passed!` (exit 0).
  - `bash scripts/bab_quick.sh` → `quick preflight OK` (299 passed: 104 targeted trio + 195 smoke).
  - `python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary`, `--check-capacity-summary`, `--check-turnover-summary`, `bab_p36_rank_weighted.py --check-rank-weighted-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": true, "drift_detected": true, "pass": true}`.
  - `python3 scripts/bab_replay_decisions.py --self-test` → `pass:true`.
  - `python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary` → OK (byte-identical json).
  - `python3 scripts/bab_replay_decisions.py --subset p38_decision.md` → OK (byte-identical).
  - `python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → OK.
  - `python3 -m pytest -q tests/test_bab_p38_tail_risk.py tests/test_bab_p38_decision_consistency.py` → 97 passed, 1 skipped.
- **NOT completed this session (slow — do NOT treat as a blocker for P39 WP1/WP2):** the full `bash scripts/bab_gate.sh` (runs the ~5,800-test suite + coverage + `--xproc` cross-process ledger + `--check-provenance`). A direct full-suite coverage run **exceeded the 10-minute command budget and was terminated**; this is the **P39 WP0** close-out — run it on a session with a multi-hour budget. It does NOT block P39 WP1/WP2 — use the cheap inner loop below while iterating. (The last confirmed `TOTAL 100%` coverage is 2026-11-18 @`33b84e2`; P38 added scripts/tests only — no `strategies/` changes — so package coverage is unaffected.)

## FIRST ACTION (verify baseline, then start P39 WP1)

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN (299 passed)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary # expect PASS (byte-identical)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary           # expect PASS (byte-identical)
python3 scripts/bab_replay_full.py --self-test                           # expect pass:true
python3 scripts/bab_replay_decisions.py --self-test                      # expect pass:true
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json
python3 -m pytest -q tests/test_bab_p38_tail_risk.py tests/test_bab_p38_decision_consistency.py
```
If any of the above is RED, a regression was introduced — bisect with `git log`/`git diff`; do NOT hand-edit artifacts to force green.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, run the generator (writes the active campaign path only), then `git diff` to confirm the change is intentional, and restore any accidental mutation of a frozen artifact with `git checkout -- research_state/` immediately.

> **FROZEN-ARTIFACT TRAP (hit during the P38 close-out; still true):** running the FULL pytest suite (or `bash scripts/bab_gate.sh`) **appends one trailing newline** to the frozen `research_state/bab_p27/risk_controls.md` and `research_state/bab_p27/reconciliation_e2e.md` — the `run_risk_controls()` / `run_reconciliation_e2e()` P27 tests write to the committed path and the current renderer emits one newline more than was committed. After ANY full run, restore them with `git checkout -- research_state/bab_p27/` so the working tree is clean and you never accidentally commit a frozen-artifact change. (JSON artifacts are unaffected — only the two `.md` files.)

## How the P38 determinism layer works (context — do NOT redo; reuse the pattern if new drift appears)
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
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary     # P38 WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary                # P38 WP2 (DONE)
python3 scripts/bab_p39_regime_conditional.py --check-regime-summary          # P39 WP1 (BLOCKING)
python3 scripts/bab_replay_decisions.py --subset p39_decision.md             # P39 WP3
python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary,regime_summary,cross_fixture_summary
```

---

# BINDING ROW = Campaign P39 — "Regime-Conditional & Cross-Fixture Robustness Closure" (+ P28 WP2–WP4 MAINTAINER-GATED)

**Declared:** 2026-11-23T09:27:15Z (binding row re-declared at handoff refresh; originally drafted 2026-11-23T08:37:20Z) · **Campaign:** P39 "Regime-Conditional & Cross-Fixture Robustness Closure" · **Priority: HIGH** · **Status: ACTIVE — the sole agent-executable binding row.** P20–P38 COMPLETE and frozen; do NOT re-do them.

**Why P39 (prioritized by repo name):** P38 answered the two *pooled* factor questions (deflated significance + unconditional tail). The decisive remaining question is *stability*: (a) does `SURVIVES_DEFLATION` and the bounded tail hold *within* causal regimes (not only pooled — a factor can look fine in aggregate and blow up in one regime), and (b) does it *replicate* on a second, independently parameterized synthetic universe (guarding against a single-fixture artifact)? P39 closes (a) and (b), then binds them into a decision doc + gate.

## P39 WP0 — Full-gate + cross-version determinism close-out (HYGIENE; run on a large-time-budget session)
- Run `BAB_GATE_LOG=/tmp/bab_gate_p39.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` to completion; record the TOTAL coverage % and pass/skip counts with date/HEAD in `docs/COVERAGE_NOTES.md`. **After the run, `git checkout -- research_state/bab_p27/`** to undo the trailing-newline mutation of the two frozen P27 `.md` files.
- Add `tests/test_bab_p38_determinism.py`: a cross-version determinism regression proving (i) `_round_floats` byte-identity (signed-zero `-0.0`→`0.0`, 12-sig-fig rounding) and (ii) `reconciliation._checksum` round-before-hash is stable — i.e. re-running the pure `build_*()` twice and asserting byte-identity, and asserting a deliberately un-round-tripped float would diverge (the drift the guard prevents). This is the only outstanding P38 WP0 item.
- WP0 does NOT block WP1/WP2.

## P39 WP1 — Regime-conditional deflated significance + tail risk — **BLOCKING FIRST TASK**
- New `scripts/bab_p39_regime_conditional.py` (deterministic, seeded; `--check-regime-summary` mode; mirror `bab_p38_deflated_significance.py` + `bab_p38_tail_risk.py` structure, `--output`/`--check-*` conventions, provenance block, `_round_floats`).
- On the P35/P37 40-asset wide synthetic fixture across the standard 8 seeds, split each seed's return series into regimes using a **causal, lagged** label (e.g. trailing BTC trend up/down and/or trailing realized-vol terciles — computed only from data available at t-1, no lookahead). Recompute **DSR/PSR** and **CVaR@95/@99 / expected shortfall / skew / drawdown** *within each regime* (deflate over the same `n_trials_total` from P38 WP1, read-only).
- Publish `research_state/bab_p39/regime_summary.json` (+ `.md`). Every number traces to a committed JSON leaf; synthetic-provenance caveat required. The honest per-regime verdict may be negative (e.g. `DOES_NOT_SURVIVE_DEFLATION` within a thin regime) — report it honestly, do not overclaim.
- Wire-in targets (do in WP3): register `regime_summary` in `bab_replay_full.py` as `json_only, no_xproc`.

## P39 WP2 — Cross-fixture replication (second independent synthetic universe)
- New `scripts/bab_p39_cross_fixture.py` (deterministic, seeded; `--check-cross-fixture-summary`; mirror WP1). Build a **second, independently parameterized** synthetic universe — different beta grid, different idio vol, different seed base — clearly labelled synthetic (NOT real market data). Recompute the deflated significance + tail risk and test whether the **P38 verdicts replicate** (SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) on the new fixture.
- Publish `research_state/bab_p39/cross_fixture_summary.json` (+ `.md`). Report the replication verdict honestly (may be `REPLICATES` or `DOES_NOT_REPLICATE`).
- Wire-in targets (WP3): register `cross_fixture_summary` in `bab_replay_full.py` as `json_only, no_xproc`.

## P39 WP3 — Decision doc + documentation-integrity closure + gate wire
- `generate_p39_decision.py` + `docs/BAB_P39_DECISION.md` + `tests/test_bab_p39_decision_consistency.py` (zero hand-typed numbers; independent JSON re-render byte-identity; numeric-leaf check; explicit verdicts incl. "marginal"/"not market evidence"/"no real alpha"; AST no-harness scan; ruff clean). Reuse `generate_p38_decision.py` + `tests/test_bab_p38_decision_consistency.py` as the template.
- Register `p39_decision.md` in `scripts/bab_replay_decisions.py` (mirror the `p38_decision.md` entry; `REPORT_PATH = docs/BAB_P39_DECISION.md`), then **regenerate** `research_state/bab_p32/doc_replay_summary.json` via `bab_replay_decisions.py --summary-json`.
- Register `regime_summary` + `cross_fixture_summary` in `scripts/bab_replay_full.py` as `json_only, no_xproc`.
- Wire a P39 block into `scripts/bab_gate.sh` (mirror the P38 block).
- The pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py` must include `"P39"` — add it if a new doc-pointer test fails; keep it green.
- Keep README / `docs/COVERAGE_NOTES.md` naming P39 as binding.

## P39 chartered acceptance thresholds
- WP0: full `bab_gate.sh` GREEN with `BAB_GATE_MIN_COVERAGE=100`; `tests/test_bab_p38_determinism.py` green; frozen P27 `.md` restored (`git status` clean except intended changes).
- WP1: per-regime DSR + PSR + CVaR/ES + neutrality invariants at every (seed, regime) cell; `--check-regime-summary` byte-identical; ruff clean.
- WP2: replication verdict explicit + honest; `--check-cross-fixture-summary` byte-identical; ruff clean.
- WP3: `tests/test_bab_p39_decision_consistency.py` green; replay registrations byte-identical; P39 block wired into `bab_gate.sh`; `doc_replay_summary.json` regenerated; `ruff check .` clean.

## P39 file manifest
- **Create (WP1, BLOCKING):** `scripts/bab_p39_regime_conditional.py`, `research_state/bab_p39/regime_summary.json` (+ `.md`), `tests/test_bab_p39_regime_conditional.py`.
- **Create (WP2):** `scripts/bab_p39_cross_fixture.py`, `research_state/bab_p39/cross_fixture_summary.json` (+ `.md`), `tests/test_bab_p39_cross_fixture.py`.
- **Create (WP3):** `generate_p39_decision.py`, `docs/BAB_P39_DECISION.md`, `tests/test_bab_p39_decision_consistency.py`; edit `scripts/bab_replay_full.py`, `scripts/bab_replay_decisions.py`, `scripts/bab_gate.sh`; regenerate `research_state/bab_p32/doc_replay_summary.json`.
- **Create (WP0):** `tests/test_bab_p38_determinism.py`.
- Do not create parallel docs.

---

## COMPLETED CAMPAIGNS (frozen — do NOT re-do)
- **P20–P33 — COMPLETE and frozen** (betting-against-beta core, cost/impact/capacity, short haircut, regime split, charters, provenance replay layer, decision docs).
- **CAMPAIGN P34 — COMPLETE** ("Wide-Universe Robustness & Strategy-Honesty Closure"): multi-seed robustness (8 seeds × 6 config cells) with neutrality invariants + honesty battery + doc pointer-rot guard. Frozen.
- **CAMPAIGN P35 — COMPLETE** ("Beta-Estimation Robustness & Signal-Stability Closure"). Frozen.
- **CAMPAIGN P36 — COMPLETE** ("Walk-Forward / OOS Validation + Rank-Weighted Construction Closure"). Frozen.
- **CAMPAIGN P37 — COMPLETE** ("Cost-Aware Turnover & Capacity Closure"); verdict RETAIN the shipped default. Frozen.
- **CAMPAIGN P38 — COMPLETE** ("Deflated Significance & Tail-Risk Closure"): WP1 `SURVIVES_DEFLATION` over `n_trials_total=552` (trials-adjusted p marginal: 0.079 / 0.056, reported honestly); WP2 tail-risk/CVaR `ALL_NEUTRALITY_OK` (bounded left tail, gross + costed, 8/8 seeds); WP3 `docs/BAB_P38_DECISION.md` + replay/gate wire. **Only the WP0 full-gate run remains (now P39 WP0).** Frozen.
- **P28 WP2–WP4 — MAINTAINER-GATED (not agent-executable):**
  - P28 WP2 — CI Gate Enforcement: needs `workflows:write` (repo token lacks it; agents cannot push `.github/workflows/main.yml`).
  - P28 WP3 — Real-Market Data Ingestion: needs a maintainer-supplied licensed CSV (Coinbase public API returns 403).
  - P28 WP4 — Live-Market Deployment Decision: needs WP2+WP3 + maintainer authorization.
  - Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. Route these to the maintainer.

### Bottlenecks removed (this and prior sessions)
0. **P38 WP2 + WP3 landed AND committed — the blocking work that WAS the primary bottleneck is fully resolved.** The prior handoff named P38 WP2 (tail-risk) as the blocking first task and warned a handoff-only commit while WP2 was open would be a FAILED session. That work shipped and is now **committed at `726d4bd`** (WP2 tail-risk `--check` byte-identical, `ALL_NEUTRALITY_OK`; full WP3 decision doc + replay registrations + gate wire + regenerated `doc_replay_summary.json`). P38 is COMPLETE; the binding row is P39.
1. **Full-suite frozen-artifact trap — DOCUMENTED + restore path given.** Running the full pytest suite / `bab_gate.sh` appends a trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (the `run_*()` P27 tests write the committed path; renderer emits one more newline than committed). Restore with `git checkout -- research_state/bab_p27/` after any full run (see guardrail above) so the tree never carries a frozen-artifact change.
2. **Slow full gate mis-classified as a WP-blocker — RESTRUCTURED.** The full `bab_gate.sh` exceeds the 10-minute command budget (a direct full coverage run was terminated). It is now explicitly **P39 WP0** (large-time-budget close-out) and does NOT block WP1/WP2 — the handoff's inner loop keeps P39 moving.
3. **Stale HEAD pointer + phantom "uncommitted P38 work" — REMOVED (this refresh).** HEAD is now `4361960` (`726d4bd..4361960` are HANDOFF-only checkpoint commits; `git diff --stat 726d4bd 4361960` = `HANDOFF.md` only — no code drift). P38 is committed at `726d4bd`, and the only working-tree delta is this handoff refresh. The prior prior handoff pointed at `d743c9a` and falsely claimed P38 WP2+WP3 were UNCOMMITTED — that phantom is long gone. Baseline re-verified firsthand this session (all GREEN above).
4. **RED ruff gate left by WP1 (prior) — REMOVED.** Fixed at the source; `ruff check .` clean.
5. **RED provenance gate (prior) — REMOVED.** Determinism fix (signed-zero + 12-decimal rounding + round-before-hash) landed; now GREEN.
6. **Idle-wait dead-end (prior) — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP1+WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P39 WP1–WP3 are active and heavy, so a handoff refresh that *substitutes for* landed WP1/WP2/WP3 progress is a failed session). Persisting this handoff via the normal session checkpoint is expected and is not what this rule forbids — what it forbids is calling a refresh "done" instead of doing P39.
- Editing any `research_state/bab_p20/**` … `research_state/bab_p38/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, `docs/BAB_P20..P38_DECISION.md`, or any P20–P38 script/generator (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement, or the documented `doc_replay_summary.json` / `docs/BAB_*_DECISION.md` cascade when a new campaign registers a decision doc.
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P38 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen). **Never commit the trailing-newline mutation of `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` — restore after any full run.**
- Hand-typing any number into a P20–P39 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe / tail number without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P38 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate way to handle any new drift is the documented determinism pattern (round-before-hash / signed-zero normalization via the generator), never a hand-forged hash.
- **Re-doing P20–P38** (all COMPLETE and frozen), including re-doing P38 WP1/WP2/WP3 (verify with `--check-*`, do not redo).
- Creating parallel handoff docs (this file is the single source of truth).

---

## BOTTLENECK REMOVALS — BLOCKED OR INEFFICIENT SESSIONS ARE UNBLOCKED

1. **Slow full gate mis-classified as a WP-blocker — REMOVED.** The full `bash scripts/bab_gate.sh` (~5,800 tests + coverage + `--xproc` cross-process ledger + `--check-provenance`) exceeds the 10-minute command budget and was terminated on a direct full coverage run. It is now explicitly **P39 WP0** (large-time-budget close-out) and does **NOT** block P39 WP1/WP2. Use the cheap inner loop (`bab_quick.sh` + `ruff` + `test_bab_p39_*.py` + `--check-regime-summary`) while iterating; run the full gate only on a multi-hour budget session. Bottleneck removed: WP1/WP2 progress is never gated on the slow gate.

2. **Full-suite frozen-artifact trap — DOCUMENTED + restore path.** Running the full pytest suite / `bab_gate.sh` appends one trailing newline to frozen `research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (the `run_*()` P27 tests write to the committed path; renderer emits one more newline than committed). Restore with `git checkout -- research_state/bab_p27/` after any full run so the tree never carries a frozen-artifact change. Bottleneck removed: full runs no longer silently poison the tree.

3. **Stale HEAD pointer + phantom "uncommitted P38 work" — REMOVED.** HEAD is `4361960`; `726d4bd..4361960` are HANDOFF-only checkpoint commits (`git diff --stat 726d4bd 4361960` = `HANDOFF.md` only — no code drift). P38 is committed at `726d4bd`. The only working-tree delta is this handoff refresh. Bottleneck removed: no phantom uncommitted work to chase.

4. **RED ruff / provenance gates left by prior sessions — REMOVED.** `ruff check .` clean; determinism fix (signed-zero + 12-decimal rounding + round-before-hash) landed and GREEN. Bottleneck removed: no RED gate to bisect before starting P39.

5. **Idle-wait dead-end — REMOVED.** A session may report idle-wait ONLY after the full gate is GREEN **and** P39 WP1+WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose. Bottleneck removed: no session may idle out on P39 work.

---

## INESCAPABLE FOCUS CAMPAIGN — P39 HEAVY WORK CANNOT BE AVOIDED

The repo `Crypto-Betting-Against-Beta` implements a *factor* strategy. P38 answered the two *pooled* questions (deflated significance `SURVIVES_DEFLATION`; tail risk `ALL_NEUTRALITY_OK`). The decisive remaining scientific question is **stability**: (a) do those conclusions hold *within* causal market regimes (bull / bear / high-vol / low-vol) rather than only pooled, and (b) do they *replicate* on a second, independently parameterized synthetic universe? P20–P38 answered neither. **P39 is the sole agent-executable binding row and it has NOT been started** — no `bab_p39_*` scripts, tests, state, or decision doc exist yet.

**P39 WP1 (regime-conditional deflated significance + tail risk) is the blocking first task and is inescapable.** A session that ends without new `bab_p39_*` code + tests + a byte-identical `--check-regime-summary` is a FAILED session, even if every other check is GREEN. The only acceptable exit conditions for a P39 session are:
- P39 WP1 delivered (`scripts/bab_p39_regime_conditional.py`, `research_state/bab_p39/regime_summary.{json,md}`, `tests/test_bab_p39_regime_conditional.py`, `--check-regime-summary` byte-identical, `ruff check .` clean), OR
- a genuine RED baseline regression found during FIRST ACTION that is bisected and fixed (code change, not artifact hand-edit).

A handoff refresh, docs-only edit, gate-only re-run, count-only log, or planning note does **not** satisfy P39 WP1 and is treated as no progress. Future agents must produce the `bab_p39_*` artifacts before any session can be considered complete.

---


---

## FUTURE AGENTS: READ THIS ONCE
P20–P38 are COMPLETE and frozen; **P38 is COMMITTED at HEAD `726d4bd` — there is no uncommitted P38 work to commit or continue from (the only working-tree delta is this handoff refresh).** **P38 WP1 (deflated significance) + WP2 (tail-risk) + WP3 (decision doc + gate wire) all landed and are verified GREEN** (`--check-deflated-summary` and `--check-tail-risk-summary` byte-identical; `docs/BAB_P38_DECISION.md` replay-registered; `ruff` clean; `bab_quick.sh` 299 passed; both replay self-tests `pass:true`). **The binding row is P39 and it has NOT been started — no `bab_p39_*` scripts, tests, state, or decision doc exist yet.** **Your first job is P39 WP1 (regime-conditional deflated significance + tail risk)** → WP2 (cross-fixture replication) → WP3 (decision doc + gate wire). P39 WP0 (the slow full `bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`, plus a cross-version determinism test) is a large-time-budget close-out that does NOT block WP1/WP2. Before starting, verify the baseline with the FIRST ACTION commands (all GREEN); if any is RED, bisect — do NOT hand-edit artifacts. **Never run a generator with bare/no args — it overwrites the committed artifact.** **After any full pytest/`bab_gate` run, run `git checkout -- research_state/bab_p27/` to undo the trailing-newline mutation of the two frozen P27 `.md` files.** Do not re-open frozen P20–P38 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. **A handoff-only / docs-only / verification-only commit while P39 WP1–WP2 are open is a FAILED session — the only acceptable progress is new `bab_p39_*` code + tests + a byte-identical `--check-*`.** If P39 WP1+WP2+WP3 are complete AND the full gate (`bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`) is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log, not prose.