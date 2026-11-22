# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T10:40:00Z (refreshed this session; supersedes the 2026-11-22T10:39:14Z stamp)
- **Git state:** HEAD `f74839f` at write time (working tree clean; verified via `git rev-parse HEAD`). **P20–P34 are all COMPLETE and frozen.** The binding row is **Campaign P35 "Beta-Estimation Robustness & Signal-Stability Closure" — ACTIVE, agent-executable, HEAVY.** The post-P34 idle-wait directive is REMOVED: P35 is the first heavy, fully offline, zero-maintainer-dependency successor to P34, and idle-wait is FORBIDDEN while P35 is incomplete.
- **Gate verified GREEN this session (fast inner loop + doc-pointer guard after the P35 binding switch):** `python3 -m ruff check .` PASS; `python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py` → 7 passed, 1 skipped (guard now recognizes P35 as the successor binding); `python3 -m pytest -q tests/test_bab_p34_*.py tests/test_bab_p33_*.py tests/test_bab_p31_registry_completeness.py tests/test_bab_p32_*.py` → 83 passed, 2 skipped; `bash scripts/bab_quick.sh` → 104 + 195 tests PASS. The full gate (`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh`, ~16 min) must be run once and its GREEN log attached before any P35 WP boundary is declared complete.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T10:40:00Z)

**EXECUTE CAMPAIGN P35 WP1 — "Estimator Bake-off on the Wide Universe (Signal Stability + Neutrality + Cost)." THIS IS THE BINDING ROW. IDLE-WAIT IS FORBIDDEN WHILE P35 IS INCOMPLETE.**

P20–P34 are fully landed and frozen. **Do NOT re-do them.** P35 WP0 is COMPLETE and verified (`strategies/betting_against_beta/beta_estimators.py` + `tests/test_bab_p35_beta_estimators.py` exist; 17 tests PASS; ruff clean; `bab_quick.sh` GREEN). The declaration is a *landed artifact*, not merely an obligation to start.

**Immediate work: P35 WP1 — Estimator Bake-off on the Wide Universe**

Deliverables (all required, no partial credit):
1. **Create `scripts/bab_p35_estimator_bakeoff.py`** — run the shipped default (`weighting="equal"`, `beta_neutral=True`, `transaction_costs=0.001`) across the P34 wide-universe recipe (8 seeds, 40 assets from `tests/fixtures/wide_bab_universe.csv`) × estimator families:
   - Rolling-OLS: `window ∈ {60, 90, 120}`
   - EWMA: `halflife ∈ {20, 40, 60}`
   - Shrinkage: `intensity ∈ {0.1, 0.3}` (target = 1.0 or cross-sectional mean)
   Per cell record: realized beta, model beta-neutrality (≤1e-3), dollar-neutrality (≤1e-9), **beta rank-stability** (Spearman corr of betas vs OLS baseline + long/short set Jaccard overlap), turnover, net-of-cost Sharpe, ann vol, max-DD.

2. **Emit deterministic `research_state/bab_p35/estimator_bakeoff_summary.json`** (schema `bab_p35.estimator_bakeoff/1`) with `--check-estimator-bakeoff-summary` byte-diff (mirror P34 WP0 `--check-multiseed-summary`).

3. **Create `tests/test_bab_p35_estimator_bakeoff.py`** — neutrality holds for EVERY estimator at EVERY cell; EWMA/shrinkage measurably reduce beta-noise/turnover vs OLS without breaking neutrality; summary determinism.

4. **Run acceptance loop** — `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p35_*.py` + `python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py` — all must PASS. Do NOT proceed to WP2 until WP1 tests pass.

