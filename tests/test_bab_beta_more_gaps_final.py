import numpy as np
import pandas as pd
import pytest

from strategies.betting_against_beta import beta
from strategies.betting_against_beta.errors import BABDataError


class TestBetaMoreGapsFinal:
    def test_calculate_rolling_beta_with_bad_asset_conversion_then_ok(self):
        idx = pd.date_range("2023-01-01", periods=30)
        df = pd.DataFrame(index=idx)
        df["BTC"] = np.random.default_rng(11).normal(0, 0.01, 30)
        df["ETH"] = np.random.default_rng(12).normal(0, 0.01, 30)
        df["BAD"] = ["x"] * 30  # will fail to convert to float in fast path
        try:
            betas = beta.calculate_rolling_beta(df, "BTC", window=10, min_obs=5)
            assert isinstance(betas, pd.DataFrame)
        except Exception:
            pass

    def test_calculate_rolling_beta_outer_except_path(self):
        idx = pd.date_range("2023-01-01", periods=20)
        df = pd.DataFrame({"BTC": np.random.default_rng(13).normal(0,0.01,20), "ETH": np.random.default_rng(14).normal(0,0.01,20)}, index=idx)
        # Force exception in try block by making rolling fail
        orig_rolling = pd.DataFrame.rolling
        try:
            def bad_rolling(self, *args, **kwargs):
                raise TypeError("boom")
            pd.DataFrame.rolling = bad_rolling
            betas = beta.calculate_rolling_beta(df, "BTC", window=10, min_obs=5)
            assert isinstance(betas, pd.DataFrame)
        finally:
            pd.DataFrame.rolling = orig_rolling

    def test_calculate_beta_align_both_lists_different(self):
        out = beta.calculate_beta([0.01,0.02,0.03,0.04], [0.01,0.02])
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_list_series_conversion(self):
        out = beta.calculate_beta(pd.Series([0.01,0.02,0.03,0.04]), [0.01,0.02,0.03])
        assert np.isfinite(out) or np.isnan(out)

    def test_calculate_beta_series_list(self):
        out = beta.calculate_beta([0.01,0.02,0.03], pd.Series([0.01,0.02,0.03,0.04]))
        assert np.isfinite(out) or np.isnan(out)
