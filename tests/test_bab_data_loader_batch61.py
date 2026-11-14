import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 61: real-data probes (no global patching) for promote/normalize handlers


def test_894_last_resort_string_dtype():
    idx = pd.RangeIndex(5)
    df = pd.DataFrame(
        {
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
            "mystery": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        },
        index=idx,
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "mystery" not in out.columns


def test_901_903_last_resort_tz():
    idx = pd.RangeIndex(5)
    df = pd.DataFrame(
        {
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
            "mystery": [
                "2024-01-01T00:00:00Z",
                "2024-01-02T00:00:00Z",
                "2024-01-03T00:00:00Z",
                "2024-01-04T00:00:00Z",
                "2024-01-05T00:00:00Z",
            ],
        },
        index=idx,
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "mystery" not in out.columns


def test_894_datetime64_col():
    idx = pd.RangeIndex(5)
    df = pd.DataFrame(
        {
            "BTC": [0.01, 0.02, 0.03, 0.04, 0.05],
            "ETH": [0.04, 0.05, 0.06, 0.07, 0.08],
            "other_date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
        },
        index=idx,
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert isinstance(out, pd.DataFrame)


def test_867_868_single_row_unnamed():
    df = pd.DataFrame(
        {"Unnamed: 0": ["2024-01-01"], "BTC": [0.01], "ETH": [0.04]}, index=pd.RangeIndex(1)
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False, min_rows=1)
    assert "Unnamed: 0" not in out.columns


def test_859_numpy_dt64_unnamed():
    df = pd.DataFrame(
        {"Unnamed: 0": [np.datetime64("2024-01-01T00:00:00Z")], "BTC": [0.01], "ETH": [0.04]},
        index=pd.RangeIndex(1),
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False, min_rows=1)
    assert "Unnamed: 0" not in out.columns


def test_1530_case_insensitive_bench():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "btc": [0.01] * 5,
            "ETH": [0.02] * 5,
        }
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns


def test_1533_1536_flaky_rename():
    class FlakyRename(pd.DataFrame):
        _n = 0

        @property
        def _constructor(self):
            return FlakyRename

        def rename(self, *a, **k):
            FlakyRename._n += 1
            if FlakyRename._n == 1:
                raise RuntimeError("boom")
            return super().rename(*a, **k)

    df = FlakyRename(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "btc": [0.01] * 5,
            "ETH": [0.02] * 5,
        }
    )
    FlakyRename._n = 0
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "BTC" in out.columns
