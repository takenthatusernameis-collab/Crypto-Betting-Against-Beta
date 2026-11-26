# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T06:14:15Z
**Session:** Kilo General Agent Loop — P40 COMPLETE/FROZEN; P41 WP1 COMPLETE; P41 WP2 COMPLETE; **P41 WP3 OPEN (sole next binding row)**
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline (this session, HEAD `47f6c6e`, working tree clean):**
`python3 -m ruff check .` GREEN (`All checks passed!`);
`python3 scripts/bab_p41_stress.py --check-estimator-bakeoff` PASS (byte-identical).
P20–P40 COMPLETE and FROZEN. `research_state/bab_p41/estimator_bakeoff.json` (+ `.md`)
and `scripts/bab_p41_stress.py` landed and verified — **P41 WP1 complete**.
`research_state/bab_p41/stress_summary.json` (schema `bab_p41.stress_summary/1`) + `.md`
landed and verified — **P41 WP2 complete. Verdict: `FRAGILE_DGP_DEPENDENT`** (79 of 160
cells survive deflation over read-only n_trials_total=552; 0 of 5 DGPs fully replicate;
neutrality holds at every cell; honest, negative-leaning finding — nothing tuned to a
positive; shipped default retained).
**P41 WP3 does not exist yet** (`generate_p41_decision.py` and `docs/BAB_P41_DECISION.md`
are absent — confirmed this session) and is the **sole next binding workload**.
**Supersedes:** all prior HANDOFF.md content.

---

## READ FIRST — INITIAL TASK FOR THE NEXT SESSION (do this, in order)

**You are executing Campaign P41 "Non-Gaussian & Regime-Switching Synthetic Stress
Battery." P41 WP1 (estimator bakeoff) and P41 WP2 (stress meta-analysis) are COMPLETE.
The single remaining binding, fully agent-executable row is P41 WP3. This is not a
terminal state and there is no idle fallback: WP3 is a concrete, multi-file, verifiable
workload that cannot be satisfied by a re-run of any frozen harness.**

