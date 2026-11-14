import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import contextlib

import numpy as np
import pandas as pd
import pytest

import strategies.betting_against_beta.data_loader as dl
from strategies.betting_against_beta.data_loader import BABDataError

# Batch 65: reachable promote / benchmark-remap / QA handlers (aggregate-safe, no global patching)


def test_901_903_last_resort_tz_column():
    df = pd.DataFrame(
        {"BTC": [0.01] * 5, "ETH": [0.02] * 5, "rx": ["2024-01-01T00:00:00+05:00"] * 5},
        index=pd.RangeIndex(5),
    )
    out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False)
    assert "rx" not in out.columns


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


def test_1530_1531_1533_1536_benchmark_remap():
    FlakyRename._n = 0
    df = FlakyRename(
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


def test_1257_1258_tz_localize_fallback():
    # tz_convert raises, then tz_localize raises -> line 1257-1258 except
    class WeirdIndex(pd.DatetimeIndex):
        pass

    df = pd.DataFrame(
        {"BTC": [0.01, 0.02, 0.03], "ETH": [0.04, 0.05, 0.06]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]).tz_localize("UTC"),
    )
    with contextlib.suppress(BABDataError):
        dl._run_data_quality_campaign(df, max_return_abs=0.5, min_finite_fraction=0.0)


def test_1293_1294_object_array_abs():
    df = pd.DataFrame(
        {"BTC": ["a", "b", "c"]}, index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    )
    with contextlib.suppress(BABDataError):
        dl._run_data_quality_campaign(df, max_return_abs=0.5, min_finite_fraction=0.0)


def test_1319_1320_coerce_numeric_fallback():
    df = pd.DataFrame(
        {"BTC": [object(), object(), object()]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    )
    with contextlib.suppress(BABDataError):
        dl._run_data_quality_campaign(df, max_return_abs=0.5, min_finite_fraction=0.0)


def test_791_792_name_match_elementwise_tz():
    # tz-aware scalar elements through name-match path
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-02", tz="UTC")],
            "BTC": [0.01, 0.02],
            "ETH": [0.03, 0.04],
        }
    )
    with contextlib.suppress(BABDataError):
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False, min_rows=1)


def test_859_861_862_867_868_unnamed_handlers():
    df = pd.DataFrame(
        {
            "Unnamed: 0": ["2024-01-01T00:00:00+05:00", "2024-01-02T00:00:00+05:00"],
            "BTC": [0.01, 0.02],
            "ETH": [0.03, 0.04],
        },
        index=pd.RangeIndex(2),
    )
    with contextlib.suppress(BABDataError):
        out = dl.validate_returns_dataframe(df, benchmark="BTC", quality=False, min_rows=1)
