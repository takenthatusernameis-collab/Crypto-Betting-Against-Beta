# BAB P20 WP5 — cost/turnover break-even

Fixture: `tests/fixtures/real_market_prices.csv` (sha256 `bcf47693858108319c38ccbc02e9ebdb8ade7d4613acb031306d9d6827bd35e2`), 2021-01-04 -> 2022-07-15.
The fixture is a deterministic synthetic random walk with a fixed seed and a deliberate data gap: **not real market data**, and none of these numbers are real-world profitability evidence.
Method: 6-iteration bisection over tc in [0, 0.01] on the equal-weight beta-neutral grid.
Weighting: equal. Beta-neutral: True. `None` marks rows with no zero crossing inside the tested cost range; each reason is recorded in `provenance.null_field_reasons`.

| beta_window | long_quantile | short_quantile | break_even_tc | uncosted_sharpe | sharpe_at_break_even | turnover_at_break_even | gross_at_break_even |
|---|---|---|---|---|---|---|---|
| 30 | 0.200000 | 0.200000 | 0.001016 | 0.435796 | 0.005617 | 0.624799 | 2.732046 |
| 30 | 0.300000 | 0.300000 | None | -0.124867 | None | None | None |
| 60 | 0.200000 | 0.200000 | 0.004609 | 0.834694 | -0.012656 | 0.275765 | 2.442164 |
| 60 | 0.300000 | 0.300000 | None | -1.555531 | None | None | None |
| 90 | 0.200000 | 0.200000 | 0.005078 | 0.810267 | -0.008667 | 0.233905 | 2.222731 |
| 90 | 0.300000 | 0.300000 | None | -0.467052 | None | None | None |
| 120 | 0.200000 | 0.200000 | 0.006172 | 0.878289 | -0.007735 | 0.205068 | 2.073130 |
| 120 | 0.300000 | 0.300000 | 0.003516 | 0.546804 | -0.007858 | 0.164883 | 1.613669 |
| 180 | 0.200000 | 0.200000 | None | 1.216780 | None | None | None |
| 180 | 0.300000 | 0.300000 | 0.001328 | 0.146479 | 0.001227 | 0.123168 | 1.623082 |
