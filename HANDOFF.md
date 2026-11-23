# HANDOFF — Crypto-Betting-Against-Beta

**This is the ONLY durable handoff. Do not create any other `*HANDOFF*.md`, `NEXT_SESSION*.md`, `AGENT_*.md`, `NEXT_*.md`, or parallel task doc. If you find one, fold anything still true into this file and delete it.** Only `HANDOFF.md` is tracked; keep it that way.

- **Timestamp (UTC):** 2026-11-23T05:17:53Z
- **HEAD:** `586a2f7` (working tree clean; this handoff refresh only — no new campaign work landed since WP1).
- **Git state:** P20–P37 are COMPLETE and frozen (do NOT re-do them). **The binding row is Campaign P38.**
  - **P38 WP0 (provenance reproducibility) — DONE, GREEN.**
  - **P38 WP1 (deflated / multiple-testing-adjusted significance) — DONE** (landed in commit `a768c8b`: `scripts/bab_p38_deflated_significance.py` + `research_state/bab_p38/deflated_summary.{json,md}`; `--check-deflated-summary` is byte-identical).
  - **This session removed a hard-gate bottleneck WP1 left behind:** `ruff check .` was RED (9 errors in the new WP1 script — EN-DASH / MINUS-SIGN / unused `prov` / redundant `int(math.ceil(...))` / one long line). Fixed at the source and the two P38 artifacts regenerated (diff is purely cosmetic dash normalization). `ruff check .` is now **clean**.
  - **The blocking first task is now P38 WP2 (tail-risk / CVaR), then WP3 (decision doc + gate wire).** WP1 must NOT be redone — verify it and move on.

---

# INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (2026-11-23T05:17:53Z)

**Repo:** `Crypto-Betting-Against-Beta` — a market-neutral **Betting-Against-Beta** factor strategy for crypto (long low-beta, short high-beta, beta-neutral by construction). The repo's entire value proposition is *honest, reproducible, artifact-gated evidence*. **P38 WP0 is GREEN and WP1 is DONE** — do NOT redo either. **Your binding heavy work is WP2 (tail-risk / CVaR) → WP3 (decision doc + gate wire).** P20–P37 are COMPLETE and frozen; do NOT re-open them.

**Prioritization by repo name:** the repo implements a *factor* strategy (Betting Against Beta). The two decisive scientific questions for any factor are (1) *is the Sharpe statistically distinguishable from luck after accounting for how many configurations were tried?* — **answered by WP1** (verdict `SURVIVES_DEFLATION` over `n_trials_total=552`), and (2) *what does the left tail look like for a book that is structurally short high-beta / short volatility?* — **NOT yet answered; this is WP2**. P20–P37 never measured tail risk (zero `CVaR`/expected-shortfall anywhere). Therefore the remaining binding heavy campaign is **P38 WP2 → WP3**, in that order.

## VERIFIED BASELINE — firsthand this session (HEAD `a768c8b`, numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1, all UNPINNED)

Confirmed GREEN this session — trust these:

- **GREEN (confirmed):**
  - `python3 -m ruff check .` → `All checks passed!` (exit 0) — **after the WP1 ruff fix described above**.
  - `bash scripts/bab_quick.sh` → `quick preflight OK` (299 passed: 104 targeted trio + 195 smoke).
  - `python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary` → `PASS (byte-identical)`.
  - `python3 scripts/bab_replay_full.py --self-test` → `{"self_test": true, "clean_ok": true, "drift_detected": true, "pass": true}`.
  - `python3 scripts/bab_replay_decisions.py --self-test` → `pass:true`.
- **NOT YET RUN this session (slow — do NOT treat as a blocker for WP2/WP3):** the full `bash scripts/bab_gate.sh` (runs ~5,800 tests + `--xproc` cross-process ledger check, ~hours for 27 artifacts × 2 subprocess builds). This is the **WP0 close-out** item; run it to completion on a session with a large time budget *after* WP2/WP3 land. It does NOT block progress on WP2/WP3 — use the cheap inner loop below while iterating.

## FIRST ACTION (verify baseline, then start WP2)

