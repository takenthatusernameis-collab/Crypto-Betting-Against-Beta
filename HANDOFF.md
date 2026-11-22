# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T18:06:54Z (refreshed this session; supersedes the 2026-11-22T17:26:31Z stamp)
- **Git state:** working tree clean at HEAD (verified via `git rev-parse HEAD`); P20–P36 are all COMPLETE and frozen. The binding row is now **Campaign P37 "Cost-Aware Turnover & Capacity Closure"** — agent-executable, fully offline, zero maintainer dependency. P28 WP2–WP4 remain **maintainer-gated** (require `workflows:write` for CI and licensed CSV for real-market data).

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T18:06:54Z)

**CAMPAIGN P36 IS COMPLETE — ALL WPs LANDED AND GREEN.** P36 WP0 walk-forward/OOS harness, WP1 rank-weighted construction, WP2-WP3 decision doc + documentation-integrity closure + gate wire are all delivered, byte-identical, registered, and wired into `scripts/bab_gate.sh`. `tests/test_bab_p36_decision_consistency.py` → 14 PASS; `scripts/bab_p36_walk_forward.py --check-walk-forward-summary` → PASS; `scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary` → PASS; `scripts/bab_replay_decisions.py --subset p36_decision.md` → PASS; `scripts/bab_replay_full.py --subset walk_forward_summary,rank_weighted_summary` → PASS; `scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → PASS; `tests/test_bab_p34_doc_pointer_guard.py` → 7 passed, 1 skipped; ruff clean on all new/modified files.

**Do NOT re-do P20–P36 — all complete and frozen.**

**If you are the next agent:** P36 is done. The binding row is **Campaign P37 "Cost-Aware Turnover & Capacity Closure"** — the P36 successor. Execute the work packages below. The only maintainer-gated rows are P28 WP2–WP4 (`workflows:write` for CI enforcement, licensed CSV for real-market data); those stay blocked until a maintainer unblocks them and are NOT your work.

**P37 work packages (execute WP0 → WP1 → WP2 → WP3):**

- **WP0 — Transaction-cost & turnover surface on the wide universe.** `scripts/bab_p37_cost_surface.py` sweeping transaction costs × turnover on the P35 wide-universe fixture (40 assets, 8 seeds), proving per-cell costed Sharpe is non-increasing in cost level; emit `research_state/bab_p37/cost_surface_summary.json`; `tests/test_bab_p37_cost_surface.py` enforcing zero hand-typed numbers + byte-identity `--check-cost-surface-summary`.
- **WP1 — Market-impact & capacity limits.** `scripts/bab_p37_capacity.py` computing participation-rate break-even via fixed-iteration bisection on the impact grid; emit `research_state/bab_p37/capacity_summary.json`; `tests/test_bab_p37_capacity.py` pinning zero-crossing brackets and censoring reasons.
- **WP2 — Turnover reduction / hysteresis guard.** `scripts/bab_p37_turnover.py` validating turnover reduction vs the shipped equal-weight default under a hysteresis band; emit `research_state/bab_p37/turnover_summary.json`; `tests/test_bab_p37_turnover.py`.
- **WP3 — Decision doc + documentation-integrity closure + gate wire.** `generate_p37_decision.py` + `docs/BAB_P37_DECISION.md` + `tests/test_bab_p37_decision_consistency.py` (zero unmatched cells, table byte-identity, explicit verdicts, AST no-harness scan, ruff clean); register in replay registries (`scripts/bab_replay_decisions.py`, `scripts/bab_replay_full.py`); wire P37 block into `scripts/bab_gate.sh`; update README.md + docs/COVERAGE_NOTES.md "Binding next campaign" → P37; extend `tests/test_bab_p34_doc_pointer_guard.py` allow-list to include `"P37"`; re-run doc pointer guard test.

**Scope guardrails (read before coding):**
- **Additive only.** Do NOT edit frozen `strategies/betting_against_beta/beta.py`, `config.py`, `strategy.py`, `beta_estimators.py`, or any P20–P36 script/artifact, or any already-landed P36 artifact.
- **Do not weaken defaults.** The shipped default stays `weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS. P37 *evaluates* alternatives; it does not flip the default.
- **Synthetic only.** All evaluation on committed synthetic fixtures — explicitly **not real market data**. Every published figure carries the synthetic-provenance caveat.
- **Neutrality invariants are non-negotiable.** Every cell satisfies model beta-neutral (≤1e-3) / dollar-neutral (≤1e-9) / realized-beta (≤0.15).
- **Frozen P29 provenance ledger.** `research_state/bab_p29/provenance_audit.json` is frozen; the replay gate must not rewrite it.
- **No walk-forward lookahead.** OOS test periods must be strictly after training periods; no future information in training weights.
- **Rank safety valves never weakened.** `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` never below 0.20 / 4.0.

