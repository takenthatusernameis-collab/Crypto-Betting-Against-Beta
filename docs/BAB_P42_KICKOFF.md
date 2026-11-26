# BAB P42 KICKOFF — Planted-Alpha Detectability Frontier & Minimum Detectable Effect

Schema `bab_p42.charter/1`. Controlled synthetic stimulus with known ground truth:
**not real market data and not market profitability evidence.** This campaign is the
sole binding, agent-executable row for the next session. It is heavy by construction:
it cannot be satisfied by a single fixture, a re-used seed, or a re-run of any frozen
P20–P41 harness. It exists because the research record contains an unresolved
**power contradiction**:

- **P21** (`docs/BAB_SIGNAL_OR_NOISE.md`) planted a 4% annual alpha spread on a
  **wide (41-asset), Gaussian, 600-row** universe and the shipped estimator recovered
  it with OOS Sharpe ≈ 7 and DSR ≈ 0.91.
- **P40** (`docs/BAB_P40_DECISION.md`, `DOES_NOT_REPLICATE`) and **P41**
  (`docs/BAB_P41_DECISION.md`, `FRAGILE_DGP_DEPENDENT`) measured the same shipped
  estimator on **narrow (28–40 asset), non-Gaussian, 399-row** universes and found
  survival is fragile and DGP-dependent.

The honest, unmeasured question is therefore not "does BAB work?" but
**"what is the detectability frontier of the shipped estimator — the minimum planted
premium, cross-sectional breadth, and history at which the planted signal is recovered
with deflated significance — and how does non-Gaussian idio move that frontier?"**
P41 varied the noise; P21 varied the signal. **P42 varies signal, breadth, and history
jointly and reports the minimum detectable effect (MDE) surface.** A null/negative
result is a finding, not a bug; nothing is tuned to chase a positive.

## Binding row
- Campaign: P42
- Title: Planted-Alpha Detectability Frontier & Minimum Detectable Effect
- Binding row: P42 WP0 (charter) → WP1 (power grid) → WP2 (frontier meta-analysis) → WP3 (decision + gate wire)
- Artifact-gated: true
- Not market evidence: true
- Licensed data required: false (fully synthetic; no network, no credentials)
- Maintainer approval required: false (this is the agent-executable path)

## Why this campaign exists (the bottleneck it removes)
The prior handoff is stale: it declares P41 WP3 open and its artifacts absent, but
P41 WP1/WP2/WP3 are in fact complete, committed, and green at HEAD `b0a6848`. A future
session that trusts the stale handoff would redo finished work and stall. This charter
removes that bottleneck by naming the next real gap and by making the handoff point
here. The scientific gap is not closed — it is the **power contradiction between P21
and P40/P41**, which is un-probed. P42 closes it with a deterministic, offline, fully
agent-executable factorial battery. No real data, no maintainer gate, no network. A
future session that reads this file has a concrete, multi-hour workload with binding
acceptance gates.

## Charter constants (declared here, not derived from any frozen JSON)

### Reference fixture (read-only)
| Fact | Value |
|---|---|
| Fixture path | `tests/fixtures/wide_bab_universe.csv` |
| Rows | 399 (398 return rows) |
| Columns | 42 (BTC benchmark + 41 candidate assets) |
| First / last date | 2021-01-04 / 2022-07-15 |
| Synthetic | True (deterministic random walk; never market data) |

### Planted-alpha construction (declared here)
Asset returns are `beta_i * BTC_return + idio_i + daily_drift_i`, with
`daily_drift_i = mu_i / 252` and the planted annual drift vector

```
z_i      = (beta_i - mean(beta)) / std(beta)          # z-scored beta
mu_i     = -alpha_annual * z_i                        # low beta -> positive drift
```

so the shipped long-low-beta / short-high-beta book is the side that should recover a
positive premium. `alpha_annual = 0.0` is the **null panel**; its recovery must be
exactly zero and its false-survival rate must stay below the calibration ceiling.

### Factorial grid (declared here)
| Factor | Values |
|---|---|
| Breadth `n_assets` | 9, 20, 40 |
| History `n_rows` (most-recent return rows) | 126, 252, 398 |
| Planted spread `alpha_annual` | 0.0, 0.01, 0.02, 0.04, 0.08 |
| DGP `kind` | GAUSSIAN_IID, STUDENT_T, REGIME_SWITCH |
| Seeds per cell | 6 |
| **Total cells** | **3 × 3 × 5 × 3 × 6 = 810** |

### Fixed estimator / portfolio constants (shipped default; never relaxed)
| Constant | Value |
|---|---|
| Estimator | rolling-OLS (shipped default) |
| Beta window | 90 (min_obs = min(60, 90)) |
| Beta range | linspace(0.2, 2.4, n_assets) |
| Long/short quantile | 0.30 / 0.30 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Transaction costs | 0.0 |
| DSR survive threshold | 0.50 |
| Deflation trials `n_trials_total` | 552, read-only from P38 WP1 (`trial_enumeration.n_trials_total`); never re-enumerated |