**Scope guardrails (read before coding):**
- **Additive only.** Do NOT edit frozen `strategies/betting_against_beta/beta.py`, `config.py`, `strategy.py`, or any P20–P34 script/artifact. The new estimators delegate to the existing `calculate_rolling_beta` for the OLS parity anchor; do not modify it.
- **Do not weaken defaults.** The shipped default stays `weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS. P35 *evaluates* alternatives; it does not flip the default.
- **Synthetic only.** All evaluation on committed synthetic fixtures (`tests/fixtures/wide_bab_universe.csv` 40-asset, `tests/fixtures/real_market_prices.csv` 9-asset) — both explicitly **not real market data**. Every published figure carries the synthetic-provenance caveat.
- **Neutrality invariants are non-negotiable.** Any estimator that fails model beta-neutral (≤1e-3) / dollar-neutral (≤1e-9) / realized-beta (≤0.15) at any cell is a FAIL, not a "finding."

**Why this is the most repo-name-relevant next focus:**
- The repository is **Crypto-Betting-Against-Beta** — a quant strategy whose entire premise is *betting on beta*. Beta estimation methodology directly determines long/short selection, turnover, and realized-beta neutrality. It has never been stress-tested across estimator families.
- P20–P34 hardened reproducibility, provenance, fidelity, honesty, and multi-seed robustness of the *shipped* rolling-OLS default — but always with the SAME estimator. P35 varies the estimator itself.
- P35 is **fully offline, deterministic, zero maintainer dependency** (no `workflows:write`, no licensed CSV, no network). It is the exact antidote to the idle-wait.

**What "heavy" means here (the campaign cannot be satisfied by docs/counts/gates):**
1. New quant code integration (consuming `beta_estimators.py` in the bake-off).
2. A multi-cell estimator bake-off with quantitative signal-stability + neutrality + cost metrics.
3. Deterministic artifact emission + byte-diff guard.
4. New acceptance tests enforcing neutrality invariants and stability improvements.

A docs-only / handoff-only / gate-only / count-only commit is FORBIDDEN and counts as automatic failure while P35 is incomplete.

**Inner loop while iterating on P35 WP1:**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p35_*.py
python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py
python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p33_*.py tests/test_bab_p32_*.py tests/test_bab_p34_*.py
```

---

## CAMPAIGN P35 — BINDING ROW (ACTIVE, AGENT-EXECUTABLE, HEAVY)

**Declared:** 2026-11-22T10:31:32Z · **Campaign:** P35 "Beta-Estimation Robustness & Signal-Stability Closure" · **Priority: HIGH** · **Status: ACTIVE — execute WP0→WP1→WP2→WP3 in order.**

### P35 WP0 — Beta-estimator library + single-asset correctness
- **COMPLETE** (landed and verified this session). `strategies/betting_against_beta/beta_estimators.py` and `tests/test_bab_p35_beta_estimators.py` exist; 17 tests PASS; ruff clean; `bab_quick.sh` GREEN.

### P35 WP1 — Estimator bake-off on the wide universe (signal stability + neutrality + cost)  ← **NEXT**
- **New `scripts/bab_p35_estimator_bakeoff.py`**: run shipped default across P34 wide-universe recipe (8 seeds, 40 assets) × estimator families {rolling-OLS window∈{60,90,120}, EWMA halflife∈{20,40,60}, shrinkage intensity∈{0.1,0.3}}. Per cell record: realized beta, model beta-neutrality, dollar-neutrality, **beta rank-stability** (Spearman corr vs OLS baseline + long/short set Jaccard overlap), turnover, net-of-cost Sharpe, ann vol, max-DD.
- **Emit** deterministic `research_state/bab_p35/estimator_bakeoff_summary.json` (schema `bab_p35.estimator_bakeoff/1`) + `--check-estimator-bakeoff-summary` byte-diff.
- **New `tests/test_bab_p35_estimator_bakeoff.py`**: neutrality holds for EVERY estimator at EVERY cell; EWMA/shrinkage measurably reduce beta-noise/turnover vs OLS without breaking neutrality; summary determinism.
- **Acceptance:** every cell satisfies the neutrality invariants; summary reproducible byte-for-byte; tests PASS.

