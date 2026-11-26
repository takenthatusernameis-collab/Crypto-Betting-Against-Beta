# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T04:43:19Z
**Session:** Kilo General Agent Loop — P40 COMPLETE/FROZEN; **P41 binding campaign OPENED**
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline (re-confirmed this session, HEAD `1df6b87`, working tree clean):**
`python3 -m ruff check .` GREEN; `bash scripts/bab_quick.sh` GREEN (299 passed);
`python3 scripts/bab_p40_meta_analysis.py --check-meta-summary` byte-identical PASS.
P20–P40 COMPLETE and FROZEN. No `research_state/bab_p41/`, `scripts/bab_p41_stress.py`,
or `generate_p41_decision.py` exists yet — P41 is unstarted and is the sole next workload.
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

### P41 WP1 — Estimator Bakeoff Under Non-Gaussian Idio (IMMEDIATE FIRST STEP)

**Create `scripts/bab_p41_stress.py` with `--check-estimator-bakeoff` that publishes
`research_state/bab_p41/estimator_bakeoff.json` (schema `bab_p41.estimator_bakeoff/1`).**

This is the **only** deliverable for the first session. Do not start WP2 or WP3.
The script must:

1. **Implement 5 DGPs** (charter constants from KICKOFF doc — do not derive, do not edit):
   - GAUSSIAN_IID (control): idio ~ N(0, idio_vol), beta ∈ [0.2, 2.4]
   - STUDENT_T: idio ~ Student-t(ν=4) with scale matched to GAUSSIAN variance
   - REGIME_SWITCH: 2-state Markov vol (calm 0.5×, stress 2.0× base vol; persistence 0.95)
   - JUMP_DIFFUSION: Merton jump idio (intensity 0.05/day, mean −0.5σ, sd 1.5σ)
   - STOCHASTIC_VOL: log-normal vol process (vol-of-vol 0.4, mean-reversion 0.1)

2. **Per-DGP grid** (charter constants):
   - 8 seeds per DGP (base_seed + increment per KICKOFF table; 32 cells/DGP; 160 total)
   - Beta window: 90 (shipped default, never relaxed)
   - Quantile: 0.30 / 0.30 (shipped default)
   - Weighting: equal (shipped default)
   - Beta neutral: True (shipped default)
   - Deflation trials: read-only n_trials_total=552 from P38 WP1

3. **Compare estimator families** (shipped rolling-OLS vs P35 runner-ups):
   - Rolling-OLS (window=90)
   - EWMA (halflife=40)
   - Shrinkage (intensity=0.3, target=1.0 and cross_sectional_mean)
   - Report which estimator (if any) is least-broken by non-Gaussianity

4. **Output**: `research_state/bab_p41/estimator_bakeoff.json` with schema
   `bab_p41.estimator_bakeoff/1` including provenance (fixture SHA256, BTC SHA256,
   seeds, config grid, neutrality tolerances) and per-cell metrics (realized beta,
   model beta-neutrality ≤1e-3, dollar-neutrality ≤1e-9, rank-stability vs OLS,
   turnover, net-of-cost Sharpe, ann vol, max-DD).

5. **Gate**: `--check-estimator-bakeoff` must verify byte-identical recomputation.

**Definition of done for this session:** `python3 -m ruff check .` GREEN,
`python3 scripts/bab_p41_stress.py --check-estimator-bakeoff` PASS (byte-identical),
new artifact exists at `research_state/bab_p41/estimator_bakeoff.json`.

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
| **P41** | **Non-Gaussian Stress (5 DGPs, 160 cells)** | **OPEN — binding** | Measures whether P38/P40 Gaussian verdicts are a Gaussian artifact |

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

P20–P40 are COMPLETE and FROZEN — do not reopen them. The next session executes **P41 WP1**
per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md). Any further work beyond P41
(real-data ingestion, CI enforcement, live deployment) is maintainer-gated and requires
explicit approval; do not invent additional agent-executable campaigns beyond P41 without
maintainer direction.

**Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Fast verify (baseline, before P41 lands):** `python scripts/bab_p40_meta_analysis.py --check-meta-summary`
and `bash scripts/bab_quick.sh` (both GREEN). Do not run the full 56-minute gate to
re-verify frozen P20–P40.

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

**END OF HANDOFF — The next agent's first action must be creating `scripts/bab_p41_stress.py`
with `--check-estimator-bakeoff` per the P41 WP1 specification above.**