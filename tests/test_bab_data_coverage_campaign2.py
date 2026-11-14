"""Coverage campaign 2: data.py — generate_synthetic_returns.

Seed determinism, custom asset_names, n_days < 2 edge, column alignment,
benchmark name override.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta.data import generate_synthetic_returns


def test_seed_determinism():
    a = generate_synthetic_returns(n_days=50, n_assets=4, seed=7)
    b = generate_synthetic_returns(n_days=50, n_assets=4, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_seed_changes_output():
    a = generate_synthetic_returns(n_days=50, n_assets=4, seed=1)
    b = generate_synthetic_returns(n_days=50, n_assets=4, seed=2)
    assert not a.equals(b)


def test_custom_asset_names():
    names = ["BTC", "ETH", "SOL"]
    df = generate_synthetic_returns(n_days=30, n_assets=3, asset_names=names, seed=3)
    assert list(df.columns) == names
    assert len(df) == 30


def test_n_days_less_than_two():
    df = generate_synthetic_returns(n_days=1, n_assets=3, seed=4)
    assert len(df) == 1
    assert df.shape[1] == 4  # benchmark + 3 assets


def test_column_alignment_benchmark_plus_assets():
    df = generate_synthetic_returns(n_days=20, n_assets=5, seed=5)
    assert "BTC" in df.columns
    assert all(f"ASSET{i}" in df.columns for i in range(5))
    assert df.shape[1] == 6


def test_benchmark_name_override():
    df = generate_synthetic_returns(n_days=20, n_assets=3, benchmark_name="ETH", seed=6)
    assert "ETH" in df.columns
    assert "BTC" not in df.columns
    assert len(df.columns) == 4


def test_no_nan_inf():
    df = generate_synthetic_returns(n_days=100, n_assets=8, seed=9)
    assert not df.isna().any().any()
    assert np.isfinite(df.to_numpy()).all()


def test_index_is_daily_datetime():
    df = generate_synthetic_returns(n_days=10, n_assets=2, seed=10)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.freq == "D"
