# BAB P38 Closing Decision -- Deflated Significance & Tail-Risk Closure

**Campaign:** P38 "Deflated Significance & Tail-Risk Closure"
**Decision row:** P38 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p38/deflated_summary.json` (WP1; DSR/PSR over the campaign search)
- `research_state/bab_p38/tail_risk_summary.json` (WP2; CVaR/ES/drawdown, gross + costed)

**Verdict strings verified:** `RETAIN`, `deflated`, `tail-risk`, `synthetic`,
`not market evidence`, `no real alpha`

**Decision:** **RETAIN the shipped default** (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS). P38 closes the two scientific questions a factor strategy must answer. (1) *Deflated significance*: over the full campaign search the deflated Sharpe ratio clears the 0.5 bar for both the shipped default and the best in-sample config, so the campaign verdict is **SURVIVES_DEFLATION**; the trials-adjusted p-values are, however, marginal and are reported as such rather than as decisive. (2) *Tail risk*: on the 40-asset wide synthetic fixture the short-high-beta / short-vol book has a bounded left tail -- CVaR and expected shortfall are small and stable across the eight seeds, the return skew is near zero, and every cell preserves model beta-neutral (<=1e-3), dollar-neutral (<=1e-9) and realized |beta| (<=0.15), gross and costed. The shipped default is retained; nothing is flipped.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema deflated | bab_p38.deflated_significance/1 |
| Schema tail_risk | bab_p38.tail_risk/1 |
| Campaign | P38 Deflated Significance & Tail-Risk Closure |
| WP | WP3 - Decision doc + documentation-integrity closure + gate wire |
| Synthetic deflated | True |
| Synthetic tail_risk | True |
| Deflated note | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Not real market data; not market profitability evidence. The verdict is honest and may be negative. |
| Tail-risk note | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Not real market data; not market profitability evidence. Tail-risk metrics are gross (transaction_costs=0.0) and costed (0.001); they characterize the structural short-high-beta / short-vol crash signature, not market alpha. |
| Fixture path | /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta/tests/fixtures/wide_bab_universe.csv |
| Returns SHA256 | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Seeds (base/inc/n) | 20261120/1009/8 |
| Seed list | 20261120, 20262129, 20263138, 20264147, 20265156, 20266165, 20267174, 20268183 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Gross transaction costs | 0.000000 |
| Costed transaction costs | 0.001000 |
| Model beta-neutral tol | 0.001000 |
| Dollar-neutral tol | 0.000000 |
| Realized beta tol | 0.150000 |
| Deflation trials (n_trials_total) | 552 |
| DSR survive threshold | 0.500000 |
| Campaign verdict | SURVIVES_DEFLATION |
| Tail-risk status | ALL_NEUTRALITY_OK |
<!-- table:provenance:end -->

---

## Deflated / Multiple-Testing-Adjusted Significance (WP1)

Deflated Sharpe Ratio (DSR) and Probabilistic Sharpe Ratio (PSR) for the shipped default
and the best in-sample config, deflated over `n_trials_total` configurations enumerated
read-only from the committed P20-P37 artifacts. `Trials_Adj_p` = 1 - DSR; values below
0.10 but above 0.05 are marginal, not decisive. `Min_BT_Len_PSR50` is the approximate
backtest length at which the standard error of Sharpe equals the observed Sharpe.

<!-- table:deflated:start -->
| Config | Beta_Window | Quantile | Mean_Sharpe | N_Trials | Sigma0 | Gamma | Kappa | DSR | PSR | Trials_Adj_p | Min_BT_Len_PSR50 | Survives | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| shipped_default | 90 | 0.300000 | 0.367434 | 552 | 0.338029 | -0.011292 | 3.163111 | 0.920930 | 1.000000 | 0.079070 | 9 | True | SURVIVES_DEFLATION |
| best_insample_config | 180 | 0.200000 | 0.128445 | 552 | 0.326794 | -0.040693 | 2.892648 | 0.944379 | 1.000000 | 0.055621 | 62 | True | SURVIVES_DEFLATION |
<!-- table:deflated:end -->

---

## Tail-Risk & Drawdown Characterization (WP2)

Per-seed tail metrics aggregated across the eight seeds, gross (structural) and costed
(10 bps). All loss metrics (CVaR, expected shortfall, worst-day, conditional drawdown,
max drawdown) are negative; more negative is a fatter left tail. `tail_asymmetry` is in
[-1, +1]; positive means the left tail dominates. `skew` and `excess_kurtosis` describe
the shape of the return distribution.

<!-- table:tail_risk:start -->
| Metric | Gross_Mean | Gross_Min | Gross_Max | Costed_Mean | Costed_Min | Costed_Max |
|---|---|---|---|---|---|---|
| cvar_95 | -0.000863 | -0.000936 | -0.000784 | -0.000876 | -0.000945 | -0.000805 |
| cvar_99 | -0.001100 | -0.001252 | -0.000932 | -0.001122 | -0.001263 | -0.000984 |
| expected_shortfall_975 | -0.000972 | -0.001083 | -0.000858 | -0.000988 | -0.001092 | -0.000888 |
| worst_day_return | -0.001263 | -0.001490 | -0.001008 | -0.001294 | -0.001499 | -0.001183 |
| skew | -0.015498 | -0.191856 | 0.226654 | -0.021136 | -0.234482 | 0.204963 |
| excess_kurtosis | 0.160747 | -0.216511 | 1.238815 | 0.163182 | -0.266321 | 1.144439 |
| tail_asymmetry | -0.000493 | -0.105366 | 0.084234 | 0.013265 | -0.087612 | 0.096093 |
| conditional_drawdown_95 | -0.007803 | -0.013260 | -0.002881 | -0.009169 | -0.015020 | -0.003048 |
| max_drawdown | -0.008564 | -0.013893 | -0.003722 | -0.009961 | -0.015790 | -0.003875 |
<!-- table:tail_risk:end -->

### Coverage & neutrality (WP2)

Every seed cell must be status ok and pass all three neutrality invariants.

<!-- table:coverage:start -->
| Config | N_Cells | N_OK | N_Neutrality_Violations | N_Error | All_Neutrality_OK |
|---|---|---|---|---|---|
| gross | 8 | 8 | 0 | 0 | True |
| costed | 8 | 8 | 0 | 0 | True |
<!-- table:coverage:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| WP1 deflated significance computed over n_trials_total (read-only trial enumeration from committed P20-P37 artifacts) | True |
| WP1 campaign verdict is SURVIVES_DEFLATION (both configs DSR >= threshold after deflation) | True |
| WP1 trials-adjusted p-values are reported honestly as marginal (below 0.10 but above 0.05), not as decisive evidence | True |
| WP2 tail-risk computed on the wide synthetic fixture for gross and costed books (CVaR / expected shortfall / drawdown) | True |
| WP2 neutrality holds at every tail-risk cell (model beta <= 1e-3, dollar <= 1e-9, realized |beta| <= 0.15) | True |
| WP2 tail metrics are internally ordered (VaR/CVaR/ES nesting, worst-day <= CVaR, drawdown ordering, tail asymmetry in [-1, 1]) | True |
| Fixture SHA256 match across the deflated and tail-risk artifacts | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence / no real alpha | True |
| Shipped default (weighting=equal, beta_neutral=True, beta_window=90, rolling-OLS) RETAINED | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from `tests/fixtures/wide_bab_universe.csv`,
  asset returns = `beta * BTC_return + idio`, `idio ~ N(0, 0.003)`, betas
  `linspace(0.35, 1.9, 40)`. It is **not real market data** and **not market
  profitability evidence** -- these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P38.
- **Marginal deflated significance.** The trials-adjusted p-values are marginal; the
  campaign does not claim decisive statistical significance, only that the deflated
  Sharpe clears its threshold.
- **Shipped default retained.** The decision does not flip `weighting="equal"` /
  `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P38 concludes here. The **RETAIN** verdict is grounded in the deflated
significance (WP1) and tail-risk (WP2) evidence. Every neutrality invariant holds at
every tail-risk cell, gross and costed. The shipped default `weighting="equal"`,
`beta_neutral=True`, `beta_window=90`, rolling-OLS is retained.

**Future work (not in scope for P38):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) -- P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision -- P28 WP4, maintainer-authorized

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p38_decision_consistency.py`
verifies zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`deflated`, `tail-risk`, `synthetic`, `not market evidence`), AST no-harness scan, and
ruff clean. Never market alpha.*
