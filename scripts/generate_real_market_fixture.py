#!/usr/bin/env python3
"""Generate the expanded real-market price fixture used by the BAB campaign.

Writes ``tests/fixtures/real_market_prices.csv`` with:
  * a ``date`` first column,
  * BTC benchmark plus 8 tradable assets (ETH, SOL, BNB, XRP, ADA, AVAX, DOT, LINK),
  * ~400 business-day rows,
  * one deliberate date gap (a missing business day mid-series),
  * one delisted asset column (``DEL``) that is entirely NaN.

The prices are deterministic random walks (fixed seed) so the fixture is
reproducible. Downstream code converts prices -> returns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

OUT = "tests/fixtures/real_market_prices.csv"

ASSETS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "AVAX", "DOT", "LINK"]
DELISTED = "DEL"
START = "2021-01-04"
N_DAYS = 400
SEED = 20261028
# Drop this business day to create a date gap mid-series.
GAP_DATE = "2021-09-17"


def main() -> None:
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range(start=START, periods=N_DAYS)
    dates = dates.drop(GAP_DATE, errors="ignore")

    # Starting prices per asset (roughly realistic magnitudes).
    starts = {
        "BTC": 32000.0,
        "ETH": 1900.0,
        "SOL": 35.0,
        "BNB": 420.0,
        "XRP": 0.55,
        "ADA": 1.20,
        "AVAX": 55.0,
        "DOT": 14.0,
        "LINK": 22.0,
    }
    # Per-asset daily drift / vol (log-space).
    params = {
        "BTC": (0.0004, 0.018),
        "ETH": (0.0006, 0.024),
        "SOL": (0.0008, 0.035),
        "BNB": (0.0005, 0.028),
        "XRP": (0.0004, 0.030),
        "ADA": (0.0005, 0.032),
        "AVAX": (0.0007, 0.038),
        "DOT": (0.0004, 0.030),
        "LINK": (0.0005, 0.033),
    }

    data: dict[str, np.ndarray] = {}
    for name in ASSETS:
        drift, vol = params[name]
        log_ret = rng.normal(drift, vol, size=len(dates))
        # A couple of idiosyncratic shock days.
        shock_idx = rng.choice(len(dates), size=max(2, len(dates) // 120), replace=False)
        log_ret[shock_idx] += rng.normal(0, 0.05, size=len(shock_idx))
        prices = starts[name] * np.exp(np.cumsum(log_ret))
        data[name] = prices

    # Delisted asset: entirely NaN (no finite values at all).
    data[DELISTED] = np.full(len(dates), np.nan)

    df = pd.DataFrame(data, index=dates)
    df.index.name = "date"
    df = df.reset_index()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"Date gap present: {GAP_DATE!r} excluded -> {len(df)} rows")
    print(f"Delisted column {DELISTED!r} all-NaN: {bool(df[DELISTED].isna().all())}")


if __name__ == "__main__":
    main()