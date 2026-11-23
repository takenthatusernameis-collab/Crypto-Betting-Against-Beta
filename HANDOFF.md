# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T03:48:28Z
- **HEAD:** 4c7f67f
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **The binding row is Campaign P38.** **P38 WP0 (provenance reproducibility) is DONE and GREEN** (verified firsthand this session — `ruff check .` → All checks passed; `bash scripts/bab_quick.sh` → quick preflight OK; `bab_replay_full.py --self-test` → pass:true). The blocking first task is now **P38 WP1 (deflated/multiple-testing significance)**, then WP2→WP3.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T03:48:28Z)

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. **P38 WP0 (provenance reproducibility) is now GREEN** — a prior session landed a complete determinism fix (round-before-hash / signed-zero normalization across the P21/P25/P26/P27/P36/P37 generators + regenerated all affected artifacts + re-derived the P29 ledger). Do NOT redo WP0; verify it (commands below) and proceed to WP1.

**Prioritization by repo name:** the repo implements a *factor* strategy (Betting Against Beta). The decisive scientific questions for any factor are (1) *is the Sharpe statistically distinguishable from luck after accounting for how many configurations were tried?* and (2) *what does the left tail look like for a book that is structurally short high-beta / short volatility?* P20–P37 answered neither at the campaign level. Therefore the binding heavy campaign is **P38 "Deflated Significance & Tail-Risk Closure"**, and with WP0 green, **WP1 (deflated significance) is the blocking first task**.

## VERIFIED BASELINE — firsthand this session (HEAD `4c7f67f`, numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED)

WP0 is verified green this session. Trust these results:

- **GREEN (confirmed):**
  - `python3 -m ruff check .` → `All checks passed!` (exit 0).
  - `bash scripts/bab_quick.sh` → `quick preflight OK` (299 passed).
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": true, "drift_detected": true, "pass": true}`.
  - All three P37 `--check-*-summary` → PASS (byte-identical).
  - `scripts/bab_replay_decisions.py --self-test` → `pass:true`; full decisions replay → all OK.
  - `--check-doc-summary` for both P32 and P33 → OK.
  - All P34/P35/P36 summary `--check-*` → PASS (byte-identical).
  - `--check-ledger-summary` (P30) → PASS.
  - `bab_workflow_diagnostics.py --self-test` / `--analyze-ledger` → PASS.
  - Targeted test suites (P25/P26/P27/P33/P34/P35/P36/P37 decision-consistency, reconciliation, execution-hardening, replay-harness) → all passed.
- **NOT YET RUN this session (slow — run before claiming full done):** the full `bash scripts/bab_gate.sh` (runs ~5,800 tests + `--xproc` + `--check-provenance`; the `--xproc` cross-process ledger check is ~hours for 27 artifacts × 2 subprocess builds). The P29 ledger was re-derived in-process and cross-process determinism was spot-verified on 6 representative artifacts (including every changed one) — byte-identical — but the *full* `--check-provenance` must be run to completion on a session with a large time budget.