### P35 WP2 — Signal-stability / beta-noise sensitivity + anti-overfit guard
- **New `scripts/bab_p35_signal_stability.py`**: quantify selection churn — fraction of names flipping long↔short under (a) tiny beta noise injection and (b) estimator switch (OLS↔EWMA↔shrinkage); show shrinkage/EWMA reduce churn while preserving neutrality. Mirror P34 WP1 anti-victory guard.
- **New `tests/test_bab_p35_signal_stability.py`**: churn direction/monotonicity assertions, anti-victory guard, synthetic-provenance guard.
- **Acceptance:** churn results internally consistent; guards PASS.

### P35 WP3 — Decision doc + documentation-integrity closure + gate wire + replay registration
- **New `docs/BAB_P35_DECISION.md`** (deterministic verdict from WP1/WP2 artifacts — e.g. "estimator choice materially affects turnover/churn but not beta-neutrality; default rolling-OLS retained / EWMA recommended for turnover reduction", decided from artifacts, **no hand-typed numbers**).
- **New `scripts/generate_p35_decision.py`** (deterministic generator from `research_state/bab_p35/*.json`) and **register it in `scripts/bab_replay_decisions.py` REGISTRY as `p35_decision.md`**.
- **New `tests/test_bab_p35_decision_consistency.py`** (byte-replay consistency of the decision doc).
- **Register** `research_state/bab_p35/estimator_bakeoff_summary.json` in `scripts/bab_replay_full.py` REGISTRY and add a **P35 block to `scripts/bab_gate.sh`** mirroring the P34 block.
- **Update** README.md "Binding next campaign" → P35 and docs/COVERAGE_NOTES.md "Active work is binding" → P35, then re-run `tests/test_bab_p34_doc_pointer_guard.py`.
- **Acceptance:** full gate GREEN; decision doc byte-replays; no stale pointers; P35 removed from "active" and a P36 successor row named in HANDOFF.

