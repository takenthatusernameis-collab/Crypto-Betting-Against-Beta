# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T04:46:13Z
**Session:** Kilo General Agent Loop — P40 COMPLETE/FROZEN; **P41 WP1 COMPLETE; P41 WP2 OPEN**
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline (re-confirmed this session, HEAD `1df6b87`, working tree clean):**
`python3 -m ruff check .` GREEN; `bash scripts/bab_quick.sh` GREEN (195 passed);
`python3 scripts/bab_p41_stress.py --check-estimator-bakeoff` byte-identical PASS.
P20–P40 COMPLETE and FROZEN. `research_state/bab_p41/estimator_bakeoff.json` (+ `.md` sidecar)
and `scripts/bab_p41_stress.py` landed and verified — **P41 WP1 complete**. P41 WP2 is the
sole next workload; `generate_p41_decision.py` / `docs/BAB_P41_DECISION.md` do not exist yet (WP3).
P40 artifacts landed and verified: `research_state/bab_p40/meta_summary.json` + `.md`,
`scripts/bab_p40_meta_analysis.py`, `generate_p40_decision.py`, `docs/BAB_P40_DECISION.md`,
`tests/test_bab_p40_meta_analysis.py`, `tests/test_bab_p40_decision_consistency.py`.
P40 verdict: **DOES_NOT_REPLICATE** (0 of 4 fixtures replicate the P38 pooled verdict;
16 of 32 cells survive deflation over n_trials_total=552; neutrality holds everywhere).
**Supersedes:** all prior HANDOFF.md content. The former "terminal — no agent-executable
campaign remains" section is **RESCINDED** (it was the primary bottleneck; see below).

---

## READ FIRST — INITIAL TASK FOR THE NEXT SESSION (do this, in order)

**You are executing Campaign P41 "Non-Gaussian & Regime-Switching Synthetic Stress
Battery." This is the sole binding, fully agent-executable row. It is heavy by
construction and cannot be satisfied by re-running any frozen P20–P40 harness.**

The single source of truth for the campaign is **[`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md)**.
Read it end-to-end before writing code. Then execute its WPs in order:

### P41 WP1 — Estimator Bakeoff Under Non-Gaussian Idio (COMPLETE)

**Done.** `scripts/bab_p41_stress.py` created with `--check-estimator-bakeoff`;
`research_state/bab_p41/estimator_bakeoff.json` (schema `bab_p41.estimator_bakeoff/1`)
and `.md` sidecar landed and verified byte-identical. 160 cells (5 DGPs × 8 seeds ×
4 estimators), all ok, 0 errors, neutrality invariants hold at every cell.
Bakeoff verdict: `shrinkage_i0.3_t1.0_LEAST_BROKEN` (shrinkage intensity=0.3,
target=1.0 least-broken by non-Gaussianity among neutrality-passing estimators;
honest, negative-allowed ranking). Test file `tests/test_bab_p41_estimator_bakeoff.py`
added (pins schema, cell count, neutrality, DSR/PSR bounds, byte-identity, shas).

**Do not re-run or re-derive WP1.** Move to WP2.

### P41 WP2 — Five-DGP Stress Meta-Analysis (IMMEDIATE NEXT STEP; sole deliverable)

**Extend `scripts/bab_p41_stress.py` with `--check-stress-summary` that publishes
`research_state/bab_p41/stress_summary.json` (schema `bab_p41.stress_summary/1`)
plus `.md` sidecar.** The single source of truth for the full WP2 spec is
**[`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md)** — read its WP2 section
end-to-end before writing code.

WP2 must (per charter):
- Reuse the 160 WP1 cells (5 DGPs × 8 seeds × 4 estimators); per-cell DSR/PSR
  deflated over read-only n_trials_total=552, tail risk, and the three neutrality
  invariants; every cell labelled synthetic; not market evidence.
- Emit a consolidated verdict ∈ {`ROBUST_ACROSS_DGPS`, `FRAGILE_DGP_DEPENDENT`,
  `DOES_NOT_REPLICATE`} — honest, may be negative; **no seed/parameter tuning
  to chase a positive.**
- `--check-stress-summary` verifies byte-identical recomputation.

**Definition of done for the next session:** `python3 -m ruff check .` GREEN,
`python3 scripts/bab_p41_stress.py --check-stress-summary` PASS (byte-identical),
new artifact exists at `research_state/bab_p41/stress_summary.json` (+ `.md`).
Do not start WP3.

---

