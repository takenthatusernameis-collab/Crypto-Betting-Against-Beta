"""Data loading and normalization for BAB strategy."""

import numpy as np
import pandas as pd


def generate_synthetic_returns(
    n_days: int = 252,
    n_assets: int = 5,
    asset_names: list = None,
    benchmark_name: str = "BTC",
    seed: int = 42,
):
    """Generate synthetic returns for testing."""
    np.random.seed(seed)
    if asset_names is None:
        asset_names = [f"ASSET{i}" for i in range(n_assets)]

    dates = pd.date_range(start="2023-01-01", periods=n_days, freq="D")

    # Generate benchmark returns
    benchmark_returns = np.random.normal(0.0005, 0.02, n_days)

    returns_data = {benchmark_name: benchmark_returns}

    # Generate asset returns with different betas
    for i, asset in enumerate(asset_names):
        beta = 0.5 + i * 0.5  # betas from 0.5 to ~2.5
        asset_returns = beta * benchmark_returns + np.random.normal(0, 0.01, n_days)
        returns_data[asset] = asset_returns

    df = pd.DataFrame(returns_data, index=dates)
    return df
