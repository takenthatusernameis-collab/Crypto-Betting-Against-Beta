"""Tests for the beta.py fallback path (P19-5 residue line coverage)."""

import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta.beta import calculate_rolling_beta
from strategies.betting_against_beta.data_loader import BABDataError


def test_beta_uncoercible_asset_column_raises_babdataerror():
    """calculate_rolling_beta raises BABDataError for uncoercible asset columns.

    Covers beta.py:544-548 where:
    1. returns_df[asset].to_numpy(dtype=float, copy=False) raises TypeError
    2. np.asarray(returns_df[asset], dtype=float) also raises TypeError
    3. BABDataError is raised with the error message
    """
    df = pd.DataFrame({
        "BTC": [0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.03, -0.02, 0.01, 0.02],
        "ETH": [object(), object(), object(), object(), object(), object(),
                object(), object(), object(), object()],
        "SOL": [0.02, 0.01, 0.03, 0.01, 0.02, 0.03, 0.01, 0.02, 0.01, 0.03],
    })
    df.index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(BABDataError,
                       match=r"float\(\) argument must be a string or a real number, not 'object'"):
        calculate_rolling_beta(df, "BTC", window=5, min_obs=3)


def test_beta_uncoercible_asset_column_with_valid_benchmark():
    """Benchmark works while an uncoercible asset column raises BABDataError."""
    df = pd.DataFrame({
        "BTC": [0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.03, -0.02, 0.01, 0.02],
        "BAD_ASSET": ["not_a_number", "also_bad", "still_bad", "nope", "fail",
                      "bad", "worse", "terrible", "awful", "horrible"],
    })
    df.index = pd.date_range("2020-01-01", periods=10, freq="D")

    with pytest.raises(BABDataError, match=r"could not convert string to float"):
        calculate_rolling_beta(df, "BTC", window=5, min_obs=3)


def test_beta_benchmark_with_objects_raises():
    """An uncoercible benchmark column raises BABDataError."""
    df = pd.DataFrame({
        "BAD_BENCH": [object(), object(), object(), object(), object()],
        "ETH": [0.02, 0.01, 0.03, 0.01, 0.02],
        "SOL": [0.01, 0.03, 0.02, 0.01, 0.03],
    })
    df.index = pd.date_range("2020-01-01", periods=5, freq="D")

    with pytest.raises(BABDataError,
                       match=r"float\(\) argument must be a string or a real number, not 'object'"):
        calculate_rolling_beta(df, "BAD_BENCH", window=3, min_obs=2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])