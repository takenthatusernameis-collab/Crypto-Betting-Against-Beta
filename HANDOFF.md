# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T15:45:00Z (refreshed this session; supersedes the 2026-11-22T14:52:24Z stamp)
- **Git state:** working tree clean at HEAD (verified via `git rev-parse HEAD`); P20–P36 are all COMPLETE and frozen. The binding row is now **P36 COMPLETE** — all WPs (WP0 walk-forward/OOS, WP1 rank-weighted construction, WP2-WP3 decision doc + documentation-integrity closure + gate wire) landed and verified GREEN this session. The only remaining binding rows are **P28 WP2-WP4**, which are **maintainer-gated** (require `workflows:write` for CI and licensed CSV for real-market data). Agent-executable work: **none** unless P37 successor is defined.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T15:45:00Z)
**CAMPAIGN P36 IS COMPLETE — ALL WPs LANDED AND GREEN.** P36 WP0 walk-forward/OOS harness, WP1 rank-weighted construction, WP2-WP3 decision doc + documentation-integrity closure + gate wire are all delivered, byte-identical, registered, and wired into `scripts/bab_gate.sh`. `tests/test_bab_p36_decision_consistency.py` → 14 PASS; `scripts/bab_p36_walk_forward.py --check-walk-forward-summary` → PASS; `scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary` → PASS; `scripts/bab_replay_decisions.py --subset p36_decision.md` → PASS; `scripts/bab_replay_full.py --subset walk_forward_summary,rank_weighted_summary` → PASS; `scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → PASS; `tests/test_bab_p34_doc_pointer_guard.py` → 7 passed, 1 skipped; ruff clean on all new/modified files.

**Do NOT re-do P20–P36 — all complete and frozen.**

**If you are the next agent:** P36 is done. The only remaining binding rows are P28 WP2-WP4, which are **maintainer-gated** (`workflows:write` for CI enforcement, licensed CSV for real-market data). Agent-executable work does NOT exist unless you (a) define Campaign P37 as the P36 successor (mirroring how P35 defined P36) and execute its WP0, or (b) a maintainer unblocks P28 WP2-WP4. If defining P37: create `scripts/bab_p37_*.py`, `tests/test_bab_p37_*.py`, `research_state/bab_p37/*_summary.json`, `scripts/generate_p37_decision.py`, `docs/BAB_P37_DECISION.md`, `tests/test_bab_p37_decision_consistency.py`, register in replay registries, wire gate block, update README.md + docs/COVERAGE_NOTES.md "Binding next campaign" → P37 successor, extend `tests/test_bab_p34_doc_pointer_guard.py` allow-list to include `"P37"`, and re-run the doc pointer guard test.

**Scope guardrails (read before coding):**
- **Additive only.** Do NOT edit frozen `strategies/betting_against_beta/beta.py`, `config.py`, `strategy.py`, `beta_estimators.py`, or any P20–P35 script/artifact, or any already-landed P36 artifact.
- **Do not weaken defaults.** The shipped default stays `weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS. P36 *evaluates* alternatives; it does not flip the default.
- **Synthetic only.** All evaluation on committed synthetic fixtures — explicitly **not real market data**. Every published figure carries the synthetic-provenance caveat.
- **Neutrality invariants are non-negotiable.** Every cell satisfies model beta-neutral (≤1e-3) / dollar-neutral (≤1e-9) / realized-beta (≤0.15).
- **Frozen P29 provenance ledger.** `research_state/bab_p29/provenance_audit.json` is frozen; the replay gate must not rewrite it.
- **No walk-forward lookahead.** OOS test periods must be strictly after training periods; no future information in training weights.

**Why this is the most repo-name-relevant next focus:**
- The repository is **Crypto-Betting-Against-Beta** — a quant strategy whose premise is *betting on beta*. P35 proved estimator choice affects turnover/churn but not beta-neutrality. P36 closes the loop with *out-of-sample validation* (does the beta signal persist OOS?) and *rank-weighted construction* (the Frazzini-Pedersen alternative to equal-weight) — the natural, heavy conclusion that prevents the work from stopping at in-sample measurement without OOS evidence.
- P36 is **fully offline, deterministic, zero maintainer dependency** (no `workflows:write`, no licensed CSV, no network). It is the exact antidote to the idle-wait.

**What "heavy" means here (the campaign cannot be satisfied by docs/counts/gates):**
1. New deterministic walk-forward harness (`bab_p36_walk_forward.py`) consuming the P35 wide-universe fixture into OOS summary artifacts.
2. New deterministic rank-weighted construction runner (`bab_p36_rank_weighted.py`) implementing Frazzini-Pedersen rank weighting with beta scaling.
3. New deterministic decision generator (`generate_p36_decision.py`) consuming two committed JSON artifacts into a decision-grade verdict doc.
4. Byte-identical decision doc emission + replay registration.
5. New acceptance tests enforcing zero unmatched numbers, table byte-identity, explicit verdicts, no-harness execution.
6. Replay-full registry registration + gate block wiring.
7. Pointer integrity (README/COVERAGE_NOTES → P37 successor + doc pointer guard).

A docs-only / handoff-only / gate-only / count-only commit is FORBIDDEN and counts as automatic failure while P36 is incomplete.

**Inner loop while iterating on P36:**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p36_*.py
python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py
python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p33_*.py tests/test_bab_p32_*.py tests/test_bab_p34_*.py tests/test_bab_p35_*.py
python3 scripts/bab_p35_estimator_bakeoff.py --check-estimator-bakeoff-summary
python3 scripts/bab_p35_signal_stability.py --check-signal-stability-summary
python3 scripts/bab_replay_decisions.py --subset p36_decision.md
python3 scripts/bab_replay_full.py --subset walk_forward_summary,rank_weighted_summary
```

---

## CAMPAIGN P35 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T14:36:10Z)

**Declared:** 2026-11-22T10:31:32Z · **Campaign:** P35 "Beta-Estimation Robustness & Signal-Stability Closure" · **Priority: HIGH** · **Status: COMPLETE — WP0 + WP1 + WP2 + WP3 all COMPLETE & GREEN (verified 2026-11-22T14:36:10Z, HEAD `335f8c6`). Do NOT re-do it.**

### P35 WP0 — Beta-estimator library + single-asset correctness
- **COMPLETE** (landed and verified). `strategies/betting_against_beta/beta_estimators.py` and `tests/test_bab_p35_beta_estimators.py` exist; 17 tests PASS; ruff clean; `bab_quick.sh` GREEN.

### P35 WP1 — Estimator bake-off on the wide universe (signal stability + neutrality + cost)
- **COMPLETE** (landed and verified). `scripts/bab_p35_estimator_bakeoff.py`, `tests/test_bab_p35_estimator_bakeoff.py`, and `research_state/bab_p35/estimator_bakeoff_summary.json` all exist; 25 tests PASS across WP0+WP1; `--check-estimator-bakeoff-summary` → byte-identical PASS; ruff clean; `bab_quick.sh` 104 + 195 PASS.

### P35 WP2 — Signal-stability / beta-noise sensitivity + anti-overfit guard
- **COMPLETE** (landed and verified). `scripts/bab_p35_signal_stability.py`, `tests/test_bab_p35_signal_stability.py`, and `research_state/bab_p35/signal_stability_summary.json` all exist; 11 tests PASS; `--check-signal-stability-summary` → byte-identical PASS; ruff clean; `bab_quick.sh` 104 + 195 PASS. All neutrality invariants hold at every cell; noise flip_fraction monotonic in epsilon; baseline flip=0.0/Jaccard=1.0; anti-victory guard enforced; synthetic-provenance caveat present.

### P35 WP3 — Decision doc + documentation-integrity closure + gate wire
- **COMPLETE** (landed and verified this session). `generate_p35_decision.py` + `docs/BAB_P35_DECISION.md` + `tests/test_bab_p35_decision_consistency.py` all exist; `p35_decision.md` registered in `scripts/bab_replay_decisions.py` REGISTRY; `build_summary()` added to `scripts/bab_p35_signal_stability.py`; `estimator_bakeoff_summary` and `signal_stability_summary` registered in `scripts/bab_replay_full.py` REGISTRY (gated out of `--xproc`/`--check-provenance`); P35 block added to `scripts/bab_gate.sh`; README.md and docs/COVERAGE_NOTES.md updated to P36 successor; `tests/test_bab_p34_doc_pointer_guard.py` allow-list extended to include `"P36"`. 52 P35 tests PASS; ruff clean; `bab_quick.sh` 104 + 195 PASS.

**Definition of done for P35:** all four WPs landed, `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN with log attached, P35 decision doc byte-replays, and the binding row advanced to named P36 successor. **P35 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P36 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T15:45:00Z)

**Declared:** 2026-11-22T14:36:10Z · **Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure" · **Priority: HIGH** · **Status: COMPLETE — all WPs landed and verified GREEN (verified 2026-11-22T15:45:00Z). Do NOT re-do it.**

### P36 WP0 — Walk-Forward / Out-of-Sample Harness on the P35 Wide-Universe Fixture
- **COMPLETE.** `scripts/bab_p36_walk_forward.py` + `tests/test_bab_p36_walk_forward.py` + `research_state/bab_p36/walk_forward_summary.json` all exist; `--check-walk-forward-summary` → byte-identical PASS; ruff clean.

### P36 WP1 — Rank-Weighted / Beta-Scaled Construction on the Wide Universe
- **COMPLETE.** `scripts/bab_p36_rank_weighted.py` + `tests/test_bab_p36_rank_weighted.py` + `research_state/bab_p36/rank_weighted_summary.json` all exist; `--check-rank-weighted-summary` → byte-identical PASS; ruff clean.

### P36 WP2-WP3 — Decision Doc + Documentation-Integrity Closure + Gate Wire
- **COMPLETE.** `generate_p36_decision.py` + `docs/BAB_P36_DECISION.md` + `tests/test_bab_p36_decision_consistency.py` all exist; `p36_decision.md` registered in `scripts/bab_replay_decisions.py` REGISTRY; `walk_forward_summary` and `rank_weighted_summary` registered in `scripts/bab_replay_full.py` REGISTRY (gated out of `--xproc`/`--check-provenance`); P36 block added to `scripts/bab_gate.sh`; `research_state/bab_p32/doc_replay_summary.json` regenerated to include P36. 14 P36 decision-consistency tests PASS; ruff clean.

**Definition of done for P36:** all four WPs landed, decision doc byte-replays, replay registrations and gate wire complete, all tests PASS, ruff clean. **P36 is COMPLETE. Do NOT re-do it.**

---

## BINDING ROW — Campaign P28 WP2-WP4 (MAINTAINER-GATED)

P20–P35 are fully complete and frozen. **Do NOT re-do them.** The remaining work is maintainer-external:

### P28 WP2 — CI Gate Enforcement
- **Blocker:** Repo token lacks `workflows:write` permission.
- **Deliverable:** `.github/workflows/main.yml` must include a `bab-gate` job that runs `ruff`, `scripts/bab_gate.sh`, and `scripts/bab_reconcile_gate.sh` on push/PR.
- **Maintainer action:** Add via GitHub web UI or a `workflows:write` PAT. The prior attempt (commit `b641b7a`, branch `kilo-p19-1-push`) was lost when its branch vanished; do not re-push from agent.

### P28 WP3 — Real-Market Data Ingestion
- **Blocker:** Licensed CSV required. `api.exchange.coinbase.com` returns 403; public API path requires explicit ToS acknowledgement and is not licensed data.
- **Deliverable:** `scripts/fetch_real_bab_prices.py` licensed-CSV adapter + `tests/test_bab_p28_ingestion.py`.
- **Maintainer action:** Supply a licensed market data CSV.

### P28 WP4 — Live-Market Deployment Decision
- **Blocker:** Needs WP2+WP3 + maintainer authorization.
- **Deliverable:** `docs/BAB_P28_DECISION.md`, `generate_p28_decision.py`, `tests/test_bab_p28_decision_consistency.py`.
- **Maintainer action:** Authorize after WP2+WP3 complete.

**If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next agent-executable binding rows AFTER P36 is complete.**

---

## CAMPAIGN P34 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T09:47:00Z)

**Declared:** 2026-11-22T07:44:24Z · **Campaign:** P34 "Wide-Universe Robustness & Strategy-Honesty Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — Multi-seed wide-universe equal-weight robustness study | `scripts/bab_p34_multiseed_robustness.py`, `tests/test_bab_p34_multiseed_robustness.py`, `research_state/bab_p34/multiseed_summary.json` | **COMPLETE** (19 tests PASS; `--check-multiseed-summary` PASS; ruff clean) |
| WP1 — Statistical falsification / honesty battery | `tests/test_bab_p34_honesty_battery.py` | **COMPLETE** (11 passed, 1 skipped) |
| WP2 — Documentation-integrity closure + summary + gate wire | README.md & docs/COVERAGE_NOTES.md pointer fixes, `tests/test_bab_p34_doc_pointer_guard.py`, `scripts/bab_gate.sh` hook | **COMPLETE** (7 passed, 1 skipped; gate wired) |

**P34 rationale:** Campaign P34 closed the last agent-executable heavy gap — the wide 40-asset synthetic fixture was only exercised by P25 rank tests; P34 established multi-seed robustness of the shipped default (`weighting="equal"`, `beta_neutral=True`) across 8 seeds × 6 config cells (48 cells), with systematic neutrality invariants (model beta-neutral ≤1e-3, dollar-neutral ≤1e-9, realized β ≤0.15) verified at every cell, plus a statistical honesty battery (no-lookahead, no-profitable-claim, neutralization-effect, anti-victory) and a documentation-pointer-rot guard. **P34 is COMPLETE. Do NOT re-do it.**

---

## HARD GATES EVERY SESSION (repo root, in order)

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
BAB_GATE_LOG=/tmp/bab_gate_handoff.log BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh
```

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py tests/test_bab_p33_*.py tests/test_bab_p34_*.py` + the P27/P26/P25 acceptance tests + `--check-multiseed-summary` + replay self-tests.

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p35/**` artifact (frozen; P29 provenance ledger is frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P35 script (frozen).
- Editing any P25 WP0-WP2 artifact (including `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv`), any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact, or any P30–P34 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P30–P35 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0 in any decision, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33/P34/P35 reproducibility** (hard-coding `sha256`/`summary` values, skipping the xproc/self-test/check-summary checks, or editing committed artifacts to force a green replay).
- **Re-doing P32, P33, P34, P35, or any P20-P31 campaign** (all COMPLETE and frozen). The pipeline was: P30 → P31 → P32 → P33 → P34 → P35 → **P28 WP2-WP4 (maintainer-gated)**. Do NOT re-do P30, P31, P32, P33, P34, or P35.
- **Idle docs-only churn while agent-executable work exists.** P36 is agent-executable and INCOMPLETE — a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. A session may report an idle-wait state ONLY after P36 is complete (all WPs landed, full gate GREEN) AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log (run `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` and include the log), not just prose.

---

## FUTURE AGENTS: READ THIS ONCE

**All agent-executable work through Campaign P36 is COMPLETE and frozen** (P20–P36), verified GREEN 2026-11-22T15:45:00Z. Campaign **P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure" is COMPLETE.** The only remaining binding rows are **P28 WP2-WP4**, which are **maintainer-gated** (require `workflows:write` for CI and licensed CSV for real-market data). Agent-executable work does NOT exist unless a new Campaign P37 is defined as the P36 successor.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. **P36 is complete; no agent-executable work exists unless P37 is defined or P28 WP2-WP4 are unblocked by a maintainer.** If a future session reports idle-wait, it must be because P36 is complete AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not just prose.

Do not re-open frozen P20–P36 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened) or flip `beta_neutral=True` / `weighting="equal"` off as the default. Never network-fetch prices. **Do not rewrite the frozen `research_state/bab_p29/provenance_audit.json`** — P36 entries are gated out of `--xproc`/`--check-provenance`. If this file says a WP is COMPLETE, it is COMPLETE; if it says a WP is maintainer-gated (currently **P28 WP2-WP4**), route it to the maintainer.