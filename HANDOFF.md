# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T04:42:22Z
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

1. **P41 WP0** — charter is locked in the KICKOFF doc; do not edit its constants.
2. **P41 WP1** — `scripts/bab_p41_stress.py --check-estimator-bakeoff` →
   `research_state/bab_p41/estimator_bakeoff.json` (schema `bab_p41.estimator_bakeoff/1`).
3. **P41 WP2** — `scripts/bab_p41_stress.py --check-stress-summary` →
   `research_state/bab_p41/stress_summary.json` (schema `bab_p41.stress_summary/1`) + `.md`.
   160 cells (5 DGPs × 8 seeds); DSR/PSR deflated over read-only n_trials_total=552.
4. **P41 WP3** — `generate_p41_decision.py` → `docs/BAB_P41_DECISION.md`; register in
   `scripts/bab_replay_decisions.py` + `scripts/bab_replay_full.py`; extend EXPECTED_NAMES
   in `tests/test_bab_p29_replay_coverage.py` and `tests/test_bab_p29_decision_replay.py`;
   add the `bab_p41` block to `scripts/bab_gate.sh`; allow-list the KICKOFF in
   `tests/test_bab_p33_doc_registry_completeness.py` with a written reason.

**Definition of done for P41:** `python3 -m ruff check .` GREEN, `bash scripts/bab_quick.sh`
GREEN, every new `--check-*` byte-stable, new tests pass, replay + gate wired, and a full
`BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` run to completion GREEN on a
large-time-budget session (restore `research_state/bab_p27/` with `git checkout --` after a
full run — the P27 `run_*()` tests append one trailing newline to two frozen files).

**Scientific target (why this is not busywork):** every prior campaign drew synthetic
universes from one i.i.d.-Gaussian family (`strategies/betting_against_beta/data.py`). The
P38 `SURVIVES_DEFLATION` and P40 `DOES_NOT_REPLICATE` verdicts were measured **only** on
Gaussian data. P41 measures whether the BAB estimator's behaviour is an artifact of the
Gaussian assumption, across Student-t, regime-switching, jump-diffusion, and stochastic-vol
DGPs. The verdict may be negative — that is a valid, publishable finding. **Do not tune
seeds/parameters to chase a positive. Do not flip the shipped default.**

---

## PROJECT STATE SUMMARY

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| **P38 WP1** | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default (β=90,q=0.3,equal) DSR=0.921; best in-sample (β=180,q=0.2) DSR=0.944 |
| **P39 WP1** | Regime-Conditional Deflation | **DOES_NOT_SURVIVE_IN_SOME_REGIME** | `bear_mid_vol` 3/8 survive (DSR 0.35); `bull_high_vol`/`bull_mid_vol` 4/8 (DSR 0.53); low-vol regimes 5–6/8 |
| **P39 WP2** | Cross-Fixture Replication (2nd universe) | **DOES_NOT_REPLICATE** | Only 3/8 survive; mean DSR 0.396 (< 0.5) |
| **P39 WP0** | Full-Gate Close-Out (100% cov) | **GREEN (committed)** | `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0, TOTAL 100%, 7675 passed/39 skipped |
| **P36** | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Negative Sharpe, higher vol, worse maxDD. Dead end. |
| **P40 WP0** | Multi-Fixture Meta-Analysis (4 fixtures, 32 cells) | **DOES_NOT_REPLICATE** | 0 of 4 fixtures replicate P38 pooled verdict; 16/32 cells survive; neutrality holds everywhere |
| **P41** | Non-Gaussian & Regime-Switching Stress (5 DGPs, 160 cells) | **OPEN — binding** | Measures whether P38/P40 Gaussian verdicts are a Gaussian-family artifact |

**One-line verdict (P38–P40, frozen):** BAB survives pooled deflation on the primary
synthetic fixture (P38) but fails in high-vol regimes (P39 WP1), fails to replicate on a
second fixture (P39 WP2), and does not replicate across four independent Gaussian fixtures
(P40). The open question — does this hold under non-Gaussian dynamics? — is P41.

---

## BOTTLENECKS — STATUS

**Bottleneck 1 (RESOLVED): full gate cannot complete in one tool window.** `scripts/bab_gate.sh`
runs parallel xdist (~5–6 min) and P39 WP0 already ran it GREEN at 100% coverage. Use
`scripts/bab_quick.sh` for the inner loop; run the full gate once at P41 WP3.

**Bottleneck 2 (RESOLVED): P40 artifacts landed.** All P40 WP0–WP3 artifacts exist, are
replay-registered, test-covered, and gate-wired.

**Bottleneck 3 (CLOSED): rank weighting.** P36 proved it strictly worse. Never reopen.

**Bottleneck 4 (CLOSED): regime coverage gap.** All six regimes have `n_ok_cells = 8` in
`research_state/bab_p39/regime_summary.json`.

**Bottleneck 5 (REMOVED THIS SESSION): the "terminal / no campaign remains" framing.**
The prior HANDOFF told the next agent there was nothing to do. That was the dominant
bottleneck — it guaranteed an idle session. It is rescinded. P41 is the binding workload.

**Bottleneck 6 (EXTERNAL / maintainer-only): CI workflow enforcement is not agent-fixable.**
`.github/workflows/main.yml` does not invoke ruff/full gate/reconcile gate, and the repo
token lacks `workflows:write`. Do not burn a session trying to push a workflow change.
Local gates remain the agent-executable proof.

---

## NEXT STATE (binding: P41)

P20–P40 are COMPLETE and FROZEN — do not reopen them. The next session executes **P41**
per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md). Any further work beyond P41
(real-data ingestion, CI enforcement, live deployment) is maintainer-gated and requires
explicit approval; do not invent additional agent-executable campaigns beyond P41 without
maintainer direction.

**Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Fast verify (baseline, before P41 lands):** `python scripts/bab_p40_meta_analysis.py --check-meta-summary`
and `bash scripts/bab_quick.sh` (both GREEN). Do not run the full 56-minute gate to
re-verify frozen P20–P40.