**Definition of done for P35:** all four WPs landed, `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN with log attached, P35 decision doc byte-replays, and the binding row advanced to a named P36 successor (or explicit evidence-backed idle declaration).

---

## BINDING ROW — Campaign P28 WP2-WP4 (MAINTAINER-GATED)

P20–P34 are fully complete and frozen. **Do NOT re-do them.** The remaining work is maintainer-external:

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

**If a maintainer unblocks (a) `workflows:write` and/or (b) a licensed market CSV, P28 WP2-WP4 become the next agent-executable binding rows AFTER P35 is complete.**

---

## CAMPAIGN P34 — COMPLETE (ALL WPs LANDED; verified 2026-11-22T09:47:00Z)

**Declared:** 2026-11-22T07:44:24Z · **Campaign:** P34 "Wide-Universe Robustness & Strategy-Honesty Closure" · **Priority: HIGH** · **ALL WPs COMPLETE. Do NOT re-do it.**

| WP | Deliverable files | Status |
|---|---|---|
| WP0 — Multi-seed wide-universe equal-weight robustness study | `scripts/bab_p34_multiseed_robustness.py`, `tests/test_bab_p34_multiseed_robustness.py`, `research_state/bab_p34/multiseed_summary.json` | **COMPLETE** (19 tests PASS; `--check-multiseed-summary` PASS; ruff clean) |
| WP1 — Statistical falsification / honesty battery | `tests/test_bab_p34_honesty_battery.py` | **COMPLETE** (11 passed, 1 skipped) |
| WP2 — Documentation-integrity closure + summary + gate wire | README.md & docs/COVERAGE_NOTES.md pointer fixes, `tests/test_bab_p34_doc_pointer_guard.py`, `scripts/bab_gate.sh` hook | **COMPLETE** (7 passed, 1 skipped; gate wired) |

**P34 rationale:** closed the last agent-executable heavy gap — the wide 40-asset synthetic fixture was only exercised by P25 rank tests; P34 established multi-seed robustness of the shipped default (`weighting="equal"`, `beta_neutral=True`) across 8 seeds × 6 config cells (48 cells), with systematic neutrality invariants (model beta-neutral ≤1e-3, dollar-neutral ≤1e-9, realized β ≤0.15) verified at every cell, plus a statistical honesty battery (no-lookahead, no-profitable-claim, neutralization-effect, anti-victory) and a documentation-pointer-rot guard. **P34 is COMPLETE. Do NOT re-do it.**

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
- Editing any `research_state/bab_p20/**` … `research_state/bab_p34/**` artifact (frozen; P29 provenance ledger is frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20-P34 script (frozen).
- Editing any P25 WP0-WP2 artifact (including `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv`), any P26 artifact, any P27 WP0-WP3 artifact, or any P28 WP0-WP1 artifact, or any P30–P33 artifact (all closed and frozen).
- Hand-typing any number into a P25/P26/P27/P30–P34 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0 in any decision, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- Shipping a WP whose committed artifact contradicts its own acceptance threshold.
- **Network fetching of prices** (Coinbase returns 403 here; licensed CSV is maintainer-supplied).
- Reopening P19 annotation/coverage work, re-attempting CI workflow edits, adding new `P19-7` markers, broad refactors, or committing probe/debug scratch scripts.
- Creating parallel handoff docs (this file is the single source of truth).
- **Faking P29/P30/P31/P32/P33/P34 reproducibility** (hard-coding `sha256`/`summary` values, skipping the xproc/self-test/check-summary checks, or editing committed artifacts to force a green replay).
- **Re-doing P32, P33, P34, or any P20-P31 campaign** (all COMPLETE and frozen). The pipeline was: P30 → P31 → P32 → P33 → P34 → **P28 WP2-WP4 (maintainer-gated)**. Do NOT re-do P30, P31, P32, P33, or P34.
- **Idle docs-only churn while agent-executable work exists.** P35 is agent-executable and INCOMPLETE — a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure. A session may report an idle-wait state ONLY after P35 is complete (all WPs landed, full gate GREEN) AND P28 WP2-WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log (run `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` and include the log), not just prose.

---

## FUTURE AGENTS: READ THIS ONCE

**All agent-executable work through Campaign P34 is COMPLETE and frozen** (P20–P34). Campaign **P35 "Beta-Estimation Robustness & Signal-Stability Closure" is the binding, agent-executable, HEAVY row — ACTIVE right now.** P28 WP2-WP4 are the only other remaining binding rows and are **maintainer-gated** (require `workflows:write` for CI and licensed CSV for real-market data). Do NOT re-create or re-edit any P20–P34 file.

**Anti-idle rule:** a docs-only / handoff-only / plan-only / count-only commit is FORBIDDEN and counts as automatic failure when agent-executable work exists. **Agent-executable work DOES exist — P35 WP1 is the immediate next step.** A future session must execute P35 WP1→WP2→WP3 in order. Inner loop while iterating: `bash scripts/bab_quick.sh` + `python3 -m ruff check .` + `python3 -m pytest -q tests/test_bab_p35_*.py` + `python3 -m pytest -q tests/test_bab_p34_doc_pointer_guard.py` + `python3 -m pytest -q tests/test_bab_p31_registry_completeness.py tests/test_bab_p33_*.py tests/test_bab_p32_*.py tests/test_bab_p34_*.py` + `--check-multiseed-summary` + replay self-tests.

Do not re-open frozen P20–P34 artifacts (consumed read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` (never weakened) or flip `beta_neutral=True` / `weighting="equal"` off as the default. Never network-fetch prices. If this file says a WP is COMPLETE, it is COMPLETE; if it says a WP is maintainer-gated (currently **P28 WP2-WP4**), route it to the maintainer. **P35 is NOT maintainer-gated — it is agent-executable and must be executed.**