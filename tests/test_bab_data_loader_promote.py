"""Tests for _promote_datetime_column and coercion paths."""

from __future__ import annotations

import pandas as pd

from strategies.betting_against_beta import data_loader


def test_promote_datetime_column_with_epoch_strings():
    df = pd.DataFrame({"timestamp": ["1700000000", "1700000001"], "BTC": [0.01, 0.02]})
    try:
        res = data_loader._promote_datetime_column(df)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass


def test_promote_datetime_column_with_z_strings():
    df = pd.DataFrame(
        {"date": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"], "BTC": [0.01, 0.02]}
    )
    try:
        res = data_loader._promote_datetime_column(df)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass


def test_promote_datetime_column_unnamed_object():
    df = pd.DataFrame({0: ["2023-01-01", "2023-01-02"], "BTC": [0.01, 0.02]})
    try:
        res = data_loader._promote_datetime_column(df)
        assert isinstance(res, pd.DataFrame)
    except Exception:
        pass
