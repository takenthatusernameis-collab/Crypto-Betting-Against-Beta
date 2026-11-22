# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, or parallel task doc. If you find one, delete it and fold anything still true into this file.**

- **Timestamp (UTC):** 2026-11-22T23:32:55Z
- **HEAD:** `d6e901a`
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **The binding row is Campaign P38.** The provenance replay gate remains **RED on a freshly bootstrapped runner** (see INITIAL TASK); no WP0 remediation has landed yet. Restoring an *honest* GREEN is the blocking first task (P38 WP0), not a victory lap.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-22T23:32:55Z)

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. A RED provenance gate therefore undermines the repo's core claim and is the single most relevant thing to fix first.

**True baseline verified this session (fresh `bash scripts/bab_bootstrap.sh` → numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED):**
- GREEN: `ruff check .`; `bash scripts/bab_quick.sh` (299 passed); `scripts/bab_reconcile_gate.sh`; `scripts/bab_workflow_diagnostics.py --self-test` + `--analyze-ledger`; `scripts/bab_p34_multiseed_robustness.py --check-multiseed-summary`.
- **RED (all on a clean bootstrap, deterministic per-environment):**
  - `scripts/bab_replay_full.py --self-test` → `pass:false` (`research_state/bab_p27/reconciliation_e2e.json` `fills_checksum` drift).
  - `bash scripts/bab_replay_gate.sh` → exit 1 at its first step (so `bash scripts/bab_gate.sh` is RED).
  - `scripts/bab_p37_cost_surface.py --check-cost-surface-summary` → FAIL (byte mismatch).
  - `scripts/bab_p37_capacity.py --check-capacity-summary` → FAIL.
  - `scripts/bab_p37_turnover.py --check-turnover-summary` → FAIL.
  - `scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → DRIFT.
  - `scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json` → DRIFT (committed P33 manifest is missing the `docs/BAB_P37_DECISION.md` entry the registry now produces).

**FIRST ACTION (do this before anything else):** reproduce the RED, then fix it as P38 WP0.
```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .
bash scripts/bab_quick.sh
python3 scripts/bab_replay_full.py --self-test                 # expect pass:false -> RED
python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary   # expect FAIL
bash scripts/bab_replay_gate.sh                                # expect exit 1
```
Do **not** claim GREEN until `bab_replay_gate.sh` exits 0 AND every `--check-*-summary` is PASS.

> **CRITICAL GUARDRAIL — learned the hard way this session:** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` which those scripts do NOT accept). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, pass an explicit throwaway `--output /tmp/...` and diff first; restore any accidental mutation with `git checkout -- research_state/` immediately.

**Root cause (already localized this session — do not re-derive from scratch):** the committed artifacts were generated under an *older* numpy/pandas/scipy; `requirements.txt` pins nothing, so a fresh bootstrap computes slightly different float representations and every byte-identity check diverges. Two representative signatures:
- `cost_surface_summary.json`: `"sharpe": 0.0004581629459300575` (committed) vs `0.00045816294593005745` (fresh) — a one-ULP float-repr difference (1 extra digit → 1 byte).
- `reconciliation_e2e.json`: `fills_checksum` committed `560baed34c45dc0523d95f9078f280ee5b64938efd561f9c833262a9eec3a56e` vs fresh `2d651b00b6b103c171c90c258e99fc68f7ea9212a2b5c89abcf0bca235396127`.
- `doc_consistency_summary.json`: stale — missing the `BAB_P37_DECISION.md` replay-gated entry (a deterministic manifest-registration gap, independent of library versions).

Both are **library-version / derived-manifest reproducibility gaps, not logic regressions**. The prior "baseline GREEN" was true only on the machine that generated the artifacts; it is false on a clean runner.

