# BAB P37 Closing Decision -- Cost-Aware Turnover & Capacity Closure

**Campaign:** P37 "Cost-Aware Turnover & Capacity Closure"
**Decision row:** P37 WP3 -- Decision doc + documentation-integrity closure + gate wire
**Artifacts consumed (read-only):**
- `research_state/bab_p37/cost_surface_summary.json` (8 cells)
- `research_state/bab_p37/capacity_summary.json` (8 cells)
- `research_state/bab_p37/turnover_summary.json` (8 cells)

**Verdict strings verified:** `RETAIN`, `cost-aware`, `turnover`, `capacity`,
`synthetic`, `not market evidence`

**Decision:** **RETAIN the shipped default** (`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS). P37 closes the economic loop on the 40-asset wide synthetic fixture: costed Sharpe is non-increasing in the transaction-cost level at every (seed, turnover) cell, capacity break-even impact coefficients are measurable via fixed-iteration bisection (books with no zero crossing are censored with a documented reason), and the hysteresis no-trade band reduces turnover vs the shipped equal-weight default at every cell while preserving model beta-neutral (<=1e-3), dollar-neutral (<=1e-9) and realized |beta| (<=0.15). All neutrality invariants hold at every cell across all 24 P37 cells. The shipped default is retained; cost-aware turnover and capacity are now bounded and documented, not flipped.
Every number traces to a committed JSON leaf; no hand-typed numbers.
Synthetic-provenance caveat applies.

---

## Provenance

<!-- table:provenance:start -->
| Fact | Value |
|---|---|
| Schema cost_surface | bab_p37.cost_surface/1 |
| Schema capacity | bab_p37.capacity/1 |
| Schema turnover | bab_p37.turnover/1 |
| Campaign | P37 Cost-Aware Turnover & Capacity Closure |
| WP | WP3 - Decision doc + documentation-integrity closure + gate wire |
| Synthetic universe | Deterministic synthetic wide universe (P35 wide-universe recipe). BTC prices from tests/fixtures/wide_bab_universe.csv. Asset returns = beta * BTC_return + idio, idio ~ N(0, 0.003), betas linspace(0.35, 1.9, 40). Not real market data; not market profitability evidence. |
| Fixture SHA256 | `892c5d59bcbf1a124be798e47b176aeef5199e9e431bef7230cabfdc6b4f3205` |
| BTC source SHA256 | `cf1472e154f38b062d8b40ffe9bddcc6a51286e41400acd51d64e12e9d585a77` |
| Seeds (base/inc/n) | 20261120/1009/8 |
| Seed list | 20261120, 20262129, 20263138, 20264147, 20265156, 20266165, 20267174, 20268183 |
| Beta window | 90 |
| Quantile | 0.300000 |
| Weighting | equal |
| Beta neutral | True |
| Dollar neutral | True |
| Cost grid | 0.000000, 0.001000, 0.002500, 0.005000, 0.010000, 0.020000 |
| Turnover grid | 1.000000, 1.500000, 2.000000, 3.000000 |
| Impact grid | 0.000000, 0.000500, 0.001000, 0.002500, 0.005000, 0.010000, 0.020000, 0.050000 |
| Hysteresis grid | 0.000000, 1.000000, 2.000000, 5.000000, 10.000000 |
| Transaction costs (turnover guard) | 0.001000 |
| Model beta-neutral tol | 0.001000 |
| Dollar-neutral tol | 0.000000 |
| Realized beta tol | 0.150000 |
| Cost surface monotonicity tol | 0.000000 |
| Turnover monotonicity tol | 0.000000 |
<!-- table:provenance:end -->

---

## Cost Surface -- Per-Seed Summary

Costed Sharpe at cost=0.0 and cost=0.02, both at turnover multiplier 1.0 (the shipped
equal-weight default, no hysteresis). Costed Sharpe must be non-increasing in the cost
level at every (seed, turnover) cell.

<!-- table:cost_surface:start -->
| Seed_Idx | N_Periods | N_Valid_Beta | Monotonicity_OK | Neutrality_OK | Status | Sharpe_Cost0_Mult1.0 | Sharpe_Cost02_Mult1.0 |
|---|---|---|---|---|---|---|---|
| 0 | 339 | 339 | True | True | ok | 0.760518 | -5.684110 |
| 1 | 339 | 339 | True | True | ok | 0.320261 | -5.929406 |
| 2 | 339 | 339 | True | True | ok | 1.865525 | -4.634530 |
| 3 | 339 | 339 | True | True | ok | -0.129599 | -6.046680 |
| 4 | 339 | 339 | True | True | ok | -0.531831 | -6.380286 |
| 5 | 339 | 339 | True | True | ok | 0.967765 | -5.105037 |
| 6 | 339 | 339 | True | True | ok | -0.845875 | -7.234725 |
| 7 | 339 | 339 | True | True | ok | 0.532712 | -5.816690 |
<!-- table:cost_surface:end -->

---

## Capacity -- Per-Seed Summary

Market-impact participation-rate break-even via fixed-iteration bisection on the
discrete impact grid. `Break_Even_Impact` is null when no zero crossing is bracketed;
such books are censored with a documented reason instead of a midpoint.

<!-- table:capacity:start -->
| Seed_Idx | N_Periods | Zero_Crossing | Break_Even_Impact | Censoring_Reason | Neutrality_OK | Status |
|---|---|---|---|---|---|---|
| 0 | 339 | True | 0.001339 | None | True | ok |
| 1 | 339 | True | 0.000691 | None | True | ok |
| 2 | 339 | True | 0.005619 | None | True | ok |
| 3 | 339 | False | None | costed sharpe non-positive at every impact level including zero | True | ok |
| 4 | 339 | False | None | costed sharpe non-positive at every impact level including zero | True | ok |
| 5 | 339 | True | 0.002616 | None | True | ok |
| 6 | 339 | False | None | costed sharpe non-positive at every impact level including zero | True | ok |
| 7 | 339 | True | 0.001145 | None | True | ok |
<!-- table:capacity:end -->

---

## Turnover -- Per-Seed Summary

Hysteresis no-trade band vs the shipped equal-weight default (band_multiplier=0.0).
Turnover must be non-increasing in the band width and neutrality must hold at the
widest band. `Turnover_Reduction` = base turnover minus widest-band turnover.

<!-- table:turnover:start -->
| Seed_Idx | N_Periods | Turnover_Monotonic | Neutrality_OK | Turnover_Reduction | Base_Turnover | Widest_Band_Turnover | Status |
|---|---|---|---|---|---|---|---|
| 0 | 339 | True | True | 0.001470 | 0.014831 | 0.013361 | ok |
| 1 | 339 | True | True | 0.001445 | 0.012336 | 0.010892 | ok |
| 2 | 339 | True | True | 0.001439 | 0.008795 | 0.007356 | ok |
| 3 | 339 | True | True | 0.001498 | 0.013818 | 0.012320 | ok |
| 4 | 339 | True | True | 0.001507 | 0.012795 | 0.011288 | ok |
| 5 | 339 | True | True | 0.001432 | 0.009862 | 0.008431 | ok |
| 6 | 339 | True | True | 0.001478 | 0.008934 | 0.007456 | ok |
| 7 | 339 | True | True | 0.001444 | 0.011922 | 0.010478 | ok |
<!-- table:turnover:end -->

---

## Decision Criteria (Chartered Acceptance Thresholds)

<!-- table:decision:start -->
| Criterion | Required |
|---|---|
| All 24 P37 cells (8 cost-surface + 8 capacity + 8 turnover) complete with status ok | True |
| Cost surface: costed Sharpe non-increasing in the cost level at every (seed, turnover) cell (monotonicity OK) | True |
| Cost surface: realized |beta| <= 0.15 at every cell | True |
| Capacity: realized |beta| <= 0.15 at every cell | True |
| Turnover: turnover non-increasing in the hysteresis band width at every cell | True |
| Turnover: neutrality preserved at the widest band at every cell | True |
| Capacity: break-even impact coefficient computed via bisection, or censored with a documented reason, at every cell | True |
| Turnover: hysteresis reduces turnover vs the shipped equal-weight default at every cell (reduction > 0) | True |
| Fixture SHA256 match across all three artifacts | True |
| Synthetic universe labelled controlled synthetic | True |
| Not market evidence / no real alpha | True |
| Shipped default (weighting=equal, beta_neutral=True, beta_window=90, rolling-OLS) RETAINED | True |
<!-- table:decision:end -->

---

## What This Does Not Prove

- **No demonstrated real-world profitability.** The synthetic wide universe is a
  controlled synthetic stimulus: BTC prices from
  `tests/fixtures/wide_bab_universe.csv`, asset returns = `beta * BTC_return + idio`,
  `idio ~ N(0, 0.003)`, betas `linspace(0.35, 1.9, 40)`. It is **not real market data**
  and **not market profitability evidence** — these results are **never market alpha**.
- **No live execution evidence.** No network was used in this campaign.
- **No real market data.** Coinbase public API returns 403; real-market ingestion
  (P28 WP3) requires a maintainer-supplied licensed CSV and is out of scope for P37.
- **Shipped default retained.** The decision does not flip
  `weighting="equal"` / `beta_neutral=True` / `beta_window=90` / rolling-OLS.

---

## Next Steps

Campaign P37 concludes here. The **RETAIN** verdict is grounded in the cost-surface,
capacity, and turnover evidence from WP0-WP2. All neutrality invariants hold at every
cell; costed Sharpe degrades monotonically with transaction cost as expected; capacity
break-even impact coefficients are bounded; hysteresis reduces turnover vs the shipped
default while preserving neutrality. The shipped default
`weighting="equal"`, `beta_neutral=True`, `beta_window=90`, rolling-OLS is retained.

**Future work (not in scope for P37):**
- Real market data ingestion (maintainer-supplied licensed CSV; Coinbase public API
  returns 403) — P28 WP3, maintainer-gated
- CI enforcement of `ruff`, `scripts/bab_gate.sh`, `scripts/bab_reconcile_gate.sh`
  (P28 WP2, maintainer-only; requires `workflows:write`)
- Live-market deployment decision — P28 WP4, maintainer-authorized

---

*This report is artifact-gated: every numeric table cell resolves to a committed JSON
leaf at 6 dp. The acceptance test `tests/test_bab_p37_decision_consistency.py` verifies
zero unmatched cells, table byte-identity, explicit verdict strings (`RETAIN`,
`cost-aware`, `turnover`, `capacity`, `synthetic`, `not market evidence`), AST no-harness
scan, and ruff clean. Never market alpha.*
