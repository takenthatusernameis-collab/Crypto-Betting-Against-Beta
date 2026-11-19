# BAB P23 WP3 — short-availability haircut ladder

Schema `bab_p23.short_haircut/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; charter schema `bab_p23.charter/1`; haircut ladder [0.0, 0.1, 0.25, 0.5, 0.75].
Availability rule: u = numpy.random.default_rng(seed).random(n_assets) drawn once per seed; asset i is short-unavailable at haircut h when u_i < h; unavailable short positions are dropped, never re-levered; rows whose short book is wiped out are flattened and reported via per_seed_degenerate_rows.
Cost rule: costed_pnl_t = baseline_book_pnl_t - haircut * mean_baseline_short_gross; baseline_book_pnl and mean_baseline_short_gross are the haircut-0 book quantities for that weighting/variant, so the fee term is seed-invariant and costed_sharpe is non-increasing in haircut by construction; the availability effect is isolated in availability_sharpe.
Haircut semantics: borrow/availability stress: P22 WP2 owns nonlinear market impact; this ladder is not a price-impact model.

| haircut | weighting | variant | recovery_mean | recovery_min | recovery_positive_frac | null_max_abs | availability_mean | short_survival_mean | availability_sharpe_mean | costed_sharpe_mean | active_rows_min | degenerate_rows_max | min_leg_beta | gross_max | censored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | equal | planted | 0.000261 | 0.000261 | 1.0 | 0.0 | 1.0 | 1.0 | 7.034781 | 7.034781 | 541 | 0 | 0.0 | 0.0 | False |
| 0.0 | equal | null | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 0.639801 | 0.639801 | 541 | 0 | 0.0 | 0.0 | False |
| 0.0 | rank | planted | 0.01736 | 0.01736 | 1.0 | 0.0 | 1.0 | 1.0 | 44.378201 | 44.378201 | 541 | 0 | 0.507692 | 2.414949 | False |
| 0.0 | rank | null | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 0.649924 | 0.649924 | 541 | 0 | 0.507692 | 2.414949 | False |
| 0.1 | equal | planted | 0.000357 | 0.000179 | 1.0 | 0.0 | 0.904878 | 0.895833 | 5.183151 | -993.970148 | 541 | 0 | 0.0 | 0.0 | False |
| 0.1 | equal | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.904878 | 0.895833 | 0.57083 | -1011.674983 | 541 | 0 | 0.0 | 0.0 | False |
| 0.1 | rank | planted | 0.017103 | 0.016528 | 1.0 | 0.0 | 0.904878 | 0.888462 | 39.711127 | -69.059967 | 541 | 0 | 0.507692 | 2.414949 | False |
| 0.1 | rank | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.904878 | 0.888462 | 0.571271 | -316.091723 | 541 | 0 | 0.507692 | 2.414949 | False |
| 0.25 | equal | planted | 0.000517 | 0.000228 | 1.0 | 0.0 | 0.734146 | 0.71875 | 2.920566 | -2495.477541 | 541 | 0 | 0.0 | 0.0 | False |
| 0.25 | equal | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.734146 | 0.71875 | 0.389922 | -2530.147157 | 541 | 0 | 0.0 | 0.0 | False |
| 0.25 | rank | planted | 0.016615 | 0.016052 | 1.0 | 0.0 | 0.734146 | 0.665385 | 28.569371 | -239.21722 | 541 | 0 | 0.507692 | 2.378743 | False |
| 0.25 | rank | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.734146 | 0.665385 | 0.416336 | -791.204195 | 541 | 0 | 0.507692 | 2.378743 | False |
| 0.5 | equal | planted | 0.000836 | 0.000372 | 1.0 | 0.0 | 0.479268 | 0.452083 | 2.395322 | -4997.989862 | 541 | 0 | 0.0 | 0.0 | False |
| 0.5 | equal | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.479268 | 0.452083 | 0.334072 | -5060.934115 | 541 | 0 | 0.0 | 0.0 | False |
| 0.5 | rank | planted | 0.016103 | 0.015449 | 1.0 | 0.0 | 0.479268 | 0.411538 | 19.388105 | -522.812641 | 541 | 0 | 0.507692 | 2.264554 | False |
| 0.5 | rank | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.479268 | 0.411538 | 0.341833 | -1583.058313 | 541 | 0 | 0.507692 | 2.264554 | False |
| 0.75 | equal | planted | 0.001129 | 0.000955 | 1.0 | 0.0 | 0.228049 | 0.225 | 2.197401 | -7500.502184 | 541 | 0 | 0.0 | 0.0 | False |
| 0.75 | equal | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.228049 | 0.225 | 0.28712 | -7591.721073 | 541 | 0 | 0.0 | 0.0 | False |
| 0.75 | rank | planted | 0.014816 | 0.0 | 0.95 | 0.0 | 0.228049 | 0.207692 | 13.372195 | -806.408062 | 0 | 541 | 0.0 | 2.158721 | True |
| 0.75 | rank | null | 0.0 | 0.0 | 0.0 | 0.0 | 0.228049 | 0.207692 | 0.293379 | -2374.912432 | 0 | 541 | 0.0 | 2.158721 | True |