**P38 WP0 (BLOCKING) — restore honest provenance reproducibility.** Never hand-edit a committed artifact to fake green (automatic failure per FORBIDDEN). Do it in two legitimate moves:
1. **Pin runtime deps (primary).** Bisect `numpy`/`pandas`/`scipy` in a scratch venv until `bab_replay_full.py --self-test` is `pass:true` AND all three P37 `--check-*-summary` are PASS, then pin those exact versions in `requirements.txt` + `pyproject.toml` and record the pinned set + verified date/HEAD in `docs/COVERAGE_NOTES.md`. This edits packaging metadata (not a frozen artifact) and makes the committed artifacts reproduce as-is.
2. **If no installable version reproduces them (derived-manifest / float-repr cleanup).** (a) Regenerate the P33 doc-consistency manifest and the P32 doc-replay summary through their legitimate `--summary-json` writers so they include the P37 entries, and (b) canonicalize float serialization (e.g. fixed-decimal rounding) in the generators before hashing so artifacts are version-independent — then regenerate each affected artifact **through its generator** and add a regression test that proves cross-run + documented-rounding byte-identity. This edits frozen P27/P32/P33/P37 artifacts *only* via the legitimate generator with a real determinism improvement (never a hand-forged hash).
- **Acceptance for WP0:** `bab_replay_gate.sh` exit 0; self-test `pass:true`; all three P37 `--check-*-summary` PASS; `--check-doc-summary` for both P32 and P33 PASS; `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` GREEN; a NEW cross-version determinism test committed. Do NOT lower `BAB_GATE_MIN_COVERAGE` and do NOT skip the replay gate.

**THEN proceed to Campaign P38 WP1→WP2→WP3 (defined below).** P38 is the mandatory heavy campaign so no future session can "idle-wait": P20–P37 established construction fidelity, OOS, and cost/capacity/turnover, but never closed the *statistical-significance-under-multiple-testing* loop nor characterized *tail risk* for a structurally short-volatility, short-high-beta book. That is real, heavy, offline, deterministic, agent-executable science.

**HARD GATES EVERY SESSION (repo root, in order — run after WP0 is green):**
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
`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. Inner loop while iterating P38:
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p38_*.py
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary   # WP1
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary              # WP2
python3 scripts/bab_replay_decisions.py --subset p38_decision.md            # WP3
python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary
```

---

# BINDING ROW = Campaign P38 — "Deflated Significance & Tail-Risk Closure" (+ P28 WP2-WP4 MAINTAINER-GATED)

**Declared:** 2026-11-22T23:32:55Z · **Campaign:** P38 "Deflated Significance & Tail-Risk Closure" · **Priority: HIGH** · **Status: ACTIVE — the sole agent-executable binding row.** P20–P37 COMPLETE and frozen; do NOT re-do them.

**Why P38 (prioritized by repo name):** the repo implements a *factor* strategy (Betting Against Beta). The decisive scientific questions for any factor are (1) *is the Sharpe statistically distinguishable from luck after accounting for how many configurations were tried?* and (2) *what does the left tail look like for a book that is structurally short high-beta / short volatility?* P20–P37 answered neither at the campaign level: P21 deflated only the narrow 40-candidate P20 grid, and no campaign characterized tail risk (grep: zero `CVaR`/`expected shortfall` anywhere in `scripts/`, `strategies/`, `docs/`, `research_state/`). P38 closes both, on the committed synthetic fixtures, fully offline and deterministic.

## P38 WP0 — Provenance reproducibility hardening (BLOCKING; see INITIAL TASK)
Make the ENTIRE provenance layer honestly GREEN on a clean bootstrap: `bab_replay_gate.sh` exit 0, `bab_replay_full.py --self-test` `pass:true`, all three P37 `--check-*-summary` PASS, and both P32/P33 `--check-doc-summary` PASS. Two legitimate routes (pin deps; or derived-manifest regeneration + float-serialization canonicalization), full detail + guardrails in INITIAL TASK. This is the bottleneck removal: without it the gate is RED and every later claim is unverifiable.

