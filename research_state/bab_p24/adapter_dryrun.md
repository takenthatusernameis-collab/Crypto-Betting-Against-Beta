# BAB P24 WP3 — licensed-data adapter dry run

Schema `bab_p24.adapter_dryrun/1`. Controlled synthetic stimulus with known ground truth: not real market data and not market profitability evidence.

Fixture: `tests/fixtures/licensed_price_schema.csv` (offline only, network_used=false).
Fixture sha256: `3dd449d6ccbc8f9b4f52f1b424b9791fd963d41d2fec78939f14329f97cd74ce`.
Licensed schema declared by charter: `tests/fixtures/licensed_price_schema.csv`.
Universe contract: 41 assets + `BTC` benchmark + `date` = 43 columns, decimals 6, start 2024-01-02.
Validated: 5 rows, 43 columns, valid=True.
Verdict: controlled synthetic, not market evidence, no-go for market (no_go_for_market=True).
