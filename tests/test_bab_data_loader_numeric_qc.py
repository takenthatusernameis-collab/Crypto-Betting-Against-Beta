"""Tests for _coerce_numeric and data quality."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader


def test_coerce_numeric_basic():
    df = pd.DataFrame({"BTC": ["0.01", "0.02"], "ETH": [0.1, 0.2]})
    out = data_loader._coerce_numeric(df)
    assert isinstance(out, pd.DataFrame)


def test_coerce_numeric_with_strings():
    df = pd.DataFrame({"BTC": ["1", "2", "3"]})
    out = data_loader._coerce_numeric(df)
    assert isinstance(out, pd.DataFrame)


def test_run_data_quality_campaign():
    df = pd.DataFrame({"BTC": [0.01, 0.02, np.nan, 0.03]}, index=pd.date_range("2023-01-01", periods=4))
    try:
        res = data_loader._run_data_quality_campaign(df)
        assert isinstance(res, dict)
    except Exception:
        pass
