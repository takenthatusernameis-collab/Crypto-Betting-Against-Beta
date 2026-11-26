# DURABLE HANDOFF — Crypto-Betting-Against-Beta
**Timestamp:** 2026-11-26T04:15:00Z
**Session:** Kilo General Agent Loop — Campaign P40 COMPLETE (P40 WP0–WP3 landed)
**Repository:** Crypto-Betting-Against-Beta (Betting Against Beta crypto quant research)
**Verified baseline:** HEAD `4a6f9d9`, working tree clean. P40 artifacts landed this session:
`research_state/bab_p40/meta_summary.json` + `.md`, `scripts/bab_p40_meta_analysis.py`,
`generate_p40_decision.py`, `docs/BAB_P40_DECISION.md`,
`tests/test_bab_p40_meta_analysis.py`, `tests/test_bab_p40_decision_consistency.py`.
P40 verdict: **DOES_NOT_REPLICATE** (0 of 4 fixtures replicate the P38 pooled verdict;
16 of 32 cells survive deflation; neutrality holds at every cell). P38
`campaign_verdict=SURVIVES_DEFLATION` with `trial_enumeration.n_trials_total=552`;
P39 regime `DOES_NOT_SURVIVE_DEFLATION_IN_SOME_REGIME`; P39 cross `DOES_NOT_REPLICATE`.
All reference scripts/tests/registries named below exist.
**Supersedes:** all prior HANDOFF.md content. Campaign B / P37 regime-conditional is CLOSED.
P20–P39 are COMPLETE and FROZEN. P40 is COMPLETE and FROZEN. No binding campaign remains;
next state is a terminal P38–P40 consolidation summary (maintainer decision required for
any real-data follow-on).

---

## P40 OUTCOME (this session — heavy work landed)

| Artifact | Path | Status |
|---|---|---|
| WP0 meta-analysis generator | `scripts/bab_p40_meta_analysis.py` | LANDED, `--check-meta-summary` PASS |
| WP0 summary JSON | `research_state/bab_p40/meta_summary.json` | LANDED, byte-stable |
| WP0 summary Markdown | `research_state/bab_p40/meta_summary.md` | LANDED, byte-stable |
| WP2 decision generator | `generate_p40_decision.py` | LANDED |
| WP2 decision doc | `docs/BAB_P40_DECISION.md` | LANDED, generated from committed JSON |
| WP3 meta-analysis tests | `tests/test_bab_p40_meta_analysis.py` | LANDED, 29 tests PASS |
| WP3 decision consistency tests | `tests/test_bab_p40_decision_consistency.py` | LANDED, 13 tests PASS |
| Replay full registry | `scripts/bab_p40_meta_analysis` entry | REGISTERED (json_only, no_xproc) |
| Replay coverage guard | `tests/test_bab_p29_replay_coverage.py` | `meta_summary` added to EXPECTED_NAMES |
| Replay decisions registry | `scripts/bab_replay_decisions.py` | `p40_decision.md` entry REGISTERED |
| Replay decision guard | `tests/test_bab_p29_decision_replay.py` | `p40_decision.md` added to EXPECTED_NAMES |
| Gate block | `scripts/bab_gate.sh` | P40 block added (check + tests + replay) |
| ruff | `python3 -m ruff check .` | GREEN |
| bab_quick.sh | `bash scripts/bab_quick.sh` | GREEN |

**Consolidated verdict:** `DOES_NOT_REPLICATE` — 0 of 4 fixtures (F1_PRIMARY, F2_P39_SECOND,
F3_LOW_VOL_WIDE, F4_HIGH_VOL_NARROW) replicate the P38 pooled verdict
(SURVIVES_DEFLATION + ALL_NEUTRALITY_OK) after deflation over n_trials_total=552.
16 of 32 cells survive deflation; neutrality invariants hold at every cell.
Honest negative: the P38 pooled survival is fixture-dependent, not a universal
factor property. All inputs are deterministic synthetic; not real market data.

---

## READ FIRST — ANTI-SPIN CONTRACT

**P40 is complete. Do not reopen P20–P40.** Do not add new fixtures, do not re-tune
seeds/parameters, do not chase a positive verdict. The only legitimate follow-on is a
real-data validation campaign, and only `ROBUST_ACROSS_FIXTURES` justifies it — P40 did
not produce that verdict, so no follow-on is warranted without explicit maintainer
approval and a licensed real-market CSV.

**Editing HANDOFF.md without landing P40 artifacts is forbidden.** P40 artifacts are
landed; this file records the outcome. Do not spend a session re-validating frozen
P20–P39 or re-running the 56-minute full gate.

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

**One-line verdict:** BAB survives pooled deflation on the primary synthetic fixture (P38)
but fails in high-vol regimes (P39 WP1), fails to replicate on a second fixture (P39 WP2),
and does not replicate across four independent fixtures (P40). The factor is
fixture-dependent, not robust. Terminal: no further agent-executable campaign remains.

---

## BOTTLENECKS — CURRENT STATUS

**Bottleneck 1 (RESOLVED): full gate cannot complete in one tool window.** P39 WP0 already
ran the full 100%-coverage gate GREEN and committed it. Do NOT rerun `scripts/bab_gate.sh`
to verify P39 WP0.

**Bottleneck 2 (RESOLVED): P40 artifacts missing.** All P40 artifacts (WP0–WP3) are now
landed, replay-registered, test-covered, and gate-wired. Bottleneck closed.

**Bottleneck 3 (CLOSED): rank weighting.** P36 proved it strictly worse. Never reopen.

**Bottleneck 4 (CLOSED): regime coverage gap.** All six regimes have `n_ok_cells = 8` in
`research_state/bab_p39/regime_summary.json`; do not re-litigate.

**Bottleneck 5 (EXTERNAL / maintainer-only): CI workflow enforcement is not agent-fixable.**
`.github/workflows/main.yml` does not invoke ruff/full gate/reconcile gate, and the repo
token lacks `workflows:write`. Do not burn a session trying to push a workflow change.
Record it as a maintainer action; local gates remain the agent-executable proof.

---

## NEXT STATE (terminal — no agent-executable campaign remains)

P20–P40 are COMPLETE and FROZEN. There is no binding campaign for the next agentic
session. The consolidated P38–P40 verdict is:

> BAB survives pooled deflation on one synthetic fixture but fails in high-vol regimes
> and fails to replicate across four independent synthetic fixtures. The P38 pooled
> verdict is fixture-dependent, not a universal factor property. Synthetic-provenance
> caveat applies throughout; never market alpha.

Any further work (real-data ingestion, CI enforcement, live deployment) is maintainer-gated
and requires explicit approval. Do not invent new agent-executable campaigns without
maintainer direction.

**Repository root:** `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
**Fast verify:** `python scripts/bab_p40_meta_analysis.py --check-meta-summary` and
`bash scripts/bab_quick.sh` (both GREEN). Do not run the full 56-minute gate.
