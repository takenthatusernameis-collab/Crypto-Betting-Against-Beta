# BAB P21 WP3 — multi-component cost surface on the planted universe

Schema `bab_p21.cost_surface/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Universe seed 20261118; components: borrow_funding, linear_transaction_cost, notional_slippage; grids: {"borrow_funding": [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2], "linear_transaction_cost": [0.0, 0.00025, 0.0005, 0.001, 0.002, 0.005, 0.01], "notional_slippage": [0.0, 5e-05, 0.0001, 0.00025, 0.0005, 0.001, 0.002]}

| variant | weighting | active_rows | gross_sharpe | gross_turnover_mean | short_notional_mean | gross_final_cumulative | censored | censor_reason |
|---|---|---|---|---|---|---|---|---|
| planted | equal | 541 | 7.034781 | 0.009797 | 0.367046 | 1.167118 | False | None |
| planted | rank | 541 | 44.378201 | 0.007204 | 0.362007 | 11401.093638 | False | None |
| null | equal | 541 | 0.639801 | 0.009797 | 0.367046 | 1.013905 | False | None |
| null | rank | 541 | 0.649924 | 0.007204 | 0.362007 | 1.049395 | False | None |

| variant | weighting | component | level | costed_sharpe | cost_drag_mean | total_cost | final_cumulative |
|---|---|---|---|---|---|---|---|
| planted | equal | borrow_funding | 0.0 | 7.034781 | 0.0 | 0.0 | 1.167118 |
| planted | equal | borrow_funding | 0.005 | 6.840165 | 7e-06 | 0.00437 | 1.16203 |
| planted | equal | borrow_funding | 0.01 | 6.645201 | 1.5e-05 | 0.008739 | 1.156965 |
| planted | equal | borrow_funding | 0.02 | 6.254267 | 2.9e-05 | 0.017478 | 1.146901 |
| planted | equal | borrow_funding | 0.05 | 5.074075 | 7.3e-05 | 0.043696 | 1.117229 |
| planted | equal | borrow_funding | 0.1 | 3.087078 | 0.000146 | 0.087392 | 1.06947 |
| planted | equal | borrow_funding | 0.2 | -0.925486 | 0.000291 | 0.174784 | 0.979978 |
| planted | equal | linear_transaction_cost | 0.0 | 7.034781 | 0.0 | 0.0 | 1.167118 |
| planted | equal | linear_transaction_cost | 0.00025 | 6.965451 | 2e-06 | 0.00147 | 1.165404 |
| planted | equal | linear_transaction_cost | 0.0005 | 6.894337 | 5e-06 | 0.002939 | 1.163693 |
| planted | equal | linear_transaction_cost | 0.001 | 6.747015 | 1e-05 | 0.005878 | 1.160278 |
| planted | equal | linear_transaction_cost | 0.002 | 6.43399 | 2e-05 | 0.011757 | 1.153477 |
| planted | equal | linear_transaction_cost | 0.005 | 5.394763 | 4.9e-05 | 0.029392 | 1.133307 |
| planted | equal | linear_transaction_cost | 0.01 | 3.628799 | 9.8e-05 | 0.058784 | 1.100451 |
| planted | equal | notional_slippage | 0.0 | 7.034781 | 0.0 | 0.0 | 1.167118 |
| planted | equal | notional_slippage | 5e-05 | 7.021061 | 0.0 | 0.000294 | 1.166775 |
| planted | equal | notional_slippage | 0.0001 | 7.007267 | 1e-06 | 0.000588 | 1.166432 |
| planted | equal | notional_slippage | 0.00025 | 6.965451 | 2e-06 | 0.00147 | 1.165404 |
| planted | equal | notional_slippage | 0.0005 | 6.894337 | 5e-06 | 0.002939 | 1.163693 |
| planted | equal | notional_slippage | 0.001 | 6.747015 | 1e-05 | 0.005878 | 1.160278 |
| planted | equal | notional_slippage | 0.002 | 6.43399 | 2e-05 | 0.011757 | 1.153477 |
| planted | rank | borrow_funding | 0.0 | 44.378201 | 0.0 | 0.0 | 11401.093638 |
| planted | rank | borrow_funding | 0.005 | 44.375231 | 7e-06 | 0.00431 | 11352.902366 |
| planted | rank | borrow_funding | 0.01 | 44.372258 | 1.4e-05 | 0.008619 | 11304.91442 |
| planted | rank | borrow_funding | 0.02 | 44.3663 | 2.9e-05 | 0.017238 | 11209.545079 |
| planted | rank | borrow_funding | 0.05 | 44.348344 | 7.2e-05 | 0.043096 | 10928.228534 |
| planted | rank | borrow_funding | 0.1 | 44.318134 | 0.000144 | 0.086192 | 10474.940961 |
| planted | rank | borrow_funding | 0.2 | 44.256634 | 0.000287 | 0.172384 | 9623.895351 |
| planted | rank | linear_transaction_cost | 0.0 | 44.378201 | 0.0 | 0.0 | 11401.093638 |
| planted | rank | linear_transaction_cost | 0.00025 | 44.35277 | 2e-06 | 0.001081 | 11388.873182 |
| planted | rank | linear_transaction_cost | 0.0005 | 44.326556 | 4e-06 | 0.002161 | 11376.661837 |
| planted | rank | linear_transaction_cost | 0.001 | 44.271796 | 7e-06 | 0.004322 | 11352.266456 |
| planted | rank | linear_transaction_cost | 0.002 | 44.15306 | 1.4e-05 | 0.008645 | 11303.584765 |
| planted | rank | linear_transaction_cost | 0.005 | 43.72569 | 3.6e-05 | 0.021612 | 11158.408882 |
| planted | rank | linear_transaction_cost | 0.01 | 42.796701 | 7.2e-05 | 0.043224 | 10919.323952 |
| planted | rank | notional_slippage | 0.0 | 44.378201 | 0.0 | 0.0 | 11401.093638 |
| planted | rank | notional_slippage | 5e-05 | 44.373178 | 0.0 | 0.000216 | 11398.648818 |
| planted | rank | notional_slippage | 0.0001 | 44.368123 | 1e-06 | 0.000432 | 11396.204362 |
| planted | rank | notional_slippage | 0.00025 | 44.35277 | 2e-06 | 0.001081 | 11388.873182 |
| planted | rank | notional_slippage | 0.0005 | 44.326556 | 4e-06 | 0.002161 | 11376.661837 |
| planted | rank | notional_slippage | 0.001 | 44.271796 | 7e-06 | 0.004322 | 11352.266456 |
| planted | rank | notional_slippage | 0.002 | 44.15306 | 1.4e-05 | 0.008645 | 11303.584765 |
| null | equal | borrow_funding | 0.0 | 0.639801 | 0.0 | 0.0 | 1.013905 |
| null | equal | borrow_funding | 0.005 | 0.438821 | 7e-06 | 0.00437 | 1.009485 |
| null | equal | borrow_funding | 0.01 | 0.237817 | 1.5e-05 | 0.008739 | 1.005083 |
| null | equal | borrow_funding | 0.02 | -0.164217 | 2.9e-05 | 0.017478 | 0.996338 |
| null | equal | borrow_funding | 0.05 | -1.369783 | 7.3e-05 | 0.043696 | 0.970555 |
| null | equal | borrow_funding | 0.1 | -3.37221 | 0.000146 | 0.087392 | 0.929055 |
| null | equal | borrow_funding | 0.2 | -7.314578 | 0.000291 | 0.174784 | 0.851294 |
| null | equal | linear_transaction_cost | 0.0 | 0.639801 | 0.0 | 0.0 | 1.013905 |
| null | equal | linear_transaction_cost | 0.00025 | 0.572112 | 2e-06 | 0.00147 | 1.012416 |
| null | equal | linear_transaction_cost | 0.0005 | 0.504307 | 5e-06 | 0.002939 | 1.01093 |
| null | equal | linear_transaction_cost | 0.001 | 0.36857 | 1e-05 | 0.005878 | 1.007962 |
| null | equal | linear_transaction_cost | 0.002 | 0.098125 | 2e-05 | 0.011757 | 1.002053 |
| null | equal | linear_transaction_cost | 0.005 | -0.67613 | 4.9e-05 | 0.029392 | 0.984528 |
| null | equal | linear_transaction_cost | 0.01 | -1.721845 | 9.8e-05 | 0.058784 | 0.955979 |
| null | equal | notional_slippage | 0.0 | 0.639801 | 0.0 | 0.0 | 1.013905 |
| null | equal | notional_slippage | 5e-05 | 0.626275 | 0.0 | 0.000294 | 1.013607 |
| null | equal | notional_slippage | 0.0001 | 0.612743 | 1e-06 | 0.000588 | 1.013309 |
| null | equal | notional_slippage | 0.00025 | 0.572112 | 2e-06 | 0.00147 | 1.012416 |
| null | equal | notional_slippage | 0.0005 | 0.504307 | 5e-06 | 0.002939 | 1.01093 |
| null | equal | notional_slippage | 0.001 | 0.36857 | 1e-05 | 0.005878 | 1.007962 |
| null | equal | notional_slippage | 0.002 | 0.098125 | 2e-05 | 0.011757 | 1.002053 |
| null | rank | borrow_funding | 0.0 | 0.649924 | 0.0 | 0.0 | 1.049395 |
| null | rank | borrow_funding | 0.005 | 0.593267 | 7e-06 | 0.00431 | 1.044883 |
| null | rank | borrow_funding | 0.01 | 0.536608 | 1.4e-05 | 0.008619 | 1.04039 |
| null | rank | borrow_funding | 0.02 | 0.423283 | 2.9e-05 | 0.017238 | 1.031462 |
| null | rank | borrow_funding | 0.05 | 0.083274 | 7.2e-05 | 0.043096 | 1.005133 |
| null | rank | borrow_funding | 0.1 | -0.483412 | 0.000144 | 0.086192 | 0.962735 |
| null | rank | borrow_funding | 0.2 | -1.615943 | 0.000287 | 0.172384 | 0.883219 |
| null | rank | linear_transaction_cost | 0.0 | 0.649924 | 0.0 | 0.0 | 1.049395 |
| null | rank | linear_transaction_cost | 0.00025 | 0.635638 | 2e-06 | 0.001081 | 1.048262 |
| null | rank | linear_transaction_cost | 0.0005 | 0.621266 | 4e-06 | 0.002161 | 1.047129 |
| null | rank | linear_transaction_cost | 0.001 | 0.592291 | 7e-06 | 0.004322 | 1.044866 |
| null | rank | linear_transaction_cost | 0.002 | 0.533596 | 1.4e-05 | 0.008645 | 1.040351 |
| null | rank | linear_transaction_cost | 0.005 | 0.355345 | 3.6e-05 | 0.021612 | 1.026886 |
| null | rank | linear_transaction_cost | 0.01 | 0.073453 | 7.2e-05 | 0.043224 | 1.004715 |
| null | rank | notional_slippage | 0.0 | 0.649924 | 0.0 | 0.0 | 1.049395 |
| null | rank | notional_slippage | 5e-05 | 0.647074 | 0.0 | 0.000216 | 1.049169 |
| null | rank | notional_slippage | 0.0001 | 0.64422 | 1e-06 | 0.000432 | 1.048942 |
| null | rank | notional_slippage | 0.00025 | 0.635638 | 2e-06 | 0.001081 | 1.048262 |
| null | rank | notional_slippage | 0.0005 | 0.621266 | 4e-06 | 0.002161 | 1.047129 |
| null | rank | notional_slippage | 0.001 | 0.592291 | 7e-06 | 0.004322 | 1.044866 |
| null | rank | notional_slippage | 0.002 | 0.533596 | 1.4e-05 | 0.008645 | 1.040351 |

| variant | weighting | component | monotonic_sharpe | period_wise_non_increasing |
|---|---|---|---|---|---|
| planted | equal | borrow_funding | True | True |
| planted | equal | linear_transaction_cost | True | True |
| planted | equal | notional_slippage | True | True |
| planted | rank | borrow_funding | True | True |
| planted | rank | linear_transaction_cost | True | True |
| planted | rank | notional_slippage | True | True |
| null | equal | borrow_funding | True | True |
| null | equal | linear_transaction_cost | True | True |
| null | equal | notional_slippage | True | True |
| null | rank | borrow_funding | True | True |
| null | rank | linear_transaction_cost | True | True |
| null | rank | notional_slippage | True | True |

Per-book costed Sharpe is non-increasing in every cost-component level (monotonic_sharpe = true), and every period's costed return is non-increasing in the level (period_wise_non_increasing = true), since each drag is a non-negative rate times a non-negative exposure. Censored books carry a documented censor_reason and never a zero tolerance.
