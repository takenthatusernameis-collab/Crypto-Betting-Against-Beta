#!/usr/bin/env python3
"""P25 WP0 — wide synthetic universe generator.

Deterministic, seeded, no-network generator producing a 41+ column price
fixture (date, BTC, A001..A040[, DEL]) whose 398 return rows match the dates
of ``tests/fixtures/real_market_prices.csv`` exactly, including the
``2021-09-17`` gap and one all-NaN ``DEL`` column.

Asset returns are synthesized as ``r_asset = beta * r_BTC + idio`` with
``idio ~ N(0, 0.003)`` and betas uniformly spanning 0.35-1.90 across 40
assets, so the wide cross-section makes rank-weighted BAB empirically
evaluable out of sample.

Single entry point: ``build_wide_universe()`` returns a ``pd.DataFrame`` and
writes the CSV + metadata JSON sidecar.

Usage:
  python3 scripts/bab_wide_universe.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SEED = 20261120
IDIO_VOL = 0.003
BETA_MIN = 0.35
BETA_MAX = 1.90
N_ASSETS = 40
NAN_COLUMN = "DEL"
REFERENCE_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "real_market_prices.csv"
OUTPUT_CSV = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe.csv"
OUTPUT_META = _REPO_ROOT / "tests" / "fixtures" / "wide_bab_universe_meta.json"
SCHEMA_VERSION = "bab_p25.wide_universe/1"


def _load_reference_prices() -> pd.DataFrame:
    """Load the reference price fixture and return it with a DatetimeIndex."""
    df = pd.read_csv(REFERENCE_FIXTURE, index_col="date", parse_dates=True)
    df.index = pd.DatetimeIndex(df.index)
    if "BTC" not in df.columns:
        raise ValueError(f"reference fixture missing BTC column: {list(df.columns)}")
    return df


def _build_wide_universe() -> tuple[pd.DataFrame, dict]:
    """Build the wide synthetic universe price frame and metadata.

    Returns ``(prices_df, metadata)`` where ``prices_df`` has columns
    ``[BTC, A001..A040, DEL]`` indexed by date matching the reference fixture.
    """
    ref = _load_reference_prices()
    btc_prices = ref["BTC"].astype(float)
    dates = ref.index

    btc_returns = btc_prices.pct_change().iloc[1:]
    btc_return_dates = btc_returns.index

    rng = np.random.default_rng(SEED)
    betas = np.linspace(BETA_MIN, BETA_MAX, N_ASSETS)

    n_returns = len(btc_return_dates)
    idio = rng.normal(loc=0.0, scale=IDIO_VOL, size=(N_ASSETS, n_returns))

    asset_returns = np.vstack([
        beta * btc_returns.to_numpy(dtype=float) + idio[i]
        for i, beta in enumerate(betas)
    ])

    asset_columns = [f"A{i:03d}" for i in range(1, N_ASSETS + 1)]
    returns_df = pd.DataFrame(
        asset_returns.T,
        index=btc_return_dates,
        columns=asset_columns,
    )

    # Reconstruct prices from returns: first price = BTC first price, then cumprod.
    btc_first_price = float(btc_prices.iloc[0])
    btc_price_series = btc_first_price * (1.0 + btc_returns).cumprod()
    # Prepend the first price so the price frame aligns with reference dates.
    btc_price_full = pd.concat([
        pd.Series({dates[0]: btc_first_price}),
        btc_price_series,
    ])

    asset_price_series = {}
    for i, col in enumerate(asset_columns):
        # Start each asset at price 100 (arbitrary base), then cumprod returns.
        asset_prices = 100.0 * (1.0 + returns_df[col]).cumprod()
        asset_price_series[col] = asset_prices

    prices = pd.DataFrame({"BTC": btc_price_full, **asset_price_series}, index=dates)
    prices[NAN_COLUMN] = np.nan

    # Column order: date (index), BTC, A001..A040, DEL
    prices = prices[["BTC", *asset_columns, NAN_COLUMN]]

    btc_sha256 = hashlib.sha256(
        btc_prices.to_numpy(dtype=float).tobytes()
    ).hexdigest()

    metadata = {
        "schema": SCHEMA_VERSION,
        "fixture_sha256": "",  # filled in after CSV write
        "seed": SEED,
        "beta_range": [BETA_MIN, BETA_MAX],
        "idio_vol": IDIO_VOL,
        "date_first": str(dates[0].date()),
        "date_last": str(dates[-1].date()),
        "price_rows": len(prices),
        "return_rows": int(n_returns),
        "synthetic": True,
        "provenance": (
            "Deterministic synthetic wide universe for P25 WP0. BTC prices "
            "copied from tests/fixtures/real_market_prices.csv (same dates, "
            "including the 2021-09-17 gap). Asset returns = beta * BTC_return "
            + f" + idio, idio ~ N(0, {IDIO_VOL}), betas linspace({BETA_MIN}, "
            + f"{BETA_MAX}, {N_ASSETS}). "
            "One all-NaN DEL column for loader robustness testing. Not real "
            "market data; not market profitability evidence."
        ),
        "btc_source_sha256": btc_sha256,
        "assets": asset_columns,
        "nan_column": NAN_COLUMN,
    }

    return prices, metadata


def build_wide_universe(*, write: bool = True) -> pd.DataFrame:
    """Build the wide synthetic universe and (optionally) write CSV + metadata.

    Parameters
    ----------
    write : bool
        When True (default), write ``tests/fixtures/wide_bab_universe.csv``
        and ``tests/fixtures/wide_bab_universe_meta.json`` sidecar.

    Returns
    -------
    pd.DataFrame
        Price frame with columns ``[BTC, A001..A040, DEL]`` indexed by date.
    """
    prices, metadata = _build_wide_universe()

    if write:
        _REPO_ROOT.joinpath("tests", "fixtures").mkdir(parents=True, exist_ok=True)
        csv_bytes = prices.to_csv(date_format="%Y-%m-%d").encode("utf-8")
        OUTPUT_CSV.write_bytes(csv_bytes)
        metadata["fixture_sha256"] = hashlib.sha256(csv_bytes).hexdigest()
        OUTPUT_META.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            f"wrote {OUTPUT_CSV} ({len(csv_bytes)} bytes, "
            f"sha256={metadata['fixture_sha256'][:16]}...)"
        )
        print(f"wrote {OUTPUT_META}")

    return prices


def main() -> None:
    started = time.perf_counter()
    prices = build_wide_universe(write=True)
    elapsed = time.perf_counter() - started
    print(f"shape={prices.shape} cols={list(prices.columns)}")
    print(f"date_first={prices.index[0].date()} date_last={prices.index[-1].date()}")
    print(f"DEL all-NaN={prices['DEL'].isna().all()}")
    print(f"build+write {elapsed:.3f}s")


if __name__ == "__main__":
    main()