```bash
bash scripts/bab_bootstrap.sh
python3 -m ruff check .                                                  # GREEN
bash scripts/bab_quick.sh                                                # GREEN (299 passed)
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary # expect PASS (byte-identical)
python3 scripts/bab_replay_full.py --self-test                           # expect pass:true
python3 scripts/bab_replay_decisions.py --self-test                      # expect pass:true
python3 scripts/bab_p37_cost_surface.py --check-cost-surface-summary     # expect PASS
python3 scripts/bab_p37_capacity.py  --check-capacity-summary            # expect PASS
python3 scripts/bab_p37_turnover.py  --check-turnover-summary            # expect PASS
python3 scripts/bab_p36_rank_weighted.py --check-rank-weighted-summary   # expect PASS
```
If any of the above is RED, a regression was introduced — bisect with `git log`/`git diff` (the WP1 ruff fix touched only `scripts/bab_p38_deflated_significance.py` + the two `research_state/bab_p38/` artifacts); do NOT hand-edit artifacts to force green.

> **CRITICAL GUARDRAIL — learned the hard way (still true):** NEVER run a generator script with bare/no args or an unrecognized flag (e.g. `python3 scripts/bab_p37_cost_surface.py`, or `--summary-json` where those scripts do NOT accept it). Many generators **write to the committed artifact path by default**, silently overwriting frozen `research_state/**` files and turning a RED gate falsely GREEN. To verify, use ONLY the `--check-*` flags. To intentionally regenerate during a fix (as done for WP1 this session), run the generator (it writes the active P38 path only), then `git diff` to confirm the change is intentional, and restore any accidental mutation of a frozen artifact with `git checkout -- research_state/` immediately.

## How WP0 was fixed (for context — do NOT redo; reuse the pattern if new drift appears)

The committed artifacts had been generated under an *older* numpy/pandas/scipy; `requirements.txt` pins nothing, so a fresh bootstrap computed slightly different floats and every byte-identity check diverged. Pinning adjacent versions was empirically verified to STILL FAIL (identical byte diff), so the fix was route 2 (canonicalization), not pinning:

1. **Signed-zero normalization** (`-0.0` vs `0.0` — `==` but `json.dumps` emits different bytes): added `+ 0.0` to the `round(...)` in the `_clean` helpers of `bab_walk_forward_rank`, `bab_promotion_bakeoff`, `bab_signal_null_battery`, `bab_p26_regime_stress`, `bab_rank_capacity`, `bab_rank_eval`. Regenerated the 6 P21/P25/P26 artifacts.
2. **Realized-beta / metric ULP rounding**: rounded `realized_beta` to 12 decimals in `bab_p37_cost_surface/capacity/turnover` and the float metrics in `bab_p36_rank_weighted`; rounded the raw `gross_mean_active`/`short_leg_beta_mean`/`min_leg_beta` in `bab_rank_eval`.
3. **P27 `fills_checksum` (raw SHA-256 over computed fills)**: added a `_canonicalize` (round floats to 12 decimals + normalize `-0.0`) inside `strategies/betting_against_beta/reconciliation.py::_checksum`.
4. **Cascade**: regenerated `docs/BAB_P25_DECISION.md` + `docs/BAB_P26_DECISION.md` through their generators; regenerated `bab_p32`/`bab_p33` manifests; re-derived the P29 ledger (27/27 `replay_ok:true`).

**Pattern for any NEW drift:** identify whether it is signed-zero (`-0.0`/`0.0`), ~1-ULP float (round to 12 decimals at the source), or a raw hash over floats (canonicalize before hashing). Regenerate through the generator (confirm diff, then keep), then re-derive the P29 ledger and cascade-regenerate any decision doc that embeds the changed artifact.

## HARD GATES EVERY SESSION (repo root, in order — run after WP0 is green)

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
`scripts/bab_gate.sh` invokes `scripts/bab_replay_gate.sh` at the end, so the replay check cannot be skipped by running the full gate alone. **Inner loop while iterating P38 (use this, NOT the full gate, to keep sessions fast):**
```bash
bash scripts/bab_quick.sh
python3 -m ruff check .
python3 -m pytest -q tests/test_bab_p38_*.py
python3 scripts/bab_p38_deflated_significance.py --check-deflated-summary   # WP1 (DONE)
python3 scripts/bab_p38_tail_risk.py --check-tail-risk-summary              # WP2 (BLOCKING)
python3 scripts/bab_replay_decisions.py --subset p38_decision.md            # WP3
python3 scripts/bab_replay_full.py --subset deflated_summary,tail_risk_summary
```