## P38 WP1 — Deflated / multiple-testing-adjusted significance over the FULL search
- New `scripts/bab_p38_deflated_significance.py` (deterministic, seeded; `--check-deflated-summary` mode).
- Enumerate the **total effective number of trials** actually searched across the campaign lineage: the P20 80-config in-sample grid + P21–P37 bakeoff/walk-forward/rank/estimator variants + P36 walk-forward folds. Derive a defensible `n_trials_total` from committed artifacts (read-only) — do not invent it.
- For the shipped default AND the best in-sample config, compute the **Deflated Sharpe Ratio (DSR)** and **Probabilistic Sharpe Ratio (PSR)** against `n_trials_total`, plus the trials-adjusted p-value and the minimum-backtest-length implication. Publish `research_state/bab_p38/deflated_summary.json` (+ `.md`).
- Honest verdict string is mandatory and may be negative: `SURVIVES_DEFLATION` or `DOES_NOT_SURVIVE_DEFLATION`. Every number must trace to a committed JSON leaf; synthetic-provenance caveat required.

## P38 WP2 — Tail-risk & drawdown characterization (CVaR / expected shortfall)
- New `scripts/bab_p38_tail_risk.py` (deterministic, seeded; `--check-tail-risk-summary` mode).
- On the P35/P37 40-asset wide synthetic fixture across the standard 8 seeds, compute per-seed: CVaR@95, CVaR@99, expected shortfall, worst-day return, return skew/kurtosis, tail asymmetry (left vs right), and drawdown-at-confidence. Assert the neutrality invariants (model beta ≤ 1e-3, dollar ≤ 1e-9, realized |beta| ≤ 0.15) hold at every cell. Publish `research_state/bab_p38/tail_risk_summary.json` (+ `.md`).
- This quantifies the short-vol / short-high-beta crash signature that P20–P37 never measured.