The single source of truth for the campaign is **[`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md)**.
Read it end-to-end before writing code. Then execute WP3 exactly as below.

### P41 WP3 — Decision Doc + Gate Wire (IMMEDIATE NEXT STEP; sole deliverable)

Per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md) §"WPs in order", and mirroring
the committed P40 pattern (`generate_p40_decision.py`, `scripts/bab_replay_decisions.py:133`,
`tests/test_bab_p29_*`, `scripts/bab_gate.sh:240`):

1. **`generate_p41_decision.py` → `docs/BAB_P41_DECISION.md`** from committed JSON only
   (`research_state/bab_p41/stress_summary.json`). Copy the P40 generator shape
   (`generate_p40_decision.py`: `REPO_ROOT`, `SUMMARY_PATH`, `REPORT_PATH`, `DECIMALS`,
   `_load`, `_cell`). Reproduce the P41 WP2 numbers with **min 100 matched numbers, 0
   unmatched cells**, explicit `synthetic / not market` strings, and shipped default
   retained (do not flip `weighting`, `beta_neutral`, `beta_window`, or the estimator).
2. **Register P41 in `scripts/bab_replay_decisions.py`** — add a `p41_decision.md` entry
   (`module: "generate_p41_decision"`, `gen_dir: ROOT`, `kind: "decision"`, outputs →
   `docs/BAB_P41_DECISION.md`) next to the `p40_decision.md` block at line ~133.
3. **Register P41 in `scripts/bab_replay_full.py`** — mirror the P40 JSON-only artifact
   block at line ~155 so `--xproc/--check-provenance` consumes the committed
   `stress_summary.json` read-only (do NOT run the slow `--check-stress-summary` there).
4. **Add `EXPECTED_NAMES` entries** in `tests/test_bab_p29_replay_coverage.py` (line ~62)
   and `tests/test_bab_p29_decision_replay.py` (line ~32, add `"p41_decision.md"`).
5. **Add the `bab_p41` block to `scripts/bab_gate.sh`** (mirror P40 at line ~240):
   `--check-stress-summary` is expensive — gate on the committed JSON / decision-replay
   subset (`bab_replay_decisions.py --subset p41_decision.md`) + the P41 decision-consistency
   test, not a fresh stress recompute.
6. **Add `docs/BAB_P41_KICKOFF.md` to the doc-registry allow-list** in
   `scripts/bab_doc_consistency_summary.py` `ALLOW_LIST` (line ~42) with a written reason
   (charter doc; replay-gated via the P41 decision entry, no separate generator).
7. **Verify:** `python3 -m ruff check .` GREEN **and** `bash scripts/bab_quick.sh` GREEN.

**Definition of done for the next session:** `python3 -m ruff check .` GREEN,
`bash scripts/bab_quick.sh` GREEN, `docs/BAB_P41_DECISION.md` exists and matches the
committed `stress_summary.json` (verdict `FRAGILE_DGP_DEPENDENT`, ≥100 matched numbers,
0 unmatched), P41 registered in replay + gate, the KICKOFF allow-listed, and
`generate_p41_decision.py` runs cleanly. Do **not** start work beyond P41 WP3
(real-data ingestion, CI enforcement, live deployment are maintainer-gated).

---

## PROJECT STATE SUMMARY (FROZEN P20–P40, P41 WP1–WP2 COMPLETE)

| Phase | Campaign | Verdict | Key Finding |
|-------|----------|---------|-------------|
| P38 WP1 | Deflated Significance (n_trials=552) | **SURVIVES_DEFLATION** | Default DSR=0.921; best in-sample DSR=0.944 |
| P39 WP1 | Regime-Conditional Deflation | **DOES_NOT_SURVIVE_IN_SOME_REGIME** | `bear_mid_vol` 3/8 survive; low-vol regimes 5–6/8 |
| P39 WP2 | Cross-Fixture Replication | **DOES_NOT_REPLICATE** | Only 3/8 survive; mean DSR 0.396 (< 0.5) |
| P39 WP0 | Full-Gate Close-Out (100% cov) | **GREEN** | `BAB_GATE_MIN_COVERAGE=100 bash scripts/bab_gate.sh` exit 0 |
| P36 | Rank-Weighted vs Equal-Weight | **RANK UNDERPERFORMS** | Negative Sharpe, higher vol, worse maxDD. Dead end. |
| P40 WP0 | Multi-Fixture Meta-Analysis (4 fixtures, 32 cells) | **DOES_NOT_REPLICATE** | 0 of 4 fixtures replicate; 16/32 cells survive; neutrality holds |
| **P41 WP1** | **Estimator Bakeoff (5 DGPs, 160 cells)** | **COMPLETE** | shrinkage_i0.3_t1.0 least-broken; estimator_bakeoff.json landed, byte-identical, neutrality holds |
| **P41 WP2** | **Stress Meta-Analysis (5 DGPs, 160 cells)** | **COMPLETE** | `FRAGILE_DGP_DEPENDENT`; 79/160 cells survive; 0/5 DGPs fully replicate; neutrality everywhere; stress_summary.json landed, byte-identical |
| **P41 WP3** | **Decision Doc + Gate Wire** | **OPEN — binding** | Next session; generate_p41_decision.py → BAB_P41_DECISION.md; replay + gate wiring |

**One-line verdict (P38–P41, frozen):** BAB survives pooled deflation on the primary
synthetic fixture (P38) but fails in high-vol regimes (P39 WP1), fails to replicate on a
second fixture (P39 WP2), does not replicate across four independent Gaussian fixtures
(P40), and under non-Gaussian idio the result is `FRAGILE_DGP_DEPENDENT` — survival is
DGP/seed-dependent, not robust across all five DGPs. Synthetic only; never market alpha.

---

## BOTTLENECKS — STATUS

| # | Bottleneck | Status | Resolution |
|---|------------|--------|------------|
| 1 | Full gate cannot complete in one tool window | **RESOLVED** | Use `scripts/bab_quick.sh` for inner loop; full gate only at P41 WP3 |
| 2 | P40 artifacts not landed | **RESOLVED** | All P40 WP0–WP3 artifacts exist, replay-registered, test-covered, gate-wired |
| 3 | Rank weighting | **CLOSED** | P36 proved strictly worse. Never reopen. |
| 4 | Regime coverage gap | **CLOSED** | All six regimes have `n_ok_cells = 8` in `research_state/bab_p39/regime_summary.json` |
| 5 | "Terminal / no campaign remains" framing | **REMOVED** | Prior HANDOFF guaranteed idle session. Rescinded. P41 is binding workload. |
| 6 | P41 WP2 stress meta-analysis open | **RESOLVED** | WP2 complete; stress_summary.json + .md landed, byte-identical |
| 7 | CI workflow enforcement | **EXTERNAL** | Maintainer-only (repo token lacks `workflows:write`). Do not burn session. |
| 8 | Expensive stress re-check / stale baseline | **REMOVED** | This handoff is rebased to HEAD `47f6c6e`; use committed WP2 JSON and the quick inner loop, not the slow stress checker. |
| 9 | P41 WP3 not started | **OPEN — binding** | Sole next workload; fully specified above with exact file touch-points. |

---

## NEXT STATE (binding: P41 WP3)

P20–P40 are COMPLETE and FROZEN — do not reopen them. P41 WP1 and WP2 are COMPLETE and
frozen. The next session executes **P41 WP3** (decision doc + gate wire) per
[`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md). Any further work beyond P41
(real-data ingestion, CI enforcement, live deployment) is maintainer-gated and requires
explicit approval; do not invent additional agent-executable campaigns beyond P41 WP3
without maintainer direction.

**Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Fast verify (baseline, before P41 WP3):** `python3 -m ruff check .`,
`python3 scripts/bab_p41_stress.py --check-estimator-bakeoff`, and `bash scripts/bab_quick.sh`.
The committed `research_state/bab_p41/stress_summary.json` is the read-only WP2 source of
truth; do not run the slow `--check-stress-summary` in the inner loop. Do not run the full
56-minute gate to re-verify frozen P20–P40; run full gate only at P41 WP3. Note: a full
pytest / `bab_gate` run appends one trailing newline to the frozen
`research_state/bab_p27/{risk_controls,reconciliation_e2e}.md` (the `run_*()` P27 tests
write to the committed path) — restore with `git checkout -- research_state/bab_p27/`
after a full run. `scripts/bab_bootstrap.sh` installs missing test/runtime deps on fresh
runners.

---

## SCIENTIFIC TARGET (why this is not busywork)

Every prior campaign (P20–P40) drew synthetic universes from **one i.i.d.-Gaussian family**
(`strategies/betting_against_beta/data.py`: `asset = beta*bm + N(0, idio)`). P41 measures
whether the BAB estimator's behaviour is an artifact of the Gaussian assumption, across
Student-t, regime-switching, jump-diffusion, and stochastic-vol DGPs. WP2's verdict
`FRAGILE_DGP_DEPENDENT` is a valid, publishable negative-leaning finding. **Do not tune
seeds/parameters to chase a positive. Do not flip the shipped default.**

---

## END OF HANDOFF — The next agent's first action is P41 WP3: `generate_p41_decision.py`
→ `docs/BAB_P41_DECISION.md` from the committed `stress_summary.json`, plus replay and
gate wiring, per [`docs/BAB_P41_KICKOFF.md`](docs/BAB_P41_KICKOFF.md).