---

# BINDING ROW = Campaign P38 — "Deflated Significance & Tail-Risk Closure" (+ P28 WP2–WP4 MAINTAINER-GATED)

**Declared:** 2026-11-22T23:32:55Z · **Campaign:** P38 "Deflated Significance & Tail-Risk Closure" · **Priority: HIGH** · **Status: ACTIVE — the sole agent-executable binding row.** P20–P37 COMPLETE and frozen; do NOT re-do them.

**Why P38 (prioritized by repo name):** the repo implements a *factor* strategy (Betting Against Beta). The decisive scientific questions for any factor are (1) *is the Sharpe statistically distinguishable from luck after accounting for how many configurations were tried?* and (2) *what does the left tail look like for a book that is structurally short high-beta / short volatility?* WP1 closed (1); WP2 closes (2); WP3 binds them into a decision doc and the gate. P20–P37 answered neither at the campaign level.

## P38 WP0 — Provenance reproducibility hardening (DONE — GREEN)
The entire provenance layer is GREEN on a clean bootstrap. Fix was route 2 (canonicalization): signed-zero normalization + 12-decimal rounding + round-before-hash in `reconciliation.py::_checksum`, with all affected artifacts regenerated through their generators. **Do NOT redo WP0.** The only remaining WP0 verification is the full `bash scripts/bab_gate.sh` (slow cross-process `--xproc`/`--check-provenance`) — run it on a large-time-budget session. A cross-version determinism regression test was NOT yet added — add one (proves round-before-hash + signed-zero normalization byte-identity) as part of WP0 close-out if you touch this layer.

## P38 WP1 — Deflated / multiple-testing-adjusted significance (DONE — verified byte-identical)
- `scripts/bab_p38_deflated_significance.py` (deterministic, seeded; `--check-deflated-summary`).
- Enumerates `n_trials_total = 552` read-only from committed P20/P35/P36/P37 artifacts (P20 grid 80 + P35 estimator 80 + P35 signal-stability 96 + P36 rank-weighted 8 + P36 walk-forward 80 + P37 cost-surface 192 + P37 capacity 8 + P37 turnover 8).
- Shipped default: DSR=0.920930, PSR=1.0, trials-adjusted p=0.079070. Best in-sample config (beta_window=180, quantile=0.20): DSR=0.944379, PSR=1.0, trials-adjusted p=0.055621. Campaign verdict **`SURVIVES_DEFLATION`** (both DSR ≥ 0.5 over n_trials=552).
- Artifacts: `research_state/bab_p38/deflated_summary.json` + `.md`. **Do NOT redo.** Note for WP3: the trials-adjusted p-values (0.079 / 0.056) are *marginal* (<0.10 but >0.05) — the decision doc must state this honestly rather than overclaiming.