## P38 WP3 — Decision doc + documentation-integrity closure + gate wire
- `generate_p38_decision.py` + `docs/BAB_P38_DECISION.md` + `tests/test_bab_p38_decision_consistency.py` (zero hand-typed numbers; byte-identity `--check` on both summaries; explicit verdicts; AST no-harness scan; ruff clean).
- Register `p38_decision.md` in `scripts/bab_replay_decisions.py`; register `deflated_summary` + `tail_risk_summary` in `scripts/bab_replay_full.py` as `json_only, no_xproc` (gated out of the frozen P29 provenance ledger, exactly like the P35–P37 entries); wire a P38 block into `scripts/bab_gate.sh`; add `"P38"` to the pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py` (sanctioned guard maintenance, same as P35→P36→P37) and update its comment; keep README/COVERAGE_NOTES naming P38 as binding.

## P38 chartered acceptance thresholds
- WP0: `bab_replay_gate.sh` exit 0, self-test `pass:true`, full gate GREEN with `BAB_GATE_MIN_COVERAGE=100`, new determinism test committed.
- WP1: DSR + PSR computed for shipped default and best config over `n_trials_total`; explicit `SURVIVES_DEFLATION`/`DOES_NOT_SURVIVE_DEFLATION` verdict; all cells trace to committed JSON.
- WP2: CVaR@95/@99, ES, worst-day, skew/kurtosis, tail asymmetry, drawdown-at-confidence at every seed; neutrality invariants hold at every cell; JSON byte-identical.
- WP3: 100% coverage maintained; `tests/test_bab_p38_decision_consistency.py` green; replay registrations byte-identical; P38 block wired into `bab_gate.sh`.

## P38 file manifest (create these; do not create parallel docs)
- `scripts/bab_p38_deflated_significance.py`, `scripts/bab_p38_tail_risk.py`, `generate_p38_decision.py`
- `research_state/bab_p38/deflated_summary.json`, `research_state/bab_p38/tail_risk_summary.json`
- `docs/BAB_P38_DECISION.md`
- `tests/test_bab_p38_deflated_significance.py`, `tests/test_bab_p38_tail_risk.py`, `tests/test_bab_p38_decision_consistency.py`

---

## COMPLETED CAMPAIGNS (frozen — do NOT re-do)
- **CAMPAIGN P34 — COMPLETE** ("Wide-Universe Robustness & Strategy-Honesty Closure"): multi-seed robustness across 8 seeds × 6 config cells (48 cells) with neutrality invariants at every cell, plus the honesty battery and the doc pointer-rot guard. Frozen.
- **CAMPAIGN P35 — COMPLETE** ("Beta-Estimation Robustness & Signal-Stability Closure"): beta-estimator bakeoff + signal-stability on the wide universe. Frozen.
- **CAMPAIGN P36 — COMPLETE** ("Walk-Forward / Out-of-Sample Validation + Rank-Weighted Construction Closure"): walk-forward OOS harness + rank-weighted construction. Frozen.
- **CAMPAIGN P37 — COMPLETE** ("Cost-Aware Turnover & Capacity Closure"): cost surface × turnover, capacity break-even via bisection, hysteresis turnover guard on the wide synthetic fixture; verdict RETAIN the shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS). Frozen.
- **P20–P37 are all COMPLETE and frozen.** Do NOT re-do any of them.
- **P28 WP2–WP4 — MAINTAINER-GATED (not agent-executable):**
  - P28 WP2 — CI Gate Enforcement: needs `workflows:write` (repo token lacks it; agents cannot push `.github/workflows/main.yml`).
  - P28 WP3 — Real-Market Data Ingestion: needs a maintainer-supplied licensed CSV (Coinbase public API returns 403).
  - P28 WP4 — Live-Market Deployment Decision: needs WP2+WP3 + maintainer authorization.
  - Agents must NOT spin on, re-push, or re-edit CI workflows, licensed data, or live deployment. Route these to the maintainer.

### Bottlenecks removed this session
1. **False-GREEN dead-end.** The prior handoff told the next agent to "confirm GREEN then report idle-wait" — but on a clean bootstrap the replay gate is RED, so that instruction would have produced a false report or a confused spin. Removed: the handoff now states the true RED baseline and makes reproducibility the blocking P38 WP0.
2. **Idle-wait dead-end.** "Idle-wait is acceptable when P28 is gated" let a session do nothing. Removed: binding advances to P38, a mandatory multi-WP heavy campaign. A session may report idle-wait ONLY after the full gate is GREEN **and** P38 is complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P38 is active, so a handoff refresh without a landed fix is a failed session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p37/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20–P37 script (frozen).
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P37 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen).
- Hand-typing any number into a P20–P38 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P37 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The ONLY legitimate way to turn the RED replay gate green is a real determinism/pinning fix + a committed regression test (P38 WP0).
- **Re-doing P20–P37** (all COMPLETE and frozen).
- Creating parallel handoff docs (this file is the single source of truth).

---

## FUTURE AGENTS: READ THIS ONCE
P20–P37 are COMPLETE and frozen. **The binding row is P38.** On a clean bootstrap the ENTIRE provenance layer is **RED** — `reconciliation_e2e.json` `fills_checksum`, all three P37 `--check-*-summary`, and both P32/P33 `--check-doc-summary` fail byte-identity under the current unpinned numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1 (cross-version float-repr drift + a stale P33 manifest missing the P37 entry). The prior "baseline GREEN" was environment-specific. Your first job is P38 WP0: restore an *honest* GREEN (pin deps, or regenerate derived manifests + canonicalize float serialization + regression test; **never hand-edit an artifact to fake green**, and **never run a generator with bare/no args — it overwrites the committed artifact**). Then execute P38 WP1 (deflated/multiple-testing significance over the full search) → WP2 (tail-risk/CVaR characterization) → WP3 (decision doc + gate wire). Do not re-open frozen P20–P37 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. If P38 is complete AND the full gate is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log attached.