### Per-DGP seeds (declared here; base + increment, 6 each)
| DGP | base_seed | increment |
|---|---|---|
| GAUSSIAN_IID | 20261201 | 1009 |
| STUDENT_T | 20271201 | 1013 |
| REGIME_SWITCH | 20281201 | 1019 |

### DGP process parameters (reuse P41 constants verbatim)
| DGP | Process | Parameters |
|---|---|---|
| GAUSSIAN_IID | i.i.d. Gaussian idio | idio_vol = 0.003 |
| STUDENT_T | heavy-tailed idio | ν = 4, scale matched to Gaussian variance |
| REGIME_SWITCH | 2-state Markov vol | calm 0.5×, stress 2.0× base vol, persistence 0.95 |

### Acceptance thresholds (WP1–WP3)
| WP | Threshold | Value |
|---|---|---|
| WP1 | min_total_cells | 810 |
| WP1 | cells_per_factor_level | exact (3 × 3 × 5 × 3 × 6) |
| WP1 | dgp_ids_exact | GAUSSIAN_IID, STUDENT_T, REGIME_SWITCH |
| WP1 | null_recovery_exactly_zero | True |
| WP1 | null_false_survival_rate_max | 0.05 |
| WP1 | neutrality_invariants_all_cells | True |
| WP1 | power_grid_schema | bab_p42.power_grid/1 |
| WP2 | frontier_schema | bab_p42.frontier_summary/1 |
| WP2 | mde_defined_or_censored_every_cell | True |
| WP2 | verdict_is_honest | True |
| WP3 | numbers_matched_min | 100 |
| WP3 | zero_unmatched_cells | 0 |
| WP3 | explicit_synthetic_not_market_strings | True |
| WP3 | gate_wired_and_green | True |
| WP3 | shipped_default_retained | True |

## WPs in order (each is a hard gate; do not skip)
- **P42 WP0 — charter lock.** This doc is the charter. Do not edit constants mid-campaign.
- **P42 WP1 — planted-alpha power grid.** New generator `scripts/bab_p42_power.py`
  with `--check-power-grid`; publish `research_state/bab_p42/power_grid.json`
  (schema `bab_p42.power_grid/1`) + `.md` sidecar. Reuse the P41 DGP builders
  (`scripts/bab_p41_stress.py`) and the shipped
  `strategies/betting_against_beta` estimators/metrics/portfolio, adding only the
  planted-drift layer above. For every one of the 810 cells report: `recovery_mean`,
  `recovery_frac_positive`, `oos_sharpe`, `dsr`, `psr`, `survives_deflation`,
  `verdict`, the three neutrality invariants, and `status`. The `alpha_annual = 0`
  cells are the null panel: recovery exactly 0, false-survival rate ≤ 0.05.
- **P42 WP2 — frontier meta-analysis.** Extend `scripts/bab_p42_power.py` with
  `--check-frontier-summary`; publish `research_state/bab_p42/frontier_summary.json`
  (schema `bab_p42.frontier_summary/1`) + `.md` sidecar. For each
  `(n_assets, n_rows, dgp)` compute the **minimum detectable effect**: the smallest
  `alpha_annual` at which ≥ 50% of seeds survive deflation (DSR ≥ 0.50); mark it
  `censored` when no grid level reaches that bar. Consolidated verdict ∈
  {`DETECTABLE_WITHIN_GRID`, `POWER_LIMITED_FRONTIER`, `NOT_DETECTABLE_IN_GRID`} —
  honest, may be negative; **no seed/parameter tuning to chase a positive.**
- **P42 WP3 — decision doc + gate wire.** `generate_p42_decision.py` →
  `docs/BAB_P42_DECISION.md` from committed JSON only; register in
  `scripts/bab_replay_decisions.py` + `scripts/bab_replay_full.py`; add
  `"p42_decision.md"` to `EXPECTED_NAMES` in
  `tests/test_bab_p29_decision_replay.py` and `"power_grid"` to `EXPECTED_NAMES` in
  `tests/test_bab_p29_replay_coverage.py`; add the `bab_p42` block to
  `scripts/bab_gate.sh`; add this KICKOFF to the doc-registry allow-list with a
  written reason. `ruff` + `scripts/bab_quick.sh` GREEN.

## Provenance & honesty
- Universe seed family: 20261118 (frozen); P42 DGP seeds declared above.
- All cells are deterministic synthetic random processes with a known planted drift.
  **Never market alpha.**
- A null/negative result is a finding, not a bug. A positive recovery on synthetic
  data is **not** evidence of real profitability and does **not** by itself justify a
  real-data campaign — only `DETECTABLE_WITHIN_GRID` plus explicit maintainer approval
  and a licensed CSV would.
- The shipped default (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`,
  rolling-OLS) is retained regardless of outcome; nothing is flipped by this campaign.
- Real-data ingestion, CI workflow changes, and live deployment remain maintainer-gated
  and out of scope.