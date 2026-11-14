"""Tests for _coerce_series_to_datetime_index."""

from __future__ import annotations

import pandas as pd

from strategies.betting_against_beta import data_loader


def test_coerce_series_to_datetime_index_with_tz():
    df = pd.DataFrame(
        {"date": pd.date_range("2023-01-01", periods=3, tz="UTC"), "BTC": [0.01, 0.02, 0.03]}
    )
    coerced = df["date"].copy()
    res = data_loader._coerce_series_to_datetime_index(df, "date", coerced)
    assert isinstance(res, bool)


def test_coerce_series_to_datetime_index_list():
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    coerced = pd.to_datetime(df["date"]).tolist()
    res = data_loader._coerce_series_to_datetime_index(df, "date", coerced)
    assert isinstance(res, bool)


def test_coerce_series_to_datetime_index_empty():
    df = pd.DataFrame({"date": [], "BTC": []})
    res = data_loader._coerce_series_to_datetime_index(df, "date", [])
    assert res is False
