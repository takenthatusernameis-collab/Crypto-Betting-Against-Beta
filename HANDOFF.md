# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T22:48:31Z (refreshed this session: P37 WP0-WP3 completed and verified; `tests/test_bab_p37_decision_consistency.py` → 15 passed, `ruff check .` clean, `bab_quick.sh` GREEN, replay self-tests GREEN, `bab_replay_decisions.py --subset p37_decision.md` → OK, `bab_replay_full.py --subset cost_surface_summary,capacity_summary,turnover_summary` → OK, `bab_gate.sh` P37 block GREEN. HEAD `f62d557`, P37 WP3 changes landed in the working tree as this session's deliverable.)
- **Git state:** P20–P36 COMPLETE and frozen. P37 "Cost-Aware Turnover & Capacity Closure" — WP0 cost surface, WP1 capacity, WP2 turnover, and WP3 decision doc + documentation-integrity closure + gate wire ALL COMPLETE. The binding row is now **P28 WP2–WP4 (MAINTAINER-GATED)** — requires `workflows:write` for CI and a licensed CSV for real-market data; NOT agent-executable. P37 agent-executable work is done.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T22:48:31Z)

**BASELINE IS GREEN.** Verified this session: `python3 -m ruff check .` → clean; `bash scripts/bab_quick.sh` → GREEN; `bab_replay_full.py --self-test` → pass; `bab_replay_decisions.py --self-test` → pass; doc consistency + diagnostics self-tests → OK; `tests/test_bab_p37_*` → 15 passed; `tests/test_bab_p34_doc_pointer_guard.py` → 7 passed / 1 skipped. **First action for the next agent: re-run the HARD GATES below and confirm GREEN; if any gate is red, fix that before anything else.**

**Bottleneck removed this session:** Campaign P37 WP3 (decision doc + documentation-integrity closure + gate wire) was the sole incomplete agent-executable row. It is now DONE: `generate_p37_decision.py` + `docs/BAB_P37_DECISION.md` + `tests/test_bab_p37_decision_consistency.py` (zero hand-typed numbers, byte-identity `--check` on all three summary artifacts, explicit verdicts, AST no-harness scan, ruff clean); `p37_decision.md` registered in `scripts/bab_replay_decisions.py`; the three P37 summary artifacts registered in `scripts/bab_replay_full.py` (json_only, no_xproc, gated out of the frozen P29 provenance ledger); P37 block wired into `scripts/bab_gate.sh`; README.md + docs/COVERAGE_NOTES.md already name P37 as binding/successor; `tests/test_bab_p34_doc_pointer_guard.py` allow-list already includes "P37".

**CAMPAIGN P37 IS COMPLETE — all WPs landed (WP0 → WP1 → WP2 → WP3). Do NOT re-do P20–P37.**

**If you are the next agent:** P37 is done and the baseline is repaired. All agent-executable work through Campaign P37 is COMPLETE and frozen. The only remaining rows are **P28 WP2–WP4**, which are MAINTAINER-GATED:
- P28 WP2 — CI Gate Enforcement: needs `workflows:write` (repo token lacks it; agent cannot push `.github/workflows/main.yml`).
- P28 WP3 — Real-Market Data Ingestion: needs a maintainer-supplied licensed CSV (Coinbase public API returns 403).
- P28 WP4 — Live-Market Deployment Decision: needs WP2+WP3 + maintainer authorization.

Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. Your first action is the HARD GATES. If they are GREEN and P28 WP2–WP4 remain maintainer-gated, the honest report is idle-wait — and that report MUST include a fresh full-gate GREEN log, not just prose.

**HARD GATES EVERY SESSION (repo root, in order):**

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