## P38 WP2 — Tail-risk & drawdown characterization (CVaR / expected shortfall) — **BLOCKING FIRST TASK**
- New `scripts/bab_p38_tail_risk.py` (deterministic, seeded; `--check-tail-risk-summary` mode; mirror the WP1 script's structure, `--output`/`--check-*` conventions, and provenance block).
- On the P35/P37 40-asset wide synthetic fixture across the standard 8 seeds, compute per-seed: **CVaR@95, CVaR@99, expected shortfall, worst-day return, return skew/kurtosis, tail asymmetry (left vs right), and drawdown-at-confidence**. Assert the neutrality invariants (model beta ≤ 1e-3, dollar ≤ 1e-9, realized |beta| ≤ 0.15) hold at every cell.
- Publish `research_state/bab_p38/tail_risk_summary.json` (+ `.md`). Every number must trace to a committed JSON leaf; synthetic-provenance caveat required. This quantifies the short-vol / short-high-beta crash signature that P20–P37 never measured.
- Wire-in targets (do in WP3, not WP2): register `tail_risk_summary` in `scripts/bab_replay_full.py` as `json_only, no_xproc`.

## P38 WP3 — Decision doc + documentation-integrity closure + gate wire
- `generate_p38_decision.py` + `docs/BAB_P38_DECISION.md` + `tests/test_bab_p38_decision_consistency.py` (zero hand-typed numbers; byte-identity `--check` on both summaries; explicit verdicts; AST no-harness scan; ruff clean). Reuse `generate_p37_decision.py` + `tests/test_bab_p37_decision_consistency.py` as the template.
- Register `p38_decision.md` in `scripts/bab_replay_decisions.py` (mirror the `p37_decision.md` entry at ~line 107: `{"name": "p38_decision.md", "module": "generate_p38_decision", ...}` with `REPORT_PATH = docs/BAB_P38_DECISION.md`).
- Register `deflated_summary` + `tail_risk_summary` in `scripts/bab_replay_full.py` as `json_only, no_xproc` (gated out of the frozen P29 provenance ledger, exactly like the P35–P37 entries at ~line 123–133).
- Wire a P38 block into `scripts/bab_gate.sh` (mirror the P37 block at ~line 205–214: `--check-tail-risk-summary`, `--check-deflated-summary`, and the P38 decision-consistency pytest).
- The pointer-guard allow-list in `tests/test_bab_p34_doc_pointer_guard.py` **already includes `"P38"`** (line ~206) — no change needed; just confirm it stays green.
- Keep README / `docs/COVERAGE_NOTES.md` naming P38 as binding.

## P38 chartered acceptance thresholds
- WP0 (DONE): `bab_replay_full.py --self-test` `pass:true`, all P34–P37 `--check-*` PASS, P32/P33 `--check-doc-summary` OK, decisions replay OK, P29 ledger 27/27 `replay_ok:true`. Remaining: run the full `bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100` to completion on a large-time-budget session; add a cross-version determinism regression test if you touch the provenance layer.
- WP1 (DONE): DSR + PSR for shipped default and best config over `n_trials_total=552`; explicit `SURVIVES_DEFLATION` verdict; all cells trace to committed JSON; `--check-deflated-summary` byte-identical; ruff clean.
- WP2 (BLOCKING): CVaR@95/@99, ES, worst-day, skew/kurtosis, tail asymmetry, drawdown-at-confidence at every seed; neutrality invariants hold at every cell; JSON byte-identical (`--check-tail-risk-summary` PASS); ruff clean.
- WP3: 100% coverage maintained; `tests/test_bab_p38_decision_consistency.py` green; replay registrations byte-identical; P38 block wired into `bab_gate.sh`; `ruff check .` clean.

## P38 file manifest
- **Exist (WP1, DONE):** `scripts/bab_p38_deflated_significance.py`, `research_state/bab_p38/deflated_summary.json`, `research_state/bab_p38/deflated_summary.md`.
- **Create (WP2, BLOCKING):** `scripts/bab_p38_tail_risk.py`, `research_state/bab_p38/tail_risk_summary.json` (+ `.md`), `tests/test_bab_p38_tail_risk.py`.
- **Create (WP3):** `generate_p38_decision.py`, `docs/BAB_P38_DECISION.md`, `tests/test_bab_p38_decision_consistency.py`; edit `scripts/bab_replay_full.py`, `scripts/bab_replay_decisions.py`, `scripts/bab_gate.sh`.
- Do not create parallel docs.

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
1. **RED ruff gate left by WP1 (primary bottleneck this session) — REMOVED.** The WP1 commit (`a768c8b`) landed the deflated script + artifacts but left `ruff check .` RED with 9 errors (EN-DASH `–`/MINUS-SIGN `−` in strings/comments/docstrings, an unused `prov` local, a redundant `int(math.ceil(...))`, and one E501 long line). Because `ruff check .` is the first hard gate, the next session would have been blocked before doing any work. Fixed at the source in `scripts/bab_p38_deflated_significance.py` (ASCII hyphens, removed dead `prov`, removed redundant `int()`, wrapped the long line) and regenerated `research_state/bab_p38/deflated_summary.{json,md}` through the generator — the artifact diff is purely cosmetic dash normalization, and `--check-deflated-summary` is byte-identical again. `ruff check .` is now clean.
2. **Stale handoff misdirecting to WP1 — REMOVED.** The prior handoff named WP1 as the blocking first task, but WP1 is now done. This handoff advances the binding row to WP2 → WP3 so the next session starts on real work instead of redoing WP1.
3. **RED provenance gate (prior) — REMOVED.** On a clean bootstrap the entire replay layer was RED; a prior session landed the full determinism fix (signed-zero `+0.0`, 12-decimal rounding, round-before-hash). Now GREEN.
4. **False-GREEN dead-end (prior).** A prior handoff told the next agent to "confirm GREEN then report idle-wait" — but the replay gate was RED. Removed: the handoff now states the true, firsthand-verified baseline.
5. **Idle-wait dead-end (prior).** "Idle-wait is acceptable when P28 is gated" let a session do nothing. Removed: binding advances to P38, a mandatory multi-WP heavy campaign. A session may report idle-wait ONLY after the full gate is GREEN **and** P38 WP2+WP3 are complete **and** P28 WP2–WP4 remain maintainer-gated — and that report MUST include a fresh full-gate GREEN log, not prose.
6. **"JSON-rounding will fix P27" misdirection (prior, resolved).** P27's `fills_checksum` was fixed via `_canonicalize` (round floats + normalize `-0.0`) inside `reconciliation.py::_checksum`.

---

## FORBIDDEN (automatic failure)
- Handoff-only / docs-only / gate-only / count-only / analysis-only commits **while agent-executable work exists** (P38 WP2–WP3 are active and heavy, so a handoff refresh without landed WP2/WP3 progress is a failed session).
- Editing any `research_state/bab_p20/**` … `research_state/bab_p37/**` artifact (frozen; P29 provenance ledger frozen too), `docs/BAB_RESEARCH_REPORT.md`, or any P20–P37 script (frozen). The ONLY exception is a legitimate regeneration *through the generator* with a real determinism improvement (the pattern used for WP0; reuse it only if NEW drift appears).
- Editing any P25 WP0–W2 / P26 / P27 WP0–W3 / P28 WP0–W1 / P30–P37 artifact, or `tests/fixtures/wide_bab_universe.csv` / `real_market_prices.csv` (frozen).
- Hand-typing any number into a P20–P38 report, charter, or verdict that is not a committed JSON field.
- Weakening `rank_min_leg_beta=0.20` / `rank_max_gross=4.0` below 0.20 / 4.0, or flipping `beta_neutral=True` / `weighting="equal"` off as the shipped default.
- Describing the synthetic wide universe or the synthetic 9-asset fixture as real market data, or publishing a Sharpe without the provenance caveat.
- Deleting, skipping, `xfail`-ing, or loosening existing tests.
- **Network fetching of prices** (Coinbase returns 403; licensed CSV is maintainer-supplied).
- **Faking P29–P37 reproducibility** (hard-coding `sha256`/`summary`, skipping xproc/self-test/check-summary, or hand-editing committed artifacts to force a green replay). The legitimate way to handle any new drift is the documented determinism pattern (round-before-hash / signed-zero normalization via the generator), never a hand-forged hash.
- **Re-doing P20–P37** (all COMPLETE and frozen), **re-doing P38 WP0** (DONE), or **re-doing P38 WP1** (DONE — verify with `--check-deflated-summary`, do not redo).
- Creating parallel handoff docs (this file is the single source of truth).

---

## FUTURE AGENTS: READ THIS ONCE
P20–P37 are COMPLETE and frozen. **The binding row is P38.** **P38 WP0 is GREEN** and **P38 WP1 (deflated significance) is DONE** (`--check-deflated-summary` byte-identical, verdict `SURVIVES_DEFLATION` over `n_trials_total=552`). A prior session landed the WP1 script + artifacts; this session removed the RED-ruff bottleneck it left (now `ruff check .` is clean) and refreshed this handoff. **Your first job is P38 WP2 (tail-risk / CVaR)** → WP3 (decision doc + gate wire). Before starting, verify the baseline with the FIRST ACTION commands (all should be GREEN); if any is RED, a regression was introduced — bisect, do NOT hand-edit artifacts. **Never hand-edit an artifact to fake green**, and **never run a generator with bare/no args — it overwrites the committed artifact**. Do not re-open frozen P20–P37 artifacts (read-only). Do not chase `test_null_stats_consistent` (pre-existing, certified unrelated, read-only). Do not edit `rank_min_leg_beta`/`rank_max_gross` or flip the shipped default. Never network-fetch prices. If P38 WP2+WP3 are complete AND the full gate (`bash scripts/bab_gate.sh` with `BAB_GATE_MIN_COVERAGE=100`) is GREEN AND P28 WP2–WP4 remain maintainer-gated, you may report idle-wait — but only with a fresh full-gate GREEN log attached.