**Why P37 is the most repo-name-relevant next focus:**
- The repository is **Crypto-Betting-Against-Beta** — P36 proved the beta signal persists OOS and rank-weighted reduces churn without improving OOS Sharpe. P37 closes the *economic* loop: does BAB survive transaction costs, market impact, and capacity limits on the wide universe? That is the heavy, agent-executable conclusion that prevents the work from stopping at signal validation without cost/capacity evidence.
- P37 is **fully offline, deterministic, zero maintainer dependency** (no `workflows:write`, no licensed CSV, no network). It is the antidote to the idle-wait.

**What "heavy" means here (the campaign cannot be satisfied by docs/counts/gates):**
1. New deterministic cost-surface runner (`bab_p37_cost_surface.py`) sweeping costs × turnover into summary artifacts.
2. New deterministic capacity runner (`bab_p37_capacity.py`) computing break-even impact coefficients via bisection.
3. New deterministic turnover/hysteresis runner (`bab_p37_turnover.py`) validating churn reduction.
4. New deterministic decision generator (`generate_p37_decision.py`) consuming three committed JSON artifacts into a decision-grade verdict doc.
5. Byte-identical decision doc emission + replay registration.
6. New acceptance tests enforcing zero unmatched numbers, table byte-identity, explicit verdicts, no-harness execution.
7. Replay-full registry registration + gate block wiring.
8. Pointer integrity (README/COVERAGE_NOTES → P37 successor + doc pointer guard allow-list extended to "P37").

A docs-only / handoff-only / gate-only / count-only commit is FORBIDDEN and counts as automatic failure while P37 is incomplete.

**Inner loop while iterating on P37:**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p37_*.py
python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py
python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary
python3 scripts/bab_p37_capacity.py --check-capacity-summary
python3 scripts/bab_p37_turnover.py --check-turnover-summary
python3 scripts/bab_replay_decisions.py --subset p37_decision.md
python3 scripts/bab_replay_full.py --subset cost_surface_summary,capacity_summary,turnover_summary
python3 scripts/bab_p36_walk_forward.py --check-walk-forward-summary
python3 scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary
```

---

## CAMPAIGN P36 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T15:45:00Z)

**Declared:** 2026-11-22T14:36:10Z · **Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure" · **Priority: HIGH** · **Status: COMPLETE — all WPs landed and verified GREEN (verified 2026-11-22T15:45:00Z). Do NOT re-do it.**

P36 WP0 walk-forward/OOS harness, WP1 rank-weighted construction, WP2-WP3 decision doc + documentation-integrity closure + gate wire all complete. `tests/test_bab_p36_decision_consistency.py` → 14 PASS; `scripts/bab_p36_walk_forward.py --check-walk-forward-summary` → PASS; `scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary` → PASS; `scripts/bab_replay_decisions.py --subset p36_decision.md` → PASS; `scripts/bab_replay_full.py --subset walk_forward_summary,rank_weighted_summary` → PASS; `scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → PASS; `scripts/bab_replay_full.py --self-test` → PASS; ruff clean. **P36 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P35 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T14:36:10Z)