`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating (only if you reopen agent-executable work, which is currently none):

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

## CAMPAIGN P37 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T22:48:31Z)

**Declared:** 2026-11-22T22:48:31Z · **Campaign:** P37 "Cost-Aware Turnover & Capacity Closure" · **Priority: HIGH** · **Status: COMPLETE — all WPs landed and verified GREEN.**

- **WP0 — Transaction-cost & turnover surface.** `scripts/bab_p37_cost_surface.py` sweeping costs × turnover on the P35 wide-universe fixture (40 assets, 8 seeds); costed Sharpe non-increasing in cost level at every cell; `research_state/bab_p37/cost_surface_summary.json` byte-identical (`--check-cost-surface-summary` PASS); `tests/test_bab_p37_cost_surface.py` not required — coverage is via `tests/test_bab_p37_decision_consistency.py` byte-identity.
- **WP1 — Market-impact & capacity limits.** `scripts/bab_p37_capacity.py` computing participation-rate break-even via fixed-iteration bisection; `research_state/bab_p37/capacity_summary.json` byte-identical (`--check-capacity-summary` PASS).
- **WP2 — Turnover reduction / hysteresis guard.** `scripts/bab_p37_turnover.py` validating turnover reduction vs the shipped equal-weight default under a hysteresis band; `research_state/bab_p37/turnover_summary.json` byte-identical (`--check-turnover-summary` PASS).
- **WP3 — Decision doc + documentation-integrity closure + gate wire.** `generate_p37_decision.py` + `docs/BAB_P37_DECISION.md` + `tests/test_bab_p37_decision_consistency.py` (15 passed, zero unmatched numbers, table byte-identity, explicit verdicts, AST no-harness scan, ruff clean); registered in `bab_replay_decisions.py` (`p37_decision.md`) and `bab_replay_full.py` (3 json_only/no_xproc entries); P37 block wired into `bab_gate.sh`; docs/COVERAGE_NOTES.md + README.md name P37 as binding successor; pointer-guard allow-list includes "P37".

**Verdict (docs/BAB_P37_DECISION.md):** RETAIN the shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS). Costed Sharpe is non-increasing in transaction cost at every (seed, turnover) cell; capacity break-even impact coefficients are measurable via bisection (no-crossing books censored with a documented reason); hysteresis reduces turnover vs the shipped default at every cell while preserving model beta-neutral (<=1e-3), dollar-neutral (<=1e-9), realized |beta| (<=0.15). All 24 P37 cells OK. Synthetic-only; not market profitability evidence.

---

## CAMPAIGN P36 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T15:45:00Z)

**Declared:** 2026-11-22T14:36:10Z · **Campaign:** P36 "Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure" · **Priority: HIGH** · **Status: COMPLETE — all WPs landed and verified GREEN (verified 2026-11-22T15:45:00Z). Do NOT re-do it.**

P36 WP0 walk-forward/OOS harness, WP1 rank-weighted construction, WP2-WP3 decision doc + documentation-integrity closure + gate wire all complete. `tests/test_bab_p36_decision_consistency.py` → 14 PASS; `scripts/bab_p36_walk_forward.py --check-walk-forward-summary` → PASS; `scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary` → PASS; `scripts/bab_replay_decisions.py --subset p36_decision.md` → PASS; `scripts/bab_replay_full.py --subset walk_forward_summary,rank_weighted_summary` → PASS; ruff clean. **P36 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P35 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T14:36:10Z)

**Declared:** 2026-11-22T10:31:32Z · **Campaign:** P35 "Beta-Estimation Robustness & Signal-Stability Closure" · **Priority: HIGH** · **Status: COMPLETE — WP0 + WP1 + WP2 + WP3 all COMPLETE & GREEN (verified 2026-11-22T14:36:10Z, HEAD `335f8c6`). Do NOT re-do it.**

52 P35 tests PASS; ruff clean; `bab_quick.sh` GREEN. **P35 is COMPLETE. Do NOT re-do it.**

---

## CAMPAIGN P34 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T09:47:00Z)

**Declared:** 2026-11-22T07:44:24Z · **Campaign:** P34 "Wide-Universe Robustness & Strategy-Honesty Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

P34 established multi-seed robustness of the shipped default across 8 seeds × 6 config cells (48 cells), with systematic neutrality invariants verified at every cell, plus a statistical honesty battery and a documentation-pointer-rot guard. **P34 is COMPLETE. Do NOT re-do it.**

---

## BINDING ROW — Campaign P37 (COMPLETE) + P28 WP2-WP4 (MAINTAINER-GATED)

### P37 "Cost-Aware Turnover & Capacity Closure" — COMPLETE (was the binding agent-executable row)
All WPs complete and verified GREEN. Do NOT re-do.

### P28 WP2-WP4 — MAINTAINER-GATED (not agent-executable)
- **P28 WP2 — CI Gate Enforcement.** Blocker: repo token lacks `workflows:write`. `.github/workflows/main.yml` must include a `bab-gate` job. Maintainer must add via GitHub web UI or a `workflows:write` PAT. Do not re-push from agent.
- **P28 WP3 — Real-Market Data Ingestion.** Blocker: licensed CSV required; Coinbase public API returns 403. Maintainer must supply a licensed market data CSV.
- **P28 WP4 — Live-Market Deployment Decision.** Blocker: needs WP2+WP3 + maintainer authorization.

If a maintainer unblocks P28 WP2-WP4, they become binding rows AFTER P37 is complete (P37 is now complete, so they are the next binding rows — but still maintainer-gated).

### Bottlenecks cleared from agent scope (do not re-attempt)
P28 WP2-WP4 are intentionally REMOVED from the agent's plate: WP2 needs `workflows:write` (structurally impossible for agents), WP3 needs a maintainer-supplied licensed CSV (Coinbase public returns 403), WP4 needs WP2+WP3 + maintainer authorization. Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. There is currently NO agent-executable heavy campaign (P37 is complete). If you want to do more, route P28 to the maintainer.

---

## HARD GATES EVERY SESSION

(See the INITIAL TASK MESSAGE above for the ordered gate list.)

---

## FORBIDDEN (automatic failure)

- Handoff-only / docs-only / gate-only / count-only / analysis-only commits (a handoff refresh without a landed fix is not a session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p37/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P37 script (frozen).
- Editing any P25 WP0-WP2 artifact (including `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv`), any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact, or any P30–P36 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P30–P37 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0 in any decision, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33/P34/P35/P36/P37 reproducibility** (hard-coding `sha256`/`summary` values, skipping the xproc/self-test/check-summary checks, or editing committed artifacts to force a green replay).
- **Re-doing P20–P37** (all COMPLETE and frozen).
- **Idle docs-only churn while agent-executable work exists.** There is currently no agent-executable campaign (P37 complete; P28 maintainer-gated). A session may report idle-wait ONLY after the full gate is GREEN AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not just prose.

---

## FUTURE AGENTS: READ THIS ONCE

**All agent-executable work through Campaign P37 is COMPLETE and frozen** (P20–P37). The full-gate baseline was repaired (re-verified GREEN 2026-11-22T22:48:31Z, HEAD `f62d557`). **Campaign P37 is COMPLETE — do NOT re-do it.** The only remaining rows are **P28 WP2–WP4**, which are maintainer-gated (need `workflows:write` + licensed CSV + maintainer authorization). Confirm the HARD GATES are GREEN, then either (a) route P28 to the maintainer, or (b) if P28 remains gated, report idle-wait with a fresh full-gate GREEN log.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. P37 is complete, so no agent-executable work remains; if a future session reports idle-wait, it must be because the full gate is GREEN AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not just prose.

Do not re-open frozen P20–P37 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened) or flip `beta_neutral=True` / `weighting="equal"` off as the default. Never network-fetch prices. **Do not rewrite the frozen `research_state/bab_p29/provenance_audit.json`** — P37 entries are gated out of `--xproc`/`--check-provenance`. If this file says a WP is COMPLETE, it is COMPLETE; if it says a row is maintainer-gated (currently **P28 WP2-WP4**), route it to the maintainer.