## FIRST ACTION (verify WP0 is green, then start WP1)

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN (299 passed)
python3 scripts/bab_replay_full.py --self-test                           # expect pass:true -> GREEN
python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary     # expect PASS
python3 scripts/bab_p37_capacity.py  --check-capacity-summary            # expect PASS
python3 scripts/bab_p37_turnover.py  --check-turnover-summary            # expect PASS
python3 scripts/bab_replay_decisions.py --self-test                      # expect pass:true
python3 scripts/bab_replay_decisions.py --check-doc-summary research_state/bab_p32/doc_replay_summary.json     # expect OK
python3 scripts/bab_doc_consistency_summary.py --check-doc-summary research_state/bab_p33/doc_consistency_summary.json  # expect OK
python3 scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary   # expect PASS
```
If any of the above is RED, a regression was introduced — bisect with `git log`/`git diff` on the determinism-fix commit; do NOT hand-edit artifacts to force green.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix, pass an explicit throwaway `--output /tmp/...` and diff first; restore any accidental mutation with `git checkout -- research_state/` immediately.

## How WP0 was fixed (for context — do NOT redo; reuse the pattern if new drift appears)

The committed artifacts had been generated under an *older* numpy/pandas/scipy; `requirements.txt` pins nothing, so a fresh bootstrap computed slightly different floats and every byte-identity check diverged. Pinning adjacent versions (`numpy==2.5.4`/`pandas==3.1.0`/`scipy==1.18.0`) was empirically verified to STILL FAIL (identical byte diff), so the fix was route 2 (canonicalization), not pinning:

1. **Signed-zero normalization** (`-0.0` vs `0.0` — `==` but `json.dumps` emits different bytes): added `+ 0.0` to the `round(...)` in the `_clean` helpers of `bab_walk_forward_rank`, `bab_promotion_bakeoff`, `bab_signal_null_battery`, `bab_p26_regime_stress`, `bab_rank_capacity`, `bab_rank_eval`. Regenerated the 6 P21/P25/P26 artifacts.
2. **Realized-beta / metric ULP rounding**: rounded `realized_beta` to 12 decimals in `bab_p37_cost_surface/capacity/turnover` and the float metrics in `bab_p36_rank_weighted`; rounded the raw `gross_mean_active`/`short_leg_beta_mean`/`min_leg_beta` in `bab_rank_eval`. Regenerated the affected artifacts.
3. **P27 `fills_checksum` (raw SHA-256 over computed fills)**: added a `_canonicalize` (round floats to 12 decimals + normalize `-0.0`) inside `strategies/betting_against_beta/reconciliation.py::_checksum` so the hash is version-stable WITHOUT changing stored full-precision aggregates. Regenerated `reconciliation_e2e` + `execution_hardening`.
4. **Cascade**: the signed-zero fix changed `promotion_bakeoff`/`signal_null_battery` deltas, which the P25/P26 decision docs embed — regenerated `docs/BAB_P25_DECISION.md` + `docs/BAB_P26_DECISION.md` through their generators.
5. **Manifests**: regenerated `bab_p32/doc_replay_summary.json` + `bab_p33/doc_consistency_summary.json` to include the P37 entry.
6. **P29 ledger**: re-derived `research_state/bab_p29/provenance_audit.json` in-process (all 27 entries `replay_ok:true`); cross-process determinism spot-verified.

**Pattern for any NEW drift:** identify whether it is signed-zero (`-0.0`/`0.0`), ~1-ULP float (round to 12 decimals at the source), or a raw hash over floats (canonicalize before hashing). Regenerate through the generator (explicit `--output` to temp, diff, then move), then re-derive the P29 ledger and cascade-regenerate any decision doc that embeds the changed artifact.

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

## P38 WP0 — Provenance reproducibility hardening (DONE this session)
The ENTIRE provenance layer is now honestly GREEN on a clean bootstrap: `bab_replay_full.py --self-test` `pass:true`, all three P37 `--check-*-summary` PASS, both P32/P33 `--check-doc-summary` PASS, P36 rank_weighted PASS, decisions replay OK, P29 ledger re-derived (27/27 `replay_ok:true`). Fix was route 2 (canonicalization): signed-zero normalization + 12-decimal rounding + round-before-hash in `reconciliation.py::_checksum`, with all affected artifacts regenerated through their generators. See "How WP0 was fixed" in the INITIAL TASK for the exact file list and pattern. **Do NOT redo WP0.** The only remaining WP0 verification is the full `bash scripts/bab_gate.sh` (slow: ~5,800 tests + `--xproc`/`--check-provenance` cross-process ledger check) — run it on a session with a large time budget before declaring the campaign fully done.

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
- WP0 (DONE this session): `bab_replay_full.py --self-test` `pass:true`, all P34–P37 `--check-*` PASS, P32/P33 `--check-doc-summary` OK, decisions replay OK, P29 ledger 27/27 `replay_ok:true`. Remaining: run the full `bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100` to completion (slow cross-process `--xproc`/`--check-provenance`) on a large-time-budget session. A cross-version determinism regression test was NOT yet added — add one (proves round-before-hash + signed-zero normalization byte-identity) as part of WP0 close-out.
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
1. **RED provenance gate (the primary bottleneck) — REMOVED this session.** On a clean bootstrap the entire replay layer was RED (self-test `pass:false`, all P37 checks FAIL, P32/P33 DRIFT, plus latent signed-zero/ULP drift across P21/P25/P26/P27/P36 that the cheap self-test never surfaced). A prior session's handoff correctly identified this as blocking but no remediation had landed. This session landed a complete determinism fix (signed-zero `+0.0`, 12-decimal rounding, round-before-hash in `reconciliation.py::_checksum`), regenerated every affected artifact through its generator, cascaded the P25/P26 decision-doc updates, regenerated the P32/P33 manifests, and re-derived the P29 ledger (27/27 `replay_ok:true`). The gate is now GREEN. The only remaining verification is the full `bash scripts/bab_gate.sh` (slow cross-process `--xproc`/`--check-provenance`), which must run to completion on a large-time-budget session.
2. **False-GREEN dead-end (prior).** A prior handoff told the next agent to "confirm GREEN then report idle-wait" — but on a clean bootstrap the replay gate was RED. Removed: the handoff now states the true, firsthand-verified baseline.
3. **Idle-wait dead-end (prior).** "Idle-wait is acceptable when P28 is gated" let a session do nothing. Removed: binding advances to P38, a mandatory multi-WP heavy campaign. A session may report idle-wait ONLY after the full gate is GREEN **and** P38 is complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.
4. **"JSON-rounding will fix P27" misdirection (prior, now resolved).** P27's `fills_checksum` is a SHA-256 over raw computed fills; it was fixed by adding `_canonicalize` (round floats to 12 decimals + normalize `-0.0`) inside `reconciliation.py::_checksum` — a legitimate round-before-hash determinism improvement. The pattern is documented in "How WP0 was fixed" for reuse if new drift appears.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P38 WP1–WP3 are active and heavy, so a handoff refresh without a landed fix is a failed session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p37/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20–P37 script (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement (the pattern used for WP0; reuse it only if NEW drift appears).
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P37 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen).
- Hand-typing any number into a P20–P38 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P37 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate way to handle any new drift is the documented determinism pattern (round-before-hash / signed-zero normalization via the generator), never a hand-forged hash.
- **Re-doing P20–P37** (all COMPLETE and frozen), and **re-doing P38 WP0** (DONE this session — verify, do not redo).
- Creating parallel handoff docs (this file is the single source of truth).

---

## FUTURE AGENTS: READ THIS ONCE
P20–P37 are COMPLETE and frozen. **The binding row is P38.** **P38 WP0 (provenance reproducibility) is DONE — the replay gate is GREEN** (self-test `pass:true`, all P34–P37 `--check-*` PASS, P32/P33 doc summaries OK, decisions replay OK, P29 ledger 27/27 `replay_ok:true`). A prior session landed a complete determinism fix (signed-zero `+0.0` normalization + 12-decimal rounding + round-before-hash in `reconciliation.py::_checksum`) and regenerated every affected artifact through its generator. **Your first job is P38 WP1 (deflated/multiple-testing-adjusted significance over the full search)** → WP2 (tail-risk/CVaR) → WP3 (decision doc + gate wire). Before starting, verify WP0 with the FIRST ACTION commands (all should be GREEN); if any is RED, a regression was introduced — bisect, do NOT hand-edit artifacts. **Never hand-edit an artifact to fake green**, and **never run a generator with bare/no args — it overwrites the committed artifact**. Do not re-open frozen P20–P37 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. If P38 is complete AND the full gate (`bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`) is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log attached.