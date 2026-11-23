# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T01:21:44Z
- **HEAD:** 862102b
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **The binding row is Campaign P38.** The provenance replay gate is **RED on a freshly bootstrapped runner** (verified firsthand this session — see VERIFIED BASELINE). No WP0 remediation has landed. Restoring an *honest* GREEN is the blocking first task (P38 WP0), not a victory lap.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T01:21:03Z)

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. A RED provenance gate therefore undermines the repo's core claim and is the single most relevant thing to fix first.

**Prioritization by repo name:** the repo implements a *factor* strategy (Betting Against Beta). The decisive scientific questions for any factor are (1) *is the Sharpe statistically distinguishable from luck after accounting for how many configurations were tried?* and (2) *what does the left tail look like for a book that is structurally short high-beta / short volatility?* P20–P37 answered neither at the campaign level. Therefore the binding heavy campaign is **P38 "Deflated Significance & Tail-Risk Closure"**, and its **WP0 (provenance reproducibility) is the blocking first task** — nothing downstream is verifiable while the replay gate is RED.

## VERIFIED BASELINE — firsthand this session (HEAD `dee9131`, numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED)

I re-ran the gates directly. Do not trust any prior "GREEN" claim; trust these results:

- **GREEN (confirmed):** `ruff check .` → `All checks passed!` (exit 0). `bash scripts/bab_reconcile_gate.sh` → `GATE GREEN` (drift fails closed rc=2; clean + emit-only rc=0).
- **RED (confirmed, all on a clean bootstrap):**
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": false, "drift_detected": true, "pass": false}`.
  - `bash scripts/bab_replay_gate.sh` → stops at the self-test step (RED), so `bash scripts/bab_gate.sh` is RED too.
  - `scripts/bab_p37_cost_surface.py --check-cost-surface-summary` → FAIL (first diff byte 1990: expected `53` got `52`; length 101013 vs 101014).
  - `scripts/bab_p37_capacity.py --check-capacity-summary` → FAIL (first diff byte 15094; length 73648 vs 73645).
  - `scripts/bab_p37_turnover.py --check-turnover-summary` → FAIL (first diff byte 2066: expected `52` got `50`).
  - `scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json` → DRIFT.
  - `scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json` → DRIFT.