## PROJECT STATE SUMMARY (FROZEN P20–P40)

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| P38 WP1 | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default DSR=0.921; best in-sample DSR=0.944 |
| P39 WP1 | Regime-Conditional Deflation | **DOES_NOT_SURVIVE_IN_SOME_REGIME** | `bear_mid_vol` 3/8 survive; low-vol regimes 5–6/8 |
| P39 WP2 | Cross-Fixture Replication | **DOES_NOT_REPLICATE** | Only 3/8 survive; mean DSR 0.396 (< 0.5) |
| P39 WP0 | Full-Gate Close-Out (100% cov) | **GREEN** | `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0 |
| P36 | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Negative Sharpe, higher vol, worse maxDD. Dead end. |
| P40 WP0 | Multi-Fixture Meta-Analysis (4 fixtures, 32 cells) | **DOES_NOT_REPLICATE** | 0 of 4 fixtures replicate; 16/32 cells survive; neutrality holds |
| **P41 WP1** | **Estimator Bakeoff (5 DGPs, 160 cells)** | **COMPLETE** | shrinkage_i0.3_t1.0 least-broken; estimator_bakeoff.json landed, byte-identical, neutrality holds |
| **P41 WP2** | **Stress Meta-Analysis (5 DGPs, 160 cells)** | **OPEN — binding** | Next session; verdict ∈ {ROBUST_ACROSS_DGPS, FRAGILE_DGP_DEPENDENT, DOES_NOT_REPLICATE} |

**One-line verdict (P38–P40, frozen):** BAB survives pooled deflation on the primary
synthetic fixture (P38) but fails in high-vol regimes (P39 WP1), fails to replicate on a
second fixture (P39 WP2), and does not replicate across four independent Gaussian fixtures
(P40). The open question — does this hold under non-Gaussian dynamics? — is P41.

---

## BOTTLENECKS — STATUS (ALL RESOLVED FOR P41 EXECUTION)

| # | Bottleneck | Status | Resolution |
|---|------------|--------|------------|
| 1 | Full gate cannot complete in one tool window | **RESOLVED** | Use `scripts/bab_quick.sh` for inner loop; full gate only at P41 WP3 |
| 2 | P40 artifacts not landed | **RESOLVED** | All P40 WP0–WP3 artifacts exist, replay-registered, test-covered, gate-wired |
| 3 | Rank weighting | **CLOSED** | P36 proved strictly worse. Never reopen. |
| 4 | Regime coverage gap | **CLOSED** | All six regimes have `n_ok_cells = 8` in `research_state/bab_p39/regime_summary.json` |
| 5 | "Terminal / no campaign remains" framing | **REMOVED** | Prior HANDOFF guaranteed idle session. Rescinded. P41 is binding workload. |
| 6 | CI workflow enforcement | **EXTERNAL** | Maintainer-only (repo token lacks `workflows:write`). Do not burn session. |

---

## NEXT STATE (binding: P41)

P20–P40 are COMPLETE and FROZEN — do not reopen them. The next session executes
**P41 WP2** (stress meta-analysis) per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md);
P41 WP1 is complete and frozen. Any further work beyond P41
(real-data ingestion, CI enforcement, live deployment) is maintainer-gated and requires
explicit approval; do not invent additional agent-executable campaigns beyond P41 without
maintainer direction.

**Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Fast verify (baseline, before P41 WP2):** `python scripts/bab_p40_meta_analysis.py --check-meta-summary`
and `bash scripts/bab_quick.sh` (both GREEN). Do not run the full 56-minute gate to
re-verify frozen P20–P40; run full gate only at P41 WP3.

---

## SCIENTIFIC TARGET (why this is not busywork)

Every prior campaign (P20–P40) drew synthetic universes from **one i.i.d.-Gaussian family**
(`strategies/betting_against_beta/data.py`: `asset = beta*bm + N(0, idio)`). The P38
`SURVIVES_DEFLATION` and P40 `DOES_NOT_REPLICATE` verdicts were measured **only** on
Gaussian data. P41 measures whether the BAB estimator's behaviour is an artifact of the
Gaussian assumption, across Student-t, regime-switching, jump-diffusion, and stochastic-vol
DGPs. The verdict may be negative — that is a valid, publishable finding. **Do not tune
seeds/parameters to chase a positive. Do not flip the shipped default.**

---

## END OF HANDOFF — The next agent's first action is P41 WP2: extend
`scripts/bab_p41_stress.py` with `--check-stress-summary` and publish
`research_state/bab_p41/stress_summary.json` (schema `bab_p41.stress_summary/1`)
plus `.md` sidecar, per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md).