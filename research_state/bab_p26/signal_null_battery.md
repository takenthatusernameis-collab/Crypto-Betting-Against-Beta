# P26 WP0 — Signal-to-Noise Validation of Rank-Weighted BAB

**Verdict:** NO-SIGNAL
**Verdict rule:** SIGNAL iff p_rank < 0.05 and p_equal > 0.05; otherwise NO-SIGNAL.
**Seed:** 20261120  |  **Null replications:** 1000  |  **Folds:** 5
**Fixture:** tests/fixtures/wide_bab_universe.csv  |  **SHA256:** a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b

## Observed mean OOS Sharpe (reproduces P25 WP2 bake-off)

| weighting | mean_oos_sharpe | reference | match_6dp |
|---|---|---|---|
| equal | 0.170267 | 0.170267 | yes |
| rank | 0.437311 | 0.437311 | yes |

## Null distribution vs observed (per weighting)

| weighting | observed | null_mean | null_std | null_min | null_max | p_value | z_score | percentile |
|---|---|---|---|---|---|---|---|---|
| equal | 0.170267 | 0.030835 | 1.206484 | -4.663803 | 4.130415 | 0.451548 | 0.115569 | 54.900000 |
| rank | 0.437311 | 0.361307 | 0.736551 | -2.193169 | 2.855762 | 0.468531 | 0.103189 | 53.200000 |

## Conclusion

The recorded verdict is **NO-SIGNAL**, grounded in p_rank=0.468531 and p_equal=0.451548 at level 0.05.
On the no-alpha P25 WP0 fixture the honest outcome is NO-SIGNAL: the rank book's beta-neutral realized return is a pure idiosyncratic spread with mean zero, so its OOS Sharpe is structurally consistent with noise.

## Provenance

- fixture_path: tests/fixtures/wide_bab_universe.csv
- fixture_sha256: a6d390fc755641ea28d14b8204615786fdc9a95733a87e4c3b63d66be64c163b
- return_rows: 398
- date_first: 2021-01-05
- date_last: 2022-07-15
- seed: 20261120
- synthetic: True
- provenance: Deterministic synthetic wide universe (P25 WP0 fixture); not real market data and not evidence of real-market profitability.
- no_lookahead: Each fold runs both weightings over causal history [0, test_end); weights at row t use the one-day backtest lag and rolling betas computed from returns through t-1, so the OOS return at row t is never used to weight itself. The test slice [test_start, test_end) is scored but never read during weight construction. Null draws are fixed per fold (never per row), so turnover and cost drag match the observed book's scale.
- rank_rule: Frazzini-Pedersen rank weighting: long the lowest-beta quantile, short the highest-beta quantile, beta-neutral by construction, rank_min_leg_beta=0.2, rank_max_gross=4.0. Equal weighting is the dollar-neutral default (not beta-neutral).
- verdict_rule: SIGNAL iff p_rank < 0.05 and p_equal > 0.05; otherwise NO-SIGNAL. The verdict is data-driven and never forced.
