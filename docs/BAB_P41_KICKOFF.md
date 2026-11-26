# BAB P41 KICKOFF — Non-Gaussian & Regime-Switching Synthetic Stress Battery

Schema `bab_p41.charter/1`. Controlled synthetic stimulus with known ground truth:
**not real market data and not market profitability evidence.** This campaign is the
sole binding, agent-executable row for the next session. It is heavy by construction:
it cannot be satisfied by a single fixture, a re-used seed, or a re-run of any frozen
P20–P40 harness. It exists because every prior campaign (P20–P40) drew its synthetic
universes from the **same i.i.d.-Gaussian generator family**
(`strategies/betting_against_beta/data.py`: `asset = beta*bm + N(0, idio)`). The P38
pooled `SURVIVES_DEFLATION` and the P40 `DOES_NOT_REPLICATE` verdict were both measured
**only** on Gaussian data. Whether the BAB estimator's apparent behaviour is an artifact
of the Gaussian assumption is **unmeasured**. P41 measures it.

## Binding row
- Campaign: P41
- Title: Non-Gaussian & Regime-Switching Synthetic Stress Battery
- Binding row: P41 WP0 (charter) → WP1 (bakeoff) → WP2 (stress meta-analysis) → WP3 (decision + gate wire)
- Artifact-gated: true
- Not market evidence: true
- Licensed data required: false (fully synthetic; no network, no credentials)
- Maintainer approval required: false (this is the agent-executable path)

## Why this campaign exists (the bottleneck it removes)
The prior HANDOFF declared the project "terminal — no agent-executable campaign
remains." That framing is itself the bottleneck: it instructs the next agent to idle.
The honest scientific gap is not closed — it is un-probed. P41 closes it with a
deterministic, offline, fully agent-executable battery. No real data, no maintainer
gate, no network. A future session that reads this file has a concrete, multi-day
workload with binding acceptance gates.

## Charter constants (declared here, not derived from any frozen JSON)

### DGP battery (WP1/WP2) — five independent data-generating processes
| DGP id | Process | Key parameters | Rationale |
|---|---|---|---|
| GAUSSIAN_IID | baseline (frozen P40 family) | idio_vol ∈ {0.003, 0.006}, beta ∈ [0.2, 2.4] | control; must reproduce P40-family behaviour |
| STUDENT_T | heavy-tailed idio (ν=4) | idio scale matched to GAUSSIAN variance | fat tails / excess kurtosis |
| REGIME_SWITCH | 2-state Markov vol (calm/stress) | calm 0.5×, stress 2.0× base vol; persistence 0.95 | vol clustering / non-stationarity |
| JUMP_DIFFUSION | Merton jump idio | jump intensity 0.05/day, mean −0.5σ, sd 1.5σ | discontinuity / gap risk |
| STOCHASTIC_VOL | log-normal vol process | vol-of-vol 0.4, mean-reversion 0.1 | persistent heteroskedasticity |

### Per-DGP grid (declared here)
| Grid | Values |
|---|---|
| Seeds per DGP | 8 (32 cells per DGP; 160 cells total across 5 DGPs) |
| Beta window | 90 (shipped default; never relaxed) |
| Long/short quantile | 0.30 / 0.30 (shipped default) |
| Weighting | equal (shipped default) |
| Beta neutral | True (shipped default) |
| Deflation trials (n_trials_total) | read-only from P38 WP1 (`trial_enumeration.n_trials_total`=552); never re-enumerated |
| DSR survive threshold | 0.50 |

### Per-DGP seeds (declared here; base + increment, 8 each)
| DGP | base_seed | increment |
|---|---|---|
| GAUSSIAN_IID | 20261201 | 1009 |
| STUDENT_T | 20271201 | 1013 |
| REGIME_SWITCH | 20281201 | 1019 |
| JUMP_DIFFUSION | 20291201 | 1021 |
| STOCHASTIC_VOL | 20301201 | 1031 |

### Acceptance thresholds (WP1–WP3)
| WP | Threshold | Value |
|---|---|---|
| WP1 | min_dgps | 5 |
| WP1 | dgp_ids_exact | GAUSSIAN_IID, STUDENT_T, REGIME_SWITCH, JUMP_DIFFUSION, STOCHASTIC_VOL |
| WP1 | gaussian_control_reproduces_p40_family | True |
| WP1 | every_dgp_labelled_synthetic | True |
| WP1 | estimator_bakeoff_schema | bab_p41.estimator_bakeoff/1 |
| WP2 | min_total_cells | 160 |
| WP2 | cells_per_dgp | 8 |
| WP2 | deflation_trials_read_only_from_p38 | True |
| WP2 | neutrality_invariants_all_cells | True |
| WP2 | summary_schema | bab_p41.stress_summary/1 |
| WP2 | verdict_is_honest | True |
| WP3 | numbers_matched_min | 100 |
| WP3 | zero_unmatched_cells | 0 |
| WP3 | explicit_synthetic_not_market_strings | True |
| WP3 | gate_wired_and_green | True |
| WP3 | shipped_default_retained | True |

## WPs in order (each is a hard gate; do not skip)
- **P41 WP0 — charter lock.** This doc is the charter. Do not edit constants mid-campaign.
- **P41 WP1 — estimator bakeoff under non-Gaussian idio.** New generator
  `scripts/bab_p41_stress.py` with `--check-estimator-bakeoff`; publish
  `research_state/bab_p41/estimator_bakeoff.json` (schema `bab_p41.estimator_bakeoff/1`).
  Compare shipped rolling-OLS vs the P35 runner-up estimators on each DGP; report which
  estimator (if any) is least-broken by non-Gaussianity. Honest verdict allowed.
- **P41 WP2 — five-DGP stress meta-analysis.** Extend `scripts/bab_p41_stress.py` with
  `--check-stress-summary`; publish `research_state/bab_p41/stress_summary.json` (schema
  `bab_p41.stress_summary/1`) + `.md` sidecar. 160 cells; per-cell DSR/PSR deflated over
  read-only n_trials_total=552, tail risk, and the three neutrality invariants. Verdict ∈
  {`ROBUST_ACROSS_DGPS`, `FRAGILE_DGP_DEPENDENT`, `DOES_NOT_REPLICATE`} — honest, may be
  negative; **no seed/parameter tuning to chase a positive.**
- **P41 WP3 — decision doc + gate wire.** `generate_p41_decision.py` →
  `docs/BAB_P41_DECISION.md` from committed JSON only; register in
  `scripts/bab_replay_decisions.py` + `scripts/bab_replay_full.py`; add EXPECTED_NAMES in
  `tests/test_bab_p29_replay_coverage.py` and `tests/test_bab_p29_decision_replay.py`; add
  the `bab_p41` block to `scripts/bab_gate.sh`; add this KICKOFF to the doc-registry
  allow-list with a written reason. `ruff` + `scripts/bab_quick.sh` GREEN.

## Provenance & honesty
- Universe seed family: 20261118 (frozen); P41 DGP seeds declared above.
- All five DGPs are deterministic synthetic random processes. **Never market alpha.**
- A null/negative result is a finding, not a bug. A positive result on synthetic data is
  **not** evidence of real profitability and does **not** by itself justify a real-data
  campaign — only `ROBUST_ACROSS_DGPS` plus explicit maintainer approval and a licensed
  CSV would.
- The shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
  rolling-OLS) is retained regardless of outcome; nothing is flipped by this campaign.