## FIRST ACTION (do this before anything else): reproduce, then fix as P38 WP0

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN (299 passed)
python3 scripts/bab_replay_full.py --self-test                           # expect pass:false -> RED
python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary     # expect FAIL
python3 scripts/bab_p37_capacity.py  --check-capacity-summary            # expect FAIL
python3 scripts/bab_p37_turnover.py  --check-turnover-summary            # expect FAIL
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json     # expect DRIFT
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json  # expect DRIFT
bash scripts/bab_replay_gate.sh                                          # expect exit 1
```
Do **not** claim GREEN until `bab_replay_gate.sh` exits 0 AND every `--check-*-summary` is PASS.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, pass an explicit throwaway `--output /tmp/...` and diff first; restore any accidental mutation with `git checkout -- research_state/` immediately.

## Root cause (localized — do not re-derive from scratch)

The committed artifacts were generated under an *older* numpy/pandas/scipy; `requirements.txt` pins nothing, so a fresh bootstrap computes slightly different float representations and every byte-identity check diverges. Two distinct failure classes:

1. **Cross-version float-repr drift (P37 cost_surface / capacity / turnover; P32 doc_replay_summary; P27 `costs_checksum`).** The underlying doubles differ by ~1 ULP between library versions (e.g. `...0.0004581629459300575` committed vs `...0.00045816294593005745` fresh → one extra digit → one extra byte). This is a numerical-library difference, not a JSON-formatting choice.

2. **Stale derived manifest (P33 doc_consistency_summary).** Confirmed firsthand: the committed manifest contains `BAB_P35_DECISION` and `BAB_P36_DECISION` but **NOT** `BAB_P37_DECISION.md`, which the registry now discovers. This is a deterministic manifest-registration gap, independent of library versions.

3. **NEW, IMPORTANT — P27 `fills_checksum` is NOT a JSON-formatting artifact.** `research_state/bab_p27/reconciliation_e2e.json` `fills_checksum` (committed `560baed34…`) is a **SHA-256 over 13,858 computed fill records** produced by the paper-trading execution engine + backtest. Because it hashes raw computed fills, **JSON float-rounding alone (route 2b) CANNOT fix it** — any ~1-ULP difference in a fill price/quantity changes the hash completely. It is only fixable by (a) pinning the exact library versions that reproduce the original fill stream, or (b) changing the fills hashing to quantize/round values before hashing (a legitimate determinism improvement) and regenerating through the generator with the P29 provenance ledger re-derived. This distinction is the key thing prior sessions missed: do not waste time trying to JSON-round your way past P27.

> **Adjacent-version claim is UNVERIFIED.** A prior session's note says installing `numpy==2.5.4` / `pandas==3.1.0` / `scipy==1.18.0` still failed. Prior sessions are unreliable — **verify empirically before trusting it.** The cheapest first probe is to test candidate pins against the *fastest* discriminating check in a scratch venv (do NOT mutate the main env or committed artifacts):
> ```bash
> python3 -m venv /tmp/pinprobe && /tmp/pinprobe/bin/pip -q install numpy==2.5.4 pandas==3.1.0 scipy==1.18.0
> /tmp/pinprobe/bin/python scripts/bab_p37_cost_surface.py --check-cost-surface-summary   # PASS = lead
> ```
> pip network access works in this environment (verified). But note: even a P37 PASS is **necessary but not sufficient** — the P27 `fills_checksum` must also reproduce, and it requires the *whole* pipeline to match, which adjacent pins are unlikely to fix. Treat any pin that does not make **all** of `replay_full --self-test` pass:true, all three P37 `--check-*-summary` PASS, and both P32/P33 `--check-doc-summary` PASS as a dead end.

## P38 WP0 (BLOCKING) — restore honest provenance reproducibility

Never hand-edit a committed artifact to fake green (automatic failure per FORBIDDEN). Choose the route that matches the root cause and verify the FULL acceptance set:

1. **Pin runtime deps (preferred when a version reproduces everything).** In a scratch venv, bisect `numpy`/`pandas`/`scipy` until `bab_replay_full.py --self-test` is `pass:true` **AND** all three P37 `--check-*-summary` PASS **AND** both P32/P33 `--check-doc-summary` PASS. Then pin those exact versions in `requirements.txt` + `pyproject.toml` and record the pinned set + verified date/HEAD in `docs/COVERAGE_NOTES.md`. This edits packaging metadata (not a frozen artifact) and makes the committed artifacts reproduce as-is. **Accept only a pin that turns the entire replay layer GREEN; a pin that fixes P37 but leaves P27 RED is not done.**
2. **If no installable version reproduces them (derived-manifest / float-repr cleanup).** (a) Regenerate the P33 doc-consistency manifest and the P32 doc-replay summary through their legitimate `--summary-json` writers so they include the P37 entries (fixes failure class 2). (b) Canonicalize float serialization (e.g. fixed-decimal rounding before hashing) in the generators so JSON artifacts are version-independent, AND — for P27 — quantize fill values before hashing; then regenerate each affected artifact **through its generator** (explicit `--output` to a temp path, diff, then move) and re-derive the P29 provenance ledger. Add a regression test that proves cross-run + documented-rounding byte-identity. This edits frozen P27/P32/P33/P37 artifacts *only* via the legitimate generator with a real determinism improvement (never a hand-forged hash).
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

# BINDING ROW = Campaign P38 — "Deflated Significance & Tail-Risk Closure" (+ P28 WP2–WP4 MAINTAINER-GATED)

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

### Bottlenecks removed (this and prior sessions)
1. **False-GREEN dead-end.** A prior handoff told the next agent to "confirm GREEN then report idle-wait" — but on a clean bootstrap the replay gate is RED, so that instruction would have produced a false report or a confused spin. Removed: the handoff now states the true, firsthand-verified RED baseline and makes reproducibility the blocking P38 WP0.
2. **Idle-wait dead-end.** "Idle-wait is acceptable when P28 is gated" let a session do nothing. Removed: binding advances to P38, a mandatory multi-WP heavy campaign. A session may report idle-wait ONLY after the full gate is GREEN **and** P38 is complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.
3. **NEW — "JSON-rounding will fix P27" misdirection.** Prior notes implied all drift was float-repr that could be rounded away. Confirmed wrong for P27: `fills_checksum` is a SHA-256 over 13,858 raw computed fills, so only an exact-version pin or a round-before-hash change to the fills generator can fix it. The route decision tree now states this explicitly so a session does not burn itself on route 2b for P27.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P38 is active, so a handoff refresh without a landed fix is a failed session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p37/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20–P37 script (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement, per WP0 route 2.
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
P20–P37 are COMPLETE and frozen. **The binding row is P38.** On a clean bootstrap the ENTIRE provenance layer is **RED** — I re-verified this firsthand on HEAD `6bb185b` with unpinned numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1: `reconciliation_e2e.json` self-test `pass:false`, all three P37 `--check-*-summary` FAIL (byte drift), and both P32/P33 `--check-doc-summary` DRIFT (P33 is genuinely missing the `BAB_P37_DECISION.md` entry). Your first job is P38 WP0: restore an *honest* GREEN — pin deps (verified to reproduce the *whole* replay layer, not just P37) **or** regenerate the derived manifests + canonicalize float/fill serialization + regression test. **Never hand-edit an artifact to fake green**, and **never run a generator with bare/no args — it overwrites the committed artifact**. Remember: P27's `fills_checksum` is a raw hash over 13,858 fills, so JSON float-rounding alone will NOT fix it — plan for a real version pin or a round-before-hash generator change. Then execute P38 WP1 (deflated/multiple-testing significance over the full search) → WP2 (tail-risk/CVaR characterization) → WP3 (decision doc + gate wire). Do not re-open frozen P20–P37 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. If P38 is complete AND the full gate is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log attached.