**Declared:** 2026-11-22T10:31:32Z · **Campaign:** P35 "Beta-Estimation Robustness & Signal-Stability Closure" · **Priority: HIGH** · **Status: COMPLETE — WP0 + WP1 + WP2 + WP3 all COMPLETE & GREEN (verified 2026-11-22T14:36:10Z, HEAD `335f8c6`). Do NOT re-do it.**

52 P35 tests PASS; ruff clean; `bab_quick.sh` GREEN. **P35 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P34 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T09:47:00Z)

**Declared:** 2026-11-22T07:44:24Z · **Campaign:** P34 "Wide-Universe Robustness & Strategy-Honesty Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

P34 established multi-seed robustness of the shipped default across 8 seeds × 6 config cells (48 cells), with systematic neutrality invariants verified at every cell, plus a statistical honesty battery and a documentation-pointer-rot guard. **P34 is COMPLETE. Do NOT re-do it.**

---

## BINDING ROW — Campaign P37 (AGENT-EXECUTABLE) + P28 WP2-WP4 (MAINTAINER-GATED)

### P37 "Cost-Aware Turnover & Capacity Closure" — the binding agent-executable row
P37 is the sole agent-executable binding row. All WPs are offline/deterministic/synthetic-only with zero maintainer dependency. Execute WP0 → WP1 → WP2 → WP3 per the INITIAL TASK MESSAGE above.

### P28 WP2-WP4 — MAINTAINER-GATED (not agent-executable)
- **P28 WP2 — CI Gate Enforcement.** Blocker: repo token lacks `workflows:write`. `.github/workflows/main.yml` must include a `bab-gate` job. Maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-push from agent.
- **P28 WP3 — Real-Market Data Ingestion.** Blocker: licensed CSV required; Coinbase public API returns 403. Maintainer must supply a licensed market data CSV.
- **P28 WP4 — Live-Market Deployment Decision.** Blocker: needs WP2+WP3 + maintainer authorization.

If a maintainer unblocks P28 WP2-WP4, they become binding rows AFTER P37 is complete.

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

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating: see P37 inner loop above.

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p36/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P36 script (frozen).
- Editing any P25 WP0-WP2 artifact (including `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv`), any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact, or any P30–P36 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P30–P36 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0 in any decision, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33/P34/P35/P36 reproducibility** (hard-coding `sha256`/`summary` values, skipping the xproc/self-test/check-summary checks, or editing committed artifacts to force a green replay).
- **Re-doing P32, P33, P34, P35, P36, or any P20-P31 campaign** (all COMPLETE and frozen).
- **Idle docs-only churn while agent-executable work exists.** P37 is agent-executable and INCOMPLETE — a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. A session may report an idle-wait state ONLY after P37 is complete (all WPs landed, full gate GREEN) AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not just prose.

---

## FUTURE AGENTS: READ THIS ONCE

**All agent-executable work through Campaign P36 is COMPLETE and frozen** (P20–P36), verified GREEN 2026-11-22T15:45:00Z. **Campaign P37 "Cost-Aware Turnover & Capacity Closure" is the binding agent-executable row — NOT STARTED.** Execute WP0 → WP1 → WP2 → WP3 per the INITIAL TASK MESSAGE. The only maintainer-gated rows are P28 WP2-WP4.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. P37 is agent-executable and INCOMPLETE. If a future session reports idle-wait, it must be because P37 is complete AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not just prose.

Do not re-open frozen P20–P36 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened) or flip `beta_neutral=True` / `weighting="equal"` off as the default. Never network-fetch prices. **Do not rewrite the frozen `research_state/bab_p29/provenance_audit.json`** — P37 entries are gated out of `--xproc`/`--check-provenance`. If this file says a WP is COMPLETE, it is COMPLETE; if it says a WP is maintainer-gated (currently **P28 WP2-WP4**), route it to the maintainer.
